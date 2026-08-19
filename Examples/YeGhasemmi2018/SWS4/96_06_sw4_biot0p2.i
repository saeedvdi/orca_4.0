# =============================================================================
# 96-SERIES -- POROELASTIC-CONSISTENCY PROBE.  SW-S4 mesh 5
# Built from 93_07_sw4_final_theta30_jrc5_ppfix.i.  NOTHING is refitted.  Only the
# parameter(s) named below move; the envelope, the mesh, the postprocessors and
# every other constant are identical to that deck.
#
# WHAT IS BEING TESTED
#   Two parameters pull the same lever -- how much pore pressure de-stresses the
#   fracture -- and one of them is outside its physical bound.
#
#   (a) THE BOUND.  All four decks use E = 67 GPa and nu = 0.32, so the drained bulk
#       modulus is K = E/(3(1-2nu)) = 62.0 GPa.  Biot requires alpha = 1 - K/K_s, and
#       for granite K_s (mineral) is 45-50 GPa.  K already EXCEEDS K_s, so alpha comes
#       out negative, not 0.6; reaching 0.6 at this K would need K_s = 155 GPa, above
#       any silicate mineral.  At a more usual granite nu ~ 0.22 one gets K ~ 39.9 GPa
#       and alpha ~ 0.17.  nu = 0.32 and alpha = 0.6 are jointly inconsistent.
#
#   (b) THE REDUNDANCY.  fault_pressure_coefficient scales the pressure fed to the CZM
#       fault-pressure kernels.  SW-T1 and SW-T2 run at 1.0; only the two SAW CUTS are
#       attenuated (SW-S3 0.87, SW-S4 0.86, the latter labelled "legacy fitted").
#       Physically a joint's effective-stress coefficient is ~1 -- the contact-area
#       ratio is a few percent at these stresses -- so < 1 is absorbing something.
#       One knob above its bound and one below, both controlling pressure-driven
#       de-stressing, is the classic two-compensating-errors signature.
#
# THIS DECK MOVES
#   biot_coefficient 0.6 -> 0.2
#
# HOW TO READ THE RESULT
#   This is a SENSITIVITY probe, not a recalibration.  If the Table-2 scores barely
#   move, the inconsistency is cosmetic and alpha can be corrected by fiat -- a fitted
#   parameter deleted for free, which is worth more to the paper than another 0.5 %
#   of nRMSE.  If they move a lot, nu must be revisited before anything else, because
#   alpha is not independently adjustable at nu = 0.32.
#
# WHAT IS DELIBERATELY NOT IN THIS SERIES
#   nu 0.32 -> 0.22.  It would change the elastic response and therefore require
#   re-gating axial_pres_final, so it is not a one-change deck.  It is the follow-up
#   if this probe comes back sensitive.
#
# NOTE ON COVERAGE
#   SW-T1 and SW-T2 get only the alpha probe: their fault_pressure_coefficient is
#   already 1.0, so an "fpc1p0" deck would be a byte-for-byte rerun of 93.
#
# CONTROL: 93_07_sw4_final_theta30_jrc5_ppfix.i.
# =============================================================================
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
biot_coefficient = 0.2

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
exodus_file_base = results_exodus_hpc_rorqual/96_06_sw4_biot0p2
csv_file_base    = results_csv_hpc_rorqual/96_06_sw4_biot0p2
checkpoint_file_base = results_checkpoint_hpc_rorqual/96_06_sw4_biot0p2

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
  end_time = 3500              # FULL SW-S4 cycle (was 1800 -> truncated mid-experiment, before the burst)

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


