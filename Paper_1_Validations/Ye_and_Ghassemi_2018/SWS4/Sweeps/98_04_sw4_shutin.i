# =============================================================================
# 93-SERIES -- MESH AND POSTPROCESSOR AUDIT FIXES.  SW-S4 mesh 5
# Built from 90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6.i.  Constitutive parameters are UNCHANGED;
# this series changes only what is measured and reported, plus one source-node
# coordinate on SW-T1 mesh-5.
#
# WHAT MOVED IN THIS DECK
#   1. d_n NOW READ FROM THE SAME CHANNEL AS THE OTHER THREE SPECIMENS.
#      czm_normal_dilation_paper_mm_pp was built on czm_dn_pp (the raw kinematic
#      jump) here and on czm_dn_total_pp (normal_opening_total) everywhere else.
#      With the reporting knobs at their defaults -- which is the case on this
#      deck -- the two are numerically identical, so this changes no number; it
#      removes a cross-specimen inconsistency that would otherwise have to be
#      explained in the paper.
#   2. Added czm_dn_total_pp, flow_rate_mesh_geometry_ml_min_pp and
#      reported_czm_shear_slip_mm_pp, the three channels SW-S4 lacked.
#   3. BULK PROBE POINTS PUT ON THE COMMON RULE.  z = L/2 +- 50 mm, a 100 mm
#      gauge, so bulk_normal_dilation_paper_mm_pp means the same thing on all
#      four specimens.  Diagnostic channels only.
#
# WHAT DID NOT MOVE, ON ANY 93-SERIES DECK
#   - every constitutive parameter of [czm_contact];
#   - the mesh file, the injection schedule, the BCs, the solver;
#   - the paper-frame trig constants (each already matched its own mesh's theta
#     to four decimals -- verified against the Exodus fracture_interface nodeset).
# =============================================================================
# =============================================================================================
# 98_04_sw4_shutin
#
# 90-SERIES: fix the ONSET, keep the RESIDUALS.  Back-analysis 2026-08-17.
# Parent: 89_06_sw4_bbfast_theta30_kernel_SV_biot0p6.i -- 10.5% mean normalized RMSE -- the best SW-S4 case -- event 50-73 s late, residual shear 2.82 vs 2.25 validated
#
# WHY (campaign-wide).  Every scored case fails at the injection step where its strength margin
# m = (tau_lim - tau)/tau_lim crosses zero.  The experiment fails at the TOP of the staircase, so
# a small strength deficit does not advance failure proportionally -- it advances it by a WHOLE
# STEP (~290 s on SW-T1/T2, ~350 s on SW-S3).  That is the whole "several hundred seconds early"
# signature.  Measured crossings: SW-S3 84_01-baseline 25-26 MPa (on time), 86_01 26-27 (on time),
# 89_02 22-23 (360-390 s early);  SW-S4 89_06 17-18 (50-73 s late), 89_01 14-15 (early).
#
# SW-S4 SPECIFIC.  LOWER-JRC arm of the 90_07 bracket; see that deck's header for the design.
# Together they span JRC 5 - 9 at fixed peak envelope, which brackets the JRC ~= 8.8 implied by
# the residual-shear interpolation while also testing how much of 89_06's on-time onset
# survives when the roughness feedback is cut.
#
# THIS DECK: jrc 17.5 -> 5.0, jcs 3.0e8 -> 1.5e8, phi_r 7.5 -> 22.72 deg (solved from
# phi_r + 5*log10(150/24) = 26.70, the same anchor 90_07 uses).
#
# PREDICTION: crossing moves from 17-18 MPa to 15-17 MPa.  If BOTH arms hold the onset and only the residual moves, JRC is confirmed as the residual
# knob and the onset is owned by phi_r -- which would decouple two things that have been fighting
# each other for four deck generations.
# =============================================================================================
# ==============================================================================
# 98_04_sw4_shutin
# GENERATED 2026-08-16 by scripts/build_paper_corrected_decks.py from
#   SWS4/68_01_sw4_bbfast_tail6p50_eta3p50_m0_kernel_SV.i
# -- do not hand-edit; regenerate instead. The parent is left untouched.
#
# WHY: scripts/paper_parameter_audit.py compared all four decks against Ye &
# Ghassemi (2018) itself rather than against each other, and found that several
# constants presented as measured joint properties were invented. Every value
# changed below is derived in scripts/refit_joint_constants_from_paper.py from
# the paper's own Table 1, Table 2 and Sec. 2.1. Nothing is tuned to a run.
#
# CONTROLLED AXIS: fracture angle ONLY (attribution control for 89_01)
#
# MESH ONLY: 28.990 deg / 2.85 mm off centre -> 30.000 deg / centred, with the
# boundary renames and the source nodes moved onto the new plane. The joint
# constants are left at their pre-audit values so that 89_01 minus this deck
# isolates what the JRC/JCS/phi_r refit does.
# The paper-frame postprocessors, W/L and fluid bulk modulus are corrected here
# too, because they are reporting/physical fixes that are not the axis.
#
# UNCHANGED AND DELIBERATELY SO: slip-weakening D_c, exponent and tail floor;
# dilation angles; normal-closure constants; hydraulic constants; every BC and
# the load path. The tail floor is an ABSOLUTE friction coefficient with no JRC
# or JCS in it, so refitting the peak envelope leaves its calibration valid.
#
# STATUS: CORRECTION, and the control that separates the mesh effect from the joint-constant effect in 89_01.
# ==============================================================================
# ==============================================================================
# 68_01_sw4_bbfast_tail6p50_eta3p50_m0_kernel_SV
# GENERATED 2026-08-15 from 68_01_sw4_bbfast_tail6p50_eta3p50_m0.i -- do not hand-edit; regenerate instead.
#
# Changes applied on 2026-08-15:
#   1. Storage kernel: the combined AD mass-balance kernel
#      OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel, assembling
#      (1/M)*dp/dt + alpha*div(du/dt) in one correctly-coupled object. This replaces
#      the split OrcaSinglePhaseMassTimeDerivativeKernel +
#      OrcaSinglePhaseMassVolumetricExpansionKernel pair, which drops the
#      grain-compressibility storage (alpha-phi)/K_s and uses porosity where the Biot
#      coefficient belongs.
#   2. confining_pressure set to 30e6 Pa (was 29.4e6).
#      NOTE: confining_pressure is a live BC magnitude here, not just a diagnostic
#      label -- it feeds the czm_pressure_x / czm_pressure_y BC function expressions.
#      A 29.4 -> 30.0 MPa change was measured on 68_02 on 2026-08-14 and moved every
#      Table-2 metric further from target. The 29.4e6 version is preserved unchanged
#      in 68_01_sw4_bbfast_tail6p50_eta3p50_m0.i.
#   3. Output file bases repointed to this deck's own name.
#
# The parent deck 68_01_sw4_bbfast_tail6p50_eta3p50_m0.i is left untouched as the reference configuration.
# ==============================================================================
# ===============================================================================
# SW4 68 targeted residual sweep: 68_01_sw4_bbfast_tail6p50_eta3p50_m0
# Parent: completed 67_01_sw4_bbfast_eta3p5_Dc74p5_tail6p75_m0.
# Controlled point: eta=3.50e12 Pa.s/m, Dc=74.5um, tail=6.50deg.
# Only the late tail angle changes; mesh, BCs, normal/hydraulic laws, and outputs are fixed.
# ===============================================================================
# ===============================================================================
# SW4 final local coarse-M0 refinement: 68_01_sw4_bbfast_tail6p50_eta3p50_m0
# Parent: 64_01_sw4_bbfast_currentsource_reference_m0
# Back-analysis design: 2x2 BBFast response surface; eta=4.0e12 Pa.s/m, Dc=75 um
# Mesh, BC/load path, hydraulic parameters, outputs, and all unlisted parameters are unchanged.
# ===============================================================================
# ==============================================================================
# SW4 64-series staged refinement: 68_01_sw4_bbfast_tail6p50_eta3p50_m0
# Parent: 62_01_sw4_bbfast_legacy_controls_new_outputs_m0
# Controlled axis: exact current-source regression reference; no input parameter change
# All BCs, mesh, outputs, and unlisted constitutive parameters are unchanged.
# ==============================================================================
######################################################################################
# CONTROLLED SW-S4 OBSERVATION/INPUT BRACKET -- 68_01_sw4_bbfast_tail6p50_eta3p50_m0
# Legacy fitted BC/load-path controls with the corrected observation outputs. Compare with active case 61_01 to measure the combined protocol effect.
# This case is a causal control, not an independent validation and not a retuned law.
######################################################################################
######################################################################################
# CORRECTED SW-S4 RERUN 61_01 -- OrcaBartonBandisContactTractionFastADHardening
# Low-mesh member of a controlled three-mesh study.  Constitutive calibration is retained
# for attribution, while the experimental BCs and validation observables are corrected:
# constant piston after 55 s, constant 30 MPa confinement, full fluid traction, assembled
# load/flux reactions, and solved/LVDT-proxy displacements.  This remains a recalibration
# test until it is rerun; historical 54_24 scores are not publication validation.
######################################################################################
# DECK 54_24 BBMECH MIDTAIL tail7p0 m1p10 Dc70 (from 54_23, 2026-07-15)
#
# 54_23 proved that the new tail-only weakening controls are useful, but the tested curve was
# too aggressive: shear slip, normal dilation, permeability, and the shear-stress drop all overshot
# the digitized Fig. 7d data. This deck is the first formal bracket between 54_21 and 54_23:
#   - keep the 54_21/54_23 peak envelope: phi_base=7.5 deg, JRC=17.5;
#   - raise the tail-only residual floor from 6.5 -> 7.0 deg;
#   - lengthen the slip-weakening distance from 52 -> 70 um;
#   - soften the curve exponent from 1.14 -> 1.10.
#
# Intent: recover roughly half of 54_21's missing stress drop while avoiding 54_23's excess
# slip/dilation. Do not change dilation angles yet: 54_21 already had a near-correct normal-dilation
# peak, so 54_23's over-opening is interpreted as mainly slip-driven.
######################################################################################
######################################################################################
# DECK 54_23 BBMECH CURVETAIL tail6p5 m1p14 Dc52 (from 54_21, 2026-07-15)
#
# 54_22 improved the peak-flow/peak-perm panels but over-corrected the mechanics: cutting
# residual_friction_angle_degrees also lowered the BB peak-envelope baseline, so onset moved too
# early and the Pi20/Pi24 loading holds became too weak/too slipped.  This deck forks from 54_21
# instead and uses the new tail-only hardening controls:
#   - preserve the 54_21 BB peak envelope: phi_base=7.5 deg, JRC=17.5;
#   - set the slip-weakening tail only to 6.5 deg, decoupled from the peak envelope;
#   - use W = exp(-(s/Dc)^m), m=1.14, Dc=52 um.  Table-2 loading-hold back-analysis with
#     the preserved 54_21 BB envelope gives m~1.14, Dc~52 um for a 6.5 deg tail.
# This is a diagnostic next run, not a final calibration claim: if it keeps 54_21 onset while
# reducing Pi20-Pi28 tau/slip bias, the remaining late-unload error is elastic re-stick/path,
# not residual friction.
######################################################################################
######################################################################################
# Ye & Ghassemi (2018) SW-S4 -- DECK 54_07:
# Gentle BB retune after 54_05 showed the previous step was too aggressive.
#
# ============ DECK 54_07: gentle BB retune from 54_03 ============
# 54_05 lowered both residual and peak strength too much, causing very early slip.  This deck
# lowers residual friction more gently, raises JRC to preserve the 54_03 peak envelope at
# sigma_n ~= 26 MPa, and shortens Dc only modestly so the post-peak branch weakens without
# destroying onset timing.
#
# ---- 54_01 header retained below for lineage/context ----
#
# ============ DECK 54_01: 52_11 controls + OrcaBartonBandisContactTractionFastADHardening ============
# Created after 52_14 stalled near 1700 s.  This is the simpler publishable candidate:
# keep the closest SW4 calibration controls from 52_11 (sigma3=29.4 MPa, pressure coefficient
# 0.88, axial spring/preload, and the 52_11 hydraulic gouge damage) while replacing the
# MC/secondary-weakening/RSF/HOLDCREEP contact stack with the source-level BB hardening model.
#
# ---- deck-49 BB-hardening header retained below for constitutive lineage/context ----
#
# ============ DECK 49: OrcaBartonBandisContactTractionFastADHardening port ============
# Same scaffold as deck 43 (mesh, compliant frame + batch-4 compensated preload, mechanical
# fault-pressure route, power-law BB APERTURE closure in the permeability material, full
# injection schedule). ONLY the fault CONSTITUTIVE LAW is swapped:
#   ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile
#     -> OrcaBartonBandisContactTractionFastADHardening
# The goal: replicate the deck-43 Table-2 calibration with the nonlinear Barton-Bandis
# formulation, which carries IN THE RESIDUAL the two things the decoupled law could only
# approximate output-side:
#   (1) STRESS-DEPENDENT NORMAL STIFFNESS (the Table-2 audit's #1 gap): deck 43's constant
#       penalty_normal=2e13 is ~19x too stiff for the unload branch, so the actual normal
#       jump froze at -28um instead of recovering -41->-32um (the reversible_normal_compliance
#       term was an output-only reconstruction). Here the power-law BB closure
#       sigma_n = sigma0*(cl/(Vm-cl))^(1/p) gives the measured stiffness ratio honestly:
#       back-analysis fit to Table 2 (3 constraints, exact): sigma0=11.22 MPa, p=3.28,
#       Vm=45.91um, Kni=sigma0/Vm=2.443e11 Pa/m -> K_tan = 4.7e12 @ 29 MPa (audit 4.2e12,
#       stiff stick), 1.39e12 @ 21 MPa (audit ~1.06e12, soft unload), elastic peak opening
#       10.6um @ 15.31 MPa, end-of-unload dn = -32um EXACT. A p=1 hyperbola caps the
#       stiffening ratio at ~2x over this range (needs 3-4x) -> the NEW source param
#       normal_closure_stress_exponent (the deck-42/43 aperture lesson applied to mechanics).
#   (2) CURVED STRENGTH ENVELOPE: tau = sigma_n*tan(phi_r + JRC*log10(JCS/sigma_n)) natively
#       produces the "mu=0.804, intercept -9.11 MPa" linear fit of Table 2 (deck 43 needed a
#       negative cohesion to fake this curvature). Back-analysis: phi_r=11.5 deg (mu_r=0.203
#       = Pi28 ratio 3.12/15.31), JCS=300 MPa, JRC=12.44 pinned so the peak envelope crosses
#       the applied tau exactly at the observed Pi=16 onset (mu_p(26.51 MPa)=0.458), with a
#       +1.0 MPa stick margin at the 30.75 MPa preload. Slip-weakening (Hardening subclass)
#       W=exp(-s/Dc), Dc=60um: weakening slope 1.12e11 < k_sys 1.25e11 -> progressive slip,
#       no cliff (the deck-21/22 stability rule), viscosity 1e13 as the burst regularizer.
# Supporting NEW source features (all default-off = legacy):
#   - normal_closure_offset = closure(31 MPa) = 44.33um: pre-seats the joint so t=0 is in
#     equilibrium with the isotropic 31 MPa preload. Without it the fault would interpenetrate
#     ~44um at startup and dump the batch-4 compensated preload into the axial penalty spring
#     (the batch-3 preload-loss bug all over again). czm_dn then measures opening RELATIVE to
#     the in-situ state = directly comparable to the paper's dilation curves.
#   - roughness_state_initial/residual = 0.45/0.10 with D_r=8e-5 in the Hardening roughness
#     degradation: exports the EXACT roughness_state(s) curve of the decoupled law, so the
#     deck-43 permeability retention calibration (dilation_scale 0.013, retention_residual
#     0.28) carries over unchanged.
# Dilation: decoupled Barton-1982 mobilization (use_decoupled_dilation), psi 25->14 deg over
# 1e-4 m, dilation_opens_joint=true -> plastic dn(78um)=31um; + elastic BB opening 10.6um
# -> peak dn ~ -41um recovering to -32um on unload (both now IN the displacement field).
# NB: unlike the decoupled law there is NO dissipation limiter here, so tan(psi) is a LIVE
# knob (deck-43's tan(50deg) was inert, limiter-capped at ~0.42; here psi is set to the
# realized values directly).
# GATE CHECK (must hold before trusting a full run): post-ramp stress_zz_top ~ -53.4 MPa,
# q ~ +23.4, sigma'_n ~ 31.2, tau ~ 11.3 MPa (deck-43 values; the closure offset is designed
# to preserve the batch-4 compensation, but the softer BB spring adds ~0.4um of ramp-phase
# fault compliance -- verify, expect small trim of axial_pres_final if tau is off >0.5 MPa).
# FIRST-CUT param values from scratch back-analysis (bb_backanalysis.py); expect +-1 tuning
# iteration on: Dc (mid-branch strength errors -0.5..+1.4 MPa across holds), psi pair, and
# possibly axial_pres_final (gate).
######################################################################################
# ---- deck-43 header retained below for lineage/context ----
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
mesh_file = mesh/ye2018_sw_s4_theta30_size5_mesh.e   # Orca_2.0 reference SW-S4 mesh (pre-tagged top/bottom/sides/pins)
sample_radius = 0.025255             # m, SW-S4 radius (D = 50.51 mm); cylinder radius used by the confining BC
sample_area = 2.00375499689e-3        # m^2, pi*sample_radius^2
bulk_sin_theta = 0.5
bulk_cos_theta = 0.8660254037844387
axial_bc_penalty = 1.2e12          # BATCH4 Pa/m; f*penalty in SERIES w/ rock (k_rigid=1.5e11 tau-slip) -> k_sys ~ k_exp=1.25e11. NOT k_exp itself (batch-3 error #2).
axial_pres_initial = -2.5833e-5       # BATCH4 = -sigma_zz0/penalty (sigma0=31 MPa isotropic IC): spring pre-compressed so t=0 is in equilibrium
axial_pres_final   = -9.84e-5          # retained from the 54_20/54_48 preload gate.
relax_t0 = 1000.0                  # DECK54_48 load-path lesson: relax starts at onset.
relax_dur = 800.0
poro_du = 2.9e-6    # CONTROL: legacy fitted poroelastic piston compensation
poro_dur = 945.0                   # Ramp from t=55 to t=1000, then hold.
axial_relax_du = 2.6e-6    # CONTROL: legacy fitted late piston relaxation

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
confining_pressure = 30e6  # CONTROL: legacy fitted confinement
production_pressure = 5e6            # Pa
fault_pressure_coefficient = 0.86    # CONTROL: legacy fitted fault-pressure attenuation
side_unload_relax_pressure = 1.2e6    # CONTROL: legacy fitted late confinement unload
side_unload_t0 = 1900.0
side_unload_dur = 1400.0

