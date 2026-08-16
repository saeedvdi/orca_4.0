#!/usr/bin/env python3
"""
refit_joint_constants_from_paper.py -- derive every constant that changes when the
four Ye & Ghassemi (2018) decks are rebuilt on the PAPER's joint properties instead
of on invented ones.

WHY THIS EXISTS
===============
scripts/paper_parameter_audit.py established WHAT is wrong (2026-08-16):

  * SW-S3 runs JRC = 23.35 and SW-S4 JRC = 17.50 against the paper's own measured
    1.96 and 1.19 -- 11.9x and 14.7x -- and 23.35 is outside Barton's 0-20 scale.
  * both run JCS = 300 MPa against a measured UCS of 150 MPa.
  * phi_r = 8.45 and 7.50 deg exist only to compensate; no granite joint has a
    basic friction angle below ~25 deg.
  * SW-T1/T2 already use the measured JRC and JCS but then need phi_r = 44.1 and
    46.3 deg, because a MATED tensile fracture held at sigma'_n/JCS ~ 0.4 has no
    other way to express asperity interlock: Barton's roughness term is
    mobilization-limited and vanishes as sigma'_n approaches JCS.

The errors mutually mask at the calibration point -- every deck still reproduces
its own measured peak tau -- but d(tau)/d(sigma'_n) does not, and that derivative
is the entire point of an experiment in which injection halves sigma'_n.

This script does the refit. Nothing here is tuned to a simulation result: every
number is a closed-form solve of the paper's own equations against Table 1 and
Table 2. It also derives the mesh-driven quantities (source-node coordinates,
paper-frame reduction coefficients) that move when SW-S4 and SW-T2 are rebuilt at
the fracture angle their own data implies.

Run:  python3 scripts/refit_joint_constants_from_paper.py
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paper_parameter_audit import (  # noqa: E402
    PAPER_ROCK, PAPER_TABLE1, PAPER_TABLE2, PAPER_TEST, PAPER_ONSET_PI_MPa,
    PI_LOAD, DECK, last_stick_index, rule,
)

UCS = PAPER_ROCK["ucs_Pa"]
PHI_INTACT = PAPER_ROCK["intact_friction_angle_deg"]

# Barton's law is evaluated on the joint's own wall strength. The paper reports no
# separate JCS, and Sec. 2.2 describes fresh unweathered surfaces, so JCS = UCS is
# the paper-faithful choice; the current decks' 300 MPa is 2x the measured value.
JCS = UCS


def roughness_angle(jrc, sn_Pa, jcs_Pa=JCS):
    """Barton's roughness term JRC*log10(JCS/sigma'_n), in degrees.

    jcs_Pa is explicit so the deck's own 300 MPa and the paper's 150 MPa are never
    silently mixed: the whole point of the audit is that JRC and JCS compensate.
    """
    return jrc * math.log10(jcs_Pa / sn_Pa)


def phi_peak(phi_r, jrc, sn_Pa, jcs_Pa=JCS):
    return phi_r + roughness_angle(jrc, sn_Pa, jcs_Pa)


def tau_limit(phi_r, jrc, sn_Pa, cohesion_Pa=0.0, jcs_Pa=JCS):
    return cohesion_Pa + sn_Pa * math.tan(math.radians(phi_peak(phi_r, jrc, sn_Pa, jcs_Pa)))


def dtau_dsn(phi_r, jrc, sn_Pa, jcs_Pa=JCS):
    """d(tau_lim)/d(sigma'_n). Cohesion drops out -- that is the whole point of it.

    tau = c + s*tan(phi_r + JRC*log10(JCS/s))
      -> dtau/ds = tan(phi) - JRC*(pi/180)/(ln10 * cos^2(phi))
    """
    phi = math.radians(phi_peak(phi_r, jrc, sn_Pa, jcs_Pa))
    return math.tan(phi) - jrc * (math.pi / 180.0) / (math.log(10.0) * math.cos(phi) ** 2)


def onset_state(sample):
    """(sigma'_n, tau) [Pa] at the last hold stage before appreciable slip."""
    i = last_stick_index(None, sample)
    t2 = PAPER_TABLE2[sample]
    return t2["sn"][i] * 1e6, t2["tau"][i] * 1e6, PI_LOAD[i]


def end_of_loading_state(sample):
    """(sigma'_n, tau) [Pa] at the last loading hold -- the post-slip residual."""
    i = len(PI_LOAD) - 1
    t2 = PAPER_TABLE2[sample]
    return t2["sn"][i] * 1e6, t2["tau"][i] * 1e6, PI_LOAD[i]


def mohr_coulomb_cohesion(ucs_Pa, phi_deg):
    """Intact-rock cohesion implied by UCS and the internal friction angle.

    UCS = 2c*cos(phi)/(1 - sin(phi))  ->  c = UCS*(1 - sin(phi))/(2 cos(phi)).
    """
    p = math.radians(phi_deg)
    return ucs_Pa * (1.0 - math.sin(p)) / (2.0 * math.cos(p))


# ---------------------------------------------------------------------------
# 1. The saw cuts: solve for phi_r at the paper's JRC and JCS
# ---------------------------------------------------------------------------

def refit_sawcuts():
    rule("1. Saw cuts SW-S3 / SW-S4: phi_r at the paper's own JRC and JCS = UCS")
    print("  Barton's envelope has one free parameter once JRC and JCS are the measured")
    print("  values. Pin it through the last stick stage of Table 2 -- the highest shear")
    print("  stress the joint is observed to carry without appreciable slip.\n")
    out = {}
    for s in ("SW-S3", "SW-S4"):
        jrc = PAPER_TABLE1[s]["jrc"]
        sn, tau, pi = onset_state(s)
        phi_mob = math.degrees(math.atan(tau / sn))
        ra = roughness_angle(jrc, sn)
        phi_r = phi_mob - ra
        d = DECK[s]
        print(f"  {s}   last stick stage Pi = {pi} MPa,  sigma'_n = {sn/1e6:.2f} MPa, "
              f"tau = {tau/1e6:.2f} MPa")
        print(f"        mobilised phi = atan(tau/sigma'_n)      = {phi_mob:8.3f} deg")
        print(f"        Barton roughness JRC*log10(JCS/sigma'n) = {ra:8.3f} deg   "
              f"(JRC = {jrc}, JCS = {JCS/1e6:.0f} MPa)")
        print(f"        -> phi_r  = {phi_r:8.3f} deg      (deck currently "
              f"{d['residual_friction_angle_degrees']})")
        print(f"        envelope slope d(tau)/d(sigma'_n) at that stage: "
              f"{dtau_dsn(phi_r, jrc, sn):.4f}   "
              f"(deck constants give "
              f"{dtau_dsn(d['residual_friction_angle_degrees'], d['jrc'], sn, d['jcs']):.4f})")
        out[s] = dict(phi_r=phi_r, jrc=jrc, jcs=JCS, sn_onset=sn, tau_onset=tau)
        print()
    print("  Both land inside or just below the measured granite basic-friction range")
    print("  (29-32 deg for a rough saw cut, lower for a lapped one), which the deck")
    print("  values of 8.45 and 7.50 deg do not.\n")
    return out


# ---------------------------------------------------------------------------
# 2. Where the old and new envelopes actually differ
# ---------------------------------------------------------------------------

def envelope_comparison(fit):
    rule("2. The two envelopes across the injection sweep (this is the real change)")
    print("  Both parameterisations pass through the same calibration point, so peak")
    print("  strength is unchanged there. What differs is the SHAPE: the deck's JRC is")
    print("  large enough that the roughness term grows sharply as injection unloads the")
    print("  joint, so the envelope RISES as sigma'_n falls. The deck comments call this")
    print("  the 'LOCK' and several tuning generations were spent fighting it.\n")
    for s in ("SW-S3", "SW-S4"):
        f, d = fit[s], DECK[s]
        t2 = PAPER_TABLE2[s]
        print(f"  {s}")
        print(f"    {'Pi':>4} {'sigma_n':>9} {'tau meas':>9} | "
              f"{'tau_lim deck':>13} {'mu deck':>8} | {'tau_lim new':>12} {'mu new':>8}")
        for i, pi in enumerate(PI_LOAD):
            sn = t2["sn"][i] * 1e6
            td = tau_limit(d["residual_friction_angle_degrees"], d["jrc"], sn,
                           jcs_Pa=d["jcs"])
            tn = tau_limit(f["phi_r"], f["jrc"], sn)
            print(f"    {pi:>4} {sn/1e6:9.2f} {t2['tau'][i]:9.2f} | "
                  f"{td/1e6:13.2f} {td/sn:8.3f} | {tn/1e6:12.2f} {tn/sn:8.3f}")
        print()


# ---------------------------------------------------------------------------
# 3. Slip-weakening stability -- the constraint the deck headers impose
# ---------------------------------------------------------------------------

K_SYS = {"SW-S3": None, "SW-S4": 1.25e11}  # SW-S4's is measured; see deck-49 header.


def stability(fit):
    rule("3. Slip-weakening stability: sigma'_n*(mu_p - mu_r)/D_c vs the system stiffness")
    print("  The deck-21/22 rule: if the weakening slope exceeds k_sys the quasi-static")
    print("  solver meets a strength cliff instead of progressive slip. The tail floor")
    print("  mu_r = tan(slip_weakening_residual_friction_angle) is an ABSOLUTE friction")
    print("  coefficient -- it does not contain JRC or JCS -- so refitting the peak")
    print("  envelope leaves it valid and only changes mu_p.\n")
    tails = {"SW-S3": 8.45, "SW-S4": 6.50}      # unchanged by this refit
    dc = {"SW-S3": 6.0e-5, "SW-S4": 7.45e-5}
    for s in ("SW-S3", "SW-S4"):
        f, d = fit[s], DECK[s]
        sn = f["sn_onset"]
        mu_r = math.tan(math.radians(tails[s]))
        mu_p_old = math.tan(math.radians(phi_peak(d["residual_friction_angle_degrees"],
                                                  d["jrc"], sn, d["jcs"])))
        mu_p_new = math.tan(math.radians(phi_peak(f["phi_r"], f["jrc"], sn)))
        so = sn * (mu_p_old - mu_r) / dc[s]
        sn_ = sn * (mu_p_new - mu_r) / dc[s]
        k = K_SYS[s]
        verdict = ""
        if k:
            verdict = (f"   k_sys = {k:.3g}: deck {'ABOVE' if so > k else 'below'}, "
                       f"new {'ABOVE' if sn_ > k else 'below'}")
        print(f"  {s}  D_c = {dc[s]*1e6:.1f} um, tail phi = {tails[s]} deg "
              f"(mu_r = {mu_r:.4f})")
        print(f"        deck slope {so:.4g} Pa/m   ->   new slope {sn_:.4g} Pa/m "
              f"({100*(sn_/so - 1):+.1f} %){verdict}")
    print("\n  The refit lowers both slopes, so it cannot introduce an instability the")
    print("  current decks do not already have. For SW-S4 it moves the onset slope from")
    print("  just above the measured k_sys to just below it.\n")


# ---------------------------------------------------------------------------
# 4. The tensile pair: cohesion instead of an impossible phi_r
# ---------------------------------------------------------------------------

def refit_tensiles(fit):
    rule("4. Tensile SW-T1 / SW-T2: asperity cohesion instead of phi_r = 44-46 deg")
    c_intact = mohr_coulomb_cohesion(UCS, PHI_INTACT)
    print(f"  The paper's own intact-rock constants (Sec. 2.1: UCS = {UCS/1e6:.0f} MPa,")
    print(f"  internal friction angle = {PHI_INTACT:.0f} deg) imply a Mohr-Coulomb")
    print(f"  cohesion c_intact = UCS*(1-sin phi)/(2 cos phi) = {c_intact/1e6:.2f} MPa.")
    print("  A perfectly mated Mode-I fracture shears through asperities that ARE intact")
    print("  rock, so its cohesion should approach that number.\n")
    print("  Fix phi_r at the basic friction angle measured on this campaign's OWN rough")
    print(f"  saw cut (SW-S3, refitted above: {fit['SW-S3']['phi_r']:.2f} deg) and let")
    print("  cohesion carry the interlock:\n")
    out = {}
    phi_r = fit["SW-S3"]["phi_r"]
    for s in ("SW-T1", "SW-T2"):
        jrc = PAPER_TABLE1[s]["jrc"]
        sn, tau, pi = onset_state(s)
        ra = roughness_angle(jrc, sn)
        frictional = sn * math.tan(math.radians(phi_r + ra))
        c = tau - frictional
        d = DECK[s]
        print(f"  {s}   last stick stage Pi = {pi} MPa,  sigma'_n = {sn/1e6:.2f} MPa, "
              f"tau = {tau/1e6:.2f} MPa   (mu = {tau/sn:.3f})")
        print(f"        JRC = {jrc} (measured), sigma'_n/JCS = {sn/JCS:.2f} -> roughness "
              f"term only {ra:.2f} deg")
        print(f"        frictional part sigma'_n*tan({phi_r + ra:.2f} deg) = "
              f"{frictional/1e6:8.2f} MPa")
        print(f"        -> cohesion c = {c/1e6:8.2f} MPa  = {100*c/c_intact:5.1f} % of "
              f"c_intact")
        print(f"        replaces phi_r = {d['residual_friction_angle_degrees']:.2f} deg "
              f"with c = 0 (deck as it stands)")
        print(f"        envelope slope d(tau)/d(sigma'_n): deck "
              f"{dtau_dsn(d['residual_friction_angle_degrees'], jrc, sn, d['jcs']):.4f}"
              f"  ->  new {dtau_dsn(phi_r, jrc, sn):.4f}")
        # Post-burst residual. At full weakening the roughness term is gone (Barton's own
        # picture: slip destroys roughness, not the rock's basic friction angle), so the
        # tail friction angle is phi_r itself and the tail cohesion is what is left over.
        sn_r, tau_r, pi_r = end_of_loading_state(s)
        c_res = tau_r - sn_r * math.tan(math.radians(phi_r))
        print(f"        post-burst stage Pi = {pi_r} MPa: sigma'_n = {sn_r/1e6:.2f}, "
              f"tau = {tau_r/1e6:.2f} MPa (mu = {tau_r/sn_r:.3f})")
        print(f"        tail phi = phi_r = {phi_r:.2f} deg (roughness destroyed) -> "
              f"residual cohesion c_res = {c_res/1e6:.3f} MPa "
              f"({100*c_res/c:.0f} % of c retained)")
        out[s] = dict(phi_r=phi_r, jrc=jrc, jcs=JCS, cohesion=c, residual_cohesion=c_res,
                      sn_onset=sn, tau_onset=tau)
        print()
    print("  The two cohesions straddle c_intact. That is the expected signature of a")
    print("  fully mated Mode-I fracture and it is a RESULT, not a fitted coincidence:")
    print("  nothing in the derivation knows about c_intact. The phi_r = 44-46 deg")
    print("  parameterisation it replaces has no such interpretation -- it simply")
    print("  exceeds every measured granite basic friction angle.\n")
    print("  NB the slope change is large (~40 %), because cohesion is sigma'_n")
    print("  independent and the phi_r it replaces was not. These two decks are")
    print("  therefore CANDIDATES that must be scored, not drop-in corrections.\n")
    return out


# ---------------------------------------------------------------------------
# 5. Mesh-driven quantities for the rebuilt 30-degree specimens
# ---------------------------------------------------------------------------

MESH30 = {
    # sample: (radius m, length m, theta deg)
    "SW-S4": (0.025255, 0.11870, 30.0),
    "SW-T2": (0.02526, 0.13270, 30.0),
}


def mesh_quantities():
    rule("5. SW-S4 and SW-T2 rebuilt at 30 deg: source nodes and reduction coefficients")
    print("  Table 2 recovers theta from the paper's own equations (3)/(4) via")
    print("  tan(theta) = (sigma'_n - sigma_3 + P_p)/tau, independently of Table 1:")
    print("  SW-S4 -> 30.02 deg (meshed at 28.99 and 2.85 mm off centre),")
    print("  SW-T2 -> 30.00 deg (meshed at 31.00, the value Table 1 prints).\n")
    offset = PAPER_TEST["borehole_offset_from_sidewall_m"]
    for s, (R, L, th) in MESH30.items():
        cot = 1.0 / math.tan(math.radians(th))
        x = R - offset
        zc = L / 2.0
        z_in, z_out = zc - x * cot, zc + x * cot
        print(f"  {s}  R = {R*1e3:.3f} mm, L = {L*1e3:.2f} mm, theta = {th:.1f} deg")
        print(f"        borehole axis {offset*1e3:.1f} mm inside the sidewall -> "
              f"x = {x:.6f} m")
        print(f"        plane z = L/2 + x*cot(theta):")
        print(f"          source_in   coord = '{-x:.6f} 0 {z_in:.6f}'")
        print(f"          source_out  coord = '{x:.6f} 0 {z_out:.6f}'")
        sin, cos = math.sin(math.radians(th)), math.cos(math.radians(th))
        print(f"        paper-frame reduction, eq (3)-(4):")
        print(f"          sin^2(theta)     = {sin*sin:.15f}   "
              f"(effective_normal_paper_frame_mpa_pp)")
        print(f"          sin*cos(theta)   = {sin*cos:.15f}   "
              f"(shear_stress_paper_frame_mpa_pp)")
        print(f"        fracture ellipse area pi D^2/(4 sin theta) = "
              f"{math.pi*(2*R)**2/(4*sin)*1e3:.4f} e-3 m^2")
        print()


# ---------------------------------------------------------------------------
# 6. Flow geometry factor W/L straight from the paper's eq (10)
# ---------------------------------------------------------------------------

def flow_factor():
    rule("6. W/L from the paper's own cubic-law inversion, eq (9)-(10)")
    print("  a_h = (-12 mu L Q / (W dP))^(1/3), so inverting Table 2's own Q, a_h and")
    print("  dP fixes W/L with no modelling assumption. dP = P_i - P_o.\n")
    mu = PAPER_TEST["fluid_viscosity_Pa_s"]
    for s in ("SW-T1", "SW-T2", "SW-S3", "SW-S4"):
        t2 = PAPER_TABLE2[s]
        vals = []
        for i, pi in enumerate(PI_LOAD + [24, 20, 16, 12, 8]):
            dp = (pi - 5) * 1e6
            if dp <= 0:
                continue
            Q = t2["Q"][i] / 6.0e7          # ml/min -> m^3/s
            ah = t2["ah"][i] * 1e-6
            vals.append(12.0 * mu * Q / (ah ** 3 * dp))
        wl = sum(vals) / len(vals)
        print(f"  {s}   W/L = {wl:.12f}   (deck uses "
              f"{'0.81 -- 0.5 % low' if s == 'SW-S4' else 'the Table-2 value'})")
    print()


def main():
    fit = refit_sawcuts()
    envelope_comparison(fit)
    stability(fit)
    refit_tensiles(fit)
    mesh_quantities()
    flow_factor()
    rule("Summary of every constant this script changes")
    print("""
  SW-S3   jrc 23.35 -> 1.96      jcs 3.0e8 -> 1.5e8   phi_r 8.45 -> 29.76 deg
  SW-S4   jrc 17.50 -> 1.19      jcs 3.0e8 -> 1.5e8   phi_r 7.50 -> 23.71 deg
          mesh 28.99 deg / -2.85 mm  ->  30.00 deg / centred
          W/L 0.81 -> the Table-2 value
  SW-T2   mesh 31.00 deg -> 30.00 deg (Table 2 implies 30, Table 1 prints 31)
  SW-T1   phi_r 44.10 -> 29.76 deg + cohesion 24.6 MPa   [CANDIDATE, must be scored]
  SW-T2   phi_r 46.29 -> 29.76 deg + cohesion 31.6 MPa   [CANDIDATE, must be scored]

  Slip-weakening tails, D_c, exponents, dilation angles, normal-closure constants,
  hydraulic constants and every BC are DELIBERATELY untouched: they are calibrated
  against measurements this refit does not change, and the tail floor is already an
  absolute friction coefficient independent of JRC and JCS.
""")


if __name__ == "__main__":
    main()
