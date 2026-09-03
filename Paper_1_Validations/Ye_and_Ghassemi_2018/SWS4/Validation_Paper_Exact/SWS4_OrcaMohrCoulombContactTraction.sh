#!/bin/bash

# Nine-run equal-budget MC sweep: center plus an eight-run fractional design.
# Submit all: sbatch SWS4_OrcaMohrCoulombContactTraction.sh
# Center only: sbatch --array=0 SWS4_OrcaMohrCoulombContactTraction.sh

#SBATCH --job-name=mc_sws4_sweep
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-8
#SBATCH --output=logs/SWS4_OrcaMohrCoulombContactTraction_%A_%a.out
#SBATCH --error=logs/SWS4_OrcaMohrCoulombContactTraction_%A_%a.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4
INPUT=SWS4_OrcaMohrCoulombContactTraction.i
LABELS=(center pb01 pb02 pb03 pb04 pb05 pb06 pb07 pb08)
MU_ROUGH=(0.9804 0.901968 0.901968 0.901968 0.901968 1.058832 1.058832 1.058832 1.058832)
C_ROUGH=(3.225e6 2.9025e6 2.9025e6 3.5475e6 3.5475e6 2.9025e6 2.9025e6 3.5475e6 3.5475e6)
MU_SMOOTH=(0.1139 0.100232 0.127568 0.100232 0.127568 0.100232 0.127568 0.100232 0.127568)
C_SMOOTH=(0 0 0 0 0 0 0 0 0)
D_ROUGH=(8e-5 1e-4 6e-5 1e-4 6e-5 6e-5 1e-4 6e-5 1e-4)

IDX=${SLURM_ARRAY_TASK_ID:-0}
if (( IDX < 0 || IDX >= ${#LABELS[@]} )); then
  echo "SLURM_ARRAY_TASK_ID must be between 0 and 8" >&2
  exit 2
fi

STEM=SWS4_OrcaMohrCoulombContactTraction_${LABELS[$IDX]}
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
  "bb_roughness_characteristic_slip=${D_ROUGH[$IDX]}" \
  "csv_file_base=results_csv_mc_sweep_hpc/${STEM}" \
  "exodus_file_base=results_exodus_mc_sweep_hpc/${STEM}"