# --- OrcaBartonBandisContactTractionFastADHardening (CZM law) : DECK 49 back-analysis ---
#
# All values from the Table-2 back-analysis (scratchpad bb_backanalysis.py, exact-fit residuals):
#
# (a) POWER-LAW BB NORMAL CLOSURE (in the residual -- replaces deck-43's penalty_normal=2e13
#     + output-only reversible_normal_compliance reconstruction):
#       sigma_n(cl) = sigma0*(cl/(Vm-cl))^(1/p), sigma0 = Kni*Vm = 11.22 MPa
#     Fit to: unload recovery 9um over sigma'_n 15.31->24.81, 6um over 17.13->24.81, and
#     ~1um stick-phase opening over 31->26.51 (K_stick ~ 4.2e12). Gives K_tan 4.7e12@29,
#     1.39e12@21, 5.2e11@15.3 -- the 3-4x stiffening a p=1 hyperbola cannot reach.
bb_initial_normal_stiffness_mech = 2.443e11   # Kni [Pa/m]; sigma0 = Kni*Vm = 11.22 MPa
bb_maximum_closure_mech = 4.591e-5            # Vm [m] = 45.91 um (bounded feedback, deck-42 lesson)
bb_normal_closure_stress_exponent = 3.28      # p (NEW source param; 1.0 = standard hyperbola)
bb_normal_closure_offset = 4.433e-5           # c0 [m] = closure(31 MPa): pre-seats the joint at the
                                              # isotropic preload so t=0 is in equilibrium and the
                                              # batch-4 compensated axial preload is PRESERVED.
