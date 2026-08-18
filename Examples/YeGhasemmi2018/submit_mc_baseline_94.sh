#!/bin/bash
# ============================================================================
# The 94-series Mohr-Coulomb baseline -- mesh 5.
#
# These decks were built and --check-input validated on 2026-08-18 (see
# MC_BASELINE_94_SERIES.md) but NEVER SUBMITTED: there is not a single 94_* CSV
# anywhere in the repo. The paper's discussion-1 claim (BBFast outperforms
# Mohr-Coulomb) currently has no data behind it at all. This is the batch that
# produces it.
#
# Each 94 deck is its 93 sibling with ONE block replaced -- [czm_contact] --
# and the MC envelope is a tangent-match transfer of the already-calibrated
# Barton-Bandis envelope, not a fresh fit. So a 93/94 pair differs in
# constitutive FORM rather than in fitted strength, and the comparison is fair.
#
# WHAT THE PAIR DOES AND DOES NOT TEST. It tests the shear envelope: log-curved
# Barton-Bandis vs a straight Coulomb line through the onset tangent, the
# W = exp(-(s/Dc)^m) weakening path vs linear-in-Rbar, and one characteristic
# distance instead of two. It does NOT test the normal-closure law: the MC decks
# carry use_hyperbolic_normal_closure = true with the SAME K_ni, V_m, exponent
# 3.28 and offset as their BBFast siblings, deliberately, so the pair isolates
# shear. Any claim about nonlinear CLOSURE needs a different deck.
#
# BEFORE BELIEVING THE NUMBERS, check the three build-error red flags from
# MC_BASELINE_94_SERIES.md sec 6:
#   1. slip onset must land on the SAME injection stage as the BBFast sibling
#      (the peak envelopes agree to 0.09 MPa, so it should);
#   2. Q at stages 1-5, before any slip, must agree to better than 1 %;
#   3. sigma'_n and tau must agree at stage 1 (nothing has yielded yet).
# Any of those failing means the block swap leaked something.
#
# 4 jobs, 32 ranks / 32 G / 24 h. The mesh-3 siblings (94_02/04/06/08) are NOT
# submitted here -- the mesh-3 convergence set is a separate, longer campaign.
# ============================================================================
set -u
cd "$(dirname "$0")"

JOBS=(
  SWT1/94_01_swt1_mc_final_hpc_nochk.sh
  SWT2/94_03_swt2_mc_final_hpc_nochk.sh
  SWS3/94_05_sw3_mc_final_hpc_nochk.sh
  SWS4/94_07_sw4_mc_final_hpc_nochk.sh
)

echo "MC baseline batch: ${#JOBS[@]} decks (mesh 5)"
for s in "${JOBS[@]}"; do
  if [ ! -f "$s" ]; then
    echo "MISSING: $s" >&2
    continue
  fi
  echo "sbatch $s"
  sbatch "$s"
done
