######################################################################################
# BENCHMARK: Sneddon (1946) -- pressurized 2D crack in an infinite elastic medium
#
# Reference configuration follows the GEOS validation case:
#   https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/
#   validationStudies/faultMechanics/sneddon/Example.html
#
# A crack of half-length b, internally pressurized at p_f in a linear elastic medium of
# Young's modulus E and Poisson's ratio nu, opens as
#
#     w(s) = 4 (1 - nu^2) p_f / E * sqrt(b^2 - s^2)
#
# so the maximum (mid-crack) opening is
#
#     w_max = 4 (1 - nu^2) p_f b / E
#
# WHAT THIS VERIFIES
# ------------------
# The crack is OPEN everywhere, so the interface must carry essentially no traction: the
# whole response comes from the elastic medium plus the fluid load on the faces. That
# makes this a check of (a) the CZM kinematics and interface-kernel sign convention,
# (b) the fluid-pressure interface kernel, and (c) that the constitutive law correctly
# returns a traction-free open state.
#
# The SAME deck is run with all four interface material models, each configured to the
# identical idealized interface. All four must reproduce the same analytic opening --
# that cross-model agreement is the point of the test, not a per-model calibration.
#
# MODEL: ADOrcaBartonBandisContactTractionFastADHardening
######################################################################################

fracture = matrix_top_mid_matrix_bottom_mid

# --- benchmark parameters (GEOS case) ---
youngs_modulus = 1.0e10
poissons_ratio = 0.25
crack_pressure = 2.0e6
half_length = 1.0                        # crack runs from x = -1 to x = +1

# closed form
w_max_analytic = ${fparse 4.0 * (1.0 - poissons_ratio^2) * crack_pressure * half_length / youngs_modulus}

[Mesh]
  [base]
    type = GeneratedMeshGenerator
    dim = 2
    nx = 80
    ny = 80
    xmin = -20
    xmax = 20
    ymin = -20
    ymax = 20
    elem_type = QUAD4
  []
  [set_bottom]
    type = SubdomainBoundingBoxGenerator
    input = base
    bottom_left = '-20 -20 -1'
    top_right = '20 0 1'
    block_id = 11
    block_name = matrix_bottom
  []
  [set_top]
    type = SubdomainBoundingBoxGenerator
    input = set_bottom
    bottom_left = '-20 0 -1'
    top_right = '20 20 1'
    block_id = 12
    block_name = matrix_top
  []
  [set_bottom_mid]
    type = SubdomainBoundingBoxGenerator
    input = set_top
    bottom_left = '-1 -20 -1'
    top_right = '1 0 1'
    block_id = 13
    block_name = matrix_bottom_mid
  []
  [set_top_mid]
    type = SubdomainBoundingBoxGenerator
    input = set_bottom_mid
    bottom_left = '-1 0 -1'
    top_right = '1 20 1'
    block_id = 14
    block_name = matrix_top_mid
  []
  [refine_crack_blocks]
    type = RefineBlockGenerator
    input = set_top_mid
    block = 'matrix_bottom_mid matrix_top_mid'
    refinement = '4 4'
  []
  [break]
    type = BreakMeshByBlockGenerator
    input = refine_crack_blocks
    block_pairs = 'matrix_bottom_mid matrix_top_mid'
    split_interface = true
    add_interface_on_two_sides = true
  []
  construct_side_list_from_node_list = true
[]

[GlobalParams]
  displacements = 'disp_x disp_y'
[]

[Variables]
  [disp_x][]
  [disp_y][]
[]

[AuxVariables]
  # Prescribed crack fluid pressure. Held as an AuxVariable so no flow problem is solved:
  # OrcaCZMInterfacePressure averages it across the interface and
  # OrcaCZMFluidPressureInterfaceKernel converts it into the face load.
  [pore_pressure]
    initial_condition = ${crack_pressure}
  []
  [crack_opening]
    order = CONSTANT
    family = MONOMIAL
  []
  [czm_sigma_n_out]
    order = CONSTANT
    family = MONOMIAL
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
  # Fluid pressure on the crack faces. The -1 coefficient is the app's tension-positive
  # convention: it pushes the faces apart, exactly as it relieves the contact normal
  # stress in the Ye (2018) injection decks.
  [crack_pressure_x]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${fracture}
    variable = disp_x
    neighbor_var = disp_x
    component = 0
    displacements = 'disp_x disp_y'
    pressure_traction_coefficient = -1.0
  []
  [crack_pressure_y]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${fracture}
    variable = disp_y
    neighbor_var = disp_y
    component = 1
    displacements = 'disp_x disp_y'
    pressure_traction_coefficient = -1.0
  []
[]

[BCs]
  [confine_x]
    type = DirichletBC
    variable = disp_x
    preset = false
    boundary = 'left right'
    value = 0.0
  []
  [confine_y]
    type = DirichletBC
    variable = disp_y
    preset = false
    boundary = 'bottom top'
    value = 0.0
  []
[]

[AuxKernels]
  [crack_opening_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = crack_opening
    property = czm_dn
    boundary = ${fracture}
    execute_on = TIMESTEP_END
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

[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = ${youngs_modulus}
    poissons_ratio = ${poissons_ratio}
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
    penalty_tangent = 1e+12
    initial_normal_stiffness = 1e+12
    use_hyperbolic_normal_closure = false
    contact_gap_regularization = 1e-12
    # jrc = 0 collapses the Barton-Bandis roughness angle to zero, so
    # phi_peak = residual_friction_angle_degrees = 30 deg and mu is constant.
    jrc = 0.0
    jcs = 1.0e8
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
  [czm_dn]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = ${fracture}
    real_vector_value = interface_displacement_jump
    property_name = czm_dn
    index = 0
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
  # Mid-crack opening: the element average over the two elements straddling x = 0 is the
  # cleanest scalar proxy for w_max on a structured mesh.
  [w_max]
    type = ElementExtremeValue
    variable = crack_opening
    value_type = max
    block = 'matrix_top_mid matrix_bottom_mid'
  []
  [w_max_analytic]
    type = ConstantPostprocessor
    value = ${w_max_analytic}
  []
  [w_max_rel_error]
    type = ParsedPostprocessor
    pp_names = 'w_max w_max_analytic'
    expression = 'abs(w_max - w_max_analytic) / w_max_analytic'
  []
  # The crack is open, so the CONSTITUTIVE traction must be negligible against the applied
  # crack pressure. This is what distinguishes a correct open state from a law that leaks
  # a spurious tensile or contact traction.
  [sigma_n_mean]
    type = SideAverageValue
    variable = czm_sigma_n_out
    boundary = ${fracture}
  []
  [open_traction_ratio]
    type = ParsedPostprocessor
    pp_names = sigma_n_mean
    expression = 'abs(sigma_n_mean) / ${crack_pressure}'
  []
[]

[VectorPostprocessors]
  [crack_opening_profile]
    type = SideValueSampler
    variable = 'crack_opening'
    boundary = ${fracture}
    sort_by = x
    # NOT `FINAL`: a side sampler executed on FINAL never runs its boundary loop, so the
    # profile CSV came out header-only on every deck in this suite until 2026-09-02.
    # TIMESTEP_END writes one file per step; the last one is the converged profile.
    execute_on = TIMESTEP_END
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
  dt = 1.0
  end_time = 1.0
  nl_abs_tol = 1e-8
  nl_rel_tol = 1e-10
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
  exodus = true
[]
