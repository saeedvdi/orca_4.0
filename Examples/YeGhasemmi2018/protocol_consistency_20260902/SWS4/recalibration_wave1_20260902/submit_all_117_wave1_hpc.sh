#!/bin/bash

# Master submitter for the SW-S4 wave-1 recalibration (117_01 .. 117_06).
#
#   cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS4/recalibration_wave1_20260902
#   ./submit_all_117_wave1_hpc.sh
#
# Submits each case's own script (117_0N_..._hpc.sh) as a separate sbatch job so
# they can be tracked, cancelled, or resubmitted independently. Pass specific
# case IDs to submit a subset, e.g.:
#
#   ./submit_all_117_wave1_hpc.sh 01 04

set -euo pipefail

PACKAGE_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)

declare -a stems=(
  "117_01_sws4_jrc1p19_m1p60_dc74p5_protocol_ppfix"
  "117_02_sws4_jrc1p19_m1p90_dc74p5_protocol_ppfix"
  "117_03_sws4_jrc1p19_m2p20_dc74p5_protocol_ppfix"
  "117_04_sws4_jrc1p19_m1p90_dc60_protocol_ppfix"
  "117_05_sws4_jrc1p19_m1p90_dc90_protocol_ppfix"
  "117_06_sws4_jrc1p19_m1p90_dc105_protocol_ppfix"
)

ids=("$@")

for stem in "${stems[@]}"; do
  case_id=${stem:4:2}
  if [[ ${#ids[@]} -gt 0 ]]; then
    match=0
    for id in "${ids[@]}"; do
      [[ "${id}" == "${case_id}" ]] && match=1
    done
    [[ ${match} -eq 1 ]] || continue
  fi

  script="${PACKAGE_DIR}/${stem}_hpc.sh"
  if [[ ! -f "${script}" ]]; then
    echo "Missing per-case script: ${script}" >&2
    exit 3
  fi

  echo "Submitting ${stem} ..."
  sbatch "${script}"
done
