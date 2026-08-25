#!/usr/bin/env python3
"""
make_kalantar_jobs.py -- SLURM scripts for the 110-series Kalantar decks.

Resourcing is deliberately NOT copied from the Ye2018 mesh-5 jobs. Those ran a
3500 s schedule; these run 3600 / 6800 / 9100 s, so wall time scales with the
schedule, not with the mesh. The meshes are also finer at the fracture (0.98-1.04 mm
interface pitch against Ye2018's ~3 mm) and OG-SH carries 100k elements.

Every script is emitted through set_hpc_resources.verify, which raises if
`#SBATCH --ntasks` and `srun -n` disagree. That mismatch is the 97/98 truncation
bug: the scripts asked SLURM for one rank count and launched another, and the runs
were silently cut short.
"""

from __future__ import annotations

from pathlib import Path

from set_hpc_resources import verify

ROOT = Path(__file__).resolve().parents[1]
REMOTE = "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0"
ACCOUNT = "def-biaoli66"

NTASKS = 64
MEM_GB = 64

# The round-3 per-segment dt schedule cut the step count 4.2-5.0x. Budget from
# OG-SH's measured round-1 cost -- 24.3 s per solving ramp step and 1.65 s per hold
# step at 64 ranks -- gives about 4.3 h for OG-SH and 6.6 h for OG-SC. The 24 h
# request leaves 5.6x and 3.6x margins, respectively.
#
# Round 6 uses the same 24 h request for every submitted case, per the campaign
# resource constraint.  OG-T is intentionally a 60 s diagnostic probe rather than
# another invalid full schedule.
WALLTIME = "1-00:00:00"

JOBS = [
    ("Examples/Kalantar2025/OGSH", "110_13_og_sh_bbfast_r6", WALLTIME),
    ("Examples/Kalantar2025/OGT",  "110_14_og_t_preload_probe", WALLTIME),
    ("Examples/Kalantar2025/OGSC", "110_15_og_sc_bbfast_r6", WALLTIME),
]

TEMPLATE = """#!/bin/bash

#SBATCH --job-name={stem}_hpc
#SBATCH --chdir={remote}/{subdir}
#SBATCH --account={account}
#SBATCH --time={walltime}
#SBATCH --nodes=1
#SBATCH --ntasks={ntasks}
#SBATCH --cpus-per-task=1
#SBATCH --mem={mem}G
#SBATCH --output=logs/{stem}_hpc_%j.out
#SBATCH --error=logs/{stem}_hpc_%j.err

cd {remote}/{subdir}

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc logs

srun --mpi=pmi2 -n {ntasks} {remote}/orca-opt -i {stem}.i \\
    Outputs/chk/enable=false \\
    csv_file_base=results_csv_hpc/{stem}_hpc \\
    exodus_file_base=results_exodus_hpc/{stem}_hpc
"""


def main() -> int:
    for subdir, stem, walltime in JOBS:
        deck = ROOT / subdir / f"{stem}.i"
        if not deck.exists():
            raise SystemExit(f"no deck for {stem} -- run build_110_kalantar_decks.py first")
        text = TEMPLATE.format(stem=stem, remote=REMOTE, subdir=subdir,
                               account=ACCOUNT, walltime=walltime,
                               ntasks=NTASKS, mem=MEM_GB)
        verify(text, NTASKS, MEM_GB, walltime)
        out = ROOT / subdir / f"{stem}_hpc.sh"
        out.write_text(text)
        out.chmod(0o755)
        print(f"  {NTASKS:>4} ranks {MEM_GB:>4}G {walltime}  ->  "
              f"{out.relative_to(ROOT)}")
    print("\nntasks and srun -n agree in every script (the 97/98 truncation check).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
