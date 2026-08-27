#!/bin/bash

# Nine-run equal-budget MC sweep: center plus an eight-run fractional design.
# Submit all: sbatch SWS3_OrcaMohrCoulombContactTraction.sh
# Center only: sbatch --array=0 SWS3_OrcaMohrCoulombContactTraction.sh

#SBATCH --job-name=mc_sws3_sweep
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-8
#SBATCH --output=logs/SWS3_OrcaMohrCoulombContactTraction_%A_%a.out
#SBATCH --error=logs/SWS3_OrcaMohrCoulombContactTraction_%A_%a.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS3
INPUT=SWS3_OrcaMohrCoulombContactTraction.i
LABELS=(center pb01 pb02 pb03 pb04 pb05 pb06 pb07 pb08)
MU_ROUGH=(0.8818 0.811256 0.811256 0.811256 0.811256 0.952344 0.952344 0.952344 0.952344)
C_ROUGH=(2.645e6 2.3805e6 2.3805e6 2.9095e6 2.9095e6 2.3805e6 2.3805e6 2.9095e6 2.9095e6)
MU_SMOOTH=(0.1486 0.130768 0.166432 0.130768 0.166432 0.130768 0.166432 0.130768 0.166432)
C_SMOOTH=(1.4e6 1.61e6 1.61e6 1.19e6 1.19e6 1.19e6 1.19e6 1.61e6 1.61e6)
D_ROUGH=(4e-5 5e-5 3e-5 5e-5 3e-5 3e-5 5e-5 3e-5 5e-5)

IDX=${SLURM_ARRAY_TASK_ID:-0}
if (( IDX < 0 || IDX >= ${#LABELS[@]} )); then
  echo "SLURM_ARRAY_TASK_ID must be between 0 and 8" >&2
  exit 2
fi

STEM=SWS3_OrcaMohrCoulombContactTraction_${LABELS[$IDX]}
cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_mc_sweep_hpc results_exodus_mc_sweep_hpc logs

echo "Running ${STEM}: mu_r=${MU_ROUGH[$IDX]}, c_r=${C_ROUGH[$IDX]}, mu_s=${MU_SMOOTH[$IDX]}, c_s=${C_SMOOTH[$IDX]}, D_R=${D_ROUGH[$IDX]}"
srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "${INPUT}" \
  Outputs/chk/enable=false \
  "Materials/czm_contact/friction_coefficient_rough=${MU_ROUGH[$IDX]}" \
  "Materials/czm_contact/cohesion_rough=${C_ROUGH[$IDX]}" \
  "Materials/czm_contact/friction_coefficient_smooth=${MU_SMOOTH[$IDX]}" \
  "Materials/czm_contact/cohesion_smooth=${C_SMOOTH[$IDX]}" \
  "Materials/czm_contact/roughness_decay_distance=${D_ROUGH[$IDX]}" \
  "csv_file_base=results_csv_mc_sweep_hpc/${STEM}" \
  "exodus_file_base=results_exodus_mc_sweep_hpc/${STEM}"
