#!/usr/bin/env python3
"""
paper_parameter_audit.py -- audit every physical parameter in the four
Ye & Ghassemi (2018) decks against the paper itself.

WHY THIS EXISTS
===============
doc/sample_parameter_unification_2026-08-16.md asked "are the rock parameters the
same in every deck?" and answered it by comparing the decks *to each other*. That
finds drift but cannot find a value that is consistently wrong in all four. This
script asks the other question: **does each deck value match the source paper?**

Everything in PAPER below is transcribed from the PDF (Ye & Ghassemi, JGR Solid
Earth 123, 9009-9032, 2018) -- Sec. 2.1 for the rock, Sec. 2.2 for JRC, Sec. 2.4
for the protocol, Table 1 for geometry, Table 2 for the hold-stage measurements.
Deck values in DECK are transcribed from the current production decks named in
DECK_FILES and are re-checked against those files at run time.

Nothing here is fitted. Where the script derives a quantity (dilation angle,
mobilised friction, the phi_r implied by the paper's own JRC/JCS) the derivation
is the paper's own equation, stated in the function docstring.

Run:  python3 scripts/paper_parameter_audit.py
"""

import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "Examples", "YeGhasemmi2018")

DECK_FILES = {
    "SW-T1": "SWT1/87_01_swt1_bbfast_injfix_kernel_SV_biot0p6.i",
    "SW-T2": "SWT2/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6.i",
    "SW-S3": "SWS3/86_01_sw3_bbfast_biot0p6_phir8p45_m0_kernel_SV.i",
    "SW-S4": "SWS4/68_01_sw4_bbfast_tail6p50_eta3p50_m0_kernel_SV.i",
}

SAMPLES = ["SW-T1", "SW-T2", "SW-S3", "SW-S4"]

# ---------------------------------------------------------------------------
# THE PAPER
# ---------------------------------------------------------------------------

# Sec. 2.1, intact Sierra White granite.
PAPER_ROCK = {
    "youngs_modulus_Pa": 67e9,          # E = 67 GPa
    "poissons_ratio": 0.32,             # nu = 0.32
    "ucs_Pa": 150e6,                    # uniaxial compressive strength 150 MPa
    "intact_friction_angle_deg": 46.0,  # internal friction angle of the INTACT rock
    "tensile_strength_Pa": 11e6,        # T = 11 MPa
    "matrix_perm_lo_m2": 5e-19,         # 5e-19 .. 1e-18 m^2
    "matrix_perm_hi_m2": 1e-18,
    "mean_crystal_size_m": 0.5e-3,
}

# Sec. 2.4 protocol.
PAPER_TEST = {
    "confining_pressure_Pa": 30e6,      # sigma_3
    "production_pressure_Pa": 5e6,      # P_o held constant
    "injection_initial_Pa": 5e6,
    "injection_max_Pa": 28e6,           # >= 2 MPa below sigma_3
    "injection_ramp_rate_Pa_s": 0.03e6,
    "step_duration_s": (300.0, 500.0),  # buildup 150-250 s + hold 150-250 s
    "fluid_viscosity_Pa_s": 1.002e-3,   # water at 20 C
    "borehole_diameter_m": 3.5e-3,
    "borehole_offset_from_sidewall_m": 6.0e-3,
}

# Table 1: geometry. theta measured from the specimen long axis to the plane.
PAPER_TABLE1 = {
    "SW-T1": dict(kind="tensile", L_mm=128.80, D_mm=50.52, theta_deg=32.0, jrc=15.32),
    "SW-T2": dict(kind="tensile", L_mm=132.70, D_mm=50.52, theta_deg=31.0, jrc=14.63),
    "SW-S3": dict(kind="saw cut", L_mm=123.40, D_mm=50.53, theta_deg=29.0, jrc=1.96),
    "SW-S4": dict(kind="polished saw cut", L_mm=118.70, D_mm=50.51, theta_deg=30.0, jrc=1.19),
}

# Table 2: hold-stage measurements. Loading 8..28 then unloading 24..8.
# Columns: Pi (MPa), Q (ml/min), dn (mm), ds (mm), sigma'_n (MPa), tau (MPa),
#          a_h (1e-6 m), k (m^2)
PI_LOAD = [8, 12, 16, 20, 24, 28]
PI_UNLOAD = [24, 20, 16, 12, 8]

