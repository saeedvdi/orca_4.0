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

WHAT STILL HAS TO BE GATED
==========================
axial_pres_final is a first estimate from sigma_1 / penalty under a series-spring
assumption. Ye2018 needed a short preload run per specimen to pin it. Expect the
same here: run 200 s, read the realised (tau, sigma'_n) at the fracture, and correct.
The target is printed by this script and written into each deck header.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KAL = ROOT / "Examples/Kalantar2025"

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

SPECIMENS = {
    "OGSH": dict(
        tag="og_sh", label="OG-SH", kind="shear", theta=29.0, jrc=15.60,
        mu_peak=0.7, c_peak=1.2e6, p_max=18.0e6, hold=300.0,
        mesh="mesh/kalantar2025_og_sh_theta29_size3.e",
        src_in=(-0.019992000, 0.023933478), src_out=(0.019992000, 0.096066522),
        sep_paper=0.0824654, tau1=26.14e6, sn1=42.99e6, parent="SWT2/93_03_swt2_final_theta30_resc9p71_ppfix.i",
    ),
    "OGT": dict(
        tag="og_t", label="OG-T", kind="tensile", theta=28.0, jrc=12.10,
        mu_peak=1.1, c_peak=0.0, p_max=30.0e6, hold=300.0,
        mesh="mesh/kalantar2025_og_t_theta28_size3.e",
        src_in=(-0.020362222, 0.011704230), src_out=(0.020362222, 0.088295770),
        sep_paper=0.0851596, tau1=66.50e6, sn1=63.86e6, parent="SWT1/93_01_swt1_final_c26p9_resc9p19_ppfix.i",
    ),
    "OGSC": dict(
        tag="og_sc", label="OG-SC", kind="saw-cut", theta=30.0, jrc=4.23,
        mu_peak=0.4, c_peak=0.0, p_max=24.0e6, hold=600.0,
        mesh="mesh/kalantar2025_og_sc_theta30_size3.e",
        src_in=(-0.020184231, 0.015039887), src_out=(0.020184231, 0.084960113),
        sep_paper=0.0799600, tau1=13.16e6, sn1=36.10e6, parent="SWS3/93_05_sw3_final_resc1p40_ppfix.i",
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


def envelope(spec: dict) -> tuple[float, float]:
    """Split the paper's fitted peak criterion into Barton-Bandis terms at the
    stage-1 effective normal stress:

        phi_peak = atan( (mu sigma'_n + c) / sigma'_n )
        phi_r    = phi_peak - JRC log10(JCS / sigma'_n)

    so the deck reproduces Figure 3's envelope at the stress the experiment
    actually starts from, rather than at an arbitrary reference.
    """
    sn = spec["sn1"]
    phi_peak = math.degrees(math.atan((spec["mu_peak"] * sn + spec["c_peak"]) / sn))
    return phi_peak - spec["jrc"] * math.log10(UCS / sn), phi_peak


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


def build(name: str, spec: dict) -> Path:
    parent = (ROOT / "Examples/YeGhasemmi2018" / spec["parent"]).read_text()
    theta = math.radians(spec["theta"])
    phi_r, phi_peak = envelope(spec)
    xs, ys, ups, downs = schedule(spec["p_max"], spec["hold"])
    sigma1 = SIGMA3 + spec["tau1"] / (math.sin(theta) * math.cos(theta))
    penalty = K_SYS / SAMPLE_AREA
    sep_mesh = math.dist(spec["src_in"], spec["src_out"])
    deck = DECK_NUMBER[name]
    stem = f"{deck}_{spec['tag']}_bbfast_r1"

    subs = [
        ("mesh_file", spec["mesh"], f"{spec['label']} factor-3 mesh, verified 5b9fcc5"),
        ("sample_radius", f"{SAMPLE_RADIUS:.5f}", "Table 1, D = 49.98 mm"),
        ("sample_area", f"{SAMPLE_AREA:.9e}", "pi r^2"),
        ("bulk_sin_theta", f"{math.sin(theta):.16f}", f"sin({spec['theta']} deg)"),
        ("bulk_cos_theta", f"{math.cos(theta):.16f}", f"cos({spec['theta']} deg)"),
        ("axial_bc_penalty", f"{penalty:.4e}",
         "MEASURED K_sys 796 kN/mm / A -- Ye2018 had to infer this"),
        ("axial_pres_initial", f"{-SIGMA3 / penalty:.6e}", "-sigma_3/penalty, t=0 equilibrium"),
        ("axial_pres_final", f"{-sigma1 / penalty:.6e}",
         f"FIRST ESTIMATE -sigma_1/penalty, sigma_1 = {sigma1/1e6:.2f} MPa. MUST BE GATED"),
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

    # Joint law: JRC/JCS/envelope from the paper.
    for key, value in (("jrc", f"{spec['jrc']:.2f}"), ("jcs", f"{UCS:.3g}"),
                       ("residual_friction_angle_degrees", f"{phi_r:.3f}"),
                       ("cohesion", f"{spec['c_peak']:.3g}"),
                       ("residual_cohesion", "0.0")):
        text = re.sub(rf"^(\s+{key}\s*=\s*)[^\n#]*", rf"\g<1>{value}   ", text,
                      count=1, flags=re.M)

    # Timeline.
    end = xs[-1]
    text = re.sub(r"^(\s*end_time\s*=\s*)[^\n#]*", rf"\g<1>{end:.0f}   ", text,
                  count=1, flags=re.M)
    text = re.sub(r"if\(t<2550\.0", f"if(t<{end:.1f}", text)
    for key, base in (("exodus_file_base", "results_exodus_hpc"),
                      ("csv_file_base", "results_csv_hpc"),
                      ("checkpoint_file_base", "results_checkpoint_hpc")):
        text = apply(text, key, f"{base}/{stem}_hpc", "self-named")

    header = f"""# =============================================================================
# {stem}
#
# KALANTAR ET AL. (2025), specimen {spec['label']} ({spec['kind']} fracture) -- ROUND 1.
# Built by scripts/build_110_kalantar_decks.py from
# Examples/YeGhasemmi2018/{spec['parent']}.
#
# NOTHING IN THIS DECK IS CALIBRATED. Every constant below is derived from the
# paper or measured off the verified mesh. The parent supplies structure only.
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
#                    {spec['sn1']/1e6:.2f} MPa, so phi_r = phi_peak - JRC log10(JCS/sigma'_n)
#                    = {phi_r:.3f} deg.
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
# WHAT MUST BE GATED BEFORE THIS IS BELIEVED
#   axial_pres_final is a first estimate, -sigma_1/penalty with sigma_1 =
#   {sigma1/1e6:.2f} MPa solved from Table 2 stage 1 via tau = (sigma_1-sigma_3) sin
#   theta cos theta. Run ~200 s and check the realised fracture stresses against
#   the stage-1 target: tau = {spec['tau1']/1e6:.2f} MPa, sigma'_n = {spec['sn1']/1e6:.2f} MPa.
#
# PREDICTION, WRITTEN BEFORE THE RUN
#   {spec['label']} slips {'through every hold (42 um total, largest step 11 um)' if name=='OGSH' else 'in one burst at the top of the staircase' if name=='OGSC' else 'progressively, 275 um total'}.
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
    return out, leftovers, dict(phi_r=phi_r, phi_peak=phi_peak, sigma1=sigma1,
                                penalty=penalty, end=end, ups=ups, downs=downs,
                                sep_mesh=sep_mesh)


def main() -> int:
    expect = {"OGSH": (5, 4), "OGT": (9, 8), "OGSC": (7, 6)}   # Table 2 stage counts
    print(f"{'specimen':<9}{'phi_peak':>9}{'phi_r':>8}{'sigma_1':>9}{'penalty':>12}"
          f"{'end_time':>10}{'stages':>9}{'W/L mesh':>10}")
    for name, spec in SPECIMENS.items():
        out, leftovers, d = build(name, spec)
        got = (d["ups"], d["downs"])
        assert got == expect[name], f"{name} schedule gives {got}, Table 2 has {expect[name]}"
        print(f"{spec['label']:<9}{d['phi_peak']:>8.2f}d{d['phi_r']:>7.3f}d"
              f"{d['sigma1']/1e6:>8.2f}M{d['penalty']:>12.3e}{d['end']:>10.0f}"
              f"{str(got):>9}{2*SAMPLE_RADIUS/d['sep_mesh']:>10.5f}")
        if leftovers:
            print(f"    !! {len(leftovers)} active line(s) still name a Ye2018 object:")
            for ln in leftovers[:5]:
                print(f"       {ln.strip()[:100]}")
        print(f"    -> {out.relative_to(ROOT)}")
    print("\nSchedules match Table 2's stage counts on all three specimens.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
