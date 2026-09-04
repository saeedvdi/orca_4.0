######################################################################################
# BENCHMARK: two intersecting fractures -- a pressurized vertical crack terminating
#            against a compressed, frictional horizontal fracture ("T-fracture")
#
# Reference configuration follows the GEOS validation case:
#   https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/
#   validationStudies/faultMechanics/intersectFrac/Example.html
# built from inputFiles/lagrangianContactMechanics/TFrac_base.xml.
# The reference curves are the symmetric-Galerkin BEM solution of Phan et al. (2003),
# Int. J. Numer. Meth. Engng, shipped with GEOS as Aperture.txt / Slip.txt /
# NormalTraction.txt.
#
# GEOMETRY (matches mesh/frac_intersection_mesh.e exactly)
# --------------------------------------------------------
#   vertical fracture    x = 0,    y in [-50, +50]     (100 m long, pressurized)
#   horizontal fracture  y = +50,  x in [-25, +25]     ( 50 m long, frictional)
# The vertical fracture's UPPER tip lands on the MIDDLE of the horizontal one, so the
# two form a T. The lower tip is an ordinary crack tip embedded in the matrix.
#
# LOADING
# -------
#   phase 1 (t = 0 -> 1)   far-field sigma_yy ramps 0 -> -100 MPa (sigma_xx stays 0)
#   phase 2 (t = 1 -> 2)   fluid pressure in the VERTICAL fracture ramps 0 -> 100 MPa
# GEOS applies the far field as an initial condition on rock_stress component 1 with
# rollers on every outer boundary; `initial_stress` below is the same prestress, ramped
# rather than imposed in one step so the contact solve has something to follow.
#
# WHAT THIS VERIFIES -- and why it is not covered by sneddon/ or shear_compression/
# --------------------------------------------------------------------------------
# Sneddon exercises an OPEN interface, shear_compression a CLOSED SLIDING one. This case
# has BOTH AT ONCE and, crucially, has them MEET. Three things are under test that no
# single-fracture benchmark can reach:
#
#   1. The T-junction itself. Where the two fractures meet, the mesh node must separate
#      into THREE pieces (left flank, right flank, and the cap above), because the
#      vertical crack faces slide apart ALONG the horizontal fracture. If the junction
#      node is not split, the aperture and the slip are both pinned to zero exactly where
#      the reference puts their maxima. See the [Mesh] block for how this is arranged.
#   2. Interaction. The horizontal fracture is what lets the vertical crack open at its
#      upper end at all: the reference aperture there is 135 mm, not the zero a Sneddon
#      tip would give, and the peak aperture is ~3 % ABOVE the isolated-crack closed form.
#   3. Frictional response to a purely induced shear. Nothing shears the horizontal
#      fracture directly -- the far field is normal to it. Its ~67 mm of slip is driven
#      entirely by the opening of the crack beneath it, through the Coulomb limit at a
#      normal traction that the same opening is simultaneously changing.
#
# The SAME deck is run with all four interface material models, each configured to the
# identical constant-mu (30 deg, zero-cohesion) interface. All four must agree.
#
# MODEL: ADOrcaBartonBandisContactTractionFastADHardening
######################################################################################

frac_v = block_left_block_right      # vertical, pressurized
frac_h = core_cap                    # horizontal, frictional
frac_all = 'block_left_block_right core_cap'

# --- benchmark parameters (GEOS TFrac_base.xml) ---
bulk_modulus = 38.89e9
shear_modulus = 29.17e9
youngs_modulus = ${fparse 9.0 * bulk_modulus * shear_modulus / (3.0 * bulk_modulus + shear_modulus)}
poissons_ratio = ${fparse (3.0 * bulk_modulus - 2.0 * shear_modulus) / (2.0 * (3.0 * bulk_modulus + shear_modulus))}
remote_compression = 1.0e8           # sigma_yy = -100 MPa
crack_pressure = 1.0e8               # 100 MPa in the vertical fracture
friction_angle_deg = 30.0            # GEOS defaultFrictionCoefficient = 0.577350269
half_length_v = 50.0                 # vertical fracture half-length

