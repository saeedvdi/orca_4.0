# =============================================================================
# 93-SERIES -- MESH AND POSTPROCESSOR AUDIT FIXES.  SW-S3 mesh 5
# Built from 92_03_sw3_final_paperjrc_resc1p40.i.  Constitutive parameters are UNCHANGED;
# this series changes only what is measured and reported, plus one source-node
# coordinate on SW-T1 mesh-5.
#
# WHAT MOVED IN THIS DECK
#   1. OUTPUT-ONLY REPORTING KNOBS REMOVED.  SW-S3 was the only one of the four
#      specimens setting reported_reversible_normal_opening_scale = 0.758 and
#      reported_reversible_normal_opening_retention_fraction = 0.552 (library
#      defaults 1.0 and 0.0).  The source labels both OUTPUT ONLY: they change
#      neither contact, nor aperture, nor permeability, nor flow -- only the
#      reconstruction of normal_opening_total, which is exactly the channel the
#      Table-2 gate scores for d_n.
#      MEASURED COST OF THE HONEST SETTING: d_n nRMSE 2.46 % with the knobs,
#      7.42 % off the raw kinematic jump (+4.96 points).  SW-T1 and SW-T2, whose
#      knobs were already at defaults, show delta 0.00 between the two channels --
#      which is how we know the knobs, and not the channel choice, are the effect.
#      SW-S3's headline five-observable mean therefore moves 3.59 % -> 4.58 %.
#      This is a disclosure/consistency fix, not a physics fix: a two-parameter
#      fit on the reporting path is invisible in the scorecard, and three of the
#      four specimens do not use it.
#   2. TWENTY DIAGNOSTIC CHANNELS ADDED (task #82).  SW-S4 carried 87
#      postprocessors and the other three carried 70; the eight bb_* envelope
#      channels, the five loading-frame channels and the seven bulk_* kinematic
#      channels existed only there.  All eight 93-series decks now emit the same
#      91.  None of them feeds the Table-2 gate.
#      bulk_sin_theta / bulk_cos_theta are set from THIS specimen's own theta
#      (29.0 deg), not copied from SW-S4.
#
# WHAT DID NOT MOVE, ON ANY 93-SERIES DECK
#   - every constitutive parameter of [czm_contact];
#   - the mesh file, the injection schedule, the BCs, the solver;
#   - the paper-frame trig constants (each already matched its own mesh's theta
#     to four decimals -- verified against the Exodus fracture_interface nodeset).
# =============================================================================
# =============================================================================================
# 97_03_sw3_cyclic3
#
# 92-SERIES: close out the four-specimen validation.  Back-analysis of the 91-series, 2026-08-17.
#
# Parent: 97_03_sw3_cyclic3.i
#
# WHERE THE CAMPAIGN STANDS.  Every 90- and 91-series run was re-scored against the paper's own
# Table 2 with scripts/table2_gate.py -- eleven injection hold stages, five independent measured
# quantities each (Q, sigma'_n, tau, d_n, d_s), normalised by the measured range of each column:
#
#     specimen  case    Q      sigma'n  tau     d_n     d_s     MEAN nRMSE
#     SW-T1     90_01   4.12   5.78     7.98    5.53    6.37     5.96
#     SW-T1     91_01  13.41   2.97     4.14   13.40    5.52     7.89
#     SW-T1     91_02   7.38   1.98     2.73    9.06    1.02     4.44   <-- best SW-T1
#     SW-T2     90_03   7.59   2.87     3.88    3.46    2.95     4.15
#     SW-T2     91_03   4.46   1.06     1.43    2.36    2.63     2.39
#     SW-T2     91_04   5.87   1.26     1.70    2.06    1.25     2.43   <-- SW-T2 FINAL
#     SW-S3     90_05   8.66   2.82     6.93   14.48   17.12    10.00
#     SW-S3     91_05   3.24   4.30    10.30    4.74    2.75     5.07   <-- best SW-S3
#     SW-S3     91_06   9.78  16.90    40.32   44.93   44.00    31.19
#     SW-S4     90_07   5.22   4.00    10.61    4.30    6.27     6.08
#     SW-S4     90_08   4.94   3.74    10.01    4.53    7.01     6.05   <-- SW-S4 FINAL
#     SW-S4     91_07   9.43  11.23    28.86   20.57   24.26    18.87
#     SW-S4     91_08   4.77   6.49    16.70   24.46   32.02    16.89
#
# THE RESIDUAL-COHESION KNOB IS NOW BRACKETED ON EVERY SPECIMEN.  Interpolating each observable
# between the two runs of a bracket and asking what parameter value would put it on the paper
# gives, per specimen:
#
#     SW-T2 (8.74 -> 9.71 MPa):  tau 9.15  sigma'n 9.15  d_s 9.65  d_n 9.36  Q 8.51
#     SW-T1 (7.21 -> 9.19 MPa):  tau 8.48  sigma'n 8.47  d_s 9.05  d_n 12.5  Q 11.7
#     SW-S3 (0.00 -> 1.65 MPa):  tau 0.76  sigma'n 0.73  d_s 1.40  d_n 1.22  Q 1.81
#
# SW-T2's five estimates agree to +-0.6 MPa: the parameter is identified, both bracket arms
# straddle it, and neither is more than 0.6 MPa away.  SW-T2 is done.  SW-T1 and SW-S3 SPLIT --
# their stress channels want one value and their displacement/flow channels want another.  A
# split like that is not a mis-set parameter; it means one knob is being asked to do two jobs.
#
# SW-S3's SPLIT, AND WHAT CAUSES IT.  The residual-cohesion estimates divide into a stress pair
# (tau 0.76, sigma'_n 0.73 MPa) and a displacement/flow triple (d_n 1.22, d_s 1.40, Q 1.81).
# 91_05 runs 1.65 MPa -- above even the displacement group -- so it matches d_n and d_s (4.74 and
# 2.75% nRMSE, the best in the campaign for SW-S3) while leaving tau 1.1-1.7 MPa high on every
# unloading stage.
#
# The split is not a mis-set cohesion.  Measure the secant tau-slip stiffness of the system
# across the slip event, dtau/dd_s between the Table-2 stages that straddle it:
#
#     specimen   measured   model    ratio
#     SW-T1        70.6      70.6     1.00
#     SW-T2        82.6      80.6     0.98
#     SW-S4       107.9      99.9     0.93
#     SW-S3       153.0     123.5     0.81   <-- 19% too compliant
#
# Three of the four specimens reproduce the experiment's tau-slip stiffness to within 7%.  SW-S3
# does not, so on SW-S3 alone a given amount of slip sheds too little shear traction, and no
# single residual cohesion can put both tau and d_s on the paper at once.  SW-S3's
# axial_bc_penalty is already 1.0e13 Pa/m -- effectively rigid, and the stiffest of the four --
# so the remaining compliance is the rock and the interface, not the frame, and it is not a
# tunable.  What is left is to choose where in the split to sit.
#
# THIS DECK: residual_cohesion 1.65e6 -> 1.40e6 Pa.  Nothing else moves.  The value is inside the
# displacement group rather than at its top, which should give back ~0.4 MPa of the tau excess
# for a few um of slip.  The pair 1.40 / 1.20 brackets the median of the five estimates (1.22).
#
# WHY THE DISPLACEMENT SIDE AND NOT THE STRESS SIDE.  Dropping to 0.75 MPa would satisfy tau and
# sigma'_n, but the stiffness deficit above means the model would then have to slip ~20% further
# to shed the same traction -- it would reproduce the paper's residual stress for the wrong
# reason, by over-sliding.  d_n and d_s are what the joint model actually predicts; tau on the
# unloading branch is partly a loading-path quantity.  91_05's 5.07% mean is the reference to
# beat; if neither arm beats it, 91_05 is final.
#
# HPC: submitted with scripts/make_hpc_nochk_jobs.py output; --chdir is pinned absolutely so
# SLURM can open logs/ regardless of the submission directory.  Outputs/chk is disabled and the
# file_base names differ from the parent deck.
# =============================================================================================
# ==============================================================================
# 89_02_sw3_bbfast_paperjrc_kernel_SV_biot0p6
# GENERATED 2026-08-16 by scripts/build_paper_corrected_decks.py from
#   SWS3/86_01_sw3_bbfast_biot0p6_phir8p45_m0_kernel_SV.i
# -- do not hand-edit; regenerate instead. The parent is left untouched.
#
# WHY: scripts/paper_parameter_audit.py compared all four decks against Ye &
# Ghassemi (2018) itself rather than against each other, and found that several
# constants presented as measured joint properties were invented. Every value
# changed below is derived in scripts/refit_joint_constants_from_paper.py from
# the paper's own Table 1, Table 2 and Sec. 2.1. Nothing is tuned to a run.
#
# CONTROLLED AXIS: joint constants only (the SW-S3 mesh is already at its Table-1 angle)
#
# JOINT  JRC 23.35 -> 1.96, JCS 300 -> 150 MPa, phi_r 8.45 -> 29.756 deg.
# 23.35 is 11.9x the paper's measured 1.96 AND outside Barton's 0-20 scale;
# phi_r = 8.45 deg existed only to compensate for it. The refitted 29.756 deg
# sits squarely in the measured granite basic-friction range.
# The old envelope's mu rises 0.607 -> 0.800 across the injection sweep and sits
# 12-31 % ABOVE the measured tau at every loading hold; the new one is flat at
# 0.603 -> 0.618 and passes exactly through the last stick stage.
# Slip-weakening slope at onset falls 2.084e11 -> 1.797e11 Pa/m (13.8 % more
# stable), so this cannot introduce a strength cliff the parent does not have.
# W/L -> 0.812485740964 and fluid_bulk_modulus -> 2.2e9 as elsewhere.
#
# NOTE the SW-S3 mesh is 124.40 mm long against the paper's 123.40 mm. That
# needs Cubit, which is not available here; mesh/sw3_mesh_L123p4.jou carries the
# corrected journal and mesh/README_mesh_length.md records what it changes
# (0.8 % on axial stiffness only -- the flow path length is set from Table 2).
#
# UNCHANGED AND DELIBERATELY SO: slip-weakening D_c, exponent and tail floor;
# dilation angles; normal-closure constants; hydraulic constants; every BC and
# the load path. The tail floor is an ABSOLUTE friction coefficient with no JRC
# or JCS in it, so refitting the peak envelope leaves its calibration valid.
#
# STATUS: CORRECTION. The parent deck's own header already concedes that JRC = 23.35 is 'an explicitly labeled effective transfer parameter, not a measured joint property'. This deck makes it the measured one.
# ==============================================================================
# =============================================================================
# SW-S3 at the PHYSICAL Biot coefficient, with the slip-onset envelope refitted.
# Derived from 84_01_..._kernel_SV_biot0p6.i on 2026-08-16.  See
# doc/sample_parameter_unification_2026-08-16.md
#
# WHY.  84_01 was calibrated at biot_coefficient = 1e-12 and scores within 4%
# on every channel there (diff stress 0.996, injection 1.000, flow 1.039,
# permeability 1.001, dilation 0.987, sigma'n 1.008, slip 1.010, tau 0.989).
# Raising alpha to the physical 0.6 -- to agree with SW-S4 and with alpha > phi --
# breaks only ONE thing, the slip onset, and every other reported symptom follows
# from it:
#
#     onset (5% of final slip)   2394 s -> 2062 s   (experiment 2451 s)
#     final slip                 0.0743 -> 0.0930 mm (experiment 0.0737)
#     dilation ratio              0.987 -> 1.193
#     flow ratio                  1.039 -> 1.168
#
# Dilation is not an independent error: dilation/slip = tan(dilation angle)
# identically, so fixing slip fixes dilation and the flow/permeability that
# follow the aperture.
#
# SIZING.  In the 330 s before onset the alpha=0.6 run closes its strength margin
# (limit_tau - tau) at -0.00150 MPa/s.  Delaying onset by the required 389 s
# therefore needs about 0.58 MPa more limit_tau.  At the operating sigma'_n of
# 24.9 MPa, d(tau_limit)/d(phi_r) = 0.613 MPa/deg, so delta phi_r ~ 0.95 deg.
#
# WHY phi_r AND NOT jrc.  Both move the envelope, and jrc would need only +0.88.
# But SW-S3 already runs jrc = 23.35, above the Barton scale's 0-20 range, and
# phi_r = 7.5 deg is far below any measured granite basic friction angle (~30).
# Raising phi_r moves toward the physical value; raising jrc moves further from
# it.  slip_weakening_residual_friction_angle_degrees is moved in step so that
# the two stay equal and weakening still comes only from roughness degradation,
# exactly as in 84_01.
#
# CAVEAT ON THE SIZING.  The margin above is a SIDE AVERAGE over the whole
# fracture, while yield begins locally.  A side-averaged extrapolation cannot
# resolve onset on its own -- it gives a magnitude, not a prediction.  That is
# why this is run as a bracket (86_01 phi_r = 8.45, 86_02 phi_r = 9.00) rather
# than as a single computed answer.
#
# ALSO CHANGED: youngs_modulus 75e9 -> 67e9.  The SW-S3 family was the only one
# at 75e9; every other deck uses 67e9, and orca_3.0_full records 67e9 as
# "paper Sec. 2.1".  75e9 has no provenance anywhere.
#
# THIS DECK: residual_friction_angle_degrees = 8.45
# =============================================================================

