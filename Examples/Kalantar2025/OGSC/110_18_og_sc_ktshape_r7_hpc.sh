#!/bin/bash

#SBATCH --job-name=110_18_og_sc_ktshape_r7
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025/OGSC
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/110_18_og_sc_ktshape_r7_%j.out
#SBATCH --error=logs/110_18_og_sc_ktshape_r7_%j.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
stem=110_18_og_sc_ktshape_r7

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc logs

srun --mpi=pmi2 -n 32 "${project_root}/orca-opt" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc"
