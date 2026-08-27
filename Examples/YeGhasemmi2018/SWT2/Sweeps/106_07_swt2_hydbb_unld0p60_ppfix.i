# =============================================================================
# 106_07 CORNER -- SW-T2  (106_05 hydraulic closure + 106_06 unload reclosure)
# Parent: 100_04_swt2_apscale0p0177_ppfix.i
#
# Carries BOTH single-axis changes:
#   106_05  aperture_scale 0.0177 -> 0.01093, V_h 34.3624 um, K_h 3.2640e11 Pa/m,
#           p 3.28                                              (targets Q)
#   106_06  normal_unload_retention_fraction 0.84 -> 0.60       (targets d_n, and
#           the unloading half of sigma'_n / tau)
#
# Interpretable only after 106_05 and 106_06 have both scored.  Note the two arms
# overlap on the unloading branch -- both reduce a_h over stages 7-11 -- so unlike
# the SW-T1 pair these are NOT expected to be orthogonal, and the corner may
# overshoot.  Read it as the lower bound of the pair, not as their sum.
# =============================================================================
# =============================================================================
# 100_04 REFINEMENT PROBE -- SW-T2
# Parent: 99_04_swt2_apscale0p0170_ppfix.i
# One hydraulic axis only: aperture_scale 0.0170 -> 0.0177. This is the upper
# bracket around the stagewise fitted optimum (~0.01765); it is separate from
# 100_03 so the curvature and late-unloading flow penalty can be observed.
# =============================================================================
# =============================================================================
# 99_04 CONTROLLED CALIBRATION PROBE -- SW-T2
# Parent: 93_03_swt2_final_theta30_resc9p71_ppfix.i
# One material axis only: hydraulic aperture scale 0.0165 -> 0.0170.
# Hypothesis: reduce the peak-event flow deficit. This is deliberately a narrow
# bracket because late-unloading flow in the parent is already slightly high.
# =============================================================================
# =============================================================================
# 93-SERIES -- MESH AND POSTPROCESSOR AUDIT FIXES.  SW-T2 mesh 5
# Built from 91_04_swt2_bbfast_theta30_resc9p71_kernel_SV_biot0p6.i.  Constitutive parameters are UNCHANGED;
# this series changes only what is measured and reported, plus one source-node
# coordinate on SW-T1 mesh-5.
#
# WHAT MOVED IN THIS DECK
#   1. TWENTY DIAGNOSTIC CHANNELS ADDED (task #82).  SW-S4 carried 87
#      postprocessors and the other three carried 70; the eight bb_* envelope
#      channels, the five loading-frame channels and the seven bulk_* kinematic
#      channels existed only there.  All eight 93-series decks now emit the same
#      91.  None of them feeds the Table-2 gate.
#      bulk_sin_theta / bulk_cos_theta are set from THIS specimen's own theta
#      (30.0 deg), not copied from SW-S4.
#
# WHAT DID NOT MOVE, ON ANY 93-SERIES DECK
#   - every constitutive parameter of [czm_contact];
#   - the mesh file, the injection schedule, the BCs, the solver;
#   - the paper-frame trig constants (each already matched its own mesh's theta
#     to four decimals -- verified against the Exodus fracture_interface nodeset).
# =============================================================================
# =============================================================================================
# 93_03_swt2_final_theta30_resc9p71_ppfix
#
# 91-SERIES: fix the RESIDUAL, keep the ONSET.  Back-analysis of the 90-series, 2026-08-17.
#
# Parent: 90_03_swt2_bbfast_theta30_cohesion_c33p2_kernel_SV_biot0p6.i
#
# WHAT THE 90-SERIES SETTLED.  The level correction worked.  Every deck that was given more peak
# strength moved its margin crossing to the top of the staircase and its onset onto the measured
# event:
#
#     specimen  case    crosses 0 at   slip onset (sim vs val)   mean nRMSE (corrected sigma_d)
#     SW-T1     90_01   24->25 MPa     1610 vs 1650-1725 s        10.6%
#     SW-T1     90_02   never          locked                     51.3%
#     SW-T2     90_03   24->25 MPa     2220 vs 2225-2255 s         6.3%
#     SW-T2     90_04   never          locked                     37.7%
#     SW-S3     90_05   24->25 MPa     2431 vs 2445 s              8.8%
#     SW-S3     90_06   24->25 MPa     2428 vs 2445 s              9.1%
#     SW-S4     90_07   19->20 MPa     1404 vs 1320 s (stage 2)    6.9%
#     SW-S4     90_08   19->20 MPa     1402 vs 1320 s (stage 2)    6.8%
#
# THE REPORTING-CHANNEL CORRECTION.  The scores above use differential_stress_reaction_mpa_pp,
# not differential_stress_mpa_pp.  The latter is (sigma1_pp - 30e6)*1e-6: it subtracts a TOTAL
# confining stress from a SKELETON axial stress and therefore reads alpha*p ~= 3.5 MPa low for
# the entire run.  Two independent operators agree against it -- the load-cell reaction
# (|top reaction|/A - confining) and sigma1 - sigma3_bulk -- and they agree with each other to
# < 0.4 MPa and with the digitized pre-event plateau to 0.1-0.5 MPa on SW-S4.  The broken channel
# is referenced nowhere outside [Postprocessors], so no physics was affected and no re-run was
# needed; the notebooks were repointed instead.  It is the channel the paper-frame tau and
# sigma'_n operators already consumed, so the margin analysis was never contaminated.
#
# WHAT IS LEFT, AND IT IS NOT THE ONSET.  With the corrected channel the residual differential
# stress splits cleanly by fracture type:
#
#     SW-T1 90_01   final sigma_d 71.52 vs 62.68 MPa   +8.83   UNDER-weakened   res_c = 11.176 MPa
#     SW-T2 90_03   final sigma_d 67.36 vs 62.84 MPa   +4.52   UNDER-weakened   res_c = 10.695 MPa
#     SW-S3 90_05   final sigma_d  1.60 vs  5.50 MPa   -3.90   OVER-weakened    res_c = 0
#     SW-S4 90_08   final sigma_d  5.36 vs  5.14 MPa   +0.22   correct          res_c = 0
#
# The two mated tensile fractures keep too much interlock after the burst; the saw cut that was
# given none keeps too little.  SW-S4, whose roughness-degradation floor supplies its residual,
# is already right.  So the 91-series moves residual_cohesion only, at fixed peak envelope, on
# the three specimens that need it -- and brackets D_c on SW-S4, where the remaining error is
# the SHAPE of the transition rather than its level.
#
# THIS DECK.  The conservative half of the SW-T2 residual bracket: residual_cohesion
# 1.0695e7 -> 9.71e6 Pa (-0.98 MPa), peak cohesion unchanged at 3.320e7 Pa.
#
# SW-T2 is the specimen with the least to gain -- 90_03 already scores 6.3% -- so the risk here
# is losing a good case to an over-correction.  This deck exists so that outcome is recoverable
# without another round.  Expect final sigma_d 64-66 MPa; it should be strictly between 90_03's
# 67.36 and 91_03's result, and if it is not, the residual response is nonlinear in cohesion.
#
# =============================================================================================
# ==============================================================================
# 90_03_swt2_bbfast_theta30_cohesion_c33p2_kernel_SV_biot0p6
# GENERATED 2026-08-16 by scripts/build_paper_corrected_decks.py from
#   SWT2/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6.i
# -- do not hand-edit; regenerate instead. The parent is left untouched.
#
# WHY: scripts/paper_parameter_audit.py compared all four decks against Ye &
# Ghassemi (2018) itself rather than against each other, and found that several
# constants presented as measured joint properties were invented. Every value
# changed below is derived in scripts/refit_joint_constants_from_paper.py from
# the paper's own Table 1, Table 2 and Sec. 2.1. Nothing is tuned to a run.
#
# CONTROLLED AXIS: fracture angle AND strength parameterisation
#
# 1. MESH  31.000 -> 30.000 deg, as 89_03; see that deck's header.
# 2. STRENGTH  phi_r = 46.29 deg, c = 0  ->  phi_r = 29.756 deg,
#    cohesion = 31.65 MPa, residual_cohesion = 10.695 MPa, tail phi = 29.756 deg.
#    46.29 deg is essentially the paper's INTACT-rock friction angle of 46 deg,
#    which is not a joint property. The refitted cohesion is 104 % of the
#    30.30 MPa intact cohesion implied by the paper's own UCS and phi -- exactly
#    what a fully mated Mode-I fracture should show, since its asperities ARE
#    intact rock. d(tau)/d(sigma'_n) changes 0.999 -> 0.553.
#
# UNCHANGED AND DELIBERATELY SO: slip-weakening D_c, exponent and tail floor;
# dilation angles; normal-closure constants; hydraulic constants; every BC and
# the load path. The tail floor is an ABSOLUTE friction coefficient with no JRC
# or JCS in it, so refitting the peak envelope leaves its calibration valid.
#
# STATUS: CANDIDATE, not a correction. Score against 89_03 (mesh only) to separate the two effects.
# ==============================================================================
# ==============================================================================
# 87_02_swt2_bbfast_injfix_kernel_SV_biot0p6
# GENERATED 2026-08-16 from Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot0p6.i -- injection schedule rebuilt from the
# 2026-08-16 re-extracted validation curve. Only the injection_pressure function and the output
# file_base names differ from the parent deck.
# ==============================================================================
# 87_02_swt2_bbfast_injfix_kernel_SV_biot0p6
# GENERATED 2026-08-15 from Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe.i -- do not hand-edit; regenerate instead.
#
# Changes applied on 2026-08-15:
#   1. Storage kernel: the combined AD mass-balance kernel
#      OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel, assembling
#      (1/M)*dp/dt + alpha*div(du/dt) in one correctly-coupled object. This replaces
#      the split OrcaSinglePhaseMassTimeDerivativeKernel +
#      OrcaSinglePhaseMassVolumetricExpansionKernel pair, which drops the
#      grain-compressibility storage (alpha-phi)/K_s and uses porosity where the Biot
#      coefficient belongs.
#   2. confining_pressure set to 30e6 Pa (was 30e6).
#      NOTE: confining_pressure is a live BC magnitude here, not just a diagnostic
#      label -- it feeds the czm_pressure_x / czm_pressure_y BC function expressions.
#      A 29.4 -> 30.0 MPa change was measured on 68_02 on 2026-08-14 and moved every
#      Table-2 metric further from target. The 29.4e6 version is preserved unchanged
#      in Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe.i.
#   3. Output file bases repointed to this deck's own name.
#
#   4. biot_coefficient raised 1e-12 -> 0.6. The parent value is below the porosity
#      (0.001), which is unphysical: Biot's coefficient cannot be smaller than
#      porosity. At 1e-12 the bulk rock is poroelastically decoupled -- pore pressure
#      does not enter the bulk effective stress and bulk strain does not drive fluid.
#      This is a RECALIBRATION, not a normalisation: it changes the Biot modulus by
#      roughly a factor of 20 and turns on the effective-stress coupling, so the
#      existing onset timing and strength-envelope tuning will not carry over.
#
# The parent deck Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe.i is left untouched as the reference configuration.
# ==============================================================================
################################################################################
# I/O-SAFE RECOVERY SWEEP V4 SWT2-21: KINEMATIC APERTURE
# Parent/control: Ye2018_SWT2_BBFast_sweep_18_F0p90_Pp0p60_T40p20_U0p84_A0p0168.
# Purpose: replace v18 exponential closure with bounded Barton-Bandis; high aperture bracket.
# Corrected coupling: dilation_opens_joint=true is paired with
# use_kinematic_aperture=true; the separate cumulative-dilation feed is zero.
# The reported normal dilation uses the actual global interface jump.
# frame factor = 0.900
# peak friction offset = 0.600 deg
# post-slip tail friction angle = 40.200 deg
# normal-unload retention fraction U = 0.840000
# kinematic hydraulic aperture scale A = 0.01650000
# hydraulic normal-closure type = barton_bandis (bounded)
# I/O safety: CSV every step; Exodus only at FINAL; one checkpoint
# generation retained every 800 time steps.
################################################################################