# ==============================================================================
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6
# GENERATED 2026-08-15 from 84_01_sw3_bbfast_postevent_retreat4p5um_m0.i -- do not hand-edit; regenerate instead.
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
#      in 84_01_sw3_bbfast_postevent_retreat4p5um_m0.i.
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
# The parent deck 84_01_sw3_bbfast_postevent_retreat4p5um_m0.i is left untouched as the reference configuration.
# ==============================================================================
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# SW3 Level 84 orthogonal-residual campaign.
# Parent: SW3_83_KINEMATIC_DECOUPLING/83_01_sw3_bbfast_outputscale0p758_ret0p552_m0
# Parameters: post-event axial actuator retreat=4.5um over t=2550-2850s
# Hypothesis: The BBFast shear residual is post-event positive, not globally negative. A delayed retreat should reduce q by about 2.1MPa and paper shear by about 0.9MPa without changing the failure event.
# Decision rule: Keep only if late shear improves while slip, reported dilation, permeability, and flow remain within their guardrails.
# Raw CZM slip remains in czm_shear_slip_mm_pp; reported slip is a separate column.
######################################################################################
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# SW3 Level 83 kinematic-decoupling campaign.
# Parent: SW3_82_RESIDUAL_CORRECTIONS/82_00_sw3_bbfast_exact81_00_control_m0
# Parameters: reported reversible scale=0.758; reclosure retention=0.552; activation=50um
# Hypothesis: The 82_00 decomposition gives 35.764um irreversible opening plus a 13.028um peak reversible part; the validation peak/end solve directly to scale=0.7574 and retention=0.5517.
# Decision rule: Keep only if peak and terminal dilation are within 1um and all traction, slip, permeability, and flow columns reproduce 83_00.
# This is a bounded back-analysis test, not an open-ended sweep.
######################################################################################
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# SW3 Level 82 residual-correction campaign.
# Parent: SW3_81_SOURCE_CORRECTIONS/81_00_sw3_bbfast_source_control_m1
# Parameters: exact 81_00 control; initial dt restored to 0.75 s
# Hypothesis: The Level 82 build and generator must reproduce the completed BBFast base.
# Decision rule: Reject all BBFast candidates if this control changes beyond numerical tolerance.
# This is a bounded back-analysis test, not an open-ended sweep.
######################################################################################
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# SW3 Level 81 focused source-correction confirmation.
# Parent: SW3_80_POSTPEAK_SOURCE/80_00_sw3_bbfast_exact78_01_control_m0
# Parameters: 78_01/80_00 retention=0.06 with new reclosure multiplier=1
# Hypothesis: The default new source path must reproduce the preferred BBFast parent.
# Decision rule: Reject the source change if this differs from the parent beyond nonlinear solver tolerance.
# This is a confirmation bracket, not an open-ended sweep.
######################################################################################
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# SW3 Level 80 post-peak source validation.
# Parent: SW3_78_MECHANICS_FIRST_LOCAL/78_01_sw3_bbfast_retention0p06_from77_03_m0
# Parameters: exact 78_01 mechanics/hydraulics with the new paper-frame postprocessors
# Hypothesis: Recover a complete, current-build CSV for the user's preferred case; the archived 78_01 CSV was overwritten/incomplete although its figures remain.
# Decision rule: Must reproduce the archived 78_01 curves and provides the direct control for 80_01/80_02 plus the new paper-frame stress audit.
# All unlisted load-path, mesh, hydraulic, constitutive, and numerical inputs are inherited unchanged.
######################################################################################
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# SW3 78-series mechanics-first sweep with local and Slurm launch options.
# Parent: SW3_77_EFFICIENT_THREE_PER_LAW/77_03_sw3_bbfast_jrc23p35_exp1p4_ld60_eta4e11_m0
# Parameters: retention=0.06; all shear, dilation, and hydraulic parameters held at 77_03
# Hypothesis: Primary prediction: retain more post-event opening so terminal normal compression and dilation improve together without changing the already accurate terminal shear slip.
# Decision rule: Accept if terminal sigma_n decreases toward 24.73 MPa without making peak opening more negative than the 77_03 peak.
# Numerical policy: automatic residual scaling OFF; initial dt=0.75 s; dtmax=0.75 s.
# Physical gates are enforced by run_local_78.py and score_78_sweeps.py.
######################################################################################
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# SW3 77-series efficient back-analysis: three direct cases per law.
# Parent: SW3_75_CORRECTED_DILATION_SWEEPS/75_01_sw3_bbfast_jrc23p2_dil26_26_eta5e11_m0
# Parameters: JRC=23.35; weakening exponent=1.4; Ld=60um; eta=4e11; hydraulic p=4; gouge=0.40um after 30um
# Controlled sweep axis: BBFast weakening-shape conservative exponent
# Back-analysis: This is the smallest departure from the stable 75_01 constitutive shape. The paired D=60 um again holds the 50-um strength nearly fixed, so the comparison isolates curvature.
# Numerical policy: automatic residual scaling OFF; initial dt=0.75 s; dtmax=0.75 s.
# Hydraulic correction is mechanistic, not a permeability multiplier: k remains a_h^2/12.
######################################################################################
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# 75-series corrected-dilation back-analysis; direct run, no selection gate.
# Clean parent: SW3_74_REFINED_SWEEPS/74_01_sw3_bbfast_jrc23p8_phi7p5_eta5e11_m0
# Sweep parameters: jrc=23.2;dilation_deg=26_to_26;eta=5e11
# Purpose: earliest clean BBFast onset bracket with reduced peak-dilation overshoot.
# Numerical policy: automatic scaling OFF (retained from the clean completed parent).
# Loading, E=75 GPa/pc=0.87 common control, mesh, outputs, tolerances, and
# dtmax=0.75 s are unchanged. Dilation validation is already in millimetres.
######################################################################################
######################################################################################
# 84_01_sw3_bbfast_postevent_retreat4p5um_m0
# Generated from clean completed source 72_01_sw3_bbfast_dil28_26_eta2p5e11_m0.
# Sweep parameters: jrc=23.8;phi_tail_deg=7.5;eta=5e11
# Purpose: central clean BBFast correction from the stable 72 deck.
# Numerical policy: automatic scaling OFF (the 73 BBFast/BBFlow high-eta preload
# branches were invalid); physical loading, common E=75 GPa/pc=0.87 control,
# mesh, constitutive tolerances, dtmax=0.75 s, and outputs are unchanged.
######################################################################################
######################################################################################
# 72_01 BACK-ANALYSIS CORRECTION: BBFast
# E=75 GPa is fixed by the measured event stiffness. Relative to completed 71_01,
# dilation 32/29.45 -> 28/26 deg corrects excessive opening and eta 1e12 -> 2.5e11
# shortens the over-slow traverse. Strength JRC=24 and Dc=55 um are held for attribution.
######################################################################################
######################################################################################
# 71_01: SW3 BBFast correction candidate (effective JRC=24, eta=1e12 Pa.s/m)
# Direct run: common controls are baked into this input; no Stage-1 selection file is required.
# Relative to 70_01, JRC delays its 480-s-early onset and eta shortens the slow event.
#
# Common parent: 59_07 corrected SW3 Table-2 / constant-piston / reaction-force deck.
# Constitutive material: OrcaBartonBandisContactTractionFastADHardening
# Calibration status: first SW3 transfer; requires calibration.
#
# INVARIANTS ACROSS 70_01/11/21/31:
#   mesh sw3_mesh_size5.e; full t=0..4802 s SW3 pressure schedule; constant actuator
#   command after the 55 s preload; coupled bulk HM; fault-pressure coefficient 0.85;
#   Table-2 a_h0=floor=1.22 um; paper Eq. (9) W/L=0.81; reaction differential stress;
#   inlet/outlet residual-flux diagnostics; dtmax=0.75 s; identical BCs and outputs.
#
# INTENDED DIFFERENCES: the [Materials]/[czm_contact] block and its law-local
# calibration/regularization values. Do not call these four laws equally calibrated:
# BBFlow has the corrected completed parent, MC/PST transfer prior SW3 calibrations
# onto corrected controls, and BBFast is the explicitly documented first SW3 transfer.
######################################################################################
######################################################################################
# DECK 59_07 (SW3_July18, 2026-07-20): audit baseline — Table 2, constant piston,
# external reaction stress, and two independent flow-rate diagnostics.
#
# This is intentionally forked from completed case 59_05; 59_05 is not overwritten.
# Changes are limited to corrections required by the Ye & Ghassemi SW-S3 experiment:
#   1. Constant actuator command after the t=55 s preload. The paper states that the
#      loading piston did not move during injection; the 59_05 t=2500–2800 retreat
#      is therefore disabled instead of being used to manufacture the stress drop.
#   2. Table-2 hydraulic aperture restored: a_h0 = floor = 1.22 um (k=1.24e-13 m2).
#      The old 0.709 um / 0.42e-13 curve came from a log-axis digitization error.
#   3. Hydraulic dilation transfer reset to 0.038 as a first Table-2 back-analysis:
#      target a_h is 1.22 -> 2.10 -> 1.64 um. This changes permeability only; the
#      mechanical normal jump remains an independently scoreable output.
#   4. Paper Eq. 9 W/L=0.81 is the primary validation reconstruction. The numerical
#      source-node-spacing estimate W/L=0.674 is retained as a separate diagnostic;
#      moving mesh ports without measured borehole coordinates would be unjustified.
#   5. Differential stress from the applied top reaction is added. Local fault stress
#      and bulk/top stress remain diagnostics, but are not mixed into one q curve.
#   6. Both inlet and outlet residual fluxes plus mass imbalance are exported.
#   7. dtmax 0.75 s improves resolution of the reported <10 s dynamic interval.
#
# Deliberately held fixed for attribution: effective JRC=25.1 calibration, JCS,
# friction/state parameters, contact penalties, pressure-traction coefficient=0.85,
# and the empirical 29.45-degree dilation clamp. JRC=1.96 is the measured surface
# value; 25.1 must be treated as an effective strength calibration, not a measurement.
# FALSIFIERS:
#   - If q_reaction rises before failure while the piston command is constant, the
#     rise is an internal poromechanical/model response, not a hidden BC ramp.
#   - If reaction q differs materially from top-stress q, score only reaction q and
#     audit boundary force completeness before changing friction.
#   - If residual flow and Eq. 9 flow disagree at pressure holds, inspect port/path
#     geometry and transient storage; do not retune aperture to force both to agree.
######################################################################################
######################################################################################
# DECK 59_05 (SW3_July18, 2026-07-20, ROUND 4): coupling onset lever (coeff 0.85) - later-onset bracket
#
# ROUND-3 REALIZED (local 8-rank; MD "Round 4"; data in parens):
#   deck        onset2  slip_end  tau_end  trough      perm_pk   L_end   note
#   58_03 PST   2193    83.5      (2.00)   15.02@2742  1.407     (13.86) STOPPED t=3183 (inj still 23.7 -> mid-unload; end-state NOT scoreable)
#   59_03 BB    2149    83.7       1.03    14.40@2699  1.532      12.91  full run t=4802
#   DATA        2378    73.7       2.30    15.42@2639  1.231      12.77
# THE DIAGNOSIS (why the r2->r3 strength sweeps kept overshooting onset):
#   ONSET TIME IS ILL-CONDITIONED AGAINST THE STRENGTH ENVELOPE. Near the critical
#   load the creep-to-instability clock is near-vertical: BB jrc 24.7 -> onset 2096,
#   25.1 -> 2149 (133 s per unit jrc), but 25.5 -> ~2550 (1000 s per unit) - a >7x
#   sensitivity jump over 0.4 jrc. Any strength lever (jrc, jcs, phi_r; PST peak_mu)
#   has this pathology because it moves the THRESHOLD while the load creeps up to it.
#   => onset overshoots every round. THE WELL-CONDITIONED LEVER IS THE LOAD SIDE:
#   fault_pressure_coefficient sets d(sigma'n)/d(injection), so it shifts onset TIME
#   ~linearly (~96 s per 0.01, from the injection ramp-rate arithmetic) and cannot
#   flip to no-burst. Bonus: raising sigma'n during the burst ALSO lifts the trough
#   (14.4 -> ~15.4) AND tempers the over-drive (stronger fault -> arrests sooner ->
#   less of the +10 um overshoot) AND lowers perm (less BB-closure opening). One
#   physical knob moves onset+trough+overshoot+perm all toward the data.
#   SECOND MISS = RELAX OVERLAP: the servo unload (du) must overlap the burst (data L
#   drops 14.5->12.7 DURING 2400-2500). r3 relax_t0 2450 fired AFTER the early (2149)
#   burst had already run at full L 16.6 -> +10 um. Fix: slave relax_t0 to onset.
#   THIRD (tau_end): 59_03 L_end 12.91 ~ data 12.77 ALREADY; its tau_end 1.03 is
#   ENTIRELY the slip overshoot (L_end - k*s: 12.91 - 0.142*73.7 = 2.44 if slip were
#   right). Fix the slip and tau_end self-corrects. Same L-identity as SW-S4.
# NO SOURCE CHANGE. BB dilation-slaving (the SW-S4 issue) does not bite here: dn is
#   diagnostic (zeta 0.27) and perm is OVER not under, so the slaved burst dilation is
#   if anything too generous. The recurring pain was calibration conditioning, not
#   missing physics - solved on the deck side.
# ROUND-4 MATRIX (dscale 0.0225 UNCHANGED - coupling+slip-fix drop perm on their own;
#   trim only if perm still >1.5 next round):
#   59_04 BB  coeff 0.86  relax_t0 2410  (nominal: onset ~2340)
#   59_05 BB  coeff 0.85  relax_t0 2500  (later-onset bracket: onset ~2435)
#   59_06 BB  coeff 0.86  SLIP-TRIGGERED relax (probe: auto-arrest, no timing chase)
#   58_04 PST coeff 0.86  relax_t0 2410  (nominal)
#   58_05 PST coeff 0.85  relax_t0 2500  (later-onset bracket)
# ATTRIBUTION: 04 vs 59_03/58_03 = the coupling+overlap fix; 05 vs 04 = coupling
#   sensitivity (relax tracks onset); 06 vs 04 = time-relax vs slip-triggered relax
#   (does auto-relax remove the onset<->relax chase?).
# THIS DECK: BB coeff 0.88->0.85 (onset ~2435), relax_t0 2450->2500. Brackets 59_04 on the late side so the 0.88/0.86/0.85 triple gives a clean coeff->onset map (relax >= onset in all three).
# EXPECT: onset 2380-2520; slip end 73-78; tau_end 2.1-2.7; trough 15.2-16.0; perm pk 1.15-1.35; L_end ~12.8. If onset lands 2360-2400 this is the winner.
# FALSIFIERS: onset >2540 or no burst by 2560 -> coeff too low, back to 0.86 AND relax_t0 -> 2540; trough >16.2 -> coupling over-strengthened, use 0.86; else as 59_04.
# ---- parent 59_03 banner below ----
######################################################################################
# DECK 59_03 (SW3_July18, 2026-07-19, round 3): jrc re-split + relax overlap + dscale
#
# 59_02 RESULT (local 8-rank, full t=4802; MD "Round 3"): the AHFLOOR fix + gate 2um
# + jrc 24.7 SWUNG PAST CENTER: 2um creep at 2096 (data 2380; 59_01 with jrc 25.5
# never fired), burst 2250-2500 entirely BEFORE the relax (t0 2550) -> full L 17.3
# -> slip 96.7 um (data 73.7), tau_end 0.69, perm peak 2.35 (data 1.23). The GOOD:
# sn trough 15.15 ~ data 15.4, sn end 26.1 ~ 24.7, and the creep-clock is now
# BRACKETED BOTH SIDES: jrc 24.7 -> 2um @ 2096; jrc 25.5 -> ~2550-2650 (59_01,
# floor-corrected). The tail is post-mortem garbage - do not tune on it.
# THREE fixes (this deck):
#   1. jrc 24.70 -> 25.10: log-interp of the measured bracket for 2um ~ 2350 ->
#      mobilization gate crossed ~2350-2420, burst 2380-2540.
#   2. relax_t0 2550 -> 2450, relax_dur 400 -> 300: overlap the burst (data L 13.94
#      at 2500); arrest ladder (L(t)-tau_res)/k: 90/84/75 um at 2550/2650/2750;
#      du 14.0 kept (locked-fault delivery -0.272 MPa/um -> L_end ~12.8).
#   3. dilation_scale 0.038 -> 0.0225 (x0.59): 59_02 grew a_h +0.92 um at g_np 53 um
#      (pinned 29.45-deg dilation x over-slip); data grew +0.506. At corrected slip
#      ~74: dil*ret 0.40 + BB closure 0.375 lands peak 1.214 (data 1.215), end 0.948
#      (data 0.953).
# EXPECT: onset(2um) 2330-2420, burst 2380-2560, end 72-78, tau_end 2.0-2.6, sn
# trough 15.0-15.8, perm 0.42 -> ~1.2-1.35 -> ~0.8, L_end ~12.8.
# FALSIFIERS: onset < 2280 -> jrc -> 25.3; no burst by 2500 -> jrc -> 24.9 AND
# relax_t0 -> 2550 (59_01 starve mode); end > 80 -> relax_t0 -> 2400; end < 69 ->
# relax_t0 -> 2500; perm peak > 1.5 -> dscale -> 0.019. NOTE flow-rate panel ~6x low
# at matched perm (SW3 area constant, unaudited) - do not tune physics on it.
# ---- original 59_02 banner below ----
# DECK 59_02 (SW3_July18, 2026-07-19, round 2): AHFLOOR bugfix + onset re-arm
#
# 59_01 RESULT (full HPC t=4802): NO BURST - slip end 2.2 um vs data 73.7; tau_end
# 11.84 (elastic lock). FOUR findings from the CSV (full writeup in the SW3 MD):
#   1. APERTURE FLOOR BUG (deck-cut error, mine): initial_hydraulic_aperture was
#      corrected to 0.709 um but min_hydraulic_aperture stayed 1.22 (the v6 "floor =
#      initial" convention) -> a_h clamped straight back to 1.22 and PINNED (perm flat
#      1.24e-13 all run; hydraulic panel inert). FIXED: floor 0.709.
#   2. THE DESIGN sn PATH NEVER ARRIVES: round-1 sized the jrc 25.5 envelope to cross
#      at sn ~ 22, but the REALIZED pre-burst path bottoms at sn 23.4-23.7 (quasi-
#      steady fracture pressure mean ~17.4 is pinned by the outlet BC at 5 MPa and
#      sn_tot RISES poroelastically 39.0 -> 41.0). g-crossing with 25.5 came only at
#      ~2550-2600 - marginal and too late. FIXED: jrc 24.70 -> crossing at sn ~ 25.3
#      (t ~ 2380-2450) ON THE REALIZED PATH. Residual cost ~0.2 deg at arrest y.
#   3. GATE UNCROSSABLE: mobilization_onset_slip 4 um (imported from SW-S4 57_05) vs
#      realized pre-onset creep of only 2.0 um by t=2500 -> the table never started
#      decaying -> no self-acceleration. SW-S4 forgives late gates (repeated injection
#      steps); SW-S3 gives ONE window. FIXED: back to v21's empirically-anchored 2 um
#      (v21 creep-clock hit 2.00 um exactly at its onset; jrc -0.8 speeds the clock
#      ~x2 -> 2 um by ~2350-2420).
#   4. RELAX: delivery MEASURED on the locked fault: du 16 um -> L 16.50 -> 12.15 =
#      -4.35 MPa (-0.272 MPa/um), overshooting data L_end 12.78 by 0.63 -> du 14.0.
#      And t0 2650 closed the burst window before onset; data L is already 13.9 at
#      t=2500 (servo retreats DURING the burst tail) -> t0 2550, dur 400 kept.
# FIVE changes vs 59_01: min_hydraulic_aperture 1.22e-6 -> 0.709e-6; jrc 25.50 ->
# 24.70; mobilization_onset_slip 4e-6 -> 2e-6; relax_t0 2650 -> 2550; axial_relax_du
# 16.0e-6 -> 14.0e-6. (delta_p 1.60, df/29.45-pin, kappa 8.0e-9, visc 5e12 all kept.)
# EXPECT: onset 2380-2520 (data 2380); burst 0 -> 55-65 um by ~2600-2650; sn trough
# 15-16.5 (data 15.4) NOW REACHABLE (dilation-fed aperture growth unclamped); tail
# creep arrested by the relax at s_end 71-76; tau_end = L_end - 0.142*s_end ~ 2.2-2.7
# (data 2.30); perm 0.42 -> ~1.2-1.5 -> ~0.7-0.9e-13 (data 0.42/1.23/0.76).
# FALSIFIERS: no onset by 2550 (slip < 4 um) -> jrc 24.7 -> 24.4 AND relax_t0 -> 2650
# (do NOT touch the gate); onset < 2300 -> jrc -> 25.0; burst overshoots (slip@2650 >
# 80) -> relax_t0 -> 2500 or visc 5e12 -> 8e12; L_end from CSV: > 13.1 -> du -> 15.5,
# < 12.5 -> du -> 13.0; trough < 14.5 -> check aperture growth (dilation_scale chain)
# before touching strength. KNOWN SCORING CAVEAT: the flow-rate panel reads ~6x low
# at MATCHED perm and matched inlet/outlet (0.144 vs 0.84 ml/min in 59_01) -> the
# flow_rate_validation area/width constant needs an audit for the SW3 mesh; do not
# tune physics against the flow panel until audited. dn stays DIAGNOSTIC (zeta 0.27).
# ---- original 59_01 banner below ----
# DECK 59_01 (SW3_July18, 2026-07-18): SW-S3 VERIFICATION of the SW-S4-validated
# BB flow-RSF product. Fork of SW3 v21 with the three shared deck corrections
# (LOADRELAX restored / a_h0 0.709 um / DMGREV kappa 8e-9 -- see the 58_01 banner:
# v21's own +30 um over-slip is fully explained by its L_end 16.9 vs data 12.78,
# so the v21 MECHANICS with the corrected load line already lands at ~72 um) plus
# TWO BB-specific onset fixes sized from the v21 CSV:
#
# 1) jrc 23.10 -> 25.50: v21 slipped at t=1684 / sn 27.2 (data 2380 / ~22-23) --
#    the envelope crossed too early. tan(8.51 + 25.5*log10(300/23))*0.9*23 ~ 15.3
#    = drive -> crossing at sn ~22 on the corrected (3x slower) pressurization.
#    Residual cost ~+0.55 deg at y(74/1.6)~0.23. Same documented fiction as 23.1
#    (no honest BB saw-cut parameterization), resized to the corrected drive path.
# 2) mobilization_onset_slip 2 -> 4 um (the SW-S4 57_05-validated creep gate):
#    v21's pre-onset creep hit 2.00 um exactly at its onset -- the convex Barton
#    table started burning immediately. 4 um of non-damaging creep arrives only
#    near t ~2350-2400.
#
# peak_shear_displacement 1.60 um KEPT (v21 arrest sizing now correct under the
# restored load line); NO mobilization shelves (SW-S3 is the single-burst sample;
# the MULTISHELF staircase feature stays default-off).
# TARGETS: onset ~2380, slip end 73.7 um, tau_end 2.30, sn trough/end 15.4/24.7,
#   q_end 5.4, k 0.42 -> 1.23 -> 0.76 e-13, Q_pk 0.84.
# FALSIFIERS: onset still >200 s early -> raise mobilization_onset_slip to 6 um
#   (NOT jrc: arrest pays); slip < 65 -> dp 1.6 -> 2.0; slip > 80 with L_end ~12.5
#   -> dp 1.6 -> 1.2; burst dt-crash -> tangential_viscosity 5e12 -> 2e13 (v20
#   banner ladder), then dp +0.4. W/k print will read ~15-20: expected, the burst
#   IS supercritical; flow-RSF + viscosity carry the traverse (57_05 precedent).
# RUN: needs the current MULTISHELF-era build (cluster already has it since 57_05).
######################################################################################
######################################################################################
# DECK SW3 v21 BB FLOWRSF ARRESTFIX (from v20, 2026-07-17)
#
# v20 LOCAL MIDWAY RESULT (16 ranks, t=0-2400, exit 0 -- NOTE: v20 traversed its whole
# burst at dt = 1.5 with ZERO failed steps locally, so the HPC "short time step" failure
# is NOT deck-reproducible; slurm log still wanted). Physics vs data:
#   burst t ~ 1200-1500 (data ~1500-1700: ~250 s early);
#   slip 103.5 um at t=2400 and still creeping (data final 73.7: +40% OVERSHOOT);
#   tau 2.21 MPa at sigma'n 17.7 (data residual ~3.55: OVER-WEAKENED).
# Both misses point the same way: the tail-pinned delta_p = 1.13 um bottoms the backbone
# out too deep/too fast, so the burst jumps past the data's arrest point.
#
# TWO changes vs v20 (uses the NEW mobilization_onset_slip param -> REBUILD orca-opt):
#   1. peak_shear_displacement 1.13e-6 -> 1.60e-6: arrest re-sized on the mobilization
#      table -- backbone at the sigma'n trough (15.25 MPa) crosses the data's residual
#      ratio 0.233 at s = 84 um (v20: ~104+ and still creeping); mu(74 um, trough) =
#      0.262 -> residual tau ~ 3.2-3.5 MPa (data 3.55, v20 gave 2.21). W/k 15.0 -> 10.5
#      (still "> 1: dynamic burst" -- correct for SW-S3).
#   2. mobilization_onset_slip = 2e-6 (NEW param): the first 2 um of plastic slip do not
#      decay JRC_mob. v20's pre-burst creep was ~0.35 um by t=1200 and Barton's table is
#      steepest at x=1, so creep self-fed the early breakaway; the 2 um hold-off delays
#      burst onset toward the data window WITHOUT raising peak or residual (JRC stays
#      23.10; the alternative +1.6 JRC would distort the whole envelope).
# EXPECT: burst onset +200-400 s (toward ~1500), arrest ~80-90 um (data 73.7), residual
# tau ~3.2-3.5, unchanged early/stick phases. Startup print MUST show: JRC_n 23.1,
# delta_p 1.6e-06 m (user), W_max/k_tau ~ 10.5 "> 1: dynamic burst".
######################################################################################
######################################################################################
# DECK SW3 v20 BB FLOWRSF (from v19, 2026-07-17) -- NEW MATERIAL
#
# SW-S3 on OrcaBartonBandisFlowRSFContactTraction: Barton--Bandis strength (phi_r +
# JRC_mob*log10(JCS/sigma'n), Barton 1982 post-peak JRC-mobilization table) on the
# SAME flow-form RSF chassis as v19 (identical penalties, viscosity, RSF set,
# stick_velocity_floor, load path, hydraulics). Only the [czm_contact] block differs;
# calibration, the structural shape miss, the W/k ~ 15 cliff warning, and fallbacks
# are documented at the block. Companion deck: SW4 57_01 (staircase case) -- together
# they put the BB family and the PST law on identical rate structure and numerics.
#
# NOTE v19 STATUS: v19 was reported non-convergent on HPC (2026-07-17, log not yet
# inspected -- cause unknown; the stick-floor fix IS in that build since SW4 56_02 ran
# clean on it, so this is a different mechanism, most likely the burst traverse). This
# deck does not inherit any v19-specific fix beyond the standard guards; its own cliff
# is HARDER (W/k ~ 15 vs 1.64), so treat the first submission as a numerics probe and
# apply the block-header fallbacks if it dies in the burst window.
# REQUIRES a REBUILT orca-opt (new material class: pull + make on the cluster first).
######################################################################################
######################################################################################
# DECK SW3 v19 PST FLOWRSF (from v12, 2026-07-17)
#
# SW-S3 with the NEW paper-derived law: OrcaPeakShelfTailFlowRSFContactTraction
# (see Examples/YeGhasemmi2018/HARDENING_LAW_FROM_YE2018_SW_S3_SW_S4.md).
#
# Three changes relative to v12, all motivated by the 0-D study:
#
# 1) CONSTITUTIVE SWAP: roughness-decay Coulomb + secondary weakening + referenced
#    (clamped) RSF -> peak-shelf-tail friction with FLOW-FORM rate-and-state.
#    Deck-frame backbone: mu_qs = 0.14 + (0.26-0.14)*exp(-s/40um)
#                                 + (0.68-0.26)*exp(-(<s-10um>/25um)^1.4)
#    The m_c = 1.4 concentration branch is the rough-saw-cut knob: W_max ~ 2.7e11 Pa/m
#    at sigma'n = 22 MPa -> W/k ~ 1.4-2 -> single dynamic burst (SW-S3-type), arrested
#    on the mu_shelf = 0.26 SHELF the v12 roughness law lacked (study section 4.1: v12's
#    strength had no stable arrest point; HEAVYVISC was standing in for one).
#
# 2) VISCOSITY OFF THE CRUTCH: tangential_viscosity 3.0e13 -> 5.0e12 (standard value).
#    The flow-form a*sigma'n*asinh(V) direct effect now regularizes the burst arrest.
#
# 3) LOADRELAX DISABLED: axial_relax_du 16um -> 0. The v9 piston-retreat surgery
#    emulated missing post-peak creep/relaxation; the flow form creeps physically
#    (sub-V0 velocities below quasi-static strength), so the artificial load-line
#    correction is removed. If the post-burst tau tail sits high, first check the
#    reported creep velocities before reintroducing any relax.
#
# Onset sizing: deck peak 0.68 realizes ~0.61-0.65 mobilized at the fault (campaign
# realization factor ~0.9), i.e. onset mid-ramp 24->28 MPa like the data. If onset
# lands a step early, raise peak_friction_coefficient by +0.01 first.
#
# FAILURE + FIX RECORD (2026-07-17). First full run (HPC, 64 ranks) died min_dt at the
# ramp->hold transition (last converged t=55.776 s). Root cause, reproduced locally with
# -snes_linesearch_monitor: with the pure always-flow form the preloaded fault creeps at
# V ~ 1e-14 m/s, and |R| floors at a dt-INDEPENDENT plateau (measured 1.70/1.69/1.70e-4 N
# at dt=1.5/0.75/0.375 s; full Newton steps with exact MUMPS solves cannot descend --
# residual structure at the gamma* = V*dt ~ 1e-13 m excursion scale). The ramp masked it
# via nl_rel_tol (|R|0 ~ 1e3 N); the first hold step (|R|0 ~ 3e-3 N) exposed it; dt cuts
# only shrink |R|0 -> death spiral to dtmin. NOT recoverable by IterationAdaptiveDT or
# line search (l2 landed lambda=1 throughout: direction, not step length).
# TWO-PART FIX:
#   1) MATERIAL (rebuild orca-opt required): stick_velocity_floor = 1e-11 m/s (~0.6
#      nm/min, 30x below measurable creep) takes exact elastic stick below the floor,
#      half-decade smoothstep blend in ln V, theta keeps aging. Cuts the plateau 4x
#      and makes preload steps parent-like. All resolvable creep still flows.
#   2) DECK: nl_abs_tol 1e-6 -> 1e-4 N (the residual floor of edge/transition-band qps
#      sits at ~4e-5 N here; 1e-4 N is ~1.5e-9 of the 70 kN load scale -- inert).
#      If a later stage still floors above 1e-4, raise stick_velocity_floor to
#      3e-11..1e-10 before touching anything else.
# VERIFIED (local, 8 ranks, fixed build): ramp + hold window incl. the previously fatal
# step converge at dt=1.5 under these settings; SW4 sibling deck (56_01) clean through
# t=90 at its own tolerances with the same build.
######################################################################################
######################################################################################
# DECK SW3 v11 BOUNDEDTAIL (from v10-corrected, 2026-07-12, round 12). v10 DIVERGED at
# t~2610-2750 (HPC dt -> 2e-6, q_end -2.9): the fault ran to 97 um with tau -> 0.01 MPa =
# TOTAL STRENGTH COLLAPSE, not an arrest. TWO stacked design flaws (MD s29):
#  (1) UNBOUNDED TAIL: fcs 0.02 R-floor (0.657*0.145*17 ~ 1.7 MPa) MINUS the TS depth 2.5
#      -> net strength clamps at ZERO once s > ~85 um -> frictionless fault -> runaway
#      (the aperture deck-41 lesson, now on the strength side: every weakening stack needs
#      a positive bound the HM feedback cannot pierce).
#  (2) RELAX-TIMING COUPLING: the weaker tail let slip arrive at s=70 um by t~2650 when the
#      t=2400->2900 relax had delivered only ~50% -> driving there was ~5.2 not 2.5 MPa ->
#      blew through the designed arrest and into the zero-strength zone.
# FIXES (three, each closing one hole):
#  TS OFF (dS = 0): the tail bound is back to the R-floor ~1.7-2.0 MPa > 0 ALWAYS.
#  Ld 52 -> 34 um: the tail thinning moves into R itself, which CANNOT undercut the floor:
#      mu(70um) = 0.02 + 1.2513*(0.1+0.54*e^(-70/34)) = 0.239 -> S(70) ~ 0.7*0.239*18 = 3.0.
#      Early slope 1.2513*0.54/34e-6*0.7*26e6 = 3.6e11 = 2.5x k_sys -> a REGULARIZED BURST
#      (v8/v9 already ran at 1.4x under visc 6e12; the data's own slip 0->70 um in ~300 s IS
#      bursty; dtmin 1e-4 + eta guard it).
#  relax_dur 500 -> 250 (t0 2400 kept): full relaxation by t~2650 = when the burst arrives,
#      so the arrest arithmetic uses the FULL-relaxed load line L = 12.45.
# ARREST PREDICTION (factor 0.7, sigma'n 18): S(68) = 0.7*(0.02+1.2513*0.1731)*18 = 2.98 vs
# driving(68) = 12.45 - 142*0.068 = 2.79 -> arrest 68-70 um at tau ~2.9-3.0, tau_end 2.4-2.6
# after unload decay, q_end ~7 (from 16), dn_pk ~ -48, Q_pk ~0.80-0.85 (W/L 0.674 + dilscale
# 0.038 kept). FALSIFIERS: slip < 64 -> Ld 38; slip > 74 or tau_end < 2.2 -> Ld 31; burst
# dt-crash -> visc 8e12 (keep Ld). NB fcs/fcr/W-L/dilscale/RSF/visc all kept from v10-corrected.
######################################################################################
######################################################################################
# DECK SW3 v10 ARREST -- CORRECTED SIZING (2026-07-12 evening). The first-cut v10
# (fcr139/Ld75/TS4e6) was INVALIDATED BY LOCAL RUN before HPC: at t=3078 slip was 6.2 um
# (predicted onset 2410) - the fcr pairing had used the SW-S4 R0=0.45, but SW-S3 runs at
# initial_roughness = 0.64 -> peak mu_nom was 0.02+1.37*0.64 = 0.897 vs v9's 0.821 (+1.5 MPa
# envelope). CORRECTIONS (all re-anchored to R0=0.64 and to v9's own MEASURED arrest):
#   fcr 1.39 -> 1.27  (mu_peak = 0.02 + 1.2513*0.64 = 0.8208 = v9 exactly -> onset ~2412)
#   Ld  75 -> 52 um   (revert: the Ld-75 stability arithmetic also used dR=0.35, but dR=0.54;
#                      v8/v9 ran STABLE at Ld 52 / slope ~1.4x k_sys under visc 6e12 - and the
#                      corrected-v10 local run itself showed dt_min 1.5 through yield)
#   TS dS 4.0e6 -> 2.5e6 (tail re-anchored EMPIRICALLY: v9 arrest factor = 6.12/(mu_nom(51.6)*
#                      sigma'n 19) = 0.657; S(72um) = 0.657*0.3143*18.5 = 3.82; data needs 2.3
#                      -> TS(72) = 1.5 MPa = 2.5e6*(1-e^(-34/36)); slope 6.9e10 = 0.49*k_sys)
# ARREST CHECK (corrected): S(70) = 0.657*0.3207*18.5 - 1.47 = 2.43 vs driving 12.45-142*0.070
# = 2.51 -> arrest 70-72 um at tau ~2.4; mid-branch S(51.6) - TS 0.79 = 4.14 < driving 5.15 (keeps
# sliding through v9's arrest point). Original (mis-sized) header kept below for the record.
######################################################################################
# DECK SW3 v10 ARREST (from v9, 2026-07-12, round 11). v9 RESULT: the LOADRELAX du=16um
# landed the load line ON the data (L_end 12.45 vs data 12.42, k_sys 1.42e11) but the fault
# ARRESTED at (51.6 um, tau 6.12@2900 -> 5.17 end) instead of the data's (72, ~2.5 -> 2.2):
# the RESIDUAL ENVELOPE is ~3 MPa too strong - v8's "slip match" at 79 um was excess load
# (L_end 16.18) pushing through it. Slip drop 79->51.6 = 27.4 um from a 16 um relax =
# amplification 1.71 = k_sys/(k_sys-k_w) -> k_w ~ 5.9e10 (the mu(s) tail slope).
# FIVE sized changes (relax kept EXACTLY as v9):
#  (1) fcs 0.20 -> 0.02 + fcr 1.17 -> 1.39: holds peak mu_nom 0.6365 (onset 2412 preserved)
#      while cutting the tail: mu_nom(72um) 0.382 -> 0.341 (with Ld 75 below). Realized-strength
#      report factor measured from v9's own arrest: 6.12/(0.4234*19) = 0.76.
#  (2) Ld 52 -> 75 um: MANDATORY with the bigger (fcr-fcs): early weakening slope
#      (fcr-fcs)*0.35/Ld*0.76*sigma'n(26) must stay < k_sys: Ld52 -> 1.82e11 = CLIFF;
#      Ld75 -> 1.26e11 = 0.89*k_sys (v8 was 1.29e11 = 0.91*k_sys, stable).
#  (3) TWOSTAGE ON: dS 4.0e6, s* 38 um, w 36 um (peak slope 1.11e11 = 0.78*k_sys, stable).
#      SW-S3's own tail demands it: data strength(72um) = L - k_sys*72um = 2.2-2.5 MPa but the
#      exponential-R floor with ANY fcs >= 0 gives >= 0.76*fcr*0.1*19 = 2.0 + R-tail 1.9 = 3.9.
#      TS(72) = 4.0*(1-e^(-34/36)) = 2.4 MPa bridges exactly the measured deficit.
#  (4) FLOW-PANEL FIX: paper W/L was the SW-S4 value 0.81; SW-S3's inlet-outlet path is 1.202x
#      longer (0.09554 vs 0.07946 m) -> paper_flow_width_over_length_sw_s3 = 0.674. v9's Q_peak
#      1.228 was 46% over data 0.838 PARTLY from this (corrected: 1.022, still +22%).
#  (5) dilation_scale 0.06 -> 0.038 (the queued retune, resized post-ppfix): remaining +22%
#      Q excess needs a_h x0.936; v10 slip grows dilation ~x1.36 -> scale 0.06*0.75/(0.90*1.36).
# ARREST PREDICTION (sigma'n@2900 ~18.5): S(70) = 0.76*0.3455*18.5 - TS(70) 2.36 = 2.50 vs
# driving 12.45-142*0.070 = 2.51 -> arrest 70-72 um, tau@2900 ~2.5, tau_end 2.2-2.4, q_end ~6,
# dn_peak ~ -0.048, Q_peak ~0.85-0.90. FALSIFIERS: slip > 75 -> dS 4.0 too deep, take 3.4;
# slip < 66 -> raise dS to 4.6 (NOT fcs: onset would move); early cliff/dt crash at ~2450 ->
# Ld 75 -> 85.
######################################################################################
######################################################################################
# SW-S3 TRANSFER DECK (v5, 2026-07-09): the FULL calibrated SW-S4 deck-52_12 configuration
# (cohesionless fcr 1.17 + dissipation_margin 0.16 + pcoeff 0.88 + referenced RSF + visc 6e12 +
# power-law-BB aperture closure + smooth gouge + REVcn reconstruction + compliant compensated frame)
# transplanted onto the SW-S3 ROUGH saw-cut geometry/protocol. SAME-GRANITE story: only the
# ROUGHNESS STATE and case geometry/loads change vs SW-S4.
#
# SW-S3 back-analysis (validation/ CSVs, 2026-07-09):
#   q_init 35.0 / tau_init 14.84 / sigma'n_init 32.12 (theta=29deg: tau/q = 0.424 consistent)
#   NO slip until t~2390 (Pi~26!) at mobilized mu = 0.62 -> ONE unstable burst 0->72 um in ~360 s
#   (descent ~1.5e11 Pa/m ~ frame-limited = genuine instability; model regularizes via visc+RSF and
#   will spread it somewhat -- same class as SW-S4's 1650 s event but stronger), immediate re-stick,
#   tau 3.3->2.30 elastic through unload. sigma'n trough 15.42@2639, end 24.72. Slip 73.8 um.
#   k: 0.418e-13 -> 1.23e-13 peak -> 0.757e-13 end (a_h 0.709 -> 1.215 -> 0.953 um).
#   mu(s): 0.62@onset -> ~0.52@20-40um -> 0.29@60 -> 0.23@70: ONE continuous exponential decay ->
#   TWOSTAGE OFF (dS=0). NORMAL-DILATION digitization UNUSABLE (raw -38..-44 mm) -> dn NOT a
#   calibration target here (kept SW-S4 dilation/REVcn settings; re-digitize to activate).
#
# TRANSFER SIZING (first cut -- gate-calibrate axial_pres_final locally before HPC):
#   initial_roughness 0.45 -> 0.64: same asperity endpoints fcr 1.17/fcs 0.0825 (same granite),
#     mu_eff(R=0.64) ~ 0.68 vs data onset 0.62 (+9% side-average margin, the SW-S4 lesson).
#   roughness_decay_distance 115 -> 52 um: R(72)/R(0)=0.37 from the measured mu drop 0.62->0.23.
#     NB onset strength slope ~2.2e11 > k_sys ~1.0-1.2e11 -> the burst is REAL (data shows it);
#     visc 6e12 + RSF are the regularizers; if the run stalls at the event raise visc to 1e13.
#   Preload: sigma1 65 MPa (q=35 @ sigma3 30). Rigid dsig/du = 4.13e11*(100.28/124.4) = 3.33e11
#     -> u_rigid(34 MPa) = 102.1 um; spring 65e6/1.2e12 = 54.2 um -> axial_pres_final ~ -1.563e-4.
#     Same rig -> axial penalty 1.2e12 kept; axial_pres_initial -2.5833e-5 (same -31e6 IC).
#   Aperture: a_h0 0.709 um (k0 0.418e-13); BB power-law rescaled to SW-S3 peak opening +0.51 um:
#     Vm 0.85 -> 1.2 um, Kni -> 1.25e13 (sigma0 = Vm*Kni = 15 MPa held), p=2, ref 32.1e6.
#   Injection: SW-S3 digitized staircase (11 stages Pi 8->28.6->8, ~430 s stages, end 4802 s).
#   OPEN ITEMS: paper flow W/L kept 0.81 (SW-S4 value; SW-S3 peak Q 0.84 ml/min is 7x SW-S4 --
#     if flow panel is systematically off rescale W/L, not the physics); flow_rate_residual_volume
#     PP keeps SW-S4 geometry constants (diagnostic only); gouge/retention kept SW-S4 (dn-coupled,
#     unverifiable until re-digitization).
######################################################################################
######################################################################################
# Ye & Ghassemi (2018) SW-S4 -- DD02 "smooth fracture" replication (cap1e6 slip-cap case)
#
# ====================== V20: MODERATE slip-weakening (mu 0.804 -> ~0.62) ======================
# Forked from v16 (psi37_15, the calibrated dilation case: dn/ds slope -0.563 ~ data -0.55,
# dn_final -0.031 mm ~ data -0.031). v16's ONE remaining gap is the DYNAMIC slip event at ~1650 s:
# the data shows a SHARP, near-stepwise differential-stress / shear-traction drop and a sudden slip
# jump (0.04 -> 0.079 mm); the quasi-static + viscously-regularized model slides through it SMOOTHLY,
# under-shooting slip (0.056 mm) and the dn peak dip (-0.032 vs data -0.041). This deck tests the one
# untested PHYSICAL lever for a sharper drop: SLIP-WEAKENING friction (mu degrades as asperities wear,
# already in the law via the roughness-strength coupling but DISABLED in v16, friction_rough=smooth).
# ONLY friction_rough / friction_smooth / roughness_decay_distance change vs v16 -- the stick-phase
# mu_eff is held at 0.804 (R=initial_roughness=0.45) so the validated Table-2 Coulomb fit is preserved;
# mu weakens only AFTER slip accumulates -> post-peak strength drop becomes self-accelerating (sharper)
# and should recover some of the missing slip. EXPECT: sharper diff-stress/tau drop, more slip (closer
# to 0.079), larger dn (toward the -0.041 peak), and somewhat higher flow/perm (re-tune dilation_scale
# afterward if perm overshoots). Compare the stress-drop SHARPNESS vs v16 and the data.

