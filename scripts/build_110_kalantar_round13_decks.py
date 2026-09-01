#!/usr/bin/env python3
"""Build the Kalantar 2025 Round-13 validation decks.

WHY THIS ROUND EXISTS
=====================
Rounds 7-10 produced nine runs and zero scoreable results: 110_17/110_18/110_26/
110_27/110_28 diverged, and 110_21/110_22/110_25/110_19/110_20/110_24 truncated at
~55 % of their schedule.  Every one of them added rate-and-state or a shear-exponent
change on top of the round-6 decks.  The round-6 decks themselves complete.  So this
round goes back to the round-6 parents and changes ONE constitutive number per arm.

THE ACTUAL DEFECTS, MEASURED PER STAGE (not inferred)
=====================================================
Scoring 110_13 and 110_15 stage by stage against Table 2 shows both specimens are
excellent early and fail late, in opposite directions:

  OG-SH 110_13   stages 1-3 track to <1.2 MPa in tau.  Then slip FREEZES at
                 27.4 um from stage 5 onward while the experiment slips on to
                 42 um.  Because the piston is displacement-controlled, slip that
                 does not happen is shear stress that is not shed: tau runs
                 +2.6 MPa high across the whole unloading branch, and sigma'_n
                 (+1.5) and a_h (+0.25) follow it.  ONE defect, three symptoms.

                 stage  tau_mod  tau_exp   d_s_mod  d_s_exp
                   1     25.861   26.140      2.74      2.0
                   3     24.526   23.380      8.41     18.0
                   5     21.897   19.570     27.43     39.0
                   9     21.569   18.970     27.40     42.0

                 The joint locks because characteristic_slip_distance = 100 um and
                 slip_weakening_exponent = 1.4: at 27 um only 27 % of D_c is spent,
                 so weakening has barely engaged while BB closure and 4.3 deg of
                 dilation harden the joint.  It cannot keep sliding.
                 Closing the gap needs +17 um of slip, which at the measured
                 d(tau)/d(d_s) = 0.150 MPa/um sheds 2.6 MPa -- exactly the deficit.
                 The arithmetic closes, so D_c is the lever.

  OG-SC 110_15   stages 1-5 are essentially exact (tau within 0.05-0.23 MPa,
                 sigma'_n within 0.03, a_h within 0.15 um).  Then the model BURSTS
                 one stage early -- at stage 6 (P_i = 21 MPa) instead of the
                 experiment's stage 7 (P_i = 24) -- and bursts twice as far,
                 45 um against 22 um.  Everything after inherits the offset.

                 stage  P_i  tau_mod  tau_exp   d_s_mod  d_s_exp
                   5     18   12.969   13.020      5.29      1.0
                   6     21    9.111   12.950     35.55      1.0   <- model bursts
                   7     24    8.145    9.730     45.31     20.0   <- experiment bursts
                  13      6    6.350    9.300     45.13     22.0

                 Surviving stage 6 needs tau_limit up by ~0.56 MPa at
                 sigma'_n = 26.26 MPa.  cohesion is currently 0, so a small
                 cohesion is the cleanest level shift: it does not disturb stages
                 1-5, which are nowhere near the limit.

  OG-T           still has no scoreable run.  Round 12 lengthened the preload ramp
                 53 s -> 9998 s and cut the interface overpressure 48.9 -> 21.0 MPa,
                 but failed all five gates.  The reason is in the hold at the end of
                 110_36: with the load constant, p-3 decays with a time constant that
                 converges to 3449 s, not the 1.0e3 s the round-12 rationale assumed.
                 c = kM/mu = 1.4e-20 * 108.3e9 / 1e-3 = 1.516e-6 m^2/s is right, so
                 tau = 3449 s implies a drainage length of sqrt(c*tau) = 72 mm.  The
                 concept was right and the LENGTH was wrong.

                 72 mm is not the port spacing.  It is the radial convergence into a
                 SINGLE NODE: [BCs] has exactly two pore-pressure boundaries,
                 source_in and source_out, each an ExtraNodesetGenerator with
                 use_closest_node = true.  Everything else is no-flow.  The entire
                 specimen must drain through two points on a 0.10 um fracture.

                 The reading notes' own conceptual model (section on the plane
                 channel) has the inlet and outlet as LINE SOURCES SPANNING THE FULL
                 WIDTH W, not points.  This round builds that: a
                 BoundingBoxNodeSetGenerator around each port catches the whole chord
                 -- verified against the mesh, 11 nodes spanning y = -14.910 mm to
                 +14.910 mm at both ports, against a predicted chord half-width of
                 15.221 mm.  This is the paper's stated geometry, not a new fit, and
                 it touches neither the aperture nor the matrix permeability.

                 Ramp goes BACK to the original 53 s.  Round 12 already established
                 what a long ramp buys; if the ports are the bottleneck the short
                 ramp must work, and if it does OG-T becomes cheap again.

WHAT IS DELIBERATELY *NOT* CHANGED
==================================
* No rate-and-state anywhere.  It is what broke rounds 9 and 10.
* residual_friction_angle_degrees is untouched on both specimens: 21.519 (OG-SH)
  and 22.660 (OG-SC) carry measured provenance.
* jrc / jcs untouched -- both are Kalantar's Table 1 / section 2.1 values.
* The line-source ports are applied to OG-T ONLY.  OG-SH and OG-SC already reproduce
  their flow channels (Q 9.3 %, a_h 10 %) with point ports, and changing the port
  geometry would invalidate that calibration.  If round 13 shows line sources matter,
  re-deriving the other two is a separate, deliberate round -- not a side effect.
* No mechanical boundary-condition arm on OG-T.  Five have been falsified; the memory
  note stands.  Ports are a FLOW path, not a mechanical BC.

Generated decks carry this builder's marker and are overwritten only if they do.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KAL = ROOT / "Examples/Kalantar2025"

SH_PARENT = KAL / "OGSH/110_13_og_sh_bbfast_r6.i"
SC_PARENT = KAL / "OGSC/110_15_og_sc_bbfast_r6.i"
OT_PARENT = KAL / "OGT/110_36_og_t_drained_preload_r12.i"

GENERATED = "GENERATED BY scripts/build_110_kalantar_round13_decks.py"
NOTE = "ROUND 13"


@dataclass(frozen=True)
class Arm:
    stem: str
    parent: Path
    case_dir: str
    edits: tuple[tuple[str, str, str], ...] = ()   # (key, value, why)
    rationale: str = ""
    og_t_ports: bool = False
    og_t_drain_ends: bool = False
    og_t_short_ramp: bool = False


ARMS: tuple[Arm, ...] = (
    # ---------------- OG-SH: the shear fracture, the priority ----------------
    Arm("110_38_og_sh_control_r13", SH_PARENT, "OGSH",
        rationale="Byte-for-byte 110_13 except the output names. Protects every "
                  "comparison below against the 0.1 pp cross-machine reproducibility "
                  "floor. If this does not reproduce 110_13's tau 29 % / Q 9.3 %, "
                  "STOP -- nothing else in the round can be read."),
    Arm("110_39_og_sh_dc50_r13", SH_PARENT, "OGSH",
        edits=(("characteristic_slip_distance", "5.0e-05",
                "D_c 100 -> 50 um: slip freezes at 27.4 um, only 27 % of the "
                "current D_c, so weakening never engages"),),
        rationale="Predicts d_s past 30 um and tau at stage 9 below 21.0."),
    Arm("110_40_og_sh_dc30_r13", SH_PARENT, "OGSH",
        edits=(("characteristic_slip_distance", "3.0e-05",
                "D_c 100 -> 30 um: centre of the ladder"),),
        rationale="The expected best arm. Predicts d_s ~ 40 um and tau at stage 9 "
                  "near the experiment's 18.97."),
    Arm("110_41_og_sh_dc15_r13", SH_PARENT, "OGSH",
        edits=(("characteristic_slip_distance", "1.5e-05",
                "D_c 100 -> 15 um: the over-weakened bound"),),
        rationale="Deliberately expected to OVERSHOOT. A ladder with no arm past "
                  "the answer cannot show the answer is bracketed."),
    Arm("110_42_og_sh_dc30_coh0p6_r13", SH_PARENT, "OGSH",
        edits=(("characteristic_slip_distance", "3.0e-05", "as 110_40"),
               ("cohesion", "6.0e+05",
                "1.2 -> 0.6 MPa: D_c sets how FAST tau sheds, cohesion sets the "
                "LEVEL it sheds from; the two are separable only if both are moved")),
        rationale="Separates rate from level. If 110_40 fixes the late stages but "
                  "leaves a uniform tau offset, this is the arm that removes it."),

    # ---------------- OG-SC: the saw cut ----------------
    Arm("110_43_og_sc_coh0p6_r13", SC_PARENT, "OGSC",
        edits=(("cohesion", "6.0e+05",
                "0 -> 0.6 MPa: surviving stage 6 needs tau_limit up ~0.56 MPa at "
                "sigma'_n = 26.26; stages 1-5 are far from the limit and do not move"),),
        rationale="Predicts the burst moves from stage 6 to stage 7, matching the "
                  "experiment. THE gate arm for OG-SC."),
    Arm("110_44_og_sc_coh1p0_r13", SC_PARENT, "OGSC",
        edits=(("cohesion", "1.0e+06",
                "0 -> 1.0 MPa: the upper bracket"),),
        rationale="If 110_43 still bursts early, this says how much is needed. If "
                  "110_43 works and this one never bursts, the answer is bracketed."),
    Arm("110_45_og_sc_coh0p6_swres22p2_r13", SC_PARENT, "OGSC",
        edits=(("cohesion", "6.0e+05", "as 110_43"),
               ("slip_weakening_residual_friction_angle_degrees", "22.200",
                "21.175 -> 22.200: the model's burst runs to 45 um against the "
                "experiment's 22, so it over-weakens once it goes")),
        rationale="Timing and size of the burst are different parameters. This arm "
                  "fixes the size only if 110_43 has already fixed the timing."),

    # ---------------- OG-T: preload probes, flow path only ----------------
    Arm("110_46_og_t_lineport_r13", OT_PARENT, "OGT",
        og_t_ports=True, og_t_short_ramp=True,
        rationale="Line-source ports, ORIGINAL 53 s ramp. THE GATE. If the single-node "
                  "ports were the 72 mm drainage length, dp collapses and the short "
                  "ramp is enough. Baseline to beat: 110_08 at dp = 48.9 MPa."),
    Arm("110_47_og_t_lineport_drainends_r13", OT_PARENT, "OGT",
        og_t_ports=True, og_t_drain_ends=True, og_t_short_ramp=True,
        rationale="Line ports PLUS pore pressure held at 3 MPa on the end platens. "
                  "Only meaningful if 110_46 fails: it says the specimen also needs "
                  "axial drainage, which is a claim about Kalantar's apparatus that "
                  "the reading notes do NOT confirm. Read it as a bound, not a model."),
)


def replace_assignment(text: str, key: str, value: str, why: str) -> str:
    pat = re.compile(rf"^(?P<i>[ \t]*){re.escape(key)}\s*=\s*[^\n#]*(?:#.*)?$", re.M)
    hits = list(pat.finditer(text))
    if len(hits) != 1:
        raise RuntimeError(f"expected exactly one active {key!r}, found {len(hits)}")
    return pat.sub(rf"\g<i>{key} = {value}   # {NOTE}: {why}", text, count=1)


def output_bases(text: str, stem: str) -> str:
    for key, folder in (("exodus_file_base", "results_exodus_hpc"),
                        ("csv_file_base", "results_csv_hpc"),
                        ("checkpoint_file_base", "results_checkpoint_hpc")):
        text = replace_assignment(text, key, f"{folder}/{stem}_hpc", "self-named output")
    return text


# ---- OG-T specific surgery -------------------------------------------------

# Verified against OGT/mesh/kalantar2025_og_t_theta28_graded.e: a +-0.5 mm box in x
# and z around each port node catches 11 nodes spanning the full chord,
# y = -14.910 .. +14.910 mm, against a predicted half-width of
# sqrt(r^2 - x^2) = sqrt(0.02499^2 - 0.019819655^2) = 15.221 mm.
PORT_BOX_HALF = 5.0e-4
PORT_IN = (-0.019819655172, 0.012724650276)
PORT_OUT = (0.019819655172, 0.087275349724)

LINE_PORTS = """
  # {note}: LINE-SOURCE PORTS. The parent drained the whole specimen through two
  # single nodes (ExtraNodesetGenerator + use_closest_node), which is why 110_36's
  # measured drainage time constant, 3449 s, implies a 72 mm path -- radial
  # convergence into a point, not the 40 mm port spacing. The reading notes' plane-
  # channel model has the inlet and outlet spanning the full width W. These boxes
  # select that chord: 11 mesh nodes each, y = -14.910 .. +14.910 mm, verified.
  [source_in_line]
    type = BoundingBoxNodeSetGenerator
    input = source_out
    new_boundary = source_in_line
    bottom_left = '{ix0} -0.026 {iz0}'
    top_right = '{ix1} 0.026 {iz1}'
  []
  [source_out_line]
    type = BoundingBoxNodeSetGenerator
    input = source_in_line
    new_boundary = source_out_line
    bottom_left = '{ox0} -0.026 {oz0}'
    top_right = '{ox1} 0.026 {oz1}'
  []
