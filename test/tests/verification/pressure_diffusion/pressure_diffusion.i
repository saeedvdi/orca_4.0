# =============================================================================
# VERIFICATION: OrcaFullySaturatedSinglePhaseDarcySUPGKernel
#
# Pins the Darcy flux term -- and with it the k/mu convention -- against the
# closed-form transient pressure diffusion in a semi-infinite saturated bar.
#
# The two kernels together assemble
#
#     (1/M) dp/dt - div[(K/mu) grad p] = 0
#
# on a RIGID skeleton (coupling_type = Hydro, so no alpha*div(du/dt) term), which
# is the linear diffusion equation with hydraulic diffusivity
#
#     c = M k / mu
#
# For p(0,t) = p0, p(x,0) = 0 on a half-space the solution is
#
#     p(x,t) = p0 erfc( x / (2 sqrt(c t)) )
#
# CONSTANTS (SW-T1 rock, matching the companion tests):
#     M   = 2.4562999362e11 Pa
#     k   = 5e-19 m^2
#     mu  = 1.002e-3 Pa s
#     c   = 1.2256985709e-4 m^2/s
#     p0  = 1e6 Pa
#
# The bar is 4 m long and the window is 1000 s, over which the diffusion length
# sqrt(4 c t) reaches 0.70 m. erfc at the far end is then 6e-16, so the
# zero-flux boundary at x = 4 is never felt and the half-space solution applies
# to well past the precision of the comparison.
#
# WHY THIS TEST EXISTS: the mobility tensor is built as K/mu inside
# OrcaTHMaterial and consumed by the kernel, with the density multiplier as a
# separate switch. Getting mu on the wrong side, or leaving the mass form on
# when the storage term is in volume form, changes c by orders of magnitude but
# still produces a smooth, monotone, entirely plausible diffusion profile. Only
# a comparison against a closed form with an independently known c catches it.
# scripts/pressure_diffusion_analytic.py does that comparison; this input file
# is its numerical half and the CSV regression.
#
# Both kernels run in VOLUME form (multiply_by_fluid_density = false) so that
# c = M k / mu exactly, with no density cancellation to reason about.
# =============================================================================

biot_coefficient       = 0.6
initial_porosity       = 0.001
fluid_bulk_modulus     = 4.7835616438e9
solid_bulk_compliance  = 1.611901e-11   # = 1/Kd, Kd = 62.037 GPa
matrix_permeability    = 5e-19
fluid_viscosity        = 1.002e-3

bar_length             = 4.0
inlet_pressure         = 1e6

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 1
    nx = 200
    xmax = ${bar_length}
  []
[]

[Variables]
  [pore_pressure]
    initial_condition = 0
  []
[]

[Kernels]
  # Storage: (1/M) dp/dt. Rigid skeleton -- no mechanics coupling -- so the
  # equation reduces to pure diffusion and c is known in closed form.
  [storage]
    type = OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel
    variable = pore_pressure
    coupling_type = Hydro
    multiply_by_fluid_density = false
  []
  # The term under test: div[(K/mu) grad p].
  [darcy]
    type = OrcaFullySaturatedSinglePhaseDarcySUPGKernel
    variable = pore_pressure
    multiply_by_fluid_density = false
  []
[]

[BCs]
  # Step change at the inlet at t = 0+. The far end is left natural (zero flux),
  # which the diffusion front never reaches within the window.
  [inlet]
    type = DirichletBC
    variable = pore_pressure
    boundary = left
    value = ${inlet_pressure}
  []
[]

[Materials]
  [rockTH]
    type = OrcaTHMaterial
    pore_pressure = pore_pressure
    initial_porosity = ${initial_porosity}
    initial_permeability = '${matrix_permeability} 0 0  0 ${matrix_permeability} 0  0 0 ${matrix_permeability}'
    fluid_density_model = constant
    fluid_density_ref = 1000
    fluid_bulk_modulus = ${fluid_bulk_modulus}
    fluid_viscosity_ref = ${fluid_viscosity}
    solid_bulk_compliance = ${solid_bulk_compliance}
    biot_modulus_model = time_dependent
  []
  [biot]
    type = OrcaBiotCoefficientMaterial
    model = user
    biot_coefficient = ${biot_coefficient}
  []
  # Zero gravity: the closed form is for pressure diffusion alone. The Darcy
  # kernel always subtracts rho*g from grad p, so this property must exist even
  # when it is not wanted.
  [gravity]
    type = OrcaGravityVectorMaterial
    gravity = '0 0 0'
  []
[]

[Postprocessors]
  # Probes spanning the profile at t = 1000 s, where sqrt(c t) = 0.3501 m:
  # eta = x/(2 sqrt(c t)) = 0.14, 0.36, 0.71, 1.43 respectively, so erfc runs
  # from 0.84 down to 0.04 and the comparison exercises the whole curve rather
  # than one convenient point.
  [p_x0p10]
    type = PointValue
    variable = pore_pressure
    point = '0.10 0 0'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [p_x0p25]
    type = PointValue
    variable = pore_pressure
    point = '0.25 0 0'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [p_x0p50]
    type = PointValue
    variable = pore_pressure
    point = '0.50 0 0'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [p_x1p00]
    type = PointValue
    variable = pore_pressure
    point = '1.00 0 0'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  # Far end: must stay at round-off. If this ever lifts, the domain is too short
  # for the half-space solution and every other number here is suspect.
  [p_far_end]
    type = PointValue
    variable = pore_pressure
    point = '4.00 0 0'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [biot_modulus]
    type = ADElementAverageMaterialProperty
    mat_prop = biot_modulus_qp
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  end_time = 1000
  dt = 5
  nl_abs_tol = 1e-10
  nl_rel_tol = 1e-9
  # Storage is 1/M ~ 4e-12 and mobility is k/mu ~ 5e-16, so every row of this
  # system is tiny while the Dirichlet row is O(1e6). Same conditioning trap as
  # mass_storage, and for the same reason: nothing in the problem sets an O(1)
  # scale on its own.
  automatic_scaling = true
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
[]
