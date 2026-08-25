#!/usr/bin/env python3
"""Generate the 105-series recovery decks (2026-08-25).

Three independent question sets, ten decks, all derived mechanically from a
93/94-series parent so that every difference is auditable as a diff:

  A. SW-T1 maximum-closure continuation (3 decks, BBFast).
     45.91 -> 50 -> 55 um already improves EVERY scored channel monotonically
     (mean 4.44 -> 3.68 -> 2.69).  The bracket is not yet turned around, so the
     published SW-T1 final is not the best the model reaches.  Continue to
     70/90/110 um until it does turn.

  B. SW-S4 weakening-path bracket (3 decks, BBFast).
     93_07's tau residual is not noise and not the frame: it is +2.74 MPa at
     stage 3 with d_s at -80 %, i.e. weakening starts too late, and it stays
     +0.3..+1.3 MPa through stages 5-9, i.e. the residual floor is too high.
     The 99-series exponent/viscosity probes moved tau by <= 0.6 points and
     cost more in d_n/d_s than they returned, because the exponent is the wrong
     knob.  Bracket the two knobs that set onset and floor instead.

  C. Calibrated Mohr-Coulomb upper bound (4 decks, MC).
     The orca_3.0_full archive holds 52 independently CALIBRATED MC runs.  On
     today's metric, with the corrected kinematic d_n channel, the best reach
     4.40 % on SW-S4 and 6.07 % on SW-S3, against transferred baselines of
     7.07 % and 18.23 %.  Those numbers cannot be quoted as they stand -- they
     were produced on superseded meshes, in the pre-ppfix frame, and (SW-S3)
     with biot = 1e-12.  Port the calibrated envelopes onto the corrected
     meshes and the ppfix frame so the comparison is an upper bound on
     Mohr-Coulomb rather than an artefact of a stale configuration.

Run from the repository root:  python scripts/make_105_series.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "Examples/YeGhasemmi2018"

# Barton-Bandis power-law closure, sigma_n = (K_ni V_m) [c/(V_m - c)]^(1/p),
# inverted at the 31 MPa isotropic preload.  Reproduces the offsets already in
# 93_01 (4.433e-5), 99_01 (4.774933e-5) and 100_01 (5.167067e-5) exactly.
KNI_SWT1, P_SWT1, SIGMA_PRELOAD = 2.443e11, 3.28, 31.0e6


def closure_offset(v_m: float, k_ni: float = KNI_SWT1, p: float = P_SWT1,
                   sigma: float = SIGMA_PRELOAD) -> float:
    x = (sigma / (k_ni * v_m)) ** p
    return v_m * x / (1.0 + x)


def read(path: Path) -> str:
    return path.read_text()


def sub_once(text: str, old: str, new: str, what: str) -> str:
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"{what}: expected exactly 1 occurrence of {old!r}, found {n}")
    return text.replace(old, new)


def replace_line(text: str, key: str, new_line: str, what: str) -> str:
    """Replace the single TOP-LEVEL line beginning with ``key``, comment and all.

    Anchored at column 0 on purpose: several of these names appear a second time,
    indented, inside a block as ``key = ${key}``, and that reference must survive.
    """
    import re as _re
    pat = _re.compile(r"^" + _re.escape(key) + r"[^\n]*$", _re.M)
    found = pat.findall(text)
    if len(found) != 1:
        raise SystemExit(f"{what}: expected exactly 1 top-level line starting "
                         f"{key!r}, found {len(found)}")
    return pat.sub(lambda m: new_line, text, count=1)


def retarget_outputs(text: str, parent_stem: str, stem: str) -> str:
    for kind in ("exodus", "csv", "checkpoint"):
        text = sub_once(
            text,
            f"results_{kind}_hpc_rorqual/{parent_stem}_hpc",
            f"results_{kind}_hpc_rorqual/{stem}_hpc",
            f"{stem}: {kind} output base",
        )
    return text


def banner(lines: list[str]) -> str:
    rule = "# " + "=" * 77
    return "\n".join([rule] + ["# " + ln if ln else "#" for ln in lines] + [rule, ""])


def write_deck(spec: str, stem: str, text: str) -> Path:
    path = EX / spec / f"{stem}.i"
    path.write_text(text)
    return path


def write_submit(spec: str, stem: str, parent_stem: str,
                 ntasks: int | None = None, hours: str | None = None) -> Path:
    src = EX / spec / f"{parent_stem}_hpc_nochk.sh"
    dst = EX / spec / f"{stem}_hpc_nochk.sh"
    text = read(src).replace(parent_stem, stem)
    if ntasks is not None:
        text = re.sub(r"^#SBATCH --ntasks=\d+$", f"#SBATCH --ntasks={ntasks}",
                      text, flags=re.M)
        text = re.sub(r"srun --mpi=pmi2 -n \d+", f"srun --mpi=pmi2 -n {ntasks}", text)
    if hours is not None:
        text = re.sub(r"^#SBATCH --time=[\d:]+$", f"#SBATCH --time={hours}",
                      text, flags=re.M)
    dst.write_text(text)
    dst.chmod(0o755)
    return dst


BUILT: list[tuple[str, str, str, str]] = []   # spec, stem, parent, one-line purpose


# ---------------------------------------------------------------------------
# A. SW-T1 maximum-closure continuation
# ---------------------------------------------------------------------------
SWT1_PARENT = "93_01_swt1_final_c26p9_resc9p19_ppfix"

for stem, v_m in [
    ("105_01_swt1_vm70um_ppfix", 7.000e-5),
    ("105_02_swt1_vm90um_ppfix", 9.000e-5),
    ("105_03_swt1_vm110um_ppfix", 1.1000e-4),
]:
    tag = stem.split("_")[0] + "_" + stem.split("_")[1]
    offset = closure_offset(v_m)
    sigma0 = KNI_SWT1 * v_m
    text = read(EX / "SWT1" / f"{SWT1_PARENT}.i")
    head = banner([
        f"{tag} CONTROLLED CALIBRATION PROBE -- SW-T1",
        f"Parent: {SWT1_PARENT}.i",
        "",
        f"One material axis only: mechanical BB maximum closure 45.91 -> "
        f"{v_m * 1e6:.2f} um.",
        f"The closure offset is recomputed at sigma_n = 31 MPa "
        f"(44.3306 -> {offset * 1e6:.4f} um) so the initial joint seating is",
        "preserved.  K_ni is held at 2.443e11 Pa/m, exactly as 99_01 and 100_01",
        "held it, so this arm is a continuation of that bracket and not a new one.",
        "",
        "WHY THIS BRACKET IS BEING CONTINUED.  The arm has not turned around.",
        "Scored on the corrected kinematic d_n channel, EVERY channel improves",
        "monotonically with V_m and the mean has not yet found a minimum:",
        "",
        "  V_m [um]   mean      Q     sigma'_n   tau     d_n     d_s",
        "  45.91      4.44    7.38     1.98     2.73    9.06    1.02   (93_01)",
        "  50.00      3.68    6.15     1.69     2.32    7.28    0.96   (99_01)",
        "  55.00      2.69    4.51     1.44     1.98    4.58    0.93   (100_01)",
        "",
        "A monotone bracket with no interior minimum is not a result, it is an",
        "unfinished search, and it means the published SW-T1 final is not the",
        "best this model reaches.  These three arms run until the trend turns.",
        "",
        f"NOTE ON SOFTNESS.  sigma_0 = K_ni V_m = {sigma0 / 1e6:.2f} MPa here, against the",
        "31 MPa preload, so the seated closure ratio c/V_m falls to "
        f"{offset / v_m:.4f}",
        "(0.9656 in the parent).  The joint is deliberately much more compliant",
        "than the back-analysed value; at 110 um sigma_0 approaches the preload and",
        "the arm is EXPECTED to overshoot.  That is what closes the bracket.",
        "",
        "Everything else -- mesh, BCs, injection schedule, hydraulics, solver, and",
        "the 2026-08-24 flux-measurement fix carried by this parent -- is unchanged.",
    ])
    text = head + text
    text = sub_once(text, "    maximum_closure = 4.591e-5",
                    f"    maximum_closure = {v_m:.3e}".replace("e-0", "e-") +
                    f"       # {tag}: {v_m * 1e6:.2f} um continuation bracket",
                    f"{stem}: maximum_closure")
    text = sub_once(text, "    normal_closure_offset = 4.433e-5",
                    f"    normal_closure_offset = {offset:.12e}".replace("e-0", "e-") +
                    f" # {tag}: closure(31 MPa), preserves initial seating",
                    f"{stem}: normal_closure_offset")
    text = retarget_outputs(text, SWT1_PARENT, stem)
    write_deck("SWT1", stem, text)
    write_submit("SWT1", stem, SWT1_PARENT)
    BUILT.append(("SWT1", stem, SWT1_PARENT,
                  f"BBFast V_m = {v_m * 1e6:.0f} um (closure bracket continuation)"))


# ---------------------------------------------------------------------------
# B. SW-S4 weakening-path bracket
# ---------------------------------------------------------------------------
SWS4_PARENT = "93_07_sw4_final_theta30_jrc5_ppfix"

SWS4_DIAGNOSIS = [
    "WHAT THE SW-S4 tau RESIDUAL ACTUALLY IS.  Stage-by-stage, 93_07 against",
    "Table 2 (model - paper, MPa):",
    "",
    "  stage   3      4      5      6      7      8      9     10     11",
    "  tau  +2.74  +1.06  +1.26  +0.89  +0.65  +0.45  +0.29  +0.05",
    "  d_s   -80 %  +15 %   +7.7%  +6.0%  +4.6%  +3.2%  +3.2%  +3.2%",
    "",
    "Two distinct defects, not one:",
    "  (i)  ONSET IS LATE.  At stage 3 the measured tau has already fallen",
    "       12.14 -> 9.38 MPa while the model is still at 12.12 and has slipped",
    "       3.4 um against a measured 17 um.  Weakening has not started.",
    "  (ii) THE FLOOR IS HIGH.  From stage 5 on the model tracks the shape but",
    "       sits 0.3-1.3 MPa above it, converging only at the last stage.",
    "",
    "This is why the 99-series probes failed.  99_07 (exponent 1.10 -> 1.05) and",
    "99_08 (viscosity 3.5 -> 3.0e12) each bought ~0.5 MPa at stage 4 and nothing",
    "at stage 3, and both LOST mean accuracy (6.14 -> 6.25, 6.35) because they",
    "paid for it in d_n and d_s.  The exponent reshapes a curve that has not",
    "started; it cannot move its start.  The two knobs that do are the",
    "characteristic slip distance (onset) and the residual friction angle (floor).",
    "",
    "The archive is the existence proof.  On this same specimen, a freely",
    "calibrated Mohr-Coulomb envelope -- cohesionless, mu 1.17 -> 0.055 over a",
    "115 um decay -- reached tau = 5.6 % where 93_07 sits at 10.1 %.  It is not",
    "the loading frame and it is not the mesh; it is the weakening path.",
]

for stem, dc, floor, axis in [
    ("105_04_sw4_dc4p5em5_ppfix", "4.50e-5", None,
     "characteristic slip distance 74.5 -> 45.0 um (ONSET)"),
    ("105_05_sw4_swfloor3p15_ppfix", None, "3.15",
     "slip-weakening residual friction angle 6.50 -> 3.15 deg (FLOOR)"),
    ("105_06_sw4_dc4p5em5_swfloor3p15_ppfix", "4.50e-5", "3.15",
     "both knobs together"),
]:
    tag = stem.split("_")[0] + "_" + stem.split("_")[1]
    text = read(EX / "SWS4" / f"{SWS4_PARENT}.i")
    lines = [
        f"{tag} WEAKENING-PATH BRACKET -- SW-S4",
        f"Parent: {SWS4_PARENT}.i",
        "",
        f"Axis: {axis}.",
        "",
    ] + SWS4_DIAGNOSIS + [
        "",
        "3.15 deg is mu = 0.055, the archive's calibrated residual floor, reached",
        "here through the BBFast slip-weakening residual angle rather than by",
        "adopting the archive's envelope.  45.0 um is a 0.60x contraction of the",
        "current 74.5 um, chosen to bring measurable weakening into stage 3",
        "without collapsing the stick phase (the peak envelope is untouched).",
        "",
        "Everything else -- mesh, BCs, injection schedule, dilation, hydraulics,",
        "solver, and this parent's 2026-08-24 flux fix -- is unchanged.",
        "READ d_s AND d_n TOGETHER WITH tau.  Both 99-series probes improved tau",
        "and lost overall accuracy.  A tau gain that costs more than it returns",
        "is not an improvement, and this bracket is not exempt from that.",
    ]
    text = banner(lines) + text
    if dc is not None:
        text = replace_line(
            text, "bb_characteristic_slip_distance =",
            f"bb_characteristic_slip_distance = {dc} # {tag}: 74.5 -> 45.0 um, "
            f"pull weakening onset into stage 3 (was 67_01's in-bracket midpoint).",
            f"{stem}: Dc")
    if floor is not None:
        text = replace_line(
            text, "bb_slip_weakening_residual_friction_angle =",
            f"bb_slip_weakening_residual_friction_angle = {floor} # {tag}: 6.50 -> "
            f"3.15 deg, i.e. mu 0.114 -> 0.055, the archive's calibrated floor.",
            f"{stem}: residual friction angle")
    text = retarget_outputs(text, SWS4_PARENT, stem)
    write_deck("SWS4", stem, text)
    write_submit("SWS4", stem, SWS4_PARENT)
    BUILT.append(("SWS4", stem, SWS4_PARENT, f"BBFast {axis}"))


# ---------------------------------------------------------------------------
# C. Calibrated Mohr-Coulomb upper bound
# ---------------------------------------------------------------------------
def patch_block(text: str, block: str, fn) -> str:
    """Apply ``fn`` to the body of a single top-level MOOSE sub-block."""
    start = text.index(f"  [{block}]\n")
    end = text.index("\n  []\n", start) + len("\n  []\n")
    body = text[start:end]
    return text[:start] + fn(body) + text[end:]


def set_in_block(body: str, key: str, value: str, note: str) -> str:
    pat = re.compile(r"^(\s*)" + re.escape(key) + r"\s*=[^\n]*$", re.M)
    if len(pat.findall(body)) != 1:
        raise SystemExit(f"czm_contact: expected exactly 1 {key!r}, "
                         f"found {len(pat.findall(body))}")
    return pat.sub(lambda m: f"{m.group(1)}{key} = {value}"
                             + (f"   # {note}" if note else ""), body, count=1)


MC_PROVENANCE = [
    "WHERE THESE NUMBERS COME FROM, AND WHAT THEY ARE FOR.",
    "",
    "orca_3.0_full/Examples/YeGhasemmi2018 holds 52 completed Mohr-Coulomb runs",
    "on the two saw cuts -- 32 on SW-S3 (series 70-83), 20 on SW-S4 (61-68) --",
    "that were CALIBRATED to Table 2 directly, one specimen at a time.  Scored on",
    "today's metric with the corrected kinematic d_n channel they reach",
    "",
    "                       best archived MC   94-series transfer   BBFast final",
    "  SW-S4                    4.40 %              7.07 %             6.14 %",
    "  SW-S3                    6.07 %             18.23 %             4.57 %",
    "",
    "i.e. on SW-S4 a freely calibrated Mohr-Coulomb beats our own Barton-Bandis",
    "final.  That number cannot be quoted as it stands, because every archived",
    "run was produced on a superseded mesh, in the pre-ppfix loading frame, and",
    "on SW-S3 with biot = 1e-12.  It also cannot be ignored: it is the obvious",
    "attack on the manuscript's central comparison, and it is a fair one.",
    "",
    "These decks resolve it the only honest way -- by re-running the calibrated",
    "envelope on the CORRECTED mesh, the CORRECTED frame and biot = 0.6, so the",
    "MC column of Table 6 can be accompanied by a stated upper bound rather than",
    "by a claim that Mohr-Coulomb 'fails'.  The paper's argument is parameter",
    "economy and transferability (the 94-series fits nothing per specimen; the",
    "archive fits ~8 parameters per specimen), and that argument is stronger,",
    "not weaker, when the calibrated bound is published beside it.",
]

MC_DEVIATIONS = [
    "DELIBERATE DEVIATIONS FROM THE ARCHIVED DECK, each stated so the result is",
    "not mistaken for a reproduction:",
    "  * mesh, boundary conditions, loading frame, injection schedule, paper-frame",
    "    trig constants and all flow constants are THIS repository's corrected",
    "    ones, inherited unchanged from the 94-series parent.",
    "  * biot_coefficient stays at 0.6.",
    "  * the power-law Barton-Bandis normal closure is KEPT.  83_11 used the flat",
    "    penalty_normal = 2e13 instead; that penalty is ~19x too stiff on the",
    "    unload branch and would suppress the normal recovery the corrected d_n",
    "    channel now measures.  Keeping the better normal law can only help MC,",
    "    so the bound stays an upper bound.",
    "  * roughness_decay_distance is the ARCHIVE's, which means this deck is no",
    "    longer hydraulically matched to its BBFast sibling: roughness_state feeds",
    "    czm_aperture and therefore the scored Q.  That matching was the point of",
    "    the 94-series transfer and is NOT the point here.  This deck is the",
    "    archive's own calibration, Q included.",
    "  * the output-only reversible-opening reconstruction of 83_11",
    "    (reversible_normal_compliance and the retention transform) is NOT ported.",
    "    reversible_normal_opening is consumed by nothing in the traction, and on",
    "    the corrected d_n channel the entire 80->83 'improvement' of the 3.0",
    "    campaign -- nine decks, 4.40 -> 3.23 on the old channel -- collapses to a",
    "    single value, 6.07 %, identical across all nine.  It changed no mechanics.",
]

MC_JOBS = {
    # spec, parent, stem, rsf, envelope edits, extra params, top-level edits
    "105_07_sw4_mc_calib_ppfix": dict(
        spec="SWS4", parent="94_07_sw4_mc_final", rsf=False, source="67_11",
        title="SW-S4 calibrated Mohr-Coulomb (envelope only, rate-and-state OFF)",
    ),
    "105_08_sw4_mc_calib_rsf_ppfix": dict(
        spec="SWS4", parent="94_07_sw4_mc_final", rsf=True, source="67_11",
        title="SW-S4 calibrated Mohr-Coulomb (envelope + rate-and-state, full port)",
    ),
    "105_09_sw3_mc_calib_ppfix": dict(
        spec="SWS3", parent="94_05_sw3_mc_final", rsf=False, source="83_11",
        title="SW-S3 calibrated Mohr-Coulomb (envelope only, rate-and-state OFF)",
    ),
    "105_10_sw3_mc_calib_rsf_ppfix": dict(
        spec="SWS3", parent="94_05_sw3_mc_final", rsf=True, source="83_11",
        title="SW-S3 calibrated Mohr-Coulomb (envelope + rate-and-state, full port)",
    ),
}

# ("scope", key, value, note).  "block" edits the line inside [czm_contact];
# "top" edits the top-level variable the block references as ${key}.  94_07 routes
# five of these through top-level variables and MOOSE errors on an unused
# variable, so the reference must be preserved and the variable itself moved.
ENVELOPE = {
    "67_11": [
        ("top", "bb_roughness_characteristic_slip", "1.15e-4",
         "67_11 D_R; 94_07 used 8.0e-5 (the BBFast roughness distance)"),
        ("block", "friction_coefficient_rough", "1.17",
         "67_11; was 0.9804 (BB tangent transfer)"),
        ("block", "friction_coefficient_smooth", "0.055", "67_11; was 0.1139"),
        ("block", "cohesion_rough", "0.0", "67_11 COHESIONLESS; was 3.225e6"),
        ("block", "cohesion_smooth", "0.0", "67_11 COHESIONLESS"),
        ("block", "cohesion_roughness_exponent", "2.0", "67_11; was 1.0"),
        ("top", "dilation_angle_peak_degrees", "50.0", "67_11; 94_07 used 24.0"),
        ("top", "dilation_angle_residual_degrees", "22.0", "67_11; 94_07 used 13.0"),
        ("top", "tangential_viscosity", "5.0e12", "67_11; 94_07 used 3.5e12"),
    ],
    "83_11": [
        ("block", "roughness_decay_distance", "3.5e-5", "83_11 D_R; was 4.0e-5"),
        ("block", "friction_coefficient_rough", "1.125", "83_11; was 0.8818"),
        ("block", "friction_coefficient_smooth", "0.096", "83_11; was 0.1486"),
        ("block", "cohesion_rough", "0.0", "83_11 COHESIONLESS; was 2.645e6"),
        ("block", "cohesion_smooth", "0.0", "83_11 COHESIONLESS; was 1.400e6"),
        ("block", "cohesion_roughness_exponent", "2.0", "83_11; was 1.0"),
        ("block", "dilation_angle_peak_degrees", "55.0", "83_11; parent used 26.0"),
        ("block", "dilation_angle_residual_degrees", "38.0", "83_11; parent used 26.0"),
        ("block", "tangential_viscosity", "7.5e11", "83_11; parent used 4.0e11"),
    ],
}

EXTRA = {
    "67_11": """
    # --- dissipation limiter and two-stage tail, ported from 67_11 ----------
    # The 94-series parent left dissipation_margin at its 1e-8 default, i.e.
    # effectively unlimited plastic normal work.  The archive ran it at 0.12.
    dissipation_margin = 0.12
    secondary_weakening_strength = 0.15e6
    secondary_weakening_onset_slip = 28e-6
    secondary_weakening_distance = 12e-6
