#!/bin/bash
# =============================================================================
# 108-series, 108 wave1 -- 10 decks.
#
#   sbatch submit_108_wave1.sh
#
# Controls plus arms A and B. Every parameter these use exists in the current build -- no rebuild required.
#
# These decks extend or alter the paper protocol. They are NOT scoreable against
# Table 2 and carry no nRMSE -- see Docs/Memory/RUN_LIST_108_SERIES.md.
# =============================================================================

#SBATCH --job-name=series_108_wave1
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-9
#SBATCH --output=series_108_wave1_%A_%a.out
#SBATCH --error=series_108_wave1_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/YeGhasemmi2018

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    case_dir=SWT1
    stem=108_01_swt1_ctrl_hold1e6
    ;;
  1)
    case_dir=SWS4
    stem=108_02_sw4_ctrl_hold1e6
    ;;
  2)
    case_dir=SWT1
    stem=108_03_swt1_reconf3p5x
    ;;
  3)
    case_dir=SWT2
    stem=108_04_swt2_reconf3p5x
    ;;
  4)
    case_dir=SWS3
    stem=108_05_sw3_reconf3p5x
    ;;
  5)
    case_dir=SWS4
    stem=108_06_sw4_reconf3p5x
    ;;
  6)
    case_dir=SWT1
    stem=108_07_swt1_unldtau150
    ;;
  7)
    case_dir=SWT1
    stem=108_08_swt1_unldtau1500
    ;;
  8)
    case_dir=SWT1
    stem=108_09_swt1_unldtau15000
    ;;
  9)
    case_dir=SWT2
    stem=108_10_swt2_unldtau1500
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
