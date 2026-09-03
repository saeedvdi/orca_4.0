#!/bin/bash

#SBATCH --job-name=110_03_sw3_floor1nm_nogouge_ppfix
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3
#SBATCH --account=def-biaoli66
#SBATCH --time=8:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=24G
#SBATCH --output=proposed_inputs/paper_revision_20260901_sw3_followup/logs/110_03_sw3_floor1nm_nogouge_ppfix_%j.out
#SBATCH --error=proposed_inputs/paper_revision_20260901_sw3_followup/logs/110_03_sw3_floor1nm_nogouge_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM=110_03_sw3_floor1nm_nogouge_ppfix
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS3
RUN_DIR=proposed_inputs/paper_revision_20260901_sw3_followup

cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p "${RUN_DIR}/csv" "${RUN_DIR}/exodus" "${RUN_DIR}/logs"

srun --mpi=pmi2 -n 8 "${PROJECT_ROOT}/orca-opt" -i "proposed_inputs/${CASE_STEM}.i" \
  Outputs/chk/enable=false
