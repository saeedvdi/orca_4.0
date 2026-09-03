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

`FIX 5` implements the criterion the `FIX 3` comment describes; `FIX 8` adds the junction
case; `FIX 9` makes both tests operate on **edges** rather than nodes:

| edge with `face_count == 1` | meaning | action |
|---|---|---|
| lies IN an exterior face | the fracture daylights on the sample surface | **split** |
| is an edge of another interface | a branch terminating against a second fracture | **split** |
| otherwise | a true crack front inside the material | **weld** |

Edge-based matters. In a plane-strain model **one element thick** every node lies on the
z-min or z-max face, so a node test calls every crack tip "exterior" and splits it — which
is exactly what it did, giving 2 node copies at each tip where there must be 1. The tip
*edge* runs through the thickness at an interior (x, y) and is not an edge of any exterior
face, so `exteriorEdges()` separates the two correctly at any thickness.

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

## Finding 2 (FIXED): a one-sided sideset silently welded the fracture

The generator processed each interface face once via

```cpp
if (elem->id() < neighbor->id())
  continue;
```

which assumes the sideset carries **both** sides of every face and keeps the higher-id
copy. That holds for a sideset built from a nodeset — the Kalantar path — but **not** for
one from `SideSetsBetweenSubdomainsGenerator`, which is one-sided. Every face whose owner
had the lower id was dropped, and with the usual element numbering that is all of them.

The failure was completely silent. No error, no warning; the primary and secondary
sidesets were still created with the right side counts (64 each), the interface kernels
still assembled, the solve still converged — and `w_max` came out **exactly 0** with the
crack welded shut.

**`FIX 7`** de-duplicates against what the sideset actually holds: skip this copy only when
the partner copy is also in the sideset and will be processed instead. On a one-sided
sideset this copy is the only one there is.

`sneddon_orca_generator.i` now feeds the generator a **one-sided** sideset deliberately, so
it guards the fix. With the sideset made two-sided by hand the result is bit-identical
(`w_max = 7.1193073752858e-4` either way), which is what says the de-duplication is now
correct for both layouts rather than merely working for one.

## Finding 3 (FIXED): more than one fracture with two-sided interfaces

This one was **misdiagnosed at first**. It looked like intersecting fractures were
unsupported, because a T-shaped pair failed with `Periodic boundary neighbor not found`.
Two probes showed otherwise:

| case | `add_interface_on_two_sides` | result |
|---|---|---|
| two **intersecting** sidesets | false | **OK** |
| two **parallel** sidesets | true | **failed** |
| two intersecting sidesets | true | failed |

So intersection is irrelevant. The trigger is **two or more sidesets plus two-sided
interfaces** — which is always, since that is what InterfaceKernels need.

The cause is in the secondary-sideset allocation. `find_free_boundary_id()` scans
`boundary_info.get_boundary_ids()`, but allocating only calls
`boundary_info.sideset_name(id)`, which registers a **name**. The id itself does not enter
`get_boundary_ids()` until a side is actually assigned to it, which happens much later. So
the second allocation saw the first secondary id as still free and handed out the same id:
every secondary sideset collapsed into one boundary.

The symptom was remote from the cause. The generator itself succeeded; the mesh then died
inside libMesh's `find_neighbors` at `periodic_boundaries.C:107`, because
`add_disjoint_neighbor_boundary_pairs` could not pair a primary face against a secondary
boundary that now held both sides of both fractures.

**`FIX 6`** remembers the ids it hands out. `two_fracture_generator.i` guards it: four
sidesets with distinct ids and their expected side counts (`frac_h` 8, `frac_v` 4,
`frac_h_other` 8, `frac_v_other` 4).

**A single fracture was never affected** — every Kalantar2025 deck uses one
`fracture_interface` nodeset, allocates once, and hits neither defect.

## Finding 4 (FIXED): the junction partition was inverted

The mesh-only tests passed and the junction node had the right **three** copies — and the
connectivity was still wrong. What the three copies actually contained:

