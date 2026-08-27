#!/bin/bash

# Nine-run equal-budget MC sweep: center plus an eight-run fractional design.
# Submit all: sbatch SWT2_OrcaMohrCoulombContactTraction.sh
# Center only: sbatch --array=0 SWT2_OrcaMohrCoulombContactTraction.sh

#SBATCH --job-name=mc_swt2_sweep
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT2
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-8
#SBATCH --output=logs/SWT2_OrcaMohrCoulombContactTraction_%A_%a.out
#SBATCH --error=logs/SWT2_OrcaMohrCoulombContactTraction_%A_%a.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWT2
INPUT=SWT2_OrcaMohrCoulombContactTraction.i
LABELS=(center pb01 pb02 pb03 pb04 pb05 pb06 pb07 pb08)
MU_ROUGH=(0.5528 0.508576 0.508576 0.508576 0.508576 0.597024 0.597024 0.597024 0.597024)
C_ROUGH=(4.2959e7 3.86631e7 3.86631e7 4.72549e7 4.72549e7 3.86631e7 3.86631e7 4.72549e7 4.72549e7)
MU_SMOOTH=(0.5717 0.503096 0.640304 0.503096 0.640304 0.503096 0.640304 0.503096 0.640304)
C_SMOOTH=(9.71e6 1.11665e7 1.11665e7 8.2535e6 8.2535e6 8.2535e6 8.2535e6 1.11665e7 1.11665e7)
D_ROUGH=(1.5e-4 1.875e-4 1.125e-4 1.875e-4 1.125e-4 1.125e-4 1.875e-4 1.125e-4 1.875e-4)

IDX=${SLURM_ARRAY_TASK_ID:-0}
if (( IDX < 0 || IDX >= ${#LABELS[@]} )); then
  echo "SLURM_ARRAY_TASK_ID must be between 0 and 8" >&2
  exit 2
fi

STEM=SWT2_OrcaMohrCoulombContactTraction_${LABELS[$IDX]}
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
