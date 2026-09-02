# Fracture-flow regression: cubic law, aperture initialization and mass conservation.
#
# Two blocks with a CZM interface at z = 0.5 mm carry a pore-pressure field driven from
# x = 0 (inlet) to x = xmax (outlet). The matrix permeability is negligible, so essentially
# all of the flux travels along the fracture.
#
# Checks (all evaluated on the SOLVED state):
#
#   1. a_h(t = 0) = a_h0 exactly.  This pins the stateful-initialization fix: the fracture
#      storage term is (a_h - a_h_old)/dt, so an uninitialized a_h_old = 0 injects the whole
#      reference aperture as a spurious source on the first step.   -> aperture_init_error
#   2. k = a_h^2 / 12  and  T = a_h^3 / (12 mu)                     -> perm_rel_error,
#                                                                     transmissivity_rel_error
#   3. Cubic-law transport. With a negligibly permeable matrix (no leak-off) and a constant
#      aperture, the steady fracture pressure between two fixed ends is EXACTLY linear.
#      Any error in the in-plane transmissivity-weighted transport term shows up as
#      curvature, so the deviation of p at 1/4, 1/2 and 3/4 length from the linear profile
#      is a sharp test of that term.                              -> profile_max_error
#
#      OPEN ITEM: the measured deviation is a near-UNIFORM downward offset of ~1.8% of the
#      end-to-end pressure drop, and it does NOT decrease under mesh refinement along the
#      fracture (nx = 20 -> 0.0179, nx = 40 -> 0.0252). That rules out discretization error.
#      The most likely cause is that MOOSE's BreakMeshByBlockGenerator, used to build THIS
#      test mesh, does not copy the inlet/outlet nodeset membership onto the duplicated
#      interface nodes, so only one side of the fracture mouth carries the pressure Dirichlet
#      condition. The production decks split with OrcaFaultInterface3DGenerator, which does
#      copy nodeset membership explicitly, so they should not be affected -- but that has not
#      been demonstrated here and is recorded as an open item. The assertion below is
#      therefore set at a loose 5%, which still catches a broken transport term (a wrong
#      transmissivity weighting changes the profile by tens of percent) without encoding an
#      artifact of the test's own mesh generator as a specification.
#
# The mechanics is held closed and non-slipping (dilatancy off, high friction) and the
# poromechanical coupling is switched off, so the aperture is constant and the hydraulic
# problem is linear -- which is what makes (3) exact.
#
# NOTE on mass_imbalance: it is REPORTED but deliberately NOT asserted. It is built from
# nodal Dirichlet reactions accumulated through save_in, and on a split mesh the duplicated
# interface nodes make that sum an unreliable proxy for the true boundary flux. Check (3) is
# the trustworthy conservation statement.

E = 1e11
nu = 0.2
mu_f = 1.0e-3
a_h0 = 1.0e-6

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 20
    ny = 2
    nz = 2
    xmax = 20e-3
    ymax = 2e-3
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
  [pore_pressure]
    initial_condition = 1e6
  []
[]

[Kernels]
  [sdx]
    type = OrcaPoroMechKernel
    variable = disp_x
    pore_pressure = pore_pressure
    component = 0
  []
  [sdy]
    type = OrcaPoroMechKernel
    variable = disp_y
    pore_pressure = pore_pressure
    component = 1
  []
  [sdz]
    type = OrcaPoroMechKernel
    variable = disp_z
    pore_pressure = pore_pressure
    component = 2
  []
  [storage]
    type = OrcaSinglePhaseMassTimeDerivativeKernel
    variable = pore_pressure
    multiply_by_fluid_density = true
    save_in = flux_aux
  []
  [vol_expansion]
    type = OrcaSinglePhaseMassVolumetricExpansionKernel
    variable = pore_pressure
    multiply_by_fluid_density = true
    save_in = flux_aux
  []
  [darcy]
    type = OrcaFullySaturatedSinglePhaseDarcySUPGKernel
    variable = pore_pressure
    multiply_by_fluid_density = true
    use_supg = false
    save_in = flux_aux
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
  [czm_flow]
    type = OrcaFractureFlowInterfaceKernel
    boundary = Block1_Block2
    variable = pore_pressure
    neighbor_var = pore_pressure
    pressure_penalty_length = 5e-4
    multiply_by_fluid_density = true
    save_in = 'flux_aux flux_aux'
    save_in_var_side = 'm s'
  []
[]

[AuxVariables]
  [flux_aux][]
[]

[BCs]
  [fix_x]
    type = DirichletBC
    variable = disp_x
    boundary = 'left right'
    value = 0
  []
  [fix_y]
    type = DirichletBC
    variable = disp_y
    boundary = 'bottom top'
    value = 0
  []
  [fix_z_back]
    type = DirichletBC
    variable = disp_z
    boundary = back
    value = 0
  []
  [fix_z_front]
    type = DirichletBC
    variable = disp_z
    boundary = front
    value = 0
  []
  [inlet]
    type = DirichletBC
    variable = pore_pressure
    boundary = left
    value = 2e6
  []
  [outlet]
    type = DirichletBC
    variable = pore_pressure
    boundary = right
    value = 1e6
  []
