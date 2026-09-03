#!/bin/bash

set -euo pipefail

sbatch "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs/112_04_sw4_mesh3_ppfix.sh"
sbatch "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3/proposed_inputs/113_01_sw3_dscale0304_ppfix.sh"
sbatch "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3/proposed_inputs/113_02_sw3_dscale0456_ppfix.sh"
