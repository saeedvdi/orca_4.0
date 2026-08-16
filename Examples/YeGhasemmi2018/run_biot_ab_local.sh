#!/bin/bash
# =============================================================================
# run_biot_ab_local.sh -- Biot A/B campaign, LOCAL, generated 2026-08-15
#
# Six full-length decks: three samples x two configurations.
#
#     baseline   biot_coefficient = 1e-12   (as-calibrated, unphysical: alpha < phi)
#     fixed      biot_coefficient = 0.6     (physical, aligned with SW-S4)
#
# Both members of a pair are otherwise identical -- same kernel_SV mass balance,
# same confining_pressure = 30e6, same mesh, same end_time -- so the only thing
# separating them is alpha. That is what makes the comparison mean anything;
# running only the fixed member would show that it ran, not that it is better.
#
# SCHEDULING
#   8 MPI ranks per deck, at most 4 decks at once = 32 ranks = the whole box.
#   Before each launch the script waits until the machine has 8 free cores, so
#   it is safe to start while other jobs are still finishing -- it will simply
#   sit idle until they drain rather than oversubscribing them.
#   Pairs are launched together so both members see identical machine load.
#
# USAGE
#   ./run_biot_ab_local.sh            run the campaign (stays in foreground;
#                                     launch it with nohup/setsid to detach)
#   ./run_biot_ab_local.sh --dry      print the plan and exit
#   ./run_biot_ab_local.sh --status   report progress of an in-flight campaign
# =============================================================================
set -u

ROOT=/media/geomechanics/Data4TB/projects/orca_4.0
EX=$ROOT/Examples/YeGhasemmi2018
BIN=$ROOT/orca-opt
NP=8            # MPI ranks per deck
MAXJOBS=4       # concurrent decks
CORES=32        # physical cores on this machine
TAG=biot_ab_20260815
POLL=60         # seconds between capacity checks

# sample | deck basename
DECKS=(
  "SWS3|84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV"
  "SWS3|84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6"
  "SWT1|Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV"
  "SWT1|Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV_biot0p6"
  "SWT2|Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV"
  "SWT2|Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot0p6"
)

log() { echo "[$(date '+%F %T')] $*"; }

# Ranks currently running anywhere on the machine, ours and anyone else's.
# Matches the executable name exactly, so wrapper shells are not counted.
machine_ranks() { pgrep -x orca-opt 2>/dev/null | wc -l; }

status_report() {
  printf '%-56s %-10s %-22s %s\n' DECK STATE "LAST STEP" EXC
  for entry in "${DECKS[@]}"; do
    s=${entry%%|*}; d=${entry#*|}
    L=$EX/$s/logs/${d}_${TAG}.log
    if [ ! -f "$L" ]; then
      printf '%-56s %-10s %-22s %s\n' "${d:0:56}" queued - -
      continue
    fi
    last=$(grep -E '^Time Step' "$L" | tail -1 | sed 's/Time Step //;s/, dt.*//')
    exc=$(grep -c 'Solve Did NOT Converge\|MOOSE Exception' "$L")
    if grep -q 'Finished Executing' "$L"; then st=done
    elif grep -qE '\*\*\* ERROR|Segmentation|EXIT STRING' "$L"; then st=FAILED
    elif [ -n "$(pgrep -f -- "-i ${d}.i" 2>/dev/null)" ]; then st=running
    else st=stopped; fi
    printf '%-56s %-10s %-22s %s\n' "${d:0:56}" "$st" "${last:--}" "$exc"
  done
}

case "${1:-}" in
  --status) status_report; exit 0 ;;
  --dry)
    echo "plan: ${#DECKS[@]} decks, $NP ranks each, $MAXJOBS at a time"
    echo "machine currently running $(machine_ranks) orca-opt ranks of $CORES cores"
    i=0
    for entry in "${DECKS[@]}"; do
      i=$((i+1)); s=${entry%%|*}; d=${entry#*|}
      [ -f "$EX/$s/$d.i" ] && ok="ok     " || ok="MISSING"
      echo "  $i. $ok $s/$d.i"
    done
    exit 0 ;;
esac

# The moose env's activate.d hook reads CONDA_BUILD unguarded, so it trips
# 'set -u'. Relax it just across activation.
set +u
source /home/geomechanics/miniforge/etc/profile.d/conda.sh
conda activate moose
set -u

PIDS=()

# Block until fewer than MAXJOBS of ours are alive AND the machine has room.
wait_for_slot() {
  while :; do
    alive=0
    for p in "${PIDS[@]:-}"; do
      [ -n "$p" ] && kill -0 "$p" 2>/dev/null && alive=$((alive+1))
    done
    busy=$(machine_ranks)
    if [ "$alive" -lt "$MAXJOBS" ] && [ $((busy + NP)) -le "$CORES" ]; then
      return 0
    fi
    log "waiting: $alive/$MAXJOBS of mine running, $busy/$CORES ranks busy machine-wide"
    sleep "$POLL"
  done
}

log "campaign $TAG starting: ${#DECKS[@]} decks, $NP ranks each, max $MAXJOBS concurrent"
log "machine currently running $(machine_ranks) orca-opt ranks"

for entry in "${DECKS[@]}"; do
  sample=${entry%%|*}; deck=${entry#*|}
  if [ ! -f "$EX/$sample/$deck.i" ]; then
    log "MISSING $sample/$deck.i -- skipped"
    continue
  fi
  wait_for_slot
  cd "$EX/$sample" || { log "cannot cd $EX/$sample"; continue; }
  mkdir -p logs results_csv results_exodus results_checkpoint
  nohup mpiexec -n "$NP" "$BIN" -i "$deck.i" \
      exodus_file_base=results_exodus/${deck}_${TAG} \
      csv_file_base=results_csv/${deck}_${TAG} \
      checkpoint_file_base=results_checkpoint/${deck}_${TAG} \
      > "logs/${deck}_${TAG}.log" 2>&1 &
  pid=$!
  PIDS+=("$pid")
  log "launched $sample/$deck  pid=$pid  log=$sample/logs/${deck}_${TAG}.log"
  sleep 10   # let MPI settle before the next capacity read
done

log "all ${#PIDS[@]} decks launched; waiting for completion"
wait
log "campaign $TAG complete"
status_report
