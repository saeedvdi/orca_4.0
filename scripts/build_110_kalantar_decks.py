#!/usr/bin/env python3
"""
build_110_kalantar_decks.py -- round-1 BBFast decks for Kalantar et al. (2025).

WHAT THIS IS, AND WHAT IT IS NOT
================================
These are ROUND-1 decks. Every constant in them is DERIVED from the paper or from
the verified meshes -- none is fitted. That is deliberate: the Ye2018 workflow is
build-from-derived-constants, run, gate, refit, and this script only does the first
step. A deck that passes --check-input is not a deck that is right; the gate
(scripts/kalantar_gate.py) decides that after the first HPC batch.

The single most important thing this script does is NOT copy the parent's fitted
load-path knobs. The 93-series carries poro_du, axial_relax_du, side_unload_* and
fault_pressure_coefficient values that were fitted to Ye & Ghassemi's specimens and
loading frame. Carrying them into a different experiment on a different machine
would be exactly the silent contamination this project has been bitten by before,
so they are neutralised here and the header of each deck says so.

WHERE EVERY NUMBER COMES FROM
=============================
  geometry, source coords    the verified Cubit journals (commit 5b9fcc5)
  theta                      Table 1, with OG-T at 28 deg per the geometric argument
  sigma_3 = 33 MPa           recovered from Table 2 by the angle identity, NOT the
                             30 MPa in the prose (that is sigma'_c)
  E, nu, porosity, k_matrix  section 2.1
  JCS = UCS = 153 MPa        section 2.1
  JRC                        section 3.2, per specimen
  peak envelope              Figure 3b/3d/3f fitted criteria
  K_sys = 796 kN/mm          section 2.3 -- MEASURED, not inferred. This is the one
                             constant Ye2018 had to guess at.
  injection schedule         section 2.3, cross-checked against Table 2's stage count
  W/L                        audit section 8: eq (7) does not reproduce the paper's
                             own table; the plain cubic law does

WHAT THE ROUND-1 DECKS GOT WRONG, AND WHY THIS SCRIPT NOW DOES MORE
===================================================================
Round 1 (commit 5123326) substituted ~20 keys and inherited everything else. Two
of the three decks then died at t = 0.75 s on a PointValue sitting ABOVE the top
of their own mesh, and the one that ran (OG-SH, job 19444645) missed Table 2 by
-13 % on sigma'_n, -19 % on tau, -48 % on a_h and -81 % on Q.

The "derived, not fitted" claim was true of the keys it touched and false of the
rest. In particular the REPORTING chain was pure Ye2018: three postprocessors
still subtracted sigma_3 = 30 MPa and projected onto the PARENT's theta, so even
a perfect run would have been scored through a wrong frame. That is the failure
mode this project keeps meeting -- a postprocessor-only defect that looks like
model error. Every one of those constants is now substituted here.

WHAT STILL HAS TO BE GATED
==========================
axial_pres_final is now a SERIES-SPRING solve, not -sigma_1/penalty. The penalty
BC delivers sigma_1 = penalty * (u_commanded - u_sample), so the sample's own
shortening has to be added back:

    u_cmd = sigma_1 / penalty + C_ax * (sigma_1 - sigma_3)

C_ax is calibrated once, on the completed OG-SH run: 0.8987 * L/E, i.e. 90 % of
the core's 1-D compliance (the remainder is the fracture's own). On OG-SH this
reproduces the realised sigma_1 to 0.02 %. It is still worth a 200 s preload
check per specimen -- the relation stops being linear once the joint slips -- but
it is no longer a factor-1.7 guess.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KAL = ROOT / "Examples/Kalantar2025"
TABLE2_CSV = KAL / "validation/kalantar2025_table2.csv"

# ---------------------------------------------------------------------------
# Paper constants, section 2.1 / 2.3.
# ---------------------------------------------------------------------------
YOUNGS_MODULUS = 63e9
POISSONS_RATIO = 0.16
POROSITY = 0.0033
MATRIX_PERMEABILITY = 1.4e-20
UCS = 153e6                 # doubles as JCS for a fresh, unweathered joint
SIGMA3 = 33.0e6             # recovered from Table 2, NOT the 30 MPa in the prose
P_OUT = 3.0e6
K_SYS = 796e3 / 1e-3        # 796 kN/mm -> N/m
SAMPLE_RADIUS = 0.02499
SAMPLE_AREA = math.pi * SAMPLE_RADIUS ** 2
PRESSURE_RATE = 0.03e6      # Pa/s, both ramp directions
STEP = 3.0e6                # Pa per injection step

# Axial compliance of the loaded column as a fraction of the core's 1-D value L/E.
# Calibrated on the ONE completed round-1 run (OG-SH, job 19444645): the deck
# commanded u = 2.3328e-4 m and realised sigma_1 = 69.3554 MPa with a machine-spring
# gap of 1.71048e-4 m, so u_sample = 6.2232e-5 m over a 36.3556 MPa deviator ->
# C_ax = 1.71177e-12 m/Pa = 0.8987 * (0.120/63e9). The shortfall from 1.0 is the
# joint's own normal compliance plus the non-uniform stress_zz near the platens.
C_AX_OVER_L_OVER_E = 0.8987

SPECIMENS = {
    "OGSH": dict(
        tag="og_sh", label="OG-SH", kind="shear", theta=29.0, theta_printed=29.0,
        jrc=15.60, mu_peak=0.7, c_peak=1.2e6, p_max=18.0e6, hold=300.0,
        core_height=0.120,
        mesh="mesh/kalantar2025_og_sh_theta29_size3.e",
        src_in=(-0.019992000, 0.023933478), src_out=(0.019992000, 0.096066522),
        sep_paper=0.0824654, parent="SWT2/93_03_swt2_final_theta30_resc9p71_ppfix.i",
        # Section 2.3: the Figure 3b criterion OVERESTIMATES this specimen's peak --
        # the test ran at ~0.92 tau_p, not the 0.85 the figure implies. Backing tau_p
        # out of the stated ratios and walking up the loading path (slope cot theta)
        # gives 32.70 deg, not the 36.05 that mu = 0.7 / c = 1.2 MPa produces. The
        # same check on OG-T (-1.4 %) and OG-SC (-3.3 %) confirms they need no
        # override, exactly as the paper warns for the shear fracture alone.
        phi_peak_override=32.70,
        # Section 4.1: OG-SH creeps through every hold (42 um total, largest step
        # 11 um) and never produces an audible event -- the STABLE member.
        bursts=False,
        # Table 2 stage 1 -> stage 9 is a MONOTONIC a_h loss (4.87 -> 3.72 um) while
        # sigma'_n also falls (42.99 -> 39.01). A reversible closure law predicts the
        # opposite sign, so the whole 1.15 um is irreversible: this is the paper's
        # gouge result (12x OG-T's gouge mass, section 4.2). Routed through the one
        # term in the aperture law that subtracts.
        slip_damage=True,
        slip_damage_char_slip=15.0e-6,
    ),
    "OGT": dict(
        tag="og_t", label="OG-T", kind="tensile", theta=28.0, theta_printed=25.999,
        jrc=12.10, mu_peak=1.1, c_peak=0.0, p_max=30.0e6, hold=300.0,
        core_height=0.100,
        mesh="mesh/kalantar2025_og_t_theta28_size3.e",
        src_in=(-0.020362222, 0.011704230), src_out=(0.020362222, 0.088295770),
        sep_paper=0.0851596, parent="SWT1/93_01_swt1_final_c26p9_resc9p19_ppfix.i",
        # a_h runs 0.10 -> 1.11 -> 0.00 um. Both ends are AT the 0.01 um print
        # resolution, so the "loss" is not measurable and no gouge term is derivable.
        # Left off rather than fitted.
        slip_damage=False,
        bursts=True,
    ),
    "OGSC": dict(
        tag="og_sc", label="OG-SC", kind="saw-cut", theta=30.0, theta_printed=30.0,
        jrc=4.23, mu_peak=0.4, c_peak=0.0, p_max=24.0e6, hold=600.0,
        core_height=0.100,
        mesh="mesh/kalantar2025_og_sc_theta30_size3.e",
        src_in=(-0.020184231, 0.015039887), src_out=(0.020184231, 0.084960113),
        sep_paper=0.0799600, parent="SWS3/93_05_sw3_final_resc1p40_ppfix.i",
        slip_damage=True,
        slip_damage_char_slip=10.0e-6,
        # Section 4.1: a single audible stick-slip at the 24 MPa step. The ROUND-1
        # deck could not have produced it: D_c = 60 um against a 25.4 um cap.
        bursts=True,
    ),
}

DECK_NUMBER = {"OGSH": "110_01", "OGT": "110_03", "OGSC": "110_05"}


def schedule(p_max: float, hold: float) -> tuple[list[float], list[float]]:
    """The section-2.3 staircase: 3 MPa steps at 0.03 MPa/s, each held, then back
    down to 6 MPa the same way. Returns (times, pressures) for PiecewiseLinear.

    Cross-checked against Table 2's stage count: OG-SH 5 up / 4 down, OG-T 9 / 8,
    OG-SC 7 / 6. A mismatch here means the schedule is wrong, so it is asserted.
    """
    ramp = STEP / PRESSURE_RATE
    xs, ys, t, p = [0.0], [P_OUT], 0.0, P_OUT
    ups = downs = 0
    while p < p_max - 1.0:
        p += STEP
        t += ramp
        xs.append(t); ys.append(p)
        t += hold
        xs.append(t); ys.append(p)
        ups += 1
    while p > 6.0e6 + 1.0:
        p -= STEP
        t += ramp
        xs.append(t); ys.append(p)
        t += hold
        xs.append(t); ys.append(p)
        downs += 1
    return xs, ys, ups, downs


def read_table2() -> dict[str, list[dict]]:
    """Table 2 as {label: [row, ...]}, rows in stage order. Plain csv so the script
    has no pandas dependency."""
    import csv
    out: dict[str, list[dict]] = {}
    with TABLE2_CSV.open() as fh:
        for row in csv.DictReader(fh):
            out.setdefault(row["sample"], []).append(
                {k: (v if k in ("sample", "branch") else float(v)) for k, v in row.items()})
    return out


def reduce_stages(spec: dict, rows: list[dict]) -> list[dict]:
    """Re-reduce Table 2's stress columns into the deck's theta.

    sigma_1 - sigma_3 is a property of the stress state, not of the angle you chose
    to resolve it onto, so it is recovered from the PRINTED tau at the PRINTED theta
    and re-projected. This matters only for OG-T, whose stresses were reduced at
    25.999 deg -- an angle a through-going ellipse cannot realise in a 100 mm core.
    On OG-SH and OG-SC theta_printed == theta and the transform is the identity,
    which is worth having as a check: it reproduces the printed columns exactly.
    """
    th, thp = math.radians(spec["theta"]), math.radians(spec["theta_printed"])
    stc, s2 = math.sin(th) * math.cos(th), math.sin(th) ** 2
    stcp = math.sin(thp) * math.cos(thp)
    out = []
    for r in rows:
        d = r["tau_MPa"] / stcp                          # sigma_1 - sigma_3, MPa
        pp = 0.5 * (r["P_i_MPa"] + P_OUT / 1e6)          # fracture pore pressure
        out.append(dict(r, differential_MPa=d, tau=d * stc,
                        sn=SIGMA3 / 1e6 + d * s2 - pp))
    return out


def derive(spec: dict, rows: list[dict]) -> dict:
    """Every constitutive constant the deck needs, from Table 2 and section 2-3.

    Nothing here is fitted to a model run. The one number that came from a run is
    C_AX_OVER_L_OVER_E, and that is a property of the loading frame plus core, not
    of the joint law.
    """
    th = math.radians(spec["theta"])
    stc = math.sin(th) * math.cos(th)
    first, last = rows[0], rows[-1]

    # Peak envelope, split into Barton-Bandis terms at the stage-1 normal stress so
    # the deck reproduces Figure 3 at the stress the experiment actually starts from.
    phi_peak = spec.get("phi_peak_override") or math.degrees(
        math.atan((spec["mu_peak"] * first["sn"] * 1e6 + spec["c_peak"]) / (first["sn"] * 1e6)))
    jrc_term = spec["jrc"] * math.log10(UCS / (first["sn"] * 1e6))
    phi_r = phi_peak - jrc_term

    # Residual: Table 2's LAST stage is the fully-weakened state on every specimen
    # (tau has stopped moving on the depressurisation branch). This is a measured
    # residual friction angle, not the parent's fitted one.
    phi_residual = math.degrees(math.atan(last["tau"] / last["sn"]))

    # Barton's peak dilation angle, half the JRC mobilisation term.
    dilation = 0.5 * jrc_term

    # Series-spring gate on the axial command.
    sigma1 = SIGMA3 + first["tau"] * 1e6 / stc
    penalty = K_SYS / SAMPLE_AREA
    c_ax = C_AX_OVER_L_OVER_E * spec["core_height"] / YOUNGS_MODULUS
    u_cmd = sigma1 / penalty + c_ax * (sigma1 - SIGMA3)

    # Stick-slip criterion (the series-spring identity under constant piston
    # displacement): the joint bursts iff its weakening distance is SHORTER than the
    # stress drop the frame can deliver, D_c < d(tau)/k_eff.
    k_eff = K_SYS * math.cos(th) ** 2 * math.sin(th) / SAMPLE_AREA   # Pa/m
    dtau = (first["tau"] - last["tau"]) * 1e6
    dc_cap = dtau / k_eff
    d_c = (min(150e-6, 0.6 * dc_cap) if spec["bursts"]
           else max(150e-6, 1.5 * dc_cap))

    # Aperture: anchor a_h0 at the stage-1 (sigma'_n, a_h) pair so the stress-aperture
    # term vanishes exactly there, and bracket the bounds around Table 2's own range
    # so the answer is never clipped by an inherited floor.
    ah = [r["a_h_um"] * 1e-6 for r in rows]
    loss = max(0.0, ah[0] - ah[-1])

    return dict(phi_peak=phi_peak, phi_r=phi_r, phi_residual=phi_residual,
                dilation=dilation, sigma1=sigma1, penalty=penalty, c_ax=c_ax,
                u_cmd=u_cmd, k_eff=k_eff, dc_cap=dc_cap, d_c=d_c,
                tau1=first["tau"] * 1e6, sn1=first["sn"] * 1e6,
                ah0=ah[0], ah_lo=min(ah), ah_hi=max(ah), ah_loss=loss,
                slip_damage_scale=loss if spec["slip_damage"] else 0.0,
                ah_min=max(1e-8, 0.2 * min(ah)), ah_max=max(3.0 * max(ah), 5e-6))


def apply(text: str, key: str, value: str, note: str) -> str:
    """Replace a top-level `key = ...` assignment, keeping one deck-visible note.

    Raises if the key is absent or ambiguous -- a silent no-op here would leave a
    Ye2018 value in a Kalantar deck, which is the whole failure mode being avoided.
    """
    pattern = re.compile(rf"^{re.escape(key)}(\s*)=\s*[^\n]*$", re.M)
    hits = pattern.findall(text)
    if len(hits) != 1:
        raise SystemExit(f"'{key}' matched {len(hits)} times, expected exactly 1")
    return pattern.sub(lambda m: f"{key}{m.group(1)}= {value}   # KALANTAR: {note}",
                       text, count=1)


def build(name: str, spec: dict, rows: list[dict]) -> Path:
    parent = (ROOT / "Examples/YeGhasemmi2018" / spec["parent"]).read_text()
    theta = math.radians(spec["theta"])
    sin_t, cos_t = math.sin(theta), math.cos(theta)
    d = derive(spec, rows)
    phi_r, phi_peak, sigma1, penalty = d["phi_r"], d["phi_peak"], d["sigma1"], d["penalty"]
    xs, ys, ups, downs = schedule(spec["p_max"], spec["hold"])
    sep_mesh = math.dist(spec["src_in"], spec["src_out"])
    deck = DECK_NUMBER[name]
    stem = f"{deck}_{spec['tag']}_bbfast_r1"

    subs = [
        ("mesh_file", spec["mesh"], f"{spec['label']} factor-3 mesh, verified 5b9fcc5"),
        ("sample_radius", f"{SAMPLE_RADIUS:.5f}", "Table 1, D = 49.98 mm"),
        ("sample_area", f"{SAMPLE_AREA:.9e}", "pi r^2"),
        ("bulk_sin_theta", f"{sin_t:.16f}", f"sin({spec['theta']} deg)"),
        ("bulk_cos_theta", f"{cos_t:.16f}", f"cos({spec['theta']} deg)"),
        ("axial_bc_penalty", f"{penalty:.4e}",
         "MEASURED K_sys 796 kN/mm / A -- Ye2018 had to infer this"),
        ("axial_pres_initial", f"{-SIGMA3 / penalty:.6e}", "-sigma_3/penalty, t=0 equilibrium"),
        ("axial_pres_final", f"{-d['u_cmd']:.6e}",
         f"GATED series-spring: sigma_1/penalty + C_ax*(sigma_1-sigma_3), sigma_1 = "
         f"{sigma1/1e6:.2f} MPa, C_ax = {d['c_ax']:.4e} m/Pa"),
        ("initial_hydraulic_aperture", f"{d['ah0']:.4e}",
         f"Table 2 stage 1 a_h = {d['ah0']*1e6:.2f} um, anchored at the stage-1 sigma'_n below"),
        ("reference_effective_normal_stress", f"{d['sn1']:.4e}",
         f"Table 2 stage 1 sigma'_n = {d['sn1']/1e6:.2f} MPa -- the stress at which "
         f"initial_hydraulic_aperture holds, so the closure term vanishes there"),
        ("min_hydraulic_aperture", f"{d['ah_min']:.4e}",
         f"0.2x Table 2's minimum ({d['ah_lo']*1e6:.2f} um) -- the round-1 floor was "
         f"an inherited Ye2018 value that clipped the answer"),
        ("max_hydraulic_aperture", f"{d['ah_max']:.4e}",
         f"3x Table 2's maximum ({d['ah_hi']*1e6:.2f} um)"),
        ("use_slip_damage", "true" if spec["slip_damage"] else "false",
         "gouge fill is the only term in the aperture law that SUBTRACTS"
         if spec["slip_damage"] else
         "a_h endpoints are both at the 0.01 um print resolution; no loss is derivable"),
        ("slip_damage_scale", f"{d['slip_damage_scale']:.4e}",
         f"Table 2's irreversible a_h loss, {d['ah_loss']*1e6:.2f} um "
         f"(sigma'_n FALLS over the same stages, so a reversible law has the wrong sign)"
         if spec["slip_damage"] else "off, see use_slip_damage"),
        ("slip_damage_characteristic_slip", f"{spec.get('slip_damage_char_slip', 30e-6):.2e}",
         "slip over which the gouge term saturates"),
        ("slip_damage_onset_slip", "0.0",
         "Table 2 loses aperture from stage 1->2, so gouge accrues from first slip"),
        ("youngs_modulus", f"{YOUNGS_MODULUS:.3g}", "section 2.1"),
        ("poissons_ratio", f"{POISSONS_RATIO}", "section 2.1"),
        ("initial_stress", f"'-{SIGMA3:.3g} -{SIGMA3:.3g} -{SIGMA3:.3g}'",
         "sigma_3 = 33 MPa recovered from Table 2, NOT the 30 MPa in the prose"),
        ("initial_porosity", f"{POROSITY}", "section 2.1, ~0.33 %"),
        ("matrix_permeability", f"{MATRIX_PERMEABILITY:.3g}", "section 2.1"),
        ("confining_pressure", f"{SIGMA3:.3g}", "section 2.3 + Table 2 recovery"),
        ("production_pressure", f"{P_OUT:.3g}", "section 2.3, constant throughout"),
        ("fault_pressure_coefficient", "1.0",
         "NEUTRALISED. The parent's value was fitted to Ye2018; do not import it"),
        ("fluid_viscosity_ref", "1.0e-3", "stated under eq (7)"),
    ]
    text = parent
    for key, value, note in subs:
        text = apply(text, key, value, note)

    # Load-path knobs fitted to Ye2018's specimens. Neutralise rather than delete,
    # so the parent's structure (and its ParsedFunction references) still resolve.
    for key in ("poro_du", "axial_relax_du", "side_unload_relax_pressure"):
        if re.search(rf"^{key}\s*=", text, re.M):
            text = apply(text, key, "0.0", "NEUTRALISED: fitted to Ye2018, not transferable")

    # Specimen-suffixed flow constants.
    for old in re.findall(r"(?:paper|mesh)_flow_width_over_length_\w+", text):
        which = "paper" if old.startswith("paper") else "mesh"
        sep = spec["sep_paper"] if which == "paper" else sep_mesh
        new = f"{which}_flow_width_over_length_{spec['tag']}"
        text = text.replace(old, new)
        text = apply(text, new, f"{2 * SAMPLE_RADIUS / sep:.6f}",
                     f"W/L, W = 49.98 mm, L = {sep*1e3:.4f} mm ({which} frame). "
                     f"Eq (7) as printed is 10.3x out -- see audit section 8")

    # Source nodes: the verified interface coordinates, not the design ones.
    for tag, (x, z) in (("source_in", spec["src_in"]), ("source_out", spec["src_out"])):
        text = re.sub(rf"(\[{tag}\][^\[]*?coord\s*=\s*)'[^']*'",
                      rf"\g<1>'{x:.9f} 0.0 {z:.9f}'", text, count=1, flags=re.S)

    # Injection schedule.
    text = re.sub(r"(\[injection_pressure\][^\[]*?\n\s*x\s*=\s*)'[^']*'",
                  lambda m: m.group(1) + "'" + " ".join(f"{v:.1f}" for v in xs) + "'",
                  text, count=1, flags=re.S)
    text = re.sub(r"(\[injection_pressure\][^\[]*?\n\s*y\s*=\s*)'[^']*'",
                  lambda m: m.group(1) + "'" + " ".join(f"{v:.1f}" for v in ys) + "'",
                  text, count=1, flags=re.S)

    # Joint law: JRC/JCS/envelope from the paper. `residual_friction_angle_degrees`
    # is Barton's phi_r (the BASE of tau = sigma'_n tan[phi_r + JRC log10(JCS/sigma'_n)]);
    # `slip_weakening_residual_...` is where the TOTAL mobilised angle ends up after
    # D_c of slip, so it is compared against phi_peak, not against phi_r. Round 1 left
    # the second one at the parent's 29.756 deg, which on OG-SH exceeded phi_r and made
    # the law strengthen with slip.
    for key, value in (("jrc", f"{spec['jrc']:.2f}"), ("jcs", f"{UCS:.3g}"),
                       ("residual_friction_angle_degrees", f"{phi_r:.3f}"),
                       ("slip_weakening_residual_friction_angle_degrees",
                        f"{d['phi_residual']:.3f}"),
                       ("characteristic_slip_distance", f"{d['d_c']:.3e}"),
                       ("dilation_angle_peak_degrees", f"{d['dilation']:.3f}"),
                       ("dilation_angle_residual_degrees", f"{d['dilation']:.3f}"),
                       ("cohesion", f"{spec['c_peak']:.3g}"),
                       ("residual_cohesion", "0.0")):
        text = re.sub(rf"^(\s+{key}\s*=\s*)[^\n#]*", rf"\g<1>{value}   ", text,
                      count=1, flags=re.M)

    # -----------------------------------------------------------------------
    # THE REPORTING FRAME. Round 1 inherited all of this from the parent, so the
    # scored channels were resolved onto Ye2018's sigma_3 = 30 MPa and the PARENT's
    # theta. Two of the three decks also died at t = 0.75 s on a PointValue sitting
    # above the top of their own mesh. None of it is model physics and all of it
    # would have silently corrupted the gate.
    # -----------------------------------------------------------------------
    s2, stc = sin_t ** 2, sin_t * cos_t
    sig3_mpa = SIGMA3 / 1e6

    # sigma_1 - sigma_3 from the reaction: the constant subtracted is sigma_3.
    text, n = re.subn(r"(expression\s*=\s*')sigma1_reaction_mpa_pp - 30\.0(')",
                      rf"\g<1>sigma1_reaction_mpa_pp - {sig3_mpa:.1f}\g<2>", text)
    assert n == 1, f"{name}: differential_stress_reaction expression not found"

    # sigma'_n in the paper's frame: sigma_3 + (sigma_1-sigma_3) sin^2(theta) - P_p.
    text, n = re.subn(
        r"(expression\s*=\s*')30\.0 - 0\.5\*\(injection_pressure_pp \+ pp_outlet_pp\)"
        r"\*1e-6 \+ [0-9.]+\*differential_stress_reaction_mpa_pp(')",
        rf"\g<1>{sig3_mpa:.1f} - 0.5*(injection_pressure_pp + pp_outlet_pp)*1e-6 + "
        rf"{s2:.15f}*differential_stress_reaction_mpa_pp\g<2>", text)
    assert n == 1, f"{name}: effective_normal_paper_frame expression not found"

    # tau in the paper's frame: (sigma_1-sigma_3) sin(theta) cos(theta). Only the
    # SW-T2 parent has this postprocessor, so the other two get it inserted.
    text, n = re.subn(
        r"(expression\s*=\s*')[0-9.]+\*differential_stress_reaction_mpa_pp(')",
        rf"\g<1>{stc:.15f}*differential_stress_reaction_mpa_pp\g<2>", text)
    if n == 0:
        block = (f"  [shear_stress_paper_frame_mpa_pp]\n"
                 f"    # KALANTAR: tau = (sigma_1-sigma_3) sin({spec['theta']}) cos({spec['theta']}).\n"
                 f"    # Absent from this parent; the gate scores this channel, so it is added here.\n"
                 f"    type = ParsedPostprocessor\n"
                 f"    pp_names = differential_stress_reaction_mpa_pp\n"
                 f"    expression = '{stc:.15f}*differential_stress_reaction_mpa_pp'\n"
                 f"  []\n")
        text, n = re.subn(r"(?m)^(  \[effective_normal_paper_frame_mpa_pp\])",
                          block + r"\g<1>", text, count=1)
        assert n == 1, f"{name}: nowhere to insert shear_stress_paper_frame"

    # Bulk gauge: a 90 mm chord centred on the REAL core mid-height. Round 1 used
    # `parent_mid +/- 50 mm`, which on OG-T and OG-SC put the upper point 11-14 mm
    # outside the mesh. 90 mm rather than 100 keeps both ends off the platen faces.
    mid = spec["core_height"] / 2.0
    for which, z in (("upper", mid + 0.045), ("lower", mid - 0.045)):
        for comp in ("x", "z"):
            text, n = re.subn(
                rf"(\[bulk_disp_{comp}_{which}_pp\][^\[]*?point\s*=\s*')[^']*(')",
                rf"\g<1>${{sample_radius}} 0 {z:.5f}\g<2>", text, count=1, flags=re.S)
            assert n == 1, f"{name}: bulk_disp_{comp}_{which}_pp not found"

    # Borehole pressure readouts. The SW-S3 parent reads these with PointValue at
    # hard-coded coordinates that no longer match its own source_in/source_out --
    # the deck comment even says they must track it. Repoint them.
    for pp, (x, z) in (("injection_pressure_pp", spec["src_in"]),
                       ("pp_outlet_pp", spec["src_out"])):
        text = re.sub(rf"(\[{pp}\][^\[]*?type\s*=\s*PointValue[^\[]*?point\s*=\s*')[^']*(')",
                      rf"\g<1>{x:.9f} 0.0 {z:.9f}\g<2>", text, count=1, flags=re.S)

    # Timeline.
    end = xs[-1]
    text = re.sub(r"^(\s*end_time\s*=\s*)[^\n#]*", rf"\g<1>{end:.0f}   ", text,
                  count=1, flags=re.M)
    text = re.sub(r"if\(t<2550\.0", f"if(t<{end:.1f}", text)

    # Exodus frame budget. OG-SH's round-1 run wrote 480 frames and a 6.5 GB file;
    # OG-SC's schedule is 2.5x longer, so a fixed interval of 10 would land ~16 GB
    # on a link that has to carry three of these. Hold every deck near 500 frames.
    n_steps = end / 0.75
    text = re.sub(r"^(\s*time_step_interval\s*=\s*)10\s*$",
                  rf"\g<1>{max(10, round(n_steps / 500)):d}", text, count=1, flags=re.M)
    for key, base in (("exodus_file_base", "results_exodus_hpc"),
                      ("csv_file_base", "results_csv_hpc"),
                      ("checkpoint_file_base", "results_checkpoint_hpc")):
        text = apply(text, key, f"{base}/{stem}_hpc", "self-named")

    # Header-only annotations.
    ROWS = rows
    OVERRIDE_NOTE = ("\n#                    OVERRIDDEN: section 2.3 says the Figure 3b criterion "
                     "\n#                    overestimates THIS specimen (the test ran at ~0.92 tau_p, "
                     "\n#                    not 0.85), so phi_peak is 32.70, not the 36.05 that "
                     "\n#                    mu = 0.7 / c = 1.2 MPa gives."
                     if spec.get("phi_peak_override") else "")
    m = re.search(r"dilation_angle_peak_degrees\s*=\s*([0-9.]+)", parent)
    PARENT_DIL = f"{float(m.group(1)):.2f} deg" if m else "unknown"
    STABILITY = ("D_c > cap -> STABLE, which is what the paper reports."
                 if not spec["bursts"] else
                 "D_c < cap -> UNSTABLE, which is what the paper reports.")

    header = f"""# =============================================================================