#
# FAITHFUL orca_3.0 recreation of the Orca_2.0 reference deck
#   Examples/M/CZM/TriAxial/Ye2018/April1st/sensitivity_v8_stage23/inputs/
#       ye2018_smooth_fracture_April1_V8_DD02_cap1e6.i
#
# Unlike the Route-B caseE/caseF decks (which substituted OrcaCZMMohrCoulombFriction as a
# stand-in because the decoupled-dilation-roughness law had not yet been ported), this deck uses
# the ACTUAL decoupled law from the reference:
#   - ADOrcaDecoupledDilationRoughnessContactTraction: penalty contact, roughness-controlled
#     strength evolution (here friction_rough = friction_smooth and cohesion_rough = cohesion_smooth
#     => effectively constant strength, as in the reference), a SEPARATE cumulative-slip dilation
#     decay law, and a max_plastic_slip_increment cap (the "cap1e6" burst stabilizer -- the cap IS
#     the stabilizer for this law; there is no Duvaut-Lions viscosity parameter).
#   - ADOrcaRoughnessDamageFracturePermeability in ROUGHNESS-COUPLED mode (use_kinematic_aperture =
#     false): a_h is built from the mechanical aperture + the law's dilation_jump_increment and
#     roughness_state, with self-propping retention -- exactly the reference wiring.
#
# Pressure -> fault coupling is the MECHANICAL effective-stress route (the reference applied pore
# pressure to the fault as a traction via OrcaFaultPressureInterfaceKernel, coeff 0.935, sign -1).
# The decoupled law has no pore-pressure-in-strength term, so this mechanical route is REQUIRED. The
# orca_3.0 equivalent is OrcaCZMFluidPressureInterfaceKernel with pressure_traction_coefficient =
# -fault_pressure_coefficient (pushes faces apart -> reduces contact normal stress -> Coulomb
# strength falls through the mechanics = true poroelastic effective stress).
#
# Mesh/scaffold = the Orca_2.0 reference SW-S4 mesh (mesh/ye2018_sw_s4_low_mesh.e): a PRE-TAGGED
# mesh that already carries the top/bottom/sides surfaces and the no_disp_x/no_disp_y pins. The
# injection/production source nodes (source_in/source_out) are added here and the conforming fault is
# split into the CZM interface 'fracture_interface' via OrcaFaultInterface3DGenerator -- the exact
# reference wiring (no geometric rebuild of boundaries/pins, no damage zone, no near-injection patch).
#
# DILATION RETUNE (forked from kernels_update_new_mesh.i): dilation_scale raised from 5.0e-4 to 0.4.
# Quantified gap: integrating this law's own dilation angle (1.5 deg -> 0.3 deg, decay distance 1e-4 m,
# exponent 0.5) out to the paper's peak SW-S4 shear slip (~0.075 mm) gives cumulative_dilation ~= 1.3
# micron. With dilation_scale=5e-4 and retention_factor ~0.6-0.7, that contributes ~1e-10 m to a_h --
# negligible vs. the ~0.33 micron of aperture growth needed to reproduce the paper's ~2x permeability
# rise (a_h: 0.74 -> ~1.07 micron). Solving dilation_scale*1.3e-6*0.65 ~= 0.33e-6 gives dilation_scale
# ~= 0.39; rounded to 0.4 as the starting point for calibration. aperture_scale is left untouched:
# mechanical_aperture stays clamped at 0 throughout (the fault never goes into net elastic tension in
# this confined test), so that term does not contribute regardless of its scale.
#
# FRICTION/COHESION RECALIBRATION (post sideset-area fix): after correcting the fracture_interface
# area bug, the stick-phase sigma'_n/tau matched paper Table 2 closely, but the slip stage was still
# ~28x too small in shear slip and ~37x too small in normal dilation, with onset delayed to Pi~21 MPa
# vs. the paper's stated >16 MPa threshold for SW-S4. The fix is NOT a structural bug -- it is that
# friction_coefficient=0.57/cohesion=1.5e6 (carried over from the rough-fracture DD02 reference) do not
# match this sample. The paper's OWN SW-S4 Table 2 data are internally consistent with a SINGLE linear
# Coulomb envelope tau = cohesion + mu*sigma'_n holding almost exactly (R^2 ~= 1, residuals < 0.1 MPa)
# at every loading-segment hold stage where ds>0 (Pi = 16, 20, 24, 28 MPa: sigma'_n/tau pairs (26.51,
# 12.14), (22.92,9.38), (19.25,6.48), (15.31,3.12)) -- i.e., the paper's own data show SW-S4 sitting
# essentially ON its Coulomb limit throughout the reported slip stage (gradual slip tracking Pi, not a
# sudden dynamic burst -- per Sec. 3, SW-S4's slip "occurred gradually", unlike the rough-fracture
# samples' "rapid slip ... in a short time"). A least-squares fit through those 4 points gives
# mu = 0.804, cohesion = -9.11 MPa (an effective negative intercept, not a literal physical cohesion --
# this Coulomb law has no normal-stress-dependent friction term, so a negative intercept is the best
# linear approximation of what is likely a curved Barton-Bandis envelope over this sigma'_n range).
# Cross-check: the SAME fit predicts a positive (stable) strength margin at Pi=8,12 MPa (3.06, 1.47 MPa)
# where the paper reports ds=0, and a large positive margin throughout the entire unloading segment
# (1.85-8.58 MPa), matching the paper's statement of no further shearing during unloading. Replaces
# friction_coefficient_rough/smooth 0.57->0.804 and cohesion_rough/smooth 1.5e6->-9.11e6.
# CAVEAT carried forward: even with the slip magnitude corrected, paper's measured normal dilation
# (dn=0.041 mm at peak) implies an average dilation angle of atan(0.041/0.075)~=28.6 deg from peak ds --
# implausibly large for an "ideally smooth, polished saw-cut" fracture (the paper's own characterization
# of SW-S4). This suggests the paper's LVDT-measured dn likely captures broader sample/assembly
# deformation beyond the fault's local geometric dilatancy, not purely the CZM-resolvable opening, so dn
# may remain a smaller, model-intrinsic quantity than the paper's reported value even after this fix.
#
# V5 PAPER-FLOW DIAGNOSTIC FIX: the prior "validation" flow postprocessor used the Orca_2.0
# reference-area form Q = k * A/(mu*L) * dP. Ye et al. Table 2 reports flow inferred from their
# cubic-law Eq. 9, Q = (W/L) * a_h^3/(12*mu) * dP. This deck keeps the nonlinear physics unchanged
# and corrects only the paper-facing Q postprocessor. The old formula is retained under
# flow_rate_reference_area_ml_min_pp so the previous diagnostic remains auditable.
#
# V10 STABLE STRESS-CLOSURE APERTURE LAW: SW-S4 is the polished saw-cut case, and the paper reports only
# minor permeability retention after unloading. The v5 material made a_h mostly a retained cumulative
# dilation state, so k plateaued after peak pressure. This deck enables the new opt-in normal-stress
# aperture term in ADOrcaRoughnessDamageFracturePermeability and a small shear-damage/gouge-fill term:
#     a_h = a_h0 + Cn*(sigma_n_ref - sigma'_n) + retained_dilation - gouge_fill
#     k   = a_h^2 / 12
#     Q   = (W/L)*a_h^3*dP/(12*mu)
# The chosen Cn/gouge values were fit against the v5 hold-stage sigma'_n, cumulative slip, and Ye2018
# Table 2 SW-S4 hydraulic aperture trend. Treat this as the next calibration candidate, not a universal
# fracture law.
#
# Compared with v6, the reversible normal-stress compliance and gouge-fill scale are reduced to avoid
# over-conductive pressure diffusion and the resulting early effective-normal-stress collapse.
#
# V14 keeps the V13 paper-aperture model but uses the project's slip-burst mitigation settings:
#   - tangential_viscosity = 1e11 Pa.s/m, within the documented 1e10/1e11/1e12 sweep range for
#     pressure-driven stick-slip bursts;
#   - dtmin = 1e-6 s, matching the older SW4 burst-crawl decks. v12/v13 both failed after the
#     timestepper reached the 0.01 s floor while state variables were still smooth.
# This is a numerical continuation deck, not a new calibration target until the full run is checked.
#
# ============================== V15: KINEMATIC DILATION (opens_joint) ==============================
# Supersedes the V14 caveat that the paper's dn=-41 um is an unrecoverable measurement artifact.
# Root cause (source + unit test): the decoupled law applied dilation as a TENSILE increment to the
# normal traction (dilatant SOFTENING) -> as the joint dilates it RELIEVES normal compression, so the
# kinematic normal jump (dn=czm_dn) CLOSES and sigma'_n collapses. That is backwards from a physical
# dilatant joint, where dilation rides asperities apart and the joint OPENS (dilatant HARDENING).
#
# New opt-in flag dilation_opens_joint=true (default false == V14) flips the dilation sign in the
# normal-traction update AND the return-map denominator consistently. Verified on a 2-block direct-
# shear unit test (directshear_dilation_opens_joint_unit_test.i):
#   opens_joint=FALSE: slip grows -> sigma_n COLLAPSES (-8 -> 0 MPa), dn CLOSES (-0.5 -> -14 um)
#   opens_joint=TRUE : slip grows -> sigma_n STAYS -8 MPa,            dn OPENS  (-0.5 -> +4.8 um)
# Data decomposition: SW-S4 dn is ~100% shear-dilation, apparent d(open)/d(slip) ~ 0.55 -> psi ~29 deg.
#
# THREE coupled changes from V14 (all else identical); ALL are physically-motivated STARTING values
# that must be re-calibrated once the full run is scored vs Fig.7d / Table 2:
#   1. dilation_opens_joint = true                              (the fix)
#   2. dilation_angle_peak/residual 1.5/0.3 -> 25/10 deg        -> tune to the dn/ds ~0.55 slope
#   3. dilation_scale 0.4 -> 0.013 (perm law)                   -> angle ~17x larger grows the
#      cumulative_dilation feeding a_h ~17x, so dilation_scale is cut ~17x to hold a_h (hence
#      permeability) at the V14 fit. This makes the hydraulic-vs-mechanical aperture DECOUPLING
#      explicit: MECHANICAL aperture (dn) opens ~tens of um (matches paper) while HYDRAULIC aperture
#      stays sub-um (sub-linear). Re-tune dilation_scale to the perm curve.
# HONEST EXPECTATION: dn flips to OPENING and tracks slip at ~tan(psi); absolute magnitude is gated by
# ds, itself ~0.6x the paper because the dynamic slip burst (~1700 s) is a quasi-static limitation.
# sigma'_n / tau preserved (far-field-governed); perm preserved by the dilation_scale rebalance.
######################################################################################
# ============================== BATCH 4 (cases 18-20): COMPLIANT FRAME, DONE RIGHT ==============================
# Batch-3 post-mortem (measured from the 13/14/15 CSVs):
#   1. PRELOAD LOST. FunctionPenaltyDirichletBC was swapped in while keeping the rigid-BC ramp
#      (-4.6e-5 m). A penalty spring transmits traction = penalty*(u_prescribed - u), so holding the
#      53.4 MPa post-ramp axial stress at penalty=1e11 needs ~534 um of extra prescribed displacement.
#      Result: the sample dumped its preload into the spring -- stress_zz_top relaxed -31 -> -18 MPa,
#      differential stress went NEGATIVE (-12 MPa), sigma'_n fell 31 -> 22 MPa, tau0 fell 11.3 -> 3.7 MPa.
#      Everything downstream (early slip, 4x flow, low perm-match, tiny shear traction) followed.
#      FIX: compensated ramp  u_pres(t) = u_rigid(t) - sigma_zz_top(t)/penalty  (piecewise linear:
#      -sigma0/penalty before the ramp, u_rigid_end - sigma_end/penalty after; sigma0=31 MPa from the
#      isotropic initial stress, sigma_end measured = 53.42 MPa in case 05). t=0 is then in exact
#      equilibrium (also removes the t~2.4 s crash of case 13).
#   2. PENALTY ARITHMETIC. Batch 3 set penalty ~ k_exp = 1.25e11 Pa/m. But k_exp is the WHOLE system
#      stiffness in (tau, slip) space; the spring is in SERIES with the rock column AND projects through
#      the fault geometry. Measured from the runs: rigid model dtau/dslip = 1.50e11 (05, 05_01);
#      compliant runs give the projection factor f = k_tau_slip/(axial penalty) ~ 0.62 (14: 4.44e10 @1e11;
#      15: 2.50e10 @5e10, both series-consistent). Matching k_exp:
#        1/1.25e11 = 1/1.50e11 + 1/(0.62*penalty)  =>  penalty ~ 1.2e12 Pa/m  (x A_top=2.0e-3 m^2
#      => k_machine ~ 2.4 GN/m, a plausible servo-frame value). Batch 3's 1e11 was ~12x too soft.
#   3. FRICTION FLOOR. mu_eff = fcs + (fcr-fcs)*R with R floored at residual_roughness=0.10, so
#      fcr=0.8/fcs=0.20 can never weaken below mu=0.26 (and only reaches ~0.31 within 75 um at
#      Ld=5e-5), while Table 2 shows mu -> 0.20 during slip. Two-point solve (mu_onset=0.447 at
#      R~0.42, mu_res=0.20 at R=0.10): fcr=0.89, fcs=0.123. Stability (weakening slope < k_sys)
#      then requires Ld >= 6e-5.
# Quasi-static slip-balance predictions (tau unloading line vs mu(s)*sigma'_n at the injection peak):
#   18: ~53 um   19: ~58 um   20: ~72-75 um   (data: 75-79 um; 05 rigid gave 45 um)
# Case 20 additionally (a) scales the preload x1.11 so the stuck-phase tau plateau hits the data's
# 12.5 MPa (model 05 sat at 11.3 -- an onset deficit worth ~10 um of slip), and (b) softens the frame
# to k_sys ~ 1.07e11 as a quasi-static stand-in for the dynamic 1650-1700 s slip burst, which a
# quasi-static solver cannot overshoot (it parks on the stable equilibrium branch).
######################################################################################