################################################################################
# Ye and Ghassemi (2018) SW-T2: minimal timing recalibration v2
#
# Geometry: H=0.13270 m, D=0.05052 m,
# fracture angle=31.0 deg, mesh=mesh/ye2018_sw_T2_mesh_size_5.e
# Paper properties: E=67 GPa, nu=0.32, UCS/JCS=150 MPa, JRC=14.63
# Protocol: sigma3=30 MPa, Po=5 MPa, Pi=8..28..8 MPa.
#
# MINIMAL TIMING RECALIBRATION AFTER REJECTING BACK-ANALYSIS V1:
#   - retain the stable transfer-deck load train, preload, weakening,
#     dilation, residual roughness, strength floor, and time stepping;
#   - replace only the pressure schedule/end time with the digitized
#     Figure-7 protocol and report boundary-average pressures;
#   - for SW-T1 only, apply the bounded +0.593 degree peak-threshold
#     correction that moves initiation from ~25.5 to ~27.9 MPa;
#   - do not reuse the v1 soft load train, cubic weakening, tail-angle
#     reduction, shear-strength floor, or opening-output suppression.
# This remains a candidate until its distinct CSV completes.
# Table-2 anchors:
#   basic friction angle       = 45.6918 deg (24 MPa pre-slip hold)
#   weakened friction angle    = 43.1056 deg (28 MPa post-slip hold)
#   dilation angle             = 13.9654 deg (peak |dn|/ds)
#   hydraulic dilation scale   = 0.019789
#   retained aperture fraction = 0.747331
#   Eq.-9 flow W/L             = 0.813243
#
# REQUIRED PRE-FULL-RUN GATE:
#   (1) t=55 s plastic slip must be zero;
#   (2) first 8 MPa hold should give q~169.591 MPa and
#       tau~74.87 MPa;
#   (3) axial_pres_final is calibrated on this size-5 mesh; recheck this gate
#       whenever the mesh, penalty, elastic properties, or boundary setup changes.
################################################################################

mesh_file = mesh/ye2018_sw_T2_theta30_mesh_size_5.e
sample_radius = 0.02526
sample_area = 0.00200454848465
bulk_sin_theta = 0.4999999999999999          # 93-series: sin(30.0 deg), THIS specimen's fracture angle.
bulk_cos_theta = 0.8660254037844387   # 93-series: cos(30.0 deg). Used only by the bulk_* diagnostics.
axial_bc_penalty = 512100000000

axial_pres_initial = -6.05350517477055e-05
axial_pres_final = -0.000734759213894729

youngs_modulus = 67e9
poissons_ratio = 0.32
strain_model = incremental
initial_stress = '-31e6 -31e6 -31e6'
biot_coefficient = 0.6

initial_porosity = 0.001
matrix_permeability = 5e-19

confining_pressure = 30e6

production_pressure = 5e6
fault_pressure_coefficient = 1.0

penalty_tangent = 1e13
initial_roughness = 1.0
residual_roughness = 0.10

tangential_traction_tolerance = 1e-16

initial_hydraulic_aperture = 2.11e-06

aperture_scale = 0.01093  # 106_05: refitted jointly with the stress term. Was 0.0177.
normal_stress_aperture_compliance = 0.0
reference_effective_normal_stress = 66740000

use_nonlinear_normal_closure = true
nonlinear_closure_type = barton_bandis
bb_max_aperture_closure = 3.43624e-5  # 106_05: V_h fitted to Table 2 flow. Was 1.2e-6 (saturated).

bb_initial_normal_stiffness = 3.2640e11 # 106_05: K_h = sigma_0/V_h with sigma_0 = K_ni*V_m = 11.2158 MPa.
bb_stress_exponent = 3.28             # 106_05: same exponent as this deck's MECHANICAL closure. Was 4.0.
dilation_scale = 0.0

retention_residual = 0.747330960854

self_propping_scale = 0.0
self_propping_exponent = 1.0
use_slip_damage = false
slip_damage_scale = 0.0

slip_damage_onset_slip = 30e-6

