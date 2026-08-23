#!/bin/bash

#SBATCH --job-name=110_03_og_t_bbfast_r1_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025/OGT
#SBATCH --account=def-biaoli66
#SBATCH --time=3-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --output=logs/110_03_og_t_bbfast_r1_hpc_%j.out
#SBATCH --error=logs/110_03_og_t_bbfast_r1_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025/OGT

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc logs

srun --mpi=pmi2 -n 64 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 110_03_og_t_bbfast_r1.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc/110_03_og_t_bbfast_r1_hpc \
    exodus_file_base=results_exodus_hpc/110_03_og_t_bbfast_r1_hpc
