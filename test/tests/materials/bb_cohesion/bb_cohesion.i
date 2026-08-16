# =============================================================================
# VERIFICATION: the `cohesion` / `residual_cohesion` terms of
#               ADOrcaBartonBandisContactTractionFastAD(Hardening)
#
# A single direct-shear cell: two hex blocks split at mid-height into a CZM
# interface, held under a CONSTANT NORMAL TRACTION while the top face is dragged
# in +x at a constant rate. The traction BC is what makes the gold exact --
# equilibrium fixes sigma'_n at the applied value regardless of how the joint and
# the rock share compliance, so `limit_tau` can be checked against a number
# computed by hand rather than against whatever the solve happened to produce.
#
# WHAT IS BEING PINNED
# --------------------
# Barton's law is purely frictional,
#
#     tau_lim = sigma'_n * tan(phi_r + JRC*log10(JCS/sigma'_n)),
#
# and its roughness term is mobilization-limited: it decays to zero as sigma'_n
# approaches JCS. A mated Mode-I fracture held at sigma'_n/JCS ~ 0.4 therefore
# has no way to express asperity interlock except through phi_r, which is why the
# Ye & Ghassemi (2018) tensile decks carried phi_r = 44-46 deg -- above every
# measured granite basic friction angle, and for SW-T2 essentially the paper's
# INTACT-rock friction angle. `cohesion` adds the missing sigma'_n-independent
# term and `residual_cohesion` the part of it that survives slip:
#
#     tau_lim = c(s) + sigma'_n * tan(phi_r + JRC*log10(JCS/sigma'_n))
#     c(s)    = c_res + (c - c_res) * W,     W = exp(-(s/D_c)^m)
#
# so the interlock lives where it physically belongs and phi_r stays measurable.
#
# HAND-COMPUTED GOLD at the constants below
# -----------------------------------------
#   sigma'_n  = 20 MPa (applied)
#   roughness = JRC*log10(JCS/sigma'_n) = 15.32*log10(150/20) = 15.32*0.875061
#             = 13.4059 deg
#   phi_p     = 29.756 + 13.4059 = 43.1619 deg   ->  tan(phi_p) = 0.937568
#   phi_tail  = 29.756 deg                       ->  tan(phi_r) = 0.571412
#
#   peak     (W = 1):  tau_lim = c     + 20e6*0.937568 = c     + 18.7514 MPa
#   residual (W = 0):  tau_lim = c_res + 20e6*0.571412 = c_res + 11.4282 MPa
#
#   D_c = 20 um and the pull reaches 80 um, so W runs from 1 to exp(-4^1.4)
#   = 9.5e-4: the run spans essentially the whole weakening curve.
#
# The three cases in `tests`:
#   cohesionless  c = 0,      c_res = 0     -- legacy guard: MUST reproduce the
#                                              pre-cohesion code exactly
#   cohesive      c = 20 MPa, c_res = 0     -- full interlock loss
#   retained      c = 20 MPa, c_res = 8 MPa -- interlock surviving slip
#
# `cohesive` minus `cohesionless` is exactly c*W at every step, and `retained`
# minus `cohesive` is exactly c_res*(1-W). Those are differences of outputs, so
# they hold independently of anything the normal side does.
# =============================================================================

# --- law constants (overridable from the command line) ------------------------
cohesion            = 0.0
residual_cohesion   = 0.0
phi_r               = 29.756     # granite basic friction (SW-S3 refit, 2026-08-16)
jrc                 = 15.32      # SW-T1, Ye & Ghassemi (2018) Table 1
jcs                 = 1.5e8      # = UCS, Sec. 2.1
dc                  = 2.0e-5     # slip-weakening distance D_c
sw_exponent         = 1.4

initial_normal_stiffness = 1.0e13   # K_ni; sigma0 = K_ni*V_m = 1 GPa
maximum_closure          = 1.0e-4   # V_m
penalty_tangent          = 1.0e13

normal_closure      = 2.0e-6     # m of imposed closure -> sigma_n ~ 17.7 MPa on this cell
shear_rate          = 4.0e-6     # m/s; 20 s of pull = 80 um = 4 D_c
cell                = 1.0e-3     # m, cell edge: small enough that the rock's own
                                 # elastic shear (~0.7 um) does not eat the pull

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
    xmax = ${cell}
    ymax = ${cell}
    zmax = ${cell}
  []
  [split]
    type = SubdomainBoundingBoxGenerator
    input = gen
    block_id = 2
    bottom_left = '0 0 ${fparse 0.5 * cell}'
    top_right = '${cell} ${cell} ${cell}'
  []
  [iface]
    type = BreakMeshByBlockGenerator
    input = split
    split_interface = true
  []
[]

[Problem]
  kernel_coverage_check = false
[]

[Variables]
  [disp_x]
  []
  [disp_y]
  []
  [disp_z]
  []
[]

# Dry mechanical test. OrcaPoroMechKernel is the app's only bulk momentum kernel,
# so pore pressure is carried as an aux variable pinned at zero.
[AuxVariables]
  [pore_pressure]
    initial_condition = 0.0
  []
[]

[Kernels]
  [mech_x]
    type = OrcaPoroMechKernel
    variable = disp_x
    pore_pressure = pore_pressure
    component = 0
    block = '0 2'
  []
  [mech_y]
    type = OrcaPoroMechKernel
    variable = disp_y
    pore_pressure = pore_pressure
    component = 1
    block = '0 2'
  []
  [mech_z]
    type = OrcaPoroMechKernel
    variable = disp_z
    pore_pressure = pore_pressure
    component = 2
    block = '0 2'
  []
