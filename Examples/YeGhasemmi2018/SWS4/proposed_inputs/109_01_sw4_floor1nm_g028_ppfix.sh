#!/bin/bash

#SBATCH --job-name=109_01_sw4_floor1nm_g028_ppfix
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4
#SBATCH --account=def-biaoli66
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs/109_01_sw4_floor1nm_g028_ppfix_%j.out
#SBATCH --error=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs/109_01_sw4_floor1nm_g028_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM=109_01_sw4_floor1nm_g028_ppfix
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4
RESULTS_ROOT=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4/proposed_inputs/results
CSV_DIR=${RESULTS_ROOT}/results_csv
EXODUS_DIR=${RESULTS_ROOT}/results_exodus

# Run from the specimen directory, not from Sweeps/.  The deck's mesh path
# (../mesh/...) is resolved relative to the INPUT FILE, so it reaches SWS4/mesh
# from Sweeps/; the Outputs file_base paths are resolved relative to the
# WORKING DIRECTORY, so they must be read from SWS4/.
cd "${CASE_DIR}"

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU

# The requested result directories must already exist; do not create per-run
# output directories here.
if [[ ! -d "${CSV_DIR}" || ! -d "${EXODUS_DIR}" ]]; then
    echo "Missing result directory: ${CSV_DIR} and/or ${EXODUS_DIR}" >&2
    exit 1
fi

srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" \
    -i "${CASE_DIR}/proposed_inputs/${CASE_STEM}.i" \
    Outputs/chk/enable=false \
    "csv_file_base=${CSV_DIR}/${CASE_STEM}" \
    "exodus_file_base=${EXODUS_DIR}/${CASE_STEM}"
