#!/usr/bin/env python3
"""
Build the Kalantar 2025 ROUND-11 platen-restraint series.

WHY THIS ROUND EXISTS
---------------------
Measured on the runs already in hand (all sampled at the same point in the preload,
5 um of joint slip), the ratio of the joint's own effective normal stress to the
paper-frame value it should be tracking is:

    OG-T   r7  (28 deg, traction control, 3.00 mm tip clearance)   0.515
    OG-T   r6  (26 deg, displacement control, 1.00 mm clearance)   0.509
    OG-T   r4  (28 deg, displacement control)                      0.520
    OG-SC  r6                                                      0.931
    OG-SH  r6                                                      0.999
    Ye SW-T1 100_01                                                0.969

OG-T delivers HALF the normal stress to its joint, on both meshes, under both load
trains.  Everything else in both campaigns tracks within 7 %.

WHAT THAT KILLS.  Round 3 blamed fracture-tip clearance and preregistered that the
1.00 mm mesh would be markedly worse than the 3.00 mm mesh.  It came out 0.509 vs
0.515 -- a 1 % move.  The tip-clearance hypothesis is REFUTED by its own falsifier.
Round 7's load-train swap is refuted the same way: 0.515 vs 0.520.

WHAT IS LEFT.  The one distinguishing feature never tested is the PLATEN.  Both end
faces are laterally free: `base_fixed_z` pins disp_z on the bottom only, the top
carries an axial traction or penalty in z only, and disp_x / disp_y are restrained
nowhere except the four rigid-body pin vertices.  OG-T's fracture spans 94 mm of a
100 mm core, so its two halves are two nearly-complete wedges with 3 mm end caps;
with frictionless platens they are free to translate laterally past one another and
the joint never builds normal stress.  OG-SH's 14.92 mm end caps carry that shear
themselves, which is why it scores 0.999.  Real triaxial platens are steel bonded
against ground rock, not frictionless.

THE ARMS (all inherit 110_16_og_t_traction_probe_r7.i; 60 s preload, no injection)
    110_30  OG-T   disp_x = disp_y = 0 on BOTH platens        -- the hypothesis
    110_31  OG-T   disp_x = disp_y = 0 on the BOTTOM platen   -- asymmetric control
    110_32  OG-T   platens free, JOINT LOCKED (c = 1 GPa)     -- the null

PASS GATE for 110_30: the pre-slip slope d(bb_effective_normal_stress)/d(sigma_d)
must come out at +0.20 +- 0.04 (the correct value is sin^2 28 deg = 0.2204); it is
currently -0.076.  Equivalently bb_effective_normal_stress_pp /
effective_normal_paper_frame_mpa_pp must reach 0.93 or better, matching OG-SC.

FALSIFIERS.  110_32 is the null: if the joint cannot slip and the ratio is STILL
~0.5, the shielding is elastic and no platen BC will fix it -- the mesh or the
interface map is at fault instead, and 110_30 will be a false positive.  110_31
must land between 110_30 and r7; if bonding one platen already recovers everything,
the mechanism is not symmetric rigid-body translation.

Wave B (built here but submitted only if 110_30 passes):
    110_35  OG-T   full 17-stage cycle with bonded platens
    110_33  OG-SH  r6 rerun with bonded platens  -- over-constraint control
    110_34  OG-SC  r6 rerun with bonded platens  -- over-constraint control
The two controls exist so that a 110_30 "pass" cannot be claimed without showing the
same change leaves the two specimens that ALREADY score 0.93-1.00 undamaged.

Idempotent: rerun freely, it overwrites its own outputs and touches nothing else.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDY = os.path.join(ROOT, "Examples", "Kalantar2025")

BASE_PROBE = os.path.join(STUDY, "OGT", "110_16_og_t_traction_probe_r7.i")
BASE_FULL = os.path.join(STUDY, "OGT", "110_29_og_t_graded_full_r10.i")
BASE_SH = os.path.join(STUDY, "OGSH", "110_13_og_sh_bbfast_r6.i")
BASE_SC = os.path.join(STUDY, "OGSC", "110_15_og_sc_bbfast_r6.i")

HPC_ROOT = "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0"

BOND_BLOCK = """  [platen_top_x]
    type = DirichletBC
    variable = disp_x
    boundary = top_nodeset
    value = 0
  []
  [platen_top_y]
    type = DirichletBC
    variable = disp_y
    boundary = top_nodeset
    value = 0
  []
  [platen_bottom_x]
    type = DirichletBC
    variable = disp_x
    boundary = bottom_nodeset
    value = 0
  []
  [platen_bottom_y]
    type = DirichletBC
    variable = disp_y
    boundary = bottom_nodeset
    value = 0
  []