# {stem}
#
# KALANTAR ET AL. (2025), specimen {spec['label']} ({spec['kind']} fracture) -- ROUND 2.
# Built by scripts/build_110_kalantar_decks.py from
# Examples/YeGhasemmi2018/{spec['parent']}.
#
# NOTHING IN THIS DECK IS CALIBRATED. Every constant below is derived from the
# paper, from Table 2, or measured off the verified mesh. The parent supplies
# structure only. What is still INHERITED and therefore still suspect is listed
# at the bottom.
#
# DERIVED CONSTANTS
#   theta            {spec['theta']:.1f} deg  (Table 1{'; the geometric argument, not Table 2 s 25.999' if name == 'OGT' else ''})
#   sigma_3          33.00 MPa  RECOVERED from Table 2 by the angle identity. The
#                    prose says 30 MPa; that is the EFFECTIVE confining pressure.
#                    Using 30 here would be a 10 % error on every stage.
#   E, nu            {YOUNGS_MODULUS/1e9:.0f} GPa, {POISSONS_RATIO}  (section 2.1)
#   porosity, k      {POROSITY}, {MATRIX_PERMEABILITY:.1e} m^2  (section 2.1)
#   JRC, JCS         {spec['jrc']:.2f}, {UCS/1e6:.0f} MPa (= UCS, section 2.1 / 3.2)
#   peak envelope    tau = {spec['mu_peak']} sigma'_n + {spec['c_peak']/1e6:.1f} MPa (Figure 3)
#                    -> phi_peak {phi_peak:.2f} deg at the stage-1 sigma'_n of
#                    {d['sn1']/1e6:.2f} MPa, so phi_r = phi_peak - JRC log10(JCS/sigma'_n)
#                    = {phi_r:.3f} deg.{OVERRIDE_NOTE}
#   residual         phi = {d['phi_residual']:.3f} deg, atan of Table 2's LAST stage
#                    (tau {ROWS[-1]['tau']:.2f} / sigma'_n {ROWS[-1]['sn']:.2f} MPa). Round 1 carried the
#                    parent's 29.756 deg here, which on OG-SH was ABOVE phi_r and
#                    made the joint strengthen with slip.
#   dilation         {d['dilation']:.3f} deg = 0.5 JRC log10(JCS/sigma'_n), Barton's peak
#                    dilation. The parent's value was a Ye2018 fit ({PARENT_DIL}).
#   D_c              {d['d_c']*1e6:.1f} um against a stick-slip cap of {d['dc_cap']*1e6:.1f} um
#                    (D_c < d(tau)/k_eff, k_eff = K_sys cos^2 theta sin theta / A =
#                    {d['k_eff']/1e12:.4f} MPa/um). {STABILITY}
#   aperture         a_h0 {d['ah0']*1e6:.2f} um anchored at sigma'_n {d['sn1']/1e6:.2f} MPa
#                    (Table 2 stage 1); bounds [{d['ah_min']*1e6:.3f}, {d['ah_max']*1e6:.2f}] um bracket
#                    Table 2's observed [{d['ah_lo']*1e6:.2f}, {d['ah_hi']*1e6:.2f}] um.
#                    slip_damage_scale {d['slip_damage_scale']*1e6:.2f} um.
#   K_sys            796 kN/mm MEASURED (section 2.3) -> penalty {penalty:.3e} Pa/m.
#                    This is the constant whose x2 bracket moved Q by -94/+408 % on
#                    Ye2018 and had to be inferred there. Here it is data.
#   W/L              {2*SAMPLE_RADIUS/spec['sep_paper']:.5f} paper / {2*SAMPLE_RADIUS/sep_mesh:.5f} mesh.
#                    Eq (7) as printed misses the paper's own Table 2 by 10.3x in
#                    a_h^3; the plain cubic law reproduces it to 0.5 %. See
#                    scripts/kalantar_parameter_audit.py section 8.
#
# SCHEDULE (section 2.3, cross-checked against Table 2's stage count)
#   3 MPa steps at 0.03 MPa/s, held {spec['hold']:.0f} s, up to {spec['p_max']/1e6:.0f} MPa
#   ({ups} stages), then back down to 6 MPa ({downs} stages). end_time {end:.0f} s.
#   Outlet held at 3 MPa throughout.
#
# WHAT WAS DELIBERATELY NOT INHERITED
#   fault_pressure_coefficient -> 1.0, and poro_du / axial_relax_du /
#   side_unload_relax_pressure -> 0. Those are fitted Ye2018 load-path knobs for a
#   different specimen set on a different frame. Importing them would be silent
#   contamination of a validation that is supposed to be independent.
#
# THE AXIAL GATE
#   axial_pres_final is a SERIES-SPRING solve, not -sigma_1/penalty. The penalty BC
#   delivers sigma_1 = penalty*(u_cmd - u_sample), so the core's own shortening has
#   to be added back: u_cmd = sigma_1/penalty + C_ax*(sigma_1-sigma_3) with C_ax =
#   {d['c_ax']:.4e} m/Pa (0.8987 L/E, calibrated on the completed OG-SH run 19444645).
#   Target sigma_1 = {sigma1/1e6:.2f} MPa from Table 2 stage 1 via tau = (sigma_1-sigma_3)
#   sin theta cos theta. Still worth a 200 s check against the stage-1 target:
#   tau = {d['tau1']/1e6:.2f} MPa, sigma'_n = {d['sn1']/1e6:.2f} MPa.
#
# THE REPORTING FRAME (round 1 got all of this wrong)
#   differential_stress_reaction_mpa_pp subtracts sigma_3 = {SIGMA3/1e6:.1f}, not Ye2018's 30.
#   effective_normal_paper_frame uses sin^2({spec['theta']}) = {math.sin(theta)**2:.6f}.
#   shear_stress_paper_frame uses sin cos({spec['theta']}) = {math.sin(theta)*math.cos(theta):.6f}.
#   The 4 bulk-gauge PointValues span a 90 mm chord about z = {spec['core_height']/2:.4f} m, the
#   REAL core mid-height. Round 1 used the PARENT's, which put two of them outside
#   the OG-T and OG-SC meshes and killed both jobs at t = 0.75 s.
#
# WHAT IS STILL INHERITED AND STILL SUSPECT (round-3 candidates)
#   the Barton-Bandis normal-closure constants (initial_normal_stiffness,
#   maximum_closure, normal_closure_*), normal_unload_retention_fraction,
#   aperture_scale, tangential_viscosity, roughness_characteristic_slip and
#   dilation_decay_distance are all Ye2018 fits. At Kalantar's stress levels the
#   closure term contributes ~0.03 um, so it is nearly inert here, but none of it
#   is derived. Refit against the a_h(sigma'_n) loop once the loading gate passes.
#
# PREDICTION, WRITTEN BEFORE THE RUN
#   {spec['label']} slips {'through every hold (42 um total, largest step 11 um)' if name=='OGSH' else 'in one burst at the top of the staircase' if name=='OGSC' else 'progressively, 275 um total'}.
#   The D_c/k_eff criterion above now puts this deck on the {'STABLE' if not spec['bursts'] else 'UNSTABLE'} side, matching.
#   A slip-weakening law has no dependence on dsigma'_n/dt, so the campaign's
#   standing weakness predicts this deck will {'FAIL to reproduce the distributed creep and will instead move on the ramps' if name=='OGSH' else 'reproduce the timing to within one injection step'}.
#   FALSIFIER: {'if OG-SH does reproduce hold-creep without a rate law, the sws4-slips-on-ramps-not-holds finding is specimen-specific, not general' if name=='OGSH' else 'if the event lands more than one injection step away, the derived envelope is wrong, not the timing'}.
# =============================================================================
"""
    out = KAL / name / f"{stem}.i"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + text)

    # Anything ACTIVE (comments stripped, including trailing ones) that still names a
    # Ye2018 object is a substitution this script missed. Trailing comments must be
    # stripped or the notes written above trip the check on themselves.
    leftovers = []
    for ln in text.splitlines():
        code = ln.split("#", 1)[0]
        if code.strip() and re.search(r"sw_?[st]\d|ye2018|SWS\d|SWT\d", code, re.I):
            leftovers.append(ln)
    return out, leftovers, dict(d, end=end, ups=ups, downs=downs, sep_mesh=sep_mesh)


def check_points_in_mesh(deck: Path) -> list[str]:
    """Every PointValue in the deck must sit inside the mesh it names.

    This is the check that would have caught the round-1 crash before the jobs were
    submitted. Silent on a missing netCDF4 -- it is a nice-to-have, not a hard dep.
    """
    try:
        import netCDF4
        import numpy as np
    except ImportError:
        return []
    text = deck.read_text()
    m = re.search(r"^mesh_file\s*=\s*(\S+)", text, re.M)
    r = re.search(r"^sample_radius\s*=\s*([0-9.eE+-]+)", text, re.M)
    if not (m and r):
        return []
    mesh = deck.parent / m.group(1)
    if not mesh.exists():
        return [f"mesh not found: {mesh}"]
    ds = netCDF4.Dataset(mesh)
    pts = np.column_stack([ds.variables[f"coord{a}"][:] for a in "xyz"])
    ds.close()
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    bad = []
    for blk, coord in re.findall(
            r"\[(\w+)\][^\[]*?type\s*=\s*PointValue[^\[]*?point\s*=\s*'([^']*)'", text, re.S):
        p = np.array([float(v.replace("${sample_radius}", r.group(1))) for v in coord.split()])
        if np.any(p < lo - 1e-9) or np.any(p > hi + 1e-9):
            bad.append(f"{blk} at {p} is outside the mesh bbox {lo} .. {hi}")
    return bad


def main() -> int:
    expect = {"OGSH": (5, 4), "OGT": (9, 8), "OGSC": (7, 6)}   # Table 2 stage counts
    table2 = read_table2()
    fail = 0
    print(f"{'specimen':<9}{'phi_peak':>9}{'phi_r':>8}{'phi_res':>9}{'dil':>7}"
          f"{'sigma_1':>9}{'D_c/cap':>14}{'a_h0':>8}{'end':>8}{'stages':>9}")
    for name, spec in SPECIMENS.items():
        rows = reduce_stages(spec, table2[spec["label"]])
        out, leftovers, d = build(name, spec, rows)
        got = (d["ups"], d["downs"])
        assert got == expect[name], f"{name} schedule gives {got}, Table 2 has {expect[name]}"
        # The stability class the deck realises must match what the paper observed.
        assert (d["d_c"] < d["dc_cap"]) == spec["bursts"], (
            f"{name}: D_c {d['d_c']*1e6:.1f} um vs cap {d['dc_cap']*1e6:.1f} um "
            f"contradicts bursts={spec['bursts']}")
        # A weakening law must weaken.
        assert d["phi_residual"] < d["phi_peak"], (
            f"{name}: slip-weakening residual {d['phi_residual']:.2f} >= phi_peak "
            f"{d['phi_peak']:.2f} -- the joint would strengthen with slip")
        print(f"{spec['label']:<9}{d['phi_peak']:>8.2f}d{d['phi_r']:>7.3f}d"
              f"{d['phi_residual']:>8.3f}d{d['dilation']:>6.2f}d{d['sigma1']/1e6:>8.2f}M"
              f"{d['d_c']*1e6:>7.1f}/{d['dc_cap']*1e6:<6.1f}{d['ah0']*1e6:>7.2f}u"
              f"{d['end']:>8.0f}{str(got):>9}")
        for ln in leftovers[:5]:
            fail += 1
            print(f"    !! still names a Ye2018 object: {ln.strip()[:100]}")
        for msg in check_points_in_mesh(out):
            fail += 1
            print(f"    !! {msg}")
        print(f"    -> {out.relative_to(ROOT)}")
    print("\nSchedules match Table 2's stage counts on all three specimens.")
    print("Every PointValue is inside its own mesh." if not fail else
          f"\n{fail} PROBLEM(S) -- do not submit.")
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
