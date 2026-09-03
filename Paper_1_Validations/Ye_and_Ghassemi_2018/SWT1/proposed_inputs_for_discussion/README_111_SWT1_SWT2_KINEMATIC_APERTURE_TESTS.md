# SW-T1 and SW-T2 111-series kinematic-aperture tests

Selected parents:

- SW-T1: `107_01_swt1_coh27p2_apscale0p01512_ppfix.i`
- SW-T2: `100_04_swt2_apscale0p0177_ppfix.i`

The saw-cut SW-S3/SW-S4 ablations cannot be copied literally to these tensile cases. SW-T1 and SW-T2 already use `dilation_scale=0`, `use_slip_damage=false`, and `use_kinematic_aperture=true`. Their retained hydraulic response is carried by the mechanically persistent gap through `aperture_scale`. Therefore, setting hydraulic dilation or gouge loss to zero again would produce duplicate controls.

The active-mechanism tests are:

| Deck | Controlled changes | Scientific question |
|---|---|---|
| `111_01_swt1_floor1nm_control_ppfix.i` | lower bound reduced to 0.001 µm | Is the calibrated SW-T1 response floor-independent? |
| `111_02_swt1_floor1nm_nokinematic_ppfix.i` | relaxed bound; `aperture_scale=0` | How much SW-T1 retention is carried by mapped persistent geometric opening? |
| `111_03_swt2_floor1nm_control_ppfix.i` | lower bound reduced to 0.001 µm | Is the calibrated SW-T2 response floor-independent? |
| `111_04_swt2_floor1nm_nokinematic_ppfix.i` | relaxed bound; `aperture_scale=0` | How much SW-T2 retention is carried by mapped persistent geometric opening? |

Mechanical dilatancy remains active in every case. The no-kinematic runs remove only the hydraulic-aperture mapping, so their mechanical histories should remain close to the parent apart from coupled pressure feedback.

Each input has a matching eight-task SLURM launcher following the format used in `SWS4/proposed_inputs`. The outputs are isolated beneath `proposed_inputs/paper_revision_20260901_tensile_followup/` in the corresponding specimen directory.

Run no more than three cases concurrently. Score completed CSV files with `scripts/table2_gate.py` and report actual peak and final values before nRMSE.
