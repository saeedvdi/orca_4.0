######################################################################################
# EFFECTIVE STRESS COEFFICIENT, part 1 of 2: the homogenized interface
#
# Verifies that Orca's fracture pressure coefficient does what the effective-stress law
# says it does:
#
#     sigma'_n  =  sigma_n  +  chi p                       (tension positive)
#
# A block is compressed to sigma_n through a single fracture, and a fluid pressure p is
# then raised inside that fracture with `pressure_traction_coefficient = -chi`. The
# interface normal traction must come out at sigma_n + chi p, and the coefficient
# recovered from it,
#
#     chi_measured = (sigma_n_interface - sigma_n_far) / p
#
# must return the chi that was set, for any chi.
#
# This is the operator check. Part 2 (chi_resolved.i) is the physics check: it builds the
# contact patches explicitly and shows that the chi this deck applies uniformly is the
# correct upscaling of a partially-contacting fracture, chi = 1 - A_c/A.
#
# WHY IT MATTERS
# --------------
# `fault_pressure_coefficient` is 0.86 on Ye SW-S4, 0.87 on SW-S3 and 1.0 on SW-T1/T2,
# and the reference model used 0.935. Those are load-side calibration levers, and the
# analytical bound (see ../../YeGhasemmi2018/FRACTURE_PRESSURE_COEFFICIENT.md) says the
# saw-cut values sit below the physically attainable range. Before that argument can be
# made, the coefficient in the code has to be shown to be the coefficient in the theory --
# acting on the right area, with the right sign, and with no hidden normalization.
######################################################################################

sigma_far = 30.0e6                 # far-field normal compression, Pa (magnitude)
fluid_pressure = 20.0e6            # fracture fluid pressure, Pa
chi = 0.86                         # the SW-S4 value; the .py sweeps others

# closed form
sigma_eff_analytic = ${fparse -sigma_far + chi * fluid_pressure}
##########################################################
[Mesh]
  [base]
    type = GeneratedMeshGenerator
    dim = 2
    nx = 100
    ny = 40
    xmin = 0
    xmax = 0.1
    ymin = -0.05
    ymax = 0.05
    elem_type = QUAD4
  []
  [set_bottom]
    type = SubdomainBoundingBoxGenerator
    input = base
    bottom_left = '-1 -1 -1'
    top_right = '1 0 1'
    block_id = 1
    block_name = lower
  []
  [set_top]
    type = SubdomainBoundingBoxGenerator
    input = set_bottom
    bottom_left = '-1 0 -1'
    top_right = '1 1 1'
    block_id = 2
    block_name = upper
  []
  [break]
    type = BreakMeshByBlockGenerator
    input = set_top
    block_pairs = 'lower upper'
    split_interface = true
    add_interface_on_two_sides = true
  []
  construct_side_list_from_node_list = true
[]

fracture = lower_upper
##########################################################
[GlobalParams]
  displacements = 'disp_x disp_y'
[]

[Variables]
  [disp_x][]
  [disp_y][]
[]

[Functions]
  # Phase 1: seat the fracture under the far-field compression. Phase 2: raise the fluid
  # pressure. Both ramped -- a step load lets the first Newton trial interpenetrate freely.
  [normal_load]
    type = PiecewiseLinear
    x = '0 1 2'
    y = '0 ${fparse -sigma_far} ${fparse -sigma_far}'
  []
  [fluid_ramp]
    type = PiecewiseLinear
    x = '0 1 2'
    y = '0 0 ${fluid_pressure}'
  []
[]

[AuxVariables]
  [pore_pressure][]
  [czm_sigma_n_out]
    order = CONSTANT
    family = MONOMIAL
  []
  [czm_dn_out]
    order = CONSTANT
    family = MONOMIAL
  []
[]

