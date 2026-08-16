# =============================================================================
# VERIFICATION: Mandel's problem -- the poroelastic test Terzaghi cannot do
#
# Terzaghi (test/tests/verification/terzaghi) is 1D: pressure only ever decays.
# A code can reproduce it while still having the Biot coupling wrong in ways
# that only show up in a multi-axial stress state.
#
# Mandel's problem is the standard check for exactly that. A sample is squashed
# between rigid impermeable platens and drained at its sides. Because the
# platens are rigid, load shed by the draining edges is transferred INWARD, and
# the pressure at the centre RISES ABOVE its initial undrained value before
# decaying -- the Mandel-Cryer effect. It is a genuinely non-monotonic response
# that a decoupled or mis-signed formulation cannot produce at all.
#
# GEOMETRY  -a <= x <= a, -b <= y <= b, plane strain.
# Simulated as the quarter sample 0 <= x <= a, 0 <= y <= b with roller BCs at
# x = 0 and y = 0, drained at x = a.
#
# PARAMETERS -- identical to MOOSE's porous_flow mandel_constM.i, so any
# discrepancy is Orca's and not the problem set-up's. Dimensionless throughout.
#
#   a  = 1        sample half-width
#   b  = 0.1      sample half-height
#   la = 0.5      Lame lambda    -> E  = mu(3la+2mu)/(la+mu) = 1.8
#   mu = 0.75     shear modulus  -> nu = la/(2(la+mu))       = 0.2
#   K  = la + 2mu/3 = 1          -> solid_bulk_compliance    = 1
#   Kf = 8        fluid bulk modulus
#   phi= 0.1      porosity
#   a_b= 0.6      Biot coefficient
#   k/mu_f = 1.5  mobility
#   F  = 1        applied normal force per unit area
#
#   M   = 1/(phi/Kf + (a_b - phi)(1 - a_b)/K) = 4.705882   Biot modulus
#   Ku  = K + a_b^2 M                         = 2.694118   undrained bulk mod.
#   nuu = (3Ku - 2G)/(6Ku + 2G)               = 0.372627   undrained Poisson
#   B   = a_b M / Ku                          = 1.048035   Skempton
#   c   = 2 k B^2 G (1-nu)(1+nuu)^2 / (9(1-nuu)(nuu-nu))   consolidation coeff.
#
# HOW THE LOAD IS APPLIED. A rigid platen is a constraint, not a traction, and
# imposing it directly needs a contact or a Lagrange multiplier. The standard
# workaround, and the one MOOSE uses, is to invert the problem: prescribe the
# platen's downward DISPLACEMENT from the analytic solution, then verify that
# the total force it takes to produce that displacement is constant in time,
# which is the actual physical boundary condition. That is what the
# `total_downwards_force` postprocessor is for -- it is not a diagnostic, it is
# half the verification. The other half is the pressure profile, compared
# against the analytic series in scripts/mandel_analytic.py.
#
# The top_velocity table below is the analytic platen displacement. It is
# reproduced from the MOOSE reference input so that the two codes are solving
# the identically-posed problem; scripts/mandel_analytic.py regenerates it
# independently from the series solution and reports the agreement, so it is
# checked rather than trusted.
# =============================================================================

a                      = 1
b                      = 0.1
youngs_modulus         = 1.8
poissons_ratio         = 0.2
solid_bulk_compliance  = 1          # = 1/K, K = 1
fluid_bulk_modulus     = 8
initial_porosity       = 0.1
biot_coefficient       = 0.6
permeability           = 1.5        # with viscosity 1 -> mobility 1.5

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 10
    ny = 1
    nz = 1
    xmin = 0
    xmax = ${a}
    ymin = 0
    ymax = ${b}
    zmin = 0
    zmax = 1
  []
[]

[Variables]
  [disp_x]
  []
  [disp_y]
  []
  [disp_z]
  []
  [pore_pressure]
    initial_condition = 0
  []
[]

[Kernels]
  # Momentum balance with the Biot effective-stress coupling built in.
  [mech_x]
    type = OrcaPoroMechKernel
    variable = disp_x
    pore_pressure = pore_pressure
    component = 0
  []
  [mech_y]
    type = OrcaPoroMechKernel
    variable = disp_y
    pore_pressure = pore_pressure
    component = 1
  []
  [mech_z]
    type = OrcaPoroMechKernel
    variable = disp_z
    pore_pressure = pore_pressure
    component = 2
  []
  # Volume form and plain Darcy, matching terzaghi.i for the same reasons: the
  # analytic solution describes the unstabilised, undensity-weighted operator.
  [darcy]
    type = OrcaFullySaturatedSinglePhaseDarcyKernel
    variable = pore_pressure
    multiply_by_fluid_density = false
  []
  # (1/M) dp/dt + alpha * div(du/dt)
  [fluid_storage]
    type = OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel
    variable = pore_pressure
    coupling_type = HydroMechanical
    multiply_by_fluid_density = false
  []
[]

[BCs]
  # Quarter-sample symmetry.
  [roller_xmin]
    type = DirichletBC
    variable = disp_x
    value = 0
    boundary = left
  []
  [roller_ymin]
    type = DirichletBC
    variable = disp_y
    value = 0
    boundary = bottom
  []
  [plane_strain]
    type = DirichletBC
    variable = disp_z
    value = 0
    boundary = 'back front'
  []
  # Drained side face.
  [xmax_drained]
    type = DirichletBC
    variable = pore_pressure
    value = 0
    boundary = right
  []
  # The platen, imposed as displacement (see the header).
  [top_velocity]
    type = FunctionDirichletBC
    variable = disp_y
    function = top_velocity
    boundary = top
  []
