# =============================================================================
# 95-SERIES -- RATE-AND-STATE FRICTION REPLACES THE PERZYNA VISCOSITY.  SW-S3 mesh 5
# Built from 93_05_sw3_final_resc1p40_ppfix.i.  The Barton-Bandis envelope, the
# slip-weakening constants, the dilation law, the mesh, the postprocessors and
# every boundary condition are IDENTICAL to that deck.  Exactly two things move:
# tangential_viscosity -> 0, and the new rate-and-state overstress switches on.
#
# WHAT IS BEING TESTED
#   The 93-series carries tangential_viscosity, documented as a numerical
#   regulariser.  It is not one: the kernel forms eta*V, so at SW-S3's
#   eta = 4e+11 Pa.s/m it is worth 0.03-3.5 MPa across the plausible slip-velocity
#   range, against a shear strength of 15-25 MPa.  It is the model's de facto rate
#   law -- fitted, numerically, on a knob labelled numerics.  SW-S4 alone needed 9x
#   the other three, and SW-S4 alone is the specimen whose staircase timing never
#   fitted and whose D_c bracket failed in BOTH directions.
#
#   Dieterich-Ruina does the same job with two measurable constants:
#       tau = c(W) + sigma'_n*mu(s) + sigma'_n*[ a*ln(1+V/V0) - b*ln(1+V_theta/V0) ]
#   and, unlike slip weakening, b > 0 makes the interface heal while it is HELD.
#   Pure slip weakening cannot: at constant stress with no slip nothing evolves.
#
# THIS DECK
#   VELOCITY NEUTRAL. a-b = 0: the steady-state envelope is rate independent and only
#   the transient (healing during holds, direct effect on ramps) survives. Isolates
#   the transient from the steady-state rate dependence.
#
#   rsf_a = 0.01, rsf_b = 0.01
#   rsf_characteristic_slip = 5e-06 m and rsf_reference_velocity = 5e-08 m/s are held
#   FIXED across all four specimens and all four variants -- they are not fitted.
#   D_rs = 5 um is a laboratory value for bare/saw-cut granite and must be well below
#   the ~30-80 um of total slip in this test, or b cannot express itself at all.
#
# FALSIFIABLE PREDICTION
#   If the SW-S4 hold-stage deficit is a healing effect, b > 0 supplies the slip during
#   holds that 90_08/93_07 miss, and the staircase timing improves without touching
#   D_c.  If the timing is set by the injection protocol instead, no value of b helps
#   and the b bracket comes back flat -- which closes the question.
#
# WHAT WOULD BE A BUILD ERROR RATHER THAN A PHYSICS RESULT
#   Equating eta*V0 = sigma'_n*a*ln2, the four fitted viscosities imply
#     SW-T1 a = 5.07e-4   SW-T2 4.99e-4   SW-S3 1.23e-3   SW-S4 9.52e-3
#   against a laboratory range of 0.008-0.015.  Only SW-S4 is already physical; the
#   other three sit 8-20x below it.  So the a = 0.010 decks give T1/T2/S3 roughly an
#   order of magnitude MORE rate strengthening than they were calibrated with, and
#   those three are EXPECTED to move.  A large degradation on T1/T2/S3 with SW-S4
#   improving is the physics result.  A large degradation on ALL FOUR, including the
#   aeq_b0 control, means the overstress is wired wrong -- check rsf_overstress_mpa_pp
#   against eta*V from the 93 run before drawing any conclusion.
#
# NEW DIAGNOSTICS
#   rsf_theta_pp [s], rsf_slip_velocity_pp [m/s], rsf_overstress_mpa_pp [MPa].
#   The last one is the whole experiment in one channel: it is what eta*V used to be.
#
# CONTROL: 93_05_sw3_final_resc1p40_ppfix.i is the 93-series deck this was built
# from; it IS the control run and does not need rebuilding.
# =============================================================================
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
exodus_file_base = results_exodus_hpc_rorqual/95_11_sw3_rsf_a010_b010
csv_file_base    = results_csv_hpc_rorqual/95_11_sw3_rsf_a010_b010
checkpoint_file_base = results_checkpoint_hpc_rorqual/95_11_sw3_rsf_a010_b010

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
  [injection_pressure]  # SW-S3 digitized schedule (from v4 deck)
    type = PiecewiseLinear
    x = '0.0 69.8 171.1 281.0 390.9 500.8 583.5 639.1 676.0 832.0 972.7 1060.7 1125.4 1199.2 1309.1 1418.9 1528.8 1611.7 1645.9 1694.8 1804.7 1914.6 1997.3 2052.9 2089.9 2205.1 2300.4 2383.1 2429.4 2475.7 2569.2 2699.0 2750.3 2795.5 2831.5 2973.5 3115.1 3206.6 3251.8 3324.4 3434.2 3544.1 3626.3 3671.5 3744.2 3854.0 3963.8 4045.6 4090.8 4241.1 4360.1 4392.5 4465.0 4546.9 4656.8 4739.2 4802.4'
    y = '5754797 5754797 7730940 7840970 7840970 7951000 8985284 10877804 11802058 12019512 12019512 12594276 14244730 15895183 16027219 16027219 16159256 17523630 18731707 19768247 19988308 20032320 21000586 22805082 23949396 24039024 23993408 24785626 26260031 28086533 28565854 28565854 27734436 26194013 24411523 24195122 23949396 23597299 22100888 20120344 19988308 19988308 19460163 18007764 16137250 16027219 15851171 14310748 12462240 12097561 11941463 11432357 9337381 7862976 7840970 7840970 7882927'
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
    type = OrcaBartonBandisRateStateHardening
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
    tangential_viscosity = 0.0
    # --- 95-SERIES: Dieterich-Ruina rate-and-state overstress, replacing the
    #     linear Perzyna tangential_viscosity (now 0). The Barton-Bandis envelope
    #     above is UNCHANGED and is the V -> 0 (fully healed) strength.
    use_rate_and_state = true
    rsf_a = 0.01
    rsf_b = 0.01
    rsf_characteristic_slip = 5e-06
    rsf_reference_velocity = 5e-08
    rsf_theta0 = 0.0                       # 0 seeds steady state D_rs/V0

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
  [rsf_theta_pp]
    type = SideAverageMaterialProperty
    property = rate_state_theta
    boundary = fracture_interface
  []
  [rsf_slip_velocity_pp]
    type = SideAverageMaterialProperty
    property = rate_state_slip_velocity
    boundary = fracture_interface
  []
  [rsf_overstress_mpa_pp]
    type = ParsedPostprocessor
    pp_names = rsf_overstress_pa_pp
    expression = 'rsf_overstress_pa_pp * 1e-6'
  []
  [rsf_overstress_pa_pp]
    type = SideAverageMaterialProperty
    property = rate_state_overstress
    boundary = fracture_interface
  []
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
  end_time = 4802              # FULL SW-S3 cycle (11 stages, ~430 s each)

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
