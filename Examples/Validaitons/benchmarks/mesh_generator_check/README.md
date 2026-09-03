# Mesh-generator check — `OrcaFaultInterface3DGenerator` against a closed form

## Why this directory exists

Every benchmark in `../sneddon`, `../shear_compression`, `../fracutre_interseciton_problem`
and `../Induced_stress_along_a_fault_mesh` builds its fracture with MOOSE's stock
`BreakMeshByBlockGenerator`, or has no fracture at all. **None of them touches
`OrcaFaultInterface3DGenerator`** — the generator every `Examples/Kalantar2025` OG-SH,
OG-SC and OG-T deck depends on. So the generator the research results actually rest on had
no verification against a closed-form solution.

`sneddon_orca_generator.i` supplies that. It is `../sneddon/sneddon_barton_bandis.i` with
exactly three changes — a 3D one-element-thick mesh, `disp_z` pinned on both z faces (which
makes it plane strain, i.e. the same boundary-value problem), and the fracture cut by
`SideSetsBetweenSubdomainsGenerator` + `OrcaFaultInterface3DGenerator`. Material, loading,
solver and refinement are untouched, so any difference is attributable to the generator.

## Result

Refinement is 2 rather than the shipped 4, to keep a 3D direct solve affordable on four
ranks. `../README.md`'s convergence table gives the target at that refinement exactly.

| | this deck | `BreakMeshByBlockGenerator`, level 2 | meshed |
|---|---:|---:|---:|
| `w_max` error | **−5.0759 %** | −5.076 % | — |
| fitted amplitude error | **−1.388 %** | −1.388 % | — |
| fitted half-length | **0.96195 m** | 0.96195 m | 1.0 m |
| open-crack traction ratio | 3.5e-16 | 3.1e-16 | 0 |

**The two generators agree to the printed precision on every quantity.** That is the
statement this deck exists to make: the crack-opening amplitude, the effective crack
length and the traction-free open state do not depend on which generator cut the fracture.

This required a fix, described next.

## Finding 1 (FIXED): the crack-front nodes were split, and both options meant to prevent it were inert

### What was wrong

An embedded crack must be held shut at its tips by the intact rock beyond them. The
generator split the tip nodes along with the rest, so the crack had free ends:

| | before the fix | after | `BreakMeshByBlock` |
|---|---:|---:|---:|
| `w_max` error | +12.838 % | −5.0759 % | −5.076 % |
| fitted amplitude error | −1.681 % | −1.388 % | −1.388 % |
| fitted half-length | 1.14696 m | 0.96195 m | 0.96195 m |
| tip-element opening | 4.77e-4 m | 1.51e-4 m | — |

The shape fit localized the defect precisely: the **amplitude was already right**, so the
interface kernels, the fluid-pressure kernel and the contact law were never in question.
Only the effective *length* was wrong — the crack behaved as if it were 15 % longer than
the one that was meshed.

`preserve_front_nodes` and `split_only_interior_nodes` were documented to prevent exactly
this and did nothing. Setting **both to false** produced a mesh with the **same 41290
nodes** as setting both to true.

### Why

The removal set was

```
nodes_to_remove = { n in bnd_node_ids : n not in nodes_with_cross_neighbor }
```

but `nodes_with_cross_neighbor` was built by scanning the same faces, with the same
`!neighbor` and `elem->id() < neighbor->id()` filters, that built `bnd_node_ids`. The two
sets were equal by construction, so the removal was always a no-op.

This was the second attempt at the logic. The `FIX 3` comment in the source records that
the *original* code treated every `face_count == 1` edge as crack front, which wrongly
welded a through-going fracture shut where it daylights on the sample surface. That comment
also states the correct criterion — and then the code does something else.

### The fix

`FIX 5` implements the criterion the `FIX 3` comment describes. A node is welded when it
lies on an edge that bounds the interface surface **and** that edge is not wholly on the
specimen exterior:

