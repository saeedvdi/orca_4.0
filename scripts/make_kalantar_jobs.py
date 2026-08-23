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
WALLTIME = "2-00:00:00"

JOBS = [
    ("Examples/Kalantar2025/OGSH", "110_01_og_sh_bbfast_r1"),
    ("Examples/Kalantar2025/OGT",  "110_03_og_t_bbfast_r1"),
    ("Examples/Kalantar2025/OGSC", "110_05_og_sc_bbfast_r1"),
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
    for subdir, stem in JOBS:
        text = TEMPLATE.format(stem=stem, remote=REMOTE, subdir=subdir,
                               account=ACCOUNT, walltime=WALLTIME,
                               ntasks=NTASKS, mem=MEM_GB)
        verify(text, NTASKS, MEM_GB, WALLTIME)
        out = ROOT / subdir / f"{stem}_hpc.sh"
        out.write_text(text)
        out.chmod(0o755)
        print(f"  {NTASKS:>4} ranks {MEM_GB:>4}G {WALLTIME}  ->  {out.relative_to(ROOT)}")
    print("\nntasks and srun -n agree in every script (the 97/98 truncation check).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
