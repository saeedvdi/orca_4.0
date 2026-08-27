# Final BBFast pressure-stage Exodus reruns

## Purpose

The existing final calibrations are preserved. The Slurm array launcher
`run_final_bbfast_exodus_pressure_stages_hpc.sh` reruns those exact four input
decks and changes only the output controls on the command line. Trusted CSV
files and any existing Exodus files are not overwritten.

Each new Exodus database contains synchronized states at:

- the initial state, `t = 0`;
- loading at 6, 8, 10, ..., 28 MPa; and
- unloading at 26, 24, 22, ..., 8 MPa.

The nominal experimental stages at 8, 12, 16, 20, 24, and 28 MPa are sampled
at the end of each hold. The intermediate even pressures are sampled at the
exact crossing time obtained by linear interpolation of the deck's own
`[Functions]/[injection_pressure]` PiecewiseLinear function. MOOSE's
`sync_times` forces the transient solver to land exactly on these times;
`sync_only = true` prevents the Exodus database from growing at every ordinary
time step.

## Important lower-pressure limit

The selected simulations do not contain physical 0, 2, or 4 MPa injection
states. SW-T1, SW-T2, and SW-S4 start at 5 MPa; SW-S3 starts at 5.755 MPa. The
unloading schedules end near 8 MPa. The launcher therefore writes the initial
state at `t = 0`, followed by the first attainable even pressure, 6 MPa.
Producing fields at 0, 2, and 4 MPa would require changing the prescribed
pressure history and would no longer be a rerun of the selected final model.

## Array mapping

| Array index | Specimen | Final input deck |
|---:|---|---|
| 0 | SW-T1 | `SWT1_OrcaBartonBandisContactTractionFastADHardening.i` |
| 1 | SW-T2 | `SWT2_OrcaBartonBandisContactTractionFastADHardening.i` |
| 2 | SW-S3 | `SWS3_OrcaBartonBandisContactTractionFastADHardening.i` |
| 3 | SW-S4 | `SWS4_OrcaBartonBandisContactTractionFastADHardening.i` |

## Submission

From `Examples/YeGhasemmi2018` on the cluster:

```bash
sbatch run_final_bbfast_exodus_pressure_stages_hpc.sh
```

To submit or repeat just one specimen, supply its array index. For example,
SW-T1 only is:

```bash
sbatch --array=0 run_final_bbfast_exodus_pressure_stages_hpc.sh
```

## New outputs

Each sample directory receives distinct output folders:

```text
results_exodus_pressure_stages/<case>_exostages_hpc.e
results_csv_pressure_stages/<case>_exostages_hpc.csv
```

The compact synchronized CSV is retained as an audit companion to the Exodus
file. It should have 23 states/rows (subject to the CSV writer's representation
of the initial state), ordered monotonically in time. Checkpoints are disabled
because these are clean full reruns intended only to reconstruct field output.

The same synchronized times are now embedded directly in all four renamed
input decks. Four individual submission scripts with matching names are also
available in the specimen folders; the array launcher is retained as a
convenient all-specimen alternative.

## Peak-stage details

The nominal 28 MPa stage is anchored to the end of the actual peak hold, as in
the Table 2 scoring procedure. This matters for the digitized schedules:
SW-S3 peaks at about 28.566 MPa and SW-S4 at about 27.964 MPa. Treating those
peaks as nominal stage 28 is consistent with the experiment and avoids sampling
the rising side of the peak before the main response has developed.

SW-S3's pressure function has a final knot at 4802.4 s, whereas the validated
deck ends at 4802.0 s. Its final synchronized state is therefore set to 4802.0
s rather than extending the selected simulation.
