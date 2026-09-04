######################################################################################
# BENCHMARK: induced stresses along a fault bounding a pressurized, displaced reservoir
#            PERMEABLE FAULT -- both compartments are pressurized
#
# Reference configuration follows the GEOS validation case:
#   https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/
#   validationStudies/faultMechanics/faultVerification/Example.html
# verified there against the analytical solution of Wu et al. (2020).
#
# THE PROBLEM
# -----------
# A 300 m thick reservoir is cut by a normal fault dipping at 60 deg with a 100 m
# vertical offset, so the two compartments only partly overlap:
#
#     sampled compartment  (x > x_fault):   z = -100 .. +200 m   [up-thrown]
#     opposite compartment (x < x_fault):   z = -200 .. +100 m   [down-thrown]
#     fault:  x_fault(z) = tan(30 deg) * z
#
# These are the two halves of the mesh's `fracture_block`, which IS the reservoir.
# `offset_top` and `offset_bottom` are NOT reservoir: they are the non-reservoir
# blocks juxtaposed against it by the 100 m throw. Reading the block layout the
# other way round -- treating offset_top as the top of the left compartment --
# produces a geometry that is wrong by exactly the throw, and the resulting
# profiles miss the reference by about 4 MPa. Verified against the mesh: on the
# left of the fault fracture_block spans z = -200..+100, on the right +?100..+200.
#
# Raising the pore pressure in a compartment makes it expand, and that deformation
# perturbs the stress on the fault plane. The benchmark compares the perturbation
# along the fault against the closed form.
#
# THE FAULT IS NOT A MECHANICAL INTERFACE HERE. The GEOS case carries no contact or
# friction: the fault is purely a geometric feature, the surface across which the
# reservoir is displaced and along which stresses are reported. There is therefore no
# CZM in this deck -- unlike the sneddon/ and shear_compression/ benchmarks, this one
# exercises the POROELASTIC coupling, not the contact law.
#
# WHY THIS IS SOLVED AS A PERTURBATION PROBLEM
# --------------------------------------------
# The response is linear elastic and only the CHANGE in stress is compared, so the
# initial stress state cancels exactly and need not be imposed. This deck therefore
# starts from zero stress and applies only the pressure CHANGE:
#
#     computed stress          =  delta sigma'   (effective, tension positive)
#     delta sigma  (total)     =  delta sigma' - alpha * delta p
#
# which is the quantity the reference curve reports. For the same reason the constant
# -70 MPa overburden traction of the GEOS deck becomes a traction-free top here: its
# perturbation is zero. Rollers on the lateral and lower boundaries are unchanged.
#
# The pressure field is PRESCRIBED rather than diffused. With k = 1e-18 m^2 over a
# 4000 m domain the diffusion time is geological; the reference solution is an
# inclusion problem with a uniform pressure change in the reservoir, and prescribing
# it is what reproduces that. pore_pressure is a CONSTANT MONOMIAL aux variable, which
# also matches the cell-centred TPFA pressure GEOS uses.
#
# THIS CASE: PERMEABLE FAULT. Pressure crosses the fault, so both compartments rise
# by the same 20 MPa. The sampled column is then inside a pressurized reservoir over
# z = -100..+200 and outside it elsewhere, and the reference data shows exactly that:
# delta sigma_xx + delta sigma_zz = -alpha dp (1-2nu)/(1-nu) = -14.824 MPa on that
# interval and zero outside it.
######################################################################################

# --- benchmark parameters (GEOS case) ---
youngs_modulus = 14.95e9
poissons_ratio = 0.15
grain_bulk_modulus = 7.12e10
# K = E / (3 (1 - 2 nu)) = 7.119047e9  ->  alpha = 1 - K/Ks = 0.9 exactly
bulk_modulus = ${fparse youngs_modulus / (3.0 * (1.0 - 2.0 * poissons_ratio))}
biot_coefficient = ${fparse 1.0 - bulk_modulus / grain_bulk_modulus}

pressure_buildup = 20.0e6          # 35 MPa -> 55 MPa

# fault geometry: x_fault(z) = tan(30 deg) * z, i.e. a 60 deg dip
fault_slope = 0.5773502691896258

# Reservoir compartments, i.e. the two halves of `fracture_block`.
reservoir_left_bottom = -200       # x < x_fault, down-thrown
reservoir_left_top = 100
reservoir_right_bottom = -100      # x > x_fault, up-thrown; this is the sampled one
reservoir_right_top = 200

