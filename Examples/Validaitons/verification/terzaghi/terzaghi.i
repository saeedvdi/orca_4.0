# Terzaghi 1D consolidation — HM benchmark
#
# 1D column of height H=1 m along z-axis.
# Base (z=0): fixed vertically, impermeable.
# Top  (z=H): constant compressive load q, freely drained (p=0).
# Lateral faces: fully confined (disp_x = disp_y = 0).
#
# Reference: Terzaghi (1943) — classical 1D consolidation.
# Setup follows the MOOSE PorousFlow poroelasticity validation: start from an
# unstressed, unpressurised column, then apply the load in the first transient
# increment. The analytical curve is the t=0+ undrained state.
# Compare with: terzaghi_analytical.py
#
# Material (must match the Python script):
#   E = 1e5 Pa,  nu = 0.2
#   K = 55556 Pa,  G = 41667 Pa,  Mc = lambda+2G = 111111 Pa
#   phi = 0.3,  alpha_biot = 1,  k = 1e-10 m^2,  mu = 1e-3 Pa.s
#   Kf = 1e12 Pa approximates the incompressible-fluid analytical assumption
#   M = Kf/phi = 3.333e12 Pa
#   cv = (k/mu)/(1/M + alpha^2/Mc) = 0.01111 m^2/s  =>  tc = H^2/cv = 90 s
##########################################################

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

##########################################################
[Mesh]
  type = GeneratedMesh
  dim  = 3
  nx   = 1
  ny   = 1
  nz   = 50
  xmin = 0
  xmax = 0.01
  ymin = 0
  ymax = 0.01
  zmin = 0
  zmax = 1.0
[]

##########################################################
[Variables]
  [pore_pressure]
    order  = FIRST
    family = LAGRANGE
  []
  [disp_x]
    order  = FIRST
    family = LAGRANGE
  []
  [disp_y]
    order  = FIRST
    family = LAGRANGE
  []
  [disp_z]
    order  = FIRST
    family = LAGRANGE
  []
[]

##########################################################
# Initial condition: unstressed/unpressurised state, as in the MOOSE
# PorousFlow Terzaghi validation. The first transient increment applies q and
# establishes the analytical undrained excess pressure p0 ~= q.
[ICs]
  [init_pp]
    type     = ConstantIC
    variable = pore_pressure
    value    = 0
  []
[]

##########################################################
[Kernels]
  # ---- Mechanics ---------------------------------------------------
  [mech_x]
    type         = OrcaPoroMechKernel
    variable     = disp_x
    pore_pressure = pore_pressure
    component    = 0
    displacements = 'disp_x disp_y disp_z'
  []
  [mech_y]
    type         = OrcaPoroMechKernel
    variable     = disp_y
    pore_pressure = pore_pressure
    component    = 1
    displacements = 'disp_x disp_y disp_z'
  []
  [mech_z]
    type         = OrcaPoroMechKernel
    variable     = disp_z
    pore_pressure = pore_pressure
    component    = 2
    displacements = 'disp_x disp_y disp_z'
  []

  # ---- Fluid mass balance ------------------------------------------
  # (1/M)*dp/dt + alpha*d(eps_v)/dt + div(q) = 0   [volume form]
  # These are exactly the kernels used by the production Ye (2018) decks, so this benchmark
  # verifies the code path that the validation runs exercise.
  [fluid_storage]
    type = OrcaSinglePhaseMassTimeDerivativeKernel
    variable = pore_pressure
    multiply_by_fluid_density = false
  []
  [vol_expansion]
    type = OrcaSinglePhaseMassVolumetricExpansionKernel
    variable = pore_pressure
    multiply_by_fluid_density = false
  []

  # Darcy flux: -div( (k/mu)*grad(p) )
  [darcy]
    type = OrcaFullySaturatedSinglePhaseDarcySUPGKernel
    variable = pore_pressure
    multiply_by_fluid_density = false
    use_supg = false
  []
[]