# --- mesh / geometry ---
mesh_file = mesh/sw3_mesh_L123p4_size5.e  # SW-S3 rough saw-cut (theta=29.000deg, D=50.53mm, L=123.40mm), pre-tagged scaffold
                                     # L123p4 2026-08-16: rebuilt from mesh/sw3_mesh_L123p4.jou. The old
                                     # sw3_mesh_size5.e is L=124.40 mm, 1.00 mm (0.8%) longer than Table 1.
                                     # It is KEPT in mesh/ because the 83/84/86-series decks were gated on
                                     # it. Verified with scripts/check_mesh_geometry.py: L 123.40, D 50.53,
                                     # theta 29.000. Node/interface counts are unchanged (11425/457), so
                                     # this is a pure axial rescaling of the same discretisation.
sample_radius = 0.025265             # m, SW-S4 radius (D = 50.51 mm); cylinder radius used by the confining BC
sample_area = 2.0053421295e-3        # m2, pi*sample_radius^2; nominal area used for applied reaction stress
bulk_sin_theta = 0.4848096202463371          # 93-series: sin(29.0 deg), THIS specimen's fracture angle.
bulk_cos_theta = 0.8746197071393957   # 93-series: cos(29.0 deg). Used only by the bulk_* diagnostics.
axial_bc_penalty = 1.0e13          # SW3-v8 (STIFFFRAME2): 2.4e12 -> 1.0e13. MEASURED from the v6/v7 pair
                                   # (burst dtau/ds = 1.079e11 @1.2e12 and 1.248e11 @2.4e12): series model
                                   # 1/k_sys = 1/k_rock + 1/(f*axp) solves to f = 0.334, k_rock = 1.478e11
                                   # Pa/m -- i.e. k_sys SATURATES at 1.48e11 even rigid (data wants 1.51e11,
                                   # right at the ceiling). axp 1e13 -> k_sys ~ 1.42e11; slip = dtau_burst/
                                   # k_sys ~ 10.3e6/1.415e11 ~ 73 um (+ arrest creep) vs data 71-73.
                                   # effective system than SW-S4: burst dtau/dslip = 10.7 MPa/71 um = 1.51e11
                                   # Pa/m (SW-S4: 1.25e11). Series estimate with k_rigid ~1.5e11 (tau-slip) and
                                   # f~0.62: penalty 2.4e12 -> k_sys ~1.36e11 -> burst slip (14.8-3.55)/1.36e11
                                   # ~ 82 um (v6 predicts ~90 at 1.25e11; data 71). NB k_rigid/f are SW-S4-mesh
                                   # measurements -- treat v7 as the stiffness AXIS of the sweep, v6 as control.
                                   # COMPENSATION RE-DERIVED for the new penalty (below) -- a penalty change
                                   # without it re-breaks the preload (batch-3 bug).