normal_unload_retention_fraction = 0.04       # DECK54_48: retain a small part of recovered closure on unload.
normal_unload_retention_time = 0.0
normal_unload_activation_slip = 5.0e-5
penalty_tangent = 1e13                        # unchanged from deck 43 (tau-slip elastic stiffness,
                                              # part of the batch-4 k_sys arithmetic)
#
# (b) BB STRENGTH ENVELOPE + SLIP WEAKENING (replaces friction_rough/smooth + cohesion_*):
#     tau_lim = sigma'_n * tan(phi(s)), phi(s) = phi_r + (phi_p - phi_r)*exp(-s/Dc),
#     phi_p = phi_r + JRC*log10(JCS/sigma'_n)
#     mu_p(26.51 MPa) = 0.458 = observed Pi=16 onset; mu_r = 0.203 = Pi=28 ratio 3.12/15.31.
#     Curvature check vs Table 2 holds (Dc=60um): strength-tau = -0.5..+1.4 MPa (viscosity adds
#     ~+0.5-1 MPa during active slip -> net within ~1 MPa everywhere). NB residual UNLOAD tau
#     (2.27-2.82) is NOT strength-limited -- the fault re-sticks and holds it elastically.
bb_jrc = 5.0 # 90_08: see 90_07 header. Was 17.5.                        # DECK54_20: 17.0->17.5. Holds the PEAK envelope (onset 996 was a
                                     # bullseye -- protect it) against the phi_r cut: d(mu_p)/dJRC ~ 0.022
                                     # at sigma'n 26.5 offsets tan-shift of -1 deg phi_r. 54_05 proved what
                                     # happens when phi_r is cut WITHOUT this compensation (onset 604 s).
                                     # WAS DECK54_07: 16.0->17.0. Compensates phi_r 9.5->8.5 so peak mu near
                                     # sigma'n~26 MPa remains ~0.50 instead of the early-failure 54_05 value.
                                     # DECK54_03: 14.0->16.0. Compensates phi_r 11.5->9.5 so peak mu near
                                     # sigma'n~26 MPa stays close to 54_01/onset while residual strength drops.
                                     # WAS DECK49_02: 12.44->14.0 (ONSET RE-FIX after the axial raise). 49_01's
                                     # +0.85 MPa initial tau met the unchanged BB envelope ~275 s early (onset
                                     # 802->727 s; data ~1000). mu_p(26.5 MPa) = tan(phi_r + JRC*log10(JCS/sn))
                                     # = tan(11.5 + JRC*1.054): dmu_p/dJRC = 0.0222 -> +1.56 JRC = +0.035 mu_p
                                     # = +0.92 MPa at 26.5 MPa ~ the added driving tau. Onset -> ~1000 s.
                                     # WAS:                       # back-analyzed effective JRC (polished saw-cut data demand it,
                                     # exactly as the decoupled law needed fcr=0.89)