slip_damage_characteristic_slip = 30e-6
min_hydraulic_aperture = 2.0045e-06

max_hydraulic_aperture = 8e-6

compute_transmissibility = true

fault_thickness = 1e-3

fluid_density_ref = 1000
fluid_viscosity_ref = 1.002e-3
fluid_bulk_modulus = 2.2e9  # water at 20 C (Sec. 2.5); was 4.7835616438e9, 2.17x too stiff
paper_flow_width_over_length = 0.813242611781
mesh_flow_width_over_length = 0.813242611781
ml_per_m3_per_min = 6.0e7

exodus_file_base = results_exodus_hpc_rorqual/106_07_swt2_hydbb_unld0p60_ppfix_hpc
csv_file_base    = results_csv_hpc_rorqual/106_07_swt2_hydbb_unld0p60_ppfix_hpc
checkpoint_file_base = results_checkpoint_hpc_rorqual/106_07_swt2_hydbb_unld0p60_ppfix_hpc

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Problem]
  boundary_restricted_elem_integrity_check = false  # split-interface lower-D map is orientation-sensitive
  kernel_coverage_check = false  # block 900 (fracture_surface) is output-only
  extra_tag_vectors = 'mech_reaction mass_reaction'
[]

[Mesh]

  [file_mesh]
    type = FileMeshGenerator
    file = ${mesh_file}
  []

  [sidesets_from_nodesets]
    type = SideSetsFromNodeSetsGenerator
    input = file_mesh
    nodesets_to_convert = 'top_nodeset bottom_nodeset sides_nodeset'
  []
  [source_in]
    type = ExtraNodesetGenerator
    input = sidesets_from_nodesets
    coord = '-0.018370909 0.0 0.034530652'   # exact interface node on the 30 deg plane
    new_boundary = source_in
    use_closest_node = true
  []
  [source_out]
    type = ExtraNodesetGenerator
    input = source_in
    coord = '0.018370909 0.0 0.098169348'   # exact interface node on the 30 deg plane
    new_boundary = source_out
    use_closest_node = true
  []
  [fault_split_3d]
    type = OrcaFaultInterface3DGenerator
    input = source_out
    nodesets = 'fracture_interface'
    preserve_front_nodes = true
    split_only_interior_nodes = true
    rebuild_sidesets_from_nodesets = false
    add_interface_on_two_sides = true
    secondary_sidesets = 'fracture_interface_other_side'
  []
  construct_side_list_from_node_list = false

  # Explicit 2-D output block coincident with the solved CZM interface. Required by
  # every AuxVariable carrying block = fracture_surface.
  [fracture_surface_output]
    type = LowerDBlockFromSidesetGenerator
    input = fault_split_3d
    sidesets = fracture_interface
    new_block_id = 900
    new_block_name = fracture_surface
  []
[]

[Variables]
  # Restricted to the 3-D bulk: the mesh also carries the lower-dimensional
  # 'fracture_surface' block (id 900) used only for interface output.
  [disp_x]
    block = 'top_block bottom_block'
  []
  [disp_y]
    block = 'top_block bottom_block'
  []
  [disp_z]
    block = 'top_block bottom_block'
  []
  [pore_pressure]
    block = 'top_block bottom_block'
  []
[]

[ICs]
  [pp_ic]
    type = ConstantIC
    variable = pore_pressure
    value = 5e6
  []
[]

[Functions]

  [axial_disp_ramp]
      type = ParsedFunction

      expression = 'if(t<2.0,${axial_pres_initial},if(t<55.0,${axial_pres_initial}+(${axial_pres_final}-${axial_pres_initial})*(t-2.0)/53.0,${axial_pres_final}))'
    []

  [injection_pressure]
    # REBUILT 2026-08-16 from SWT2_injection_pressure_MPA.csv (re-extraction dated 2026-08-16).
    # The previous schedule was a hand-built idealised staircase: correct hold LEVELS but
    # transition times late by +48..+155 s, and the 28 MPa peak hold only 220 s of measured
    # duration. Because injection pressure is the DRIVER, that timing error propagates into
    # flow rate, permeability, slip onset and the unload branch -- so it must be fixed before
    # any friction/dilation parameter is re-tuned against these curves.
    #
    # Plateau VALUES are snapped to the nominal 5/8/12/16/20/24/28 MPa the experiment held;
    # only the measured TRANSITION TIMES are adopted. Feeding the raw digitised trace would
    # inject +-0.3 MPa extraction jitter as a real pressure BC and excite spurious transients.
    #   whole-record RMSE against the measurement: 1.536 MPa -> 0.266 MPa
    type = PiecewiseLinear
    x = '0.0 60.0 130.0 480.0 565.0 995.0 1070.0 1360.0 1460.0 1755.0 1850.0 2145.0 2280.0 2500.0 2510.0 2560.0 2570.0 2605.0 2615.0 2650.0 2660.0 2705.0 2725.0 2830.0 2852.5'
    y = '5e+06 5e+06 8e+06 8e+06 1.2e+07 1.2e+07 1.6e+07 1.6e+07 2e+07 2e+07 2.4e+07 2.4e+07 2.8e+07 2.8e+07 2.4e+07 2.4e+07 2e+07 2e+07 1.6e+07 1.6e+07 1.2e+07 1.2e+07 8e+06 8e+06 8e+06'
  []

  [production_pressure_fn]
    type = ConstantFunction
    value = ${production_pressure}
  []

  [sigma3_x]
    type = ParsedFunction
    expression = '-${confining_pressure}*x/${sample_radius}'
  []
  [sigma3_y]
    type = ParsedFunction
    expression = '-${confining_pressure}*y/${sample_radius}'
  []
[]

[Kernels]
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
    extra_vector_tags = 'mech_reaction'
  []

#   [fluid_storage]
#     type = OrcaSinglePhaseMassTimeDerivativeKernel
#     variable = pore_pressure
#     multiply_by_fluid_density = true
#     save_in = inj_flux_aux
#   []
  [darcy]
    type = OrcaFullySaturatedSinglePhaseDarcySUPGKernel
    variable = pore_pressure
    multiply_by_fluid_density = true
    use_supg = true
    save_in = inj_flux_aux
    extra_vector_tags = mass_reaction
  []
#   [mass_vol_expansion]
#     type = OrcaSinglePhaseMassVolumetricExpansionKernel
#     variable = pore_pressure
#     multiply_by_fluid_density = true
#   []
  # (1/M)*dp/dt + alpha*div(du/dt)  [volume form] -- KERNEL FIX 2026-08-14: combined,
  # correctly-coupled mass time-derivative kernel, replacing the old split
  # fluid_storage + mass_vol_expansion pair above (commented out, kept for reference).
  # Validated against 68_02_sw4_bbfast_tail6p75_eta3p25_m0 (this exact deck) in
  # SW4_July10/SW4_68_TARGETED_RESIDUAL_SWEEPS/ -- see CHANGELOG/memory
  # sw-s4-kernel-alpha-backanalysis-2026-08-14 for the full back-analysis.
  [fluid_storage]
    type                 = OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel
    variable             = pore_pressure
    coupling_type        = HydroMechanical
    multiply_by_fluid_density = true
    extra_vector_tags = mass_reaction
  []
[]

