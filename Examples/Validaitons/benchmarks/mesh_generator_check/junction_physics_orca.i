######################################################################################
# GENERATOR EQUIVALENCE ON A JUNCTION: OrcaFaultInterface3DGenerator
#
# The mesh-only tests show the T-junction node splits into three. This deck asks the
# question that actually matters: does the SOLUTION come out the same as it does with
# MOOSE's BreakMeshByBlockGenerator?
#
# It is ../fracutre_interseciton_problem scaled by 1/25 and meshed in 3D, one element
# thick, so the geometry is the GEOS TFrac configuration:
#
#     vertical fracture    x = 0,   y in [-2, +2]   pressurized to 100 MPa
#     horizontal fracture  y = +2,  x in [-1, +1]   frictional, mu = tan(30 deg)
#     domain               +-20 m                   (same 10:1 ratio as the benchmark)
#
# `junction_physics_breakmesh.i` is this deck with ONLY the [Mesh] block and the two
# fracture boundary names changed. Every postprocessor must agree between the two.
#
# This is the end-to-end check on FIX 5 through FIX 8. A welded junction, a dropped
# interface face, or a collided secondary sideset id all change the answer here, and
# none of them raises an error on its own.
######################################################################################

frac_v = frac_v
frac_h = frac_h
frac_all = 'frac_v frac_h'

youngs_modulus = 70.0068e9
poissons_ratio = 0.19998
remote_compression = 1.0e8
crack_pressure = 1.0e8
friction_angle_deg = 30.0
half_length_v = 2.0

sneddon_aperture_max = ${fparse 4.0 * (1.0 - poissons_ratio^2) * crack_pressure * half_length_v / youngs_modulus}
##########################################################
[Mesh]
  [base]
    type = GeneratedMeshGenerator
    dim = 3
    # 0.25 m cells put boundaries exactly on x = 0, +-1 and y = +-2.
    nx = 160
    ny = 160
    nz = 1
    xmin = -20
    xmax = 20
    ymin = -20
    ymax = 20
    zmin = 0
    zmax = 0.25
    elem_type = HEX8
  []
  [lower_left]
    type = SubdomainBoundingBoxGenerator
    input = base
    bottom_left = '-1 -2 -1'
    top_right = '0 2 1'
    block_id = 2
    block_name = lower_left
  []
  [lower_right]
    type = SubdomainBoundingBoxGenerator
    input = lower_left
    bottom_left = '0 -2 -1'
    top_right = '1 2 1'
    block_id = 3
    block_name = lower_right
  []
  [cap]
    type = SubdomainBoundingBoxGenerator
    input = lower_right
    bottom_left = '-1 2 -1'
    top_right = '1 20 1'
    block_id = 4
    block_name = cap
  []
  # One-sided sidesets, straight from SideSetsBetweenSubdomainsGenerator.
  [make_frac_h]
    type = SideSetsBetweenSubdomainsGenerator
    input = cap
    primary_block = 'lower_left lower_right'
    paired_block = 'cap'
    new_boundary = 'frac_h'
  []
  [make_frac_v]
    type = SideSetsBetweenSubdomainsGenerator
    input = make_frac_h
    primary_block = 'lower_left'
    paired_block = 'lower_right'
    new_boundary = 'frac_v'
  []
  [split]
    type = OrcaFaultInterface3DGenerator
    input = make_frac_v
    sidesets = 'frac_h frac_v'
    preserve_front_nodes = true
    split_only_interior_nodes = true
    add_interface_on_two_sides = true
    secondary_sidesets = 'frac_h_other frac_v_other'
  []
[]
##########################################################
[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Variables]
  [disp_x][]
  [disp_y][]
  [disp_z][]
[]

[Functions]
  [far_field_yy]
    type = PiecewiseLinear
    x = '0 1 2'
    y = '0 ${fparse -remote_compression} ${fparse -remote_compression}'
  []
  [crack_pressure_fn]
    type = PiecewiseLinear
    x = '0 1 2'
    y = '0 0 ${crack_pressure}'
  []
[]

[AuxVariables]
  [pore_pressure][]
  [dn_v]
    order = CONSTANT
    family = MONOMIAL
  []
  [dn_h]
    order = CONSTANT
    family = MONOMIAL
  []
  [ds_h]
    order = CONSTANT
    family = MONOMIAL
  []
  [sigma_n_h]
    order = CONSTANT
    family = MONOMIAL
  []
[]

