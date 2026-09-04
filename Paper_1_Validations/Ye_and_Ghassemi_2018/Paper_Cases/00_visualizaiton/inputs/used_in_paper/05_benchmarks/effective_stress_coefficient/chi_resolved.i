######################################################################################
# EFFECTIVE STRESS COEFFICIENT, part 2 of 2: resolved contact patches
#
# Part 1 (chi_homogenized.i) showed that Orca applies chi as the theory writes it. This
# deck asks the physics question instead: what SHOULD chi be?
#
# The effective-stress coefficient of a fracture is not free. A force balance across the
# interface, over a representative area A of which A_c is in solid-solid contact and the
# rest carries fluid at pressure p, gives (tension positive)
#
#     sigma_n A = sigma_c A_c - p (A - A_c)
#     sigma'_n  = sigma_c A_c / A = sigma_n + p (1 - A_c/A)
#     =>   chi = 1 - A_c/A                                            [EXACT]
#
# This deck builds that geometry EXPLICITLY. The fracture is divided into alternating
# strips: contact strips carry a stiff contact law and no fluid, void strips carry a
# negligible stiffness and the full fluid pressure with coefficient 1. Nothing tells the
# model what chi is -- it is measured from the result:
#
#     chi_measured = (c_realized * sigma_c_mean - sigma_n_far) / p
#
# and must equal 1 - A_c/A.
#
# The default contact fraction is 0.14, because that is exactly what Ye SW-S4's
# chi = 0.86 implies. The deck therefore answers a concrete question: is a 14 % real
# contact area a physically sensible state for a saw-cut granite joint at 30 MPa?
# ../../YeGhasemmi2018/FRACTURE_PRESSURE_COEFFICIENT.md answers that separately -- the
# plastic-asperity bound gives 6.7 %, so 14 % needs an indentation hardness of 1.43 x UCS
# where Tabor's relation requires about 3 x. This deck supplies the other half: that
# chi = 1 - A_c/A really is the relation linking the two.
#
# WHY IT IS NOT CIRCULAR
# ----------------------
# The strips are a geometric construction, not a constitutive one. The only inputs are
# where the contact patches are and how stiff they are; the coefficient falls out of the
# force balance the solver performs. A wrong area normalization, a wrong sign, or a
# fluid load applied over the wrong fraction would all show up here and in none of the
# GEOS benchmarks.
######################################################################################

sigma_far = 30.0e6                 # far-field normal compression, Pa (magnitude)
fluid_pressure = 20.0e6            # fluid pressure in the non-contacting area, Pa
contact_fraction = 0.14            # A_c/A -- what Ye SW-S4's chi = 0.86 implies
strip_period = 0.02                # m; 5 periods across the 0.1 m fracture

# closed form
chi_analytic = ${fparse 1.0 - contact_fraction}
sigma_eff_analytic = ${fparse -sigma_far + chi_analytic * fluid_pressure}
##########################################################
[Mesh]
  [base]
    type = GeneratedMeshGenerator
    dim = 2
    # 400 elements across 0.1 m gives 80 per strip period, so the narrowest contact patch
    # (14 % of 0.02 m = 2.8 mm) is still resolved by 11 elements.
    nx = 400
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
  # The strips are cut out of the ALREADY BROKEN interface, so the fracture stays one
  # continuous split surface. Doing it with blocks instead would put four subdomains at
  # every strip edge, and BreakMeshByBlockGenerator refuses to split a node touching more
  # than two -- welding the interface at every strip boundary and corrupting the very
  # force balance being measured.
  [contact_strips]
    type = ParsedGenerateSideset
    input = break
    included_boundaries = 'lower_upper'
    new_sideset_name = 'contact_patches'
    constant_names = 'lam frac'
    constant_expressions = '${strip_period} ${contact_fraction}'
    combinatorial_geometry = 'x - floor(x / lam) * lam < frac * lam'
  []
  [void_strips]
    type = ParsedGenerateSideset
    input = contact_strips
    included_boundaries = 'lower_upper'
    new_sideset_name = 'void_patches'
    constant_names = 'lam frac'
    constant_expressions = '${strip_period} ${contact_fraction}'
    combinatorial_geometry = 'x - floor(x / lam) * lam >= frac * lam'
  []
  construct_side_list_from_node_list = true
[]

