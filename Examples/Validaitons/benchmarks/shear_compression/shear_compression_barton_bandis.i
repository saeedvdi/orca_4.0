######################################################################################
# BENCHMARK: single inclined fracture under far-field compression (frictional slip)
#
# Reference configuration follows the GEOS validation case:
#   https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/
#   validationStudies/faultMechanics/singleFracCompression/Example.html
#
# A fracture of half-length b, inclined at psi to the direction of a remote uniaxial
# compression sigma, slips frictionally with
#
#     g_t(s) = 4 (1 - nu^2) / E * sigma sin(psi) [cos(psi) - sin(psi) tan(theta)]
#              * sqrt(b^2 - s^2)
#     sigma_n = -sigma sin^2(psi)                     (tension positive)
#
# where theta is the friction angle. The maximum (mid-fracture) slip is therefore
#
#     g_t,max = 4 (1 - nu^2) b sigma sin(psi)[cos(psi) - sin(psi) tan(theta)] / E
#
# WHAT THIS VERIFIES
# ------------------
# Unlike Sneddon, the interface here is CLOSED and SLIDING, so the Coulomb return map is
# the mechanism under test: the analytic slip depends on the friction coefficient through
# the [cos psi - sin psi tan theta] driving term. Getting the amplitude right requires the
# yield surface, the contact normal stress and the slip direction all to be correct.
#
# The SAME deck is run with all four interface material models, each configured to the
# identical constant-friction interface. All four must reproduce the same analytic slip.
#
# MODEL: ADOrcaBartonBandisContactTractionFastADHardening
######################################################################################

fracture = matrix_top_mid_matrix_bottom_mid

# --- benchmark parameters (GEOS case) ---
bulk_modulus = 16.66666666666666e9
shear_modulus = 1.0e10
youngs_modulus = ${fparse 9.0 * bulk_modulus * shear_modulus / (3.0 * bulk_modulus + shear_modulus)}
poissons_ratio = ${fparse (3.0 * bulk_modulus - 2.0 * shear_modulus) / (2.0 * (3.0 * bulk_modulus + shear_modulus))}
remote_compression = 1.0e8
inclination_deg = 20.0
friction_angle_deg = 30.0
half_length = 1.0

# closed form
psi = ${fparse inclination_deg * pi / 180.0}
theta = ${fparse friction_angle_deg * pi / 180.0}
driving_stress = ${fparse remote_compression * sin(psi) * (cos(psi) - sin(psi) * tan(theta))}
slip_max_analytic = ${fparse 4.0 * (1.0 - poissons_ratio^2) * driving_stress * half_length / youngs_modulus}
sigma_n_analytic = ${fparse -remote_compression * sin(psi)^2}

[Mesh]
  [file_mesh]
    type = FileMeshGenerator
    file = mesh/single_fracture_under_shear_compression_mesh.e
  []
  [side_from_node]
    type = SideSetsFromNodeSetsGenerator
    input = file_mesh
    nodesets_to_convert = 'top bottom left right fracture_interface'
  []
  [refine_crack_blocks]
    type = RefineBlockGenerator
    input = side_from_node
    block = 'matrix_top_mid matrix_bottom_mid'
    refinement = '0 0'
  []
  [no_disp_x]
    type = ExtraNodesetGenerator
    input = refine_crack_blocks
    coord = '0 -40 0 ; 0 40 0'
    new_boundary = no_disp_x
  []
  [no_disp_y]
    type = ExtraNodesetGenerator
    input = no_disp_x
    coord = '-40 0 0 ; 40 0 0'
    new_boundary = no_disp_y
    use_closest_node = true
  []
  [break]
    type = BreakMeshByBlockGenerator
    input = no_disp_y
    block_pairs = 'matrix_top_mid matrix_bottom_mid'
    split_interface = true
    add_interface_on_two_sides = true
  []
[]

[GlobalParams]
  displacements = 'disp_x disp_y'
[]

[Variables]
  [disp_x][]
  [disp_y][]
[]