# Isolated-crack closed form, for scale only. The T-junction is EXPECTED to beat it:
# Phan et al. put the peak at 282.2 mm, about 3 % above this.
sneddon_aperture_max = ${fparse 4.0 * (1.0 - poissons_ratio^2) * crack_pressure * half_length_v / youngs_modulus}
##########################################################
[Mesh]
  [file_mesh]
    type = FileMeshGenerator
    file = mesh/frac_intersection_mesh.e
  []
  [outer_sides]
    type = SideSetsFromNodeSetsGenerator
    input = file_mesh
  []
  # ---- Why the fractures are split in TWO passes, with a re-block in between ----
  # BreakMeshByBlockGenerator's `block_pairs` mode refuses to split any node touching
  # more than two blocks (framework/src/meshgenerators/BreakMeshByBlockGenerator.C:
  # "If it is a junction between more than two blocks, we do not split it"). That rule is
  # what we want at the three fracture TIPS -- they must stay welded -- but it would also
  # weld the T-junction shut, since that node touches the left flank, the right flank and
  # the cap above. Splitting one fracture at a time keeps every node a two-block node at
  # the moment it is split:
  #
  #   pass 1  flanks merged into `core`, so (0,50) sees {core, cap}         -> splits
  #   pass 2  `core` re-split into left/right; the core-side copy of (0,50)
  #           now sees {block_left, block_right}                            -> splits
  #
  # Net result at (0,50): three node copies -- left flank, right flank, cap -- which is
  # exactly the physical topology. Verified: 3 copies at the junction, 1 at each tip
  # (0,-50), (-25,50), (25,50), and 2 along the interiors.
  [merge_core]
    type = RenameBlockGenerator
    input = outer_sides
    old_block = 'block_left block_right'
    new_block = 'core core'
  []
  # The strip directly above the horizontal fracture. Carving it out of `matrix` makes
  # the core/cap interface coincide with the horizontal fracture and nothing else: a
  # fracture with tips inside the domain is never a whole block boundary, so the pair
  # has to be manufactured.
  [make_cap]
    type = SubdomainBoundingBoxGenerator
    input = merge_core
    block_id = 10
    block_name = cap
    bottom_left = '-25.001 49.999 -1'
    top_right = '25.001 500.001 1'
    restricted_subdomains = 'matrix'
  []
  [break_horizontal]
    type = BreakMeshByBlockGenerator
    input = make_cap
    block_pairs = 'core cap'
    split_interface = true
    add_interface_on_two_sides = true
  []
  [make_left]
    type = SubdomainBoundingBoxGenerator
    input = break_horizontal
    block_id = 11
    block_name = block_left
    bottom_left = '-26 -51 -1'
    top_right = '0 51 1'
    restricted_subdomains = 'core'
  []
  [make_right]
    type = RenameBlockGenerator
    input = make_left
    old_block = 'core'
    new_block = 'block_right'
  []
  [break_vertical]
    type = BreakMeshByBlockGenerator
    input = make_right
    block_pairs = 'block_left block_right'
    split_interface = true
    add_interface_on_two_sides = true
  []
[]
##########################################################
[GlobalParams]
  displacements = 'disp_x disp_y'
[]
##########################################################
[Variables]
  [disp_x]
    order = FIRST
    family = LAGRANGE
  []
  [disp_y]
    order = FIRST
    family = LAGRANGE
  []