| edge | meaning | action |
|---|---|---|
| `face_count == 1`, entirely on the mesh exterior | the fracture daylights on the sample surface | **split** |
| `face_count == 1`, not entirely on the exterior | a true crack front inside the material | **weld** |
| `face_count > 2` | a junction between branches | **weld** |

`exteriorNodes()` computes the exterior set once, from element sides with no neighbour.
`getSidesetNodes` now takes the mesh so it can use it.

### Does this mean the Kalantar cases must be rerun? No.

For a fracture that cuts the whole specimen, **every** bounding edge of the interface lies
on the cylindrical surface, so the new rule removes nothing and the generated mesh is
unchanged. Verified directly, by generating each mesh with the new removal active
(`true/true`, what the decks set) and disabled (`false/false`, which is exactly what the
old inert code did) and comparing node counts and MD5 hashes of the coordinate and
connectivity arrays:

| deck | nodes | elements | result |
|---|---:|---:|---|
| `OGSH/110_38_og_sh_control_r13.i` | 106758 | 101972 | **bit-identical** |
| `OGSC/110_05_og_sc_bbfast_r1.i` | 74290 | — | **bit-identical** |
| `OGT/110_03_og_t_bbfast_r1.i` | 59722 | — | **bit-identical** |

The argument is airtight because *old behaviour ≡ no removal*: the old code removed nothing
regardless of the flags (proven by the identical node counts above), and the new removal
block is guarded by `if (_split_only_interior_nodes || _preserve_front_nodes)`, so with both
false it is skipped entirely. Old ≡ new-with-flags-false ≡ new-with-flags-true on these
meshes. **No Kalantar or Ye result changes, and nothing needs rerunning.**

What the fix does change is that the generator is now correct for embedded cracks too, and
that the two front options finally mean what they say.

## Finding 2 (open): a one-sided sideset silently welds the fracture

The generator processes each interface face once, via

```cpp
if (elem->id() < neighbor->id())
  continue;
```

which assumes the sideset carries **both** sides of every face and keeps the higher-id
copy. `SideSetsBetweenSubdomainsGenerator` produces a **one-sided** sideset. Every face
whose owner has the lower id is then dropped — here, all of them.

The failure is completely silent. No error, no warning; the primary and secondary sidesets
are still created with the right side counts (64 each), the interface kernels still
assemble, the solve still converges — and `w_max` comes out **exactly 0** with the crack
welded shut. The deck works around it by adding a second
`SideSetsBetweenSubdomainsGenerator` with the blocks swapped and the same
`new_boundary` name.

## Finding 3 (open): intersecting fractures are not supported

Given two sidesets that share an edge, the generator hard-fails with
`Periodic boundary neighbor not found`. Each one alone is fine:

| `sidesets` | result |
|---|---|
| `frac_h` | OK — 258 nodes from a 243-node base |
| `frac_v` | OK — 252 nodes |
| `frac_h frac_v` | **ERROR** — `Periodic boundary neighbor not found` |

Tested on a synthetic 3D box with the same T topology as
`../fracutre_interseciton_problem`. This one at least fails loudly.

## Why there are no shear-compression or T-fracture variants

Both would need the same treatment, and neither can get it here:

* `OrcaFaultInterface3DGenerator` hard-errors on `mesh_dimension() != 3`;
* both benchmark meshes are 2D **`SHELL4`**, and `MeshExtruderGenerator` refuses to extrude
  shell elements (`libMesh::MeshTools::Generation::build_extrusion` — *"feature not
  implemented"*);
* there is no Cubit on this workstation to regenerate them as 3D meshes.

The T-fracture variant would in any case stop at Finding 3 above. Sneddon is the one
benchmark whose mesh is generated in-deck, so it is the only one that could be rebuilt in
3D without Cubit — which is why it is the one that exists.

## Running it

```bash
mpiexec -n 4 ../../../../orca-opt -i sneddon_orca_generator.i
```
