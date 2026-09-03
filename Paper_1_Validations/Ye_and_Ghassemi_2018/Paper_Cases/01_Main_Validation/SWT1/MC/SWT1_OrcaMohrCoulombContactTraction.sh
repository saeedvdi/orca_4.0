#!/bin/bash

# Nine-run equal-budget MC sweep: center plus an eight-run fractional design.
# Submit all: sbatch SWT1_OrcaMohrCoulombContactTraction.sh
# Center only: sbatch --array=0 SWT1_OrcaMohrCoulombContactTraction.sh

#SBATCH --job-name=mc_swt1_sweep
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-8
#SBATCH --output=logs/SWT1_OrcaMohrCoulombContactTraction_%A_%a.out
#SBATCH --error=logs/SWT1_OrcaMohrCoulombContactTraction_%A_%a.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWT1
INPUT=SWT1_OrcaMohrCoulombContactTraction.i
LABELS=(center pb01 pb02 pb03 pb04 pb05 pb06 pb07 pb08)
MU_ROUGH=(0.5536 0.509312 0.509312 0.509312 0.509312 0.597888 0.597888 0.597888 0.597888)
C_ROUGH=(3.7034e7 3.33306e7 3.33306e7 4.07374e7 4.07374e7 3.33306e7 3.33306e7 4.07374e7 4.07374e7)
MU_SMOOTH=(0.5717 0.503096 0.640304 0.503096 0.640304 0.503096 0.640304 0.503096 0.640304)
C_SMOOTH=(9.19e6 1.05685e7 1.05685e7 7.8115e6 7.8115e6 7.8115e6 7.8115e6 1.05685e7 1.05685e7)
D_ROUGH=(1.5e-4 1.875e-4 1.125e-4 1.875e-4 1.125e-4 1.125e-4 1.875e-4 1.125e-4 1.875e-4)

IDX=${SLURM_ARRAY_TASK_ID:-0}
if (( IDX < 0 || IDX >= ${#LABELS[@]} )); then
  echo "SLURM_ARRAY_TASK_ID must be between 0 and 8" >&2
  exit 2
fi

STEM=SWT1_OrcaMohrCoulombContactTraction_${LABELS[$IDX]}
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
