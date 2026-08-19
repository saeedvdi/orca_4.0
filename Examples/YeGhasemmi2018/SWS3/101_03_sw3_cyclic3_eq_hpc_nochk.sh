#!/bin/bash

#SBATCH --job-name=101_03_sw3_cyclic3_eq_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3
#SBATCH --account=def-biaoli66
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/101_03_sw3_cyclic3_eq_hpc_%j.out
#SBATCH --error=logs/101_03_sw3_cyclic3_eq_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

# ---------------------------------------------------------------------------
# 101-series discussion deck: equal-peak 3-cycle
#
# RESOURCES ARE SIZED FROM THE STEP COUNT, NOT THE SIMULATED DURATION.  This
# deck runs 15793 s at dtmax = 0.75 s, i.e. >= 21057 steps.  At the
# measured 5.3 s/step on 16 ranks and an assumed 1.6x from 16 -> 32 ranks, that
# is ~19.3 h, so --time=48:00:00.  The 97-series jobs died because they
# inherited 16 ranks / 12 h from a template while their own documentation
# advertised 32 ranks / 24 h, and because the wall estimate was made from
# simulated seconds against a deck with a 2x coarser dtmax.
#
# Outputs/chk/enable=false -- the cluster caps file count and a 32-rank MOOSE
# Checkpoint writes a _cp/ tree of one .rd per rank.  No checkpoint means no
# restart, but CSV is written incrementally, so even a killed job leaves a
# readable partial record.
# ---------------------------------------------------------------------------

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 101_03_sw3_cyclic3_eq.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/101_03_sw3_cyclic3_eq_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/101_03_sw3_cyclic3_eq_hpc
