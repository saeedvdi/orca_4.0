# ==============================================================================
# 67_11_sw4_mc_dS0p15_s28_w12_m0_kernel_SV_mesh3
# GENERATED 2026-08-15 from 67_11_sw4_mc_dS0p15_s28_w12_m0_kernel_SV.i -- do not hand-edit; regenerate instead.
#
# Change applied on 2026-08-15:
#   mesh_file: ye2018_sw_s4_size5_mesh.e -> ye2018_sw_s4_size3_mesh.e
#     size 3 is the FINER mesh: 8,640 -> 88,504 elements (10.2x).
#
#   The solver is a DIRECT one (-pc_type lu, MUMPS). Factorisation cost and
#   memory grow much faster than the element count, so this deck is an HPC
#   deck, not a local one -- see doc/TODO.md section H.
#
#   Source coordinates are re-pinned against this mesh by
#   scratchpad/repin_source_coords.py; they are NOT inherited blindly from the
#   mesh-5 parent, because ExtraNodesetGenerator searches the whole mesh and
#   runs before the fault split, so a coordinate that is merely near the
#   fracture can snap to a BULK node with no error at all.
#
# The parent deck 67_11_sw4_mc_dS0p15_s28_w12_m0_kernel_SV.i is left untouched.
# ==============================================================================
# ===============================================================================
# SW4 final-four coarse-M0 candidate: 67_11_sw4_mc_dS0p15_s28_w12_m0
# Parent: completed 65_11_sw4_mc_dS0p45_s36_m0.
# Retain fcs=0.055; use a late-only 0.15 MPa drop at 28um over 12um.
# The rejected 66 global-fcs axis is not imported because it corrupted pre-event stress.
# Mesh, BC/load path, hydraulic parameters, outputs, and all unlisted parameters are unchanged.
# ===============================================================================
# ==============================================================================
# SW4 64-series staged refinement: 67_11_sw4_mc_dS0p15_s28_w12_m0
# Parent: 63_11_sw4_mc_legacy_controls_powerlaw_normal_m0
# Controlled axis: secondary weakening magnitude only: 1.35 -> 0.75 MPa
# All BCs, mesh, outputs, and unlisted constitutive parameters are unchanged.
# ==============================================================================
# ==============================================================================
# SW4 mechanical-normal-closure validation: 67_11_sw4_mc_dS0p15_s28_w12_m0
#
# Single controlled change from its completed 62 legacy-control M0 baseline:
# replace the solved K_n=2e13 Pa/m linear contact penalty with the same pre-seated,
# recoverable power-law BB closure used by successful reference case 62_01.
# Friction, irreversible shear dilation, hydraulic aperture, BCs, mesh, and outputs
# are unchanged. Output-only reversible-normal reconstruction remains disabled.
# This case requires an orca-opt rebuilt from the accompanying source changes.
# ==============================================================================
######################################################################################
# CONTROLLED SW-S4 OBSERVATION/INPUT BRACKET -- 67_11_sw4_mc_dS0p15_s28_w12_m0
# Legacy fitted BC/load-path controls and legacy Kn with corrected observation outputs. Compare with 62_11 to measure the combined protocol effect at fixed Kn.
# This case is a causal control, not an independent validation and not a retuned law.
######################################################################################
######################################################################################
# CORRECTED SW-S4 RERUN 61_11 -- ADOrcaDecoupledDilationRoughness...CompressionTensile
# Low-mesh member of a controlled three-mesh study.  The fitted shear/hydraulic law is
# retained, but validation now uses exact experimental BCs, physical normal compliance,
# assembled reactions/fluxes, and solved/LVDT-proxy displacements.  Historical 52_25
# agreement must not be carried forward without this rerun.
######################################################################################
# DECK 52_25 MC DROPBRAKE fcs055 s44 w18 (from 52_24, 2026-07-15)
#
# 52_24 proved the AD decoupled path is basically right: pressure/flow/permeability
# improved and the stress-drop timing moved toward the validation curve. It over-shot
# the mechanical values, though:
#   - final slip reached ~85.5 um vs. data ~79.1 um;
#   - post-peak tau fell to ~1.6 MPa vs. data ~2.2 MPa;
#   - q after the drop was ~2.4 MPa too low;
#   - the run stopped at t ~= 3255 s, so late flat extrapolation should not be over-read.
#
# Diagnosis: 52_24 changed two strong hardening levers at once. The smooth residual
# friction cut 0.07 -> 0.04 was too large, and the secondary weakening onset 48 -> 40 um
# lets the cliff engage as soon as the model reaches the measured 40 um shelf. That makes
# the 1500--1700 s slip acceleration too strong and leaves the residual branch too weak.
#
# This deck keeps the 52_24 load path and hydraulic settings, but brakes the local AD
# hardening:
#   - friction_coefficient_smooth 0.04 -> 0.055, the midpoint implied by final slip/q
#     back-analysis of 52_23 vs. 52_24;
#   - secondary_weakening_onset_slip 40 -> 44 um, so the shelf is not immediately erased;
#   - secondary_weakening_distance 14 -> 18 um, spreading the cliff while retaining its
#     overall shape.
#
# No source change is used here. The backend already has the needed hardening knobs; the
# 52_24 error is a calibration overshoot, not a missing-law limitation.
######################################################################################
######################################################################################
# DECK 52_24 MC DROPBOOST fcs040 s40 dissm012 (from 52_23, 2026-07-15)
#
# 52_23 fixed the hydraulic/load-path side but still left the AD law mechanically too locked:
#   - shear slip ended 4.5 um low (74.6 vs 79.1 um);
#   - reported normal dilation peak was 5.2 um too shallow;
#   - shear traction stayed high after the drop (end +0.83 MPa; t=1400 +3.36 MPa).
#
# This deck keeps the 52_23 load path unchanged and retunes only local constitutive levers:
#   - friction_coefficient_smooth: 0.07 -> 0.04, sized from the deck's measured ~0.4 MPa
#     residual-tau movement per 0.015 smooth-friction change;
#   - secondary_weakening_onset_slip: 48 -> 40 um, so the second weakening stage engages closer
#     to the measured 40 um slip shelf instead of waiting for the model's delayed 48 um crossing;
#   - dissipation_margin: 0.16 -> 0.12, per the 52_22 falsifier note, to convert the recovered
#     slip into a little more solved plastic opening.
######################################################################################
######################################################################################
# DECK 52_23 MC 54_48LOADPATH poro2p9 srelax1p2 (from 52_22, 2026-07-14)
#
# Port of the load-path and hydraulic lessons from the best 54_48 cohesionless hybrid
# candidate into the AD decoupled dilation/roughness law.  This keeps the AD law's own
# roughness/RSF/friction calibration from 52_22, but applies the cross-model controls that
# should be constitutive-law agnostic:
#   - poroelastic axial compensation: poro_du = 2.9 um, held after t=1000 s;
#   - reduced post-onset axial relaxation: axial_relax_du = 2.6 um, preserving the 54_48
#     end-load-line retreat when combined with poro_du;
#   - late confining side-unload: side_unload_relax_pressure = 1.2 MPa over t=1900..3300 s;
#   - hydraulic dilation_scale = 0.0117, matching the 54_48 dscale rebalance.
#
# AD-specific choice: retain 52_22's relax_t0=1200 / relax_dur=600 timing because that
# deck explicitly delayed the relaxation past the AD first-yield dt crawl; the end state is
# still reached at the same trough window as 54_48.
######################################################################################
######################################################################################
# DECK 52_22 LOADRELAX2 (from 52_21, 2026-07-12, round 11): fix 52_21's numerical death.
# 52_21 DIED at t=1047: dt collapsed at t=994 (FIRST YIELD, before the relax was even
# active) and never recovered - the relax's negative dtau/dt landed inside the stick->slip
# branch transition (the marginal RSF b=0.016 @ visc 5e12 regime; 52_19 crossed the same
# crawl at dt 0.063 over t=994-1100 and RECOVERED by t=1100 because nothing was unloading).
# FIX (2 changes + relax retune):
#   relax_t0  1000 -> 1200 (starts AFTER the measured recovery of the onset crawl; slip ~10um,
#                           V ~ 4.5e-8 m/s, dt back at 1.5 s in 52_19)
#   relax_dur  800 -> 600  (full relaxation still reached at the sigma'n trough t~1800)
#   axial_relax_du 5.7e-6 -> 6.2e-6 and fcs 0.0825 -> 0.07 (see below): sized from the round-11
#   ARREST-POINT AMPLIFICATION law measured on 54_23 & SW3-v9: Delta_s = Delta_L/(k_sys - k_w),
#   k_w = local strength slope at arrest. MC k_w ~ 2.9e10 (R-tail 2.3e10 + TS tail 0.6e10) ->
#   ds/dL = 10.4 um/MPa. du 6.2um: dL 0.775 -> slip 87.1 - 8.1 = 79.0; fcs 0.0825->0.07 lowers the
#   arrest strength 0.17 MPa (data sits 0.2 below the model mu(s) tail at 79um: 52_19 tau_end 2.19
#   was AT 87um; S(79.7) ~ 2.40) -> +1.8um back = 80.8um and tau_end = L_end - k_sys*s = 2.20.
# PREDICT: completes t=3500 (relax outside the crawl window); onset ~1015 (fcs cut moves the
# PEAK envelope < 0.02 MPa - onset is fcr/R0-controlled); slip_end 80.8 +- 1.5; tau_end 2.20 +- 0.1;
# L_end 12.30; q_end ~5.0; trough ~14.6; dn_peak ~ -0.0386 (known -6%: plastic part scales with slip;
# recover next round via dissm 0.16->0.12 if slip lands).
# FALSIFIERS: dies again near onset -> the crawl is relax-independent, raise visc to 8e12 during
# a re-issue; slip < 78.5 -> MC k_w is larger than 2.9e10, recompute A from this run's own pair.
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
mesh_file = mesh/ye2018_sw_s4_size3_mesh.e   # Orca_2.0 reference SW-S4 mesh (pre-tagged top/bottom/sides/pins)
sample_radius = 0.025255             # m, SW-S4 radius (D = 50.51 mm); cylinder radius used by the confining BC
sample_area = 2.00375499689e-3
bulk_sin_theta = 0.5
bulk_cos_theta = 0.8660254037844387
axial_bc_penalty = 1.2e12          # BATCH4 Pa/m; f*penalty in SERIES w/ rock (k_rigid=1.5e11 tau-slip) -> k_sys ~ k_exp=1.25e11. NOT k_exp itself (batch-3 error #2).
axial_pres_initial = -2.5833e-5       # BATCH4 = -sigma_zz0/penalty (sigma0=31 MPa isotropic IC): spring pre-compressed so t=0 is in equilibrium
axial_pres_final   = -9.84e-5         # retained from the 52_22/54_48 preload gate.
relax_t0 = 1200.0                 # AD-specific carry-over from 52_22: starts after the first-yield dt crawl.
relax_dur = 600.0                 # Full relaxation still reaches the sigma'n trough window (~1800 s).
poro_du = 2.9e-6    # CONTROL: legacy fitted poroelastic piston compensation
poro_dur = 945.0                  # Ramp from t=55 to t=1000, then hold.
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
                                     # below to RAISE the differential stress q=sig1-sig3 at ~FIXED sigma'n.
                                     # Goal: model initial tau=11.46/q_fault=26.9 -> data tau=12.56/diff=29.2
                                     # (SAME theta=29.2deg, so q and tau move together). d(sigma'n)=cos^2*dsig3
                                     # +sin^2*dsig1 = 0.762*(-0.6)+0.238*(+1.8) ~= 0 -> sigma'n held ~31.
                                     # dq~+2.4 -> tau~+1.0 -> ~12.5. CAVEAT: higher tau drives the fault HARDER
                                     # -> earlier yield / more slip -> RE-VERIFY the preload gate (sigma'n~31,
                                     # q~29) and expect to re-trim Ld/load to hold slip 75-79um. This is the
                                     # HONEST fix for the low initial shear (vs deck45's empirical pcoeff).
