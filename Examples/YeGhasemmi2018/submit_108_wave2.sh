#!/bin/bash
# =============================================================================
# 108-series, 108 wave2 -- 6 decks.
#
#   sbatch submit_108_wave2.sh
#
# Arm C (closure creep). REQUIRES an orca_v11 orca-opt built on the cluster. Submitting this against an older build will fail at input parse on use_closure_creep, which is the intended failure mode.
#
# These decks extend or alter the paper protocol. They are NOT scoreable against
# Table 2 and carry no nRMSE -- see Docs/Memory/RUN_LIST_108_SERIES.md.
# =============================================================================

#SBATCH --job-name=series_108_wave2
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-5
#SBATCH --output=series_108_wave2_%A_%a.out
#SBATCH --error=series_108_wave2_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/YeGhasemmi2018

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    case_dir=SWT1
    stem=108_11_swt1_creeptc1e5
    ;;
  1)
    case_dir=SWT2
    stem=108_12_swt2_creeptc1e5
    ;;
  2)
    case_dir=SWS3
    stem=108_13_sw3_creeptc1e5
    ;;
  3)
    case_dir=SWS4
    stem=108_14_sw4_creeptc1e5
    ;;
  4)
    case_dir=SWT1
    stem=108_15_swt1_creeptc1e4
    ;;
  5)
    case_dir=SWT1
    stem=108_16_swt1_creeptc1e6
    ;;
  *)
    echo "Unexpected SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}" >&2
    exit 2
    ;;
esac

case_root=${study_root}/${case_dir}/Sweeps
cd "${case_root}"

if [[ ! -f "${stem}.i" ]]; then
  echo "Missing input deck: ${case_root}/${stem}.i" >&2
  exit 3
fi

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

echo "Starting array task ${SLURM_ARRAY_TASK_ID}: ${case_dir}/${stem}.i"

srun --mpi=pmi2 -n 32 "${project_root}/orca-opt" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc_rorqual/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc_rorqual/${stem}_hpc"