axial_pres_initial = -3.1e-6          # SW3-v8: = -sigma_zz0/penalty = -31e6/1.0e13 (spring pre-compressed so t=0 equilibrium)
axial_pres_final   = -6.41358437936e-5 # E=75 GPa; preserves the 31 MPa preload through the axial rock/penalty series
# relax_t0 removed in DECK59_07: no post-preload actuator retreat.
                                  # servo retreats DURING the burst tail, not after); 2550 starts just after the
                                  # predicted onset 2420-2520 so the burst is never starved pre-onset (the 59_01
                                  # death) yet the tail is caught and arrested at ~72-75 um. Full delivery by 2950.
# relax_dur removed in DECK59_07: no post-preload actuator retreat.
                                  # when the 500-s ramp had delivered only ~50% (driving 5.2 not 2.5 MPa) -> blew
                                  # through the arrest. Full relaxation by ~2650 = burst arrival; arrest math then
                                  # uses the full-relaxed L = 12.45. (t0 2400 kept = onset, per v9.)
# axial_relax_du removed in DECK59_07: constant actuator command after preload.
                                  # = -4.35 MPa for 16 um (-0.272 MPa/um); data wants L_end 12.78, i.e. ~ -3.7 MPa
                                  # -> du ~ 13.3-14.0. (59_01 note kept:) 0 -> 16um RESTORED (v9-v12 value). v19 disabled LOADRELAX
                                  # betting flow-form creep would relax the drive; v20/v21 FULL RUNS refute it:
                                  # L_end = tau_end + k*s_end = 16.9 MPa vs data 12.78 -> the whole +24-30 um
                                  # over-slip is this load-line error (103 um realized; 103 - 4.45/0.142 ~ 72 =
                                  # data 73.7). Fault creep cannot retreat the piston; the servo relax is physical.
                                  # tau/q = 0.424). SIZED FROM v8 LOAD LINE: L_end = tau_end + 1.42e11*s_end = 16.18 vs
                                  # data 12.77 (+3.4); q_end 12.7 vs data 5.4 (+7.3). Same structure as SW-S4 but 3x
                                  # larger: SW3's injection phase is 2.4x longer, so the un-relaxed drive accumulates more.

                                   # gate q 37.4/37.8 vs data 35.0: the -65 MPa szz target assumed sigma3_bulk
                                   # = 30, but the run gives sigma3_bulk ~ 27.0 -> target szz = 27 + 35 = -62.
                                   # Rock-column slope k_rock,axial = 4.78e11 (v5); series slope at 1e13 =
                                   # 1/(1/4.78e11 + 1/1e13) = 4.562e11 -> u_final = -31e6/1e13 - 31e6/4.562e11
                                   # = -7.105e-5 m. Predicted gate: szz -62, q ~35, tau ~15.0, sigma'n ~33.2
                                   # (= data init 33.2). GATE-VERIFY t=0-120 locally before HPC (done).
                                 # 1/3.42e11 = 1/k_rock + 1/1.2e12 -> k_rock = 4.78e11; at 2.4e12 the series
                                 # slope = 1/(1/4.78e11 + 1/2.4e12) = 3.99e11 Pa/m -> u(-65 MPa) = 1.2917e-5
                                 # + 34e6/3.99e11 = 9.81e-5. GATE-VERIFY t~120 (sigma_zz -65 / q 35 / tau 14.8)
                                 # BEFORE the full run -- the trim is first-order, expect ~2% correction.
                                 # (v6 GATEFIX note: -1.563e-4 -> -1.253e-4. The v5 "first cut" was NEVER
                                 # gate-calibrated (banner said to): measured sigma_zz_top(t=100) = -75.6 MPa
                                 # vs the -65 target -> q_init 48.8 / tau_init 20.85 vs data 35 / 14.7. That
                                 # single overshoot cascaded into EVERYTHING v5 got wrong: +6.1 MPa of stored
                                 # driving tau -> burst stress drop 21.2 (data 10.7) -> slip 186 um (data 71)
                                 # -> dn -82 (data -44) -> q_end NEGATIVE (-4.9). Slope measured FROM THE v5
                                 # RUN itself: (75.6-31)e6/(1.563e-4 - 2.5833e-5) = 3.42e11 Pa/m ->
                                 # u(sigma_zz=-65) = 2.5833e-5 + 34e6/3.42e11 = 1.253e-4. Predicted gate:
                                 # sigma_zz_top -65, q ~35, tau ~14.8, sigma'n ~32. VERIFY the gate at t~120
                                 # before the full run.         # DECK46 (Q-FIX) -9.4e-5->-9.84e-5: +1.8 MPa axial sig1 (dsig/du=4.13e11,
                                     # du=-4.36e-6). Raises q with the confining cut above at fixed sigma'n. WAS DECK35 (RESIDtune): -9.6e-5 -> -9.4e-5. Small trim to offset the ~+4um slip that the shorter Ld adds (holds slip ~77-79). dσ/du=4.13e11 -> ~0.83 MPa less axial. fcs and Ld drive the residual drop; this only protects the slip match.

# --- mechanics (OrcaMechMaterial) : DD02 reference values ---
youngs_modulus = 67e9
poissons_ratio = 0.32
strain_model = incremental
initial_stress = '-31e6 -31e6 -31e6'
biot_coefficient = 0.6

# --- matrix HM ---
initial_porosity = 0.001
matrix_permeability = 5e-19          # m^2, intact granite matrix permeability

# --- loading ---
confining_pressure = 30e6            # SW-S3: paper sigma3 (the SW-S4 Q-FIX -0.6 was case-specific)
                                     # below to RAISE the differential stress q=sig1-sig3 at ~FIXED sigma'n.
                                     # Goal: model initial tau=11.46/q_fault=26.9 -> data tau=12.56/diff=29.2
                                     # (SAME theta=29.2deg, so q and tau move together). d(sigma'n)=cos^2*dsig3
                                     # +sin^2*dsig1 = 0.762*(-0.6)+0.238*(+1.8) ~= 0 -> sigma'n held ~31.
                                     # dq~+2.4 -> tau~+1.0 -> ~12.5. CAVEAT: higher tau drives the fault HARDER
                                     # -> earlier yield / more slip -> RE-VERIFY the preload gate (sigma'n~31,
                                     # q~29) and expect to re-trim Ld/load to hold slip 75-79um. This is the
                                     # HONEST fix for the low initial shear (vs deck45's empirical pcoeff).
production_pressure = 5e6            # Pa
fault_pressure_coefficient = 0.87 # fixed direct common control from completed 72_93
                                     # 14.5-14.9 through t=1750-1850 vs data ~15.3 -- exactly the window where
                                     # ALL the excess slip accrues (model tracks data's ds to +-3um until the
                                     # trough t~1788, then data RE-STICKS at 75-76um while model creeps to 86.6).
                                     # -0.02 pcoeff = +0.5 MPa sigma'n at peak injection -> strength in the
                                     # re-stick window +0.15-0.2 -> slip -2-3um; trough -> ~15.0 (data 15.28).
                                     # Caveat (disclosed): empirical lever, Biot for an open fracture ~1.
                                     # WAS DECK45 (OPT-c) 0.935->0.90: SEPARATE sigma'n lever from the closure.
                                     # Reduces the pore-pressure traction resolved on the fault -> raises
                                     # sigma'n (deck43 peak 12.9 vs data 15.3) WITHOUT changing aperture/perm.
                                     # CAVEAT: sigma'n also drives Coulomb strength (mu*sigma'n), so higher
                                     # sigma'n RAISES strength -> may delay onset / reduce slip -> re-check
                                     # tau/slip. Modest 0.035 cut as a probe; full sigma'n fix would need ~0.09.

# --- ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile (CZM law) : DD02 reference ---
#
# NOTE (differences vs the old-law v20 deck):
#   1. cohesion_rough/smooth = -9.11e6 (the original v20 calibration) is RESTORED. The revised law now
#      treats cohesion_* as the frictional Coulomb intercept (allows a negative value) and floors the
#      shear strength at 0 internally, exactly like the old law. This is what lets the joint slip at
#      the observed onset (peak strength ~ -9.11 + 1.09*sigma_n) and weaken to the ~2 MPa residual.
#   2. dilation_decay_exponent: old 0.5 is disallowed (singular slope at zero slip); set to 1.0. This
#      is a minor change to the dilation-angle decay SHAPE with slip; retune dilation_decay_distance
#      if the normal-dilation slope needs adjusting.
#   3. max_plastic_slip_increment: increment caps are incompatible with the on-yield return map; set
#      to 0 and rely on event-aware substepping + tangential_viscosity (already 1e11) instead.
penalty_tangent = 1e13
initial_roughness = 0.64             # SW-S3 ROUGH saw-cut (see banner; SW-S4 = 0.45)
residual_roughness = 0.10
# UNUSED after PST swap: roughness_decay_distance = 3.0e-5    # SW3-v11: 52 -> 34 um. The tail thinning moves from the (runaway-capable)
                                     # TWOSTAGE into R itself: mu floors at 0.02+1.2513*0.1 = 0.145 > 0 ALWAYS.
                                     # mu(70) = 0.239 -> S(70) ~ 3.0 = the data arrest strength. Early slope
                                     # 3.6e11 = 2.5x k_sys -> regularized burst (visc 6e12 + dtmin guard; v8/v9
                                     # already ran supercritical at 1.4x; the data slip 0->70um/~300s IS a burst).
                                     # (~ -1.7um; predicted final slip 76.6 + 5-7 (TS) - 1.7 ~ 80-82 vs data
                                     # 79.1). dq/dt cost ~ -2.34 -> ~-2.45 (data -1.78) -- acceptable, the
                                     # tau(s) reshape below dominates the late panels. WAS DECK52_01: 95->100um (slip trim half of the fcs give-back). WAS DECK50: 80->95um. TWO targets: (a) deck46 over-slips (89.6 vs data 79.1um;
                                     # campaign dslip/dLd ~ -0.4um/um -> -6um) and (b) the post-onset weakening
                                     # slope is ~2x too steep (dq/dt 1100-1500 = -3.4 vs data -1.8 MPa/100s;
                                     # deck27 showed Ld 70->120 flattens tau@1300 5.8->8.5). Longer Ld also
                                     # raises resid tau ~ +0.3 (deck46 1.98 vs data 2.20 -> lands ~2.3).   # DECK35 (RESIDtune): 90->80um. Shorter Ld -> weakening reaches residual at LESS slip -> DEEPER & sharper post-peak drop (targets the too-gradual differential-stress/shear decline). Ld trend: 120->4.4 resid/62 slip, 90->3.4/75.6; 80 -> ~3.0 resid tau, +~4um slip. Paired with the load trim below to hold slip in band. (Single Ld still can't make the ~1600 s near-vertical cliff -- that's the dynamic event; two-stage weakening in deck 36 targets it.)
