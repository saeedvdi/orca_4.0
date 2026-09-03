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
| `w_max` error | **+12.838 %** | −5.076 % | — |
| fitted amplitude error | **−1.681 %** | −1.388 % | — |
| fitted half-length | **1.14696 m** | 0.96195 m | 1.0 m |
| open-crack traction ratio | 1.8e-16 | 3.1e-16 | 0 |

**The amplitude is right; the half-length is not.** That split is the whole finding. The
amplitude is the constitutive half of the answer, so the interface kernels, the
fluid-pressure kernel and the contact law are all wired correctly through this generator —
it produces a mechanically sound interface, and the open crack is traction-free to 1e-16.
The half-length says the crack behaves as if it were 15 % longer than the one that was
meshed.

## Three findings

### 1. The crack-front nodes are split, and both options meant to prevent that are inert

An embedded crack must be held shut at its tips by the intact rock beyond them. This
generator splits the tip nodes along with the rest, so the crack has free ends — the tip
element still carries 4.77e-4 m of opening, 64 % of `w_max`.

`preserve_front_nodes` and `split_only_interior_nodes` are documented to prevent exactly
this. They do not. Setting **both to false** produces a mesh with the **same 41290 nodes**
as setting both to true:

| `preserve_front_nodes` | `split_only_interior_nodes` | nodes |
|---|---|---:|
| true | true | 41290 |
| false | false | 41290 |

The reason is visible in `src/meshgenerators/OrcaFaultInterface3DGenerator.C`. The removal
set is

```
nodes_to_remove = { n in bnd_node_ids : n not in nodes_with_cross_neighbor }
```

but `nodes_with_cross_neighbor` is built by scanning the same faces, with the same
`!neighbor` and `elem->id() < neighbor->id()` filters, that built `bnd_node_ids`. The two
sets are therefore equal by construction and the removal is always a no-op. The only other
removal rule — `face_count > 2` — cannot fire either, because `edge_face_count` is rebuilt
inside the per-sideset loop, so it never sees an edge shared by faces of two different
fractures.

**This does not invalidate the Kalantar2025 results.** Those fractures cut the whole
specimen, so their edge lies on the sample's outer surface where splitting *is* correct,
and there is no crack front inside the material for the broken logic to mishandle. What it
does mean is that the generator is verified only for **through-going** fractures, and that
the two front options should not be relied on.

### 2. A one-sided sideset silently welds the fracture

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

### 3. Intersecting fractures are not supported

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

The T-fracture variant would in any case stop at finding 3 above. Sneddon is the one
benchmark whose mesh is generated in-deck, so it is the only one that could be rebuilt in
3D without Cubit — which is why it is the one that exists.

## Running it

```bash
mpiexec -n 4 ../../../../orca-opt -i sneddon_orca_generator.i
```
