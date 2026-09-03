#!/bin/bash

# Submit with:
#   sbatch submit_all_remaining_hpc.sh
#
# Twelve SWT1, SWT2, and SWS3 cases are indexed below.  SWS4 is excluded because
# it is being run locally.  The %3 suffix limits the array to three simultaneous
# jobs; the remaining tasks stay queued on the cluster.

#SBATCH --job-name=orca_t1_t2_s3
#SBATCH --account=def-biaoli66
#SBATCH --time=18:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=24G
#SBATCH --array=0-11%3
#SBATCH --output=slurm_orca_t1_t2_s3_%A_%a.out
#SBATCH --error=slurm_orca_t1_t2_s3_%A_%a.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
ORCA=${PROJECT_ROOT}/orca-opt
PACKAGE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

# 112_02 and 112_03 are omitted because their local calculations reached the
# configured end time.  All SWS4 cases, including 112_04 and 115_04, are omitted
# from this HPC array.  The locally interrupted non-SWS4 cases restart cleanly
# on HPC.
cases=(
  "SWT1:112_01_swt1_dt0375_ppfix"
  "SWS3:113_01_sw3_dscale0304_ppfix"
  "SWS3:113_02_sw3_dscale0456_ppfix"
  "SWS3:113_03_sw3_gouge032_ppfix"
  "SWS3:113_04_sw3_gouge048_ppfix"
  "SWS3:113_05_sw3_closure096_ppfix"
  "SWS3:113_06_sw3_closure144_ppfix"
  "SWT2:114_01_swt2_ascale01416_ppfix"
  "SWT2:114_02_swt2_ascale02124_ppfix"
  "SWT1:115_01_swt1_extended_depressurization_ppfix"
  "SWT2:115_02_swt2_extended_depressurization_ppfix"
  "SWS3:115_03_sws3_extended_depressurization_ppfix"
)

if [[ -z "${SLURM_ARRAY_TASK_ID:-}" ]]; then
  echo "This is a Slurm array script. Submit it with: sbatch $0" >&2
  exit 2
fi

entry=${cases[${SLURM_ARRAY_TASK_ID}]}
specimen=${entry%%:*}
case_stem=${entry#*:}
case_dir=${PROJECT_ROOT}/Examples/YeGhasemmi2018/${specimen}
input_file=${case_dir}/proposed_inputs/${case_stem}.i
packaged_input=${PACKAGE_DIR}/${specimen}/${case_stem}.i

if [[ ! -x "${ORCA}" ]]; then
  echo "ORCA executable is missing or not executable: ${ORCA}" >&2
  exit 3
fi

if [[ -f "${packaged_input}" ]]; then
  # Keep the live project deck synchronized with the submitted package.  The
  # input must run from the specimen directory so its relative mesh path works.
  cp "${packaged_input}" "${input_file}"
elif [[ ! -f "${input_file}" ]]; then
  echo "Input is absent from both the package and live project:" >&2
  echo "  ${packaged_input}" >&2
  echo "  ${input_file}" >&2
  exit 4
fi

cd "${case_dir}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p proposed_inputs/paper_compelling_20260902/{csv,exodus,checkpoint,logs}

echo "Starting ${case_stem} for ${specimen} as array task ${SLURM_ARRAY_TASK_ID}."
srun --mpi=pmi2 -n 8 "${ORCA}" -i "proposed_inputs/${case_stem}.i" \
  Outputs/chk/enable=false
echo "Completed ${case_stem}."