# UNUSED after PST swap: friction_coefficient_rough = 1.27    # SW3-v10 CORRECTED: 1.17 -> 1.27 (NOT 1.39: that sizing used the SW-S4
                                     # R0=0.45; SW-S3 initial_roughness = 0.64). Peak envelope preserved exactly:
                                     # mu_nom(0.64) = 0.02 + 1.2513*0.64 = 0.8208 = v9's 0.20+0.97*0.64 -> onset ~2412
                                     # (realized 0.657-0.76 factor x sigma'n, = data 0.62). All the cut lands in the
                                     # tail where R -> 0.1: mu_floor 0.02+1.25*0.1 = 0.145 (v9: 0.297).
                                     # WAS DECK52_09: 1.15 -> 1.17. 52_08 MEASURED onset 952 s (data ~1000;
                                     # 52_07 with cohR18.5e6 got 1018) -> the original sizing arithmetic said
                                     # 1.17 and the run confirms 1.15 was ~0.2 MPa light: +0.02 fcr = +0.20 MPa
                                     # onset envelope (0.862 report factor x R 0.446 x sn 25.5) = +60-70 s ->
                                     # onset ~1015. Lock cost +0.06 MPa (absorbed in the TS retune below).
                                     # WAS DECK52_08 (COHESIONLESS): 0.89 -> 1.15. The onset strength that
                                     # cohesion_rough carried is moved into roughness FRICTION so the sawcut
                                     # fault is cohesion-free (physically consistent: a sawcut has no cementation;
                                     # fcr is the ASPERITY-SCALE friction endpoint at R=1, tan(49deg) -- never
                                     # realized; realized onset mu_eff ~0.50 vs Table-2's own cohesionless onset
                                     # ratio tau/sigma'n = 12.14/26.51 = 0.458, ~9% margin for progressive edge
                                     # yield + viscous regularization). Sizing from 52_04 CSV at t=1000: envelope
                                     # 12.35 = friction 10.01 (mu_eff 0.392) + cohesion 2.34; 52_07-equivalent
                                     # envelope 12.72 -> mu_eff needed 0.498 -> fcr = 0.0825+(0.498-0.0825)/0.383
                                     # ~ 1.17; set 1.15 since the cohesionless form also weakens SLOWER early
                                     # (strength slope prop. to R not R^2: 7.4e10 vs 10.9e10 Pa/m -> more stable,
                                     # later 2um crossing). Expected side-effects vs 52_07: mid-slope ~-0.5..-0.8
                                     # MPa (slip +3-5um risk; trim = Ld 120->115), lock strength ~-0.5 MPa
                                     # (tau_end ~2.4 with the same TWOSTAGE dS=1e6).   # WAS BATCH4: mu endpoints recalibrated to Table 2 (onset 0.447, residual 0.20)
# UNUSED after PST swap: friction_coefficient_smooth = 0.02   # SW3-v10: 0.20 -> 0.02. v9 EXPOSED the v6 sizing: with the load line correct
                                     # (L_end 12.45 = data 12.42) the fault arrests at 51.6 um / 6.12 MPa - the
                                     # "arrest ratio 0.233" that pinned fcs 0.20 was v5's DRIVING ratio (excess load),
                                     # not strength. Data strength at (72um, sigma'n 18.5-19) = 2.2-2.5 MPa -> mu 0.12:
                                     # even fcs=0 leaves mu_floor = fcr*0.1 = 0.139 -> the last ~2.4 MPa comes from the
                                     # TWOSTAGE tail below. fcs 0.02 keeps the smooth-branch conditioning nonzero.
                                     # WAS SW3-v6: 0.0825 (SW-S4 transfer) -> 0.20. SW-S3's own data pins the
                                     # residual SLIDING friction: at the burst arrest (Pi=28 hold) tau/sigma'n
                                     # = 3.55/15.25 = 0.233; minus the RSF/viscous rate share ~0.03 -> fcs
                                     # ~0.20. The SW-S4 0.0825 let v5 weaken ~2.2 MPa too deep (+~18 um slip)
                                     # and unload to tau ~0. The unloading branch ratios (0.185 -> 0.093) are
                                     # RE-STICK elastic, NOT friction -- do not fit fcs to them (SW-S4 lesson).
                                     # WAS DECK52_01 (SWEEP B, middle of the slip<->resid tradeoff): 0.095->0.085
                                     # (resid ~2.7, slip +2) paired with Ld 95->100 below (slip -2, resid +0.35):
                                     # net (slip ~84, resid ~2.9) vs deck52's (88, 2.5). Brackets the reachable
                                     # front so the paper point can be picked from data. WAS DECK50: # DECK50: 0.085->0.095. Slip trim #2 (with Ld): raising the residual
                                     # strength shrinks the peak->residual stress drop -> dslip = -dtau_res/k_sys
                                     # ~ -0.27e6/1.25e11 ~ -2um; resid tau +~0.27 (0.4 MPa per 0.015 fcs).
                                     # Slip budget: 89.6 (deck46) -6 (Ld) -2 (fcs) ~ 81-82um; resid tau ~2.2-2.3.   # DECK35 (RESIDtune): 0.115->0.085. PRIMARY residual lever for the Fig-7d gaps (differential stress, shear traction, sigma'n all stay too HIGH after ~1600 s because the fault LOCKS at too high a strength). Empirically ~0.4 MPa resid tau per 0.015 fcs (deck29/32) -> 0.030 cut targets resid tau 3.4->~2.6. Lowers residual shear -> less locked-in q -> sigma'n recovers less high. Does NOT add slip (independent of the slip<->resid tension).
# UNUSED after PST swap: friction_roughness_exponent = 1.0
# UNUSED after PST swap: cohesion_rough = 0                       # DECK52_08 (COHESIONLESS): 18.5e6 -> 0. Sawcut fracture carries NO
                                     # cohesion; the onset envelope is supplied entirely by friction_
                                     # coefficient_rough = 1.15 above (see sizing there). This also removes
                                     # the residual c_eff(R=0.283) = 1.48 MPa that the TWOSTAGE dS had to eat.
                                     # initial tau (12.32 vs 11.46) met the UNCHANGED strength envelope ~255s
                                     # early (onset 984->729 s; data ~1000). Deck-25 calibration: c_eff at peak
                                     # = c_R*R^2 = c_R*0.2025; 6.5e6 bought +1.33 MPa peak strength = +267 s.
                                     # Need ~+1.0 MPa to re-balance the added driving tau: dc_R = 1.0e6/0.2025
                                     # ~ 5e6 -> 16e6. Residual unchanged: c_eff(R=0.10) = 16e6*0.01 = 0.16 MPa.                    # DECK28: 6.5->11MPa. The higher load (deck26) pulled onset back to 720s; more cohesion raises the peak strength envelope so the fault holds against the higher applied tau until ~950s. c_eff(R=0.45,exp2)=11e6*0.2025=2.23 MPa at peak; c_eff(R=0.10)=11e6*0.01=0.11 MPa at residual (still negligible -> residual tau preserved).
# UNUSED after PST swap: cohesion_smooth = 0                      # keep 0 so cohesion fully decays out by residual roughness (preserves the calibrated residual tau ~2.75).
# UNUSED after PST swap: cohesion_roughness_exponent = 2.0        # DECK25: 1->2 so cohesion decays FASTER with roughness -> big at peak (R^2=0.20), negligible at residual (R^2=0.01).

# --- DECK52_07 (LOCKFIX) new knobs vs 52_04 ---------------------------------------------------
# UNUSED after PST swap: dissipation_margin = 0.02            # SW3-v6: 0.16 (SW-S4 RESTICK value) -> 0.02. SW-S3 is the ROUGH surface:
                                     # data dn/ds = 44/71 = 0.62 -- at the limiter ceiling the plastic share
                                     # dn_pl <= (1-eps_D)*integral(tau/sigma'n)ds ~ 0.40*slip even at eps_D=0
                                     # (mu_mob falls 0.62->0.23 through the burst). So for SW3 the limiter BINDS
                                     # and every % of eps_D costs dilation the data needs: 0.02 keeps ~98% of
                                     # the admissible budget -> dn_pl ~ -30 um + rev ~ -5 -> peak ~ -35 um vs
                                     # data -44. The remaining ~9 um is STRUCTURAL for this law (energy-limited
                                     # dilation; the BB companion law with live angles owns it) -- see the SW3
                                     # back-analysis MD. WAS DECK52_11 (RESTICK): 0.10->0.16 (SW-S4).
                                     # data -0.0409 at over-slip 86.6 -- ~7% less plastic dn/ds lands the peak
                                     # once slip lands; (b) less kinematic opening relieves less sigma'n ->
                                     # trough up ~+0.1-0.2 (adds to the pcoeff move). NB both dilation measures
                                     # (czm_dn actual jump AND czm_dn_total reconstruction) converge to data
                                     # once slip ~79-80: plastic ~0.029 + rev 0.0116(pk)/0.0035(end).
                                     # WAS DECK52_07: ~0 -> 0.10. The dilation dissipation limiter caps plastic
                                     # opening work at (1-eps_D)*friction work; eps_D=0.10 cuts the realized
                                     # plastic dn/ds ~10% (52_04 plastic dn 33.1um at 78.5um slip; data implies
                                     # ~29-30um). Also raises sigma'n trough toward data (14.65 -> ~15.0-15.2;
                                     # data 15.28) since less kinematic opening relieves less normal stress.
                                     # The dn-peak loss is bought back with REVcn 5->7e-13 (elastic share).
# UNUSED after PST swap: secondary_weakening_strength = 4.0e6   # SW3-v10: ON (was OFF). The v9 arrest measurement is the direct evidence a
                                       # single exponential R-decay CANNOT reach the data's tail: strength(72um)
                                       # needed = L - k_sys*s = 2.2-2.5 MPa; the R-floor alone gives ~3.9-4.7.
                                       # dS*(1-e^(-(72-38)/36)) = 4.0*0.611 = 2.44 MPa = the measured deficit.
                                       # (onset 999, tau@2000 2.91, tau_end 2.235 vs data 1000/3.0/2.20) but
                                       # over-slipped 88.8 vs 79.1um. Slip balance (peak_env - lock)/k_sys:
                                       # 52_09 (12.92-2.79)/1.25e11 = 81um + ~8um BURST overshoot (slip surged
                                       # 64.7->81.2um in t=1700-1800 while the TS slope sat at 1.00x k_sys).
                                       # dS 1.35 raises the lock strength to mu(R80)*sn - TS80 = 0.292*14.8-1.21
                                       # = 3.11 MPa = data's 3.12 -> balance slip 78um.
# UNUSED after PST swap: secondary_weakening_onset_slip = 38e-6 # SW3-v10: 48 -> 38 um. Engage in v9's late slip phase (s>38um is t>2650)
                                       # so the matched onset/mid-path (to ~45um) is untouched but the tail is cut
                                       # well before the v9 arrest at 51.6 um (TS(51.6) = 1.24 MPa un-sticks it).
# UNUSED after PST swap: secondary_weakening_distance = 36e-6   # SW3-v10: 14 -> 36 um. Peak TS slope dS/w = 4.0e6/36e-6 = 1.11e11
                                       # = 0.78x k_sys(SW3 1.42e11) - same stability margin as the calibrated
                                       # SW-S4 52_10 (0.77x its k_sys). WAS DECK52_10: 12->14um for k_sys 1.25e11.
                                       # (was 1.00x -> mini-burst). Tames the 1700-1800 surge; with the burst
                                       # gone the ~8um overshoot should shrink to +2-4 -> final slip ~80-82.
                                       # Viscosity kept at 1e13 ON PURPOSE: eta resists the burst, so trimming
                                       # it for the mid-window pedestal would counteract this deck's one goal.
                                       # deliberately AT the stability edge to reproduce the data's sharp
                                       # 1600-1800 s plunge; visc 1e13 regularizes (deck-30/31 mechanism).

# UNUSED after PST swap: normal_traction_tolerance = 0.0
tangential_traction_tolerance = 1e-16
# UNUSED after PST swap: dilation_angle_peak_degrees = 50.0     # DECK22: 37->50 (the CORRECT dilation lever). Deck21 showed dilation_state decays 1.0->0.47 by peak slip so dilation accrues in the PEAK-angle regime (raising residual 15->22 barely moved it). tan(37)=0.75->tan(50)=1.19 to lift peak dilation -0.022->~-0.031 mm. NB longer Ld cuts slip/dilation so this is deliberately aggressive.
# UNUSED after PST swap: dilation_angle_residual_degrees = 22.0 # DECK21: raised 15->22 (tan15=0.27->tan22=0.40). Deck19 dilation/slip ratio was ~0.29 (residual-dominated); target 0.031/0.077=0.40. Lifts peak dilation -0.021->~-0.031 mm and (via sigma'n relief) nudges slip 73->~77 um.
# UNUSED after PST swap: dilation_decay_distance = 1.0e-4
# UNUSED after PST swap: dilation_decay_exponent = 1.0          # revised law requires >= 1.0 (was 0.5; singular slope at zero slip)
# UNUSED after PST swap: dilation_opens_joint = true            # V15: route dilation into the joint OPENING (kinematic hardening)

# DECK23: REVERSIBLE (elastic) joint-normal opening -- new source capability. The plastic dilation is
# thermodynamically capped at dn/ds <= tau/sigma'_n ~ mu ~0.40 (dissipation limiter, .C:1066-1100), so the
# angle is INERT and the -0.041mm PEAK dilation (needs dn/ds 0.55) is unreachable by g_np alone; the data
# ALSO recovers -0.041 -> -0.031 on unload, a purely irreversible g_np cannot. This adds an elastic opening
# d_rev = C_n*<sigma_ref - sigma'_n>_+ that opens as injection drops sigma'_n (peak) and closes as it recovers
# (residual). Decoupled/output-only: does not feed the residual (far-field-governed sigma'_n). Reported normal
# dilation = g_np + d_rev.
                                          # kappa*g_np*<32.1e6 - sn>_+ -- compliance carries slip history: stiff
                                          # pre-slip (flat dilation panel before onset, the 57_04 lesson), soft after
                                          # bulking. kappa = C_n_old/g_np_end = 3.2e-13/(0.55*73.7e-6 ~ 40.7e-6) ->
                                          # unload branch matches the SW-S3 pin v6 sized; OUTPUT-ONLY (no mechanics).
                                          # NB SW-S3 reported dn is ~73% NOT fault opening (zeta 0.27, paper-frame
                                          # study) -> dn stays a DIAGNOSTIC here, never a calibration target.|
                                     # it: dn recovers only 44->41 um (3 um) while sigma'n rises 15.25->24.79
                                     # (9.54 MPa) -> C_n = 3e-6/9.54e6 = 3.2e-13 m/Pa. The rough joint stays
                                     # PROPPED (dilation-locked asperities), unlike the sawcut's 9.5e-13.
                                     # WAS DECK52_07: 5.0->7.0e-13 (SW-S4 sizing).
                                     # drops ~33->30um; rev share must supply ~11um at the trough deficit
                                     # (31-15.1)e6*7e-13 = 11.1um -> dn peak ~-0.041 (data -0.0409) and
                                     # end-recovery improves (rev_end ~ 3.8um at sigma'n_end ~25.5 ->
                                     # dn_end ~ -0.034 vs 52_04's -0.0357; data -0.0314).   # WAS DECK52_01: 7.0->5.0e-13 (dn peak -0.0459 -> ~-0.042 at slip ~84;
                                     # rev at trough 5e-13*16.5e6 = 8.3um). WAS DECK50: 6.0e-13->7.0e-13. The slip trims cut PLASTIC dilation by
                                     # ~mu*dslip ~ 0.4*8um = 3.2um (peak -0.0417 -> ~-0.038); +1e-13 adds
                                     # C_n*(31-13.5)e6 ~ +1.75um reversible at the trough -> peak ~ -0.040,
                                     # end ~ -0.031 (was -0.0345; data -0.0314).    # DECK32: 8.5e-13->6.0e-13. Deck31 peak dil -0.0451 (target -0.041); plastic part is now ~-0.032 (limiter, raised by the higher mid-slip tau), so cut the reversible part harder: rev_peak 6e-13*16e6=0.0096 -> peak dil ~-0.041.
