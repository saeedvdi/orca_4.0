#!/bin/bash

# Submit the bounded Kalantar Round-9 mechanism diagnostics with:
#
#   cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#   sbatch submit_110_round9_array_hpc.sh
#
# Array map:
#   0  OG-T   110_23  graded 28-degree mesh, 60-s preload probe (pending Round-8 arm)
#   1  OG-SC  110_24  uniform paper-mean pressure traction, through stage 7
#   2  OG-SH  110_25  RSF direct-rate control, a=0.010 b=0, through stage 5
#   3  OG-SH  110_26  RSF aging arm, a=0.010 b=0.006, through stage 5

#SBATCH --job-name=kalantar_110_r9
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#SBATCH --account=def-biaoli66
#SBATCH --time=1-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --array=0-3
#SBATCH --output=kalantar_110_r9_%A_%a.out
#SBATCH --error=kalantar_110_r9_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/Kalantar2025

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    case_dir=OGT
    stem=110_23_og_t_graded_preload_r8
    ;;
  1)
    case_dir=OGSC
    stem=110_24_og_sc_papermean_r9
    ;;
  2)
    case_dir=OGSH
    stem=110_25_og_sh_rsf_a010_b000_r9
    ;;
  3)
    case_dir=OGSH
    stem=110_26_og_sh_rsf_a010_b006_r9
    ;;
  *)
    echo "Unexpected SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}" >&2
    exit 2
    ;;
esac

case_path=${study_root}/${case_dir}
input_path=${case_path}/${stem}.i
executable=${project_root}/orca-opt

if [[ ! -f "${input_path}" ]]; then
  echo "Missing input deck: ${input_path}" >&2
  exit 3
fi

if [[ ! -x "${executable}" ]]; then
  echo "Missing or non-executable application: ${executable}" >&2
  exit 4
fi

cd "${case_path}"

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc results_checkpoint_hpc logs

echo "Starting array task ${SLURM_ARRAY_TASK_ID}: ${case_dir}/${stem}.i"
echo "SLURM job ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}; 64 ranks, 64G, 24 h"

srun --mpi=pmi2 -n 64 "${executable}" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc"
