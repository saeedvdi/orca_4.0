#!/bin/bash

#SBATCH --job-name=87_02_swt2_bbfast_injfix_kernel_SV_biot0p6
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6_%j.out
#SBATCH --error=logs/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT2

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv results_exodus

# ---------------------------------------------------------------------------
# injection-schedule refit; still queued behind the local machine
# Outputs/chk/enable=false -- the cluster caps file count and a 32-rank
# MOOSE Checkpoint writes a _cp/ tree of one .rd per rank. Verified to
# suppress it entirely (see scripts/make_hpc_nochk_jobs.py). No checkpoint
# means no restart, so the wall time is set to 24:00:00; CSV is written
# incrementally, so even a killed job leaves a scoreable partial record.
# ---------------------------------------------------------------------------

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 87_02_swt2_bbfast_injfix_kernel_SV_biot0p6.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6_hpc \
    exodus_file_base=results_exodus/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6_hpc