[InterfaceKernels]
  [czm_mech_x]
    type = OrcaMechInterfaceKernel
    boundary = fracture_interface
    variable = disp_x
    neighbor_var = disp_x
    component = 0
  []
  [czm_mech_y]
    type = OrcaMechInterfaceKernel
    boundary = fracture_interface
    variable = disp_y
    neighbor_var = disp_y
    component = 1
  []
  [czm_mech_z]
    type = OrcaMechInterfaceKernel
    boundary = fracture_interface
    variable = disp_z
    neighbor_var = disp_z
    component = 2
    extra_vector_tags = 'mech_reaction'
  []

  [fault_pressure_x]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = fracture_interface
    variable = disp_x
    neighbor_var = disp_x
    component = 0
    displacements = 'disp_x disp_y disp_z'
    pressure_traction_coefficient = -${fault_pressure_coefficient}
  []
  [fault_pressure_y]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = fracture_interface
    variable = disp_y
    neighbor_var = disp_y
    component = 1
    displacements = 'disp_x disp_y disp_z'
    pressure_traction_coefficient = -${fault_pressure_coefficient}
  []
  [fault_pressure_z]
    type = OrcaCZMFluidPressureInterfaceKernel
    boundary = fracture_interface
    variable = disp_z
    neighbor_var = disp_z
    component = 2
    displacements = 'disp_x disp_y disp_z'
    pressure_traction_coefficient = -${fault_pressure_coefficient}
    extra_vector_tags = 'mech_reaction'
  []
  [czm_flow]
    type = OrcaFractureFlowInterfaceKernel
    boundary = fracture_interface
    variable = pore_pressure
    neighbor_var = pore_pressure
    pressure_penalty_length = 5e-4
    multiply_by_fluid_density = true
    save_in = 'inj_flux_aux inj_flux_aux'
    save_in_var_side = 'm s'
    extra_vector_tags = mass_reaction
  []
[]

[BCs]
  [confine_x]
    type = FunctionNeumannBC
    variable = disp_x
    boundary = sides_nodeset
    function = sigma3_x
  []
  [confine_y]
    type = FunctionNeumannBC
    variable = disp_y
    boundary = sides_nodeset
    function = sigma3_y
  []
  [base_fixed_z]
    type = DirichletBC
    variable = disp_z
    boundary = bottom_nodeset
    value = 0
  []
  [axial_load]

    type = FunctionPenaltyDirichletBC
    variable = disp_z
    boundary = top_nodeset
    function = axial_disp_ramp
    penalty = ${axial_bc_penalty}
  []
  [pin_x]
    type = DirichletBC
    variable = disp_x
    boundary = no_disp_x
    value = 0
  []
  [pin_y]
    type = DirichletBC
    variable = disp_y
    boundary = no_disp_y
    value = 0
  []
  [injection]
    type = FunctionDirichletBC
    variable = pore_pressure
    boundary = source_in
    function = injection_pressure
  []
  [production]
    type = DirichletBC
    variable = pore_pressure
    boundary = source_out
    value = ${production_pressure}
  []
[]

[AuxVariables]
  [inj_flux_aux]
    block = 'top_block bottom_block'
  []
  [react_disp_z]
    order = FIRST
    family = LAGRANGE
    block = 'top_block bottom_block'
  []
  [react_pore_pressure]
    order = FIRST
    family = LAGRANGE
    block = 'top_block bottom_block'
  []
  [stress_xx]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [stress_yy]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [stress_zz]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [stress_xy]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [stress_xz]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [stress_yz]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [darcy_vel_x]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [darcy_vel_y]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [darcy_vel_z]
    order = CONSTANT
    family = MONOMIAL
    block = 'top_block bottom_block'
  []
  [traction_x]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [traction_y]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [traction_z]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [normal_traction]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [tangent_traction]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [jump_x]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [jump_y]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [jump_z]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [normal_jump]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [tangent_jump]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [aperture_mech]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [aperture_mech_raw]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [aperture_open]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [aperture_hydraulic]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [fracture_permeability]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [cumulative_dilation]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [fracture_state]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [roughness_state]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [roughness_damage]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [roughness_retention_factor]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [self_propping_aperture]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [limit_tau]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [plastic_slip_increment]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [dilation_jump_increment]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [cumulative_plastic_slip]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [friction_coefficient_effective]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [cohesion_effective]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [fracture_darcy_vel_x]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [fracture_darcy_vel_y]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
  [fracture_darcy_vel_z]
    order = CONSTANT
    family = MONOMIAL
    block = fracture_surface
  []
[]