# Column immediately on the sampled side of the fault.  The reference reports stress AT
# the fault plane, so the column the profile is read from has to sit next to it.  On the
# unrefined mesh the band is one element wide and the sampler reports from that element's
# centroid, half a coarse element (12.5 m) away from the fault.  That offset preserves the
# shape of every profile but damps its amplitude, and it damps the components that vary
# fastest across the fault the most.  Refining across the fault and then sampling only the
# innermost refined column moves the reported centroid to 3.125 m.
sample_band_width = 25
sample_depth = 310
near_fault_refinement = 2
sampled_column_width = ${fparse sample_band_width / 2^near_fault_refinement}

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Mesh]
  [file_mesh]
    type = FileMeshGenerator
    file = mesh/Induced_stress_along_a_fault_mesh.e
  []
  # A one-element-wide column on the sampled side of the fault, so the profile can be
  # taken with an ElementValueSampler. It must be ELEMENTAL: the total stress is
  # discontinuous across the reservoir boundary, and nodal averaging would smear the
  # jump precisely where the comparison is made.
  # Refine a symmetric collar around the fault so the sampled column can be narrow.
  [refine_target]
    type = ParsedSubdomainMeshGenerator
    input = file_mesh
    combinatorial_geometry = '(x - ${fault_slope} * z) > -${sample_band_width} '
                             '& (x - ${fault_slope} * z) < ${sample_band_width} '
                             '& z > -${sample_depth} & z < ${sample_depth}'
    block_id = 90
    block_name = near_fault_refine
  []
  [refine_near_fault]
    type = RefineBlockGenerator
    input = refine_target
    block = 'near_fault_refine'
    refinement = '${near_fault_refinement}'
    enable_neighbor_refinement = true
  []
  [sample_band]
    type = ParsedSubdomainMeshGenerator
    input = refine_near_fault
    combinatorial_geometry = '(x - ${fault_slope} * z) > 0 '
                             '& (x - ${fault_slope} * z) < ${sampled_column_width} '
                             '& z > -${sample_depth} & z < ${sample_depth}'
    block_id = 99
    block_name = fault_sample_band
  []
  # The sampled column is on the UP-THROWN side, which is where the reference
  # reports. The mirror band on the other side is kept as a diagnostic.
  [sample_band_right]
    type = ParsedSubdomainMeshGenerator
    input = sample_band
    combinatorial_geometry = '(x - ${fault_slope} * z) < 0 '
                             '& (x - ${fault_slope} * z) > -${sampled_column_width} '
                             '& z > -${sample_depth} & z < ${sample_depth}'
    block_id = 98
    block_name = fault_sample_band_other
  []
[]

[Variables]
  [disp_x]
  []
  [disp_y]
  []
  [disp_z]
  []
[]

[AuxVariables]
  # Prescribed pressure CHANGE. Constant monomial so the reservoir boundary stays a
  # sharp jump, as it is in the reference solution.
  [delta_p]
    order = CONSTANT
    family = MONOMIAL
  []
  [dstress_xx]
    order = CONSTANT
    family = MONOMIAL
  []
  [dstress_zz]
    order = CONSTANT
    family = MONOMIAL
  []
  [dstress_xz]
    order = CONSTANT
    family = MONOMIAL
  []
  [dtotal_xx]
    order = CONSTANT
    family = MONOMIAL
  []
  [dtotal_zz]
    order = CONSTANT
    family = MONOMIAL
  []
[]

[Functions]
  # PERMEABLE: both compartments are pressurized.
  [delta_p_fn]
    type = ParsedFunction
    expression = 'if(x < ${fault_slope} * z '
                 '& z > ${reservoir_left_bottom} & z < ${reservoir_left_top},'
                 ' ${pressure_buildup},'
                 ' if(x > ${fault_slope} * z '
                 '& z > ${reservoir_right_bottom} & z < ${reservoir_right_top},'
                 ' ${pressure_buildup}, 0.0))'
  []
[]

[ICs]
  [delta_p_ic]
    type = FunctionIC
    variable = delta_p
    function = delta_p_fn
  []
[]