[]

[InterfaceKernels]
  [czm_x]
    type = OrcaMechInterfaceKernel
    boundary = 'Block0_Block2'
    variable = disp_x
    neighbor_var = disp_x
    component = 0
  []
  [czm_y]
    type = OrcaMechInterfaceKernel
    boundary = 'Block0_Block2'
    variable = disp_y
    neighbor_var = disp_y
    component = 1
  []
  [czm_z]
    type = OrcaMechInterfaceKernel
    boundary = 'Block0_Block2'
    variable = disp_z
    neighbor_var = disp_z
    component = 2
  []
[]

[Materials]
  [rock]
    type = OrcaMechMaterial
    youngs_modulus = 67e9
    poissons_ratio = 0.32
    strain_model = total
    block = '0 2'
  []
  [biot]
    type = OrcaBiotCoefficientMaterial
    model = user
    biot_coefficient = 1.0e-6   # dry: pore_pressure is identically 0, so alpha only
                                # has to sit inside the material's (0, 1] range check
    block = '0 2'
  []

  [czm_jump]
    type = OrcaCZMComputeDisplacementJump
    boundary = 'Block0_Block2'
  []
  [czm_contact]
    type = OrcaBartonBandisContactTractionFastADHardening
    boundary = 'Block0_Block2'

    # Plain hyperbola (exponent 1, no pre-seating offset): the subject of this test
    # is the SHEAR law, so the normal side is kept as simple as the law allows.
    use_hyperbolic_normal_closure = true
    initial_normal_stiffness = ${initial_normal_stiffness}
    maximum_closure = ${maximum_closure}
    normal_closure_stress_exponent = 1.0
    normal_closure_offset = 0.0
    normal_unload_retention_fraction = 0.0
    penalty_tangent = ${penalty_tangent}

    jrc = ${jrc}
    jcs = ${jcs}
    residual_friction_angle_degrees = ${phi_r}
    cohesion = ${cohesion}
    residual_cohesion = ${residual_cohesion}
    use_scale_correction = false
    use_mobilized_jrc = false
    compressive_normal_stress_floor = 1e3

    use_slip_weakening = true
    characteristic_slip_distance = ${dc}
    slip_weakening_exponent = ${sw_exponent}
    slip_weakening_residual_friction_angle_degrees = ${phi_r}

    # No dilatancy, no roughness degradation: both would couple sigma'_n or the
    # exported state to slip and blur the quantity under test.
    use_dilatancy = false
    use_roughness_degradation = false

    max_plastic_slip_increment = 0.0
    tangential_viscosity = 0.0
    min_tau_limit = 0.0
    max_return_mapping_iterations = 100
    relative_tolerance = 1e-12
  []
  [czm_global_traction]
    type = OrcaComputeGlobalTractionSmallStrain
    boundary = 'Block0_Block2'
  []
[]

[BCs]
  # Bottom face fully fixed.
  [fix_x]
    type = DirichletBC
    variable = disp_x
    boundary = back
    value = 0
  []
  [fix_y]
    type = DirichletBC
    variable = disp_y
    boundary = back
    value = 0
  []
  [fix_z]
    type = DirichletBC
    variable = disp_z
    boundary = back
    value = 0
  []

  # Top face: a fixed closure (which sets sigma'_n) ramped over the first second,
  # then a constant-rate shear pull. Closure control rather than traction control,
  # because a pure traction BC leaves the top block with an unresisted rigid-body
  # mode in z until contact develops and the first Newton step will not converge.
  # sigma'_n therefore comes out at ~17.7 MPa rather than a round number -- which
  # costs nothing, because every assertion below is a DIFFERENCE between cases run
  # at identical BCs.
  [press_z]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = front
    function = '-${normal_closure} * min(t, 1.0)'
  []
  [pull_x]
    type = FunctionDirichletBC
    variable = disp_x
    boundary = front
    function = 'if(t < 1.0, 0.0, ${shear_rate} * (t - 1.0))'
  []
  [pin_y]
    type = DirichletBC
    variable = disp_y
    boundary = front
    value = 0
  []
[]

[Postprocessors]
  # The normal stress the STRENGTH law actually sees, straight from the BB material.
  [sigma_n_pp]
    type = SideAverageMaterialProperty
    property = bb_effective_normal_stress
    boundary = 'Block0_Block2'
  []
  [limit_tau_pp]
    type = SideAverageMaterialProperty
    property = limit_tau
    boundary = 'Block0_Block2'
  []
  [cohesion_effective_pp]
    type = SideAverageMaterialProperty
    property = cohesion_effective
    boundary = 'Block0_Block2'
  []
  [cumulative_slip_pp]
    type = SideAverageMaterialProperty
    property = cumulative_plastic_slip
    boundary = 'Block0_Block2'
  []
  [peak_friction_angle_pp]
    type = SideAverageMaterialProperty
    property = bb_peak_friction_angle_degrees
    boundary = 'Block0_Block2'
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
    petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
    petsc_options_value = ' lu       mumps'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  start_time = 0
  end_time = 21.0
  dt = 1.0
  nl_abs_tol = 1e-6
  nl_rel_tol = 1e-9
[]

[Outputs]
  csv = true
  file_base = bb_cohesion_out
[]