""",
    "83_11": """
    # --- dissipation limiter and two-stage tail, ported from 83_11 ----------
    # strength = 0 is the archive's bounded tail: never subtract below Coulomb.
    dissipation_margin = 0.02
    secondary_weakening_strength = 0.0
    secondary_weakening_onset_slip = 38e-6
    secondary_weakening_distance = 36e-6
""",
}

RSF = {
    "67_11": """
    # --- rate-and-state, ported from 67_11 ----------------------------------
    # a > b throughout: velocity-STRENGTHENING, so this is a regularizer on the
    # slip burst, not a nucleation model.  The 94-series baseline deliberately
    # runs without it; the pair 105_07/105_08 isolates what it is worth.
    use_rate_and_state = true
    rate_and_state_a = 0.020
    rate_and_state_b = 0.016
    rate_and_state_Dc = 5.0e-5
    rate_and_state_V0 = 5.0e-8
    rate_and_state_theta0 = 1000
    rate_and_state_nonnegative = true
""",
    "83_11": """
    # --- rate-and-state, ported from 83_11 ----------------------------------
    # 83_11 left rate_and_state_nonnegative at its default (false), so it is not
    # set here either.  a > b: velocity-strengthening regularizer.
    use_rate_and_state = true
    rate_and_state_a = 0.020
    rate_and_state_b = 0.008
    rate_and_state_Dc = 5.0e-5
    rate_and_state_V0 = 5.0e-8
    rate_and_state_theta0 = 1000
