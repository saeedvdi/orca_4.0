#!/bin/bash

#SBATCH --job-name=88_01_swt1_bbfast_vm2x_injfix_kernel_SV_biot0p6_hpc
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/88_01_swt1_bbfast_vm2x_injfix_kernel_SV_biot0p6_hpc_%j.out
#SBATCH --error=logs/88_01_swt1_bbfast_vm2x_injfix_kernel_SV_biot0p6_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual

# ---------------------------------------------------------------------------
# normal-closure stiffness bracket arm 1
# Outputs/chk/enable=false -- the cluster caps file count and a 32-rank
# MOOSE Checkpoint writes a _cp/ tree of one .rd per rank. Verified to
# suppress it entirely (see scripts/make_hpc_nochk_jobs.py). No checkpoint
# means no restart, so the wall time is set to 24:00:00; CSV is written
# incrementally, so even a killed job leaves a scoreable partial record.
# ---------------------------------------------------------------------------

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 88_01_swt1_bbfast_vm2x_injfix_kernel_SV_biot0p6.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/88_01_swt1_bbfast_vm2x_injfix_kernel_SV_biot0p6_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/88_01_swt1_bbfast_vm2x_injfix_kernel_SV_biot0p6_hpc