# UNUSED after PST swap: max_plastic_slip_increment = 0.0     # revised law forbids increment caps; substepping + viscosity instead (was 1.0e-6).
                                      # TESTED 3.0e-6 (3x relaxation) and REJECTED: the cap was found to
                                      # bind on 14 timesteps, directly contributing 30% of total slip,
                                      # and relaxing it did close part of the peak shear-slip gap (43.2 ->
                                      # 49.4 um vs. the paper's 75 um at Pi=28). BUT the extra slip also
                                      # feeds back through the dilatant normal-stress relief (more slip ->
                                      # more dilation -> traction_new(0) less compressive -> lower
                                      # limit_tau = cohesion + mu*sigma_n), pushing the model's sigma_n/tau
                                      # trajectory OFF the near-exact linear Coulomb fit to the paper's own
                                      # Table 2 data that the friction/cohesion recalibration achieved.
                                      # Net effect, quantified over all 11 hold stages: tau RMSE worsened
                                      # 0.49->0.75 MPa (mean |err| 13.6%->22.4%, worst at -57% during late
                                      # unloading) while sigma_n RMSE only improved 0.77->0.51 MPa and ds
                                      # RMSE improved 25.8->21.3 um -- a net-negative trade since the
                                      # stress-state fit (the more rigorously, independently validated
                                      # quantity) degrades more than the displacement fit improves. Kept at
                                      # 1.0e-6; results_csv/..._cap3e6_experiment.csv preserves the test.
                                     # keeps ~60% of the burst guard (TS slope is 0.77x k_sys so margin exists)
                                     # and cuts the mid-slip viscous pedestal ~0.4 MPa (tau@1300 11.0 vs 9.12).
# --- DECK52_12: referenced regularized rate-and-state (the RE-STICK mechanism) --------------------
# THE data behavior the param decks can only approximate: the fault re-sticks AT the trough (ds freezes
# at 75-76um t~1790-1850) because sustained sliding at the hold heals/strengthens it, then it stays stuck
# through unload. Referenced RSF: mu_rs = a*(asinh(z) - asinh(1/2)), zero at V=V0, STRENGTHENS V>V0
# (brakes the 1700-1850 acceleration, V~1.8e-7), aging theta heals during deceleration -> re-stick;
# mildly NEGATIVE at V<<V0 (late creep) -> eases tau_end ~-0.2 toward data 2.20. a-b=0.012 velocity-
# strengthening (b/a=0.4). V0=5e-8 sits BELOW the window rate so the window sees +0.15-0.25 MPa brake.
# First-cut params -- expect one tuning iteration (a scales everything; V0 shifts the neutral rate).
# UNUSED after PST swap: use_rate_and_state = true

# --- ADOrcaRoughnessDamageFracturePermeability (roughness-coupled) : DD02 reference ---
initial_hydraulic_aperture = 1.22e-6  # DECK59_07: Ye & Ghassemi Table 2 initial aperture (k=1.24e-13 m2)
                                     # data PEAK aperture (1.215 um) with the initial: the digitized SW-S3 permeability
                                     # starts at 0.418e-13 m^2 (= a_h 0.709 um) and PEAKS at 1.23e-13 (= 1.215 um) --
                                     # v20/v21 ran the whole panel 3x high (k_init 1.24e-13) and pressurized the fault
                                     # 3x too fast (early sigma-n drop -> early onset). BB closure Vm/Kni were sized
                                     # around a_h 0.709->1.215 (v5 back-analysis) and are consistent again.
                                     # SW-S3's OWN a_h at Pi=8 (k_init 1.24e-13; v5 started at 0.42e-13, 3x low,
                                     # and could then never reach the 3.66e-13 peak).
aperture_scale = 0.001
normal_stress_aperture_compliance = 2.0e-14 # m/Pa, reversible aperture opening as sigma'_n decreases
reference_effective_normal_stress = 32.1e6  # Pa: DECK42 preload sigma'_n (opening=0 here).
# DECK42: POWER-LAW BARTON-BANDIS closure (bounded), replacing the linear term. Story: deck41's
# EXPONENTIAL closure captured the unload stiffening but is UNBOUNDED as sigma'n->0 -> POSITIVE
# FEEDBACK in the coupled HM (aperture drives fracture Darcy flow -> pore pressure -> sigma'n): at
# peak injection sigma'n crashed 15->7.5 MPa, a_h 2.8um, k 8.2e-13 (runaway). A single hyperbola (p=1)
# is bounded but too weak (stiffening ceiling (shi/slo)^2=2.1x < data's 3.2x). POWER-LAW BB g(s)=
# s^p/(sigma0^p+s^p) with p=2 gives ceiling (shi/slo)^3=3.18x ~ data AND stays bounded by Vm -> the
# feedback SATURATES. Fit to Table-2 unload (RMSE 11nm): Vm=1.17um, sigma0=Vm*Kni=15MPa, p=2. At the
# operating sigma'n~15 the opening ~0.35um ~= the old linear term (which was stable) -> no crash;
# curvature only differs in mid-unload (the fix). Tune: p up = sharper; sigma0(=Vm*Kni) up = stiffer.
use_nonlinear_normal_closure = true
nonlinear_closure_type = barton_bandis
bb_max_aperture_closure = 1.2e-6   # SW-S3: peak opening +0.51um (a_h 0.709->1.215) vs SW-S4 +0.33     # Vm (m): DECK43 1.17->0.85. Deck42 (Vm1.17) was too SOFT ->
                                     # coupled HM feedback drooped peak sigma'n 15->12 (aperture->perm->
                                     # flow->pore pressure->sigma'n) and perm OVERSHOT (peak k 1.22 vs
                                     # data 0.925, unload bias +0.16). Stiffer closure = less opening ->
                                     # less feedback -> sigma'n holds ~14-15 -> perm drops at peak AND
                                     # mid-unload together. Shape (p2, 3.2x stiffening) preserved.
bb_initial_normal_stiffness = 1.25e13 # sigma0 = Vm*Kni = 15 MPa held # Kni (Pa/m): sigma0 = Vm*Kni = 15 MPa (held; Kni up as Vm down)
bb_stress_exponent = 4.0              # p: power-law closure exponent (1=hyperbola, 2=matches 3.2x stiffening)
dilation_scale = 0.038               # DECK59_07: first back-analysis to Table-2 a_h 1.22 -> 2.10 -> 1.64 um
                                     # With W/L corrected (below) v9's Q_peak is still +22% (1.022 vs 0.838) -> a_h
                                     # needs x0.936; v10's recovered slip grows the dilation-aperture term x1.36 ->
                                     # scale = 0.06 * 0.75/(0.90*1.36) ~ 0.038. Judge on the FLOW panel (Q), not the
                                     # digitized k curve (flagged ~3x low vs its own Q - re-digitization pending).
                                     # WAS SW3-v6: 0.013 (SW-S4 sawcut) -> 0.06. Sized from Table-2 SW-S3
                                     # END-UNLOAD state (slip locked, closure known): a_h_end 1.64 um =
                                     # 1.22 + closure(24.8; 0.107) + ds*dn_pl(~31um)*retention(0.28) - gouge
                                     # (0.234) -> ds ~ 0.06. Physically: the rough surface channels ~5x more
                                     # of its mechanical dilation into hydraulic aperture than the polished
                                     # sawcut (less tortuosity/contact clogging). Predicts trough a_h ~1.9-2.0
                                     # um -> k ~3.2e-13 (data 3.66 peak is the burst spike, quasi-static-
                                     # clipped as in SW-S4). WAS V15 SW-S4: 0.013.
                                     # cumulative_dilation ~17x. Holds a_h (permeability) at the V14 fit.
                                     # CALIBRATE to the perm/flow curve once the full run is scored.
retention_residual = 0.28              # DECK38 (from deck35, DECOUPLED perm-only knob): 0.35->0.28.
                                     # Deck35 back-analysis vs Table 2: the ONLY real remaining gap
                                     # is fracture permeability AFTER unloading ~15-20% too high
                                     # (model k 0.53-0.81 vs Table2 0.46-0.74 e-13; sigma'n/tau/slip
                                     # all in band). Root = too much cumulative shear-dilation retained
                                     # in the aperture at residual roughness (Stage-3). retention_residual
                                     # is output-side in ADOrcaRoughnessDamageFracturePermeability -> ZERO
                                     # impact on the mechanical calibration (sigma'n/tau/slip/injection);
                                     # it only closes the aperture a bit more on unload. ~20% cut targets
                                     # k-after-unload down ~20-30% (k ~ a_h^2). First-cut value; if it
                                     # overshoots, 0.30-0.32. NB the dn-unload ELASTIC recovery miss
                                     # (actual jump frozen at -28um vs Table2 -41->-32) is a SEPARATE,
                                     # deeper issue: penalty_normal=2e13 is ~19x too stiff for the ~1e12
                                     # physical unload Kn; a single constant Kn can't match both the stiff
                                     # stick phase (Kn~4e12) and soft unload (Kn~1e12) -> needs a
                                     # stress-dependent (Bandis-Barton) normal stiffness SOURCE feature.
                                     # The reconstruction (REVcn6e13) already reproduces the dn curve.
self_propping_scale = 0.0
self_propping_exponent = 1.0
use_slip_damage = true
slip_damage_scale = 0.40e-6          # DECK52-SWEEP: re-fit to hold the developed unload gouge at slip~84um:
                                     # 0.28*(1-exp(-64/30)) = 0.247um (= deck-43/47 unload calibration). WAS DECK50 (=DECK47 values): 0.25->0.29 compensates the onset threshold
                                     # below so the fully-developed unload gouge is preserved (~0.247um at 78um
                                     # slip: 0.29*(1-exp(-(78-40)/20)) = 0.246).
slip_damage_onset_slip = 30e-6      # DECK52-SWEEP: 40->20um. The HARD 40um threshold caused the perm/flow
                                     # SPIKE at t~1380 (deck50) / t~1115 (deck51): aperture rises un-gouged,
                                     # then gouge slams in over char 20um at slip=40um and carves a dip the
                                     # data does not show. Data loading branch only needs gouge~0 up to
                                     # slip~20um (Pi=20 hold); starting at 20um with a LONGER char (below)
                                     # builds gouge gradually across the slip phase -> no spike. WAS 40e-6:       # DECK50 (=DECK47 LOADING-BRANCH FIX): gouge accrues only after 40um of
                                     # slip. Deck45/46 back-analysis: pre-slip loading aperture matches the paper
                                     # exactly; the loading-branch perm gap opens EXACTLY when slip starts (gouge
                                     # front-loaded by char slip 20um). Delaying gouge onset lets the loading
                                     # aperture rise with the paper while the unload branch is unchanged.
slip_damage_characteristic_slip = 30e-6 # DECK52-SWEEP: 20->30um (gentler gouge rate, kills the spike)
min_hydraulic_aperture = 1.22e-6     # DECK59_07: floor equals authoritative Table-2 initial aperture
                                     # hydraulic_aperture but MISSED this floor -> a_h was clamped straight back to 1.22
                                     # and PINNED there all run (perm flat 1.24e-13; the whole hydraulic panel inert).
                                     # Floor = corrected initial (perm data min IS the initial 0.42e-13).
max_hydraulic_aperture = 8e-6        # numerical cap (caseF found it necessary on the fine mesh to bound
                                     # cubic transmissivity; harmless when a_h stays below it). The coarse
                                     # 2.0 deck left it unset.
compute_transmissibility = true      # produce fracture_transmissivity for OrcaFractureFlowInterfaceKernel
                                     # (matches the proven caseF flow coupling; the 2.0 deck let the flow
                                     #  kernel form T from permeability*thickness instead).
fault_thickness = 1e-3

# --- fluid ---
fluid_density_ref = 1000
fluid_viscosity_ref = 1.002e-3
fluid_bulk_modulus = 2.2e9  # water at 20 C (Sec. 2.5); was 4.7835616438e9, 2.17x too stiff
paper_flow_width_over_length_sw_s3 = 0.812485740964  # inverted from Table 2 via eq (10)
mesh_flow_width_over_length_sw_s3 = 0.674   # diagnostic only: prior estimate based on numerical source-node spacing
ml_per_m3_per_min = 6.0e7

# --- output ---
exodus_file_base = results_exodus_hpc_rorqual/97_03_sw3_cyclic3_hpc
csv_file_base    = results_csv_hpc_rorqual/97_03_sw3_cyclic3_hpc
checkpoint_file_base = results_checkpoint_hpc_rorqual/97_03_sw3_cyclic3_hpc

