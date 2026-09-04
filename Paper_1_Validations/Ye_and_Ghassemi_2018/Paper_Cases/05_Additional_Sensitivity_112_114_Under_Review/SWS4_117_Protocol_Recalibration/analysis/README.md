# SW-S4 measured-JRC recalibration: Wave 1

This package is a bounded mechanical recalibration of the completed corrected-protocol case `116_07`. It does not change or rerun the adopted source deck.

All six decks completed `orca-opt --check-input --allow-unused` with `Syntax OK` on 2 September 2026. The inherited `OrcaTHMaterial` deprecation and local ParsedFunction JIT-link warnings do not change that parser result and are not introduced by this sweep.

## Why these parameters are varied

Case `116_07` with measured JRC = 1.19 reaches 0.001 mm slip at 16.06 MPa, compared with 16.09 MPa in the digitized experiment. The initial strength should therefore remain fixed. The problem occurs after initiation: the model reaches 0.075 mm slip at 20 MPa, while the experiment reaches it near 28 MPa.

All six cases retain:

- JRC = 1.19 and JCS = 150 MPa;
- the corrected fixed-piston and constant-confinement protocol;
- the common provisional machine stiffness of 796 kN/mm;
- the peak and tail friction angles;
- tangential viscosity and the complete dilation law;
- all hydraulic aperture, closure, and slip-damage parameters.

Only the weakening exponent `m` and characteristic slip distance `Dc` are changed. An exponent greater than one gives a small initial weakening slope and allows the strength loss to accelerate later. The Table 2 friction path suggests a useful neighborhood near `m = 1.9--2.0`; the matrix brackets this value and its interaction with `Dc`.

## Parameter matrix

| Array ID | Case | m | Dc (um) |
|---:|---|---:|---:|
| 0 | `117_01...m1p60_dc74p5...` | 1.60 | 74.5 |
| 1 | `117_02...m1p90_dc74p5...` | 1.90 | 74.5 |
| 2 | `117_03...m2p20_dc74p5...` | 2.20 | 74.5 |
| 3 | `117_04...m1p90_dc60...` | 1.90 | 60.0 |
| 4 | `117_05...m1p90_dc90...` | 1.90 | 90.0 |
| 5 | `117_06...m1p90_dc105...` | 1.90 | 105.0 |

## Recommended execution

First submit the peak-stage screen:

```bash
sbatch submit_sws4_recal_wave1_peak_screen_hpc.sh
```

It stops at 1810 s, immediately after the end of the 28 MPa peak hold. Rank the cases mechanically using the following priorities:

1. slip initiation remains close to 16 MPa;
2. shear displacement is approximately 0.017, 0.041, and 0.075 mm at the 20, 24, and 28 MPa stages;
3. shear stress is approximately 9.38, 6.48, and 3.12 MPa at these stages;
4. normal displacement approaches -0.041 mm at peak without a large early jump.

After downloading the screen CSVs, they can be ranked with:

```bash
python score_sws4_recal_wave1.py --results /path/to/peak_screen \
  --output SWS4_wave1_peak_ranking.csv
```

Then submit full cycles only for the best one or two array IDs. For example, to run IDs 1 and 4:

```bash
sbatch --array=1,4%2 submit_sws4_recal_wave1_full_hpc.sh
```

Submitting the full script without `--array` runs all six cases, with at most three simultaneous simulations:

```bash
sbatch submit_sws4_recal_wave1_full_hpc.sh
```

Every simulation uses eight MPI ranks. Checkpoints are disabled to reduce I/O. The encoded output location is:

```text
Examples/YeGhasemmi2018/SWS4/proposed_inputs/sws4_recalibration_wave1_20260902/
```

## Scientific stopping rule

Do not change the dilation or hydraulic parameters based on the peak screen alone. Select the mechanical weakening path first. After a full-cycle candidate reproduces the stress and slip histories, a second wave may adjust mechanical dilation. Only after that should the hydraulic retained-dilation and slip-damage parameters be revisited.

The common stiffness remains provisional because 796 kN/mm belongs to the MTS 815 reported by Kalantar et al. (2025), not a measured MTS 816 value for Ye and Ghassemi (2018).