"""

BOND_BOTTOM_ONLY = """  [platen_bottom_x]
    type = DirichletBC
    variable = disp_x
    boundary = bottom_nodeset
    value = 0
  []
  [platen_bottom_y]
    type = DirichletBC
    variable = disp_y
    boundary = bottom_nodeset
    value = 0
  []
"""


def read(path):
    with open(path) as fh:
        return fh.read().split("\n")


def strip_banner(lines):
    """Drop the inherited header, keeping everything from the '####' rule that
    immediately precedes the first `mesh_file =` assignment."""
    i = next(n for n, l in enumerate(lines) if l.startswith("mesh_file"))
    j = max(n for n in range(i) if re.fullmatch(r"#{10,}", lines[n].strip()))
    return lines[j:]


def retarget_outputs(lines, stem, results="hpc"):
    """Point the three *_file_base variables at this deck's own stem."""
    hits = 0
    for n, l in enumerate(lines):
        for key, kind in (("exodus_file_base", "exodus"),
                          ("csv_file_base", "csv"),
                          ("checkpoint_file_base", "checkpoint")):
            if l.startswith(key):
                pad = "    " if key == "csv_file_base" else ""
                lines[n] = (f"{key}{pad} = results_{kind}_{results}/{stem}_{results}"
                            f"   # ROUND 11: self-named")
                hits += 1
    assert hits == 3, f"expected 3 *_file_base lines, retargeted {hits}"
    return lines


def insert_bcs(lines, block):
    """Insert extra BCs immediately before the [injection] block inside [BCs]."""
    start = next(n for n, l in enumerate(lines) if l.strip() == "[BCs]")
    n = next(k for k in range(start, len(lines)) if lines[k].strip() == "[injection]")
    return lines[:n] + block.rstrip("\n").split("\n") + lines[n:]


def lock_joint(lines):
    """Raise peak and residual cohesion to 1 GPa so the joint cannot slip."""
    hits = 0
    for n, l in enumerate(lines):
        if re.match(r"^    cohesion = ", l):
            lines[n] = ("    cohesion = 1.0e9   # ROUND 11 NULL: joint locked, "
                        "measures ELASTIC stress transfer with zero slip")
            hits += 1
        elif re.match(r"^    residual_cohesion = ", l):
            lines[n] = ("    residual_cohesion = 1.0e9   # ROUND 11 NULL: joint "
                        "locked, see peak cohesion above")
            hits += 1
    assert hits == 2, f"expected 2 cohesion lines, rewrote {hits}"
    return lines


def banner(stem, parent, title, body):
    rule = "# " + "=" * 77
    out = [rule, f"# {stem}", "#", f"# {title}",
           f"# Parent: {os.path.basename(parent)} (verbatim except the change below).", "#"]
    out += ["# " + l if l else "#" for l in body.strip("\n").split("\n")]
    out += ["#", "# Generated by scripts/make_110_round11_platen.py -- edit the script, not this file.",
            rule, ""]
    return out


def write(case_dir, stem, lines):
    path = os.path.join(STUDY, case_dir, stem + ".i")
    with open(path, "w") as fh:
        fh.write("\n".join(lines))
    print(f"  wrote {os.path.relpath(path, ROOT)}  ({len(lines)} lines)")


def build(case_dir, stem, base, title, body, bcs=None, locked=False, results="hpc"):
    lines = strip_banner(read(base))
    if bcs is not None:
        lines = insert_bcs(lines, bcs)
    if locked:
        lines = lock_joint(lines)
    lines = retarget_outputs(lines, stem, results)
    write(case_dir, stem, banner(stem, base, title, body) + lines)


# ---------------------------------------------------------------------------
# Wave A -- the three 60 s OG-T diagnostics
# ---------------------------------------------------------------------------
build(
    "OGT", "110_30_og_t_platen_bonded_r11", BASE_PROBE,
    "ROUND 11 -- OG-T BONDED PLATENS.  THE HYPOTHESIS ARM.",
    """
ONE CHANGE: disp_x and disp_y are held at zero on BOTH top_nodeset and
bottom_nodeset, i.e. the steel platens are bonded to the ground end faces
instead of being frictionless in the plane.  Mesh, fracture angle, initial
stress, pore pressure, joint law, axial traction ramp and the 60 s horizon are
untouched.

The four rigid-body pin vertices (no_disp_x / no_disp_y) are left in place.
They enforce the same zero value, so the overlap is consistent, not a conflict.

PASS GATE.  The pre-slip slope d(bb_effective_normal_stress)/d(sigma_d) must
reach +0.20 +- 0.04 against the correct sin^2(28 deg) = 0.2204; it is -0.076 in
110_16.  Equivalently bb_effective_normal_stress_pp divided by
effective_normal_paper_frame_mpa_pp must reach 0.93 or better (OG-SC's value);
it is 0.515 in 110_16.  tau/tau_limit must stay below 1.0 for the whole ramp,
so that sigma_d reaches the experiment's 160.43 MPa without the joint yielding.

FAIL MEANS.  If the ratio stays near 0.5, lateral platen freedom is not the
shielding mechanism and 110_32's null decides whether the fault is elastic
(mesh / interface map) rather than frictional.
""",
    bcs=BOND_BLOCK)

