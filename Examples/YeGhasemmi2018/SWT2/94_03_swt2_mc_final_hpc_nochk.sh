#!/bin/bash

#SBATCH --job-name=94_03_swt2_mc_final_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT2
#SBATCH --account=def-biaoli66
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/94_03_swt2_mc_final_hpc_%j.out
#SBATCH --error=logs/94_03_swt2_mc_final_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT2

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

srun --mpi=pmi2 -n 16 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 94_03_swt2_mc_final.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/94_03_swt2_mc_final_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/94_03_swt2_mc_final_hpc