production_pressure = 5e6            # Pa
fault_pressure_coefficient = 0.86    # CONTROL: legacy fitted fault-pressure attenuation
                                     # closure resize (Vm 0.85->1.05) fixed perm (k_peak 0.949 vs data 0.925)
                                     # but its aperture->perm->pressure->sigma'n feedback DUG THE TROUGH
                                     # 15.31 (52_13) -> 14.65 (data 15.28) and added +3.9 um slip (81.6 ->
                                     # 85.5). Lever: -0.02 pcoeff = +0.5 MPa sigma'n at peak injection ->
                                     # trough ~15.2-15.3 restored; slip -> ~82, k_peak -> ~0.90-0.91 (do NOT
                                     # retreat Vm), onset 984 -> ~1000-1010.
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
side_unload_relax_pressure = 1.2e6    # CONTROL: legacy fitted late confinement unload
side_unload_t0 = 1900.0
side_unload_dur = 1400.0

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
penalty_normal = 2.0e13    # legacy fallback only; mechanical response below is power-law
penalty_tangent = 1e13
use_hyperbolic_normal_closure_mech = true
initial_normal_stiffness_mech = 2.443e11
maximum_closure_mech = 4.591e-5
maximum_closure_fraction_mech = 0.999
normal_closure_stress_exponent_mech = 3.28
normal_closure_offset_mech = 4.433e-5
initial_roughness = 0.45
residual_roughness = 0.10
roughness_decay_distance = 1.15e-4   # DECK52_09: 120->115um, slip counterweight for the deeper TWOSTAGE
                                     # (~ -1.7um; predicted final slip 76.6 + 5-7 (TS) - 1.7 ~ 80-82 vs data
                                     # 79.1). dq/dt cost ~ -2.34 -> ~-2.45 (data -1.78) -- acceptable, the
                                     # tau(s) reshape below dominates the late panels. WAS DECK52_01: 95->100um (slip trim half of the fcs give-back). WAS DECK50: 80->95um. TWO targets: (a) deck46 over-slips (89.6 vs data 79.1um;
                                     # campaign dslip/dLd ~ -0.4um/um -> -6um) and (b) the post-onset weakening
                                     # slope is ~2x too steep (dq/dt 1100-1500 = -3.4 vs data -1.8 MPa/100s;
                                     # deck27 showed Ld 70->120 flattens tau@1300 5.8->8.5). Longer Ld also
                                     # raises resid tau ~ +0.3 (deck46 1.98 vs data 2.20 -> lands ~2.3).   # DECK35 (RESIDtune): 90->80um. Shorter Ld -> weakening reaches residual at LESS slip -> DEEPER & sharper post-peak drop (targets the too-gradual differential-stress/shear decline). Ld trend: 120->4.4 resid/62 slip, 90->3.4/75.6; 80 -> ~3.0 resid tau, +~4um slip. Paired with the load trim below to hold slip in band. (Single Ld still can't make the ~1600 s near-vertical cliff -- that's the dynamic event; two-stage weakening in deck 36 targets it.)
