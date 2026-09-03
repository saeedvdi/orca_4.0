# Series 130 — SW-T1 loading-stiffness sweep

## Question

Ye and Ghassemi (2018, §4.3, Table 3) characterise the slip episodes by their
stress-relaxation rates — 7 to 20 MPa/s for the rough fractures — and compare
the associated slip rates with the field measurements of Guglielmi et al.
(2015). Under displacement control the specimen and the loading frame form a
series-stiffness system, so how much of that stress drop is a property of the
fracture and how much of the machine?

This sweep answers it directly: vary the axial boundary stiffness alone, hold
every constitutive parameter fixed, and measure the resulting stress-drop rate.

## Design

Seven members, all derived from the paper's selected SW-T1 Barton–Bandis deck
(`01_Main_Validation/SWT1/SWT1_OrcaBartonBandisContactTractionFastADHardening.i`).

| idx | deck | k_p (Pa/m) | k/k0 |
|----:|------|-----------:|-----:|
| 0 | `130_01_swt1_kp1p000e11` | 1.000e11 | 0.24 |
| 1 | `130_02_swt1_kp2p000e11` | 2.000e11 | 0.49 |
| 2 | `130_03_swt1_kp4p123e11` | 4.123e11 | 1.00 (control) |
| 3 | `130_04_swt1_kp1p000e12` | 1.000e12 | 2.43 |
| 4 | `130_05_swt1_kp3p000e12` | 3.000e12 | 7.28 |
| 5 | `130_06_swt1_kp1p000e13` | 1.000e13 | 24.25 |
| 6 | `130_07_swt1_kp1p000e14` | 1.000e14 | 242.5 |

The range spans the stiffnesses the four-specimen calibration actually
requires (4.1e11 for SW-T1 up to 1.0e13 for SW-S3), plus a softer end and a
near-rigid limit. Member 2 is byte-identical to the parent and is the control:
it must reproduce the paper's SW-T1 case.

## The preload compensation — why the other members are not simple copies

The boundary is a spring, so the commanded displacement must absorb sigma/k.
Changing `axial_bc_penalty` alone would change the preload state as well as the
stiffness, and the sweep would confound the two. The parent deck says so
explicitly: *"axial_pres_final is calibrated on this size-5 mesh; recheck this
gate whenever the mesh, penalty, elastic properties, or boundary setup changes."*

Each member therefore recomputes both ramp endpoints from

    u(k) = u_z* + sigma/k

with `u_z* = -2.907742886968820e-04` m and `sigma_preload = -1.81593e8` Pa,
both taken from the calibrated run's `machine_spring_gap_m_pp` (gap x k
reproduces `machine_spring_sigma1_mpa_pp` to printed precision). Round-tripping
this formula at k0 recovers the parent's `axial_pres_final` to 8e-7 relative.

**Gate to re-check on every member** (from the parent header): at t = 55 s
`cumulative_plastic_slip_pp` must be 0, and the first 8 MPa hold should give
differential stress ~147 MPa and shear stress ~67.5 MPa. The compensation is
first order in the specimen response, so a member that misses the gate needs
`axial_pres_final` iterated before its result is used.

## Running

    sbatch run_stiffness_sweep_hpc.sh            # all seven
    sbatch --array=2 run_stiffness_sweep_hpc.sh  # control only

Exodus and checkpoints are disabled and CSV is written every timestep: the
quantity of interest is d(sigma_d)/dt through the burst, not the field. The
parent writes CSV only every 5th step, which is too coarse to fit a rate.

## Analysis

    python3 analyze_stiffness_sweep.py results_csv

Prints slip-burst onset, duration, total drop, peak stress-drop rate, peak slip
rate and total slip per member, fits a power law of drop rate against k_p, and
writes `Figure_Stiffness_Sweep.pdf`.

## Baseline, measured from the existing calibrated run

Running the analysis on the parent CSV gives:

| quantity | model (calibrated) | Ye & Ghassemi SW-T1 |
|---|---:|---:|
| total stress drop | 74.4 MPa | 70–80 MPa |
| total shear slip | 0.537 mm | 0.532 mm |
| peak stress-drop rate | 3.55 MPa/s | 7.69 MPa/s |
| peak slip rate | 2.6e-5 m/s | 4.9e-5 m/s |
| burst duration | 47.5 s | < 10 s |

The magnitude of the drop and the total slip are reproduced; the burst is about
twice too slow and several times too long. That is consistent with the Perzyna
overstress regularisation, which the paper already notes "can affect the
duration of the transient". The sweep is therefore informative about the
*scaling* of drop rate with frame stiffness, which is the claim in the
discussion; it is not a prediction of the absolute rate, because viscosity is
held fixed and also influences it. A companion viscosity sweep would be needed
to separate the two contributions fully.
