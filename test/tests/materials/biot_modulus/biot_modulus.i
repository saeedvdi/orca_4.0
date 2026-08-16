# =============================================================================
# VERIFICATION: OrcaTHMaterial::computeBiotModulus
#
# Pins the storage formula against a hand-computable value. The material
# computes the Biot modulus M as
#
#     1/M = (1 - a)(a - phi) * Cs + phi / Kf          Cs = solid_bulk_compliance = 1/Kd
#     M   = 1 / [ (1 - a)(a - phi)/Kd + phi/Kf ]
#
# and stores **M** (not 1/M) in the material property `biot_modulus_qp`.
# That direction matters: the consuming kernel divides by this property, so a
# test that only checked "some positive number came out" would not catch an
# inversion. The gold values below are computed independently in
#     doc/biot_alpha_study_2026-08-15.md, section 2
# from the SW-T1 rock constants, so the two agree by derivation, not by
# copying whatever the code happened to print.
#
# Default case is SW-T1 with the physical alpha = 0.6:
#     E  = 67 GPa, nu = 0.32  ->  Kd = E/(3(1-2nu)) = 62.037 GPa
#     Cs = 1/Kd               =  1.611901e-11 1/Pa
#     phi = 0.001, Kf = 4.7835616438 GPa
#
#     1/M = 0.4 * 0.599 * 1.611901e-11 + 0.001/4.7835616438e9
#         = 3.862115e-12 + 2.090480e-13
#         = 4.071163e-12
#     M   = 2.456301e11 Pa
#
# The `alpha_unphysical` case in `tests` drives alpha = 1e-12 (the value SW-S3,
# SW-T1 and SW-T2 carried) and exists to lock in a specific, easily-missed
# consequence: because alpha < phi, the factor (a - phi) goes NEGATIVE, so the
# grain-compressibility term SUBTRACTS 7.7% of the fluid storage instead of
# adding to it. That is a sharper statement than "poroelastically decoupled",
# and it is exactly the kind of sign behaviour a regression test should hold.
# =============================================================================

# --- rock/fluid constants (overridable from the command line) -----------------
biot_coefficient       = 0.6
initial_porosity       = 0.001
fluid_bulk_modulus     = 4.7835616438e9
solid_bulk_compliance  = 1.611901e-11   # = 1/Kd, Kd = 62.037 GPa
matrix_permeability    = 5e-19

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
    initial_condition = 1e6
  []
[]

# A trivial diffusion problem: the point of this test is the material, not the
# solve. Holding pore_pressure uniform keeps every quadrature point at the same
# state so the element average IS the pointwise value.
[Kernels]
  [diff]
    type = Diffusion
    variable = pore_pressure
  []
[]

[BCs]
  [hold]
    type = DirichletBC
    variable = pore_pressure
    boundary = 'left right'
    value = 1e6
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
    # time_dependent, not constant: recompute M every step so the test reads
    # the formula rather than a frozen initial value.
    biot_modulus_model = time_dependent
  []
  [biot]
    type = OrcaBiotCoefficientMaterial
    model = user
    biot_coefficient = ${biot_coefficient}
  []
[]

[Postprocessors]
  [biot_modulus]
    type = ADElementAverageMaterialProperty
    mat_prop = biot_modulus_qp
    execute_on = 'TIMESTEP_END'
  []
  [biot_coefficient]
    type = ADElementAverageMaterialProperty
    mat_prop = biot_coefficient_qp
    execute_on = 'TIMESTEP_END'
  []
  [porosity]
    type = ADElementAverageMaterialProperty
    mat_prop = porosity_qp
    execute_on = 'TIMESTEP_END'
  []
  [solid_bulk_compliance]
    type = ADElementAverageMaterialProperty
    mat_prop = solid_bulk_compliance_qp
    execute_on = 'TIMESTEP_END'
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  num_steps = 1
  dt = 1
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
  csv = true
[]