friction_coefficient_rough = 1.17    # DECK52_09: 1.15 -> 1.17. 52_08 MEASURED onset 952 s (data ~1000;
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
friction_coefficient_smooth = 0.055  # DECK52_25: 0.04 -> 0.055. 52_24 overshot the residual branch:
                                     # slip_end 85.5 vs data 79.1 um, tau_end 1.61 vs data 2.20 MPa,
                                     # and q_end about 2.4 MPa low. Linear 52_23/52_24 interpolation
                                     # gives fcs ~0.058 from slip/q and ~0.052 from tau; choose 0.055
                                     # as the center while preserving 52_24's improved drop shape.
                                     # DECK52_24: 0.07 -> 0.04. 52_23 end tau is +0.83 MPa and slip is -4.5 um;
                                     # the existing calibration rule (~0.4 MPa and ~1.8 um per 0.015 fcs)
                                     # points to an additional ~0.03 cut. This is the primary residual/drop lever.
                                     # Prior DECK52_22: 0.0825 -> 0.07. The data point (79.1um, 2.20 MPa) sits ~0.2 MPa
                                     # BELOW the model's own mu(s) tail (52_19 measured S(87)=2.19 and the tail slope
                                     # k_w 2.9e10 puts S(79.7) at 2.40) -> lower the arrest strength by
                                     # delta_mu_eff = 0.9*0.0125 = 0.011 (0.17 MPa @ trough sigma'n ~15).
                                     # Moves arrest +1.8um along the load line; tau_end -> 2.20.
                                     # WAS DECK52_01 (SWEEP B, middle of the slip<->resid tradeoff): 0.095->0.085
                                     # (resid ~2.7, slip +2) paired with Ld 95->100 below (slip -2, resid +0.35):
                                     # net (slip ~84, resid ~2.9) vs deck52's (88, 2.5). Brackets the reachable
                                     # front so the paper point can be picked from data. WAS DECK50: # DECK50: 0.085->0.095. Slip trim #2 (with Ld): raising the residual
                                     # strength shrinks the peak->residual stress drop -> dslip = -dtau_res/k_sys
                                     # ~ -0.27e6/1.25e11 ~ -2um; resid tau +~0.27 (0.4 MPa per 0.015 fcs).
                                     # Slip budget: 89.6 (deck46) -6 (Ld) -2 (fcs) ~ 81-82um; resid tau ~2.2-2.3.   # DECK35 (RESIDtune): 0.115->0.085. PRIMARY residual lever for the Fig-7d gaps (differential stress, shear traction, sigma'n all stay too HIGH after ~1600 s because the fault LOCKS at too high a strength). Empirically ~0.4 MPa resid tau per 0.015 fcs (deck29/32) -> 0.030 cut targets resid tau 3.4->~2.6. Lowers residual shear -> less locked-in q -> sigma'n recovers less high. Does NOT add slip (independent of the slip<->resid tension).