[]

[Functions]
  [top_velocity]
    type = PiecewiseLinear
    x = '0 0.002 0.006   0.014   0.03    0.046   0.062   0.078   0.094   0.11    0.126   0.142   0.158   0.174   0.19 0.206 0.222 0.238 0.254 0.27 0.286 0.302 0.318 0.334 0.35 0.366 0.382 0.398 0.414 0.43 0.446 0.462 0.478 0.494 0.51 0.526 0.542 0.558 0.574 0.59 0.606 0.622 0.638 0.654 0.67 0.686 0.702'
    y = '-0.041824842    -0.042730269    -0.043412712    -0.04428867     -0.045509181    -0.04645965     -0.047268246 -0.047974749      -0.048597109     -0.0491467  -0.049632388     -0.050061697      -0.050441198     -0.050776675     -0.051073238      -0.0513354 -0.051567152      -0.051772022     -0.051953128 -0.052113227 -0.052254754 -0.052379865 -0.052490464 -0.052588233 -0.052674662 -0.052751065 -0.052818606 -0.052878312 -0.052931093 -0.052977751 -0.053018997 -0.053055459 -0.053087691 -0.053116185 -0.053141373 -0.05316364 -0.053183324 -0.053200724 -0.053216106 -0.053229704 -0.053241725 -0.053252351 -0.053261745 -0.053270049 -0.053277389 -0.053283879 -0.053289615'
  []
  [dt_fn]
    type = ParsedFunction
    expression = 'if(0.15*t < 0.01, 0.15*t, 0.01)'
  []
[]

[AuxVariables]
  [stress_yy]
    order = CONSTANT
    family = MONOMIAL
  []
  [tot_force]
    order = CONSTANT
    family = MONOMIAL
  []
[]

[AuxKernels]
  # ADMaterialRankTwoTensorAux, not solid_mechanics' ADRankTwoAux: Orca's stress
  # is an AD property and ADRankTwoAux is not registered in this app.
  [stress_yy]
    type = ADMaterialRankTwoTensorAux
    property = stress
    variable = stress_yy
    i = 1
    j = 1
  []
  # Total (not effective) downward stress on the platen. This must stay at the
  # applied F = 1 for the whole run: it is the boundary condition the prescribed
  # displacement is standing in for.
  [tot_force]
    type = ParsedAux
    coupled_variables = 'stress_yy pore_pressure'
    execute_on = timestep_end
    variable = tot_force
    expression = '-stress_yy + ${biot_coefficient} * pore_pressure'
  []
[]

[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = ${youngs_modulus}
    poissons_ratio = ${poissons_ratio}
    strain_model = incremental
  []
  [rockTH]
    type = OrcaTHMaterial
    pore_pressure = pore_pressure
    initial_porosity = ${initial_porosity}
    initial_permeability = '${permeability} 0 0  0 ${permeability} 0  0 0 ${permeability}'
    fluid_density_model = constant
    fluid_density_ref = 1
    fluid_bulk_modulus = ${fluid_bulk_modulus}
    fluid_viscosity_ref = 1
    solid_bulk_compliance = ${solid_bulk_compliance}
    # Constant M, matching the analytic solution's assumption and the MOOSE
    # reference's constant_biot_modulus = 4.7058823529.
    biot_modulus_model = constant
  []
  [biot]
    type = OrcaBiotCoefficientMaterial
    model = user
    biot_coefficient = ${biot_coefficient}
  []
  [gravity]
    type = OrcaGravityVectorMaterial
    gravity = '0 0 0'
  []
[]

[Postprocessors]
  # Pressure across the half-width. p0 is the centre, where the Mandel-Cryer
  # overshoot appears; p99 is the drained edge and stays at 0.
  [p0]
    type = PointValue
    point = '0.0 0 0'
    variable = pore_pressure
  []
  [p2]
    type = PointValue
    point = '0.2 0 0'
    variable = pore_pressure
  []
  [p4]
    type = PointValue
    point = '0.4 0 0'
    variable = pore_pressure
  []
  [p6]
    type = PointValue
    point = '0.6 0 0'
    variable = pore_pressure
  []
  [p8]
    type = PointValue
    point = '0.8 0 0'
    variable = pore_pressure
  []
  [p99]
    type = PointValue
    point = '1 0 0'
    variable = pore_pressure
  []
  [xdisp]
    type = PointValue
    point = '1 0.1 0'
    variable = disp_x
  []
  [ydisp]
    type = PointValue
    point = '1 0.1 0'
    variable = disp_y
  []
  # Half the verification: this is the physical boundary condition.
  [total_downwards_force]
    type = ElementAverageValue
    variable = tot_force
  []
  [dt]
    type = FunctionValuePostprocessor
    function = dt_fn
    outputs = none
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
  start_time = 0
  end_time = 0.7
  nl_abs_tol = 1e-14
  nl_rel_tol = 1e-10
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
  petsc_options_value = 'lu mumps'
  [TimeStepper]
    type = PostprocessorDT
    postprocessor = dt
    dt = 0.001
  []
[]

[Outputs]
  execute_on = 'timestep_end'
  [csv]
    type = CSV
    time_step_interval = 3
  []
[]
