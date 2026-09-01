#!/bin/bash
#SBATCH --job-name=110_02_sw3_floor1nm_nodilation_ppfix
#SBATCH --account=def-biaoli66
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --output=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs/110_02_sw3_floor1nm_nodilation_ppfix_%j.out
#SBATCH --error=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs/110_02_sw3_floor1nm_nodilation_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS3
RESULTS_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4/proposed_inputs/results

cd "${CASE_DIR}"
srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" \
  -i "${CASE_DIR}/proposed_inputs/110_02_sw3_floor1nm_nodilation_ppfix.i" \
  Outputs/chk/enable=false \
  "csv_file_base=${RESULTS_DIR}/results_csv/110_02_sw3_floor1nm_nodilation_ppfix" \
  "exodus_file_base=${RESULTS_DIR}/results_exodus/110_02_sw3_floor1nm_nodilation_ppfix"