# The physics lives on the two sub-sidesets, never on their parent. MOOSE checks
# boundary-restricted material properties by boundary ID, not by geometric coverage, so a
# property declared on 'contact_patches void_patches' does NOT satisfy a request on
# 'lower_upper' even though the two cover the same surface.
fracture = 'contact_patches void_patches'
##########################################################
[GlobalParams]
  displacements = 'disp_x disp_y'
[]

[Variables]
  [disp_x][]
  [disp_y][]
[]

[Functions]
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
  # The fluid acts on the NON-CONTACTING area only, at full strength. This is the whole
  # point: chi is not applied anywhere in this deck, it is the answer.
  [fluid_x]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = 'void_patches'
    variable = disp_x
    neighbor_var = disp_x
    component = 0
    pressure_traction_coefficient = -1.0
  []
  [fluid_y]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = 'void_patches'
    variable = disp_y
    neighbor_var = disp_y
    component = 1
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
    youngs_modulus = 67.0e9
    poissons_ratio = 0.32
    strain_model = incremental
  []
  [czm_jump]
    type = OrcaCZMComputeDisplacementJump
    boundary = ${fracture}
  []
  # The fracture fluid, present only in the void patches.
  [czm_pressure]
    type = OrcaCZMInterfacePressure
    boundary = 'void_patches'
    pore_pressure = pore_pressure
  []
  # Contact patches: asperities in solid-solid contact, stiff.
  [czm_contact]
    type = ADOrcaBartonBandisContactTractionFastADHardening
    boundary = 'contact_patches'
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
  # Void patches: a fluid-filled gap. Eight orders of magnitude softer, so it carries a
  # negligible share of the solid load -- with the interface closing ~1e-6 m the void
  # traction is ~0.1 Pa against ~1e8 Pa on the asperities.
  [czm_void]
    type = ADOrcaBartonBandisContactTractionFastADHardening
    boundary = 'void_patches'
    penalty_tangent = 1e+5
    initial_normal_stiffness = 1e+5
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
[]

[Postprocessors]
  # The realized contact fraction, measured from the mesh rather than assumed: the strip
  # edges fall between elements, so the discretized fraction is not exactly the nominal one.
  [area_contact]
    type = AreaPostprocessor
    boundary = 'contact_patches'
  []
  [area_total]
    type = AreaPostprocessor
    boundary = ${fracture}
  []
  # Guard: the two strip sidesets must tile the fracture exactly. The two combinatorial
  # expressions are complementary, so this must return the fracture length, 0.1 m.
  [area_total_expected]
    type = ConstantPostprocessor
    value = 0.1
  []
  [contact_fraction_realized]
    type = ParsedPostprocessor
    pp_names = 'area_contact area_total'
    expression = 'area_contact / area_total'
  []
  [sigma_c_mean]
    type = SideAverageValue
    variable = czm_sigma_n_out
    boundary = 'contact_patches'
  []
  [sigma_void_mean]
    type = SideAverageValue
    variable = czm_sigma_n_out
    boundary = 'void_patches'
  []
  # sigma'_n = sigma_c * A_c/A, the definition at the top of this file.
  [sigma_eff_resolved]
    type = ParsedPostprocessor
    pp_names = 'sigma_c_mean contact_fraction_realized'
    expression = 'sigma_c_mean * contact_fraction_realized'
  []
  [sigma_eff_analytic]
    type = ConstantPostprocessor
    value = ${sigma_eff_analytic}
  []
  [pressure_applied]
    type = FunctionValuePostprocessor
    function = fluid_ramp
  []
  # THE RESULT. Recovered from a resolved calculation that was never told what chi is.
  # p/(p^2+1) rather than 1/(p+1): exactly zero while the fluid pressure is zero, instead
  # of a round-off-level number whose sign depends on the rank count.
  [chi_measured]
    type = ParsedPostprocessor
    pp_names = 'sigma_eff_resolved pressure_applied'
    expression = '(sigma_eff_resolved + ${sigma_far}) * pressure_applied / (pressure_applied * pressure_applied + 1.0)'
  []
  [chi_analytic]
    type = ParsedPostprocessor
    pp_names = 'contact_fraction_realized'
    expression = '1.0 - contact_fraction_realized'
  []
  [chi_rel_error]
    type = ParsedPostprocessor
    pp_names = 'chi_measured chi_analytic'
    expression = 'abs(chi_measured - chi_analytic) / chi_analytic'
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
