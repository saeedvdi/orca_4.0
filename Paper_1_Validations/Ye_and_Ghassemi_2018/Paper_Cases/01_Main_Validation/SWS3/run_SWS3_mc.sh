#!/bin/bash
# Staged run script -- generated for the Paper_Cases/01_Main_Validation layout.
# The deck is staged beside mesh/ so its input-relative `mesh_file` resolves.
# Override the repo root without editing this file:  ORCA_ROOT=/path sbatch ...
#SBATCH --job-name=mc_sws3
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/01_Main_Validation/SWS3/MC
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=6
#SBATCH --output=logs/SWS3_OrcaMohrCoulombContactTraction_%A_%a.out
#SBATCH --error=logs/SWS3_OrcaMohrCoulombContactTraction_%A_%a.err

set -euo pipefail

PROJECT_ROOT=${ORCA_ROOT:-/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0}
CASE_DIR=${PROJECT_ROOT}/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/01_Main_Validation/SWS3/MC
cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p logs

# Paper's selected MC member for SWS3 is 'pb06' (array index 6); that is
# the default above. Submit the full equal-budget sweep with:  sbatch --array=0-8
LABELS=(center pb01 pb02 pb03 pb04 pb05 pb06 pb07 pb08)
MU_ROUGH=(0.5536 0.509312 0.509312 0.509312 0.509312 0.597888 0.597888 0.597888 0.597888)
C_ROUGH=(3.7034e7 3.33306e7 3.33306e7 4.07374e7 4.07374e7 3.33306e7 3.33306e7 4.07374e7 4.07374e7)
MU_SMOOTH=(0.5717 0.503096 0.640304 0.503096 0.640304 0.503096 0.640304 0.503096 0.640304)
C_SMOOTH=(9.19e6 1.05685e7 1.05685e7 7.8115e6 7.8115e6 7.8115e6 7.8115e6 1.05685e7 1.05685e7)
D_ROUGH=(1.5e-4 1.875e-4 1.125e-4 1.875e-4 1.125e-4 1.125e-4 1.875e-4 1.125e-4 1.875e-4)

IDX=${SLURM_ARRAY_TASK_ID:-6}
if (( IDX < 0 || IDX >= ${#LABELS[@]} )); then
  echo "SLURM_ARRAY_TASK_ID must be 0..8" >&2; exit 2
fi
STEM=SWS3_OrcaMohrCoulombContactTraction_${LABELS[$IDX]}

# one self-contained folder per case (decks otherwise split the
# artifacts across results_exodus/, results_csv/, results_checkpoint/)
OUTDIR=results/${STEM}
mkdir -p "${OUTDIR}" logs
echo "deck : ${CASE_DIR}/SWS3_OrcaMohrCoulombContactTraction.i  (member ${LABELS[$IDX]})"
srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "SWS3_OrcaMohrCoulombContactTraction.i" \
  Outputs/chk/enable=false \
  "Materials/czm_contact/friction_coefficient_rough=${MU_ROUGH[$IDX]}" \
  "Materials/czm_contact/cohesion_rough=${C_ROUGH[$IDX]}" \
  "Materials/czm_contact/friction_coefficient_smooth=${MU_SMOOTH[$IDX]}" \
  "Materials/czm_contact/cohesion_smooth=${C_SMOOTH[$IDX]}" \
  "Materials/czm_contact/roughness_decay_distance=${D_ROUGH[$IDX]}" \
  "csv_file_base=${OUTDIR}/${STEM}" \
  "exodus_file_base=${OUTDIR}/${STEM}" \
  "checkpoint_file_base=${OUTDIR}/${STEM}_chk"
