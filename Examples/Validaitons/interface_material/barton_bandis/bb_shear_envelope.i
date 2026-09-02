# CZM regression: Barton-Bandis (FastAD) normal closure, shear envelope and slip weakening.
#
# Constant-normal-DISPLACEMENT direct shear of two stiff blocks. Holding the normal
# kinematics fixed pins sigma_n, which makes all four closed forms below checkable exactly
# on the SOLVED state:
#
#   1. Normal closure:  sigma_n = (K_ni V_m)[c/(V_m - c)]^(1/p),  c = c_0 - g_n
#                                                             -> closure_rel_error
#   2. Peak envelope:   phi_p = phi_r + JRC*log10(JCS/sigma_n)   -> envelope_rel_error
#   3. Slip weakening:  mu_eff = mu_sw + (tan(phi_p) - mu_sw)*exp(-(s/D_c)^m)
#                       and tau_limit = sigma_n * mu_eff         -> weakening_rel_error,
#                                                                  strength_rel_error
#   4. On the yield surface, tau = tau_limit                     -> yield_rel_error
#
# Dilatancy is off so the normal state is fixed by the boundary condition alone; the
# dilation/normal-stress coupling is exercised by the companion CompressionTensile
# dissipation-limiter test and by the production decks.
#
# contact_gap_regularization is deliberately nonzero: the hard active set (the default) is
# what collapses dt at the stick/slip transition in the Barton-Bandis production decks, so
# this test pins the regularized path.

E = 1e13
nu = 0.0

# Barton-Bandis normal closure
kni = 2.443e11
vm = 4.591e-5
p_exp = 3.28
c0 = 4.433e-5
sigma0 = ${fparse kni * vm}

# Barton-Bandis strength
jrc = 10.0
jcs = 1.5e8
phi_r = 30.0            # basic friction angle [deg]
phi_sw = 22.0           # residual friction angle of the slip-weakening tail [deg]
dc = 5.0e-5             # slip-weakening distance [m]
sw_exp = 1.0
mu_sw = ${fparse tan(phi_sw * pi / 180.0)}

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 1
    ny = 1
    nz = 2
    xmax = 1e-3
    ymax = 1e-3
    zmax = 1e-3
  []
  [lower]
    type = SubdomainBoundingBoxGenerator
    input = gen
    block_id = 1
    bottom_left = '-1 -1 -1'
    top_right = '1 1 0.5e-3'
  []
  [upper]
    type = SubdomainBoundingBoxGenerator
    input = lower
    block_id = 2
    bottom_left = '-1 -1 0.5e-3'
    top_right = '1 1 1'
  []
  [split]
    type = BreakMeshByBlockGenerator
    input = upper
    split_interface = true
  []
[]

[Variables]
  [disp_x][]
  [disp_y][]
  [disp_z][]
[]

[Functions]
  # Close the pre-seated joint by a further 0.6 um over t = 0..1, then hold while shearing.
  [normal_drive]
    type = PiecewiseLinear
    x = '0  1       8'
    y = '0 -0.6e-6 -0.6e-6'
  []
  [shear_drive]
    type = PiecewiseLinear
    x = '0 1 8'
    y = '0 0 200e-6'
  []
[]

[Kernels]
  [sdx]
    type = OrcaPoroMechKernel
    variable = disp_x
    component = 0
  []
  [sdy]
    type = OrcaPoroMechKernel
    variable = disp_y
    component = 1
  []
  [sdz]
    type = OrcaPoroMechKernel
    variable = disp_z
    component = 2
  []
[]

[InterfaceKernels]
  [czm_x]
    type = OrcaMechInterfaceKernel
    boundary = Block1_Block2
    variable = disp_x
    neighbor_var = disp_x
    component = 0
  []
  [czm_y]
    type = OrcaMechInterfaceKernel
    boundary = Block1_Block2
    variable = disp_y
    neighbor_var = disp_y
    component = 1
  []
  [czm_z]
    type = OrcaMechInterfaceKernel
    boundary = Block1_Block2
    variable = disp_z
    neighbor_var = disp_z
    component = 2
  []
[]

[BCs]
  [base_x]
    type = DirichletBC
    variable = disp_x
    boundary = back
    value = 0
  []
  [base_y]
    type = DirichletBC
    variable = disp_y
    boundary = back
    value = 0
  []
  [base_z]
    type = DirichletBC
    variable = disp_z
    boundary = back
    value = 0
  []
  [top_z]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = front
    function = normal_drive
  []
  [top_x]
    type = FunctionDirichletBC
    variable = disp_x
    boundary = front
    function = shear_drive
  []
  [top_y]
    type = DirichletBC
    variable = disp_y
    boundary = front
    value = 0
  []
[]

