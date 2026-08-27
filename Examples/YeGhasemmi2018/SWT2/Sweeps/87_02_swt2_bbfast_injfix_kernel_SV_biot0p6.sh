#!/bin/bash

#SBATCH --job-name=87_02_swt2_bbfast_injfix_kernel_SV_biot0p6_hpc
#SBATCH --account=def-biaoli66
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6_hpc_%j.out
#SBATCH --error=logs/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT2

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual results_checkpoint_hpc_rorqual

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 87_02_swt2_bbfast_injfix_kernel_SV_biot0p6.i