| | Orca (before) | `BreakMeshByBlock` |
|---|---|---|
| copy 1 | `{EN}` | `{ES}` |
| copy 2 | `{ES, WS}` | `{EN, WN}` |
| copy 3 | `{WN}` | `{WS}` |

The reference groups the two quadrants *above* the horizontal fracture, which no fracture
separates, and keeps the two below apart, which the vertical fracture does separate. The
Orca partition was the inverse: it welded together the two flanks a fracture runs between,
and split the block nothing runs through.

The cause was the side assignment. Each sideset was processed in turn, duplicating one node
and assigning elements by a **geometric half-space test** against that interface's normal.
Correct for one fracture; wrong wherever two meet, because the second interface's pass also
moved elements that do not touch it at all — the cap sits entirely above the vertical
fracture, yet was split by it.

**`FIX 10`** partitions by **connectivity** instead: two elements at a node belong to the
same piece when they share a face that contains the node and is not an interface face. For
a single fracture this reduces exactly to the old two-sided split. `splitNodesOnInterface`
and `stitchNodesToElems` are replaced by one `splitInterfaceNodes`, which also does the
sideset bookkeeping *before* any node is repointed — removing the hazard `FIX 2` had to
work around.

### How it was caught, and why the mesh tests could not catch it

`junction_physics_orca.i` and `junction_physics_breakmesh.i` solve the **same** T-fracture
physics, cut by the two generators, and compare. Before the fix:

| | Orca | `BreakMeshByBlock` | rel. diff |
|---|---:|---:|---:|
| `slip_max_h` | 5.913e-4 | 2.079e-3 | **0.72** |
| `dn_max_h` | −1.137e-5 | −6.931e-5 | **0.84** |
| `aperture_max` | 1.0644e-2 | 1.0928e-2 | 0.026 |

After:

| | Orca | `BreakMeshByBlock` | rel. diff |
|---|---:|---:|---:|
| every postprocessor | — | — | **0.00e+00** |

Bit-identical on all seven. A node-count test cannot see an inverted partition; only
solving on it can.

## Do any of the fixes require reruns? No.

Re-verified after **all five** fixes, including the complete rewrite of the splitting
algorithm, by regenerating each Kalantar mesh and comparing MD5 hashes of the coordinate
and connectivity arrays against the pre-fix values:

| deck | nodes | coord md5 | conn md5 | |
|---|---:|---|---|---|
| `OGSH/110_38_og_sh_control_r13.i` | 106 758 | `3d41384f2470bf1c` | `dcac2f6b09187f77` | identical |
| `OGSC/110_05_og_sc_bbfast_r1.i` | 74 290 | `e7b09c3238e09240` | `f0fe36265ca5b67f` | identical |
| `OGT/110_03_og_t_bbfast_r1.i` | 59 722 | `72771d0bfb16c5c5` | `2b6fb8797338b2fb` | identical |

All three use a single nodeset-derived, two-sided interface on a through-going fracture —
the one configuration every defect here leaves alone. **No Kalantar or Ye result changes,
and nothing needs rerunning.**

## Why there are no shear-compression or T-fracture variants

Both would need the same treatment, and neither can get it here:

* `OrcaFaultInterface3DGenerator` hard-errors on `mesh_dimension() != 3`;
* both benchmark meshes are 2D **`SHELL4`**, and `MeshExtruderGenerator` refuses to extrude
  shell elements (`libMesh::MeshTools::Generation::build_extrusion` — *"feature not
  implemented"*);
* there is no Cubit on this workstation to regenerate them as 3D meshes.

(Finding 3 no longer blocks it; the remaining obstacle is purely the 2D `SHELL4` mesh.) Sneddon is the one
benchmark whose mesh is generated in-deck, so it is the only one that could be rebuilt in
3D without Cubit — which is why it is the one that exists.

## Running it

```bash
mpiexec -n 4 ../../../../orca-opt -i sneddon_orca_generator.i
```
