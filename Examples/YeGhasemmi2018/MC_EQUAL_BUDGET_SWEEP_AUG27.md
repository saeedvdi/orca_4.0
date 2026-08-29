# Equal-budget Mohr–Coulomb screening sweep

**Prepared:** 2026-08-27  
**Purpose:** answer the reviewer-level question of whether the 94-series MC comparison was disadvantaged by insufficient tuning.

## Inputs and invariants

The four audited 94-series mesh-5 inputs were renamed and placed beside the final BBFast inputs:

| Sample | MC center input | BBFast reference input |
|---|---|---|
| SWT1 | `SWT1_OrcaMohrCoulombContactTraction.i` | `SWT1_OrcaBartonBandisContactTractionFastADHardening.i` |
| SWT2 | `SWT2_OrcaMohrCoulombContactTraction.i` | `SWT2_OrcaBartonBandisContactTractionFastADHardening.i` |
| SWS3 | `SWS3_OrcaMohrCoulombContactTraction.i` | `SWS3_OrcaBartonBandisContactTractionFastADHardening.i` |
| SWS4 | `SWS4_OrcaMohrCoulombContactTraction.i` | `SWS4_OrcaBartonBandisContactTractionFastADHardening.i` |

The renamed MC center cases keep the measured quantities and the matched bulk, pressure schedule, dilation, roughness-to-aperture, hydraulic closure, and solver settings fixed. The previously mismatched shared refinements were aligned before the sweep:

- SWT1 MC now uses the BBFast `V_m = 55.00 um`, closure offset `51.6707 um`, and aperture scale `0.01512`.
- SWT2 MC now uses the BBFast aperture scale `0.0177`.
- SWS3 and SWS4 already shared these inputs.

The MC material cannot use BBFast's explicit normal-unloading-retention state. That is a constitutive capability difference, not a tunable MC scalar.

## Screening design

Each specimen has nine jobs: the unmodified center and an eight-run balanced fractional design. Only five MC-specific shear parameters vary.

| Factor | Parameter | Low level | Center | High level | Role |
|---|---|---:|---:|---:|---|
| A | `friction_coefficient_rough` | 0.92x | 1.00x | 1.08x | Peak-envelope slope/onset |
| B | `cohesion_rough` | 0.90x | 1.00x | 1.10x | Peak-envelope intercept/onset |
| C | `friction_coefficient_smooth` | 0.88x | 1.00x | 1.12x | Large-slip envelope slope |
| D | `cohesion_smooth` | 0.85x | 1.00x | 1.15x | Large-slip envelope intercept |
| E | `roughness_decay_distance` | 0.75x | 1.00x | 1.25x | Weakening distance/path |

SWS4 has `cohesion_smooth = 0`, so factor D is inactive there. It remains in the common design definition for reproducibility.

| Array index | Label | A | B | C | D | E |
|---:|---|:---:|:---:|:---:|:---:|:---:|
| 0 | `center` | 0 | 0 | 0 | 0 | 0 |
| 1 | `pb01` | - | - | - | + | + |
| 2 | `pb02` | - | - | + | + | - |
| 3 | `pb03` | - | + | - | - | + |
| 4 | `pb04` | - | + | + | - | - |
| 5 | `pb05` | + | - | - | - | - |
| 6 | `pb06` | + | - | + | - | + |
| 7 | `pb07` | + | + | - | + | - |
| 8 | `pb08` | + | + | + | + | + |

This is a screening sweep, not a declaration that a corner of the design is the optimum. After scoring, use the factor directions to make one small centered refinement around the best physically admissible case. Do not expand hydraulic or dilation parameters during that refinement; doing so would cease to isolate MC shear calibration.

## Exodus output

Every BBFast and MC input writes 23 pressure-synchronized field states:

- the initial simulation state;
- loading at 6, 8, 10, ..., 28 MPa; and
- unloading at 26, 24, 22, ..., 8 MPa.

The nominal 8/12/16/20/24/28 MPa stage states use the established stage times. Intermediate even-pressure states use exact linear-interpolation crossing times. SWS3/SWS4 retain their measured non-ideal stage pressures at the established Table-2 times.

## Submission

From each specimen directory:

```bash
# One BBFast rerun
sbatch SWT1_OrcaBartonBandisContactTractionFastADHardening.sh

# All nine MC screening cases for that specimen
sbatch SWT1_OrcaMohrCoulombContactTraction.sh

# MC center only, for a four-case fair baseline check
sbatch --array=0 SWT1_OrcaMohrCoulombContactTraction.sh
```

Replace `SWT1` with `SWT2`, `SWS3`, or `SWS4` as appropriate.

MC sweep outputs are separated from existing results:

```text
results_csv_mc_sweep_hpc/<sample>_OrcaMohrCoulombContactTraction_<label>.csv
results_exodus_mc_sweep_hpc/<sample>_OrcaMohrCoulombContactTraction_<label>.e
logs/<sample>_OrcaMohrCoulombContactTraction_<array-job>_<index>.{out,err}
```

## Selection rule

Rank only completed 11-stage cases using the same five-channel objective as BBFast: flow, effective normal stress, shear stress, normal displacement, and shear displacement. Also report per-channel errors and reject a numerically lower mean if it obtains that value through nonphysical early slip, excessive unloading creep, negative/invalid strength, or hydraulic runaway.

The defensible final comparison should report both:

1. the aligned center MC cases, which are the controlled constitutive transfer; and
2. the best physically admissible screened/refined MC cases, which are the equal-budget best-effort controls.

## Completed selection (audited 2026-08-28)

All 36 CSVs are finite, time-monotonic, and reach all eleven Table 2 stages.
The independently reproduced minimum mean five-channel nRMSE in each specimen is:

| Sample | Selected MC run | Mean nRMSE |
|---|---|---:|
| SWT1 | `SWT1_OrcaMohrCoulombContactTraction_pb04` | 6.900% |
| SWT2 | `SWT2_OrcaMohrCoulombContactTraction_pb04` | 3.780% |
| SWS3 | `SWS3_OrcaMohrCoulombContactTraction_pb06` | 5.148% |
| SWS4 | `SWS4_OrcaMohrCoulombContactTraction_center` | 7.000% |

These are the MC cases of record for validation, comparison, and manuscript
figures. The 94-series names below or in older documents identify the center
deck provenance, not the final selected MC result.
