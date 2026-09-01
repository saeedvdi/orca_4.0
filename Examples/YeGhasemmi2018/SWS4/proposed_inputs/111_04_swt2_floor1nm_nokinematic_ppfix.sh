#!/bin/bash

#SBATCH --job-name=111_04_swt2_floor1nm_nokinematic_ppfix
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT2
#SBATCH --account=def-biaoli66
#SBATCH --time=8:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --output=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs/111_04_swt2_floor1nm_nokinematic_ppfix_%j.out
#SBATCH --error=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs/111_04_swt2_floor1nm_nokinematic_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM=111_04_swt2_floor1nm_nokinematic_ppfix
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWT2
RESULTS_ROOT=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4/proposed_inputs/results
CSV_DIR=${RESULTS_ROOT}/results_csv
EXODUS_DIR=${RESULTS_ROOT}/results_exodus

cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
if [[ ! -d "${CSV_DIR}" || ! -d "${EXODUS_DIR}" ]]; then
    echo "Missing result directory: ${CSV_DIR} and/or ${EXODUS_DIR}" >&2
    exit 1
fi

srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "${CASE_DIR}/proposed_inputs/${CASE_STEM}.i" \
    Outputs/chk/enable=false \
    "csv_file_base=${CSV_DIR}/${CASE_STEM}" \
    "exodus_file_base=${EXODUS_DIR}/${CASE_STEM}"