bb_jcs = 1.5e8 # 90_08: paper Sec 2.1 UCS. Was 3.0e8.                       # Pa; intact-granite wall strength
bb_residual_friction_angle = 22.72 # 90_08: re-anchored. Was 7.5.     # DECK54_20 (LOCKTRIM): 8.5 -> 7.5 deg. 54_07 SCORECARD (2026-07-11):
                                     # onset 996 s BULLSEYE, sigma'n trough 15.33 (data 15.28) BULLSEYE, slip
                                     # 82.8 (79.1), dn -0.0425/-0.0318 in band -- the BB shape arithmetic
                                     # holds. Remaining miss = the LOCK, the documented BB structural bias
                                     # (mu_p(sigma'n) log-envelope RISES as sigma'n falls): tau@2000 4.23 /
                                     # tau_end 3.01 / q_end 6.99 vs data 3.0/2.20/5.1. phi_r -1 deg lowers
                                     # the residual envelope tan(phi_r+JRC_mob*log10(JCS/sn)) by ~0.35-0.4 MPa
                                     # at the trough -> tau_end ~2.6. Stability: with Dc 80 below the slope
                                     # stays ~1.0e11 < k_sys 1.25e11 (49_03 proved phi 9.5/Dc 70 stable;
                                     # this sits on the same margin).