[]
##########################################################
[Functions]
  # Phase 1 then phase 2. Both are ramped: the interfaces start at zero gap carrying no
  # contact traction, so a step load lets the first Newton trial interpenetrate freely.
  # The problem is rate-independent and quasi-static, so the ramp does not change the
  # final state.
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
##########################################################
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
##########################################################
[InterfaceKernels]
  [czm_mech_x]
    type = OrcaMechInterfaceKernel
    boundary = ${frac_all}
    variable = disp_x
    neighbor_var = disp_x
    component = 0
  []
  [czm_mech_y]
    type = OrcaMechInterfaceKernel
    boundary = ${frac_all}
    variable = disp_y
    neighbor_var = disp_y
    component = 1
  []
  # Fluid pressure on the VERTICAL fracture only -- the horizontal one carries no fluid.
  # The -1 coefficient is the app's tension-positive convention: it pushes the faces apart.
  [crack_pressure_x]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${frac_v}
    variable = disp_x
    neighbor_var = disp_x
    component = 0
    pressure_traction_coefficient = -1.0
  []
  [crack_pressure_y]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${frac_v}
    variable = disp_y
    neighbor_var = disp_y
    component = 1
    pressure_traction_coefficient = -1.0
  []
[]
##########################################################
[BCs]
  # GEOS constrains the normal displacement on every outer boundary (xpos/xneg,
  # ypos/yneg, zpos/zneg) and carries the far field as a prestress instead.
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
[]
##########################################################
[AuxVariables]
  # Prescribed fracture fluid pressure. Held as an AuxVariable so no flow problem is
  # solved: OrcaCZMInterfacePressure averages it across the interface and
  # OrcaCZMFluidPressureInterfaceKernel turns it into the face load.
  [pore_pressure]
    initial_condition = 0.0
  []
  # ---- One set of output variables PER FRACTURE, which is not cosmetic ----
  # These are CONSTANT MONOMIAL, i.e. one value per ELEMENT, but the elements at the
  # T-junction touch BOTH fractures: their x = 0 face is on the vertical fracture and
  # their y = 50 face is on the horizontal one. A single variable written by an aux
  # kernel spanning both boundaries therefore keeps only whichever side was visited last,
  # and it silently keeps it exactly at the junction, where both reference curves peak.
  # Splitting the variables removes the collision -- each element carries one value per
  # fracture, not one value total.
  [dn_v]
    order = CONSTANT
    family = MONOMIAL
  []
  [ds_v]
    order = CONSTANT
    family = MONOMIAL
  []
  [sigma_n_v]
    order = CONSTANT
    family = MONOMIAL
  []
  [tau_v]
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
  [tau_h]
    order = CONSTANT
    family = MONOMIAL
  []
  # Mobilized friction on the horizontal fracture. Where it slides this must sit exactly
  # on tan(30 deg) = 0.57735, independently of how hard the crack below is pushing.
  [mu_mobilized_h]
    order = CONSTANT
    family = MONOMIAL
  []
