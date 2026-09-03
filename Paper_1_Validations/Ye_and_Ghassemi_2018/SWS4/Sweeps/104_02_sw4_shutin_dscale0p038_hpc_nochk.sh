#!/bin/bash

#SBATCH --job-name=104_02_sw4_shutin_dscale0p038_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/104_02_sw4_shutin_dscale0p038_hpc_%j.out
#SBATCH --error=logs/104_02_sw4_shutin_dscale0p038_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

# ---------------------------------------------------------------------------
# 104-series follow-up
#
# RESOURCES ARE SIZED FROM THE STEP COUNT, NOT THE SIMULATED DURATION.  This
# deck runs 5519 s at dtmax = 1.5 s, i.e. >= 3680 steps.  At the
# measured 5.3 s/step on 16 ranks and an assumed 1.6x from 16 -> 32 ranks, that
# is ~3.4 h, so --time=24:00:00.  The 97-series jobs died because they
# inherited 16 ranks / 12 h from a template while their own documentation
# advertised 32 ranks / 24 h, and because the wall estimate was made from
# simulated seconds against a deck with a 2x coarser dtmax.
#
# Outputs/chk/enable=false -- the cluster caps file count and a 32-rank MOOSE
# Checkpoint writes a _cp/ tree of one .rd per rank.  No checkpoint means no
# restart, but CSV is written incrementally, so even a killed job leaves a
# readable partial record.
# ---------------------------------------------------------------------------

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 104_02_sw4_shutin_dscale0p038.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/104_02_sw4_shutin_dscale0p038_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/104_02_sw4_shutin_dscale0p038_hpc