friction_roughness_exponent = 1.0
cohesion_rough = 0                       # DECK52_08 (COHESIONLESS): 18.5e6 -> 0. Sawcut fracture carries NO
                                     # cohesion; the onset envelope is supplied entirely by friction_
                                     # coefficient_rough = 1.15 above (see sizing there). This also removes
                                     # the residual c_eff(R=0.283) = 1.48 MPa that the TWOSTAGE dS had to eat.
                                     # initial tau (12.32 vs 11.46) met the UNCHANGED strength envelope ~255s
                                     # early (onset 984->729 s; data ~1000). Deck-25 calibration: c_eff at peak
                                     # = c_R*R^2 = c_R*0.2025; 6.5e6 bought +1.33 MPa peak strength = +267 s.
                                     # Need ~+1.0 MPa to re-balance the added driving tau: dc_R = 1.0e6/0.2025
                                     # ~ 5e6 -> 16e6. Residual unchanged: c_eff(R=0.10) = 16e6*0.01 = 0.16 MPa.                    # DECK28: 6.5->11MPa. The higher load (deck26) pulled onset back to 720s; more cohesion raises the peak strength envelope so the fault holds against the higher applied tau until ~950s. c_eff(R=0.45,exp2)=11e6*0.2025=2.23 MPa at peak; c_eff(R=0.10)=11e6*0.01=0.11 MPa at residual (still negligible -> residual tau preserved).
cohesion_smooth = 0                      # keep 0 so cohesion fully decays out by residual roughness (preserves the calibrated residual tau ~2.75).
cohesion_roughness_exponent = 2.0        # DECK25: 1->2 so cohesion decays FASTER with roughness -> big at peak (R^2=0.20), negligible at residual (R^2=0.01).

# --- DECK52_07 (LOCKFIX) new knobs vs 52_04 ---------------------------------------------------
dissipation_margin = 0.12            # DECK52_24: 0.16 -> 0.12. 52_23's reported dn peak is still ~5 um shallow;
                                     # this restores ~4.8% of the admissible dilation work while fcs/s40 recover slip.
                                     # Prior DECK52_11 (RESTICK): 0.10->0.16. Two targets: (a) dn peak -0.0436 vs
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
secondary_weakening_strength = 0.15e6  # 67_11: measured dS slope predicts slip_end ~80um and tau/q near target.
                                       # (onset 999, tau@2000 2.91, tau_end 2.235 vs data 1000/3.0/2.20) but
                                       # over-slipped 88.8 vs 79.1um. Slip balance (peak_env - lock)/k_sys:
                                       # 52_09 (12.92-2.79)/1.25e11 = 81um + ~8um BURST overshoot (slip surged
                                       # 64.7->81.2um in t=1700-1800 while the TS slope sat at 1.00x k_sys).
                                       # dS 1.35 raises the lock strength to mu(R80)*sn - TS80 = 0.292*14.8-1.21
                                       # = 3.11 MPa = data's 3.12 -> balance slip 78um.
secondary_weakening_onset_slip = 28e-6 # 67_11: earlier, smaller drop spreads correction before the 1700s overshoot.
                                       # quickly once the model crossed it; 44um delays the sharp branch
                                       # without returning all the way to 52_23's too-late 48um onset.
                                       # DECK52_24: 48 -> 40um. 52_23 reaches the second weakening stage late;
                                       # the data already sits near the 40um slip shelf by ~1400-1600 s.
secondary_weakening_distance = 12e-6   # 67_11: dS/w=1.25e10 Pa/m, safely below measured system stiffness.
                                       # aggressive; widening the branch lowers dS/w from ~0.96e11 to
                                       # ~0.75e11 Pa/m while keeping the same total drop.
                                       # DECK52_10: 12 -> 14um. Peak TS slope dS/w = 0.96e11 = 0.77x k_sys
                                       # (was 1.00x -> mini-burst). Tames the 1700-1800 surge; with the burst
                                       # gone the ~8um overshoot should shrink to +2-4 -> final slip ~80-82.
                                       # Viscosity kept at 1e13 ON PURPOSE: eta resists the burst, so trimming
                                       # it for the mid-window pedestal would counteract this deck's one goal.
                                       # deliberately AT the stability edge to reproduce the data's sharp
                                       # 1600-1800 s plunge; visc 1e13 regularizes (deck-30/31 mechanism).

normal_traction_tolerance = 0.0
tangential_traction_tolerance = 1e-16
dilation_angle_peak_degrees = 50.0     # DECK22: 37->50 (the CORRECT dilation lever). Deck21 showed dilation_state decays 1.0->0.47 by peak slip so dilation accrues in the PEAK-angle regime (raising residual 15->22 barely moved it). tan(37)=0.75->tan(50)=1.19 to lift peak dilation -0.022->~-0.031 mm. NB longer Ld cuts slip/dilation so this is deliberately aggressive.
dilation_angle_residual_degrees = 22.0 # DECK21: raised 15->22 (tan15=0.27->tan22=0.40). Deck19 dilation/slip ratio was ~0.29 (residual-dominated); target 0.031/0.077=0.40. Lifts peak dilation -0.021->~-0.031 mm and (via sigma'n relief) nudges slip 73->~77 um.
dilation_decay_distance = 1.0e-4
dilation_decay_exponent = 1.0          # revised law requires >= 1.0 (was 0.5; singular slope at zero slip)
dilation_opens_joint = true            # V15: route dilation into the joint OPENING (kinematic hardening)

