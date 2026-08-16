# Ye & Ghassemi (2018) meshes — state after the 2026-08-16 paper audit

Every mesh in this campaign is a cylinder webcut by a single plane at the
specimen's fracture angle θ, measured **from the core's long axis**. Two of the
four were cut at the wrong angle, and one is the wrong length. This file records
what is here now, how it was verified, and what is still outstanding.

## How θ was checked

Not from Table 1 — from the paper's own reduction. Dividing eq (3) by eq (4)
removes the differential stress:

```
σ'ₙ = (σ₃ − P_p) + σ_d sin²θ        (3)
τ   = σ_d sinθ cosθ                 (4)
  ⇒  tan θ = (σ'ₙ − σ₃ + P_p) / τ
```

Every quantity on the right is tabulated, so θ can be recovered independently at
all eleven hold stages of Table 2. `scripts/paper_parameter_audit.py` §1b does
this. The plane in each `.e` file is recovered independently again, by fitting a
plane to the nodes shared by the two element blocks.

| specimen | Table 1 | recovered from Table 2 | mesh before | mesh now |
|---|---|---|---|---|
| SW-T1 | 32.0° | 32.000° | 32.000° ✓ | unchanged |
| SW-T2 | 31.0° | **30.001°** | 31.000° ✗ | **30.000°** |
| SW-S3 | 29.0° | 29.028° | 29.000° ✓ | unchanged |
| SW-S4 | 30.0° | 30.020° | **28.990°**, 2.85 mm off centre ✗ | **30.000°**, centred |

SW-T2 is the one case where Table 1 and Table 2 disagree with each other. The
recovery reproduces the printed angle for the other three specimens to 0.03°, so
it is the printed 31° that is wrong, not the method.

SW-S4's old journal is a copy of SW-S3's: its fracture-plane z-span is
bit-identical (0.09115854 m), which is how a 118.70 mm specimen ended up with a
123.40 mm specimen's plane offsets.

## Current files

| file | θ | centred | notes |
|---|---|---|---|
| `SWT1/mesh/ye2018_sw_T1_mesh_size_{3,5}.e` | 32.000° | yes | correct as built |
| `SWT2/mesh/ye2018_sw_T2_mesh_size_{3,5}.e` | 31.000° | yes | **superseded**, kept for the 87_02 lineage |
| `SWT2/mesh/ye2018_sw_T2_theta30_mesh_size_{3,5}.e` | 30.000° | yes | used by 89_03, 89_05 |
| `SWS3/mesh/sw3_mesh_size{3,5}.e` | 29.000° | yes | correct angle, **1.00 mm too long** |
| `SWS4/mesh/ye2018_sw_s4_size{1,3,5}_mesh.e` | 28.990° | −2.85 mm | **superseded**, kept for the 68_xx lineage |
| `SWS4/mesh/ye2018_sw_s4_theta30_size{3,5}_mesh.e` | 30.000° | yes | used by 89_01, 89_06 |

The corrected SW-T2 and SW-S4 meshes were built in `orca_3.0_claude_edit/
Examples/YeGhasemmi2018/final_simulation_runs_v3/meshes/` and had never been
ported into a repo the production decks run from. `SWS4/mesh/README_fracture_angle.md`
is that work's original write-up, copied here alongside them.

### Nodeset naming — a trap when swapping the SW-S4 mesh

The old SW-S4 mesh names its boundaries `top` / `bottom` / `sides`; every other
mesh in the campaign, including the corrected SW-S4 one, uses
`top_nodeset` / `bottom_nodeset` / `sides_nodeset`. A deck that swaps the mesh
without renaming will fail at setup, which is the good case. The 89-series decks
carry the rename.

## Still outstanding: SW-S3 length

`SWS3/mesh/sw3_mesh_size5.e` is 124.40 mm against the paper's 123.40 mm — 0.8 %.
The angle and centring are right; only the length is wrong.

`SWS3/mesh/sw3_mesh_L123p4.jou` is the corrected journal. It has **not** been
built, because that needs Cubit and Cubit is not installed on this machine. The
effect is confined to the core's axial stiffness: the fracture ellipse area is
`πD²/(4 sinθ)` and does not contain L, and the flow geometry factor W/L is set
in the deck from Table 2 rather than from the mesh. It is the smallest finding of
the audit.

## MANDATORY after any mesh rebuild

```bash
python3 scripts/check_source_nodes.py --deck Examples/YeGhasemmi2018/SWS4/89_01_sw4_bbfast_theta30_paperjrc_kernel_SV_biot0p6.i
```

`ExtraNodesetGenerator ... use_closest_node = true` never errors. If the
requested injection coordinate misses the fracture plane it silently pins the
source to the nearest **bulk** node and the run drives the matrix instead of the
joint. This is not hypothetical: on the corrected SW-S4 size-5 mesh the ideal
borehole position (6.00 mm inside the sidewall) has a bulk node 1.734 mm away and
the nearest interface node 1.776 mm away — the bulk node wins. The 89-series
decks therefore carry the **exact interface-node coordinates**, which sit 6.89 mm
inside the sidewall on this mesh resolution, rather than the ideal position.
