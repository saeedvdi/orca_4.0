#!/bin/bash

set -euo pipefail

PROJECT_ROOT=/media/geomechanics/Data4TB/projects/orca_4.0
MPIEXEC=/home/geomechanics/miniforge/envs/moose/bin/mpiexec.hydra
ORCA=${PROJECT_ROOT}/orca-opt
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS3
RUN_REL=proposed_inputs/paper_compelling_20260902

cases=(
  113_01_sw3_dscale0304_ppfix
  113_02_sw3_dscale0456_ppfix
)

mkdir -p "${CASE_DIR}/${RUN_REL}/csv" "${CASE_DIR}/${RUN_REL}/exodus" "${CASE_DIR}/${RUN_REL}/logs"

pids=()
for case_stem in "${cases[@]}"; do
  (
    cd "${CASE_DIR}"
    "${MPIEXEC}" -n 8 "${ORCA}" -i "proposed_inputs/${case_stem}.i" \
      Outputs/chk/enable=false \
      >"${RUN_REL}/logs/${case_stem}.out" \
      2>"${RUN_REL}/logs/${case_stem}.err"
  ) &
  pids+=("$!")
done

status=0
for index in "${!pids[@]}"; do
  if ! wait "${pids[$index]}"; then
    status=1
    echo "${cases[$index]} failed; inspect its log." >&2
  fi
done

exit "${status}"
