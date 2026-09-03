#!/bin/bash

#SBATCH --job-name=sws4_r117_full
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=24G
#SBATCH --array=0-5%3
#SBATCH --output=slurm_sws4_r117_full_%A_%a.out
#SBATCH --error=slurm_sws4_r117_full_%A_%a.err

set -euo pipefail

PROJECT_ROOT=${ORCA_PROJECT_ROOT:-/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0}
ORCA=${PROJECT_ROOT}/orca-opt
PACKAGE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4

cases=(
  "117_01_sws4_jrc1p19_m1p60_dc74p5_protocol_ppfix"
  "117_02_sws4_jrc1p19_m1p90_dc74p5_protocol_ppfix"
  "117_03_sws4_jrc1p19_m2p20_dc74p5_protocol_ppfix"
  "117_04_sws4_jrc1p19_m1p90_dc60_protocol_ppfix"
  "117_05_sws4_jrc1p19_m1p90_dc90_protocol_ppfix"
  "117_06_sws4_jrc1p19_m1p90_dc105_protocol_ppfix"
)

if [[ -z "${SLURM_ARRAY_TASK_ID:-}" ]]; then
  echo "Submit with sbatch. To run selected cases, override the array, for example:" >&2
  echo "  sbatch --array=1,4%2 $0" >&2
  exit 2
fi

stem=${cases[${SLURM_ARRAY_TASK_ID}]}
source_input=${PACKAGE_DIR}/${stem}.i
installed_input=${CASE_DIR}/proposed_inputs/${stem}.i

if [[ ! -x "${ORCA}" ]]; then
  echo "Orca executable is missing or not executable: ${ORCA}" >&2
  exit 3
fi
if [[ ! -f "${source_input}" ]]; then
  echo "Input file is missing: ${source_input}" >&2
  exit 4
fi

cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p proposed_inputs/sws4_recalibration_wave1_20260902/{csv,exodus,checkpoint,logs}
cp "${source_input}" "${installed_input}"

echo "Full-cycle recalibration: ${stem} (array task ${SLURM_ARRAY_TASK_ID})."
srun --mpi=pmi2 -n 8 "${ORCA}" -i "${installed_input}" Outputs/chk/enable=false
echo "Completed full-cycle recalibration: ${stem}."