# DECK23: REVERSIBLE (elastic) joint-normal opening -- new source capability. The plastic dilation is
# thermodynamically capped at dn/ds <= tau/sigma'_n ~ mu ~0.40 (dissipation limiter, .C:1066-1100), so the
# angle is INERT and the -0.041mm PEAK dilation (needs dn/ds 0.55) is unreachable by g_np alone; the data
# ALSO recovers -0.041 -> -0.031 on unload, a purely irreversible g_np cannot. This adds an elastic opening
# d_rev = C_n*<sigma_ref - sigma'_n>_+ that opens as injection drops sigma'_n (peak) and closes as it recovers
# (residual). Decoupled/output-only: does not feed the residual (far-field-governed sigma'_n). Reported normal
# dilation = g_np + d_rev.
reversible_normal_compliance = 0.0         # output-only opening reconstruction disabled
                                     # drops ~33->30um; rev share must supply ~11um at the trough deficit
                                     # (31-15.1)e6*7e-13 = 11.1um -> dn peak ~-0.041 (data -0.0409) and
                                     # end-recovery improves (rev_end ~ 3.8um at sigma'n_end ~25.5 ->
                                     # dn_end ~ -0.034 vs 52_04's -0.0357; data -0.0314).   # WAS DECK52_01: 7.0->5.0e-13 (dn peak -0.0459 -> ~-0.042 at slip ~84;
                                     # rev at trough 5e-13*16.5e6 = 8.3um). WAS DECK50: 6.0e-13->7.0e-13. The slip trims cut PLASTIC dilation by
                                     # ~mu*dslip ~ 0.4*8um = 3.2um (peak -0.0417 -> ~-0.038); +1e-13 adds
                                     # C_n*(31-13.5)e6 ~ +1.75um reversible at the trough -> peak ~ -0.040,
                                     # end ~ -0.031 (was -0.0345; data -0.0314).    # DECK32: 8.5e-13->6.0e-13. Deck31 peak dil -0.0451 (target -0.041); plastic part is now ~-0.032 (limiter, raised by the higher mid-slip tau), so cut the reversible part harder: rev_peak 6e-13*16e6=0.0096 -> peak dil ~-0.041.
reversible_normal_reference_stress = 31e6 # Pa: initial preload sigma'_n where d_rev = 0.
max_plastic_slip_increment = 0.0     # revised law forbids increment caps; substepping + viscosity instead (was 1.0e-6).
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
tangential_viscosity = 5.0e12        # DECK52_19 (MIDPATH): 8->5e12. 52_16 (visc 5e12) had the BEST mid-path
                                     # of the campaign (slip@1717 = 71.3 um vs data 72.7; 52_17's 8e12 gave
                                     # 62.7 = ~100 s late) -- it just STALLED numerically at the re-stick
                                     # (t=1878.7, V decayed to 1.4e-8 m/s, dt collapsed to 1e-6, residual
                                     # limit-cycled at ~1e-5 with 450-s local-substep residual evaluations).
                                     # Root cause = the referenced-RSF stick-boundary discontinuity, now
                                     # cured by rate_and_state_nonnegative (see below), which is what makes
                                     # 5e12 survivable. Overrun arithmetic (PART IX): pending slip at the
                                     # trough = overstress/k_sys = (eta*V_trough + rsf)/1.25e11; at 5e12,
                                     # V~1.5e-7: (0.75+0.2)e6/1.25e11 = 7.6 um -> peak slip ~ 72+7.6 ~ 79-80
                                     # (data 79.1). At 8e12 the same arithmetic gave the measured +10.6.        # DECK52_13: 6->8e12, partial give-back of window resistance (52_12's
                                     # excess driving at t1750 was 1.23 MPa -> 11um pending slip).
                                     # WAS DECK52_12: 1e13->6e12. RSF below takes over part of the rate duty;
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
use_rate_and_state = true
rate_and_state_a  = 0.020
rate_and_state_b  = 0.016           # DECK52_13: 0.008->0.016 (b/a 0.8, still a>b velocity-strengthening).
                                    # Healing doubled: during the 1850-1900 deceleration theta grows and
                                    # strength recovers ~theta^(b/a) -> the fault re-sticks SOONER (52_12
                                    # stuck at 85.9um; target ~81-83). Trade: steady-state brake exponent
                                    # 1-b/a drops 0.6->0.2 (weaker ss brake), the visc bump below covers it.
rate_and_state_Dc = 5.0e-5           # state distance ~ slip band; theta0 = Dc/V0 = 1000 s
rate_and_state_V0 = 5.0e-8
rate_and_state_theta0 = 1000
rate_and_state_nonnegative = true    # DECK52_19 (CLAMPFIX source feature, 2026-07-11): clamp the referenced
                                     # RSF term >= 0. The raw form a*(asinh(z)-asinh(1/2)) is -0.481*a*p at
                                     # V->0, so the slip-branch strength sits ~0.25 MPa BELOW the stick limit:
                                     # the stick<->slip transition is a non-monotone jump the global Newton
                                     # limit-cycles across DURING RE-STICK (52_15 died t=1831, 52_16 t=1879,
                                     # both at V~1.4e-8 m/s while arresting, residual stuck at 1-4e-5 >
                                     # nl_abs_tol with dt at dtmin). Clamped, slip strength at V->0+ equals
                                     # the stick limit (continuous, monotone). Cost: the small V<V0 weakening
                                     # (~0.1-0.2 MPa residual aid) is given up -> tau_end may read +0.1-0.2.
                                     # Validated: 13/13 suite + FD-vs-AD Jacobian 5.2e-14 with the term ON.

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
bb_max_aperture_closure = 1.05e-6     # Vm (m): DECK52_17 (PERMPEAK) 0.85 -> 1.05. SINGLE-CHANGE A/B off 52_13.
                                     # 52_13's k_peak 0.787 vs data 0.925e-13 (~15% low; flow peak 0.082 vs
                                     # 0.113). WHY NOW: Vm=0.85 was sized on deck 42/43 where the sigma'n trough
                                     # DROOPED to 12.9 (more closure-release there); the RESTICK line fixed the
                                     # trough at 15.3, so the BB opening at the trough fell (0.85um*[g(31)-g(15.3)]
                                     # = 0.255um) and the peak aperture landed 0.972 vs the 1.054um the data
                                     # needs. Sizing: need +0.082um at sigma'n 15.3 -> Vm = 0.85*(0.337/0.255)
                                     # ~ 1.05um -> predicted a_h_peak ~1.03, k_peak ~0.89e-13, Q_peak ~0.095.
                                     # RISK (measured on 42/44): softer closure feeds the aperture->perm->
                                     # pressure->sigma'n loop; at the RESTICK operating point (dissm 0.16 +
                                     # pcoeff 0.88 holding the trough) expect droop <= 0.3 MPa; if trough
                                     # falls below 14.9 or slip grows >84, split the move (Vm 0.95).
                                     # The REMAINING peak deficit after this (~0.03-0.04e-13) is the DYNAMIC
                                     # burst spike -- quasi-static + regularization smooths it (structural,
                                     # NOT a mesh problem; see MD PART VIII).
                                     # WAS DECK43 1.17->0.85. Deck42 (Vm1.17) was too SOFT ->
                                     # coupled HM feedback drooped peak sigma'n 15->12 (aperture->perm->
                                     # flow->pore pressure->sigma'n) and perm OVERSHOT (peak k 1.22 vs
                                     # data 0.925, unload bias +0.16). Stiffer closure = less opening ->
                                     # less feedback -> sigma'n holds ~14-15 -> perm drops at peak AND
                                     # mid-unload together. Shape (p2, 3.2x stiffening) preserved.