##########################################################
[BCs]
  # Laterally confined — 1D deformation only in z
  [conf_x_left]
    type     = DirichletBC
    variable = disp_x
    boundary = 'left'
    value    = 0
  []
  [conf_x_right]
    type     = DirichletBC
    variable = disp_x
    boundary = 'right'
    value    = 0
  []
  [conf_y_bottom]
    type     = DirichletBC
    variable = disp_y
    boundary = 'bottom'
    value    = 0
  []
  [conf_y_top]
    type     = DirichletBC
    variable = disp_y
    boundary = 'top'
    value    = 0
  []

  # Impermeable fixed base (z=0)
  [base_fixed_z]
    type     = DirichletBC
    variable = disp_z
    boundary = 'back'
    value    = 0
  []

  # Constant compressive load at top (z=H, front face)
  # NeumannBC applies total traction t_z = -q (downward)
  [top_load]
    type     = NeumannBC
    variable = disp_z
    boundary = 'front'
    value    = -1000  # Pa, compressive
  []

  # Drained top boundary
  [drainage]
    type     = DirichletBC
    variable = pore_pressure
    boundary = 'front'
    value    = 0
  []
[]

##########################################################
[Materials]
  # Mechanics must be declared first so bulk_modulus is visible to OrcaTHMaterial
  [mech]
    type           = OrcaMechMaterial
    displacements  = 'disp_x disp_y disp_z'
    youngs_modulus = 1e5   # Pa
    poissons_ratio = 0.2
    strain_model   = incremental  # required for vol_strain_rate
  []

  [rockHM]
    type = OrcaTHMaterial
    pore_pressure = pore_pressure
    # temperature NOT coupled: HM only

    initial_porosity    = 0.3
    initial_permeability = '1e-10 0 0   0 1e-10 0   0 0 1e-10'  # m^2

    fluid_properties_model = user
    fluid_density_model    = constant   # no temperature coupling
    fluid_density_ref      = 1000       # kg/m^3
    fluid_bulk_modulus     = 1e12       # Pa, approximates incompressible fluid
    fluid_viscosity_ref    = 1e-3       # Pa.s

    # Biot modulus is derived from bulk_modulus (from OrcaMechMaterial)
    # and fluid_bulk_modulus. For alpha=1: M = Kf/phi.
    biot_modulus_model = constant

    # Required for HM without temperature to avoid paramError in fluid branch
    fluid_thermal_expansion_model = user
  []

  [biot]
    type             = OrcaBiotCoefficientMaterial
    model            = user
    biot_coefficient = 1.0
  []

  [gravity]
    type    = OrcaGravityVectorMaterial
    gravity = '0 0 0'
  []
[]

##########################################################
[Postprocessors]
  # Pore pressure along the column (x,y at mid-face of thin slab)
  [p_z0]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.005 0.005 0.0'
    use_displaced_mesh = false
  []
  [p_z025]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.005 0.005 0.25'
    use_displaced_mesh = false
  []
  [p_z050]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.005 0.005 0.5'
    use_displaced_mesh = false
  []
  [p_z075]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.005 0.005 0.75'
    use_displaced_mesh = false
  []
  [p_z100]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.005 0.005 1.0'
    use_displaced_mesh = false
  []

  # Vertical displacement at top (settlement)
  [uz_top]
    type             = PointValue
    variable         = disp_z
    point            = '0.005 0.005 1.0'
    use_displaced_mesh = false
  []
[]

##########################################################
[Preconditioning]
  [smp]
    type                            = SMP
    full                            = true
    petsc_options_iname             = '-pc_type -pc_factor_mat_solver_package'
    petsc_options_value             = ' lu       mumps'
  []
[]

##########################################################
[Executioner]
  type       = Transient
  solve_type = Newton
  start_time = 0
  end_time   = 500   # ~5.5 * tc  (tc = 90 s)

  [TimeStepper]
    # Fine steps at early time, coarser later
    # Refined 4x vs. the original schedule. The scheme is first order in time and the
    # remaining error is entirely temporal: with this schedule the peak error is 0.50% of p0
    # (was 1.93%), and a further 4x refinement gives 0.12% -- clean first-order convergence.
    # Spatial refinement (nz = 50 -> 100 -> 200) does not change the error.
    type     = FunctionDT
    function = 'if(t<2, 0.025, if(t<20, 0.25, if(t<100, 1.25, 2.5)))'
  []

  l_max_its  = 50
  l_tol      = 1e-4
  nl_max_its = 20
  # The column volume is small, so an absolute tolerance of 1e-8 can accept
  # an unchanged pressure field after the first few steps.
  nl_abs_tol = 1e-14
[]

##########################################################
[Outputs]
  file_base = terzaghi
  exodus    = false
  [csv]
    type = CSV
  []
[]
