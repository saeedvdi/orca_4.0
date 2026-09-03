#!/bin/bash

set -euo pipefail

sbatch "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1/proposed_inputs/115_01_swt1_extended_depressurization_ppfix.sh"
sbatch "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT2/proposed_inputs/115_02_swt2_extended_depressurization_ppfix.sh"
sbatch "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3/proposed_inputs/115_03_sws3_extended_depressurization_ppfix.sh"
