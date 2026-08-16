# =============================================================================
# VERIFICATION: Terzaghi 1D consolidation -- coupled poroelasticity
#
# The first COUPLED verification in this repo. The two companion tests
# (test/tests/materials/biot_modulus, test/tests/kernels/mass_storage) pin the
# storage term in isolation; this one exercises the whole HM path at once --
# OrcaPoroMechKernel, the Darcy kernel, and the combined mass kernel in
# HydroMechanical mode -- against a closed-form solution.
#
# PROBLEM (Verruijt, "Theory and Problems of Poroelasticity", TU Delft 2013,
# section 2.2; same setup as MOOSE's porous_flow terzaghi.i so the two can be
# cross-checked directly)
#
# A saturated column of height h sits in a bath. Sides and base are confined and
# impermeable. At t=0 a normal stress q is applied to the top, which is drained
# (p = 0). The column consolidates as fluid is squeezed out of the top.
#
# PARAMETERS -- chosen to match the MOOSE reference exactly, so any discrepancy
# is Orca's and not the problem set-up's. Dimensionless units throughout.
#
#   h   = 10          column height
#   la  = 2           Lame lambda      -> E  = mu(3la+2mu)/(la+mu) = 7.2
#   mu  = 3           shear modulus    -> nu = la/(2(la+mu))       = 0.2
#   K   = la + 2mu/3  = 4              -> solid_bulk_compliance    = 0.25
#   m   = 1/(K+4mu/3) = 0.125          confined compressibility
#   Kf  = 8           fluid bulk modulus
#   phi = 0.1         porosity
#   a   = 0.6         Biot coefficient
#   k/mu_f = 1.5      mobility (permeability 1.5, viscosity 1)
#   q   = 1           applied normal stress
#
# The storativity in Verruijt's solution is
#
#   S = phi/Kf + (a - phi)(1 - a)/K = 0.0125 + 0.05 = 0.0625
#
# which is ALGEBRAICALLY IDENTICAL to Orca's 1/M in OrcaTHMaterial::
# computeBiotModulus. That is a meaningful cross-check in itself: Orca's Biot
# modulus is the Verruijt storativity, so M = 1/S = 16 here. The analytic
# solution assumes constant M, hence biot_modulus_model = constant below.
#
#   c  = k/(S + a^2 m) = 1.5/0.1075   = 13.95348837   consolidation coefficient
#   p0 = a m q/(S + a^2 m) = 0.075/0.1075 = 0.69767442  undrained pressure
#
# ANALYTIC SOLUTION (z measured up from the sealed base, drained face at z=h)
#
#   p(z,t) = (4 p0/pi) SUM_{k>=1} [(-1)^(k-1)/(2k-1)]
#                       * cos((2k-1) pi z / (2h))
#                       * exp(-(2k-1)^2 pi^2 c t / (4 h^2))
#
# The gold file is a regression lock. The comparison against the series above
# was done separately, in scripts/terzaghi_analytic.py, and its measured error
# is recorded in doc/TODO.md section L -- so the numbers here are verified
# against mathematics, not merely frozen from whatever the code first printed.
# =============================================================================

h                      = 10
youngs_modulus         = 7.2
poissons_ratio         = 0.2
solid_bulk_compliance  = 0.25       # = 1/K, K = 4
fluid_bulk_modulus     = 8
initial_porosity       = 0.1
biot_coefficient       = 0.6
permeability           = 1.5        # with viscosity 1 -> mobility 1.5
applied_stress         = 1

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 1
    ny = 1
    nz = 20
    xmin = -1
    xmax = 1
    ymin = -1
    ymax = 1
    zmin = 0
    zmax = ${h}
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
  # Volume form (no density weighting) so the discrete problem is exactly the
  # one the analytic solution describes. Plain Darcy, not the SUPG variant:
  # this problem is diffusion-dominated and needs no stabilisation, and adding
  # it would mean verifying a stabilised operator against an unstabilised
  # analytic solution.
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
  [confine_x]
    type = DirichletBC
    variable = disp_x
    value = 0
    boundary = 'left right'
  []
  [confine_y]
    type = DirichletBC
    variable = disp_y
    value = 0
    boundary = 'bottom top'
  []
  [base_fixed]
    type = DirichletBC
    variable = disp_z
    value = 0
    boundary = back
  []
  [top_drained]
    type = DirichletBC
    variable = pore_pressure
    value = 0
    boundary = front
  []
  # Compressive normal stress q on the drained face.
  [top_load]
    type = NeumannBC
    variable = disp_z
    value = -${applied_stress}
    boundary = front
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
    # Constant, to match the analytic solution's constant-M assumption.
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
  # Pressure down the column. z=0 is the sealed base, where the undrained
  # pressure persists longest; z=10 is the drained face and stays at 0.
  [p0]
    type = PointValue
    variable = pore_pressure
    point = '0 0 0'
  []
  [p2]
    type = PointValue
    variable = pore_pressure
    point = '0 0 2'
  []
  [p5]
    type = PointValue
    variable = pore_pressure
    point = '0 0 5'
  []
  [p8]
    type = PointValue
    variable = pore_pressure
    point = '0 0 8'
  []
  # Settlement of the loaded face (negative = downward).
  [uz_top]
    type = PointValue
    variable = disp_z
    point = '0 0 10'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  end_time = 10
  # dt must be capped. Backward Euler decays too SLOWLY at large lambda*dt, and
  # with an uncapped growth_factor dt reaches ~2.5 by t=10, which alone costs
  # 5% error -- independent of mesh, so it hides as if it were a physics defect.
  dtmax = 0.025
  automatic_scaling = true
  nl_abs_tol = 1e-12
  nl_rel_tol = 1e-10
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
  petsc_options_value = 'lu mumps'
  [TimeSteppers]
    [geom]
      type = IterationAdaptiveDT
      dt = 0.003
      growth_factor = 1.4
      cutback_factor = 0.5
      optimal_iterations = 10
    []
  []
[]

[Outputs]
  csv = true
[]
