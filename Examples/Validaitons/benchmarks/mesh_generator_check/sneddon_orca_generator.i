######################################################################################
# MESH-GENERATOR CHECK: Sneddon, split with OrcaFaultInterface3DGenerator
#
# WHY THIS DECK EXISTS
# --------------------
# Every benchmark in ../sneddon, ../shear_compression and ../fracutre_interseciton_problem
# builds its fracture with MOOSE's stock BreakMeshByBlockGenerator. The generator the
# RESEARCH decks actually depend on -- OrcaFaultInterface3DGenerator, used by every
# Kalantar2025 OG-SH/OG-SC/OG-T deck -- had no verification against a closed-form solution
# at all. This deck supplies it.
#
# It is ../sneddon/sneddon_barton_bandis.i with exactly three changes:
#
#   1. the mesh is 3D (one element thick) instead of 2D, because
#      OrcaFaultInterface3DGenerator hard-errors on mesh_dimension() != 3;
#   2. disp_z is added and pinned on both z faces, which makes the 3D problem plane
#      strain and therefore the SAME boundary-value problem as the 2D deck;
#   3. the fracture is cut by SideSetsBetweenSubdomainsGenerator +
#      OrcaFaultInterface3DGenerator instead of BreakMeshByBlockGenerator.
#
# Everything else -- material, loading, solver, refinement -- is untouched, so any
# difference in the answer is attributable to the generator and nothing else.
#
# WHAT COUNTS AS PASSING
# ----------------------
# Refinement is 2 rather than the shipped 4, to keep a 3D direct solve affordable. The
# 2D convergence sweep (../README.md, "Mesh convergence") gives the target at that
# refinement exactly:
#
#     w_max error 5.076 %,  fitted amplitude error 1.388 %,  fitted b = 0.96195 m
#
# The generator would be verified by reproducing those numbers. It is NOT an accuracy
# claim about the generator -- 5 % is the level-2 discretization error, which both
# generators must inherit equally.
#
# RESULT: IT REPRODUCES THEM EXACTLY, ONCE THE FRONT-NODE LOGIC IS FIXED
# ----------------------------------------------------------------------
#                            this deck        BreakMeshByBlock, level 2
#     w_max error            -5.0759 %        -5.076 %
#     fitted amplitude       -1.388 %         -1.388 %
#     fitted half-length     0.96195 m        0.96195 m   (meshed: 1.0 m)
#
# The two generators now agree to the printed precision on every quantity, which is the
# statement this deck exists to make: the crack-opening amplitude, the effective crack
# length and the traction-free open state are all independent of which generator cut the
# fracture.
#
# BEFORE the fix (2026-09-02) it gave w_max +12.838 %, amplitude -1.681 % and a fitted
# half-length of 1.14696 m -- the AMPLITUDE was already right, and only the effective
# length was wrong, which localized the defect to the crack-front nodes rather than to the
# interface mechanics. The generator was splitting the front nodes at x = +-1 along with
# everything else, so the crack had free ends instead of being held shut by the intact rock
# beyond the tip, and the tip element carried 4.77e-4 m of opening (now 1.51e-4 m).
#
# See ./README.md for the two other findings this exercise produced.
#
# MODEL: ADOrcaBartonBandisContactTractionFastADHardening
######################################################################################

fracture = fracture_interface

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
    dim = 3
    nx = 80
    ny = 80
    # One element through the thickness. With disp_z pinned on both z faces this is
    # plane strain, i.e. the same boundary-value problem the 2D deck solves.
    nz = 1
    xmin = -20
    xmax = 20
    ymin = -20
    ymax = 20
    zmin = 0
    zmax = 0.5
    elem_type = HEX8
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
    # 2, not the shipped 4: a 3D direct solve at refinement 4 does not fit on a
    # workstation. ../README.md's convergence table gives the level-2 target.
    refinement = '2 2'
  []
  # OrcaFaultInterface3DGenerator splits along a SIDESET, not a block pair, so the
  # sideset has to be built first. Between two blocks it is the same surface
  # BreakMeshByBlockGenerator would have found.
  [fracture_sideset]
    type = SideSetsBetweenSubdomainsGenerator
    input = refine_crack_blocks
    primary_block = 'matrix_bottom_mid'
    paired_block = 'matrix_top_mid'
    new_boundary = 'fracture_interface'
  []
  # ...and it must be TWO-SIDED. OrcaFaultInterface3DGenerator processes each interface
  # face once with `if (elem->id() < neighbor->id()) continue;`, which assumes the sideset
  # carries BOTH sides of every face and keeps the higher-id copy. A one-sided sideset
  # loses every face whose owner has the lower id -- here, all of them -- and the result is
  # a fracture that is silently WELDED: the sidesets are still created, the interface
  # kernels still assemble, and w_max comes out exactly 0.
  [fracture_sideset_other]
    type = SideSetsBetweenSubdomainsGenerator
    input = fracture_sideset
    primary_block = 'matrix_top_mid'
    paired_block = 'matrix_bottom_mid'
    new_boundary = 'fracture_interface'
  []
  [fault_split_3d]
    type = OrcaFaultInterface3DGenerator
    input = fracture_sideset_other
    sidesets = 'fracture_interface'
    preserve_front_nodes = true
    split_only_interior_nodes = true
    add_interface_on_two_sides = true
    secondary_sidesets = 'fracture_interface_other_side'
  []
  construct_side_list_from_node_list = true
[]

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Variables]
  [disp_x][]
  [disp_y][]
  [disp_z][]
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
  [disp_z]
    type = OrcaPoroMechKernel
    variable = disp_z
    component = 2
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
    displacements = 'disp_x disp_y disp_z'
    pressure_traction_coefficient = -1.0
  []
  [crack_pressure_y]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${fracture}
    variable = disp_y
    neighbor_var = disp_y
    component = 1
    displacements = 'disp_x disp_y disp_z'
    pressure_traction_coefficient = -1.0
  []
  [czm_mech_z]
    type = OrcaMechInterfaceKernel
    boundary = ${fracture}
    variable = disp_z
    neighbor_var = disp_z
    component = 2
  []
  [crack_pressure_z]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = ${fracture}
    variable = disp_z
    neighbor_var = disp_z
    component = 2
    displacements = 'disp_x disp_y disp_z'
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
  # Plane strain: no out-of-plane displacement on either face.
  [confine_z]
    type = DirichletBC
    variable = disp_z
    preset = false
    boundary = 'front back'
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
[]