PAPER_TABLE2 = {
    "SW-T1": dict(
        Q=[0.053, 0.114, 0.190, 0.280, 0.389, 6.220, 4.270, 2.870, 1.900, 1.120, 0.462],
        dn=[0.000, 0.000, 0.000, -0.001, -0.003, -0.157, -0.139, -0.130, -0.123, -0.118, -0.113],
        ds=[0.000, 0.000, 0.001, 0.002, 0.008, 0.532, 0.539, 0.534, 0.529, 0.525, 0.521],
        sn=[65.47, 63.35, 61.27, 59.14, 56.94, 31.79, 33.45, 35.35, 37.29, 39.22, 41.14],
        tau=[67.16, 66.96, 66.82, 66.63, 66.32, 29.35, 28.72, 28.57, 28.48, 28.36, 28.23],
        ah=[1.63, 1.59, 1.62, 1.66, 1.72, 4.05, 3.81, 3.61, 3.49, 3.40, 3.36],
        k=[0.22e-12, 0.21e-12, 0.22e-12, 0.23e-12, 0.25e-12, 1.37e-12,
           1.21e-12, 1.09e-12, 1.02e-12, 0.97e-12, 0.94e-12]),
    "SW-T2": dict(
        Q=[0.115, 0.276, 0.450, 0.750, 1.505, 11.100, 7.200, 5.150, 3.540, 2.160, 0.910],
        dn=[0.000, -0.001, -0.002, -0.003, -0.005, -0.142, -0.142, -0.139, -0.139, -0.133, -0.130],
        ds=[0.000, 0.001, 0.003, 0.007, 0.015, 0.571, 0.572, 0.566, 0.565, 0.557, 0.552],
        sn=[66.74, 64.53, 62.37, 60.19, 57.88, 29.36, 31.26, 33.23, 35.23, 37.18, 39.14],
        tau=[74.87, 74.54, 74.25, 73.94, 73.40, 27.48, 27.29, 27.24, 27.25, 27.15, 27.09],
        ah=[2.11, 2.13, 2.16, 2.31, 2.69, 4.92, 4.54, 4.39, 4.30, 4.25, 4.21],
        k=[0.37e-12, 0.38e-12, 0.39e-12, 0.44e-12, 0.60e-12, 2.02e-12,
           1.72e-12, 1.61e-12, 1.54e-12, 1.50e-12, 1.48e-12]),
    "SW-S3": dict(
        Q=[0.022, 0.050, 0.078, 0.121, 0.150, 0.860, 0.460, 0.310, 0.210, 0.130, 0.054],
        dn=[0.000, 0.000, 0.000, 0.000, 0.000, -0.044, -0.044, -0.044, -0.043, -0.042, -0.041],
        ds=[0.000, 0.000, 0.000, 0.000, 0.001, 0.071, 0.072, 0.072, 0.073, 0.073, 0.073],
        sn=[31.65, 29.58, 27.53, 25.48, 23.42, 15.25, 17.27, 19.14, 21.01, 22.86, 24.79],
        tau=[14.70, 14.57, 14.48, 14.38, 14.26, 3.55, 3.19, 2.95, 2.68, 2.44, 2.31],
        ah=[1.22, 1.21, 1.20, 1.26, 1.25, 2.10, 1.81, 1.72, 1.68, 1.66, 1.64],
        k=[1.24e-13, 1.21e-13, 1.21e-13, 1.32e-13, 1.30e-13, 3.66e-13,
           2.74e-13, 2.47e-13, 2.34e-13, 2.30e-13, 2.25e-13]),
    "SW-S4": dict(
        Q=[0.005, 0.012, 0.022, 0.035, 0.056, 0.113, 0.064, 0.037, 0.024, 0.013, 0.005],
        dn=[0.000, 0.000, -0.001, -0.008, -0.021, -0.041, -0.038, -0.036, -0.034, -0.033, -0.032],
        ds=[0.000, 0.000, 0.000, 0.017, 0.041, 0.075, 0.077, 0.078, 0.079, 0.079, 0.079],
        sn=[30.75, 28.73, 26.51, 22.92, 19.25, 15.31, 17.13, 19.00, 20.89, 22.82, 24.81],
        tau=[12.56, 12.53, 12.14, 9.38, 6.48, 3.12, 2.82, 2.59, 2.41, 2.28, 2.27],
        ah=[0.74, 0.75, 0.79, 0.83, 0.90, 1.07, 0.94, 0.85, 0.81, 0.77, 0.74],
        k=[0.46e-13, 0.47e-13, 0.52e-13, 0.58e-13, 0.67e-13, 0.95e-13,
           0.74e-13, 0.60e-13, 0.55e-13, 0.49e-13, 0.46e-13]),
}

