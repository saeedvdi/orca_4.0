#!/bin/bash
# Staged run script -- generated for the Paper_Cases/01_Main_Validation layout.
# The deck is staged beside mesh/ so its input-relative `mesh_file` resolves.
# Override the repo root without editing this file:  ORCA_ROOT=/path sbatch ...
#SBATCH --job-name=bb_sws4
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/01_Main_Validation/SWS4
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/SWS4_OrcaBartonBandisContactTractionFastADHardening_%j.out
#SBATCH --error=logs/SWS4_OrcaBartonBandisContactTractionFastADHardening_%j.err

set -euo pipefail

PROJECT_ROOT=${ORCA_ROOT:-/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0}
CASE_DIR=${PROJECT_ROOT}/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/01_Main_Validation/SWS4
cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p logs

STEM=SWS4_OrcaBartonBandisContactTractionFastADHardening

# one self-contained folder per case (decks otherwise split the
# artifacts across results_exodus/, results_csv/, results_checkpoint/)
OUTDIR=results/${STEM}
mkdir -p "${OUTDIR}" logs
echo "deck : ${CASE_DIR}/${STEM}.i"
echo "mesh : $(grep -m1 '^mesh_file' ${STEM}.i)"
srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "${STEM}.i" \
  Outputs/chk/enable=false \
  "csv_file_base=${OUTDIR}/${STEM}" \
  "exodus_file_base=${OUTDIR}/${STEM}" \
  "checkpoint_file_base=${OUTDIR}/${STEM}_chk"