[Functions]
  # Ramp the remote compression rather than applying it in one step. Applying the full
  # 100 MPa from a stress-free state fails at the first Newton solve: the interface starts
  # at zero gap carrying no contact pressure, so the first trial step interpenetrates
  # freely and the penalty traction that comes back is enormous. The problem is
  # rate-independent and quasi-static, so ramping does not change the final state.
  [compression_ramp]
    type = ParsedFunction
    expression = '${remote_compression} * t'
  []
  [compression_ramp_negative]
    type = ParsedFunction
    expression = '-${remote_compression} * t'
  []
[]

[AuxVariables]
  [crack_opening]
    order = CONSTANT
    family = MONOMIAL
  []
  [czm_sigma_n_out]
    order = CONSTANT
    family = MONOMIAL
  []
  [czm_slip_out]
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
[]

[BCs]
  [pin_x]
    type = DirichletBC
    variable = disp_x
    preset = false
    boundary = 'no_disp_x'
    value = 0.0
  []
  [pin_y]
    type = DirichletBC
    variable = disp_y
    preset = false
    boundary = 'no_disp_y'
    value = 0.0
  []
  # Remote uniaxial compression along x. The traction is t = sigma . n, so with
  # sigma_xx = -P the x-traction is -P on the +x face and +P on the -x face.
  [compress_right]
    type = FunctionNeumannBC
    variable = disp_x
    boundary = right
    function = compression_ramp_negative
  []
  [compress_left]
    type = FunctionNeumannBC
    variable = disp_x
    boundary = left
    function = compression_ramp
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
  [czm_slip_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = czm_slip_out
    property = czm_slip
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
    real_vector_value = interface_displacement_jump
    property_name = czm_ds_1
    index = 1
  []
  [czm_slip_mat]
    type = OrcaCZMRealVectorScalar
    boundary = ${fracture}
    real_vector_value = displacement_jump_global
    direction = Tangent
    property_name = czm_slip
  []
  [czm_sigma_n_mat]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = ${fracture}
    real_vector_value = interface_traction
    property_name = czm_sigma_n
    index = 0
  []
[]

[Postprocessors]
  [slip_max]
    type = ElementExtremeValue
    variable = czm_slip_out
    value_type = max
    block = 'matrix_top_mid matrix_bottom_mid'
  []
  [slip_max_analytic]
    type = ConstantPostprocessor
    value = ${slip_max_analytic}
  []
  [slip_max_rel_error]
    type = ParsedPostprocessor
    pp_names = 'slip_max slip_max_analytic'
    expression = 'abs(slip_max - slip_max_analytic) / slip_max_analytic'
  []
  [sigma_n_mean]
    type = SideAverageValue
    variable = czm_sigma_n_out
    boundary = ${fracture}
  []
  [sigma_n_analytic]
    type = ConstantPostprocessor
    value = ${sigma_n_analytic}
  []
  [sigma_n_rel_error]
    type = ParsedPostprocessor
    pp_names = 'sigma_n_mean sigma_n_analytic'
    expression = 'abs(sigma_n_mean - sigma_n_analytic) / abs(sigma_n_analytic)'
  []
  # The fracture must stay CLOSED: any net opening would invalidate the frictional
  # closed form.
  [opening_max]
    type = ElementExtremeValue
    variable = crack_opening
    value_type = max
    block = 'matrix_top_mid matrix_bottom_mid'
  []
[]

[VectorPostprocessors]
  [slip_profile]
    type = SideValueSampler
    variable = 'czm_slip_out crack_opening czm_sigma_n_out'
    boundary = ${fracture}
    sort_by = x
    execute_on = FINAL
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
  end_time = 1.0
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.1
    optimal_iterations = 8
    growth_factor = 1.5
    cutback_factor = 0.5
  []
  dtmax = 0.25
  dtmin = 1e-4
  nl_abs_tol = 1e-2
  nl_rel_tol = 1e-8
  nl_max_its = 30
  l_max_its = 100
  # A DIRECT solve is required here. The Newton itself is well behaved (quadratic:
  # 6.3e5 -> 8.6e3 -> 6.4e-2 -> 1.5e-5 in three iterations), but hypre BoomerAMG produces
  # DIVERGED_NANORINF on the penalty-stiffened contact operator once the residual reaches
  # ~1e-7 relative, and that cascades into dt collapse.
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_type'
  petsc_options_value = 'lu superlu_dist'
[]

[Outputs]
  csv = true
[]