"""


def og_t_line_ports(text: str) -> str:
    block = LINE_PORTS.format(
        note=NOTE,
        ix0=PORT_IN[0] - PORT_BOX_HALF, ix1=PORT_IN[0] + PORT_BOX_HALF,
        iz0=PORT_IN[1] - PORT_BOX_HALF, iz1=PORT_IN[1] + PORT_BOX_HALF,
        ox0=PORT_OUT[0] - PORT_BOX_HALF, ox1=PORT_OUT[0] + PORT_BOX_HALF,
        oz0=PORT_OUT[1] - PORT_BOX_HALF, oz1=PORT_OUT[1] + PORT_BOX_HALF,
    )
    # insert the two generators between source_out and the fault splitter, and
    # re-root the splitter on the last of them
    anchor = re.search(r"\n  \[fault_split_3d\]", text)
    if not anchor:
        raise RuntimeError("cannot find [fault_split_3d] to anchor the line ports")
    text = text[:anchor.start()] + "\n" + block.rstrip() + text[anchor.start():]
    pat = re.compile(r"(\[fault_split_3d\]\s*\n\s*type = OrcaFaultInterface3DGenerator\s*\n\s*)input = source_out\b")
    if not pat.search(text):
        raise RuntimeError("cannot re-root fault_split_3d onto source_out_line")
    text = pat.sub(rf"\g<1>input = source_out_line   # {NOTE}: line-source ports", text)
    # Repoint EVERY consumer of the ports -- the pressure BCs and, just as
    # importantly, the port postprocessors. inj_reaction_sum_pp / prod_reaction_sum_pp
    # are NodalSum over the port nodeset and flow_rate_pp is built straight off them,
    # so leaving them on the single node would report 1/11 of the injected mass while
    # the BC drove all 11. Confine the rewrite to everything AFTER the Mesh block, so
    # the generators that DEFINE source_in / source_out are untouched.
    mesh_end = re.search(r"\n\[\]\s*\n(?=\[)", text[text.index("[Mesh]"):])
    if not mesh_end:
        raise RuntimeError("cannot find the end of the [Mesh] block")
    cut = text.index("[Mesh]") + mesh_end.end()
    head, tail = text[:cut], text[cut:]
    n_in = len(re.findall(r"boundary = source_in\b", tail))
    n_out = len(re.findall(r"boundary = source_out\b", tail))
    if not (n_in and n_out):
        raise RuntimeError("expected port consumers after the Mesh block")
    tail = re.sub(r"boundary = source_in\b", "boundary = source_in_line", tail)
    tail = re.sub(r"boundary = source_out\b", "boundary = source_out_line", tail)
    print(f"    [{NOTE}] repointed {n_in} source_in and {n_out} source_out consumers")
    return head + tail


DRAIN_ENDS = f"""
  [drain_top]
    # {NOTE}: pore pressure held at the production value on the end platens. This is
    # a CLAIM ABOUT THE APPARATUS -- that Kalantar's platens are fluid-connected --
    # and the reading notes do not confirm it. Only meaningful if 110_46 fails.
    type = DirichletBC
    variable = pore_pressure
    boundary = top_nodeset
    value = ${{production_pressure}}
  []
  [drain_bottom]
    type = DirichletBC
    variable = pore_pressure
    boundary = bottom_nodeset
    value = ${{production_pressure}}
  []