bb_initial_normal_stiffness = 1.43e13 # Kni (Pa/m): DECK52_17 1.76e13->1.43e13 so sigma0 = Vm*Kni stays 15 MPa (shape preserved, magnitude only)
bb_stress_exponent = 2.0              # p: power-law closure exponent (1=hyperbola, 2=matches 3.2x stiffening)
dilation_scale = 0.0117              # DECK52_23: port 54_48 dscale0117 hydraulic rebalance.
                                     # V15: was 0.4; cut ~17x because the ~17x larger dilation angle grows
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
slip_damage_scale = 0.28e-6          # DECK52-SWEEP: re-fit to hold the developed unload gouge at slip~84um:
                                     # 0.28*(1-exp(-64/30)) = 0.247um (= deck-43/47 unload calibration). WAS DECK50 (=DECK47 values): 0.25->0.29 compensates the onset threshold
                                     # below so the fully-developed unload gouge is preserved (~0.247um at 78um
                                     # slip: 0.29*(1-exp(-(78-40)/20)) = 0.246).
slip_damage_onset_slip = 20e-6      # DECK52-SWEEP: 40->20um. The HARD 40um threshold caused the perm/flow
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
fluid_bulk_modulus = 4.7835616438e9
paper_flow_width_over_length_sw_s4 = 0.81  # inferred from Ye2018 Table 2 SW-S4 Eq. 9 consistency
ml_per_m3_per_min = 6.0e7

