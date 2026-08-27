#!/bin/bash

#SBATCH --job-name=103_03_sw3_weakexp1p0_ppfix_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3
#SBATCH --account=def-biaoli66
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/103_03_sw3_weakexp1p0_ppfix_hpc_%j.out
#SBATCH --error=logs/103_03_sw3_weakexp1p0_ppfix_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

# ---------------------------------------------------------------------------
# 103-series control: slip_weakening_exponent 1.4 -> 1.0, and nothing else.
# Tests whether the weakening EXPONENT is what places the slip transition, i.e.
# whether it explains the 102-series Mohr-Coulomb failing one injection stage
# early.  See scripts/build_103_weakening_exponent_decks.py for the derivation
# and the pre-registered prediction/falsifier.
#
# 6402 steps at dtmax = 0.75; measured 1.39 s/step on 32 ranks for a mesh-5 deck
# of this size, i.e. ~2.5 h.  --time=06:00:00 leaves generous margin.
#
# This deck KEEPS the paper's monotonic schedule, so unlike the 97/98/101
# discussion decks it IS scoreable with scripts/table2_gate.py, and its score is
# directly comparable to its 100-series parent and its 102-series pair.
# ---------------------------------------------------------------------------

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 103_03_sw3_weakexp1p0_ppfix.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/103_03_sw3_weakexp1p0_ppfix_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/103_03_sw3_weakexp1p0_ppfix_hpc