"""


def og_t_drain_ends(text: str) -> str:
    pat = re.compile(r"(\[production\](?:(?!\[\]).)*?\[\]\n)", re.S)
    if not pat.search(text):
        raise RuntimeError("cannot find the [production] BC to append end drainage after")
    return pat.sub(rf"\g<1>{DRAIN_ENDS}", text, count=1)


def og_t_short_ramp(text: str) -> str:
    """Back to the parent-of-parents' 53 s ramp; probe ends at 600 s."""
    text = re.sub(
        r"expression = 'if\(t<2\.0,\$\{axial_pres_initial\},if\(t<10000\.0,"
        r"\$\{axial_pres_initial\}\+\(\$\{axial_pres_final\}-\$\{axial_pres_initial\}\)"
        r"\*\(t-2\.0\)/9998\.0,\$\{axial_pres_final\}\)\)'[^\n]*",
        "expression = 'if(t<2.0,${axial_pres_initial},if(t<55.0,${axial_pres_initial}"
        "+(${axial_pres_final}-${axial_pres_initial})*(t-2.0)/53.0,${axial_pres_final}))'"
        f"   # {NOTE}: back to the original 53 s ramp -- round 12 already priced the long one",
        text)
    text = replace_assignment(text, "end_time", "600",
                              "53 s ramp + 545 s of held-load drainage decay, which is "
                              "what fits the time constant")
    text = re.sub(r"time_t = '[^']*'[^\n]*",
                  f"time_t = '0.0 0.5 2.0 55.0 600.0'   # {NOTE}: 53 s ramp then hold", text)
    text = re.sub(r"time_dt = '[^']*'[^\n]*",
                  f"time_dt = '0.50 0.50 1.50 1.50 5.00'   # {NOTE}: see time_t", text)
    text = replace_assignment(text, "dtmax", "5.0", "segment limits govern")
    text = re.sub(r"(\[injection_pressure\](?:(?!\[\]).)*?)x = '[^']*'[^\n]*",
                  rf"\g<1>x = '0.0 600.0'   # {NOTE}: preload probe, no injection schedule",
                  text, count=1, flags=re.S)
    text = re.sub(r"(\[injection_pressure\](?:(?!\[\]).)*?)y = '[^']*'[^\n]*",
                  rf"\g<1>y = '3000000.0 3000000.0'   # {NOTE}: held at production_pressure",
                  text, count=1, flags=re.S)
    text = re.sub(r"(\[event_dt_cap\](?:(?!\[\]).)*?)x = '[^']*'[^\n]*",
                  rf"\g<1>x = '0 2.0'   # {NOTE}: no event to resolve", text, count=1, flags=re.S)
    text = re.sub(r"(\[event_dt_cap\](?:(?!\[\]).)*?)y = '[^']*'[^\n]*",
                  rf"\g<1>y = '5.0 5.0'   # {NOTE}: see x", text, count=1, flags=re.S)
    return text


