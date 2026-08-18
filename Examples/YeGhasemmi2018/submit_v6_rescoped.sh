#!/bin/bash
# ============================================================================
# v6 HPC batch, RE-SCOPED after the SW-S4 rate-law result of 2026-08-18.
#
# The original plan was 24 decks (16 rate-and-state + 8 poroelastic). The SW-S4
# arm was run locally first and falsified the hypothesis the b-bracket existed
# to test: the entire b bracket moved stage-4 d_s by 0.0005 mm against a
# 0.013 mm deficit, while degrading stage 5 monotonically. See
# V6_RATE_STATE_AND_POROELASTIC_PROBES.md section 6.
#
# This script submits the 11 decks that are still worth cluster time.
#
#   KEPT (3 rate-law): the level-matched b = 0 controls for the three specimens
#   NOT yet run. These test whether the tau-inflation finding is SW-S4-specific.
#   SW-T1/T2/S3 have fitted viscosities 8-20x BELOW the laboratory range, where
#   SW-S4's was already inside it -- so the same substitution may move them the
#   other way. One deck each answers it.
#
#   KEPT (8 poroelastic): the entire 96 series. It probes biot_coefficient and
#   fault_pressure_coefficient and is completely independent of the rate law;
#   nothing in the SW-S4 result touches it.
#
#   DROPPED (13): the nine b > 0 decks for SW-T1/T2/S3, plus 95_15, plus the
#   three SW-S4 decks already run locally. Rationale below.
# ============================================================================
set -u
cd "$(dirname "$0")"

KEEP=(
  # --- level-matched b = 0 controls: rate-law FORM only ------------------
  SWT1/95_01_swt1_rsf_aeq_b0_hpc_nochk.sh      # implied a = 5.067e-4
  SWT2/95_05_swt2_rsf_aeq_b0_hpc_nochk.sh      # implied a = 4.985e-4
  SWS3/95_09_sw3_rsf_aeq_b0_hpc_nochk.sh       # implied a = 1.232e-3
  # --- 96 series: poroelastic consistency, untouched by the v6 result ----
  SWT1/96_01_swt1_biot0p2_hpc_nochk.sh
  SWT2/96_02_swt2_biot0p2_hpc_nochk.sh
  SWS3/96_03_sw3_biot0p2_hpc_nochk.sh
  SWS3/96_04_sw3_fpc1p0_hpc_nochk.sh
  SWS3/96_05_sw3_biot0p2_fpc1p0_hpc_nochk.sh
  SWS4/96_06_sw4_biot0p2_hpc_nochk.sh
  SWS4/96_07_sw4_fpc1p0_hpc_nochk.sh
  SWS4/96_08_sw4_biot0p2_fpc1p0_hpc_nochk.sh
)

# ----------------------------------------------------------------------------
# DEFERRED, and why. Do not resurrect without a reason that answers these.
#
#   SWT1/95_02,95_03,95_04    b bracket, SW-T1
#   SWT2/95_06,95_07,95_08    b bracket, SW-T2
#   SWS3/95_10,95_11,95_12    b bracket, SW-S3
#       The b bracket was run to exhaustion on SW-S4, the specimen with by far
#       the best case for it (the only staircase that never fitted, and the only
#       fitted viscosity already in the physical range). It came back flat where
#       the hypothesis needed movement. Nine more jobs to re-establish that on
#       three specimens with weaker priors is not justified.
#
#   SWS4/95_15                a = b = 0.010, velocity neutral.
#       Bracketed on both sides by 95_14 (a-b = +0.005) and 95_16
#       (a-b = -0.005), both of which are already known. No new information.
#
#   SWS4/95_13,95_14,95_16    already run locally on mesh 5; 95_16 stalled at
#       t = 1554.9 and was killed. Re-running on HPC would only re-derive a
#       finished result -- except that 95_16 is now a deterministic reproducer
#       for the slip-arrest non-convergence and is worth keeping ON PURPOSE for
#       that debugging task, not for scoring.
# ----------------------------------------------------------------------------

echo "v6 re-scoped batch: ${#KEEP[@]} decks (13 of the original 24 deferred)"
for s in "${KEEP[@]}"; do
  if [ ! -f "$s" ]; then
    echo "MISSING: $s" >&2
    continue
  fi
  echo "sbatch $s"
  sbatch "$s"
done
