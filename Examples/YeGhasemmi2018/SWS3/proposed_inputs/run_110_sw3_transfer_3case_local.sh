#!/bin/bash

set -euo pipefail

PROJECT_ROOT=/media/geomechanics/Data4TB/projects/orca_4.0
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS3
INPUT_DIR=${CASE_DIR}/proposed_inputs
RUN_DIR=${INPUT_DIR}/paper_revision_20260901_sw3_followup
MPIEXEC=/home/geomechanics/miniforge/envs/moose/bin/mpiexec.hydra
ORCA=${PROJECT_ROOT}/orca-opt

cases=(
  110_01_sw3_floor1nm_g040_ppfix
  110_02_sw3_floor1nm_nodilation_ppfix
  110_03_sw3_floor1nm_nogouge_ppfix
)

mkdir -p "${RUN_DIR}/csv" "${RUN_DIR}/exodus" "${RUN_DIR}/checkpoint" "${RUN_DIR}/logs"
cd "${CASE_DIR}"

pids=()
for case_stem in "${cases[@]}"; do
  "${MPIEXEC}" -n 8 "${ORCA}" -i "proposed_inputs/${case_stem}.i" \
    >"${RUN_DIR}/logs/${case_stem}.out" \
    2>"${RUN_DIR}/logs/${case_stem}.err" &
  pids+=("$!")
done

status=0
for index in "${!pids[@]}"; do
  if ! wait "${pids[$index]}"; then
    status=1
    echo "${cases[$index]} failed; inspect ${RUN_DIR}/logs/${cases[$index]}.err" >&2
  fi
done

exit "${status}"