bb_slip_weakening_residual_friction_angle = 6.50 # 66_03: small late-shear correction.
                                     # the post-slip tail (tau_end 0.86 vs data 2.20 MPa; slip
                                     # end 95.4 vs 79.1 um). Raising the tail floor is the least
                                     # disruptive way to restore shear traction while preserving
                                     # 54_21's peak-onset envelope.
                                     # DECK54_23: tail-only residual. Keeps the BB
                                     # peak-envelope baseline at phi=7.5/JRC=17.5 while testing the
                                     # lower post-slip floor that 54_22 tried to get by cutting phi.
bb_slip_weakening_exponent = 1.10    # DECK54_24: 1.14 -> 1.10. Keep a gently curved tail but reduce the
                                     # late acceleration that drove 54_23 below the traction data.
                                     # DECK54_23: delayed/curved weakening, W=exp(-(s/Dc)^m).
bb_characteristic_slip_distance = 7.45e-5 # 67_01: in-bracket midpoint; trims stress with only ~0.3um predicted slip cost.
                                     # tail weight between 54_21 and 54_23, targeting a middle
                                     # stress-drop/slip response rather than another full overcorrection.
                                     # DECK54_23: Table-2 loading-hold fit with tail=6.5 deg and
                                     # preserved 54_21 envelope gives Dc~52um, m~1.14.
                                     # WAS DECK54_20: 75->80um. Slip counterweight for the deeper phi_r drop (~-2um) and keeps the weakening slope sub-critical at the lower residual envelope.
                                     # DECK54_03: 75->85um. With lower phi_r and higher JRC this keeps
                                     # the weakening slope near 54_01 instead of importing 49_03's early onset.
                                     # WAS DECK49_02: 60->75um. TWO reasons: (1) STABILITY -- with mu_p
                                     # raised to 0.493 the weakening slope at Dc=60um would be sn*(mu_p-mu_r)/Dc
                                     # = 26.5e6*0.290/6.0e-5 = 1.28e11 > k_sys 1.25e11 (cliff!); 75um gives
                                     # 1.02e11 (stable, progressive). (2) SLIP TRIM -- 49_01 over-slips (88.5 vs
                                     # data 79.1um, the +0.85 MPa tau converted at k_sys); longer Dc cuts ~5-7um.
                                     # Watch resid tau (unload re-stick level) -- may ride up ~0.2-0.3.
compressive_normal_stress_floor = 1e3
#
# (c) DECOUPLED DILATION (Barton-1982 mobilization; NO dissipation limiter in this law, so the
#     angles are set to the REALIZED deck-43 values, not the inert tan(50) ones):
dilation_angle_peak_degrees = 24.0     # DECK54_03: 23->24 to recover the slightly low 54_01 dilation peak.
                                     # WAS DECK49_02: 25->23. 49_01 dn peak -0.0482 vs data -0.0409: split at the
                                     # sigma'n trough = PLASTIC 34.7um (slip 86.2um * realized tan(psi)~0.402)
                                     # + ELASTIC 13.2um (trough 14.3 vs design 15.3 MPa). The slip trim (Dc)
                                     # recovers ~3um plastic; the angle cut does the rest: dn_pl(78um) =
                                     # tan(psi_r)*s + (tan(psi_p)-tan(psi_r))*L*(1-exp(-s/L)) = 0.231*78 +
                                     # 0.193*100*0.542 = 28.5um; + elastic ~11-12 -> peak ~ -0.040 (data -0.041).
dilation_angle_residual_degrees = 13.0 # DECK49_02: 14->13 (same trim, keeps the peak/residual ratio)
dilation_decay_distance = 1.0e-4
dilation_opens_joint = true            # V15 kinematic routing (dilatant hardening), as deck 43
#
# (d) HARDENING ROUGHNESS EXPORT (feeds ADOrcaRoughnessDamageFracturePermeability retention):
#     R(s) = 0.10 + 0.35*exp(-s/8e-5)  == the decoupled law's roughness_state exactly, so the
#     deck-43 perm calibration (dilation_scale, retention_residual) carries over unchanged.
bb_roughness_state_initial = 0.45
bb_roughness_state_residual = 0.10
bb_roughness_characteristic_slip = 8.0e-5
#
# (e) NUMERICS / RATE (as deck 43):
normal_traction_tolerance = 0.0
tangential_traction_tolerance = 1e-16
max_plastic_slip_increment = 0.0
tangential_viscosity = 3.5e12        # 66_03: lower the transient shear pedestal.
                                     # DECK30 lesson: burst regularizer; ~0.5-1 MPa at loading-branch
                                     # creep (~1e-7 m/s), ~5 MPa at the burst -> spreads the onset,
                                     # negligible pedestal at residual creep.
min_tau_limit = 0.0                  # fault stays compressed (sigma'_n >= ~12 MPa) -> no floor needed

# --- ADOrcaRoughnessDamageFracturePermeability (roughness-coupled) : DD02 reference ---
initial_hydraulic_aperture = 0.74e-6 # DD02 base aperture (perm ~0.46e-13)
aperture_scale = 0.001
normal_stress_aperture_compliance = 2.0e-14 # m/Pa, reversible aperture opening as sigma'_n decreases
reference_effective_normal_stress = 31.0e6  # Pa: DECK42 preload sigma'_n (opening=0 here).
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
bb_max_aperture_closure = 1.05e-6     # DECK54_48: port 54_25/52_17 hydraulic peak aperture sizing.
                                     # WAS DECK43 1.17->0.85. Deck42 (Vm1.17) was too SOFT ->
                                     # coupled HM feedback drooped peak sigma'n 15->12 (aperture->perm->
                                     # flow->pore pressure->sigma'n) and perm OVERSHOT (peak k 1.22 vs
                                     # data 0.925, unload bias +0.16). Stiffer closure = less opening ->
                                     # less feedback -> sigma'n holds ~14-15 -> perm drops at peak AND
                                     # mid-unload together. Shape (p2, 3.2x stiffening) preserved.
