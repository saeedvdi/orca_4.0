#!/bin/bash
# =============================================================================
# run_injfix_queue.sh -- launch the SW-T1 / SW-T2 injection-schedule refit pair
#
# WHY.  The SW-T decks carried a hand-built idealised injection staircase: the
# hold LEVELS were right (5/8/12/16/20/24/28 MPa) but every stage transition was
# late -- +48..+155 s on SW-T1, +53..+77 s on SW-T2 -- and SW-T1's 28 MPa peak
# hold was only 131 s against 255 s measured, i.e. 0.51x. Injection pressure is
# the DRIVER, so that timing error propagates into flow rate, permeability,
# slip onset and the whole unload branch. It has to be fixed before any
# friction or dilation parameter is re-tuned against these curves, otherwise the
# tuning is just absorbing a timing error.
#
# 87_01/87_02 rebuild the schedule from the 2026-08-16 re-extracted validation
# curves, snapping plateau VALUES to nominal and adopting measured TRANSITION
# TIMES only. Whole-record RMSE against the measurement:
#     SW-T1  1.240 -> 0.195 MPa
#     SW-T2  1.536 -> 0.266 MPa
#
# SW-T1 also gets its event_dt_cap window shifted -210 s (1740-1825 -> 1530-1680)
# and widened, because the slip event now arrives with the earlier peak. The
# window is deliberately wider than the shift is precise: a missed dt cap costs a
# failed run, an over-wide one only costs time.
#
# SCHEDULING.  8 ranks per deck, launched only when the machine has 8 free cores,
# so this is safe to start while the SW-S3 phi_r bracket and the SW-T2 Biot A/B
# arm are still draining -- it idles rather than oversubscribing.
#
# MPI NOTE.  Must use the conda `moose` environment's mpiexec (MPICH/Hydra).
# The system /usr/bin/mpiexec is OpenMPI and aborts with
# "Runtime environment uses unsupported PMI version PMIx".
# =============================================================================
set -u

ROOT=/media/geomechanics/Data4TB/projects/orca_4.0
EX=$ROOT/Examples/YeGhasemmi2018
BIN=$ROOT/orca-opt
NP=8
CORES=32
POLL=120

# The moose env's activate.d hook reads $CONDA_BUILD unguarded, which trips
# `set -u`. Relax it just for the activation rather than dropping the flag.
set +u
source /home/geomechanics/miniforge/etc/profile.d/conda.sh
conda activate moose
set -u

QUEUE=(
  "SWT1|87_01_swt1_bbfast_injfix_kernel_SV_biot0p6"
  "SWT2|87_02_swt2_bbfast_injfix_kernel_SV_biot0p6"
)

log() { echo "[$(date +%H:%M:%S)] $*"; }

# Count solver RANKS only. `pgrep -f "$BIN"` also matches each job's mpiexec
# wrapper, which inflated the count by one per job (38 against 32 real ranks) and
# would have kept the queue waiting forever after a slot actually freed.
# `-x` matches the executable name exactly, so it sees ranks and nothing else.
busy_ranks() { pgrep -c -x orca-opt || true; }

for entry in "${QUEUE[@]}"; do
  sample=${entry%%|*}
  deck=${entry#*|}

  while :; do
    used=$(busy_ranks)
    free=$(( CORES - used ))
    if (( free >= NP )); then
      break
    fi
    log "waiting for $NP cores (in use $used of $CORES)"
    sleep "$POLL"
  done

  cd "$EX/$sample" || exit 1
  mkdir -p logs results_csv results_exodus results_checkpoint
  setsid nohup mpiexec -n "$NP" "$BIN" -i "$EX/$sample/$deck.i" \
      > "$EX/$sample/logs/$deck.log" 2>&1 < /dev/null &
  log "launched $sample/$deck  pid=$!"
  sleep 30
done

log "queue drained"
