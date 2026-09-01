# Fracture-angle audit of the four meshes

The fracture angle $\theta$ is measured **from the specimen's long axis** to the
fracture plane. It sets everything: the resolved tractions
($\tau = \sigma_d\sin\theta\cos\theta$,
$\sigma'_n = (\sigma_3-P_p) + \sigma_d\sin^2\theta$), the fracture area
($A = \pi D^2/4\sin\theta$), and the borehole separation. A 1° error is not
cosmetic.

## The check

Table 2 of Ye & Ghassemi (2018) reports **both** $\sigma'_n$ and $\tau$ at eleven
hold stages. With $\sigma_3 = 30$ MPa and $P_p = \tfrac12(P_i+P_o)$ these are two
functions of the single unknown $\sigma_d$, so their ratio recovers the angle
independently of everything else:

$$\tan\theta = \frac{\sigma'_n - \sigma_3 + P_p}{\tau}$$

Run over all eleven stages of all four samples, this is a strong test — it must
return one constant per sample. It does. (Full working: `doc/theory/orca_czm_theory.md`,
Supplement, "Internal-consistency checks on the published data".)

## Result — as found

This section records the **as-found** state, before the corrections in
"Fix" below. **Every** journal on this machine was audited — the two campaign directories and the
loose copies under `~/Downloads/Telegram Desktop/` — by parsing the cylinder and the
three webcut-plane vertices out of each file and fitting the plane. Nothing was taken
from the comments. The shipped `.e` files were then checked independently, by
least-squares fitting $z(x)$ over the `fracture_interface` nodeset, and agree with
their journals to 0.001°.

| Journal | sample | $\theta$ | Table 1 | from Table 2 | plane vs $h/2$ | $D$ ok | $L$ ok | |
|---|---|---|---|---|---|---|---|---|
| `ye_ghassemi_2018_SWT1.jou` | SW-T1 | 32.000° | 32° | 32.0° | 0.00 mm | ✔ | ✔ | ✅ |
| `ye2018_sw_t1_mesh.jou` | SW-T1 | 32.000° | 32° | 32.0° | 0.00 mm | ✔ | ✔ | ✅ |
| `ye2018_sw_T1_mesh.jou` (Telegram) | SW-T1 | 32.000° | 32° | 32.0° | 0.00 mm | ✔ | ✔ | ✅ |
| `ye_ghassemi_2018_SWS3.jou` | SW-S3 | 29.000° | 29° | 29.0° | 0.00 mm | ✔ | **✘ 124.40 vs 123.40** | ⚠️ |
| `sw3_mesh_size5.jou` (Telegram) | SW-S3 | 29.000° | 29° | 29.0° | 0.00 mm | ✔ | **✘ 124.40 vs 123.40** | ⚠️ |
| `ye_ghassemi_2018_SWT2.jou` | SW-T2 | **31.000°** | 31° | **30.0°** | 0.00 mm | ✔ | ✔ | ❌ |
| `ye2018_sw_t2_mesh.jou` | SW-T2 | **31.000°** | 31° | **30.0°** | 0.00 mm | ✔ | ✔ | ❌ |
| `ye2018_sw_T2_mesh.jou` (Telegram) | SW-T2 | **31.000°** | 31° | **30.0°** | 0.00 mm | ✔ | ✔ | ❌ |
| `ye2018_sw_s4_mesh.jou` | SW-S4 | **28.990°** | 30° | **30.0°** | **−2.85 mm** | ✔ | ✔ | ❌ |
| `ye_ghassemi_2018_SWS4_size_3_hex27.jou` | SW-S4 | **28.990°** | 30° | **30.0°** | **−2.85 mm** | ✔ | ✔ | ❌ |
| `sw4_mesh_size3_hex27.jou` (Telegram) | SW-S4 | **28.990°** | 30° | **30.0°** | **−2.85 mm** | ✔ | ✔ | ❌ |

(The `final_simulation_runs/` and `final_simulation_runs_v2/` copies of each journal are
byte-identical, so they are listed once.)

### After the fix

The four ❌ journals have been corrected in place in both campaign directories. Re-running
the audit snippet at the bottom of this file now gives:

| Journal | sample | $\theta$ | plane vs $h/2$ | area (m²) |
|---|---|---|---|---|
| `ye2018_sw_s4_mesh.jou` | SW-S4 | 30.000° | 0.00 mm | 4.0075e-3 |
| `ye_ghassemi_2018_SWS4_size_3_hex27.jou` | SW-S4 | 30.000° | 0.00 mm | 4.0075e-3 |
| `ye_ghassemi_2018_SWT2.jou` | SW-T2 | 30.000° | 0.00 mm | 4.0091e-3 |
| `ye2018_sw_t2_mesh.jou` | SW-T2 | 30.000° | 0.00 mm | 4.0091e-3 |
| `ye_ghassemi_2018_SWT1.jou`, `ye2018_sw_t1_mesh.jou` | SW-T1 | 32.000° | 0.00 mm | 3.7827e-3 |
| `ye_ghassemi_2018_SWS3.jou` | SW-S3 | 29.000° | 0.00 mm | 4.1363e-3 |

All 14 journals (7 × 2 directories) now recover their data-derived angle to 0.001°, with
every fracture plane centred on `h/2`, and the two directories remain byte-identical.

**The loose copies under `~/Downloads/Telegram Desktop/` were NOT touched** — they are
outside the repository. `sw4_mesh_size3_hex27.jou` and `ye2018_sw_T2_mesh.jou` there are
still defective. Since this bug reached production precisely by a stale journal being
reused, delete them or replace them from this directory rather than leaving them around.

**Every copy of a given sample's journal carries the same value** — the SW-S4 defect is
in all three variants including the HEX27 one, and the SW-T2 31° is in all three. So
this is a property of the source geometry, not a stray file, and **regenerating must
cover the HEX27 SW-S4 journal too** if that mesh is used.

Two independent defects.

**SW-S4 — a copy-paste from SW-S3.** The plane's z-span in `ye2018_sw_s4_mesh.jou`
is `0.09115854`, bit-identical to the span in `ye_ghassemi_2018_SWS3.jou`. SW-S3
genuinely *is* a 29° specimen, so the plane was copied and only shifted in z. The
shift applied was 5.70 mm, exactly twice the 2.85 mm difference in half-heights, so
the plane ended up both at the wrong angle *and* 2.85 mm below mid-height. Note the
SW-S4 decks already reduce at 30° (`bulk_sin_theta = 0.5`), so the mesh is the
outlier, not the decks.

**SW-T2 — the paper's Table 1 is wrong (or its reduction used 30°).** The recovered
$\tan\theta$ is 0.5771–0.5775 at all eleven stages; $\tan 30° = 0.57735$,
$\tan 31° = 0.60086$. The mesh faithfully reproduces the printed 31°, which is the
problem — the published data it is being compared against was reduced at 30°.

## What it costs, per 1° of error

For a given differential stress $\sigma_d$:

| | 29° | 30° | 31° | 32° |
|---|---|---|---|---|
| $\sin^2\theta$ (→ $\sigma'_n$ deviatoric part) | 0.235040 | 0.250000 | 0.265264 | 0.280814 |
| $\sin\theta\cos\theta$ (→ $\tau$) | 0.424024 | 0.433013 | 0.441474 | 0.449397 |

So SW-S4's mesh gives $\tau$ **2.1% low** and the deviatoric part of $\sigma'_n$
**6.1% low**; SW-T2's gives them 2.0% and 6.1% **high**. Fracture area is off by
3.2% (SW-S4) and 3.4% (SW-T2) in the opposite sense.

Much of this is absorbed by the calibration — `axial_pres_final` was tuned so the
model reproduces the *measured* $\tau$, which simply means it does so at a slightly
different $\sigma_1$ than the real specimen. Since $\sigma_1$ is not one of the
Table 2 observables, the practical damage is smaller than the raw percentages
suggest. **But there is no reason to carry it**: regenerating two meshes costs
minutes, and the production runs have not started.

## Fix

Cubit/Coreform is required (not available in this checkout).

**All four defective journals have been corrected in place** — in both
`final_simulation_runs/meshes/` and `final_simulation_runs_v2/meshes/`, which are
byte-identical. Each carries a header stating what changed and why. Re-running the
audit above now returns the data-derived angle for all 14 journals, with every
fracture plane centred on `h/2`.

```bash
cubit -nographics -batch ye2018_sw_s4_mesh.jou            # SW-S4, set factor 5 then 3
cubit -nographics -batch ye_ghassemi_2018_SWT2.jou        # SW-T2, factor 5
cubit -nographics -batch ye_ghassemi_2018_SWS4_size_3_hex27.jou   # only if HEX27 is used
```

Each journal now names the mesh its size factor produces. Export over
`ye_ghassemi_2018_SWS4_size_5.e`, `ye_ghassemi_2018_SWS4_size_3.e` and
`ye_ghassemi_2018_SWT2_size_5.e`.

**The rebuild was done on 2026-08-06.** `SWS4_size_3`, `SWS4_size_5`, `SWT2_size_3` and
`SWT2_size_5` now fit 30.0000° with the plane centred on `h/2`, verified by least-squares
on the `fracture_interface` nodeset. Still un-rebuilt, and still wrong: `SWS4_size_1`
(28.99°), `SWS4_size_3_hex27`, `SWS4_size_5_hex27` (both 28.99°) and `SWT2_size_1` (31°).
No production deck uses any of those four — rebuild them before one does.

### Deck edits that go with the mesh

Then pin the injection/production coordinates to the mesh. The decks use
`use_closest_node = true`, which searches the **whole** mesh and runs *before*
`fault_split_3d`, so a coordinate that is merely *near* the fracture does not error out —
it silently snaps to whatever node is nearest, and a bulk node can win. The injection
pressure is then imposed inside the matrix, fluid reaches the fracture only through the
5e-19 m² matrix permeability, and the flow rate collapses by orders of magnitude with no
error message.

That is not hypothetical. On the rebuilt `ye_ghassemi_2018_SWS4_size_5.e`, the ideal
borehole point sits 1.734 mm from the nearest **bulk** node and 1.775 mm from the nearest
fracture node. **41 µm** decided it, and the two SW-S4 mesh5 decks lost their injection
point to the matrix.

```bash
/home/geomechanics/miniforge/envs/moose/bin/python snap_source_coords.py          # report
/home/geomechanics/miniforge/envs/moose/bin/python snap_source_coords.py --apply  # write
```

`snap_source_coords.py` reads each deck's own `mesh_file`, finds the nearest node that is
actually a member of `fracture_interface`, and writes that node's coordinates into the deck
verbatim. The snap distance becomes 0 and the distance race disappears. It is idempotent,
and it reports which decks changed *node* (re-gate those) versus which were merely pinned
to the node they already selected (no physics change).

It supersedes `apply_30deg_source_coords.py`, which hard-coded one particular coordinate
move instead of reading the mesh. That script is kept only as the record of the 28.99°/31°
→ 30° move; do not run it.

**Then verify:**

```bash
/home/geomechanics/miniforge/envs/moose/bin/python check_source_nodes.py
```

Two hard failure criteria, and both are needed. *Nodeset membership* catches a real miss —
distance alone cannot, since a legitimate SW-T1 hit was 1.678 mm from the ideal point while
a genuine mismatch was caught 0.363 mm away on the size-3 mesh. *Snap distance* catches a
mesh rebuilt without re-running the pinning, which is now detectable precisely because every
pinned deck reads exactly 0.000 mm.

All nine decks currently pass, confirmed both by this script and independently by
`orca-opt --mesh-only`, which shows `source_in` and `source_out` each resolving to 2 nodes
(the two faces of the split) with every one of them in `fracture_interface`.

### Nodeset naming

The old `ye_ghassemi_2018_SWS4_size_5.e` was the one mesh in the set whose boundary nodesets
were named `top` / `bottom` / `sides`; all thirteen others use `top_nodeset` / `bottom_nodeset`
/ `sides_nodeset`. The rebuild normalised it, which **broke the two decks that read it** —
`SidesetsFromNodeSetsGenerator` aborts with *"Nodeset 'top' does not exist in the input mesh"*.
`SWS4_MC_case67_11_mesh5.i` and `SWS4_BBFast_case67_01_mesh5.i` were updated to the suffixed
names (`nodesets_to_convert` plus 8 `boundary =` lines each). `SWS4_MC_case67_11_mesh3.i`
already used them, because its mesh always had them.

### Both campaigns

`final_simulation_runs/` (30 decks) reads the same rebuilt meshes and had the same two
defects — worse, in fact: its SW-S4 decks still carried the **pre-30°** coordinates, since
only the v2 decks were updated in the earlier pass. Both directories have now been pinned
and renamed, and both pass `check_source_nodes.py` and `orca-opt --check-input` (9/9 and
30/30). The two `meshes/` directories hold byte-identical copies of both scripts, as they
already do for the journals.

Twelve v1 SW-S4 source points changed node and need re-gating; everything else in v1 was a
pin-only rewrite.

### The axial preload — measured, not estimated

`axial_pres_final` was calibrated on the old geometry. The earlier estimate here was that
the corrected angle would leave τ ~2% **high** for SW-S4 and need a −9.84e-5 → −9.68e-5 trim.
That was arithmetic on an assumed axial compliance, and it had the sign wrong.

Gate run, `SWS4_MC_case67_11_mesh5` on the rebuilt mesh, 8 ranks to `t = 300 s`
(the `Pi = 8` MPa hold, Table 2 stage 1):

| quantity | simulated | Table 2 / expected | error |
|---|---|---|---|
| `pp_outlet_pp` | 5.0000 MPa | 5.0000 (Dirichlet) | **exact** |
| `injection_pressure_pp` | 8.0102 MPa | 8.0102 (schedule at t=300) | **exact** |
| `shear_stress_paper_frame_mpa_pp` | 12.384 MPa | 12.56 | **−1.40 %** |
| `effective_normal_paper_frame_mpa_pp` | 30.645 MPa | 30.75 | −0.34 % |
| `hydraulic_aperture_um_pp` | 0.747 µm | 0.74 | +0.9 % |
| `fracture_interface_area_pp` | 3.9939e-3 m² | 4.0075e-3 analytic | −0.34 %, single-sided |
| `czm_shear_slip_mm_pp` | 0.0012 mm | 0.000 | pre-slip creep |

`shear_traction_magnitude_pa` (12.471 MPa) and `shear_stress_paper_frame_mpa_pp` (12.384)
now agree to 0.7%; before the mesh fix they differed by ~2%, and that gap **was** the angle
error. So the mesh, the source nodes, the sideset and the pressure BCs are all confirmed
good.

τ is **1.4% low**, so the trim is roughly `axial_pres_final = -9.84e-5 → -9.98e-5`
(σ_d 28.599 → 29.01). **Do not apply it yet.** The peak-strength envelope and the frame
stiffness (`BACKANALYSIS_2026-08-06_HPC_ALL_SAMPLES.md`, §3 and §7) both move σ_d as well,
and re-gating the preload before those are settled just has to be redone. Gate the preload
last. SW-T2 and the SW-S4 BB/mesh3 decks have not been gated — their targets are SW-T2
τ = 74.87 MPa and, for SW-S4 mesh3, the same 12.56 MPa.

## Verification after regenerating

`AreaPostprocessor` on `fracture_interface` must report

| Sample | expected area (m²) |
|---|---|
| SW-T1 | 3.7827e-3 |
| SW-T2 | 4.0091e-3 |
| SW-S3 | 4.1363e-3 |
| SW-S4 | 4.0075e-3 |

Twice these values means the sideset was doubled by the fault split — see the
`[Mesh]` block comments in any deck.

Also check that `shear_stress_paper_frame_mpa_pp` and
`shear_traction_magnitude_pa * 1e-6` now agree. They should; before the mesh fix
they differ by ~2%, and that gap **is** the angle error.

### The angle can be checked against Table 2 without touching a mesh at all

Added 2026-08-06. The paper's own stress reduction is over-determined: it reports both
σ′_n and τ at eleven stages, and

    σ′_n = (σ₃ − P_p) + σ_d sin²θ        τ = σ_d sin θ cos θ
    ⟹  tan θ = (σ′_n − σ₃ + P_p) / τ ,   P_p = ½(P_i + P_o)

so θ falls out at *every* stage, with no free parameter. Against the rebuilt meshes:

| sample | θ from Table 2 | θ in the mesh |
|---|---|---|
| SW-T1 | 32.00° | 32.000° |
| SW-T2 | 30.00° | 30.000° |
| SW-S3 | 29.03° | 29.000° |
| SW-S4 | 30.02° | 30.000° |

All four inside 0.03°. **Run this before regenerating, not after** — it is what would
have caught the 28.99°/31° journals in the first place, and it needs no solve.
`meshes/frame_stiffness.py` prints the table (θ is a by-product of the compliance
derivation it exists for).

## Not fixed

`ye_ghassemi_2018_SWS3.jou` (and its Telegram copy `sw3_mesh_size5.jou`) builds a
124.40 mm cylinder; Table 1 gives 123.40 mm for SW-S3. A 1 mm (0.8%) length error
affects only the free length between platens, not the fracture plane, the fracture
area, or any Table 2 observable. Left alone deliberately — regenerating would
invalidate the SW-S3 calibration for no measurable gain. Recorded here so it is not
discovered later and mistaken for something worse.

All other diameters and lengths across all thirteen journals match Table 1 exactly.

## Reproducing this audit

```bash
python3 - <<'EOF'
import math, re, glob
for path in sorted(glob.glob('*.jou')):
    txt = [l.split('#')[0] for l in open(path, errors='replace')]
    cyl = [m.groups() for l in txt
           for m in [re.search(r'create\s+Cylinder\s+height\s+(\S+)\s+radius\s+(\S+)', l, re.I)] if m]
    v = [tuple(map(float, m.groups())) for l in txt
         for m in [re.search(r'create\s+vertex\s+location\s+(\S+)\s+(\S+)\s+(\S+)', l, re.I)] if m][:3]
    if not cyl or len(v) < 3:
        continue
    h, r = map(float, cyl[-1])
    (x1,y1,z1),(x2,y2,z2),(x3,y3,z3) = v
    u = (x2-x1, y2-y1, z2-z1); w = (x3-x1, y3-y1, z3-z1)
    n = (u[1]*w[2]-u[2]*w[1], u[2]*w[0]-u[0]*w[2], u[0]*w[1]-u[1]*w[0])
    nn = math.sqrt(sum(c*c for c in n)); n = [c/nn for c in n]
    theta = 90 - math.degrees(math.acos(min(1.0, abs(n[2]))))
    zc = z1 + (n[0]*x1 + n[1]*y1)/n[2]
    print('%-44s theta=%7.3f  centre-h/2=%+6.2f mm  A=%.4e m2'
          % (path, theta, (zc-h/2)*1000, math.pi*(2*r)**2/(4*math.sin(math.radians(theta)))))
EOF
```
