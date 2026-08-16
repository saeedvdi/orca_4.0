# =============================================================================
# VERIFICATION: thermal term of
# OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel
#
# The kernel assembles  (1/M) dp/dt - alpha_T dT/dt [+ alpha * eps_v_dot].
# test/tests/kernels/mass_storage pins the first term and
# test/tests/verification/terzaghi pins the third; this test pins the SECOND,
# which was the last unexercised term in the combined kernel.
#
# SETUP: one element, no Darcy kernel, no BCs, no mechanics. Temperature is a
# nonlinear variable driven by ADTimeDerivative + BodyForce, so the uniform
# field T = T0 + r*t is an exact solution of the FE system (dT/dt = r at every
# node, to machine precision). The pressure equation then reduces to the scalar
# ODE
#
#     (1/M) dp/dt - alpha_T r = 0     ==>     p(t) = M alpha_T r t
#
# With the SW-T1 rock constants at the physical alpha = 0.6 (identical to the
# companion tests) and the `computed` expansion model,
#
#     alpha_T = (alpha - phi) beta_s + phi beta_f
#             = 0.599 * 2.4e-5 + 0.001 * 2.1e-4
#             = 1.4586e-5  1/K
#     M       = 2.4562999362e11 Pa
#     M alpha_T = 3.58275908694e6 Pa/K
#     r       = 1 K/s   ==>  p(10) = 3.58275908694e6 Pa   (3.58 MPa)
#
# SIGN: the term enters the residual as MINUS alpha_T dT/dt, so heating drives
# pressure UP. A flipped sign still produces a smooth, plausible-looking run --
# it just cools-and-depressurises instead -- which is why the sign is asserted
# against a signed closed form rather than a magnitude.
# =============================================================================

biot_coefficient       = 0.6
initial_porosity       = 0.001
fluid_bulk_modulus     = 4.7835616438e9
solid_bulk_compliance  = 1.611901e-11   # = 1/Kd, Kd = 62.037 GPa
matrix_permeability    = 5e-19

beta_solid             = 2.4e-5         # volumetric, drained skeleton (1/K)
beta_fluid             = 2.1e-4         # volumetric, pore fluid (1/K)

# dT/dt, held exactly by the temperature equation below.
temp_rate              = 1.0
initial_temperature    = 293.15

# Closed-form constants supplied independently of the solve, so the CSV carries
# target beside result. Overridden by the `alpha_eff_user` case in `tests`.
alpha_eff_exact        = 1.4586e-5
biot_modulus_exact     = 2.4562999362e11

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 1
    ny = 1
    nz = 1
  []
[]

[Variables]
  [pore_pressure]
    initial_condition = 0
  []
  [temperature]
    initial_condition = ${initial_temperature}
  []
[]

[Kernels]
  # The term under test. Hydro storage is present too and is what converts the
  # thermal forcing into a pressure; it is pinned separately by mass_storage.
  [storage]
    type = OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel
    variable = pore_pressure
    coupling_type = ThermoHydro
    temperature = temperature
    # Volume form, not mass form: leaving density out keeps the comparison
    # against p = M alpha_T r t exact instead of only approximate.
    multiply_by_fluid_density = false
  []

  # Temperature ramp. With a uniform initial field and no BCs or conduction,
  # int (dT/dt - r) psi = 0 is solved exactly by the uniform field T = T0 + r t,
  # so dT/dt = r to machine precision and the forcing is known analytically.
  [temperature_time]
    type = ADTimeDerivative
    variable = temperature
  []
  [temperature_ramp]
    type = BodyForce
    variable = temperature
    value = ${temp_rate}
  []
[]

[Materials]
  [rockTH]
    type = OrcaTHMaterial
    pore_pressure = pore_pressure
    temperature = temperature
    initial_porosity = ${initial_porosity}
    initial_permeability = '${matrix_permeability} 0 0  0 ${matrix_permeability} 0  0 0 ${matrix_permeability}'
    # Constant density and a constant fluid bulk modulus keep M independent of
    # the temperature ramp, so the closed form stays exact over the window.
    fluid_density_model = constant
    fluid_density_ref = 1000
    fluid_bulk_modulus = ${fluid_bulk_modulus}
    fluid_viscosity_ref = 1.002e-3
    solid_bulk_compliance = ${solid_bulk_compliance}
    biot_modulus_model = time_dependent

    volumetric_solid_thermal_expansion = ${beta_solid}
    volumetric_fluid_thermal_expansion = ${beta_fluid}
    # Required whenever temperature is coupled, but inert here: there is no
    # heat-conduction kernel, so these never enter the residual.
    dry_thermal_conductivity = '2.5 0 0  0 2.5 0  0 0 2.5'
    solid_density = 2650
    solid_specific_heat_capacity = 790
  []
  [biot]
    type = OrcaBiotCoefficientMaterial
    model = user
    biot_coefficient = ${biot_coefficient}
  []
[]

[Postprocessors]
  [pressure]
    type = ElementAverageValue
    variable = pore_pressure
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [temperature_avg]
    type = ElementAverageValue
    variable = temperature
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [alpha_eff]
    type = ADElementAverageMaterialProperty
    mat_prop = effective_thermal_expansion_coeff_qp
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [biot_modulus]
    type = ADElementAverageMaterialProperty
    mat_prop = biot_modulus_qp
    execute_on = 'INITIAL TIMESTEP_END'
  []
  # Closed-form p(t) = M alpha_T r t, evaluated independently of the solve.
  [pressure_exact]
    type = FunctionValuePostprocessor
    function = exact_p
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[Functions]
  [exact_p]
    type = ParsedFunction
    expression = 'M * a * r * t'
    symbol_names = 'M a r'
    symbol_values = '${biot_modulus_exact} ${alpha_eff_exact} ${temp_rate}'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  num_steps = 10
  dt = 1
  nl_abs_tol = 1e-12
  nl_rel_tol = 1e-10
  # Same conditioning trap as mass_storage: the pressure block's Jacobian
  # diagonal is (1/M)/dt * V ~ 2e-14 because storage is the only pressure term,
  # while the temperature block is O(1). Without scaling PETSc misjudges the
  # step on a residual that is already at round-off.
  # Deliberately NOT automatic_scaling, which the companion mass_storage test
  # does need. There, storage was the only equation in the problem, so the whole
  # residual sat at 1e-14 and PETSc could not tell convergence from noise. Here
  # the temperature equation contributes an O(1) row, so |R| starts at 0.35 and
  # one Newton step takes it to 5e-17 -- already well conditioned. Switching
  # automatic_scaling ON instead amplifies the p-row, whose two terms cancel to
  # round-off by construction, and pins |R| at a 6e-9 floor that no tolerance
  # below it can ever reach: the solve then fails with DIVERGED_LINE_SEARCH on
  # an answer that is in fact exact.
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
[]