[AuxKernels]
  [react_disp_z_aux]
    type = TagVectorAux
    vector_tag = mech_reaction
    v = disp_z
    variable = react_disp_z
    remove_variable_scaling = true
    block = 'top_block bottom_block'
  []
  [react_pore_pressure_aux]
    type = TagVectorAux
    vector_tag = mass_reaction
    v = pore_pressure
    variable = react_pore_pressure
    remove_variable_scaling = true
    block = 'top_block bottom_block'
  []
  [stress_xx_aux]
    type = ADMaterialRankTwoTensorAux
    variable = stress_xx
    property = stress
    i = 0
    j = 0
    block = 'top_block bottom_block'
  []
  [stress_yy_aux]
    type = ADMaterialRankTwoTensorAux
    variable = stress_yy
    property = stress
    i = 1
    j = 1
    block = 'top_block bottom_block'
  []
  [stress_zz_aux]
    type = ADMaterialRankTwoTensorAux
    variable = stress_zz
    property = stress
    i = 2
    j = 2
    block = 'top_block bottom_block'
  []
  [stress_xy_aux]
    type = ADMaterialRankTwoTensorAux
    variable = stress_xy
    property = stress
    i = 0
    j = 1
    block = 'top_block bottom_block'
  []
  [stress_xz_aux]
    type = ADMaterialRankTwoTensorAux
    variable = stress_xz
    property = stress
    i = 0
    j = 2
    block = 'top_block bottom_block'
  []
  [stress_yz_aux]
    type = ADMaterialRankTwoTensorAux
    variable = stress_yz
    property = stress
    i = 1
    j = 2
    block = 'top_block bottom_block'
  []
  [darcy_x_aux]
    type = OrcaDarcyVelocityComponent
    component = 0
    variable = darcy_vel_x
    fluid_pressure = pore_pressure
    block = 'top_block bottom_block'
  []
  [darcy_y_aux]
    type = OrcaDarcyVelocityComponent
    component = 1
    variable = darcy_vel_y
    fluid_pressure = pore_pressure
    block = 'top_block bottom_block'
  []
  [darcy_z_aux]
    type = OrcaDarcyVelocityComponent
    component = 2
    variable = darcy_vel_z
    fluid_pressure = pore_pressure
    block = 'top_block bottom_block'
  []
  [traction_x_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = traction_x
    variable = traction_x
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [traction_y_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = traction_y
    variable = traction_y
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [traction_z_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = traction_z
    variable = traction_z
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [normal_traction_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = normal_traction
    variable = normal_traction
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [tangent_traction_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = tangent_traction
    variable = tangent_traction
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [jump_x_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = jump_x
    variable = jump_x
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [jump_y_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = jump_y
    variable = jump_y
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [jump_z_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = jump_z
    variable = jump_z
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [normal_jump_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = normal_jump
    variable = normal_jump
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [tangent_jump_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = tangent_jump
    variable = tangent_jump
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [aperture_mech_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = mechanical_aperture
    variable = aperture_mech
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [aperture_mech_raw_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = mechanical_aperture_raw
    variable = aperture_mech_raw
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [aperture_open_aux]
    type = ParsedAux
    check_boundary_restricted = false
    variable = aperture_open
    boundary = fracture_interface
    coupled_variables = normal_jump
    expression = 'if(normal_jump > 0.0, normal_jump, 0.0)'
    execute_on = TIMESTEP_END
  []
  [aperture_hydraulic_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = hydraulic_aperture
    variable = aperture_hydraulic
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [fracture_permeability_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = fracture_permeability
    variable = fracture_permeability
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [cumulative_dilation_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = cumulative_dilation
    variable = cumulative_dilation
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [fracture_state_aux]
    type = MaterialRealAux
    check_boundary_restricted = false
    property = fracture_state
    variable = fracture_state
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [roughness_state_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = roughness_state
    variable = roughness_state
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [roughness_damage_aux]
    type = MaterialRealAux
    check_boundary_restricted = false
    property = roughness_damage
    variable = roughness_damage
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [roughness_retention_factor_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = roughness_retention_factor
    variable = roughness_retention_factor
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [self_propping_aperture_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = self_propping_aperture
    variable = self_propping_aperture
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [limit_tau_aux]
    type = MaterialRealAux
    check_boundary_restricted = false
    property = limit_tau
    variable = limit_tau
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [plastic_slip_increment_aux]
    type = MaterialRealAux
    check_boundary_restricted = false
    property = plastic_slip_increment
    variable = plastic_slip_increment
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [dilation_jump_increment_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = dilation_jump_increment
    variable = dilation_jump_increment
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [cumulative_plastic_slip_aux]
    type = MaterialRealAux
    check_boundary_restricted = false
    property = cumulative_plastic_slip
    variable = cumulative_plastic_slip
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [friction_coefficient_effective_aux]
    type = MaterialRealAux
    check_boundary_restricted = false
    property = friction_coefficient_effective
    variable = friction_coefficient_effective
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [cohesion_effective_aux]
    type = MaterialRealAux
    check_boundary_restricted = false
    property = cohesion_effective
    variable = cohesion_effective
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [fracture_darcy_x_aux]
    type = OrcaFractureDarcyVelocityComponent
    component = 0
    variable = fracture_darcy_vel_x
    fluid_pressure = pore_pressure
    boundary = fracture_interface
    check_boundary_restricted = false
    execute_on = TIMESTEP_END
  []
  [fracture_darcy_y_aux]
    type = OrcaFractureDarcyVelocityComponent
    component = 1
    variable = fracture_darcy_vel_y
    fluid_pressure = pore_pressure
    boundary = fracture_interface
    check_boundary_restricted = false
    execute_on = TIMESTEP_END
  []
  [fracture_darcy_z_aux]
    type = OrcaFractureDarcyVelocityComponent
    component = 2
    variable = fracture_darcy_vel_z
    fluid_pressure = pore_pressure
    boundary = fracture_interface
    check_boundary_restricted = false
    execute_on = TIMESTEP_END
  []
[]

[Materials]
  [mech]
    type = OrcaMechMaterial
    youngs_modulus = ${youngs_modulus}
    poissons_ratio = ${poissons_ratio}
    strain_model = ${strain_model}
    initial_stress = ${initial_stress}
    block = 'top_block bottom_block'
  []
  [rockHM]
    type = OrcaTHMaterial
    pore_pressure = pore_pressure
    initial_porosity = ${initial_porosity}
    initial_permeability = '${matrix_permeability} 0 0  0 ${matrix_permeability} 0  0 0 ${matrix_permeability}'
    fluid_properties_model = user
    fluid_density_model = constant
    fluid_density_ref = ${fluid_density_ref}
    fluid_bulk_modulus = ${fluid_bulk_modulus}
    fluid_viscosity_ref = ${fluid_viscosity_ref}
    biot_modulus_model = constant
    fluid_thermal_expansion_model = user
    block = 'top_block bottom_block'
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

  [czm_jump]
    type = OrcaCZMComputeDisplacementJump
    boundary = fracture_interface
  []
  [czm_pressure]
    type = OrcaCZMInterfacePressure
    boundary = fracture_interface
    pore_pressure = pore_pressure
  []
  [czm_contact]

    type = OrcaBartonBandisContactTractionFastADHardening
    boundary = fracture_interface

    use_hyperbolic_normal_closure = true
    initial_normal_stiffness = 2.443e11
    maximum_closure = 4.591e-5
    normal_closure_stress_exponent = 3.28
    normal_closure_offset = 4.433e-5
    normal_unload_retention_fraction = 0.60   # 106_07: from 106_06. Was 0.84.
    normal_unload_retention_time = 0.0
    normal_reclosure_stiffness_multiplier = 1.0
    normal_unload_activation_slip = 5.0e-5
    reported_reversible_normal_opening_scale = 1.0
    reported_reversible_normal_opening_retention_fraction = 0.0
    reported_reversible_normal_opening_retention_activation_slip = 50e-6
    penalty_tangent = ${penalty_tangent}
    normal_traction_tolerance = 0.0
    tangential_traction_tolerance = ${tangential_traction_tolerance}

    jrc = 14.63
    jcs = 1.5e8
    residual_friction_angle_degrees = 29.756   # granite basic friction, measured on this campaign's own saw cut (SW-S3). Was 46.29182452, above every measured granite value.
    use_scale_correction = false
    use_mobilized_jrc = false
    compressive_normal_stress_floor = 1e3
    pore_pressure_strength_coefficient = 0.0
    use_slip_weakening = true
    characteristic_slip_distance = 0.00015
    slip_weakening_exponent = 1.4
    slip_weakening_residual_friction_angle_degrees = 29.756   # slip destroys ROUGHNESS, not the rock's basic friction angle -- Barton's own picture. Was 40.2.
    cohesion = 3.320e7          # asperity interlock of a MATED Mode-I fracture; pins the peak envelope through Table 2's last stick stage.
    residual_cohesion = 9.71e6 # interlock surviving the burst; pins the post-burst stage. Table 2 shows this joint retaining most of its dilation, so it does not lose all interlock in one event.  # 91_04: half the 91_03 cut. Was 1.0695e7.
    use_dilatancy = true
    use_decoupled_dilation = true
    dilation_angle_peak_degrees = 13.96539134
    dilation_angle_residual_degrees = 13.96539134
    dilation_decay_distance = 1.5e-4
    dilation_opens_joint = true
    accumulate_irreversible_dilation = true
    cap_dilation_to_available_closure = false
    max_dilation_increment = 0.0

    use_roughness_degradation = true
    roughness_state_initial = ${initial_roughness}
    roughness_state_residual = ${residual_roughness}
    roughness_characteristic_slip = 1.5e-4

    max_plastic_slip_increment = 0.0
    tangential_viscosity = 400000000000
    min_tau_limit = 0.0
    max_return_mapping_iterations = 100
    relative_tolerance = 1e-10
  []
  [czm_global_traction]
    type = OrcaComputeGlobalTractionSmallStrain
    boundary = fracture_interface
  []

  [aperture_mech]
    type = ADOrcaCZMComputeMechanicalAperture
    boundary = fracture_interface
    jump_property_name = interface_displacement_jump
    aperture_property_name = mechanical_aperture
    raw_aperture_property_name = mechanical_aperture_raw
    clamp_to_zero = true
  []
  [czm_sigma_n]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = fracture_interface
    real_vector_value = interface_traction
    property_name = czm_sigma_n
    index = 0
  []
  [czm_aperture]
    type = ADOrcaRoughnessDamageFracturePermeability
    boundary = fracture_interface
    mechanical_aperture_name = mechanical_aperture
    dilation_jump_increment_name = dilation_jump_increment
    roughness_name = roughness_state
    hydraulic_aperture_name = hydraulic_aperture
    fracture_permeability_name = fracture_permeability
    cumulative_dilation_name = cumulative_dilation
    roughness_retention_factor_name = roughness_retention_factor
    self_propping_aperture_name = self_propping_aperture
    normal_stress_aperture_name = normal_stress_aperture
    effective_normal_compression_name = effective_normal_compression
    effective_normal_traction_name = czm_sigma_n
    transmissibility_name = fracture_transmissivity

    use_kinematic_aperture = true
    initial_hydraulic_aperture = ${initial_hydraulic_aperture}
    aperture_scale = ${aperture_scale}
    normal_stress_aperture_compliance = ${normal_stress_aperture_compliance}
    reference_effective_normal_stress = ${reference_effective_normal_stress}
    use_nonlinear_normal_closure = ${use_nonlinear_normal_closure}
    nonlinear_closure_type = ${nonlinear_closure_type}
    bb_max_aperture_closure = ${bb_max_aperture_closure}
    bb_initial_normal_stiffness = ${bb_initial_normal_stiffness}
    bb_stress_exponent = ${bb_stress_exponent}
    dilation_scale = ${dilation_scale}
    retention_residual = ${retention_residual}
    self_propping_scale = ${self_propping_scale}
    self_propping_exponent = ${self_propping_exponent}
    use_slip_damage = ${use_slip_damage}
    slip_damage_scale = ${slip_damage_scale}
    slip_damage_characteristic_slip = ${slip_damage_characteristic_slip}
    slip_damage_onset_slip = ${slip_damage_onset_slip}
    cumulative_plastic_slip_name = cumulative_plastic_slip
    cumulative_plastic_slip_is_ad = false
    slip_damage_aperture_name = slip_damage_aperture

    min_hydraulic_aperture = ${min_hydraulic_aperture}
    max_hydraulic_aperture = ${max_hydraulic_aperture}
    compute_transmissibility = ${compute_transmissibility}
    fluid_viscosity = ${fluid_viscosity_ref}
    fault_thickness = ${fault_thickness}
  []

  [czm_tau_1]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = fracture_interface
    real_vector_value = interface_traction
    property_name = czm_tau_1
    index = 1
  []
  [czm_tau_2]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = fracture_interface
    real_vector_value = interface_traction
    property_name = czm_tau_2
    index = 2
  []
  [czm_dn]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = fracture_interface
    real_vector_value = interface_displacement_jump
    property_name = czm_dn
    index = 0
  []
  [czm_ds_1]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = fracture_interface
    real_vector_value = interface_displacement_jump
    property_name = czm_ds_1
    index = 1
  []
  [czm_ds_2]
    type = OrcaCZMRealVectorCartesianComponent
    boundary = fracture_interface
    real_vector_value = interface_displacement_jump
    property_name = czm_ds_2
    index = 2
  []

  [czm_dn_global]
    type = OrcaCZMRealVectorScalar
    boundary = fracture_interface
    real_vector_value = displacement_jump_global
    direction = Normal
    property_name = czm_dn_global
  []

  # ---- CZM interface output properties consumed by the fracture_surface AuxKernels ----
  [fracture_surface_output_material]
    type = GenericConstantMaterial
    prop_names = fracture_surface_output_marker
    prop_values = 1
    block = fracture_surface
  []
  [traction_x_output_property]
    type = OrcaCZMRealVectorCartesianComponent
    real_vector_value = traction_global
    index = 0
    property_name = traction_x
    boundary = fracture_interface
  []
  [traction_y_output_property]
    type = OrcaCZMRealVectorCartesianComponent
    real_vector_value = traction_global
    index = 1
    property_name = traction_y
    boundary = fracture_interface
  []
  [traction_z_output_property]
    type = OrcaCZMRealVectorCartesianComponent
    real_vector_value = traction_global
    index = 2
    property_name = traction_z
    boundary = fracture_interface
  []
  [jump_x_output_property]
    type = OrcaCZMRealVectorCartesianComponent
    real_vector_value = displacement_jump_global
    index = 0
    property_name = jump_x
    boundary = fracture_interface
  []
  [jump_y_output_property]
    type = OrcaCZMRealVectorCartesianComponent
    real_vector_value = displacement_jump_global
    index = 1
    property_name = jump_y
    boundary = fracture_interface
  []
  [jump_z_output_property]
    type = OrcaCZMRealVectorCartesianComponent
    real_vector_value = displacement_jump_global
    index = 2
    property_name = jump_z
    boundary = fracture_interface
  []
  [normal_traction_output_property]
    type = OrcaCZMRealVectorScalar
    real_vector_value = traction_global
    direction = Normal
    property_name = normal_traction
    boundary = fracture_interface
  []
  [tangent_traction_output_property]
    type = OrcaCZMRealVectorScalar
    real_vector_value = traction_global
    direction = Tangent
    property_name = tangent_traction
    boundary = fracture_interface
  []
  [normal_jump_output_property]
    type = OrcaCZMRealVectorScalar
    real_vector_value = displacement_jump_global
    direction = Normal
    property_name = normal_jump
    boundary = fracture_interface
  []
  [tangent_jump_output_property]
    type = OrcaCZMRealVectorScalar
    real_vector_value = displacement_jump_global
    direction = Tangent
    property_name = tangent_jump
    boundary = fracture_interface
  []
[]

[Postprocessors]

  [fracture_interface_area_pp]
    type = AreaPostprocessor
    boundary = fracture_interface
  []
  [injection_pressure_pp]
    type = AverageNodalVariableValue
    variable = pore_pressure
    boundary = source_in
  []
  # --- FLOW-MEASUREMENT FIX 2026-08-24 (task #123) -------------------------
  # Ported into the 106 series from 105_01.  These two summed `inj_flux_aux`,
  # the save_in quantity.  The 2026-08-06 back-analysis established that save_in
  # does not reproduce the nodal reaction here (mass_vol_expansion carries the
  # mass_reaction tag but had no save_in, and the two-sided sum across the split
  # injection node does not recover it either), and that the deck already builds
  # the right quantity: `react_pore_pressure`, a TagVectorAux on mass_reaction
  # with remove_variable_scaling = true.  The 99-104 parents never carried the
  # repoint, so their flux diagnostics are ~2 orders of magnitude low.
  #
  # OUTPUT-ONLY, AND NOT A SCORED CHANNEL.  `inj_flux_aux` is written by save_in
  # and read by nothing but these postprocessors, so the residual, the solve and
  # every other reported channel are unchanged.  The Table-2 flow channel is
  # `flow_rate_validation_ml_min_pp`, the cubic law built from
  # hydraulic_aperture_pp and pp_drop_pp, which never touched either quantity --
  # so this port changes no score, on this deck or on its parent.
  [inj_reaction_sum_pp]
    type = NodalSum
    variable = react_pore_pressure
    boundary = source_in
  []
  [prod_reaction_sum_pp]
    type = NodalSum
    variable = react_pore_pressure
    boundary = source_out
  []
  # Superseded save_in sums, retained so the pre-fix numbers stay auditable and
  # the size of the correction is recoverable from a single run.
  [inj_saveiin_sum_legacy_pp]
    type = NodalSum
    variable = inj_flux_aux
    boundary = source_in
  []
  [prod_saveiin_sum_legacy_pp]
    type = NodalSum
    variable = inj_flux_aux
    boundary = source_out
  []
  # ------------------------------------------------------------------------
  [flow_rate_pp]
    type = ParsedPostprocessor
    pp_names = inj_reaction_sum_pp
    expression = 'abs(inj_reaction_sum_pp)'
  []

  [pp_outlet_pp]
    type = AverageNodalVariableValue
    variable = pore_pressure
    boundary = source_out
  []
  [pp_drop_pp]
    type = ParsedPostprocessor
    pp_names = 'injection_pressure_pp pp_outlet_pp'
    expression = 'injection_pressure_pp - pp_outlet_pp'
  []
  [flow_rate_validation_ml_min_pp]
    type = ParsedPostprocessor
    pp_names = 'hydraulic_aperture_pp pp_drop_pp'
    expression = '(${paper_flow_width_over_length} / (12.0 * ${fluid_viscosity_ref})) * hydraulic_aperture_pp^3 * pp_drop_pp * ${ml_per_m3_per_min}'
  []
  [flow_rate_mesh_geometry_ml_min_pp]
    type = ParsedPostprocessor
    pp_names = 'hydraulic_aperture_pp pp_drop_pp'
    expression = '(${mesh_flow_width_over_length} / (12.0 * ${fluid_viscosity_ref})) * hydraulic_aperture_pp^3 * pp_drop_pp * ${ml_per_m3_per_min}'
  []
  [flow_rate_reference_area_ml_min_pp]
    type = ParsedPostprocessor
    pp_names = 'fracture_permeability_pp pp_drop_pp'
    expression = 'fracture_permeability_pp * (7.8e-6 / (${fluid_viscosity_ref} * 7.94e-2)) * pp_drop_pp * ${ml_per_m3_per_min}'
  []
  [flow_rate_residual_volume_ml_min_pp]
    type = ParsedPostprocessor
    pp_names = flow_rate_pp
    expression = 'flow_rate_pp / ${fluid_density_ref} * ${ml_per_m3_per_min}'
  []
  [flow_rate_outlet_residual_volume_ml_min_pp]
    type = ParsedPostprocessor
    pp_names = prod_reaction_sum_pp
    expression = 'abs(prod_reaction_sum_pp) / ${fluid_density_ref} * ${ml_per_m3_per_min}'
  []
  [flow_mass_imbalance_fraction_pp]
    type = ParsedPostprocessor
    pp_names = 'inj_reaction_sum_pp prod_reaction_sum_pp'
    expression = 'abs(inj_reaction_sum_pp + prod_reaction_sum_pp) / max(abs(inj_reaction_sum_pp), 1e-30)'
  []

  [top_boundary_area_pp]
    type = AreaPostprocessor
    boundary = top_nodeset
  []
  [top_reaction_z_raw]
    type = NodalSum
    variable = react_disp_z
    boundary = top_nodeset
  []
  [top_reaction_z_abs]
    type = ParsedPostprocessor
    pp_names = top_reaction_z_raw
    expression = 'abs(top_reaction_z_raw)'
  []
  [sigma1_reaction_mpa_pp]
    type = ParsedPostprocessor
    pp_names = top_reaction_z_abs
    expression = 'top_reaction_z_abs / ${sample_area} * 1e-6'
  []
  [differential_stress_reaction_mpa_pp]
    type = ParsedPostprocessor
    pp_names = sigma1_reaction_mpa_pp
    expression = 'sigma1_reaction_mpa_pp - 30.0'
  []

  [stress_zz_top_pp]
    type = SideAverageValue
    variable = stress_zz
    boundary = top_nodeset
  []
  [sigma1_pp]
    type = ParsedPostprocessor
    pp_names = stress_zz_top_pp
    expression = '-stress_zz_top_pp'
  []
  [differential_stress_mpa_pp]
    type = ParsedPostprocessor
    pp_names = sigma1_pp
    expression = '(sigma1_pp - 30e6) * 1e-6'
  []

  [differential_stress_skeleton_bulk_pp]
    type = ParsedPostprocessor
    pp_names = 'sigma1_pp sigma3_bulk_mpa_pp'
    expression = 'sigma1_pp * 1e-6 - sigma3_bulk_mpa_pp'
  []

  [differential_stress_biot_corrected_pp]
    type = ParsedPostprocessor
    pp_names = 'sigma1_pp fracture_pressure_mean_pp'
    expression = '(sigma1_pp + ${biot_coefficient} * fracture_pressure_mean_pp - 30e6) * 1e-6'
  []

  [differential_stress_biot_corrected_injection_pp]
    type = ParsedPostprocessor
    pp_names = 'sigma1_pp injection_pressure_pp'
    expression = '(sigma1_pp + ${biot_coefficient} * injection_pressure_pp - 30e6) * 1e-6'
  []

  [stress_zz_fault_pp]
    type = SideAverageValue
    variable = stress_zz
    boundary = fracture_interface
  []
  [stress_xx_fault_pp]
    type = SideAverageValue
    variable = stress_xx
    boundary = fracture_interface
  []
  [sigma1_fault_mpa_pp]
    type = ParsedPostprocessor
    pp_names = stress_zz_fault_pp
    expression = '-stress_zz_fault_pp * 1e-6'
  []
  [sigma3_fault_mpa_pp]
    type = ParsedPostprocessor
    pp_names = stress_xx_fault_pp
    expression = '-stress_xx_fault_pp * 1e-6'
  []

  [stress_xx_bulk_pp]
    type = ElementAverageValue
    variable = stress_xx
    block = 'top_block bottom_block'
  []
  [sigma3_bulk_mpa_pp]
    type = ParsedPostprocessor
    pp_names = stress_xx_bulk_pp
    expression = '-stress_xx_bulk_pp * 1e-6'
  []

  [czm_sigma_n_pp]
    type = ADSideAverageMaterialProperty
    property = czm_sigma_n
    boundary = fracture_interface
  []
  [interface_pressure_pp]
    type = ADSideAverageMaterialProperty
    property = interface_pore_pressure
    boundary = fracture_interface
  []

  [fracture_pressure_mean_pp]
    type = ADSideAverageMaterialProperty
    property = interface_pore_pressure
    boundary = fracture_interface
  []
  [bb_effective_normal_stress_pp]
    type = ParsedPostprocessor
    pp_names = 'czm_sigma_n_pp'
    expression = '-czm_sigma_n_pp'
  []

  [cumulative_plastic_slip_pp]
    type = SideAverageMaterialProperty
    property = cumulative_plastic_slip
    boundary = fracture_interface
  []
  [plastic_slip_increment_pp]
    type = SideAverageMaterialProperty
    property = plastic_slip_increment
    boundary = fracture_interface
  []
  [limit_tau_pp]
    type = SideAverageMaterialProperty
    property = limit_tau
    boundary = fracture_interface
  []

  [bb_limit_tau_pp]
    type = SideAverageMaterialProperty
    property = limit_tau
    boundary = fracture_interface
  []
  [friction_coefficient_effective_pp]
    type = SideAverageMaterialProperty
    property = friction_coefficient_effective
    boundary = fracture_interface
  []
  [cohesion_effective_pp]
    type = SideAverageMaterialProperty
    property = cohesion_effective
    boundary = fracture_interface
  []
  [roughness_state_pp]
    type = ADSideAverageMaterialProperty
    property = roughness_state
    boundary = fracture_interface
  []
  [bb_dilation_angle_pp]
    type = SideAverageMaterialProperty
    property = bb_dilation_angle_degrees
    boundary = fracture_interface
  []
  [dilation_jump_increment_pp]
    type = ADSideAverageMaterialProperty
    property = dilation_jump_increment
    boundary = fracture_interface
  []

  [czm_tau_1_pp]
    type = ADSideAverageMaterialProperty
    property = czm_tau_1
    boundary = fracture_interface
  []
  [czm_tau_2_pp]
    type = ADSideAverageMaterialProperty
    property = czm_tau_2
    boundary = fracture_interface
  []
  [shear_traction_magnitude_pa]
    type = ParsedPostprocessor
    pp_names = 'czm_tau_1_pp czm_tau_2_pp'
    expression = 'sqrt(czm_tau_1_pp^2 + czm_tau_2_pp^2)'
  []

  [czm_ds_1_pp]
    type = ADSideAverageMaterialProperty
    property = czm_ds_1
    boundary = fracture_interface
  []
  [czm_ds_2_pp]
    type = ADSideAverageMaterialProperty
    property = czm_ds_2
    boundary = fracture_interface
  []
  [czm_shear_slip_mm_pp]
    type = ParsedPostprocessor
    pp_names = 'czm_ds_1_pp czm_ds_2_pp'
    expression = 'sqrt(czm_ds_1_pp^2 + czm_ds_2_pp^2) * 1e3'
  []

  [reported_czm_shear_slip_mm_pp]
    type = ParsedPostprocessor
    pp_names = czm_shear_slip_mm_pp
    expression = 'czm_shear_slip_mm_pp * 1'
  []

  [hydraulic_aperture_pp]
    type = ADSideAverageMaterialProperty
    property = hydraulic_aperture
    boundary = fracture_interface
  []
  [hydraulic_aperture_um_pp]
    type = ParsedPostprocessor
    pp_names = hydraulic_aperture_pp
    expression = 'hydraulic_aperture_pp * 1e6'
  []
  [fracture_permeability_pp]
    type = ADSideAverageMaterialProperty
    property = fracture_permeability
    boundary = fracture_interface
  []
  [fracture_permeability_1e13_m2_pp]
    type = ParsedPostprocessor
    pp_names = fracture_permeability_pp
    expression = 'fracture_permeability_pp * 1e13'
  []
  [cumulative_dilation_pp]
    type = ADSideAverageMaterialProperty
    property = cumulative_dilation
    boundary = fracture_interface
  []
  [normal_stress_aperture_pp]
    type = ADSideAverageMaterialProperty
    property = normal_stress_aperture
    boundary = fracture_interface
  []
  [normal_stress_aperture_um_pp]
    type = ParsedPostprocessor
    pp_names = normal_stress_aperture_pp
    expression = 'normal_stress_aperture_pp * 1e6'
  []
  [slip_damage_aperture_pp]
    type = ADSideAverageMaterialProperty
    property = slip_damage_aperture
    boundary = fracture_interface
  []
  [slip_damage_aperture_um_pp]
    type = ParsedPostprocessor
    pp_names = slip_damage_aperture_pp
    expression = 'slip_damage_aperture_pp * 1e6'
  []
  [effective_normal_compression_pp]
    type = ADSideAverageMaterialProperty
    property = effective_normal_compression
    boundary = fracture_interface
  []
  [effective_normal_compression_mpa_pp]
    type = ParsedPostprocessor
    pp_names = effective_normal_compression_pp
    expression = 'effective_normal_compression_pp * 1e-6'
  []

  [czm_dn_pp]
    type = ADSideAverageMaterialProperty
    property = czm_dn
    boundary = fracture_interface
  []

  [czm_dn_total_pp]
    type = SideAverageMaterialProperty
    property = normal_opening_total
    boundary = fracture_interface
  []

  [czm_normal_dilation_paper_mm_pp]
    type = ParsedPostprocessor
    pp_names = czm_dn_total_pp
    expression = '-czm_dn_total_pp * 1e3'
  []

  [frac_normal_jump_avg]
    type = ADSideAverageMaterialProperty
    property = czm_dn_global
    boundary = fracture_interface
  []
  [frac_normal_dilation_paper_mm]
    type = ParsedPostprocessor
    pp_names = frac_normal_jump_avg
    expression = '-1.0e3 * frac_normal_jump_avg'
  []

  [mechanical_aperture_pp]
    type = ADSideAverageMaterialProperty
    property = mechanical_aperture
    boundary = fracture_interface
  []
  [mechanical_aperture_raw_pp]
    type = ADSideAverageMaterialProperty
    property = mechanical_aperture_raw
    boundary = fracture_interface
  []
  [aperture_open_pp]
    type = ParsedPostprocessor
    pp_names = frac_normal_jump_avg
    expression = 'if(frac_normal_jump_avg > 0.0, frac_normal_jump_avg, 0.0)'
  []

  [effective_normal_paper_frame_mpa_pp]
    type = ParsedPostprocessor
    pp_names = 'differential_stress_reaction_mpa_pp injection_pressure_pp pp_outlet_pp'
    expression = '30.0 - 0.5*(injection_pressure_pp + pp_outlet_pp)*1e-6 + 0.25*differential_stress_reaction_mpa_pp'
  []
  [shear_stress_paper_frame_mpa_pp]
    type = ParsedPostprocessor
    pp_names = differential_stress_reaction_mpa_pp
    expression = '0.433012701892219*differential_stress_reaction_mpa_pp'
  []


  # ---------------------------------------------------------------------------
  # 93-series: loading-frame and bulk-kinematics diagnostics.  These existed only
  # on SW-S4 (87 postprocessors vs 70 on the other three), which made the four
  # specimens impossible to compare channel-for-channel.  Nothing here feeds the
  # Table-2 gate; they are diagnostics.  Task #82.
  # ---------------------------------------------------------------------------
  [axial_command_m_pp]
    type = FunctionValuePostprocessor
    function = axial_disp_ramp
  []
  [top_disp_z_mean_m_pp]
    type = SideAverageValue
    variable = disp_z
    boundary = top_nodeset
  []
  [machine_spring_gap_m_pp]
    type = ParsedPostprocessor
    pp_names = 'top_disp_z_mean_m_pp axial_command_m_pp'
    expression = 'top_disp_z_mean_m_pp - axial_command_m_pp'
  []
  [machine_spring_sigma1_mpa_pp]
    type = ParsedPostprocessor
    pp_names = machine_spring_gap_m_pp
    expression = 'abs(machine_spring_gap_m_pp) * ${axial_bc_penalty} * 1e-6'
  []
  [reaction_vs_machine_spring_mpa_pp]
    type = ParsedPostprocessor
    pp_names = 'sigma1_reaction_mpa_pp machine_spring_sigma1_mpa_pp'
    expression = 'sigma1_reaction_mpa_pp - machine_spring_sigma1_mpa_pp'
  []

  # Barton-Bandis envelope evolution.  All six are declared by
  # OrcaBartonBandisContactTractionFastADHardening on every BBFast deck.
  [bb_normal_closure_pp]
    type = ADSideAverageMaterialProperty
    property = bb_normal_closure
    boundary = fracture_interface
  []
  [bb_normal_closure_um_pp]
    type = ParsedPostprocessor
    pp_names = bb_normal_closure_pp
    expression = 'bb_normal_closure_pp * 1e6'
  []
  [bb_law_normal_stress_pp]           # sigma_n the BB law computed from its closure (Pa, +compression)
    type = SideAverageMaterialProperty
    property = bb_compressive_normal_stress
    boundary = fracture_interface
  []
  [bb_peak_friction_angle_pp]
    type = SideAverageMaterialProperty
    property = bb_peak_friction_angle_degrees
    boundary = fracture_interface
  []
  [bb_mu_peak_pp]
    type = SideAverageMaterialProperty
    property = bb_peak_friction_coefficient
    boundary = fracture_interface
  []
  [bb_jrc_mobilized_pp]
    type = SideAverageMaterialProperty
    property = bb_jrc_mobilized
    boundary = fracture_interface
  []
  [bb_normal_stiffness_tangent_pp]    # tangent Kn along the power-law closure (Pa/m)
    type = SideAverageMaterialProperty
    property = bb_normal_stiffness_tangent
    boundary = fracture_interface
  []

  # Bulk (LVDT-analogue) kinematics: two probes on the cylinder surface straddling
  # the fracture, resolved onto the fracture plane with THIS specimen's theta.
  # 93-series rule: z = L/2 +- 50 mm, i.e. a 100 mm gauge on all four specimens.
  [bulk_disp_x_upper_pp]
    type = PointValue
    variable = disp_x
    point = '${sample_radius} 0 0.11635'
  []
  [bulk_disp_z_upper_pp]
    type = PointValue
    variable = disp_z
    point = '${sample_radius} 0 0.11635'
  []
  [bulk_disp_x_lower_pp]
    type = PointValue
    variable = disp_x
    point = '${sample_radius} 0 0.01635'
  []
  [bulk_disp_z_lower_pp]
    type = PointValue
    variable = disp_z
    point = '${sample_radius} 0 0.01635'
  []
  [bulk_delta_x_pp]
    type = ParsedPostprocessor
    pp_names = 'bulk_disp_x_upper_pp bulk_disp_x_lower_pp'
    expression = 'bulk_disp_x_upper_pp - bulk_disp_x_lower_pp'
  []
  [bulk_delta_z_pp]
    type = ParsedPostprocessor
    pp_names = 'bulk_disp_z_upper_pp bulk_disp_z_lower_pp'
    expression = 'bulk_disp_z_upper_pp - bulk_disp_z_lower_pp'
  []
  [bulk_normal_dilation_paper_mm_pp]
    type = ParsedPostprocessor
    pp_names = 'bulk_delta_x_pp bulk_delta_z_pp'
    expression = '-(bulk_delta_x_pp*${bulk_cos_theta} - bulk_delta_z_pp*${bulk_sin_theta}) * 1e3'
  []
  [bulk_shear_slip_mm_pp]
    type = ParsedPostprocessor
    pp_names = 'bulk_delta_x_pp bulk_delta_z_pp'
    expression = 'abs(bulk_delta_x_pp*${bulk_sin_theta} + bulk_delta_z_pp*${bulk_cos_theta}) * 1e3'
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
    petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
    petsc_options_value = ' lu       mumps'
  []
[]

[Executioner]
  type = Transient
  solve_type = Newton
  line_search = l2
  start_time = 0
  end_time = 2852.530000

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.75
    optimal_iterations = 18
    growth_factor = 1.2
    cutback_factor = 0.5
  []

  dtmax = 0.75
  dtmin = 1e-6
  l_max_its = 50
  l_tol = 1e-4
  nl_max_its = 70
  nl_abs_tol = 1e-4

  nl_rel_tol = 1e-6
[]

[Outputs]
  [console]
    type = Console
    execute_postprocessors_on = none
  []
  [csv]
    type = CSV
    file_base = ${csv_file_base}
  []
  [exodus]
    type = Exodus
    file_base = ${exodus_file_base}
    execute_on = 'TIMESTEP_END FINAL'
    time_step_interval = 10
  []
  [chk]
    type = Checkpoint
    file_base = ${checkpoint_file_base}
    time_step_interval = 800
    num_files = 1
  []
[]