def banner(arm: Arm) -> str:
    lines = [
        "#" * 78,
        f"# {arm.stem}",
        f"# {GENERATED}  -- do not hand-edit; regenerate instead.",
        f"# Parent: {arm.parent.relative_to(ROOT)}",
        "#",
    ]
    for key, value, why in arm.edits:
        lines.append(f"#   {key} = {value}")
        lines.append(f"#       {why}")
    if arm.og_t_ports:
        lines.append("#   line-source ports (BoundingBoxNodeSetGenerator, 11 nodes each)")
    if arm.og_t_drain_ends:
        lines.append("#   pore pressure held at 3 MPa on top_nodeset / bottom_nodeset")
    if arm.og_t_short_ramp:
        lines.append("#   preload ramp back to 53 s; probe ends at 600 s")
    if not arm.edits and not arm.og_t_ports:
        lines.append("#   NO PARAMETER CHANGE -- reproducibility control")
    lines += ["#", f"# {arm.rationale}", "#" * 78, ""]
    return "\n".join(lines)


def build(arm: Arm) -> Path:
    text = arm.parent.read_text()
    for key, value, why in arm.edits:
        text = replace_assignment(text, key, value, why)
    if arm.og_t_short_ramp:
        text = og_t_short_ramp(text)
    if arm.og_t_ports:
        text = og_t_line_ports(text)
    if arm.og_t_drain_ends:
        text = og_t_drain_ends(text)
    text = output_bases(text, arm.stem)
    out = KAL / arm.case_dir / f"{arm.stem}.i"
    if out.exists() and GENERATED not in out.read_text():
        raise RuntimeError(f"{out} exists and is not ours; refusing to overwrite")
    out.write_text(banner(arm) + text)
    return out


def main() -> int:
    for arm in ARMS:
        print(f"wrote {build(arm).relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
