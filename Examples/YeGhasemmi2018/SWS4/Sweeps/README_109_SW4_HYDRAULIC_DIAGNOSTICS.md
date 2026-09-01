# SW-S4 109-series hydraulic diagnostic decks

Parent deck: `93_07_sw4_final_theta30_jrc5_ppfix.i`

These are controlled counterfactual tests. They must not replace the calibrated parent as the Table 2 validation case, and their remaining parameters must not be recalibrated.

| Deck | Controlled parameter changes | Scientific question |
|---|---|---|
| `109_01_sw4_floor1nm_g028_ppfix.i` | `min_hydraulic_aperture=1.0e-9` | Does the calibrated 0.28 µm gouge law tend below the initial permeability when the parent floor is removed? |
| `109_02_sw4_floor1nm_g042_ppfix.i` | `min_hydraulic_aperture=1.0e-9`; `slip_damage_scale=0.42e-6` | Where is the transition between the calibrated 0.28 µm and tested 0.56 µm gouge-loss regimes? |
| `109_03_sw4_floor1nm_nodilation_ppfix.i` | `min_hydraulic_aperture=1.0e-9`; `dilation_scale=0` | What is the unconstrained no-dilation response that was hidden by the parent 0.74 µm floor? |

Every deck uses the same mesh, schedule, mechanics, closure law, roughness law, pressure coupling, solver, and time-step controls as the parent. The mesh path is stored as `../mesh/ye2018_sw_s4_theta30_size5_mesh.e`, so no mesh override is required when the input is located in `SWS4/Sweeps`.

## Output directory

The decks write unique outputs beneath:

`SWS4/paper_revision_20260901_followup/`

with separate `csv`, `exodus`, and `checkpoint` subdirectories.

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

## Validation status

On 2026-09-01, all three decks completed `orca-opt --check-input` with exit code 0 and `Syntax OK`. The inherited `OrcaTHMaterial` deprecation warnings do not prevent execution and are unrelated to these hydraulic controls.