[]
##########################################################
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
  [ds_v_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = ds_v
    property = czm_ds_1
    boundary = ${frac_v}
    execute_on = TIMESTEP_END
  []
  [sigma_n_v_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = sigma_n_v
    property = czm_sigma_n
    boundary = ${frac_v}
    execute_on = TIMESTEP_END
  []
  [tau_v_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = tau_v
    property = czm_tau_1
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
  [tau_h_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    variable = tau_h
    property = czm_tau_1
    boundary = ${frac_h}
    execute_on = TIMESTEP_END
  []
[]
##########################################################
[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = ${youngs_modulus}
    poissons_ratio = ${poissons_ratio}
    strain_model = incremental
    # xx yy xy, negative in compression. This is GEOS's `SigmaY` FieldSpecification.
    initial_stress = '0 far_field_yy 0'
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
    # jrc = 0 collapses the Barton-Bandis roughness angle to zero, so
    # phi_peak = residual_friction_angle_degrees = 30 deg and mu is constant, matching
    # the GEOS <Coulomb> law with defaultFrictionCoefficient = 0.577350269.
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
  [czm_tau_1]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = ${frac_all}
    real_vector_value = interface_traction
    property_name = czm_tau_1
    index = 1
  []
[]
##########################################################
[Postprocessors]
  # --- vertical fracture: aperture ---
  [aperture_max]
    type = SideExtremeValue
    variable = dn_v
    boundary = ${frac_v}
    value_type = max
  []
  [sneddon_aperture_max]
    type = ConstantPostprocessor
    value = ${sneddon_aperture_max}
  []
  # The T-junction is expected to push this ABOVE 1. Phan et al. give 282.2/274.3 = 1.029.
  [aperture_over_sneddon]
    type = ParsedPostprocessor
    pp_names = 'aperture_max sneddon_aperture_max'
    expression = 'aperture_max / sneddon_aperture_max'
  []
  # --- horizontal fracture: normal traction and slip ---
  [sigma_n_mean_h]
    type = SideAverageValue
    variable = sigma_n_h
    boundary = ${frac_h}
  []
  # Away from the junction the reference sits near -118 MPa, i.e. the far field plus the
  # extra clamping the opening crack pushes into it.
  [sigma_n_min_h]
    type = SideExtremeValue
    variable = sigma_n_h
    boundary = ${frac_h}
    value_type = min
  []
  # At the junction the reference unloads all the way to zero: the crack pries the
  # horizontal fracture apart there. This picking up ~0 is the signature of that.
  [sigma_n_max_h]
    type = SideExtremeValue
    variable = sigma_n_h
    boundary = ${frac_h}
    value_type = max
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
  # The slip is driven entirely by the crack below, so it must be ANTISYMMETRIC about the
  # junction: this integral is the symmetry residual and belongs near zero.
  [slip_asymmetry_h]
    type = SideAverageValue
    variable = ds_h
    boundary = ${frac_h}
  []
  [tau_max_h]
    type = SideExtremeValue
    variable = tau_h
    boundary = ${frac_h}
    value_type = max
  []
  # The Coulomb check, as a scored quantity: tan(30 deg) = 0.57735.
  #
  # Both extremes land on the SAME element. Wherever the fracture slides, tau = mu*|sigma_n|
  # pointwise, so the largest shear necessarily sits where the normal traction is largest,
  # and that element is sliding here. The +1 Pa guard only keeps t = 0 finite.
  #
  # It is deliberately built from postprocessors rather than from the mean of a pointwise
  # ratio. A ParsedAux reading two other AuxVariables is not guaranteed to run after them,
  # and it silently reported the PREVIOUS step's ratio when it did not. An average is no
  # good either: tau is ANTISYMMETRIC about the junction, so its mean over this boundary is
  # identically zero and carries nothing but round-off.
  # frac_intersection_analytical.py recomputes the pointwise profile from the exported
  # tau_h and sigma_n_h columns, which has neither problem.
  [mu_peak_ratio_h]
    type = ParsedPostprocessor
    pp_names = 'tau_max_h sigma_n_min_h'
    expression = 'tau_max_h / (abs(sigma_n_min_h) + 1.0)'
  []
[]
##########################################################
[VectorPostprocessors]
  [aperture_profile]
    type = SideValueSampler
    variable = 'dn_v ds_v sigma_n_v tau_v'
    boundary = ${frac_v}
    sort_by = y
    # NOT `FINAL`: a side sampler executed on FINAL never runs its boundary loop.
    execute_on = TIMESTEP_END
  []
  [horizontal_profile]
    type = SideValueSampler
    variable = 'dn_h ds_h sigma_n_h tau_h'
    boundary = ${frac_h}
    sort_by = x
    execute_on = TIMESTEP_END
  []
[]
##########################################################
[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]
##########################################################
[Executioner]
  type = Transient
  solve_type = NEWTON
  start_time = 0.0
  end_time = 2.0
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.1
    optimal_iterations = 8
    growth_factor = 1.5
    cutback_factor = 0.5
  []
  dtmax = 0.25
  dtmin = 1e-5
  nl_abs_tol = 1e-2
  nl_rel_tol = 1e-8
  nl_max_its = 30
  l_max_its = 100
  # Direct solve, as in the rest of this suite: BoomerAMG goes DIVERGED_NANORINF on the
  # penalty-stiffened contact operator.
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_type'
  petsc_options_value = 'lu superlu_dist'
[]
##########################################################
[Outputs]
  csv = true
  exodus = true
[]
