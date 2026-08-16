#!/usr/bin/env python3
"""
make_hpc_nochk_jobs.py -- generate checkpoint-free SLURM scripts for the HPC.

WHY CHECKPOINT-FREE
===================
The cluster caps the number of files in the project space, and a MOOSE
Checkpoint is file-count-hostile: it writes a <base>_cp/ tree with one
<step>-restart-<rank>.rd per rank plus a mesh blob, per retained checkpoint.
At 32 ranks that is tens of files and several directories per job, and the decks
run 4 jobs at a time.

HOW IT IS SUPPRESSED, AND HOW THAT WAS VERIFIED
===============================================
Outputs/chk/enable=false on the command line. This works because
OutputWarehouse::outputStep() gates on obj->enabled() before dispatching, so a
disabled Checkpoint is never reached -- including on the interrupt-signal path
inside Output::outputStep(), which sits behind the same gate. This MOOSE version
has no automatic checkpoint (CommonOutputAction creates none), so the deck's
explicit [chk] block is the only one to disable.

That was not taken on faith. Two-arm test on 87_02, 1 rank, num_steps=2,
time_step_interval=1, output redirected to scratch:

    checkpoint ON   ->  8 files,  6 dirs, chk_cp/0002-restart-0.rd present
    enable=false    ->  2 files,  1 dir,  no chk_cp at all

CSV and Exodus are untouched by the flag.

WHY DELETING THE [chk] BLOCK WOULD HAVE BEEN WORSE
==================================================
It would fork every deck into a local copy and an HPC copy that then drift. The
command-line override keeps ONE deck, so a local run and an HPC run of the same
name are the same physics by construction. It is also compatible with the decks'
${checkpoint_file_base} variable, which must stay referenced or MOOSE aborts on
"unused parameter" (this is exactly what killed the first verification attempt).

WALL-CLOCK NOTE
===============
Without checkpoints a job that hits the time limit cannot be resumed. The
mitigation is that CSV is written incrementally, so a killed job still yields a
scoreable partial record up to the kill -- and the scorecard reads CSV, not
Exodus. Exodus here is execute_on = FINAL, so a killed job produces none. Time
is set generously below for that reason.
"""

import os
import re
import stat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "Examples", "YeGhasemmi2018")
TEMPLATE = os.path.join(EX, "SWT1", "87_01_swt1_bbfast_injfix_kernel_SV_biot0p6.sh")
TEMPLATE_DECK = "87_01_swt1_bbfast_injfix_kernel_SV_biot0p6"

WALLTIME = "24:00:00"

JOBS = [
    ("SWT2", "87_02_swt2_bbfast_injfix_kernel_SV_biot0p6",
     "injection-schedule refit; still queued behind the local machine"),
    ("SWT1", "88_01_swt1_bbfast_vm2x_injfix_kernel_SV_biot0p6",
     "normal-closure stiffness bracket arm 1"),
    ("SWT1", "88_02_swt1_bbfast_vmopt_injfix_kernel_SV_biot0p6",
     "normal-closure stiffness bracket arm 2"),
    ("SWT1", "88_03_swt1_bbfast_vmopt_kni_injfix_kernel_SV_biot0p6",
     "normal-closure stiffness bracket arm 3"),
]


def main():
    with open(TEMPLATE) as fh:
        template = fh.read()

    for sample, deck, note in JOBS:
        text = template.replace(TEMPLATE_DECK, deck).replace("/SWT1", f"/{sample}")

        text = re.sub(r"^#SBATCH --time=.*$", f"#SBATCH --time={WALLTIME}",
                      text, flags=re.M)

        # results_checkpoint is never written now; do not create it either.
        text = text.replace("mkdir -p results_csv results_exodus results_checkpoint",
                            "mkdir -p results_csv results_exodus")

        # Suppress the checkpoint and give the HPC run its own output basenames so
        # it cannot overwrite a local run of the same deck.
        text = re.sub(
            r"^(srun .*?-i \S+)\s*$",
            lambda m: (
                f"{m.group(1)} \\\n"
                f"    Outputs/chk/enable=false \\\n"
                f"    csv_file_base=results_csv/{deck}_hpc \\\n"
                f"    exodus_file_base=results_exodus/{deck}_hpc"
            ),
            text, flags=re.M)

        banner = (
            "\n# ---------------------------------------------------------------------------\n"
            f"# {note}\n"
            "# Outputs/chk/enable=false -- the cluster caps file count and a 32-rank\n"
            "# MOOSE Checkpoint writes a _cp/ tree of one .rd per rank. Verified to\n"
            "# suppress it entirely (see scripts/make_hpc_nochk_jobs.py). No checkpoint\n"
            "# means no restart, so the wall time is set to " + WALLTIME + "; CSV is written\n"
            "# incrementally, so even a killed job leaves a scoreable partial record.\n"
            "# ---------------------------------------------------------------------------\n"
        )
        text = text.replace("\nsrun ", banner + "\nsrun ", 1)

        out = os.path.join(EX, sample, deck + "_hpc_nochk.sh")
        with open(out, "w") as fh:
            fh.write(text)
        os.chmod(out, os.stat(out).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"wrote {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main()