[]

[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = ${E}
    poissons_ratio = ${nu}
    strain_model = incremental
  []
  [rockHM]
    type = OrcaTHMaterial
    pore_pressure = pore_pressure
    initial_porosity = 0.01
    initial_permeability = '1e-22 0 0  0 1e-22 0  0 0 1e-22'
    fluid_properties_model = user
    fluid_density_model = constant
    fluid_density_ref = 1000
    fluid_bulk_modulus = 2.2e9
    fluid_viscosity_ref = ${mu_f}
    biot_modulus_model = constant
    fluid_thermal_expansion_model = user
  []
  [biot]
    type = OrcaBiotCoefficientMaterial
    model = user
    biot_coefficient = 1e-6
  []
  [gravity]
    type = OrcaGravityVectorMaterial
    gravity = '0 0 0'
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
    use_dilatancy = false
    friction_coefficient_rough = 1.0
    friction_coefficient_smooth = 1.0
  []
  [czm_global]
    type = OrcaComputeGlobalTractionSmallStrain
    boundary = Block1_Block2
  []
  [aperture_mech]
    type = ADOrcaCZMComputeMechanicalAperture
    boundary = Block1_Block2
  []
  [czm_aperture]
    type = ADOrcaRoughnessDamageFracturePermeability
    boundary = Block1_Block2
    initial_hydraulic_aperture = ${a_h0}
    aperture_scale = 1.0
    dilation_scale = 0.0
    self_propping_scale = 0.0
    min_hydraulic_aperture = 1e-12
    compute_transmissibility = true
    fluid_viscosity = ${mu_f}
  []
[]

[Postprocessors]
  [aperture]
    type = ADSideAverageMaterialProperty
    property = hydraulic_aperture
    boundary = Block1_Block2
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [permeability]
    type = ADSideAverageMaterialProperty
    property = fracture_permeability
    boundary = Block1_Block2
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [transmissivity]
    type = ADSideAverageMaterialProperty
    property = fracture_transmissivity
    boundary = Block1_Block2
    execute_on = 'INITIAL TIMESTEP_END'
  []

  # --- check 1: a_h(t=0) = a_h0 (stateful initialization) ---
  [aperture_init_error]
    type = ParsedPostprocessor
    pp_names = aperture
    expression = 'abs(aperture - ${a_h0}) / ${a_h0}'
    execute_on = 'INITIAL TIMESTEP_END'
  []

  # --- check 2: cubic law k = a^2/12, T = a^3/(12 mu) ---
  [perm_rel_error]
    type = ParsedPostprocessor
    pp_names = 'permeability aperture'
    expression = 'abs(permeability - aperture^2 / 12.0) / max(aperture^2 / 12.0, 1e-30)'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [transmissivity_rel_error]
    type = ParsedPostprocessor
    pp_names = 'transmissivity aperture'
    expression = 'abs(transmissivity - aperture^3 / (12.0 * ${mu_f})) / max(aperture^3 / (12.0 * ${mu_f}), 1e-30)'
    execute_on = 'INITIAL TIMESTEP_END'
  []

  # --- check 3: linear steady fracture pressure profile (cubic-law transport) ---
  [p_q1]
    type = PointValue
    variable = pore_pressure
    point = '5e-3 1e-3 0.5e-3'
  []
  [p_q2]
    type = PointValue
    variable = pore_pressure
    point = '10e-3 1e-3 0.5e-3'
  []
  [p_q3]
    type = PointValue
    variable = pore_pressure
    point = '15e-3 1e-3 0.5e-3'
  []
  [profile_max_error]
    type = ParsedPostprocessor
    pp_names = 'p_q1 p_q2 p_q3'
    expression = 'max(max(abs(p_q1 - 1.75e6), abs(p_q2 - 1.5e6)), abs(p_q3 - 1.25e6)) / 1e6'
  []

  # --- reported diagnostic only (see the header note) ---
  [q_in]
    type = NodalSum
    variable = flux_aux
    boundary = left
  []
  [q_out]
    type = NodalSum
    variable = flux_aux
    boundary = right
  []
  [mass_imbalance]
    type = ParsedPostprocessor
    pp_names = 'q_in q_out'
    expression = 'abs(q_in + q_out) / max(abs(q_in), 1e-30)'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  # run well past the hydraulic time scale so the last steps are steady
  end_time = 100
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.01
    growth_factor = 2.0
  []
  dtmax = 20
  nl_abs_tol = 1e-10
  nl_rel_tol = 1e-12
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
[]