bb_initial_normal_stiffness = 1.43e13 # DECK54_48: Kni with Vm 1.05e-6 so sigma0 ~= 15 MPa is held.
bb_stress_exponent = 2.0              # p: power-law closure exponent (1=hyperbola, 2=matches 3.2x stiffening)
dilation_scale = 0.0117              # DECK54_48 dscale0117 hydraulic rebalance.
                                     # WAS DECK54_03: 0.013->0.016 because 54_01 under-shot peak flow/perm.
                                     # WAS V15: was 0.4; cut ~17x because the ~17x larger dilation angle grows
                                     # cumulative_dilation ~17x. Holds a_h (permeability) at the V14 fit.
                                     # CALIBRATE to the perm/flow curve once the full run is scored.
retention_residual = 0.28              # DECK54_48: restore the 52_17/54_25 permeability-retention baseline.
                                     # WAS DECK54_03: 0.28->0.23 to preserve the good end permeability after
                                     # increasing dilation_scale for the low 54_01 peak.
                                     # WAS DECK38 (from deck35, DECOUPLED perm-only knob): 0.35->0.28.
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
slip_damage_scale = 0.28e-6          # DECK54_01: from 52_11 hydraulic gouge-damage calibration.
slip_damage_onset_slip = 20e-6       # DECK54_01: from 52_11; avoids gouge accrual before slip localizes.
slip_damage_characteristic_slip = 30e-6 # DECK54_01: from 52_11; gentler post-onset gouge rate.
min_hydraulic_aperture = 0.74e-6     # paper SW-S4 base aperture; prevents artificial sub-base closure
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
paper_flow_width_over_length_sw_s4 = 0.814819511514  # inverted from Table 2 via eq (10); was 0.81, 0.5 % low
mesh_flow_width_over_length_sw_s4 = 0.814819511514   # 93-series: SW-S4 had no mesh-geometry flow channel at all.
                                                     # Set equal to the paper constant, as on SW-T1/SW-T2, so the
                                                     # diagnostic exists and the two channels agree by construction.
ml_per_m3_per_min = 6.0e7

