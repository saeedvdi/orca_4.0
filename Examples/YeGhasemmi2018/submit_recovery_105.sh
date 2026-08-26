#!/bin/bash
# =============================================================================
# 105-series recovery array -- 10 independent, Table-2-scoreable decks.
#
# Submit every case with one command:
#
#   sbatch submit_recovery_105.sh
#
# There is no array concurrency cap. All ten tasks are eligible to start at once;
# their actual start times are controlled by SLURM and available nodes.
#
# Array map
#   0-2  SW-T1 maximum-closure continuation (70/90/110 um)
#   3-5  SW-S4 weakening-path bracket (D_c, floor, both)
#   6-7  SW-S4 calibrated MC, without/with rate-and-state
#   8-9  SW-S3 calibrated MC, without/with rate-and-state
# =============================================================================

#SBATCH --job-name=recovery_105
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-9
#SBATCH --output=recovery_105_%A_%a.out
#SBATCH --error=recovery_105_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/YeGhasemmi2018

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    case_dir=SWT1
    stem=105_01_swt1_vm70um_ppfix
    ;;
  1)
    case_dir=SWT1
    stem=105_02_swt1_vm90um_ppfix
    ;;
  2)
    case_dir=SWT1
    stem=105_03_swt1_vm110um_ppfix
    ;;
  3)
    case_dir=SWS4
    stem=105_04_sw4_dc4p5em5_ppfix
    ;;
  4)
    case_dir=SWS4
    stem=105_05_sw4_swfloor3p15_ppfix
    ;;
  5)
    case_dir=SWS4
    stem=105_06_sw4_dc4p5em5_swfloor3p15_ppfix
    ;;
  6)
    case_dir=SWS4
    stem=105_07_sw4_mc_calib_ppfix
    ;;
  7)
    case_dir=SWS4
    stem=105_08_sw4_mc_calib_rsf_ppfix
    ;;
  8)
    case_dir=SWS3
    stem=105_09_sw3_mc_calib_ppfix
    ;;
  9)
    case_dir=SWS3
    stem=105_10_sw3_mc_calib_rsf_ppfix
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
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

echo "Starting array task ${SLURM_ARRAY_TASK_ID}: ${case_dir}/${stem}.i"
echo "SLURM job ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}; 32 ranks, 32G, 24 h"

srun --mpi=pmi2 -n 32 "${project_root}/orca-opt" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc_rorqual/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc_rorqual/${stem}_hpc"