# Sec. 3 narrative: the stage at which slip becomes appreciable.
PAPER_ONSET_PI_MPa = {"SW-T1": 28, "SW-T2": 28, "SW-S3": 28, "SW-S4": 20}

# ---------------------------------------------------------------------------
# THE DECKS  (values transcribed; verified against the files by check_decks())
# ---------------------------------------------------------------------------

DECK = {
    "SW-T1": dict(youngs_modulus=67e9, poissons_ratio=0.32, biot_coefficient=0.6,
                  matrix_permeability=5e-19, initial_porosity=0.001,
                  fluid_viscosity_ref=1.002e-3, fluid_bulk_modulus=4.7835616438e9,
                  confining_pressure=30e6,
                  jrc=15.32, jcs=1.5e8, residual_friction_angle_degrees=44.1,
                  dilation_angle_peak_degrees=16.44200364,
                  mesh_L_m=0.12880, mesh_R_m=0.02526,
                  mesh_zhi=0.1048244502, mesh_zlo=0.0239755498,
                  pp_theta_deg=32.0, use_kinematic_aperture=True, dilation_scale=0.0,
                  normal_unload_retention_fraction=0.94),
    "SW-T2": dict(youngs_modulus=67e9, poissons_ratio=0.32, biot_coefficient=0.6,
                  matrix_permeability=5e-19, initial_porosity=0.001,
                  fluid_viscosity_ref=1.002e-3, fluid_bulk_modulus=4.7835616438e9,
                  confining_pressure=30e6,
                  jrc=14.63, jcs=1.5e8, residual_friction_angle_degrees=46.29182452,
                  dilation_angle_peak_degrees=13.96539134,
                  mesh_L_m=0.13270, mesh_R_m=0.02526,
                  mesh_zhi=0.1083896997, mesh_zlo=0.0243103003,
                  pp_theta_deg=31.0, use_kinematic_aperture=True, dilation_scale=0.0,
                  normal_unload_retention_fraction=0.84),
    "SW-S3": dict(youngs_modulus=67e9, poissons_ratio=0.32, biot_coefficient=0.6,
                  matrix_permeability=5e-19, initial_porosity=0.001,
                  fluid_viscosity_ref=1.002e-3, fluid_bulk_modulus=4.7835616438e9,
                  confining_pressure=30e6,
                  jrc=23.35, jcs=3.0e8, residual_friction_angle_degrees=8.45,
                  dilation_angle_peak_degrees=26.0,
                  mesh_L_m=0.12440, mesh_R_m=0.025265,
                  mesh_zhi=0.10777927, mesh_zlo=0.01662073,
                  pp_theta_deg=29.0, use_kinematic_aperture=False, dilation_scale=0.038,
                  normal_unload_retention_fraction=0.06),
    "SW-S4": dict(youngs_modulus=67e9, poissons_ratio=0.32, biot_coefficient=0.6,
                  matrix_permeability=5e-19, initial_porosity=0.001,
                  fluid_viscosity_ref=1.002e-3, fluid_bulk_modulus=4.7835616438e9,
                  confining_pressure=30e6,
                  jrc=17.5, jcs=3.0e8, residual_friction_angle_degrees=7.5,
                  dilation_angle_peak_degrees=24.0,
                  mesh_L_m=0.11870, mesh_R_m=0.025255,
                  mesh_zhi=0.10207927, mesh_zlo=0.01092073,
                  pp_theta_deg=30.0, use_kinematic_aperture=False, dilation_scale=0.0117,
                  normal_unload_retention_fraction=0.04),
}

# ---------------------------------------------------------------------------

RED, YEL, GRN, RST = "\033[31m", "\033[33m", "\033[32m", "\033[0m"
if not sys.stdout.isatty():
    RED = YEL = GRN = RST = ""


def flag(ok, warn=False):
    return f"{GRN}ok{RST}" if ok else (f"{YEL}CHECK{RST}" if warn else f"{RED}MISMATCH{RST}")