build(
    "OGT", "110_31_og_t_platen_base_bonded_r11", BASE_PROBE,
    "ROUND 11 -- OG-T BOTTOM PLATEN ONLY.  ASYMMETRIC CONTROL.",
    """
ONE CHANGE from 110_30: only the BOTTOM platen is bonded laterally; the top
platen keeps its in-plane freedom.

This exists to stop 110_30 being read as a single yes/no.  If the mechanism is
symmetric rigid-body translation of the two wedges, one bonded platen removes
about half the freedom and this arm must land BETWEEN 110_16 (0.515) and
110_30.  If it recovers the whole deficit on its own, the mechanism is not
symmetric translation and 110_30's success would be over-constraint rather than
a fix.
""",
    bcs=BOND_BOTTOM_ONLY)

build(
    "OGT", "110_32_og_t_locked_joint_r11", BASE_PROBE,
    "ROUND 11 -- OG-T LOCKED JOINT, FREE PLATENS.  THE NULL.",
    """
ONE CHANGE: peak and residual cohesion are raised to 1.0e9 Pa so the joint
cannot slip at any stress this preload reaches.  The platens keep their present
in-plane freedom.  This measures the ELASTIC stress transfer alone, with the
frictional response removed.

READ IT FIRST, BEFORE 110_30.  If bb_effective_normal_stress_pp divided by
effective_normal_paper_frame_mpa_pp is near sin^2(28 deg) behaviour here, the
elastic load path is sound and the 0.515 deficit is produced by slip -- the
platen arm is then the right fix.  If the ratio is STILL near 0.5 with ZERO
slip, the deficit is elastic, no boundary condition on the platens can repair
it, and any apparent success in 110_30 is over-constraint masking a mesh or
interface-map defect.  In that case the next step is the interface itself, not
another BC arm.
""",
    locked=True)

# ---------------------------------------------------------------------------
# Wave B -- gated on 110_30 passing
# ---------------------------------------------------------------------------
build(
    "OGT", "110_35_og_t_platen_bonded_full_r11", BASE_FULL,
    "ROUND 11 -- OG-T FULL 17-STAGE CYCLE WITH BONDED PLATENS.",
    """
The Round-10 full OG-T deck with the 110_30 platen restraint applied.  Nothing
else changes: same graded mesh, same joint law, same 6800 s injection schedule.

DO NOT SUBMIT THIS UNTIL 110_30 HAS PASSED ITS GATE.  Every OG-T validation
datum to date was taken from a specimen that had already yielded during its own
preload, so this is the first OG-T deck whose Table-2 comparison is meaningful.
""",
    bcs=BOND_BLOCK)

build(
    "OGSH", "110_33_og_sh_platen_bonded_r11", BASE_SH,
    "ROUND 11 -- OG-SH OVER-CONSTRAINT CONTROL.",
    """
110_13_og_sh_bbfast_r6 with the 110_30 platen restraint and nothing else.

OG-SH already scores 0.999 on the normal-stress ratio and 9/9 on Table 2, so it
has no deficit for this change to repair.  Its only job is to show the change
does no harm: the Table-2 score must not degrade.  If bonding the platens
damages OG-SH, the restraint is over-constraint and 110_30's result cannot be
accepted at face value.
""",
    bcs=BOND_BLOCK)

build(
    "OGSC", "110_34_og_sc_platen_bonded_r11", BASE_SC,
    "ROUND 11 -- OG-SC OVER-CONSTRAINT CONTROL.",
    """
110_15_og_sc_bbfast_r6 with the 110_30 platen restraint and nothing else.

OG-SC sits at 0.931 on the normal-stress ratio -- the only specimen besides
OG-T with a visible deficit, and it has the second-smallest tip clearance
(6.72 mm).  It is therefore both a do-no-harm control and a weak positive test:
if the mechanism is real, OG-SC should move a little towards 1.0 while its
13/13 Table-2 score holds.
""",
    bcs=BOND_BLOCK)

print("\nround 11 decks built.")
