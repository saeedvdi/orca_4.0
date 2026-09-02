# CZM regression: Barton-Bandis power-law normal closure, load and unload.
#
# Two stiff blocks separated by a cohesive interface at z = 0.5 mm. The top face is driven
# down (closing the joint) and back up (opening it). The interface carries no cohesion,
# no friction mobilisation and no dilatancy, so the ONLY active response is the recoverable
# normal closure law
#
#     sigma_n(c) = (K_ni V_m) [ c / (V_m - c) ]^(1/p),   c = c_0 - g_n
#
# The deck evaluates that closed form on the SOLVED normal jump and reports the relative
# error, so the test is an analytic verification, not just a frozen-output regression.
#
# The blocks are 1000x stiffer than the joint over this stress range, so the bulk
# contribution to the imposed displacement is < 0.1%.

E = 1e13
nu = 0.0

# Barton-Bandis normal closure
kni = 2.443e11        # Pa/m
vm  = 4.591e-5        # m
p_exp = 3.28
c0 = 4.433e-5         # m, pre-seating closure (joint already loaded at zero jump)
sigma0 = ${fparse kni * vm}

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
  # Close by 1.2 um, then reopen to +6 um relative to the pre-seated state.
  # The closing leg stops short of maximum_closure_fraction*V_m so the law stays on its
  # analytic branch (above the cap the pressure is deliberately frozen and the closed form
  # no longer applies).
  [drive]
    type = PiecewiseLinear
    x = '0  1       2'
    y = '0 -1.2e-6  6e-6'
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
  [fix_z]
    type = DirichletBC
    variable = disp_z
    boundary = back
    value = 0
  []
  [drive_z]
    type = FunctionDirichletBC
    variable = disp_z
    boundary = front
    function = drive
  []
  # uniaxial confinement
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
    use_dilatancy = false
    friction_coefficient_rough = 0.6
    friction_coefficient_smooth = 0.6
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
  [dn]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = Block1_Block2
    real_vector_value = interface_displacement_jump
    property_name = czm_dn
    index = 0
  []
[]

[Postprocessors]
  [dn]
    type = ADSideAverageMaterialProperty
    property = czm_dn
    boundary = Block1_Block2
  []
  [sigma_n]
    # compression-positive contact normal stress
    type = ADSideAverageMaterialProperty
    property = czm_sigma_n
    boundary = Block1_Block2
  []
  [pressure]
    type = ParsedPostprocessor
    pp_names = sigma_n
    expression = '-sigma_n'
  []
  # closure c = c0 - g_n, clamped at 0
  [closure]
    type = ParsedPostprocessor
    pp_names = dn
    expression = 'max(0.0, ${c0} - dn)'
  []
  # closed-form Barton-Bandis pressure at the solved closure
  [pressure_reference]
    type = ParsedPostprocessor
    pp_names = closure
    expression = '${sigma0} * (closure / (${vm} - closure))^(1.0/${p_exp})'
  []
  [pressure_rel_error]
    type = ParsedPostprocessor
    pp_names = 'pressure pressure_reference'
    expression = 'abs(pressure - pressure_reference) / max(pressure_reference, 1.0)'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  end_time = 2
  dt = 0.1
  nl_abs_tol = 1e-9
  nl_rel_tol = 1e-10
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
[]