[AuxKernels]
  # Re-imposed every step so the field is never stale.
  [delta_p_aux]
    type = FunctionAux
    variable = delta_p
    function = delta_p_fn
    execute_on = 'INITIAL TIMESTEP_BEGIN'
  []

  # Effective-stress perturbation straight out of the mechanics.
  [dstress_xx_aux]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = dstress_xx
    index_i = 0
    index_j = 0
    execute_on = TIMESTEP_END
  []
  [dstress_zz_aux]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = dstress_zz
    index_i = 2
    index_j = 2
    execute_on = TIMESTEP_END
  []
  # Shear carries no pore-pressure term, so this is already the total perturbation.
  [dstress_xz_aux]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = dstress_xz
    index_i = 0
    index_j = 2
    execute_on = TIMESTEP_END
  []

  # Total-stress perturbation: what the reference curve reports.
  [dtotal_xx_aux]
    type = ParsedAux
    variable = dtotal_xx
    coupled_variables = 'dstress_xx delta_p'
    expression = 'dstress_xx - ${biot_coefficient} * delta_p'
    execute_on = TIMESTEP_END
  []
  [dtotal_zz_aux]
    type = ParsedAux
    variable = dtotal_zz
    coupled_variables = 'dstress_zz delta_p'
    expression = 'dstress_zz - ${biot_coefficient} * delta_p'
    execute_on = TIMESTEP_END
  []
[]

[Kernels]
  [mech_x]
    type = OrcaPoroMechKernel
    variable = disp_x
    component = 0
    pore_pressure = delta_p
  []
  [mech_y]
    type = OrcaPoroMechKernel
    variable = disp_y
    component = 1
    pore_pressure = delta_p
  []
  [mech_z]
    type = OrcaPoroMechKernel
    variable = disp_z
    component = 2
    pore_pressure = delta_p
  []
[]

[BCs]
  # Rollers on the lateral and lower boundaries, exactly as in the GEOS deck. The top
  # is traction-free because the perturbation of a constant overburden is zero.
  [roller_x]
    type = DirichletBC
    variable = disp_x
    boundary = 'left right'
    value = 0
  []
  [roller_y]
    type = DirichletBC
    variable = disp_y
    boundary = 'front back'
    value = 0
  []
  [roller_z]
    type = DirichletBC
    variable = disp_z
    boundary = 'bottom'
    value = 0
  []
[]

[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = ${youngs_modulus}
    poissons_ratio = ${poissons_ratio}
    strain_model = incremental
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

[VectorPostprocessors]
  # The profile along the fault. Sorted by z; the sampler emits every element of the
  # band, so the 60 out-of-plane slices at each depth appear as repeated z values and
  # are averaged by the comparison script.
  [fault_profile]
    type = ElementValueSampler
    variable = 'dtotal_xx dtotal_zz dstress_xz delta_p'
    block = fault_sample_band
    sort_by = z
    execute_on = TIMESTEP_END
  []
  [fault_profile_other]
    type = ElementValueSampler
    variable = 'dtotal_xx dtotal_zz dstress_xz delta_p'
    block = fault_sample_band_other
    sort_by = z
    execute_on = TIMESTEP_END
  []
[]

[Postprocessors]
  # Interior of a laterally extensive pressurized layer satisfies
  #   d sigma_xx (total) = -alpha dp (1-2nu)/(1-nu),   d sigma_zz (total) = 0
  # which is the sanity check that the coupling term and its sign are right.
  [uniaxial_reference_MPa]
    type = ConstantPostprocessor
    value = ${fparse -biot_coefficient * pressure_buildup * (1.0 - 2.0 * poissons_ratio) / (1.0 - poissons_ratio) / 1.0e6}
  []
  # Volume self-check. One compartment is 2000 * int(2000 -+ tan30 z) dz over its
  # 300 m span = 1.18268e9 m^3, i.e. 0.147835 of the 8.0e9 m^3 domain, so the
  # domain-average delta_p must be 0.147835 * dp per pressurized compartment. This
  # is what catches a mis-specified reservoir region.
  [dp_volume_avg]
    type = ElementAverageValue
    variable = delta_p
  []
  [dp_volume_avg_expected]
    type = ConstantPostprocessor
    value = ${fparse 2.0 * 0.14783510 * pressure_buildup}
  []
  [dtotal_xx_min_MPa]
    type = ElementExtremeValue
    variable = dtotal_xx
    value_type = min
  []
  [dtotal_xx_max_MPa]
    type = ElementExtremeValue
    variable = dtotal_xx
    value_type = max
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
  nl_abs_tol = 1e-6
  nl_rel_tol = 1e-10
  l_max_its = 200
  petsc_options_iname = '-pc_type -pc_hypre_type -ksp_type'
  petsc_options_value = 'hypre     boomeramg      gmres'
[]

[Outputs]
  csv = true
[]
