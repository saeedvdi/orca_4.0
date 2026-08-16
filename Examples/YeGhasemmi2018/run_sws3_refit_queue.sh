#!/bin/bash
# =============================================================================
# run_sws3_refit_queue.sh -- launch the SW-S3 alpha=0.6 onset-refit bracket
#
# 86_01 (phi_r = 8.45) is launched by hand; this script waits for capacity and
# then starts 86_02 (phi_r = 9.00), so the bracket completes without anyone
# having to watch the machine drain.
#
# WHY A BRACKET.  The required strength increase was sized from the rate at
# which the alpha=0.6 run closes its strength margin (-0.00150 MPa/s over the
# 330 s before onset), which gives ~0.58 MPa and so delta phi_r ~ 0.95 deg. But
# that margin is a SIDE AVERAGE over the whole fracture while yield begins
# locally, so it is a magnitude, not a prediction. Two points let the answer be
# interpolated instead of guessed.
#
# SCHEDULING.  8 ranks per deck. Waits until the machine has 8 free cores before
# launching, so it is safe to start while the Biot A/B campaign is still
# draining -- it idles rather than oversubscribing.
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
  "SWS3|86_02_sw3_bbfast_biot0p6_phir9p00_m0_kernel_SV"
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
