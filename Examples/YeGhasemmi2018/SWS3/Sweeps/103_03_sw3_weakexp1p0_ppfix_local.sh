#!/bin/bash
# Local run: 8 ranks.  The workstation ceiling is 24 ranks TOTAL across all
# concurrent jobs -- past that the wall time doubles rather than improving.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results_csv_local results_exodus_local logs

mpiexec -n 8 ../../../orca-opt -i 103_03_sw3_weakexp1p0_ppfix.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_local/103_03_sw3_weakexp1p0_ppfix_local \
    exodus_file_base=results_exodus_local/103_03_sw3_weakexp1p0_ppfix_local \
    2>&1 | tee logs/103_03_sw3_weakexp1p0_ppfix_local.log