[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = ${E}
    poissons_ratio = ${nu}
    strain_model = incremental
  []
  [czm_jump]
    type = OrcaCZMComputeDisplacementJump
    boundary = Block1_Block2
  []
  [czm]
    type = ADOrcaBartonBandisContactTractionFastADHardening
    boundary = Block1_Block2
    penalty_tangent = 1e13
    contact_gap_regularization = 1e-10

    use_hyperbolic_normal_closure = true
    initial_normal_stiffness = ${kni}
    maximum_closure = ${vm}
    normal_closure_stress_exponent = ${p_exp}
    normal_closure_offset = ${c0}

    jrc = ${jrc}
    jcs = ${jcs}
    residual_friction_angle_degrees = ${phi_r}
    use_scale_correction = false
    use_mobilized_jrc = false
    allow_negative_roughness_angle = false
    min_friction_angle_degrees = 0.0
    max_friction_angle_degrees = 85.0

    use_slip_weakening = true
    characteristic_slip_distance = ${dc}
    slip_weakening_exponent = ${sw_exp}
    slip_weakening_residual_friction_angle_degrees = ${phi_sw}

    use_dilatancy = false
  []
  [czm_global]
    type = OrcaComputeGlobalTractionSmallStrain
    boundary = Block1_Block2
  []
  [tau_1]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = Block1_Block2
    real_vector_value = interface_traction
    property_name = czm_tau_1
    index = 1
  []
  [tau_2]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = Block1_Block2
    real_vector_value = interface_traction
    property_name = czm_tau_2
    index = 2
  []
  [dn]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = Block1_Block2
    real_vector_value = interface_displacement_jump
    property_name = czm_dn
    index = 0
  []
[]

[Postprocessors]
  [normal_jump]
    type = ADSideAverageMaterialProperty
    property = czm_dn
    boundary = Block1_Block2
  []
  [sigma_n]
    type = SideAverageMaterialProperty
    property = bb_compressive_normal_stress
    boundary = Block1_Block2
  []
  [tau_1]
    type = ADSideAverageMaterialProperty
    property = czm_tau_1
    boundary = Block1_Block2
  []
  [tau_2]
    type = ADSideAverageMaterialProperty
    property = czm_tau_2
    boundary = Block1_Block2
  []
  [tau]
    type = ParsedPostprocessor
    pp_names = 'tau_1 tau_2'
    expression = 'sqrt(tau_1^2 + tau_2^2)'
  []
  [limit_tau]
    type = SideAverageMaterialProperty
    property = limit_tau
    boundary = Block1_Block2
  []
  [mu_eff]
    type = SideAverageMaterialProperty
    property = friction_coefficient_effective
    boundary = Block1_Block2
  []
  [phi_peak]
    type = SideAverageMaterialProperty
    property = bb_peak_friction_angle_degrees
    boundary = Block1_Block2
  []
  [fracture_state]
    type = SideAverageMaterialProperty
    property = fracture_state
    boundary = Block1_Block2
  []
  [cum_slip]
    type = SideAverageMaterialProperty
    property = cumulative_plastic_slip
    boundary = Block1_Block2
  []

  # --- check 1: Barton-Bandis normal closure ---
  [closure]
    type = ParsedPostprocessor
    pp_names = normal_jump
    expression = 'max(0.0, ${c0} - normal_jump)'
  []
  [sigma_n_reference]
    type = ParsedPostprocessor
    pp_names = closure
    expression = '${sigma0} * (closure / (${vm} - closure))^(1.0/${p_exp})'
  []
  [closure_rel_error]
    type = ParsedPostprocessor
    pp_names = 'sigma_n sigma_n_reference'
    expression = 'abs(sigma_n - sigma_n_reference) / max(sigma_n_reference, 1.0)'
  []

  # --- check 2: peak envelope phi_p = phi_r + JRC*log10(JCS/sigma_n) ---
  [phi_peak_reference]
    type = ParsedPostprocessor
    pp_names = sigma_n
    expression = 'if(sigma_n > 1.0, ${phi_r} + ${jrc} * log10(${jcs} / sigma_n), ${phi_r})'
  []
  [envelope_rel_error]
    type = ParsedPostprocessor
    pp_names = 'phi_peak phi_peak_reference'
    expression = 'abs(phi_peak - phi_peak_reference) / max(phi_peak_reference, 1.0)'
  []

  # --- check 3: slip weakening mu_eff = mu_sw + (tan(phi_p) - mu_sw)*exp(-(s/Dc)^m) ---
  [mu_reference]
    type = ParsedPostprocessor
    pp_names = 'phi_peak cum_slip'
    expression = '${mu_sw} + (tan(phi_peak * 0.017453292519943295) - ${mu_sw}) * exp(-(cum_slip/${dc})^${sw_exp})'
  []
  [weakening_rel_error]
    type = ParsedPostprocessor
    pp_names = 'mu_eff mu_reference'
    expression = 'abs(mu_eff - mu_reference) / max(mu_reference, 1e-3)'
  []
  [limit_tau_reference]
    type = ParsedPostprocessor
    pp_names = 'sigma_n mu_eff'
    expression = 'sigma_n * mu_eff'
  []
  [strength_rel_error]
    type = ParsedPostprocessor
    pp_names = 'limit_tau limit_tau_reference'
    expression = 'abs(limit_tau - limit_tau_reference) / max(limit_tau_reference, 1.0)'
  []

  # --- check 4: on the yield surface tau equals the strength (FractureState Slip = 2) ---
  [yield_rel_error]
    type = ParsedPostprocessor
    pp_names = 'tau limit_tau fracture_state'
    expression = 'if(fracture_state > 1.5 & fracture_state < 2.5, abs(tau - limit_tau) / max(limit_tau, 1.0), 0.0)'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  end_time = 8
  # The Barton-Bandis return map is bracketed per step, so a step demanding more slip than
  # the bracket allows raises a recoverable MooseException. Adaptive dt is part of the
  # intended usage of this law, not a workaround.
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.02
    optimal_iterations = 8
    growth_factor = 1.5
    cutback_factor = 0.5
  []
  dtmax = 0.2
  dtmin = 1e-6
  nl_abs_tol = 1e-8
  nl_rel_tol = 1e-10
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
[]
