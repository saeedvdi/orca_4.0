#!/bin/bash

# Submit the bounded Kalantar Round-10 closure batch with:
#
#   cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#   sbatch submit_110_round10_array_hpc.sh
#
# Array map:
#   0  OG-T   110_29  graded-mesh full 17-stage cycle, 6800 s
#   1  OG-SH  110_27  RSF aging bracket, a=0.010 b=0.002, full 9-stage cycle
#   2  OG-SH  110_28  RSF aging bracket, a=0.010 b=0.004, full 9-stage cycle

#SBATCH --job-name=kalantar_110_r10
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#SBATCH --account=def-biaoli66
#SBATCH --time=3-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --array=0-2
#SBATCH --output=kalantar_110_r10_%A_%a.out
#SBATCH --error=kalantar_110_r10_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/Kalantar2025

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    case_dir=OGT
    stem=110_29_og_t_graded_full_r10
    ranks=64
    ;;
  1)
    case_dir=OGSH
    stem=110_27_og_sh_rsf_a010_b002_r10
    ranks=64
    ;;
  2)
    case_dir=OGSH
    stem=110_28_og_sh_rsf_a010_b004_r10
    ranks=64
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
echo "SLURM job ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}; ${ranks} ranks, 64G, 72 h"

srun --mpi=pmi2 -n "${ranks}" "${executable}" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc"
