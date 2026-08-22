#!/bin/bash
# ==========================================================================
# 104-series follow-up batch -- 5 decks, 32 ranks / 32 G each.
#
# Opened by the 101 analysis (doc/DISCUSSION_101_RESULTS.md).  Design and the
# full derivation are in the docstring of scripts/build_104_decks.py.
#
# NONE of these is scoreable against Table 2.  Every one replaces the paper's
# monotonic injection history, and 104_01..03 additionally change a calibrated
# parameter on purpose.  Do not run scripts/table2_gate.py on them.
#
# Read them with:   python scripts/analyze_104.py
# which recomputes each 101 mirror through the same code path, so the pairs
# are compared by identical arithmetic rather than against a quoted number.
#
# Total ~35 h of 32-rank time.  Tier 1 is the one that answers a question the
# manuscript currently states without support; tier 2 removes a caveat.
# ==========================================================================
set -u
cd "$(dirname "$0")"

JOBS=(
  # --- TIER 1 -- why does SW-S4 close when the other three prop open?
  # 3.4 h, 3.4 h, 6.8 h.  104_03 is the sign control and is NOT optional:
  # without it a successful 104_01 cannot be distinguished from a knob that
  # happens to move SW-S4 for an unrelated reason.
  SWS4/104_01_sw4_shutin_nogouge_hpc_nochk.sh
  SWS4/104_02_sw4_shutin_dscale0p038_hpc_nochk.sh
  SWS3/104_03_sw3_shutin_nogouge_hpc_nochk.sh
  # --- TIER 2 -- finish the rate-independence test on the missing two.
  # 10.4 h, 10.7 h.  101 group D covered SW-T1 and SW-S4 only.
  SWT2/104_04_swt2_shutin_slowtau_hpc_nochk.sh
  SWS3/104_05_sw3_shutin_slowtau_hpc_nochk.sh
)

for job in "${JOBS[@]}"; do
  if [[ ! -f "$job" ]]; then
    echo "MISSING: $job -- run scripts/build_104_decks.py first" >&2
    exit 1
  fi
done

for job in "${JOBS[@]}"; do
  echo "sbatch $job"
  ( cd "$(dirname "$job")" && sbatch "$(basename "$job")" )
done