""",
}

# SW-S3 only: three hydraulic constants the archive fitted differently.
SWS3_HYDRAULIC = [
    ("bb_stress_exponent", "2.0", "83_11 aperture-closure exponent; 94_05 used 4.0"),
    ("slip_damage_onset_slip", "20e-6", "83_11; 94_05 used 30e-6"),
    ("slip_damage_scale", "0.28e-6", "83_11; 94_05 used 0.40e-6"),
]

for stem, job in MC_JOBS.items():
    spec, parent, src, rsf = job["spec"], job["parent"], job["source"], job["rsf"]
    tag = "_".join(stem.split("_")[:2])
    text = read(EX / spec / f"{parent}.i")

    lines = [
        f"{tag} CALIBRATED MOHR-COULOMB UPPER BOUND -- {spec}",
        f"Parent: {parent}.i   Envelope source: orca_3.0_full deck {src}",
        "",
        job["title"] + ".",
        "",
    ] + MC_PROVENANCE + [""] + MC_DEVIATIONS + [
        "",
        ("Rate-and-state is ON here, exactly as the archive ran it.  Compare against"
         if rsf else
         "Rate-and-state is OFF here, so this deck isolates the calibrated ENVELOPE."),
        ("its sibling to separate the envelope from the regularizer."
         if rsf else
         "Its sibling turns RSF on; the pair separates envelope from regularizer."),
        "",
        "The tensile specimens have no counterpart deck and never will from this",
        "archive: SW-T1 MC and SW-T2 MC are recorded 'blocked' in the 3.0",
        "SelectionReview -- two decks were written and neither produced a result.",
        "No calibrated Mohr-Coulomb tensile run has ever existed in this project.",
    ]
    text = banner(lines) + text

    def edit(body: str, _src=src, _rsf=rsf, _tag=tag) -> str:
        for scope, key, value, note in ENVELOPE[_src]:
            if scope == "block":
                body = set_in_block(body, key, value, f"{_tag}: {note}")
        insert = EXTRA[_src] + (RSF[_src] if _rsf else "")
        return body.rstrip()[: body.rstrip().rfind("\n  []")] + "\n" + insert + "  []\n"

    text = patch_block(text, "czm_contact", edit)
    for scope, key, value, note in ENVELOPE[src]:
        if scope == "top":
            text = replace_line(text, f"{key} =", f"{key} = {value}   # {tag}: {note}",
                                f"{stem}: {key}")

    if spec == "SWS3":
        for key, value, note in SWS3_HYDRAULIC:
            text = replace_line(text, f"{key} =", f"{key} = {value}   # {tag}: {note}",
                                f"{stem}: {key}")

    text = retarget_outputs(text, parent, stem)
    write_deck(spec, stem, text)
    write_submit(spec, stem, parent, ntasks=32, hours="24:00:00")
    BUILT.append((spec, stem, parent, job["title"]))


# ---------------------------------------------------------------------------
# Batch submitter
# ---------------------------------------------------------------------------
submit = EX / "submit_recovery_105.sh"
body = ["#!/bin/bash",
        "# " + "=" * 74,
        "# 105-series recovery batch -- 10 decks.",
        "#",
        "# A  105_01..03  SW-T1 maximum-closure continuation (BBFast).",
        "#                The 45.91/50/55 um bracket improves every channel",
        "#                monotonically and has not turned; 70/90/110 closes it.",
        "# B  105_04..06  SW-S4 weakening-path bracket (BBFast).  Onset knob,",
        "#                floor knob, and both.  The 99-series exponent and",
        "#                viscosity probes both LOST accuracy; those were the",
        "#                wrong knobs.",
        "# C  105_07..10  Calibrated Mohr-Coulomb upper bound (MC), SW-S4 and",
        "#                SW-S3, with and without rate-and-state, ported from the",
        "#                orca_3.0_full archive onto the corrected meshes and the",
        "#                ppfix frame.",
        "#",
        "# All ten keep the paper injection schedule and ARE scoreable against",
        "# Table 2 with scripts/table2_gate.py.",
        "# " + "=" * 74,
        "set -u",
        'cd "$(dirname "${BASH_SOURCE[0]}")"',
        "",
        "JOBS=("]
for spec, stem, _parent, purpose in BUILT:
    body.append(f"  {spec}/{stem}_hpc_nochk.sh")
body += [")",
         'echo "105 recovery batch: ${#JOBS[@]} decks"',
         'for s in "${JOBS[@]}"; do',
         '  [ -f "$s" ] || { echo "MISSING: $s" >&2; continue; }',
         '  echo "sbatch $s"; sbatch "$s"',
         "done",
         ""]
submit.write_text("\n".join(body))
submit.chmod(0o755)

print(f"{len(BUILT)} decks written\n")
w = max(len(s) for _, s, _, _ in BUILT)
for spec, stem, parent, purpose in BUILT:
    print(f"  {spec}/{stem:<{w}}  <- {parent}\n      {purpose}")
print(f"\nbatch submitter: {submit.relative_to(ROOT)}")
