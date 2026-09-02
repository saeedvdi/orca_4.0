# CZM regression: Coulomb return map + roughness weakening + dilation dissipation limiter.
#
# Direct shear of two stiff blocks separated by a cohesive-contact-friction interface.
# The normal traction is held constant at the pre-seated joint stress (~31 MPa) so the
# specimen starts in equilibrium; the top block is then sheared in x.
#
# Three properties are checked in-deck against closed forms evaluated on the SOLVED state,
# so this is an analytic verification of the constitutive update rather than a frozen-output
# regression:
#
#   1. On the yield surface,  tau = Y  with  Y = c(R) + mu(R) * p     -> yield_rel_error
#   2. The strength interpolation Y(R) reproduces the roughness law   -> strength_rel_error
#   3. The dilation limiter enforces  p * dg_np  <=  (1 - eps_D) * Y * dgamma
#      i.e.  dilation_ratio <= limiter_bound                          -> limiter_violation
#
# (3) is the check that matters most: with these parameters the limiter, not the dilation
# angle, is what actually sets dn/ds, so the bound must hold exactly at every step.

E = 1e13
nu = 0.0

kni = 2.443e11
vm = 4.591e-5
p_exp = 3.28
c0 = 4.433e-5

fcr = 0.90              # friction at R = 1
fcs = 0.20              # friction at R = R_res
r0 = 0.45               # initial roughness
rres = 0.10             # residual roughness
ld = 1.0e-4             # roughness decay distance
eps_d = 0.10            # dissipation margin

# Normal traction that puts the PRE-SEATED joint (closure = c0 at zero jump) in exact
# equilibrium at t = 0:  sigma_n(c0) = (K_ni V_m) [c0/(V_m - c0)]^(1/p).
sigma_preseat = ${fparse kni * vm * (c0 / (vm - c0))^(1.0 / p_exp)}

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
  # Constant-normal-load direct shear (the standard laboratory protocol). The applied
  # traction equals the pre-seated joint stress, so t = 0 is in exact equilibrium and the
  # joint then dilates freely against a FIXED normal stress -- which keeps the closure on
  # the analytic branch of the Barton-Bandis law instead of locking against a rigid platen.
  [normal_drive]
    type = ConstantFunction
    value = ${fparse -sigma_preseat}
  []
  [shear_drive]
    type = PiecewiseLinear
    x = '0 6'
    y = '0 150e-6'
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
  [base]
    type = DirichletBC
    variable = disp_z
    boundary = back
    value = 0
  []
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
  [top_z]
    type = FunctionNeumannBC
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
    type = ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile
    boundary = Block1_Block2
    enable_tensile_cohesion = false
    penalty_normal = 1e13
    penalty_tangent = 1e13
    use_hyperbolic_normal_closure = true
    initial_normal_stiffness = ${kni}
    maximum_closure = ${vm}
    normal_closure_stress_exponent = ${p_exp}
    normal_closure_offset = ${c0}

    initial_roughness = ${r0}
    residual_roughness = ${rres}
    roughness_decay_distance = ${ld}
    friction_coefficient_rough = ${fcr}
    friction_coefficient_smooth = ${fcs}
    cohesion_rough = 0
    cohesion_smooth = 0

    use_dilatancy = true
    dilation_opens_joint = true
    dilation_angle_peak_degrees = 20.0
    dilation_angle_residual_degrees = 8.0
    dilation_decay_distance = 1.0e-4
    dilation_decay_exponent = 1.0
    dissipation_margin = ${eps_d}
  []
  [czm_global]
    type = OrcaComputeGlobalTractionSmallStrain
    boundary = Block1_Block2
  []
  [sigma_n]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = Block1_Block2
    real_vector_value = interface_traction
    property_name = czm_sigma_n
    index = 0
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
  [ds_1]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = Block1_Block2
    real_vector_value = interface_displacement_jump
    property_name = czm_ds_1
    index = 1
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
  [pressure]
    type = ADSideAverageMaterialProperty
    property = normal_contact_pressure
    boundary = Block1_Block2
  []
  [normal_jump]
    type = ADSideAverageMaterialProperty
    property = czm_dn
    boundary = Block1_Block2
  []
  [normal_plastic_jump]
    type = ADSideAverageMaterialProperty
    property = normal_plastic_jump
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
    type = ADSideAverageMaterialProperty
    property = limit_tau
    boundary = Block1_Block2
  []
  [roughness]
    type = ADSideAverageMaterialProperty
    property = roughness_state
    boundary = Block1_Block2
  []
  [mu_eff]
    type = ADSideAverageMaterialProperty
    property = friction_coefficient_effective
    boundary = Block1_Block2
  []
  [fracture_state]
    type = ADSideAverageMaterialProperty
    property = fracture_state
    boundary = Block1_Block2
  []
  [cum_slip]
    type = ADSideAverageMaterialProperty
    property = cumulative_plastic_slip
    boundary = Block1_Block2
  []
  [slip_inc]
    type = ADSideAverageMaterialProperty
    property = plastic_slip_increment
    boundary = Block1_Block2
  []
  [dilation_inc]
    type = ADSideAverageMaterialProperty
    property = dilation_jump_increment
    boundary = Block1_Block2
  []

  # --- check 1: on the yield surface tau equals the strength ---
  # FractureState enum values: Stick = 0, Slip = 2, Open = 3.
  [yield_rel_error]
    type = ParsedPostprocessor
    pp_names = 'tau limit_tau fracture_state'
    expression = 'if(fracture_state > 1.5 & fracture_state < 2.5, abs(tau - limit_tau) / max(limit_tau, 1.0), 0.0)'
  []

  # --- check 2: strength reproduces the roughness interpolation Y = mu(Rbar) * p ---
  [mu_reference]
    type = ParsedPostprocessor
    pp_names = roughness
    expression = '${fcs} + (${fcr} - ${fcs}) * (roughness - ${rres}) / (1.0 - ${rres})'
  []
  [strength_rel_error]
    type = ParsedPostprocessor
    pp_names = 'mu_eff mu_reference'
    expression = 'abs(mu_eff - mu_reference) / max(mu_reference, 1e-3)'
  []

  # --- check 3: dilation dissipation limiter p*dg_np <= (1-eps_D)*Y*dgamma ---
  [dilation_work]
    type = ParsedPostprocessor
    pp_names = 'pressure dilation_inc'
    expression = 'pressure * dilation_inc'
  []
  [admissible_work]
    type = ParsedPostprocessor
    pp_names = 'limit_tau slip_inc'
    expression = '(1.0 - ${eps_d}) * limit_tau * slip_inc'
  []
  [closure_headroom]
    # closure / (maximum_closure_fraction * V_m); must stay below 1 so the normal law is on
    # its analytic branch throughout (above the cap the pressure is deliberately frozen)
    type = ParsedPostprocessor
    pp_names = 'normal_jump normal_plastic_jump'
    expression = '(${c0} + normal_plastic_jump - normal_jump) / (0.999 * ${vm})'
  []
  [limiter_violation]
    type = ParsedPostprocessor
    pp_names = 'dilation_work admissible_work'
    # positive only if the limiter has been breached; 1e-6 relative slack for round-off
    expression = 'max(0.0, dilation_work - admissible_work * (1.0 + 1e-6)) / max(admissible_work, 1.0)'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  end_time = 6
  dt = 0.1
  nl_abs_tol = 1e-9
  nl_rel_tol = 1e-10
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
[]