def rule(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def mesh_theta(d):
    """Angle from the core axis implied by the meshed fracture plane.

    The journal builds the plane through z = z_lo at x = -R and z = z_hi at
    x = +R, so cot(theta) = (z_hi - z_lo) / 2R.
    """
    return math.degrees(math.atan(2.0 * d["mesh_R_m"] / (d["mesh_zhi"] - d["mesh_zlo"])))


def barton_phi_peak(phi_r, jrc, jcs, sn):
    """Barton-Bandis peak friction angle, the form the code evaluates."""
    return min(phi_r + jrc * math.log10(jcs / sn), 85.0)


def phi_r_implied(jrc, jcs, sn, tau):
    """phi_r that puts the Barton-Bandis envelope exactly through (sn, tau)."""
    return math.degrees(math.atan(tau / sn)) - jrc * math.log10(jcs / sn)


def last_stick_index(s, sample):
    """Index of the last hold stage before appreciable slip, from Table 2."""
    return PI_LOAD.index(PAPER_ONSET_PI_MPa[sample]) - 1


# ---------------------------------------------------------------------------


def check_decks():
    """Re-read the decks so the transcription above cannot silently go stale."""
    rule("0. Deck transcription check (guards this script against deck edits)")
    pats = {
        "youngs_modulus": r"^\s*youngs_modulus\s*=\s*(\S+)",
        "poissons_ratio": r"^\s*poissons_ratio\s*=\s*(\S+)",
        "biot_coefficient": r"^\s*biot_coefficient\s*=\s*([0-9.eE+-]+)\s*($|#)",
        "matrix_permeability": r"^\s*matrix_permeability\s*=\s*(\S+)",
        "initial_porosity": r"^\s*initial_porosity\s*=\s*(\S+)",
        "fluid_viscosity_ref": r"^\s*fluid_viscosity_ref\s*=\s*(\S+)",
        "fluid_bulk_modulus": r"^\s*fluid_bulk_modulus\s*=\s*(\S+)",
        "confining_pressure": r"^\s*confining_pressure\s*=\s*(\S+)",
        "jrc": r"^\s*(?:bb_)?jrc\s*=\s*([0-9.eE+-]+)",
        "jcs": r"^\s*(?:bb_)?jcs\s*=\s*([0-9.eE+-]+)",
        "residual_friction_angle_degrees":
            r"^\s*(?:bb_residual_friction_angle|residual_friction_angle_degrees)\s*=\s*([0-9.eE+-]+)",
        "dilation_angle_peak_degrees": r"^\s*dilation_angle_peak_degrees\s*=\s*([0-9.eE+-]+)",
    }
    bad = 0
    for s in SAMPLES:
        path = os.path.join(EX, DECK_FILES[s])
        text = open(path).read()
        for key, pat in pats.items():
            m = re.search(pat, text, flags=re.M)
            if m is None:
                print(f"  {s:6} {key:32} {YEL}not found in deck{RST}")
                continue
            got = float(m.group(1))
            want = DECK[s][key]
            if abs(got - want) > 1e-9 * max(1.0, abs(want)):
                print(f"  {s:6} {key:32} deck={got!r} table={want!r}  {RED}STALE{RST}")
                bad += 1
    print(f"  {GRN}transcription verified{RST}" if bad == 0
          else f"  {RED}{bad} stale entries -- fix DECK before trusting this report{RST}")


def section_geometry():
    rule("1. Geometry: meshed specimen vs Ye & Ghassemi Table 1")
    print(f"{'sample':7} {'L mesh':>8} {'L paper':>8} {'dL mm':>7} "
          f"{'D mesh':>8} {'D paper':>8} {'th mesh':>8} {'th paper':>9} {'th PP':>7}  verdict")
    for s in SAMPLES:
        d, p = DECK[s], PAPER_TABLE1[s]
        thm = mesh_theta(d)
        dL = d["mesh_L_m"] * 1e3 - p["L_mm"]
        dD = 2 * d["mesh_R_m"] * 1e3 - p["D_mm"]
        bad = []
        if abs(dL) > 0.05:
            bad.append(f"length {dL:+.2f} mm")
        if abs(dD) > 0.02:
            bad.append(f"diameter {dD:+.2f} mm")
        if abs(thm - p["theta_deg"]) > 0.02:
            bad.append(f"mesh theta {thm - p['theta_deg']:+.2f} deg")
        if abs(d["pp_theta_deg"] - thm) > 0.02:
            bad.append("postproc theta != mesh theta")
        verdict = f"{GRN}ok{RST}" if not bad else f"{RED}{'; '.join(bad)}{RST}"
        print(f"{s:7} {d['mesh_L_m']*1e3:8.2f} {p['L_mm']:8.2f} {dL:+7.2f} "
              f"{2*d['mesh_R_m']*1e3:8.2f} {p['D_mm']:8.2f} {thm:8.3f} {p['theta_deg']:9.1f} "
              f"{d['pp_theta_deg']:7.1f}  {verdict}")

    print("\n  Effect of the SW-S4 angle error on the paper-frame reduction, eq (3)-(4),")
    print("  evaluated at that specimen's own differential stress:")
    d = DECK["SW-S4"]
    thm, thp = math.radians(mesh_theta(d)), math.radians(30.0)
    t2 = PAPER_TABLE2["SW-S4"]
    for i, pi in enumerate(PI_LOAD):
        sd = t2["tau"][i] / (math.sin(thp) * math.cos(thp))
        tau_m = sd * math.sin(thm) * math.cos(thm)
        sn_m = sd * math.sin(thm) ** 2
        sn_p = sd * math.sin(thp) ** 2
        print(f"    Pi={pi:2d} MPa: sigma_d={sd:6.2f}  tau {t2['tau'][i]:6.2f} -> {tau_m:6.2f} MPa "
              f"({100*(tau_m/t2['tau'][i]-1):+5.2f} %)   sigma_d-term of sigma'_n "
              f"{sn_p:6.2f} -> {sn_m:6.2f} MPa ({100*(sn_m/sn_p-1):+5.2f} %)")


def section_theta_recovery():
    """Recover theta from Table 2 alone, independently of Table 1.

    Table 2 gives both sigma'_n and tau at every hold stage. With sigma_3 and
    P_p known, eq (3) and (4) are two functions of the single unknown sigma_d,
    so their ratio depends on theta alone:

        tan(theta) = (sigma'_n - sigma_3 + P_p) / tau

    It must return the same theta at all eleven stages and agree with Table 1.
    """
    rule("1b. Fracture angle recovered from Table 2 alone (independent of Table 1)")
    s3 = PAPER_TEST["confining_pressure_Pa"] * 1e-6
    po = PAPER_TEST["production_pressure_Pa"] * 1e-6
    print(f"{'sample':7} {'th min':>8} {'th max':>8} {'th median':>10} {'Table 1':>8} "
          f"{'mesh':>8}   verdict")
    for s in SAMPLES:
        t2, p, d = PAPER_TABLE2[s], PAPER_TABLE1[s], DECK[s]
        th = []
        for i, pi in enumerate(PI_LOAD + PI_UNLOAD):
            pp = 0.5 * (pi + po)
            th.append(math.degrees(math.atan((t2["sn"][i] - s3 + pp) / t2["tau"][i])))
        med = sorted(th)[len(th) // 2]
        thm = mesh_theta(d)
        if abs(med - p["theta_deg"]) > 0.2:
            v = (f"{RED}Table 2 implies {med:.1f} deg, Table 1 prints "
                 f"{p['theta_deg']:.0f} deg{RST}")
        elif abs(thm - med) > 0.2:
            v = f"{RED}mesh is cut at {thm:.2f} deg, data was reduced at {med:.1f} deg{RST}"
        else:
            v = f"{GRN}Table 1, Table 2 and the mesh all agree{RST}"
        print(f"{s:7} {min(th):8.3f} {max(th):8.3f} {med:10.3f} {p['theta_deg']:8.1f} "
              f"{thm:8.3f}   {v}")
    print("\n  SW-S3's spread is wider than the others because its stage-6 numerator is a")
    print("  small difference of large numbers sampled across a <10 s burst; treat that one")
    print("  stage as ~10 % uncertain rather than ~1 %.")

    print("\n  Fracture-plane centring (the journal builds the plane at z = (z_hi+z_lo)/2,")
    print("  which must equal half the specimen height):")
    for s in SAMPLES:
        d = DECK[s]
        off = (0.5 * (d["mesh_zhi"] + d["mesh_zlo"]) - 0.5 * d["mesh_L_m"]) * 1e3
        mark = f"{GRN}centred{RST}" if abs(off) < 0.01 else f"{RED}{off:+.2f} mm off centre{RST}"
        print(f"    {s:7} {mark}")


def section_rock():
    rule("2. Rock and fluid properties vs paper Sec. 2.1 / 2.4")
    rows = [
        ("youngs_modulus", "Pa", PAPER_ROCK["youngs_modulus_Pa"], "Sec. 2.1  E = 67 GPa"),
        ("poissons_ratio", "-", PAPER_ROCK["poissons_ratio"], "Sec. 2.1  nu = 0.32"),
        ("matrix_permeability", "m^2", PAPER_ROCK["matrix_perm_lo_m2"],
         "Sec. 2.1  5e-19 .. 1e-18 (deck takes the low end)"),
        ("confining_pressure", "Pa", PAPER_TEST["confining_pressure_Pa"], "Sec. 2.4  sigma_3 = 30 MPa"),
        ("fluid_viscosity_ref", "Pa.s", PAPER_TEST["fluid_viscosity_Pa_s"], "Sec. 2.5  water at 20 C"),
    ]
    for key, unit, want, note in rows:
        vals = [DECK[s][key] for s in SAMPLES]
        ok = all(abs(v - want) <= 1e-9 * abs(want) for v in vals)
        same = len(set(vals)) == 1
        shown = f"{vals[0]:.6g}" if same else "/".join(f"{v:.4g}" for v in vals)
        print(f"  {key:24} {shown:>28} {unit:6} {flag(ok):22} {note}")

    print()
    print("  Parameters with no counterpart in the paper (model choices, not measurements):")
    print(f"    initial_porosity        = {DECK['SW-T1']['initial_porosity']:g}      "
          "not reported by Ye & Ghassemi; granite matrix porosity is typically 0.005-0.01")
    print(f"    biot_coefficient        = {DECK['SW-T1']['biot_coefficient']:g}        "
          "not reported; 0.6 is a literature value for low-porosity granite")
    kf = DECK["SW-T1"]["fluid_bulk_modulus"]
    print(f"    fluid_bulk_modulus      = {kf:.4g} Pa   "
          f"{RED}{kf/2.2e9:.2f}x the bulk modulus of water at 20 C (2.2e9 Pa){RST}")
    print("      -> enters only 1/M = (alpha-phi)/K_s + phi/K_f; with phi = 1e-3 the")
    print("         matrix storage error is negligible, but the same value is handed to")
    print("         the fracture fluid, where storage is not negligible during the burst.")


def section_jrc():
    rule("3. Joint constants vs paper Sec. 2.2 (JRC) and Sec. 2.1 (JCS <= UCS)")
    print(f"{'sample':7} {'JRC deck':>9} {'JRC paper':>10} {'ratio':>7}   "
          f"{'JCS deck':>10} {'UCS paper':>10} {'ratio':>7}   {'phi_r deck':>11}")
    for s in SAMPLES:
        d, p = DECK[s], PAPER_TABLE1[s]
        jr, jp = d["jrc"], p["jrc"]
        note = ""
        if abs(jr - jp) > 0.01:
            note = f"  {RED}<-- {jr/jp:.1f}x the measured value{RST}"
            if jr > 20.0:
                note += f" {RED}and outside Barton's 0-20 scale{RST}"
        print(f"{s:7} {jr:9.2f} {jp:10.2f} {jr/jp:7.2f}   {d['jcs']:10.3g} "
              f"{PAPER_ROCK['ucs_Pa']:10.3g} {d['jcs']/PAPER_ROCK['ucs_Pa']:7.2f}   "
              f"{d['residual_friction_angle_degrees']:11.2f}{note}")

    print("\n  What phi_r WOULD have to be if the paper's own JRC and JCS = UCS were used,")
    print("  fixing the envelope to pass through the last stick stage of Table 2:")
    print(f"  {'sample':7} {'onset Pi':>9} {'sigma_n':>8} {'tau':>7} {'mu':>6} "
          f"{'phi_mob':>8} {'JRC term':>9} {'phi_r req':>10}   assessment")
    for s in SAMPLES:
        p, t2, d = PAPER_TABLE1[s], PAPER_TABLE2[s], DECK[s]
        i = last_stick_index(t2, s)
        sn, tau = t2["sn"][i], t2["tau"][i]
        mu = tau / sn
        rough = p["jrc"] * math.log10(PAPER_ROCK["ucs_Pa"] / (sn * 1e6))
        req = phi_r_implied(p["jrc"], PAPER_ROCK["ucs_Pa"], sn * 1e6, tau * 1e6)
        if 25.0 <= req <= 35.0:
            a = f"{GRN}within the granite basic-friction range (29-32 deg){RST}"
        elif req < 25.0:
            a = f"{YEL}low, but defensible for a lapped surface{RST}"
        else:
            a = f"{RED}above any measured granite basic friction angle{RST}"
        print(f"  {s:7} {PI_LOAD[i]:9d} {sn:8.2f} {tau:7.2f} {mu:6.3f} "
              f"{math.degrees(math.atan(mu)):8.2f} {rough:9.2f} {req:10.2f}   {a}")

    print("\n  Envelope stress-sensitivity d(tau)/d(sigma'_n), the quantity injection actually")
    print("  sweeps -- deck constants against paper constants, at the same stress:")
    print(f"  {'sample':7} {'sigma_n':>8} {'deck mu':>8} {'paper mu':>9} "
          f"{'deck dtau/dsn':>14} {'paper dtau/dsn':>15}")
    for s in SAMPLES:
        d, p, t2 = DECK[s], PAPER_TABLE1[s], PAPER_TABLE2[s]
        i = last_stick_index(t2, s)
        sn = t2["sn"][i] * 1e6
        req = phi_r_implied(p["jrc"], PAPER_ROCK["ucs_Pa"], sn, t2["tau"][i] * 1e6)

        def dtau(phi_r, jrc, jcs):
            h = sn * 1e-4
            f = lambda x: x * math.tan(math.radians(barton_phi_peak(phi_r, jrc, jcs, x)))
            return (f(sn + h) - f(sn - h)) / (2 * h)

        mu_d = math.tan(math.radians(barton_phi_peak(
            d["residual_friction_angle_degrees"], d["jrc"], d["jcs"], sn)))
        mu_p = math.tan(math.radians(barton_phi_peak(req, p["jrc"], PAPER_ROCK["ucs_Pa"], sn)))
        print(f"  {s:7} {sn*1e-6:8.2f} {mu_d:8.3f} {mu_p:9.3f} "
              f"{dtau(d['residual_friction_angle_degrees'], d['jrc'], d['jcs']):14.3f} "
              f"{dtau(req, p['jrc'], PAPER_ROCK['ucs_Pa']):15.3f}")


def section_dilation():
    rule("4. Dilation angle vs Table 2, and the dissipation bound tan(psi) <= mu")
    print(f"{'sample':7} {'|dn| mm':>8} {'ds mm':>7} {'psi Table2':>11} {'psi deck':>9} "
          f"{'mu at onset':>12} {'atan(mu)':>9}   verdict")
    for s in SAMPLES:
        t2, d = PAPER_TABLE2[s], DECK[s]
        j = PI_LOAD.index(28)                       # end of the loading path
        dn, ds = abs(t2["dn"][j]), t2["ds"][j]
        psi_meas = math.degrees(math.atan(dn / ds)) if ds > 0 else float("nan")
        i = last_stick_index(t2, s)
        mu = t2["tau"][i] / t2["sn"][i]
        phi_mu = math.degrees(math.atan(mu))
        if psi_meas > phi_mu:
            v = (f"{RED}Table-2 psi EXCEEDS atan(mu): the measured d_n cannot be "
                 f"shear dilation alone{RST}")
        elif abs(psi_meas - d["dilation_angle_peak_degrees"]) < 0.05:
            v = f"{GRN}deck value is the Table-2 value{RST}"
        else:
            v = f"{YEL}deck differs from Table 2 by {d['dilation_angle_peak_degrees']-psi_meas:+.2f} deg{RST}"
        print(f"{s:7} {dn:8.3f} {ds:7.3f} {psi_meas:11.2f} "
              f"{d['dilation_angle_peak_degrees']:9.2f} {mu:12.3f} {phi_mu:9.2f}   {v}")

    print("\n  Irreversible (retained) fraction of dilation, Table 2, peak -> end of unload:")
    print(f"  {'sample':7} {'dn peak':>8} {'dn end':>8} {'retained':>9} {'recovered':>10}")
    for s in SAMPLES:
        t2 = PAPER_TABLE2[s]
        pk, end = abs(t2["dn"][5]), abs(t2["dn"][-1])
        print(f"  {s:7} {pk:8.3f} {end:8.3f} {end/pk:9.1%} {1-end/pk:10.1%}")


def section_flow():
    rule("5. Flow reduction: the paper's own cubic-law inversion, eq (9)-(10)")
    print("  Check that a_h in Table 2 is reproduced by eq (10) from the tabulated Q,")
    print("  which fixes the geometry factor W/L each deck must use.\n")
    print(f"  {'sample':7} {'W/L from Table 2':>17} {'W/L in deck':>12} {'ratio':>7}   "
          f"{'implied borehole offset':>24}")
    mu_f = PAPER_TEST["fluid_viscosity_Pa_s"]
    deck_wl = {"SW-T1": 0.814323680496, "SW-T2": 0.813242611781,
               "SW-S3": 0.81, "SW-S4": 0.81}
    for s in SAMPLES:
        t2, p, d = PAPER_TABLE2[s], PAPER_TABLE1[s], DECK[s]
        # eq (9): Q = (W/L) a_h^3 dP / (12 mu)  ->  W/L = 12 mu Q / (a_h^3 dP)
        vals = []
        for i, pi in enumerate(PI_LOAD + PI_UNLOAD):
            dP = (pi - 5.0) * 1e6
            Q = t2["Q"][i] / 6.0e7          # ml/min -> m^3/s
            ah = t2["ah"][i] * 1e-6
            vals.append(12.0 * mu_f * Q / (ah ** 3 * dP))
        med = sorted(vals)[len(vals) // 2]
        R = d["mesh_R_m"]
        th = math.radians(p["theta_deg"])
        A = math.pi * R * R / math.sin(th)
        L = math.sqrt(A / med)
        off = (R - 0.5 * L * math.sin(th)) * 1e3
        print(f"  {s:7} {med:17.3f} {deck_wl[s]:12.3f} {med/deck_wl[s]:7.3f}   "
              f"{off:19.2f} mm")
    print(f"\n  Paper Sec. 2.3 places the boreholes 6.00 mm from the sidewall "
          f"(3.5 mm diameter, so the axis is 6 + 1.75 = 7.75 mm in if the 6 mm is to the")
    print("  borehole wall). The spread above is the L ambiguity the manuscript already")
    print("  quotes as a ~7 % systematic on a_h; it is a real ambiguity in the source, not")
    print("  a modelling error, and W/L enters Q linearly.")


def section_protocol():
    rule("6. Injection protocol vs paper Sec. 2.4")
    print(f"  confining sigma_3       30 MPa      decks 30e6           {flag(True)}")
    print(f"  production P_o           5 MPa      (held constant)")
    print(f"  injection 5 -> 28 MPa at 0.03 MPa/s; 6 loading holds + 5 unloading holds = 11")
    print(f"  each step 300-500 s (150-250 s ramp + 150-250 s hold)")
    print(f"  P_i capped >= 2 MPa below sigma_3, hence the 28 MPa maximum\n")
    ramp = PAPER_TEST["injection_ramp_rate_Pa_s"]
    print(f"  A 4 MPa increment at {ramp*1e-6:.2f} MPa/s takes "
          f"{4e6/ramp:.0f} s -- consistent with the stated 150-250 s buildup.")
    print("  Decks drive injection through a PiecewiseLinear `injection_pressure`")
    print("  function rebuilt on 2026-08-16 from the digitized curve; the ramp rate is")
    print("  therefore inherited from the measurement, not from the nominal 0.03 MPa/s.")


def section_summary():
    rule("7. Findings, ordered by how much they move a published number")
    items = [
        ("SW-S3", "JRC = 23.35 against a measured 1.96, and above Barton's 0-20 scale",
         "changes d(tau)/d(sigma'_n), i.e. the slip-onset trajectory under injection"),
        ("SW-S4", "JRC = 17.50 against a measured 1.19",
         "same; SW-S4 is the discriminating specimen for the envelope"),
        ("SW-S3/S4", "JCS = 300 MPa against a measured UCS of 150 MPa",
         "doubles the roughness term's reference stress"),
        ("SW-S3/S4", "phi_r = 8.45 / 7.50 deg, compensating for the two rows above",
         "no granite joint has a basic friction angle below 20 deg"),
        ("SW-T1/T2", "phi_r = 44.1 / 46.3 deg",
         "carries the interlock of a mated tensile fracture because "
         "computeCohesionEffective() is hard-coded to 0"),
        ("SW-S4", "meshed fracture angle 28.99 deg against a published 30 deg",
         "the journal reuses SW-S3's plane offsets; contradicts the manuscript's own "
         "claim of theta recovered to 0.03 deg"),
        ("SW-S3", "meshed length 124.40 mm against a published 123.40 mm",
         "0.8 % on specimen length; also wrong in the manuscript's Table 1"),
        ("all", "fluid_bulk_modulus = 4.78 GPa against 2.2 GPa for water",
         "negligible in the matrix at phi = 1e-3, not negligible in the fracture"),
        ("SW-S3/S4", "dilation angle set below the Table-2 value",
         "Table-2 psi exceeds atan(mu) for both saw cuts, so the measured d_n "
         "cannot be shear dilation alone"),
    ]
    for i, (who, what, why) in enumerate(items, 1):
        print(f"  {i}. [{who}] {what}\n       -> {why}")


def main():
    check_decks()
    section_geometry()
    section_theta_recovery()
    section_rock()
    section_jrc()
    section_dilation()
    section_flow()
    section_protocol()
    section_summary()
    print()


if __name__ == "__main__":
    main()