[AuxKernels]
  [pore_pressure_aux]
    type = FunctionAux
    variable = pore_pressure
    function = crack_pressure_fn
    execute_on = 'INITIAL TIMESTEP_BEGIN'
  []
  [dn_v_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = dn_v
    property = czm_dn
    boundary = ${frac_v}
    execute_on = TIMESTEP_END
  []
  [dn_h_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = dn_h
    property = czm_dn
    boundary = ${frac_h}
    execute_on = TIMESTEP_END
  []
  [ds_h_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = ds_h
    property = czm_ds_1
    boundary = ${frac_h}
    execute_on = TIMESTEP_END
  []
  [sigma_n_h_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = sigma_n_h
    property = czm_sigma_n
    boundary = ${frac_h}
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
  [disp_z]
    type = OrcaPoroMechKernel
    variable = disp_z
    component = 2
  []
[]

[InterfaceKernels]
  [czm_x]
    type = OrcaMechInterfaceKernel
    boundary = ${frac_all}
    variable = disp_x
    neighbor_var = disp_x
    component = 0
  []
  [czm_y]
    type = OrcaMechInterfaceKernel
    boundary = ${frac_all}
    variable = disp_y
    neighbor_var = disp_y
    component = 1
  []
  [czm_z]
    type = OrcaMechInterfaceKernel
    boundary = ${frac_all}
    variable = disp_z
    neighbor_var = disp_z
    component = 2
  []
  [fluid_x]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${frac_v}
    variable = disp_x
    neighbor_var = disp_x
    component = 0
    pressure_traction_coefficient = -1.0
  []
  [fluid_y]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${frac_v}
    variable = disp_y
    neighbor_var = disp_y
    component = 1
    pressure_traction_coefficient = -1.0
  []
  [fluid_z]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${frac_v}
    variable = disp_z
    neighbor_var = disp_z
    component = 2
    pressure_traction_coefficient = -1.0
  []
[]

[BCs]
  [roller_x]
    type = DirichletBC
    variable = disp_x
    preset = false
    boundary = 'left right'
    value = 0.0
  []
  [roller_y]
    type = DirichletBC
    variable = disp_y
    preset = false
    boundary = 'top bottom'
    value = 0.0
  []
  [plane_strain_z]
    type = DirichletBC
    variable = disp_z
    preset = false
    boundary = 'front back'
    value = 0.0
  []
[]

[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = ${youngs_modulus}
    poissons_ratio = ${poissons_ratio}
    strain_model = incremental
    initial_stress = '0 far_field_yy 0 0 0 0'
  []
  [czm_jump]
    type = OrcaCZMComputeDisplacementJump
    boundary = ${frac_all}
  []
  [czm_pressure]
    type = OrcaCZMInterfacePressure
    boundary = ${frac_v}
    pore_pressure = pore_pressure
  []
  [czm]
    type = ADOrcaBartonBandisContactTractionFastADHardening
    boundary = ${frac_all}
    penalty_tangent = 1e+12
    initial_normal_stiffness = 1e+12
    use_hyperbolic_normal_closure = false
    contact_gap_regularization = 1e-12
    jrc = 0.0
    jcs = 1.0e8
    residual_friction_angle_degrees = ${friction_angle_deg}
    use_scale_correction = false
    use_mobilized_jrc = false
    use_slip_weakening = false
    use_dilatancy = false
  []
  [czm_global_traction]
    type = OrcaComputeGlobalTractionSmallStrain
    boundary = ${frac_all}
  []
  [czm_dn]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = ${frac_all}
    real_vector_value = interface_displacement_jump
    property_name = czm_dn
    index = 0
  []
  [czm_ds_1]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = ${frac_all}
    real_vector_value = interface_displacement_jump
    property_name = czm_ds_1
    index = 1
  []
  [czm_sigma_n]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = ${frac_all}
    real_vector_value = interface_traction
    property_name = czm_sigma_n
    index = 0
  []
[]

[Postprocessors]
  [aperture_max]
    type = SideExtremeValue
    variable = dn_v
    boundary = ${frac_v}
    value_type = max
  []
  # Maximum normal jump on the horizontal fracture. It stays negative (the fracture is
  # clamped shut by the far field) and is the most sensitive scalar to a mis-partitioned
  # junction: an inverted partition changed it by 84 %.
  [dn_max_h]
    type = SideExtremeValue
    variable = dn_h
    boundary = ${frac_h}
    value_type = max
  []
  [aperture_over_sneddon]
    type = ParsedPostprocessor
    pp_names = 'aperture_max'
    expression = 'aperture_max / ${sneddon_aperture_max}'
  []
  [slip_max_h]
    type = SideExtremeValue
    variable = ds_h
    boundary = ${frac_h}
    value_type = max
  []
  [slip_min_h]
    type = SideExtremeValue
    variable = ds_h
    boundary = ${frac_h}
    value_type = min
  []
  [sigma_n_mean_h]
    type = SideAverageValue
    variable = sigma_n_h
    boundary = ${frac_h}
  []
  [sigma_n_min_h]
    type = SideExtremeValue
    variable = sigma_n_h
    boundary = ${frac_h}
    value_type = min
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
  nl_abs_tol = 1e-2
  nl_rel_tol = 1e-8
  nl_max_its = 30
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_type'
  petsc_options_value = 'lu superlu_dist'
[]

[Outputs]
  csv = true
[]
