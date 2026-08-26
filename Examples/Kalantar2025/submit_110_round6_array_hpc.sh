#!/bin/bash

# Submit all Kalantar round-6 cases with one command:
#
#   sbatch submit_110_round6_array_hpc.sh
#
# Array mapping:
#   0  OG-SH  110_13 corrected-frame D_c bracket
#   1  OG-T   110_14 26-degree preload probe (NOT the full diagnostic deck)
#   2  OG-SC  110_15 tangential-viscosity arm

#SBATCH --job-name=kalantar_110_r6
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#SBATCH --account=def-biaoli66
#SBATCH --time=1-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --array=0-2
#SBATCH --output=kalantar_110_r6_%A_%a.out
#SBATCH --error=kalantar_110_r6_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/Kalantar2025

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    case_dir=OGSH
    stem=110_13_og_sh_bbfast_r6
    ;;
  1)
    case_dir=OGT
    stem=110_14_og_t_preload_probe
    ;;
  2)
    case_dir=OGSC
    stem=110_15_og_sc_bbfast_r6
    ;;
  *)
    echo "Unexpected SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}" >&2
    exit 2
    ;;
esac

cd "${study_root}/${case_dir}"

if [[ ! -f "${stem}.i" ]]; then
  echo "Missing input deck: ${study_root}/${case_dir}/${stem}.i" >&2
  exit 3
fi

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc logs

echo "Starting array task ${SLURM_ARRAY_TASK_ID}: ${case_dir}/${stem}.i"
echo "SLURM job ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}; 64 ranks, 64G, 24 h"

srun --mpi=pmi2 -n 64 "${project_root}/orca-opt" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc"
