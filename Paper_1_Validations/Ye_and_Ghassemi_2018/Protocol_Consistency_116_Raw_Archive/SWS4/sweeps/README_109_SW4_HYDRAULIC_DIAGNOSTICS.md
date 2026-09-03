# SW-S4 109-series hydraulic diagnostic decks

Parent deck: `93_07_sw4_final_theta30_jrc5_ppfix.i`

These are controlled counterfactual tests. They must not replace the calibrated parent as the Table 2 validation case, and their remaining parameters must not be recalibrated.

| Deck | Controlled parameter changes | Scientific question |
|---|---|---|
| `109_01_sw4_floor1nm_g028_ppfix.i` | `min_hydraulic_aperture=1.0e-9` | Does the calibrated 0.28 µm gouge law tend below the initial permeability when the parent floor is removed? |
| `109_02_sw4_floor1nm_g042_ppfix.i` | `min_hydraulic_aperture=1.0e-9`; `slip_damage_scale=0.42e-6` | Where is the transition between the calibrated 0.28 µm and tested 0.56 µm gouge-loss regimes? |
| `109_03_sw4_floor1nm_nodilation_ppfix.i` | `min_hydraulic_aperture=1.0e-9`; `dilation_scale=0` | What is the unconstrained no-dilation response that was hidden by the parent 0.74 µm floor? |

Every deck uses the same mesh, schedule, mechanics, closure law, roughness law, pressure coupling, solver, and time-step controls as the parent. The decks live in `SWS4/Sweeps`, beside the parent `93_07` deck, which is where `table2_gate.py` and `update_table2_ranking.py` expect a deck to sit next to its results.

Two path rules govern how these decks must be launched, and they resolve against different roots:

- `mesh_file = ../mesh/ye2018_sw_s4_theta30_size5_mesh.e` is a `MeshFileName`, resolved relative to the **input file**. From `SWS4/Sweeps/` it reaches `SWS4/mesh/`, so no mesh override is ever required.
- The `Outputs` `file_base` values are used verbatim and resolved relative to the **working directory** (`FileOutput::setFileBaseInternal` calls `std::filesystem::absolute`). They are written relative to the specimen directory, so every run must be launched from `SWS4/`, with the deck given as `-i Sweeps/<stem>.i`. MOOSE creates the output directories itself.

## Output directory

The decks write unique outputs beneath:

`SWS4/paper_revision_20260901_followup/`

with separate `csv`, `exodus`, `checkpoint`, and `logs` subdirectories.

This separation is deliberate and the submission scripts **must not** override
`csv_file_base` / `exodus_file_base` back to `results_csv_hpc_rorqual/` and
`results_exodus_hpc_rorqual/`. Those directories hold the calibrated parent
`93_07` result set and are the glob that the Table 2 ranking rebuild scores.
Writing these counterfactuals there is exactly the confusion this README warns
against in its opening paragraph.

## Eight-core commands

Run from `Examples/YeGhasemmi2018/SWS4` using the MPICH launcher that matches the ORCA build:

```bash
/home/geomechanics/miniforge/envs/moose/bin/mpiexec.hydra -n 8 \
  /media/geomechanics/Data4TB/projects/orca_4.0/orca-opt \
  -i Sweeps/109_01_sw4_floor1nm_g028_ppfix.i

/home/geomechanics/miniforge/envs/moose/bin/mpiexec.hydra -n 8 \
  /media/geomechanics/Data4TB/projects/orca_4.0/orca-opt \
  -i Sweeps/109_02_sw4_floor1nm_g042_ppfix.i

/home/geomechanics/miniforge/envs/moose/bin/mpiexec.hydra -n 8 \
  /media/geomechanics/Data4TB/projects/orca_4.0/orca-opt \
  -i Sweeps/109_03_sw4_floor1nm_nodilation_ppfix.i
```

The system OpenMPI launcher at `/usr/bin/mpiexec` is incompatible with this ORCA binary and must not be used.

## HPC submission

`Sweeps/109_0*.sh` are Slurm scripts for Rorqual. Submit them from anywhere; each
one sets `--chdir` to `SWS4` and passes the deck as `-i Sweeps/<stem>.i`, which
satisfies both path rules above. They request 24 h, matching the parent `93_07`
job -- no SW-S4 sweep in this repository has ever been given less than 12 h, and
dropping `min_hydraulic_aperture` to 1 nm makes the hydraulic problem stiffer and
the time-stepping slower than the parent, not faster.

```bash
sbatch Sweeps/109_01_sw4_floor1nm_g028_ppfix.sh
sbatch Sweeps/109_02_sw4_floor1nm_g042_ppfix.sh
sbatch Sweeps/109_03_sw4_floor1nm_nodilation_ppfix.sh
```

Slurm does not create directories for `--output` / `--error`, so
`paper_revision_20260901_followup/logs/` is kept in the repository with a
`.gitkeep`. The jobs run with `Outputs/chk/enable=false`, so a wall-clock
timeout is not restartable.

## Validation status

On 2026-09-01, all three decks completed `orca-opt --check-input` with exit code 0 and `Syntax OK`. The inherited `OrcaTHMaterial` deprecation warnings do not prevent execution and are unrelated to these hydraulic controls.
