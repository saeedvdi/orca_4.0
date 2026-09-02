#!/bin/bash

set -euo pipefail

PROJECT_ROOT=/media/geomechanics/Data4TB/projects/orca_4.0
MPIEXEC=/home/geomechanics/miniforge/envs/moose/bin/mpiexec.hydra
ORCA=${PROJECT_ROOT}/orca-opt
RUN_REL=proposed_inputs/paper_compelling_20260902

cases=(
  "SWS3:113_06_sw3_closure144_ppfix"
  "SWT2:114_01_swt2_ascale01416_ppfix"
  "SWT2:114_02_swt2_ascale02124_ppfix"
)

pids=()
labels=()
for entry in "${cases[@]}"; do
  specimen=${entry%%:*}
  case_stem=${entry#*:}
  case_dir=${PROJECT_ROOT}/Examples/YeGhasemmi2018/${specimen}
  mkdir -p "${case_dir}/${RUN_REL}/csv" "${case_dir}/${RUN_REL}/exodus" "${case_dir}/${RUN_REL}/logs"
  (
    cd "${case_dir}"
    "${MPIEXEC}" -n 8 "${ORCA}" -i "proposed_inputs/${case_stem}.i" \
      Outputs/chk/enable=false \
      >"${RUN_REL}/logs/${case_stem}.out" \
      2>"${RUN_REL}/logs/${case_stem}.err"
  ) &
  pids+=("$!")
  labels+=("${specimen}/${case_stem}")
done

status=0
for index in "${!pids[@]}"; do
  if ! wait "${pids[$index]}"; then
    status=1
    echo "${labels[$index]} failed; inspect its log." >&2
  fi
done

exit "${status}"
