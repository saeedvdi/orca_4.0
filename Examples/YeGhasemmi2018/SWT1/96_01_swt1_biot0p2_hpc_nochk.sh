#!/bin/bash

#SBATCH --job-name=96_01_swt1_biot0p2_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/96_01_swt1_biot0p2_hpc_%j.out
#SBATCH --error=logs/96_01_swt1_biot0p2_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 96_01_swt1_biot0p2.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/96_01_swt1_biot0p2_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/96_01_swt1_biot0p2_hpc
