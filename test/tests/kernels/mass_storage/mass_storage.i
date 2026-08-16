# =============================================================================
# VERIFICATION: OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel
#
# Pins the storage term against a closed-form solution, and in particular pins
# the DIRECTION of the Biot-modulus convention.
#
# The kernel assembles   (1/M) dp/dt  [+ thermal] [+ alpha * eps_v_dot]
# and OrcaTHMaterial stores **M** in `biot_modulus_qp`, so the kernel must
# DIVIDE by that property. Source line reads
#
#     _storage_rate_p = dpdt * 1/_biot_modulus[_qp];
#
# which is `(dpdt * 1) / M` by left-associativity -- a division, and correct.
# It is easy to misread as a multiplication, and two comments in that file used
# to assert the property held 1/M, which would make multiplication the "fix".
# This test exists so that mistake cannot land silently.
#
# SETUP: one element, no Darcy kernel, no BCs -- so there is no spatial
# transport and every node obeys the same scalar ODE:
#
#     (1/M) dp/dt - q = 0     ==>     p(t) = M * q * t
#
# With the SW-T1 constants at the physical alpha = 0.6 (see the companion test
# test/tests/materials/biot_modulus):
#
#     M     = 2.4562999362e11 Pa
#     q     = 1e-6
#     dp/dt = M*q = 2.4562999362e5 Pa/s
#     p(10) = 2.4562999362e6 Pa  (2.46 MPa -- a realistic pore pressure)
#
# If the division were flipped to a multiplication the rate would be q/M
# instead of M*q -- wrong by a factor of M^2 = 6.03e22 -- so this test fails
# unmissably rather than subtly.
#
# The `alpha_unphysical` case drives alpha = 1e-12, where M = 5.1832204827e12
# and the expected p(10) = 5.1832204827e7 Pa. The 21x jump in pressure response
# between the two cases is the whole reason the Biot A/B campaign was run: it is
# a recalibration of the storage compliance, not a cosmetic parameter change.
# =============================================================================

biot_coefficient       = 0.6
initial_porosity       = 0.001
fluid_bulk_modulus     = 4.7835616438e9
solid_bulk_compliance  = 1.611901e-11   # = 1/Kd, Kd = 62.037 GPa
matrix_permeability    = 5e-19
# Chosen so the response lands in a realistic pore-pressure range (MPa over the
# 10 s window) rather than micro-Pascals: q=1e-11 put the residual at 1e-12 and
# PETSc's convergence test then misjudged the step.
source_q               = 1e-6
# Closed-form M for the active alpha, supplied independently of the solve so the
# CSV carries target beside result. Overridden together with biot_coefficient by
# the alpha_unphysical case in `tests`.
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
[]

[Kernels]
  # The term under test.
  [storage]
    type = OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel
    variable = pore_pressure
    coupling_type = Hydro
    # Volume form, not mass form: leaving density out keeps the comparison
    # against p = M*q*t exact instead of only approximate.
    multiply_by_fluid_density = false
  []
  # Constant volumetric source q. MOOSE's BodyForce contributes -q to the
  # residual, so the assembled equation is (1/M) dp/dt - q = 0.
  [source]
    type = BodyForce
    variable = pore_pressure
    value = ${source_q}
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
    fluid_viscosity_ref = 1.002e-3
    solid_bulk_compliance = ${solid_bulk_compliance}
    biot_modulus_model = time_dependent
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
  [biot_modulus]
    type = ADElementAverageMaterialProperty
    mat_prop = biot_modulus_qp
    execute_on = 'INITIAL TIMESTEP_END'
  []
  # Closed-form p(t) = M*q*t, evaluated independently of the solve so the CSV
  # carries the target next to the result.
  [pressure_exact]
    type = FunctionValuePostprocessor
    function = exact_p
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[Functions]
  [exact_p]
    type = ParsedFunction
    expression = 'M * q * t'
    symbol_names = 'M q'
    symbol_values = '${biot_modulus_exact} ${source_q}'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  num_steps = 10
  dt = 1
  nl_abs_tol = 1e-14
  nl_rel_tol = 1e-10
  # The Jacobian diagonal here is (1/M)/dt * V ~ 2e-14, because storage is the
  # ONLY term in the equation -- a production deck's Darcy term would dominate
  # and hide this. Without scaling, PETSc reports a false non-convergence at
  # dt >= 0.25 even though one Newton step already drives |R| to 6e-28.
  automatic_scaling = true
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
[]
