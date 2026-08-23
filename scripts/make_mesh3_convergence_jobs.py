#!/usr/bin/env python3
"""
make_mesh3_convergence_jobs.py -- resource the eight mesh-3 convergence runs.

WHAT IS BEING RUN, AND WHY IT IS EIGHT JOBS
===========================================
The mesh-convergence study pairs each reported deck with a twin that differs
only in element size: 5 mm (reported) against 3 mm (about ten times the
elements). Four specimens times two constitutive laws is eight pairs, and the
mesh-5 half of every pair is already complete, so this generates the mesh-3
half:

    SW-T1  93_02 / 94_02      SW-T2  93_04 / 94_04
    SW-S3  93_06 / 94_06      SW-S4  93_08 / 94_08

Only SW-S4 has ever produced a complete mesh-3 pair. The other three died
partway: SW-T2 at stage 4 of 11, SW-S3 at stage 6, and SW-T1 at t = 70.5 s of
3500 -- still inside the confining preload, so it is not a near miss but a job
that barely started. Those runs were given 64 ranks, 64 G and 48 h, which is
what this batch changes.

WHY 128 RANKS AND 128 G
=======================
Saeed's call, and the two constraints behind it are worth recording. Time is
already at the 48 h ceiling those jobs used, so the only lever left is width;
128 ranks doubles it. Memory doubles with it because the mesh-3 SW-T1 problem
is the largest in the campaign and the 64 G runs left no headroom -- the SW-T1
mesh-3 CSV stops at 126 kB, which is consistent with dying early rather than
with a wall-clock kill.

The wall time is written as 2-00:00:00 rather than 48:00:00. They are the same
duration; the day-hour form is used because it is what Saeed asked for and it
survives a later edit more legibly.

WHAT THIS SCRIPT DELIBERATELY DOES NOT CHANGE
=============================================
Nothing except rank count, memory and wall time. The eight scripts already
carry the right --chdir, the checkpoint suppression, the output basenames and
the mkdir line, and the decks they launch are byte-verified twins of their
mesh-5 parents (mesh file, source-node coordinates and output basenames are the
only differences). Rewriting them from a template would risk reintroducing the
staleness that put another deck's file_base into four of them.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from set_hpc_resources import retarget  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "Examples", "YeGhasemmi2018")

NTASKS = 128
MEM_GB = 128
WALLTIME = "2-00:00:00"

JOBS = [
    ("SWT1", "93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3"),
    ("SWT1", "94_02_swt1_mc_final_mesh3"),
    ("SWT2", "93_04_swt2_final_theta30_resc9p71_ppfix_mesh3"),
    ("SWT2", "94_04_swt2_mc_final_mesh3"),
    ("SWS3", "93_06_sw3_final_resc1p40_ppfix_mesh3"),
    ("SWS3", "94_06_sw3_mc_final_mesh3"),
    ("SWS4", "93_08_sw4_final_theta30_jrc5_ppfix_mesh3"),
    ("SWS4", "94_08_sw4_mc_final_mesh3"),
]


def main() -> int:
    for sample, deck in JOBS:
        path = os.path.join(EX, sample, f"{deck}_hpc_nochk.sh")
        with open(path) as fh:
            before = fh.read()
        after = retarget(before, NTASKS, MEM_GB, WALLTIME)
        if after == before:
            print(f"unchanged  {sample}/{deck}_hpc_nochk.sh")
            continue
        with open(path, "w") as fh:
            fh.write(after)
        print(f"retargeted {sample}/{deck}_hpc_nochk.sh "
              f"-> {NTASKS} ranks, {MEM_GB}G, {WALLTIME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