# --- output ---
exodus_file_base = results_exodus/67_11_sw4_mc_dS0p15_s28_w12_m0_kernel_SV_mesh3
csv_file_base    = results_csv/67_11_sw4_mc_dS0p15_s28_w12_m0_kernel_SV_mesh3
checkpoint_file_base = results_checkpoint/67_11_sw4_mc_dS0p15_s28_w12_m0_kernel_SV_mesh3

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
    coord = '-0.0191938 0 0.0218597548'
    new_boundary = source_in
    use_closest_node = true
  []
  [source_out]
    type = ExtraNodesetGenerator
    input = source_in
    coord = '0.0191938 0 0.0911402452'
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
      # DECK52_23: add 54_48 poroelastic compensation before the AD-specific delayed relax.
      expression = 'if(t<2.0,${axial_pres_initial},if(t<55.0,${axial_pres_initial}+(${axial_pres_final}-${axial_pres_initial})*(t-2.0)/53.0,${axial_pres_final}+${poro_du}*min((t-55.0)/${poro_dur},1.0)+if(t<${relax_t0},0.0,${axial_relax_du}*min((t-${relax_t0})/${relax_dur},1.0))))'
    []

  # Injection pressure schedule (Pa): FULL digitized Ye & Ghassemi SW-S4 history -- the complete
  # rise-AND-FALL cycle to t~3404 s (peak ~28 MPa at ~1788 s, declining back to ~8 MPa). The earlier
  # caseF-derived schedule contained only the RISING limb (truncated at ~1900 s), so the run stopped
  # before the post-peak phase where the injection decline lets the fault re-stabilize and the
  # differential stress partially recovers. Restored from the Orca_2.0 reference deck.
  [injection_pressure]
    type = PiecewiseLinear
    x = '0 39.520164216741705 73.14687685794524 103.95057045328758 130.54475290608298 151.52976505320134 185.17293652746184 218.82795836152286 252.48298019558388 286.1380020296451 319.78644033048386 353.4203948582324 384.2289602681592 409.4212451565288 432.37223199458776 451.3912694507658 470.9733306681428 504.61913555569254 538.2741573897538 571.9291792238146 597.1704455993604 639.2221057055581 670.0375179900361 695.2341480103328 714.8234511142546 734.9672193861866 751.1849634561368 779.1919721385079 812.8469939725692 846.5020158066304 880.1570376406912 913.8120594747525 947.447989062468 978.2606362629926 1003.4541061873424 1028.6483661356788 1045.4320307214462 1059.4036049265023 1087.427730795252 1121.0827526293133 1154.737774463374 1188.3927962974353 1222.0458430715298 1255.6817726592453 1289.2953182340034 1317.8548170244176 1339.6833772833506 1359.2662943600467 1373.243596239006 1401.2647595178055 1434.9197813518667 1468.5748031859275 1502.2298250199888 1535.8802383807943 1569.506292668676 1600.3136730426227 1625.5110930869055 1650.7014029153083 1665.2410043668124 1687.0697621317422 1720.7188587859032 1754.3738806199644 1788.0289024540252 1821.695774647887 1852.5778122885781 1880.6710652561655 1905.966645780798 1925.6526609877606 1946.27663217295 1979.0093010025216 2012.6643228365829 2046.3193446706437 2079.974366504705 2113.637288578633 2147.3193028989067 2178.211479180761 2203.49659188757 2225.98067454948 2248.472657451258 2270.95739846649 2304.6176871271296 2338.272708961191 2371.927730795252 2405.5840693359573 2439.2575250630416 2470.14035272772 2498.23281567132 2523.5254336060025 2541.803626068639 2561.2048376283906 2576.93105510794 2607.7814917891624 2641.436513623224 2675.091535457285 2708.75050741128 2742.4200130184304 2776.1079525186046 2807.0057906390307 2832.2944584537795 2854.7805161756564 2874.467913924596 2894.127660833999 2927.780707608093 2961.4357294421548 2995.0907512762155 3028.753014996822 3062.4337126104515 3093.3199637124058 3118.603101359247 3141.086196491174 3163.5791669229343 3182.139200442831 3214.124901592964 3247.7799234270256 3281.4349452610863 3315.089967095147 3348.744988929209 3382.4000107632696 3404.836691985977'
    y = '5000000 5254620.82538901 5668743.87518708 6352528.44578387 7074836.09078049 7797143.73577711 7970497.57057629 7970497.57057629 7970497.57057629 7970497.57057629 8066805.25657584 8374989.8517744 8987506.73473153 9704035.91856817 10385894.335445 11148651.2085614 11880589.622158 12015420.3825574 12015420.3825574 12015420.3825574 12015420.3825574 12265820.3661562 12778177.2556738 13431143.3667507 14057143.3257478 14777524.8170244 15492127.8471411 16060343.1945384 16060343.1945384 16060343.1945384 16060343.1945384 16060343.1945384 16339635.4839371 16892441.6015745 17591635.4019312 18279272.279968 18920681.468725 19671881.4195215 19989696.78332 19989696.78332 19989696.78332 19989696.78332 20018589.0891199 20297881.3785186 20904619.8003157 21596108.9857925 22286635.0944092 23006053.5088259 23673465.7728028 24034619.5953011 24034619.5953011 24034619.5953011 24034619.5953011 24102034.9755008 24525788.7938988 25155641.0603358 25797050.2490928 26542471.7387293 27189659.3886463 27877296.2666831 27963973.1840827 27963973.1840827 27963973.1840827 27790619.3492835 27328342.4564856 26634927.1172889 25840388.7077926 25051628.7594563 24217604.1987002 24034619.5953011 24034619.5953011 24034619.5953011 24034619.5953011 23919050.3721016 23524188.8595035 22913598.1302663 22272188.9415093 21578773.6023126 20769789.0399164 20066742.9321196 19989696.78332 19989696.78332 19989696.78332 19970435.2461201 19700773.7253214 19226939.9102036 18545081.4933268 17793881.5425303 17086020.0504336 16360823.174857 16060343.1945384 16060343.1945384 16060343.1945384 16060343.1945384 16002558.5829387 15790681.6737397 15309143.2437419 14615727.9045452 13922312.5653484 13200004.9203518 12391020.3579556 11986528.0767575 12015420.3825574 12015420.3825574 12015420.3825574 11909481.9279578 11533881.9525596 11009968.1407221 10397451.2577649 9718482.07146811 8895051.35617197 8166965.25001537 7970497.57057629 7970497.57057629 7970497.57057629 7970497.57057629 7970497.57057629 7970497.57057629 7970497.57057629'
  []

  [production_pressure_fn]
    type = ConstantFunction
    value = ${production_pressure}
  []

  # Confining pressure on the cylindrical "sides" surface via the analytic outward normal.
  # DECK52_23: apply the 54_48 late side-unload trim to the unload branch.
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

  # (1/M)*dp/dt + alpha*div(du/dt) in one correctly-coupled AD kernel, replacing the
  # old split fluid_storage + mass_vol_expansion pair.
  [fluid_storage]
    type                 = OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel
    variable             = pore_pressure
    coupling_type        = HydroMechanical
    multiply_by_fluid_density = true
    extra_vector_tags    = mass_reaction
  []
  [darcy]
    type = OrcaFullySaturatedSinglePhaseDarcySUPGKernel
    variable = pore_pressure
    multiply_by_fluid_density = true
    use_supg = true
    save_in = inj_flux_aux
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
    type = ADMaterialRealAux
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
    type = ADMaterialRealAux
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
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = limit_tau
    variable = limit_tau
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [plastic_slip_increment_aux]
    type = ADMaterialRealAux
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
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = cumulative_plastic_slip
    variable = cumulative_plastic_slip
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [friction_coefficient_effective_aux]
    type = ADMaterialRealAux
    check_boundary_restricted = false
    property = friction_coefficient_effective
    variable = friction_coefficient_effective
    boundary = fracture_interface
    execute_on = TIMESTEP_END
  []
  [cohesion_effective_aux]
    type = ADMaterialRealAux
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
    # Revised composite cohesive-contact-friction law. For a pre-existing fault the interface is
    # initialized fully damaged (enable_tensile_cohesion=false), reproducing the frictional-joint
    # behavior of the old ADOrcaDecoupledDilationRoughnessContactTraction while adding the coupled
    # (gamma, g_np) local return map, event-aware substepping, and smooth active sets. The downstream
    # hydraulic wiring is unchanged: this model still declares dilation_jump_increment,
    # roughness_state, and cumulative_plastic_slip.
    type = ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile
    boundary = fracture_interface

    enable_tensile_cohesion = false   # pre-existing fault: start fully damaged / frictional

    penalty_normal = ${penalty_normal}
    penalty_tangent = ${penalty_tangent}
    use_hyperbolic_normal_closure = ${use_hyperbolic_normal_closure_mech}
    initial_normal_stiffness = ${initial_normal_stiffness_mech}
    maximum_closure = ${maximum_closure_mech}
    maximum_closure_fraction = ${maximum_closure_fraction_mech}
    normal_closure_stress_exponent = ${normal_closure_stress_exponent_mech}
    normal_closure_offset = ${normal_closure_offset_mech}
    max_local_newton_iterations = 80
    max_local_substeps = 48

    initial_roughness = ${initial_roughness}
    residual_roughness = ${residual_roughness}
    roughness_decay_distance = ${roughness_decay_distance}

    friction_coefficient_rough = ${friction_coefficient_rough}
    friction_coefficient_smooth = ${friction_coefficient_smooth}
    friction_roughness_exponent = ${friction_roughness_exponent}

    # NOTE: set directly (not via ${cohesion_rough}) — MOOSE brace substitution of the top-level
    # negative value was resolving to 0 here, silently zeroing the Coulomb intercept.
    cohesion_rough = ${cohesion_rough}
    cohesion_smooth = ${cohesion_smooth}
    cohesion_roughness_exponent = ${cohesion_roughness_exponent}

    normal_traction_tolerance = ${normal_traction_tolerance}
    tangential_traction_tolerance = ${tangential_traction_tolerance}

    use_dilatancy = true
    dilation_angle_peak_degrees = ${dilation_angle_peak_degrees}
    dilation_angle_residual_degrees = ${dilation_angle_residual_degrees}
    dilation_decay_distance = ${dilation_decay_distance}
    dilation_decay_exponent = ${dilation_decay_exponent}
    max_plastic_slip_increment = ${max_plastic_slip_increment}
    tangential_viscosity = ${tangential_viscosity}
    use_rate_and_state = ${use_rate_and_state}          # DECK52_12 (referenced RSF, deck-34 form)
    rate_and_state_a = ${rate_and_state_a}
    rate_and_state_b = ${rate_and_state_b}
    rate_and_state_Dc = ${rate_and_state_Dc}
    rate_and_state_V0 = ${rate_and_state_V0}
    rate_and_state_theta0 = ${rate_and_state_theta0}
    rate_and_state_nonnegative = ${rate_and_state_nonnegative}
    dissipation_margin = ${dissipation_margin}                          # DECK52_07
    secondary_weakening_strength = ${secondary_weakening_strength}      # DECK52_07 (TWOSTAGE)
    secondary_weakening_onset_slip = ${secondary_weakening_onset_slip}  # DECK52_07
    secondary_weakening_distance = ${secondary_weakening_distance}      # DECK52_07
    dilation_opens_joint = ${dilation_opens_joint}   # V15: kinematic dilatant hardening (gap opens)
    reversible_normal_compliance = ${reversible_normal_compliance}         # DECK23: elastic joint-normal opening (recoverable)
    reversible_normal_reference_stress = ${reversible_normal_reference_stress}
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
    point = '-0.0191938 0 0.0218597548'
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
    point = '0.0191938 0 0.0911402452'
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

  # --- decoupled-law state diagnostics ---
  [cumulative_plastic_slip_pp]
    type = ADSideAverageMaterialProperty
    property = cumulative_plastic_slip
    boundary = fracture_interface
  []
  [plastic_slip_increment_pp]
    type = ADSideAverageMaterialProperty
    property = plastic_slip_increment
    boundary = fracture_interface
  []
  [limit_tau_pp]
    type = ADSideAverageMaterialProperty
    property = limit_tau
    boundary = fracture_interface
  []
  # notebook alias bb_limit_tau_pa -> bb_limit_tau_pp (Coulomb shear strength, same quantity)
  [bb_limit_tau_pp]
    type = ADSideAverageMaterialProperty
    property = limit_tau
    boundary = fracture_interface
  []
  [friction_coefficient_effective_pp]
    type = ADSideAverageMaterialProperty
    property = friction_coefficient_effective
    boundary = fracture_interface
  []
  [cohesion_effective_pp]
    type = ADSideAverageMaterialProperty
    property = cohesion_effective
    boundary = fracture_interface
  []
  [roughness_state_pp]
    type = ADSideAverageMaterialProperty
    property = roughness_state
    boundary = fracture_interface
  []
  [dilation_state_pp]
    type = ADSideAverageMaterialProperty
    property = dilation_state
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
  [czm_dn_total_pp]
    type = ADSideAverageMaterialProperty
    property = normal_opening_total
    boundary = fracture_interface
  []
  [czm_rev_opening_pp]         # reversible-only component, for diagnostics (mm below)
    type = ADSideAverageMaterialProperty
    property = reversible_normal_opening
    boundary = fracture_interface
  []
  [czm_rev_opening_mm_pp]
    type = ParsedPostprocessor
    pp_names = czm_rev_opening_pp
    expression = '-czm_rev_opening_pp * 1e3'
  []
  # SIGN FIX: czm_dn follows this model's native convention (positive = opening, negative =
  # closing -- verified from source: interface_displacement_jump = R^T*(disp_neighbor - disp),
  # i.e. normal . displacement_jump_global). The paper's convention is the OPPOSITE (negative =
  # opening/dilation, per Sec. 3: "a NEGATIVE trend of normal dilation" demonstrates dilation).
  # Must negate to match the paper -- this previously did not, and disagreed in sign with the
  # (correctly negated) frac_normal_dilation_paper_mm computed from the same underlying jump.
  [czm_normal_dilation_paper_mm_pp]
    type = ParsedPostprocessor
    pp_names = czm_dn_pp
    expression = '-czm_dn_pp * 1e3'
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
    point = '${sample_radius} 0 0.115'
  []
  [bulk_disp_z_upper_pp]
    type = PointValue
    variable = disp_z
    point = '${sample_radius} 0 0.115'
  []
  [bulk_disp_x_lower_pp]
    type = PointValue
    variable = disp_x
    point = '${sample_radius} 0 0.010'
  []
  [bulk_disp_z_lower_pp]
    type = PointValue
    variable = disp_z
    point = '${sample_radius} 0 0.010'
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
  end_time = 3500              # FULL SW-S4 cycle (was 1800 -> truncated mid-experiment, before the burst)

  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1.5                  # conservative transition cadence; v12 rejected ~1.93 s around the first slip jumps
    optimal_iterations = 18
    growth_factor = 1.2
    cutback_factor = 0.5
  []

  dtmax = 1.5
  dtmin = 1e-4                 # DECK52_19: was 1e-6. At dt<1e-4 the per-step slip resolution
                               # k_t*V*dt < 1 Pa puts the stick/slip branch decision at round-off
                               # noise (the 52_15/16 death spiral burned 4 h at dt~1e-6); with the
                               # RSF clamp the re-stick no longer needs the crawl -- fail fast.
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
  []
  [chk]
    type = Checkpoint
    file_base = ${checkpoint_file_base}
    time_step_interval = 20
    num_files = 4
  []
[]


