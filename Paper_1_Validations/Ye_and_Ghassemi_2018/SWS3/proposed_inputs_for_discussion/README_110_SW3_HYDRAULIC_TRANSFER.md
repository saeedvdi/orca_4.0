# SW-S3 110-series hydraulic mechanism-transfer decks

Parent deck: `SWS3/Sweeps/100_06_sw3_resc1p30_unld0p00_ppfix.i`

These three calculations transfer the completed SW-S4 mechanism test to the second saw-cut specimen. They use one common relaxed hydraulic-aperture floor and do not recalibrate any remaining parameter.

| Deck | Controlled changes | Scientific question |
|---|---|---|
| `110_01_sw3_floor1nm_g040_ppfix.i` | `min_hydraulic_aperture=1.0e-9` | Is the calibrated SW-S3 response independent of its 1.22 µm floor? |
| `110_02_sw3_floor1nm_nodilation_ppfix.i` | relaxed floor; `dilation_scale=0` | What is the unconstrained SW-S3 response without retained hydraulic dilation? |
| `110_03_sw3_floor1nm_nogouge_ppfix.i` | relaxed floor; `use_slip_damage=false` | How much of the SW-S3 hydraulic response is removed by the calibrated 0.40 µm gouge-loss term? |

Mechanical dilation remains active in all three cases. In `110_02`, only the separate retained-dilation contribution to hydraulic aperture is removed. The calculations are diagnostic counterfactuals; the parent remains the validation case.

## Output location

The decks write unique CSV, Exodus, and checkpoint outputs beneath:

`SWS3/proposed_inputs/paper_revision_20260901_sw3_followup/`

## Local eight-core runs

Run all three concurrently, using eight MPI ranks per case, from any directory:

```bash
bash Examples/YeGhasemmi2018/SWS3/proposed_inputs/run_110_sw3_transfer_3case_local.sh
```

The launcher uses the MPICH executable that matches the local ORCA build. Do not replace it with the system OpenMPI launcher.

## Cluster runs

Each deck has a separate SLURM script requesting eight tasks:

```bash
sbatch proposed_inputs/110_01_sw3_floor1nm_g040_ppfix.sh
sbatch proposed_inputs/110_02_sw3_floor1nm_nodilation_ppfix.sh
sbatch proposed_inputs/110_03_sw3_floor1nm_nogouge_ppfix.sh
```

Submit from the `SWS3` directory. The cluster paths follow the same project layout as the earlier 109-series scripts.

## Required comparison

After completion, score every CSV with `scripts/table2_gate.py --sample SWS3` and compare the 11 ordered stages with the parent. Report actual peak and final permeability, peak enhancement, final retention, flow nRMSE, and changes in the four mechanical channels. Do not choose a new calibrated case from these runs.
