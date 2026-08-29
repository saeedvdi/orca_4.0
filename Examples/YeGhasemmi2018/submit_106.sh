#!/bin/bash
# =============================================================================
# 106-series array -- 15 independent, Table-2-scoreable decks.
#
# Submit every case with one command:
#
#   sbatch submit_106.sh
#
# There is no array concurrency cap. All 15 tasks are eligible to start at once;
# their actual start times are controlled by SLURM and available nodes.
#
# IMPORTANT: tasks 11-14 (decks 106_12-106_15) require an orca_v9 orca-opt.
# The other eleven decks are compatible with earlier builds, but this array is
# intended to run entirely with the orca_v9 executable.
#
# Array map
#   0-3    SWT1  106_01-106_04
#   4-6    SWT2  106_05-106_07
#   7-10   SWS4  106_08-106_11
#   11-12  SWT1  106_12-106_13 (stress-dependent shear stiffness; orca_v9)
#   13-14  SWT2  106_14-106_15 (stress-dependent shear stiffness; orca_v9)
# =============================================================================

#SBATCH --job-name=series_106
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-14
#SBATCH --output=series_106_%A_%a.out
#SBATCH --error=series_106_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/YeGhasemmi2018

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    case_dir=SWT1
    stem=106_01_swt1_apscale0p01512_ppfix
    ;;
  1)
    case_dir=SWT1
    stem=106_02_swt1_hydbb_vh9p84um_ppfix
    ;;
  2)
    case_dir=SWT1
    stem=106_03_swt1_unld0p70_ppfix
    ;;
  3)
    case_dir=SWT1
    stem=106_04_swt1_hydbb_unld0p70_ppfix
    ;;
  4)
    case_dir=SWT2
    stem=106_05_swt2_hydbb_vh34p36um_ppfix
    ;;
  5)
    case_dir=SWT2
    stem=106_06_swt2_unld0p60_ppfix
    ;;
  6)
    case_dir=SWT2
    stem=106_07_swt2_hydbb_unld0p60_ppfix
    ;;
  7)
    case_dir=SWS4
    stem=106_08_sw4_phir21p60_ppfix
    ;;
  8)
    case_dir=SWS4
    stem=106_09_sw4_phir22p10_ppfix
    ;;
  9)
    case_dir=SWS4
    stem=106_10_sw4_hydbb_vh1p83um_ppfix
    ;;
  10)
    case_dir=SWS4
    stem=106_11_sw4_phir21p60_hydbb_ppfix
    ;;
  11)
    case_dir=SWT1
    stem=106_12_swt1_ktbb_kref1p18e12_ppfix
    ;;
  12)
    case_dir=SWT1
    stem=106_13_swt1_ktbb_kref3p0e12_ppfix
    ;;
  13)
    case_dir=SWT2
    stem=106_14_swt2_ktbb_kref6p86e11_ppfix
    ;;
  14)
    case_dir=SWT2
    stem=106_15_swt2_ktbb_kref2p0e12_ppfix
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
echo "SLURM job ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}; 32 ranks, 32G, 24 h"

srun --mpi=pmi2 -n 32 "${project_root}/orca-opt" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc_rorqual/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc_rorqual/${stem}_hpc"
