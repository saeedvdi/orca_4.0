#!/bin/bash
# ==========================================================================
# 105-series recovery batch -- 10 decks.
#
# A  105_01..03  SW-T1 maximum-closure continuation (BBFast).
#                The 45.91/50/55 um bracket improves every channel
#                monotonically and has not turned; 70/90/110 closes it.
# B  105_04..06  SW-S4 weakening-path bracket (BBFast).  Onset knob,
#                floor knob, and both.  The 99-series exponent and
#                viscosity probes both LOST accuracy; those were the
#                wrong knobs.
# C  105_07..10  Calibrated Mohr-Coulomb upper bound (MC), SW-S4 and
#                SW-S3, with and without rate-and-state, ported from the
#                orca_3.0_full archive onto the corrected meshes and the
#                ppfix frame.
#
# All ten keep the paper injection schedule and ARE scoreable against
# Table 2 with scripts/table2_gate.py.
# ==========================================================================
set -u
cd "$(dirname "${BASH_SOURCE[0]}")"

JOBS=(
  SWT1/105_01_swt1_vm70um_ppfix_hpc_nochk.sh
  SWT1/105_02_swt1_vm90um_ppfix_hpc_nochk.sh
  SWT1/105_03_swt1_vm110um_ppfix_hpc_nochk.sh
  SWS4/105_04_sw4_dc4p5em5_ppfix_hpc_nochk.sh
  SWS4/105_05_sw4_swfloor3p15_ppfix_hpc_nochk.sh
  SWS4/105_06_sw4_dc4p5em5_swfloor3p15_ppfix_hpc_nochk.sh
  SWS4/105_07_sw4_mc_calib_ppfix_hpc_nochk.sh
  SWS4/105_08_sw4_mc_calib_rsf_ppfix_hpc_nochk.sh
  SWS3/105_09_sw3_mc_calib_ppfix_hpc_nochk.sh
  SWS3/105_10_sw3_mc_calib_rsf_ppfix_hpc_nochk.sh
)
echo "105 recovery batch: ${#JOBS[@]} decks"
for s in "${JOBS[@]}"; do
  [ -f "$s" ] || { echo "MISSING: $s" >&2; continue; }
  echo "sbatch $s"; sbatch "$s"
done