[AuxKernels]
  [pore_pressure_aux]
    type = FunctionAux
    variable = pore_pressure
    function = fluid_ramp
    execute_on = 'INITIAL TIMESTEP_BEGIN'
  []
  [czm_sigma_n_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = czm_sigma_n_out
    property = czm_sigma_n
    boundary = ${fracture}
    execute_on = TIMESTEP_END
  []
  [czm_dn_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = czm_dn_out
    property = czm_dn
    boundary = ${fracture}
    execute_on = TIMESTEP_END
  []
[]

[Kernels]
  [disp_x]
    type = OrcaPoroMechKernel
    variable = disp_x
    component = 0
  []
  [disp_y]
    type = OrcaPoroMechKernel
    variable = disp_y
    component = 1
  []
[]

[InterfaceKernels]
  [czm_mech_x]
    type = OrcaMechInterfaceKernel
    boundary = ${fracture}
    variable = disp_x
    neighbor_var = disp_x
    component = 0
  []
  [czm_mech_y]
    type = OrcaMechInterfaceKernel
    boundary = ${fracture}
    variable = disp_y
    neighbor_var = disp_y
    component = 1
  []
  # This is the object under test. The coefficient is negated because the app is
  # tension-positive: the fluid pushes the faces apart, relieving the contact stress.
  [fluid_x]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${fracture}
    variable = disp_x
    neighbor_var = disp_x
    component = 0
    pressure_traction_coefficient = ${fparse -chi}
  []
  [fluid_y]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${fracture}
    variable = disp_y
    neighbor_var = disp_y
    component = 1
    pressure_traction_coefficient = ${fparse -chi}
  []
[]

[BCs]
  # Uniaxial-strain compression: the far field is transmitted through the fracture, so the
  # interface traction is the whole force balance and nothing else can carry the load.
  [roller_x]
    type = DirichletBC
    variable = disp_x
    preset = false
    boundary = 'left right'
    value = 0.0
  []
  [fix_bottom]
    type = DirichletBC
    variable = disp_y
    preset = false
    boundary = bottom
    value = 0.0
  []
  [load_top]
    type = FunctionNeumannBC
    variable = disp_y
    boundary = top
    function = normal_load
  []
[]

[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = 67.0e9          # Sierra White granite, Ye & Ghassemi (2018)
    poissons_ratio = 0.32
    strain_model = incremental
  []
  [czm_jump]
    type = OrcaCZMComputeDisplacementJump
    boundary = ${fracture}
  []
  [czm_pressure]
    type = OrcaCZMInterfacePressure
    boundary = ${fracture}
    pore_pressure = pore_pressure
  []
  [czm]
    type = ADOrcaBartonBandisContactTractionFastADHardening
    boundary = ${fracture}
    penalty_tangent = 1e+13
    initial_normal_stiffness = 1e+13
    use_hyperbolic_normal_closure = false
    contact_gap_regularization = 1e-12
    jrc = 0.0
    jcs = 1.5e8
    residual_friction_angle_degrees = 30.0
    use_scale_correction = false
    use_mobilized_jrc = false
    use_slip_weakening = false
    use_dilatancy = false
  []
  [czm_global_traction]
    type = OrcaComputeGlobalTractionSmallStrain
    boundary = ${fracture}
  []
  [czm_sigma_n]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = ${fracture}
    real_vector_value = interface_traction
    property_name = czm_sigma_n
    index = 0
  []
  [czm_dn]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = ${fracture}
    real_vector_value = interface_displacement_jump
    property_name = czm_dn
    index = 0
  []
[]

[Postprocessors]
  [sigma_n_interface]
    type = SideAverageValue
    variable = czm_sigma_n_out
    boundary = ${fracture}
  []
  [sigma_eff_analytic]
    type = ConstantPostprocessor
    value = ${sigma_eff_analytic}
  []
  [sigma_eff_rel_error]
    type = ParsedPostprocessor
    pp_names = 'sigma_n_interface sigma_eff_analytic'
    expression = 'abs(sigma_n_interface - sigma_eff_analytic) / abs(sigma_eff_analytic)'
  []
  # The coefficient recovered from the simulation, which must return the chi that was set.
  # The +1 Pa guard only keeps t < 1 finite, where the fluid pressure is still zero.
  [pressure_applied]
    type = FunctionValuePostprocessor
    function = fluid_ramp
  []
  [chi_measured]
    type = ParsedPostprocessor
    pp_names = 'sigma_n_interface pressure_applied'
    expression = '(sigma_n_interface + ${sigma_far}) / (pressure_applied + 1.0)'
  []
  [chi_set]
    type = ConstantPostprocessor
    value = ${chi}
  []
  # The fracture must stay CLOSED: chi is an effective-stress coefficient only while the
  # faces are in contact. If chi p exceeded sigma_far the fracture would open and the
  # whole framing would change.
  [closure_max]
    type = SideExtremeValue
    variable = czm_dn_out
    boundary = ${fracture}
    value_type = max
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  start_time = 0.0
  end_time = 2.0
  dt = 0.25
  nl_abs_tol = 1e-6
  nl_rel_tol = 1e-10
  nl_max_its = 20
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_type'
  petsc_options_value = 'lu superlu_dist'
[]

[Outputs]
  csv = true
[]
