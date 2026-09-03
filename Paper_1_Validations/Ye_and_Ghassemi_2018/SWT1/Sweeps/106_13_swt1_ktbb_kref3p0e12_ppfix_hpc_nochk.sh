#!/bin/bash

#SBATCH --job-name=106_13_swt1_ktbb_kref3p0e12_ppfix_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1/Sweeps
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/106_13_swt1_ktbb_kref3p0e12_ppfix_hpc_%j.out
#SBATCH --error=logs/106_13_swt1_ktbb_kref3p0e12_ppfix_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1/Sweeps

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 106_13_swt1_ktbb_kref3p0e12_ppfix.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/106_13_swt1_ktbb_kref3p0e12_ppfix_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/106_13_swt1_ktbb_kref3p0e12_ppfix_hpc
