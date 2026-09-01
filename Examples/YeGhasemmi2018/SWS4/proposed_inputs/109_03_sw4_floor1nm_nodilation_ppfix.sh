#!/bin/bash

#SBATCH --job-name=109_03_sw4_floor1nm_nodilation_ppfix
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4
#SBATCH --account=def-biaoli66
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/109_03_sw4_floor1nm_nodilation_ppfix_%j.out
#SBATCH --error=logs/109_03_sw4_floor1nm_nodilation_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM=109_03_sw4_floor1nm_nodilation_ppfix
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4

cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "${CASE_STEM}.i" \
  Outputs/chk/enable=false \
  "csv_file_base=results_csv_hpc_rorqual/${CASE_STEM}" \
  "exodus_file_base=results_exodus_hpc_rorqual/${CASE_STEM}"
