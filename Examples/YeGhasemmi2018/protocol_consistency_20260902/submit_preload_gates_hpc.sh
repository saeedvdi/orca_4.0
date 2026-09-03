#!/bin/bash

#SBATCH --job-name=orca_gate_116
#SBATCH --account=def-biaoli66
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=12G
#SBATCH --array=0-7%3
#SBATCH --output=slurm_gate_116_%A_%a.out
#SBATCH --error=slurm_gate_116_%A_%a.err

set -euo pipefail

PROJECT_ROOT=${ORCA_PROJECT_ROOT:-/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0}
ORCA=${PROJECT_ROOT}/orca-opt
PACKAGE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

cases=(
  "SWT1:116_01_swt1_bb_commonK796_protocol_ppfix"
  "SWT1:116_02_swt1_mc_commonK796_protocol_ppfix"
  "SWT2:116_03_swt2_bb_theta31_commonK796_protocol_ppfix"
  "SWT2:116_04_swt2_mc_theta31_commonK796_protocol_ppfix"
  "SWS3:116_05_sws3_bb_fixedpiston_commonK796_protocol_ppfix"
  "SWS3:116_06_sws3_mc_fixedpiston_commonK796_protocol_ppfix"
  "SWS4:116_07_sws4_bb_jrc1p19_fixedpiston_commonK796_ppfix"
  "SWS4:116_08_sws4_mc_fixedpiston_commonK796_protocol_ppfix"
)

if [[ -z "${SLURM_ARRAY_TASK_ID:-}" ]]; then
  echo "Submit this Slurm array with: sbatch $0" >&2
  exit 2
fi

entry=${cases[${SLURM_ARRAY_TASK_ID}]}
specimen=${entry%%:*}
stem=${entry#*:}
case_dir=${PROJECT_ROOT}/Examples/YeGhasemmi2018/${specimen}
input_file=${PACKAGE_DIR}/${specimen}/${stem}.i
installed_input=${case_dir}/proposed_inputs/${stem}.i
gate_base=proposed_inputs/protocol_consistency_20260902/gates/${stem}_gate

cd "${case_dir}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p proposed_inputs/protocol_consistency_20260902/{gates,logs}
cp "${input_file}" "${installed_input}"

echo "Running preload gate for ${stem}."
srun --mpi=pmi2 -n 8 "${ORCA}" -i "${installed_input}" \
  Executioner/end_time=70 \
  Outputs/exodus/enable=false \
  Outputs/chk/enable=false \
  "csv_file_base=${gate_base}"