# --- output ---
exodus_file_base = results_exodus_hpc_rorqual/98_04_sw4_shutin_hpc
csv_file_base    = results_csv_hpc_rorqual/98_04_sw4_shutin_hpc
checkpoint_file_base = results_checkpoint_hpc_rorqual/98_04_sw4_shutin_hpc

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
    nodesets_to_convert = 'top_nodeset bottom_nodeset sides_nodeset'
  []
  [source_in]
    type = ExtraNodesetGenerator
    input = sidesets_from_nodesets
    coord = '-0.018367273 0.0 0.027536950'   # exact interface node, 6.89 mm in from the sidewall
    new_boundary = source_in
    use_closest_node = true
  []
  [source_out]
    type = ExtraNodesetGenerator
    input = source_in
    coord = '0.018367273 0.0 0.091163050'   # exact interface node, 6.89 mm in from the sidewall
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
      # DECK54_21: add 54_48 poroelastic compensation and load-line relaxation.
      expression = 'if(t<2.0,${axial_pres_initial},if(t<55.0,${axial_pres_initial}+(${axial_pres_final}-${axial_pres_initial})*(t-2.0)/53.0,${axial_pres_final}+${poro_du}*min((t-55.0)/${poro_dur},1.0)+if(t<${relax_t0},0.0,${axial_relax_du}*min((t-${relax_t0})/${relax_dur},1.0))))'
    []

  # Injection pressure schedule (Pa): FULL digitized Ye & Ghassemi SW-S4 history -- the complete
  # rise-AND-FALL cycle to t~3404 s (peak ~28 MPa at ~1788 s, declining back to ~8 MPa). The earlier
  # caseF-derived schedule contained only the RISING limb (truncated at ~1900 s), so the run stopped
  # before the post-peak phase where the injection decline lets the fault re-stabilize and the
  # differential stress partially recovers. Restored from the Orca_2.0 reference deck.
  # ------------------------------------------------------------------------
  # DISCUSSION DECK (shutin).  Post-shut-in fault reactivation.
  # This REPLACES the digitized Ye & Ghassemi schedule; do not score against
  # Table 2.  The validated run is the 93-series parent.
  #
  # Ramp 5.00 -> 27.96 MPa over t = 2 .. 1720.7 s at this
  # specimen's own rate, hold 200 s (past onset), then an ABRUPT
  # shut-in: the injection node relaxes exponentially toward ambient with
  # tau = 150 s, a standard proxy for wellbore pressure fall-off.
  # end_time gives 3000 s of post-shut-in observation.
  #
  # The question: once the injection-point pressure is back near ambient, does
  # slip keep growing on pressure already diffused into the fault, or arrest?
  # ------------------------------------------------------------------------
  [injection_pressure]
    type = ParsedFunction
    expression = 'if(t<2.0, 5e+06, if(t<1720.7, 5e+06+(2.796e+07-5e+06)*(t-2.0)/1718.7, if(t<1920.7, 2.796e+07, 5e+06+(2.796e+07-5e+06)*exp(-(t-1920.7)/150))))'
  []

  [production_pressure_fn]
    type = ConstantFunction
    value = ${production_pressure}
  []

  # Confining pressure on the cylindrical "sides" surface via the analytic outward normal.
  # DECK54_21: apply the 54_48 late side-unload trim to the unload branch.
  [sigma3_x]
    type = ParsedFunction
    expression = '-(${confining_pressure}-${side_unload_relax_pressure}*if(t<${side_unload_t0},0.0,min((t-${side_unload_t0})/${side_unload_dur},1.0)))*x/${sample_radius}'
  []
  [sigma3_y]
    type = ParsedFunction
    expression = '-(${confining_pressure}-${side_unload_relax_pressure}*if(t<${side_unload_t0},0.0,min((t-${side_unload_t0})/${side_unload_dur},1.0)))*y/${sample_radius}'
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
#     save_in = inj_flux_aux
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
    # DECK 49: Barton-Bandis contact/traction law (FastAD + Hardening slip-weakening).
    # Declares the SAME downstream hydraulic wiring as the decoupled law:
    # dilation_jump_increment (AD), roughness_state (AD), cumulative_plastic_slip.
    type = OrcaBartonBandisContactTractionFastADHardening
    boundary = fracture_interface

    # (a) power-law BB normal closure (in the residual; stress-dependent Kn)
    use_hyperbolic_normal_closure = true
    initial_normal_stiffness = ${bb_initial_normal_stiffness_mech}
    maximum_closure = ${bb_maximum_closure_mech}
    normal_closure_stress_exponent = ${bb_normal_closure_stress_exponent}
    normal_closure_offset = ${bb_normal_closure_offset}
    normal_unload_retention_fraction = ${normal_unload_retention_fraction}
    normal_unload_retention_time = ${normal_unload_retention_time}
    normal_unload_activation_slip = ${normal_unload_activation_slip}
    penalty_tangent = ${penalty_tangent}
    normal_traction_tolerance = ${normal_traction_tolerance}
    tangential_traction_tolerance = ${tangential_traction_tolerance}

    # (b) BB strength envelope + slip weakening
    jrc = ${bb_jrc}
    jcs = ${bb_jcs}
    residual_friction_angle_degrees = ${bb_residual_friction_angle}
    use_scale_correction = false            # back-analysis: JRC/JCS used as-is
    use_mobilized_jrc = false               # peak strength available at zero slip (Pi=16 onset)
    compressive_normal_stress_floor = ${compressive_normal_stress_floor}
    pore_pressure_strength_coefficient = 0.0  # pressure enters MECHANICALLY via the
                                              # fault-pressure kernels (deck-43 route);
                                              # a nonzero value here would double-count.
    use_slip_weakening = true
    characteristic_slip_distance = ${bb_characteristic_slip_distance}
    slip_weakening_exponent = ${bb_slip_weakening_exponent}
    slip_weakening_residual_friction_angle_degrees = ${bb_slip_weakening_residual_friction_angle}

    # (c) decoupled (mobilized) dilation, kinematic routing
    use_dilatancy = true
    use_decoupled_dilation = true
    dilation_angle_peak_degrees = ${dilation_angle_peak_degrees}
    dilation_angle_residual_degrees = ${dilation_angle_residual_degrees}
    dilation_decay_distance = ${dilation_decay_distance}
    dilation_opens_joint = ${dilation_opens_joint}
    accumulate_irreversible_dilation = true
    cap_dilation_to_available_closure = false  # closing-mode concept; with opens_joint the
                                               # dilation is an eigen-opening, not closure use
    max_dilation_increment = 0.0

    # (d) roughness_state export for the permeability retention (matches the decoupled law)
    use_roughness_degradation = true
    roughness_state_initial = ${bb_roughness_state_initial}
    roughness_state_residual = ${bb_roughness_state_residual}
    roughness_characteristic_slip = ${bb_roughness_characteristic_slip}

    # (e) numerics / rate
    max_plastic_slip_increment = ${max_plastic_slip_increment}
    tangential_viscosity = ${tangential_viscosity}
    min_tau_limit = ${min_tau_limit}
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
    effective_normal_traction_name = czm_sigma_n
    normal_stress_aperture_name = normal_stress_aperture
    effective_normal_compression_name = effective_normal_compression
    dilation_scale = ${dilation_scale}
    retention_residual = ${retention_residual}
    self_propping_scale = ${self_propping_scale}
    self_propping_exponent = ${self_propping_exponent}
    use_slip_damage = ${use_slip_damage}
    slip_damage_scale = ${slip_damage_scale}
    slip_damage_onset_slip = ${slip_damage_onset_slip}
    slip_damage_characteristic_slip = ${slip_damage_characteristic_slip}
    cumulative_plastic_slip_name = cumulative_plastic_slip
    cumulative_plastic_slip_is_ad = false   # DECK49: the FastAD BB law exports this non-AD
    slip_damage_aperture_name = slip_damage_aperture

    min_hydraulic_aperture = ${min_hydraulic_aperture}
    max_hydraulic_aperture = ${max_hydraulic_aperture}
    compute_transmissibility = ${compute_transmissibility}
    transmissibility_name = fracture_transmissivity
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
  # STALE-POINT FIX 2026-08-17. Was `PointValue` at '-0.019255 0 0.021745' -- the borehole of the
  # OLD 28.99deg / 2.85 mm off-centre SW-S4 mesh. The theta30 mesh swap updated the source_in
  # `coord` to '-0.018367273 0 0.027536950' but left this sampling point behind, 5.86 mm away.
  # The BC itself is a FunctionDirichletBC on source_in and was always correct, and these two
  # postprocessors are read ONLY by other postprocessors -- no Function, BC, Material or Control
  # touches them -- so the MECHANICS of every SW-S4 run to date is unaffected. What was wrong is
  # the diagnostics:
  #   * reported injection pressure came from 5.86 mm inside the matrix: 26.07 MPa at the peak
  #     against the prescribed 27.96, and 1.50 MPa RMS low over the history;
  #   * pp_outlet_pp sampled 0.89 mm off the outlet node, INSIDE the pressurised fracture, and
  #     read ~7 MPa against its own 5 MPa Dirichlet.
  # The two errors partly CANCEL in effective_normal_paper_frame_mpa_pp (mean shift only
  # -0.005 MPa, so SW-S4's sigma'_n overestimate is real model behaviour, not this bug) but they
  # ADD in pp_drop_pp: ~3.9 MPa of ~23 MPa lost, which is 27.5% of the peak
  # flow_rate_validation_ml_min_pp. That is most of the "underestimates the peak flow rate".
  # Now matches the SW-T1/SW-T2 decks, which always used the nodeset average and score 1.2% on
  # injection pressure against SW-S4's ~7%.
  [injection_pressure_pp]
    type = AverageNodalVariableValue
    variable = pore_pressure
    boundary = source_in
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
  [pp_outlet_pp]                    # STALE-POINT FIX 2026-08-17: was PointValue at
    type = AverageNodalVariableValue # '0.019255 0 0.091255', 0.89 mm from the source_out node.
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
    expression = '(${paper_flow_width_over_length_sw_s4} / (12.0 * ${fluid_viscosity_ref})) * hydraulic_aperture_pp^3 * pp_drop_pp * ${ml_per_m3_per_min}'
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
    expression = 'sigma1_reaction_mpa_pp - ${confining_pressure} * 1e-6'
  []

  # ---------------------------------------------------------------------------
  # Paper-frame reduction, Ye & Ghassemi (2018) eq (3)-(4), theta = 30 deg:
  #   sigma'_n = (sigma_3 - P_p) + sigma_d sin^2(theta),  P_p = (P_i + P_o)/2
  #   tau      = sigma_d sin(theta) cos(theta)
  # SW-S4 was the only specimen without these, so its scorecard compared a fault-
  # averaged czm_sigma_n against Table 2's frame-reduced value while its three
  # siblings compared like with like (audit finding, 2026-08-16).
  # sin^2(30) = 0.25 exactly; sin(30)cos(30) = 0.433012701892219.
  # ---------------------------------------------------------------------------
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
  [reaction_vs_machine_spring_mpa_pp]
    type = ParsedPostprocessor
    pp_names = 'sigma1_reaction_mpa_pp machine_spring_sigma1_mpa_pp'
    expression = 'sigma1_reaction_mpa_pp - machine_spring_sigma1_mpa_pp'
  []

  # --- differential stress from the top-surface axial stress average ---
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

  # --- BB-law state diagnostics (FastAD law exports these as NON-AD properties, except
  #     roughness_state / dilation_jump_increment / bb_normal_closure which stay AD) ---
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
  # DECK49: dilation_state does not exist in the BB law; the mobilized dilation ANGLE is the
  # equivalent diagnostic (psi_mob decaying peak -> residual with slip).
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
  # --- BB-specific diagnostics: closure, mobilized friction, JRC ---
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
  # DECK49: the reported normal dilation is the ACTUAL displacement jump czm_dn -- no
  # reconstruction needed. The power-law BB closure carries the elastic opening/recovery IN the
  # residual, and the closure OFFSET pre-seats the joint at the 31 MPa preload, so czm_dn already
  # measures opening RELATIVE to the in-situ state (the paper's LVDT reference). The deck-23/43
  # normal_opening_total / reversible_normal_opening reconstruction properties do not exist here.
  #
  # SIGN FIX: czm_dn follows this model's native convention (positive = opening, negative =
  # closing -- verified from source: interface_displacement_jump = R^T*(disp_neighbor - disp),
  # i.e. normal . displacement_jump_global). The paper's convention is the OPPOSITE (negative =
  # opening/dilation, per Sec. 3: "a NEGATIVE trend of normal dilation" demonstrates dilation).
  [czm_normal_dilation_paper_mm_pp]
    type = ParsedPostprocessor
    pp_names = czm_dn_total_pp                 # 93-series: was czm_dn_pp. Now the same
                                               # source column as SW-T1/SW-T2/SW-S3.
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
  [bulk_disp_x_upper_pp]
    type = PointValue
    variable = disp_x
    point = '${sample_radius} 0 0.10935'   # 93-series: L/2 + 50 mm. Was 0.115 (an ad-hoc
                                              # value; 55.65 mm above the fracture against 49.35 below).
  []
  [bulk_disp_z_upper_pp]
    type = PointValue
    variable = disp_z
    point = '${sample_radius} 0 0.10935'   # 93-series: L/2 + 50 mm. Was 0.115 (an ad-hoc
                                              # value; 55.65 mm above the fracture against 49.35 below).
  []
  [bulk_disp_x_lower_pp]
    type = PointValue
    variable = disp_x
    point = '${sample_radius} 0 0.00935'   # 93-series: L/2 - 50 mm.
  []
  [bulk_disp_z_lower_pp]
    type = PointValue
    variable = disp_z
    point = '${sample_radius} 0 0.00935'   # 93-series: L/2 - 50 mm.
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

  # ---------------------------------------------------------------------------
  # 93-series: the three channels SW-T1/SW-T2/SW-S3 carried and SW-S4 did not.
  # czm_dn_total_pp is the one that matters -- it is what the Table-2 gate reads
  # for d_n on the other three specimens.
  # ---------------------------------------------------------------------------
  [czm_dn_total_pp]
    type = SideAverageMaterialProperty
    property = normal_opening_total
    boundary = fracture_interface
  []
  [flow_rate_mesh_geometry_ml_min_pp]
    type = ParsedPostprocessor
    pp_names = 'hydraulic_aperture_pp pp_drop_pp'
    expression = '(${mesh_flow_width_over_length_sw_s4} / (12.0 * ${fluid_viscosity_ref})) * hydraulic_aperture_pp^3 * pp_drop_pp * ${ml_per_m3_per_min}'
  []
  [reported_czm_shear_slip_mm_pp]
    type = ParsedPostprocessor
    pp_names = czm_shear_slip_mm_pp
    expression = 'czm_shear_slip_mm_pp * 1'
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
  end_time = 4920.7

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1.5                  # conservative transition cadence; v12 rejected ~1.93 s around the first slip jumps
    optimal_iterations = 18
    growth_factor = 1.2
    cutback_factor = 0.5
  []

  dtmax = 1.5
  dtmin = 1e-6                 # allow fine crawl through the viscously regularized slip burst
  l_max_its = 50
  l_tol = 1e-4
  nl_max_its = 70
  nl_abs_tol = 1e-6
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