######################################################################################
[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

[Problem]
  boundary_restricted_elem_integrity_check = false  # split-interface lower-D map is orientation-sensitive
  kernel_coverage_check = false  # block 900 (fracture_surface) is output-only
  extra_tag_vectors = 'mech_reaction mass_reaction'
[]

######################################################################################
[Mesh]
  # Orca_2.0 reference SW-S4 mesh: pre-tagged with top/bottom/sides surfaces and no_disp_x/no_disp_y
  # pins. Here we only add the injection/production source nodes and split the conforming fault
  # (nodeset 'fracture_interface') into the CZM interface of the same name via OrcaFaultInterface3DGenerator.
  [file_mesh]
    type = FileMeshGenerator
    file = ${mesh_file}
  []
  # SIDESET-DUPLICATION FIX: the blanket [Mesh]/construct_side_list_from_node_list=true (needed
  # because top/bottom/sides exist only as NODESETS in the pre-tagged reference mesh) runs at
  # final mesh setup, i.e. AFTER fault_split_3d below has already built a correctly single-sided
  # 'fracture_interface' sideset. Node duplication during the split copies nodeset membership to
  # BOTH new node copies (by design, so other consumers can find either side), so the nodeset
  # 'fracture_interface' itself is "doubled" post-split. The blanket flag then re-derives sides
  # from that doubled nodeset and re-adds the second face, silently doubling the sideset's area
  # (confirmed: AreaPostprocessor on fracture_interface reports ~8.24e-3 m^2 vs. the ~4.0e-3 m^2
  # expected from the sample geometry/theta=30deg -- a factor of ~2.06). Every ADSideAverageMaterialProperty/
  # SideAverageValue over this boundary (czm_sigma_n_pp, shear_traction_magnitude_pa, etc.) was
  # therefore reporting roughly half its true value, which is why the fault's effective normal
  # stress and shear traction were running at ~40-50% of what equations (3)/(4) predict from this
  # model's own bulk sigma1/sigma3 -- a ~2x gap that persisted across both penalty-stiffness
  # (10x Kn) and pore-pressure-coefficient tests, ruling those out and pointing at the sideset.
  # Fix: convert top/bottom/sides to sidesets explicitly and EARLY (before the fault even exists
  # as a nodeset-derived boundary), via the selective nodesets_to_convert list below, then leave
  # the blanket flag off so it never touches fracture_interface after the split.
  [sidesets_from_nodesets]
    type = SideSetsFromNodeSetsGenerator
    input = file_mesh
    nodesets_to_convert = 'top_nodeset bottom_nodeset sides_nodeset'  # SW-S3 mesh names
  []
  [source_in]
    type = ExtraNodesetGenerator
    input = sidesets_from_nodesets
    coord = '-0.023159583 0.0 0.019919005'   # L123p4: exact interface-node coordinate on the 123.40 mm mesh.
                                     # Was '-0.023160 0 0.020419' (the 124.40 mm mesh). Shortening the core
                                     # moves every node on the fracture plane; use_closest_node never errors,
                                     # so a stale coordinate silently pins injection to a BULK node.
                                     # Verified on this mesh: closest node IS on the interface, 0.0 um away.
    new_boundary = source_in
    use_closest_node = true
  []
  [source_out]
    type = ExtraNodesetGenerator
    input = source_in
    coord = '0.023159583 0.0 0.103480995'   # L123p4: exact interface-node coordinate (was '0.023160 0 0.103981')
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

######################################################################################
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

######################################################################################
[Functions]
  # SW-S4 axial preload: ramp to -4.6e-5 m over t=2->55 s, then hold (constant piston disp) to end.
  # [axial_disp_ramp]
  #   type = PiecewiseLinear
  #   x = '0 2 55 3500'
  #   y = '0 0 -4.6e-5 -4.6e-5'
  # []
  [axial_disp_ramp]
      type = ParsedFunction
      # BATCH4 COMPENSATED prescribed piston displacement for the penalty (compliant-frame) BC:
      # u_pres(t) = u_rigid(t) - sigma_zz_top(t)/penalty, so the SAMPLE sees the same preload state as
      # the rigid deck (05) while the spring provides the series machine compliance during slip.
      # Held constant after t=55 s (fixed piston command); the spring then unloads as the fault slips.
      expression = 'if(t<2.0,${axial_pres_initial},if(t<55.0,${axial_pres_initial}+(${axial_pres_final}-${axial_pres_initial})*(t-2.0)/53.0,if(t<2550.0,${axial_pres_final},if(t<2850.0,${axial_pres_final}+4.5e-06*(t-2550.0)/300.0,${axial_pres_final}+4.5e-06))))'
    []

  # Injection pressure schedule (Pa): FULL digitized Ye & Ghassemi SW-S4 history -- the complete
  # rise-AND-FALL cycle to t~3404 s (peak ~28 MPa at ~1788 s, declining back to ~8 MPa). The earlier
  # caseF-derived schedule contained only the RISING limb (truncated at ~1900 s), so the run stopped
  # before the post-peak phase where the injection decline lets the fault re-stabilize and the
  # differential stress partially recovers. Restored from the Orca_2.0 reference deck.
  # ------------------------------------------------------------------------
  # DISCUSSION DECK (cyclic).  3 EQUAL-PEAK load/unload cycles.
  # This REPLACES the digitized Ye & Ghassemi schedule; do not score against
  # Table 2.  The validated run is the 93-series parent.
  #
  # Ramp rate R = 8.8891 kPa/s, taken from this specimen's own
  # schedule (5.75 -> 28.57 MPa in 2569.2 s), so the cyclic run
  # loads at the same rate as the run it is compared against.
  # Peak 28.57 MPa held 200 s; floor 8.00 MPa held 200 s.
  #
  # PERMEABILITY IS READ AT THE HOLDS, where the pressure is identical from
  # cycle to cycle and the slip velocity has relaxed (so the eta*V overstress
  # is not in the reading).  Probe instants:
  #     cycle 1 peak  hold  t =    2669.2 s
  #     cycle 1 floor hold  t =    5183.3 s
  #     cycle 2 peak  hold  t =    7697.4 s
  #     cycle 2 floor hold  t =   10211.4 s
  #     cycle 3 peak  hold  t =   12725.5 s
  #     cycle 3 floor hold  t =   15239.6 s
  # ------------------------------------------------------------------------
  [injection_pressure]
    type = PiecewiseLinear
    x = '0.0000 2.0000 2569.2000 2769.2000 5083.2799 5283.2799 7597.3599 7797.3599 10111.4398 10311.4398 12625.5197 12825.5197 15139.5996 15339.5996 15592.7197 15792.7197'
    y = '5.75e+06 5.75e+06 2.857e+07 2.857e+07 8e+06 8e+06 2.857e+07 2.857e+07 8e+06 8e+06 2.857e+07 2.857e+07 8e+06 8e+06 5.75e+06 5.75e+06'
  []

  [production_pressure_fn]
    type = ConstantFunction
    value = ${production_pressure}
  []

  # Confining pressure on the cylindrical "sides" surface via the analytic outward normal (constant,
  # since the bulk carries an isotropic -31e6 initial_stress baseline).
  [sigma3_x]
    type = ParsedFunction
    expression = '-${confining_pressure}*x/${sample_radius}'
  []
  [sigma3_y]
    type = ParsedFunction
    expression = '-${confining_pressure}*y/${sample_radius}'
  []
[]

######################################################################################
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
###################################################################################
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
  # MECHANICAL fault-pressure route (REQUIRED for the decoupled law, which has no pore-pressure
  # term in its strength). Applies pore pressure as a traction pushing the faces apart -> reduces
  # the contact normal stress -> the Coulomb strength falls through the mechanics (effective stress).
  # orca_3.0 equivalent of the reference OrcaFaultPressureInterfaceKernel (coeff 0.935, sign -1).
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

######################################################################################
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
    # BATCH3: compliant loading frame (MTS servo-hydraulic elastic give in SERIES with the rock).
    # A hard Dirichlet = infinitely stiff frame -> caps fault slip/dilation below the paper. penalty=k_machine/A.
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

######################################################################################
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

######################################################################################
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

  # --- CZM kinematics + decoupled-dilation-roughness constitutive law ---
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
    # Case 70_01: first SW3 BBFast transfer. No prior SW3 BBFast FE calibration exists.
    # The common experiment comes from corrected 59_07. The shear transfer is sized from
    # the SW3 paper targets (peak mu about 0.62, arrest mu about 0.23 at 71 um):
    # JRC=22.5 is the onset-matching value identified by the combined hardening audit,
    # while Dc=55 um and m=1.6 place the 71-um state near the arrest shelf. JRC=22.5 is
    # outside Barton's nominal 0-20 range and about 11x measured JRC=1.96; this is an
    # explicitly labeled effective transfer parameter, not a measured joint property.
    type = OrcaBartonBandisContactTractionFastADHardening
    boundary = fracture_interface

    # Power-law BB mechanical normal closure. These are the validated SW4 normal-law
    # starting values; SW3 has no independent normal-closure calibration for this law.
    use_hyperbolic_normal_closure = true
    initial_normal_stiffness = 2.443e11
    maximum_closure = 4.591e-5
    normal_closure_stress_exponent = 3.28
    normal_closure_offset = 4.433e-5
    normal_unload_retention_fraction = 0.06
    normal_unload_retention_time = 0.0
    normal_reclosure_stiffness_multiplier = 1.0
    normal_unload_activation_slip = 5.0e-5
    reported_reversible_normal_opening_scale = 1.0   # 93-series: back to the library default. Was 0.758 -- see banner.
    reported_reversible_normal_opening_retention_fraction = 0.0   # 93-series: back to the library default. Was 0.552.
    reported_reversible_normal_opening_retention_activation_slip = 50e-6
    penalty_tangent = ${penalty_tangent}
    normal_traction_tolerance = 0.0
    tangential_traction_tolerance = ${tangential_traction_tolerance}

    # BB peak envelope plus concentrated SW3 slip weakening.
    jrc = 1.96                        # PAPER Table 1 (measured). Was 23.35 -- 11.9x measured AND outside Barton's 0-20 scale.
    jcs = 1.5e8                       # PAPER Sec. 2.1 UCS. Was 3.0e8.
    residual_friction_angle_degrees = 29.756  # pins the envelope through Table 2's last stick stage (23.42 MPa, 14.26 MPa) at the measured JRC/JCS. Was 8.45.
    cohesion = 1.67e6                  # 90_05: level-only correction, see header.
    residual_cohesion = 1.40e6   # 92_03: -0.25 MPa off 91_05, see header. 89_02 ran 0.0, 91_05 ran 1.65e6.
    use_scale_correction = false
    use_mobilized_jrc = false
    compressive_normal_stress_floor = 1e3
    pore_pressure_strength_coefficient = 0.0
    use_slip_weakening = true
    characteristic_slip_distance = 6.0e-5
    slip_weakening_exponent = 1.4
    slip_weakening_residual_friction_angle_degrees = 8.45

    # Rough-sample dilation/propping transfer. The 29.45-degree residual is inherited
    # from the SW3 calibration; the 32-degree peak is the Table-2 dn/ds starting point.
    use_dilatancy = true
    use_decoupled_dilation = true
    dilation_angle_peak_degrees = 26.0
    dilation_angle_residual_degrees = 26.0
    dilation_decay_distance = 1.0e-4
    dilation_opens_joint = true
    accumulate_irreversible_dilation = true
    cap_dilation_to_available_closure = false
    max_dilation_increment = 0.0

    use_roughness_degradation = true
    roughness_state_initial = ${initial_roughness}
    roughness_state_residual = ${residual_roughness}
    roughness_characteristic_slip = 4.0e-5

    max_plastic_slip_increment = 0.0
    tangential_viscosity = 4.0e11
    min_tau_limit = 0.0
    max_return_mapping_iterations = 100
    relative_tolerance = 1e-10
  []
  [czm_global_traction]
    type = OrcaComputeGlobalTractionSmallStrain
    boundary = fracture_interface
  []

  # --- hydraulics: roughness-coupled aperture/permeability (NON-kinematic), reading the decoupled
  #     law's dilation_jump_increment + roughness_state (the reference DD02 wiring) ---
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

    use_kinematic_aperture = false
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
    cumulative_plastic_slip_is_ad = false   # BBFast exports this property non-AD
    slip_damage_aperture_name = slip_damage_aperture

    min_hydraulic_aperture = ${min_hydraulic_aperture}
    max_hydraulic_aperture = ${max_hydraulic_aperture}
    compute_transmissibility = ${compute_transmissibility}
    fluid_viscosity = ${fluid_viscosity_ref}
    fault_thickness = ${fault_thickness}
  []

  # --- scalar extraction for postprocessing (local frame: index 0 = normal, 1,2 = shear) ---
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

  # --- Orca_2.0-style GLOBAL-frame normal jump (displacement_jump_global -> Normal). This is the
  #     exact extraction the reference deck used for "normal dilation". NOTE: it is mathematically
  #     identical to czm_dn (index-0 of the local interface_displacement_jump), because the local
  #     jump is just the global jump rotated into the fault frame -- provided here so the output
  #     matches the 2.0 pipeline and to confirm the flat normal-dilation panel is PHYSICAL (the
  #     fault is not opening), not an extraction artifact. ---
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

######################################################################################
[Postprocessors]
  # --- mesh sanity check: expected elliptical fracture area for theta=30deg, D=50.51mm is
  #     pi*(D/2)*(D/2/cos(60deg)) ~= 4.0e-3 m^2. If the reported area is ~2x that, the
  #     'fracture_interface' sideset is double-counting sides (both faces of the split tagged
  #     with the same boundary id), which would explain a uniform ~2x under-report on every
  #     ADSideAverageMaterialProperty/SideAverageValue computed over this boundary. ---
  [fracture_interface_area_pp]
    type = AreaPostprocessor
    boundary = fracture_interface
  []
  [injection_pressure_pp]
    type = PointValue
    variable = pore_pressure
    point = '-0.023159583 0.0 0.019919005'  # L123p4: must track the source_in coord above
  []
  [inj_reaction_sum_pp]
    type = NodalSum
    variable = inj_flux_aux
    boundary = source_in
  []
  [prod_reaction_sum_pp]
    type = NodalSum
    variable = inj_flux_aux
    boundary = source_out
  []
  [flow_rate_pp]
    type = ParsedPostprocessor
    pp_names = inj_reaction_sum_pp
    expression = 'abs(inj_reaction_sum_pp)'
  []
  # --- FLOW-RATE DIAGNOSTICS (mL/min). Ye et al. Table 2 reports the cubic-law Eq. 9 value:
  #     Q = (W/L) * a_h^3/(12*mu) * dP. The inferred SW-S4 W/L ~= 0.81 is consistent between
  #     the first and peak Table 2 points. The previous Orca_2.0 reference-area form is retained
  #     separately as flow_rate_reference_area_ml_min_pp because it is not the paper Eq. 9 value. ---
  [pp_outlet_pp]
    type = PointValue
    variable = pore_pressure
    point = '0.023159583 0.0 0.103480995'  # L123p4: must track the source_out coord above
  []
  [pp_drop_pp]
    type = ParsedPostprocessor
    pp_names = 'injection_pressure_pp pp_outlet_pp'
    expression = 'injection_pressure_pp - pp_outlet_pp'
  []
  [flow_rate_validation_ml_min_pp]
    type = ParsedPostprocessor
    pp_names = 'hydraulic_aperture_pp pp_drop_pp'
    expression = '(${paper_flow_width_over_length_sw_s3} / (12.0 * ${fluid_viscosity_ref})) * hydraulic_aperture_pp^3 * pp_drop_pp * ${ml_per_m3_per_min}'
  []
  [flow_rate_mesh_geometry_ml_min_pp]
    type = ParsedPostprocessor
    pp_names = 'hydraulic_aperture_pp pp_drop_pp'
    expression = '(${mesh_flow_width_over_length_sw_s3} / (12.0 * ${fluid_viscosity_ref})) * hydraulic_aperture_pp^3 * pp_drop_pp * ${ml_per_m3_per_min}'
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

  # --- applied axial stress from the assembled top-boundary reaction ---
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

  # --- secondary differential stress from the top-surface axial stress average ---
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
  # --- local bulk stress AT the fault face, vs. the far-away "top" surface above. Equations 3/4
  #     applied with the TOP-surface sigma1 and the domain-average sigma3 give a fault normal/
  #     shear traction that is NOT reachable by any real fault angle (solving simultaneously for
  #     theta gives cos(2theta) > 1) -- i.e. the bulk stress state at the fault is NOT the same as
  #     at the top surface. These two diagnostics test that directly. ---
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

  # --- sigma3 cross-check: differential_stress_mpa_pp above ASSUMES sigma3 = 30 MPa exactly
  #     rather than measuring it. stress_xx already existed as an AuxVariable/AuxKernel but was
  #     never exported -- add the missing postprocessor so the 30 MPa confining assumption can
  #     actually be verified against the bulk response instead of taken on faith. ---
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

  # --- fault normal stress / pressure. The pressure enters MECHANICALLY, so the penalty contact
  #     normal stress (czm_sigma_n) is ALREADY the effective normal stress sigma'_n. ---
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
  # notebook alias interface_pore_pressure_pa -> fracture_pressure_mean_pp (same quantity)
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

  # --- decoupled-law state diagnostics ---
  # FastAD publishes the plastic-slip/strength diagnostics below as regular
  # (non-AD) material properties.  roughness_state and dilation_jump_increment
  # remain AD properties.
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
  # notebook alias bb_limit_tau_pa -> bb_limit_tau_pp (Coulomb shear strength, same quantity)
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

  # --- shear traction magnitude |tau| = sqrt(tau_1^2 + tau_2^2), Pa ---
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

  # --- total fault shear slip = |shear displacement jump| (elastic + plastic), mm ---
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
  # Level 84 observation operator. The raw local CZM jump above is retained.
  [reported_czm_shear_slip_mm_pp]
    type = ParsedPostprocessor
    pp_names = czm_shear_slip_mm_pp
    expression = 'czm_shear_slip_mm_pp * 1'
  []

  # --- hydraulics ---
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

  # --- NORMAL DILATION (fault-normal displacement jump), mm ---
  [czm_dn_pp]
    type = ADSideAverageMaterialProperty
    property = czm_dn
    boundary = fracture_interface
  []
  # DECK23: reported normal opening now = irreversible g_np + reversible elastic d_rev (new source
  # property normal_opening_total). czm_dn_pp above (kinematic g_n) is kept for diagnostics/comparison.
  # Level 83: output-only BBFast reconstruction. The kinematic czm_dn remains above for
  # diagnostics and continues to drive mechanics/hydraulics; this property is validation only.
  [czm_dn_total_pp]
    type = SideAverageMaterialProperty
    property = normal_opening_total
    boundary = fracture_interface
  []


  # SIGN FIX: czm_dn follows this model's native convention (positive = opening, negative =
  # closing -- verified from source: interface_displacement_jump = R^T*(disp_neighbor - disp),
  # i.e. normal . displacement_jump_global). The paper's convention is the OPPOSITE (negative =
  # opening/dilation, per Sec. 3: "a NEGATIVE trend of normal dilation" demonstrates dilation).
  # Must negate to match the paper -- this previously did not, and disagreed in sign with the
  # (correctly negated) frac_normal_dilation_paper_mm computed from the same underlying jump.
  [czm_normal_dilation_paper_mm_pp]
    type = ParsedPostprocessor
    pp_names = czm_dn_total_pp           # Level 83 reported opening; output only
    expression = '-czm_dn_total_pp * 1e3'
  []
  # --- Orca_2.0-style normal-dilation procedure: SideAverage of the GLOBAL normal jump, paper sign
  #     (compression positive => opening plotted negative). frac_normal_dilation_paper_mm is the 2.0
  #     column name. (Same value as czm_dn_pp; provided for 2.0-pipeline compatibility.) ---
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

  # --- APERTURE-CHAIN DIAGNOSTICS (why the permeability is ~constant): a_h grows only via
  #     aperture_scale*mechanical_aperture (=0 while the fault stays closed, mechanical_aperture
  #     clamped to >=0) and dilation_scale*cumulative_dilation (~1e-10 m here -> negligible). ---
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

  # --- VALIDATION FRAME (Ye et al. specimen transformation, theta = 29 deg) ---
  # These are reconstructed from the axial reaction and mean end pressure, exactly
  # like the experimental curves. Keep the local CZM tractions above as separate
  # constitutive diagnostics; they are not the same observable.
  [effective_normal_paper_frame_mpa_pp]
    type = ParsedPostprocessor
    pp_names = 'differential_stress_reaction_mpa_pp injection_pressure_pp pp_outlet_pp'
    expression = '30.0 - 0.5*(injection_pressure_pp + pp_outlet_pp)*1e-6 + 0.23504036788339755*differential_stress_reaction_mpa_pp'
  []
  [shear_stress_paper_frame_mpa_pp]
    type = ParsedPostprocessor
    pp_names = differential_stress_reaction_mpa_pp
    expression = '0.424024048078213*differential_stress_reaction_mpa_pp'
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
    point = '${sample_radius} 0 0.11170'
  []
  [bulk_disp_z_upper_pp]
    type = PointValue
    variable = disp_z
    point = '${sample_radius} 0 0.11170'
  []
  [bulk_disp_x_lower_pp]
    type = PointValue
    variable = disp_x
    point = '${sample_radius} 0 0.01170'
  []
  [bulk_disp_z_lower_pp]
    type = PointValue
    variable = disp_z
    point = '${sample_radius} 0 0.01170'
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

######################################################################################
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
  end_time = 15792.7

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.75                 # Level 84 controlled initial step
    optimal_iterations = 18
    growth_factor = 1.2
    cutback_factor = 0.5
  []

  dtmax = 0.75
  dtmin = 1e-6                 # allow fine crawl through the viscously regularized slip burst
  l_max_its = 50
  l_tol = 1e-4
  nl_max_its = 70
  nl_abs_tol = 1e-4            # PST-FLOWRSF: 1e-6 -> 1e-4. The flow form's transition-band
                               # qps floor |R| at ~4e-5 N (see banner FAILURE+FIX RECORD);
                               # 1e-4 N ~ 1.5e-9 of the 70 kN load scale. With the parent
                               # stick-branch laws 1e-6 was reachable; here it is not.
  nl_rel_tol = 1e-6
[]

######################################################################################
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
    time_step_interval = 20
    num_files = 4
  []
[]
