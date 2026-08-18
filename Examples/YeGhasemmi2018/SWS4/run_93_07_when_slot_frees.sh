#!/bin/bash
# Launch the 93_07 CONTROL as soon as one of the three 95-series jobs finishes, so the
# machine never exceeds the 24-rank local ceiling.
#
# Why this run is needed: 93_07 has never been executed. The scored SW-S4 final is 90_08,
# whose CSV predates the 92-series channel fixes and carries neither
# reported_czm_shear_slip_mm_pp nor flow_rate_mesh_geometry_ml_min_pp. Scoring the
# 95-series against 90_08 would confound the rate law with a change of channel definition.
# 93_07 is the like-for-like control, and it is also the run that makes task #13
# (mesh-independent Q) scoreable for SW-S4.
cd /media/geomechanics/Data4TB/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4
MPI=/home/geomechanics/miniforge/envs/moose/bin/mpiexec
S=93_07_sw4_final_theta30_jrc5_ppfix
WATCH="1427582 1427583 1427584"

while true; do
  alive=0
  for p in $WATCH; do [ -d /proc/$p ] && alive=$((alive+1)); done
  [ $alive -lt 3 ] && break
  sleep 120
done

nohup $MPI -n 8 /media/geomechanics/Data4TB/projects/orca_4.0/orca-opt -i $S.i \
  Outputs/chk/enable=false \
  csv_file_base=results_csv_local/$S \
  exodus_file_base=results_exodus_local/$S \
  > logs_local/$S.log 2>&1
