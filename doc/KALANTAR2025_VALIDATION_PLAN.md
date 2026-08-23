# Validating ORCA against Kalantar et al. (2025)

**Paper.** Kalantar, Hofmann, Ji, Blöcher, Muhl, Zang & Deon (2025), *Limits of
Self-Propping in Enhanced Geothermal Systems: New Experimental Insights From Shear,
Tensile and Saw-Cut Fractures in Odenwald Granodiorite*, JGR Solid Earth 130,
e2025JB031938. Open access; data at GFZ Data Services (Kalantar et al., 2025).

**Why this dataset and not another.** It is the same experiment as Ye & Ghassemi
(2018) run on different rock: same triaxial shear-flow cell, same constant-piston-
displacement control (they cite Ye and Ghassemi for it by name), same
`P_p = (P_i + P_o)/2` approximation, same stepwise pressurization then
depressurization, same three-fracture-type design. So the decks transfer almost
verbatim and the *differences* in the result are attributable to rock and fracture
type rather than to protocol. It also adds a fracture type we have never modelled —
a real **shear** fracture — and its headline result is a **negative** one that our
own 104-series predicted from the other direction.

---

## 1. State: what exists in the repo right now

| item | path | status |
|---|---|---|
| Digitized Table 2 (39 hold stages, 3 specimens) | `Examples/Kalantar2025/validation/kalantar2025_table2.csv` | done |
| Figure 8 Pedrosa fits, incl. their reanalysis of our four | `Examples/Kalantar2025/validation/kalantar2025_figure8_pedrosa_fits.csv` | done |
| Parameter audit (runs before any deck) | `scripts/kalantar_parameter_audit.py` | done, 7 sections |
| Cubit journal, OG-SH shear, θ = 29° | `Examples/Kalantar2025/OGSH/mesh/kalantar2025_og_sh_theta29.jou` | done |
| Cubit journal, OG-T tensile, θ = 28° (primary) | `Examples/Kalantar2025/OGT/mesh/kalantar2025_og_t_theta28.jou` | done |
| Cubit journal, OG-T tensile, θ = 26° (sensitivity arm) | `Examples/Kalantar2025/OGT/mesh/kalantar2025_og_t_theta26.jou` | done |
| Cubit journal, OG-SC saw-cut, θ = 30° | `Examples/Kalantar2025/OGSC/mesh/kalantar2025_og_sc_theta30.jou` | done |
| Meshes (`.e`) | `Examples/Kalantar2025/*/mesh/*.e` | **built and verified 2026-08-23** |
| 110-series BBFast decks, round 1 | `Examples/Kalantar2025/*/110_0*.i` | **built, `--check-input` clean** |
| SLURM jobs, 64 ranks / 64 GB / 48 h | `Examples/Kalantar2025/*/110_0*_hpc.sh` | done |
| Gate | `scripts/kalantar_gate.py` | done |
| 111-series MC siblings | — | after round 1 lands |

### 1.1 Mesh verification, 2026-08-23

Built in Cubit, checked with `scripts/check_mesh_geometry.py` and
`scripts/check_source_nodes.py` under the `moose` conda environment.

| mesh | elements | ifc nodes | ifc pitch | L / D / θ | area vs derived | source pinning |
|---|---:|---:|---:|---|---|---|
| `og_sc_theta30_size3` | 68,096 | 2185 | 1.004 mm | 100.00 / 49.98 / 30.000 | 3.923850e-3, exact | OK, 388.5 µm |
| `og_sh_theta29_size3` | 100,048 | 1977 | 1.035 mm | 120.00 / 49.98 / 29.000 | 4.046794e-3, exact | OK, 4.1 µm |
| `og_sh_theta29_size4` | 30,600 | 937 | 1.504 mm | 120.00 / 49.98 / 29.000 | 4.046794e-3, exact | **FAILS — bulk node** |
| `og_t_theta28_size3` | 53,760 | 2297 | 0.980 mm | 100.00 / 49.98 / 28.000 | 4.179007e-3, exact | OK, 792.9 µm |
| `og_t_theta26_size3` | 35,840 | 2297 | 0.992 mm | 104.48 / 49.98 / 26.000 | 4.475488e-3, exact | OK, 849.1 µm |

Every mesh reproduces its journal's derived geometry: plane-fit residual 0.00 µm on
all five, and `fracture_interface` area matching the closed-form `πr²/sin θ` to six
significant figures. All six nodesets present and populated on each.

**The one failure is `og_sh_theta29_size4`.** At 1.504 mm interface pitch, both
borehole coordinates find a *bulk* node 951 µm away while the nearest node actually
on the fracture is 1217 µm away. `use_closest_node = true` would take the bulk node
and inject into the matrix, and the run would complete and be wrong — the exact
failure `source-node-pinning-rule` exists to catch, now caught for the second time.
`og_sh_theta29_size3` pins to 4.1 µm and is the OG-SH production mesh; the journal's
size and export lines have been switched to factor 3 so regenerating cannot
reproduce the bad mesh.

**Snapped coordinates are now in each journal header and must be what the decks
use.** The snap displaces the modelled borehole from the 5 mm design inset, which
lengthens the borehole separation `L`. *(The bias figures first written here were
computed through eq (7)'s log term with the borehole diameter; §3.1 later showed
eq (7) is the wrong reduction and that the argument uses the radius. Under the
cubic law that replaced it, `Q ∝ W/L`, so the bias is just the length change.)*

| mesh | L design → snapped | bias on Q |
|---|---|---:|
| OG-SC | 79.9600 → 80.7369 mm | −0.96 % |
| OG-SH factor 3 | 82.4654 → 82.4736 mm | −0.01 % |
| OG-T 28° | 85.1596 → 86.7453 mm | −1.83 % |
| OG-T 26° | 92.8995 → 92.8995 mm | −1.83 % |

All are below anything this campaign ranks on, but the deck's flow postprocessor
must carry the snapped `L`, not the design value — that is the same class of error
as the 132× flow bug, just two orders of magnitude smaller. Both values are in
every 110-series deck as `paper_flow_width_over_length_*` and
`mesh_flow_width_over_length_*`.
Note the displacements are also smaller than the paper's own hole-centre/hole-edge
ambiguity (1.000 mm), which remains the dominant uncertainty on the flow path.

**Stale duplicate:** `og_sc_theta30_size5.e` has the same node count, element count
and interface pitch as `size3.e` — it is a pre-rename export, not a factor-5 mesh.
Scoring the two against each other would return perfect "mesh convergence" from a
no-op. Rebuild or delete it before any convergence claim. (`og_sc_theta30_size_3.e`
was renamed to `_size3.e` to match the journal's export line.)

---

## 2. The method, and how it has already been applied here

The standing procedure is `doc/back_analysis_method.md`. What follows is not a
restatement of it — it is what each step actually did to *this* paper, so you can
see the shape of the work before committing to it.

### Step 0 — audit the plumbing before believing any physics

Nothing is calibrated until the paper's own numbers have been checked against each
other. A published table is a claim; a published equation set is a second,
independent claim about the same experiment. Run them against each other first.

Concretely, equations (3), (4) and (5) give an identity in which every term is
tabulated:

```
tan θ = (σ'ₙ − σ₃ + P_p) / τ ,    P_p = (P_i + 3)/2 MPa
```

Regressing that over the hold stages recovers θ *and* σ₃ per specimen, with no
input from Table 1 at all. This is exactly the check that caught SW-T2's wrong
angle in the Ye2018 campaign after it had already been meshed and run for months.

**It fired again.** `scripts/kalantar_parameter_audit.py` §1:

| specimen | Table 1 θ | recovered θ | recovered σ₃ | max residual |
|---|---:|---:|---:|---:|
| OG-SH | 29.0° | **29.006°** | 32.996 MPa | 0.004 MPa |
| OG-SC | 30.0° | **29.998°** | 33.002 MPa | 0.006 MPa |
| OG-T | 28.0° | **25.999°** | 33.001 MPa | 0.007 MPa |

Two specimens reproduce their printed angle to 0.006°, so the method is sound and
OG-T is the anomaly. A residual of 0.007 MPa across seventeen stages whose τ spans
19.4–63.2 MPa means two constants regenerate the *entire* stress table — a
recovery, not a fit. Forcing θ = 28° leaves a systematic 0.85–2.78 MPa residual
that no constant σ₃ and no constant P_o can absorb; both were tested and both fail.

Two further things fell out of the same step:

- **σ₃ = 33.00 MPa on all three**, not the 30 MPa the text foregrounds. 30 MPa is
  the *effective* confining pressure; the deck's boundary condition must carry 33.
  Getting this wrong is a 10 % error in the clamping stress on every stage.
- **OG-T's 26° is geometrically impossible.** A through-going elliptical fracture at
  angle θ needs 2r·cot θ of axial extent: 93.999 mm at 28° (fits the 100.00 mm core,
  3.00 mm clearance per end) and 102.474 mm at 26° (overruns each end by 1.24 mm).
  Table 1 is internally consistent; Table 2's reduction is not. So the specimen is
  28° and **the published OG-T stress columns are in the wrong frame**.

§6 of the audit prints the re-reduction. τ scales by a constant 1.0521 (+5.21 %,
peak 63.21 → 66.50 MPa); σ'ₙ does *not* scale by a constant, because only its
deviatoric part moves. The fitted criterion τ = 1.1 σ'ₙ was itself fitted in the
26° frame and has to be refitted before it can set a critical stress state.

### Step 1 — know which columns are independent, before scoring anything

Table 2 prints six quantities per stage. It does not contain six measurements.

- `k` is computed from `Q` through eq (7), and `a_h = √(12k)` from `k`. **One
  channel.** The audit checks the arithmetic: `a_h = √(12k)` reproduces the printed
  `a_h` to a median 1.0 % on OG-SH but 8–9 % on the other two, because `k` is
  printed to two decimals and OG-T's `k` never exceeds 0.10 D. Where they disagree,
  `a_h` is the better-resolved statement — score against `a_h` and `Q`, not `k`.
- `σ'ₙ` and `τ` are both affine in σ₁ once θ and σ₃ are fixed. **One channel.**
  Step 0 *is* the proof: two constants regenerate the whole σ'ₙ column from τ.

- `ΔL_s` is **not** a third channel either. **CORRECTED 2026-08-23.** The rig runs
  at constant piston displacement, so eq (6) with `ΔL = 0` plus eq (4) gives an
  algebraic identity, not a correlation:

      ΔL_s = −A·Δτ / (K_sys sinθ cosθ)

  Checked against Table 2 (predicted vs fitted slope): OG-T 0.9999 at r = −1.0000,
  OG-SC 0.9962, OG-SH 1.0416 — the last inside its own 1 µm print resolution. So
  the slip column is a readout of the same force. **One channel.**

So there are **two independent observables per stage**: a flow rate and a force.
Reporting six error percentages would count the same defect three times — the same
correction the Ye2018 campaign had to make when it found `Q` was not independent of
aperture. `scripts/kalantar_gate.py` scores one force channel and one flow channel
and prints the rest as diagnostics.

`ΔL_s` in particular is a **frame** check, not a physics check: with
`axial_bc_penalty` set to `K_sys/A`, any deck that gets τ(t) right gets `ΔL_s(t)`
free. The expected slope is 0.1720 / 0.1682 / 0.1757 MPa/µm; a deviation there means
the penalty is wrong, not the joint law. And `ΔL_s` is axial *shortening*
(`= δ cosθ`), so comparing it to an in-plane slip carries 1/cosθ = 1.1434 / 1.1326 /
1.1547.

Note what is *missing* relative to Ye2018: **there is no normal-displacement
column.** Ye2018's `d_n` was the only direct mechanical constraint on the aperture
law. Here the aperture is visible only through `Q`. That is a real loss of
identifiability and it should be stated in the paper rather than discovered during
calibration — the normal-closure constants will be far less determined here.

### Step 2 — build the geometry from the recovered constants, not the printed ones

That is what the four journals do, and why each header carries its own derivation
rather than a bare vertex list. Every one also lists the intended borehole
coordinates and tells you to re-pin them against the exported mesh with
`scripts/check_source_nodes.py`, because `use_closest_node = true` snaps silently —
including onto a bulk node off the fracture entirely, which cost this project a
month once.

One ambiguity I could not resolve from the paper: §2.3 puts the boreholes "5 mm
from the sidewall" for a 2 mm diameter hole, which could mean the centre or the
near edge. The journals assume the centre. If it is the edge, the flow path length
changes by ~5 % and `Q` moves with it. Worth settling from the GFZ data release
before calibrating.

### Step 3 — localise the error in the load path before touching a knob

Not "the model is 8 % off" but "*which stage* is it off at, and is that a level
error or a slope error". The audit's §5 already does the experimental half:

| specimen | total slip | largest single step | when |
|---|---:|---|---|
| OG-SH | 42.0 µm | 11.0 µm (26 %) | stage 4, P_i = 15 MPa |
| OG-T | 275.0 µm | 139.0 µm (51 %) | stage 8, P_i = 27 MPa |
| OG-SC | 22.0 µm | 19.0 µm (86 %) | stage 7, P_i = 24 MPa |

Three different slip styles in one paper: OG-SH creeps through every stage, OG-SC
does essentially everything in one burst, OG-T is in between. That is the axis this
dataset is *for*, and it is also where the Ye2018 campaign's known weakness lives —
`sws4-slips-on-ramps-not-holds`: a slip-weakening law keeps sliding through a hold
because it has no dependence on dσ'ₙ/dt. **OG-SH is the specimen that will expose
that most sharply**, because its slip is distributed across five holds.

### Step 4 — price the knob before building the deck

Before running anything, ask what the parameter would have to be worth to close the
gap, and whether it can get there. The Ye2018 campaign twice found a knob that was
already exhausted (`ye2018-loading-path-cannot-identify-jrc`,
`exhausted-knob-vs-unfinished-sweep`), and once found a knob with a floor in the
middle of its range rather than at an end (the SW-T1 `V_m` result, §3(a) of
`FINAL_DECK_SELECTION.md`). Half an hour of algebra saves a 48-hour HPC job.

For this paper the first thing to price is the **roughness channel**, and the answer
is already visible. The paper propagates the scanner's 0.012 mm resolution to
**±2.10 in JRC** and concludes:

| specimen | JRC before | after | change | resolvable? |
|---|---:|---:|---:|---|
| OG-SH | 15.60 | 15.21 | −0.39 | no |
| OG-T | 12.10 | 11.81 | −0.29 | no |
| OG-SC | 4.23 | 1.36 | **−2.87** | **yes** |

So **OG-SC is the only specimen in the paper where a JRC-degradation law has an
observable to fit** — and the change is a smoothing of an already-smooth saw cut.
This independently reproduces the campaign's own finding that JRC mobilization is
inert on this loading path.

### Step 5 — design the experiment so it can fail, and write the prediction into the deck header

Every mechanism deck states in its header what result would falsify the hypothesis,
*before* it runs. The 103-series is the worked example: it predicted that dropping
the slip-weakening exponent alone would move each BBFast deck onto its
Mohr–Coulomb pair, named the falsifier, and the falsifier fired on SW-S3 — which is
how we learned the MC/BBFast gap is not monocausal. A prediction written after the
fact is not a prediction.

### Step 6 — record the negative results

Including your own errors, in the file, at the size they actually were. The
`nonmonotonic-window-matched-state-bug` write-up exists because a metric that had
already reached the manuscript was wrong; the correction strengthened the argument
it broke.

---

## 3. The plan

**Series numbering** continues the existing scheme, so nothing collides with the
Ye2018 93–104 series. Use **110-series** for Kalantar.

| step | what | depends on |
|---|---|---|
| **A** | Build 6 meshes in Cubit: 3 specimens × factors 5 and 3. Export under the names in each journal. | you |
| **B** | Run `scripts/check_source_nodes.py` on each; write the exact interface-node coordinates back into the journals' header blocks. | A |
| **C** | ~~Derive the flow geometry factor for eq (7)~~ — **done 2026-08-23, and it inverted: see §3.1. Eq (7) as printed is wrong; the Ye2018 cubic form transfers unchanged.** | done |
| **D** | ~~Port the injection schedule~~ — **done**, generated in `scripts/build_110_kalantar_decks.py` and asserted against Table 2's stage counts (5/4, 9/8, 7/6). | done |
| **E** | ~~Build a `kalantar_gate.py`~~ — **done**, `scripts/kalantar_gate.py`. Reuses `table2_gate`'s stage walking; scores σ'ₙ, τ, a_h, ΔL_s always and Q only where Table 2 resolves it; re-reduces OG-T to 28°. | done |
| **F** | 110-series BBFast decks — **round 1 built and `--check-input` clean** (`110_01` OG-SH, `110_03` OG-T, `110_05` OG-SC) with SLURM at 64 ranks / 64 GB / 48 h. Uncalibrated by design. 111-series MC siblings still to come, after round 1 lands. | partly |
| **G** | Mechanism decks, chosen after F lands. The obvious first one is the gouge arm on OG-SH — see §4. | F |

### 3.1 Step C, resolved — and it inverted

Read off page 6 of the PDF, eq (7) is

```
k = ∛{ [ (Qη/ΔP) · ln(2L/r − 1) / (Bπ) ]² } / 12,    B = 2/(π·tan⁻¹(2n)),  n = b/a
```

with `a_h = √(12k)`, which collapses to **`a_h³ = (Qη/ΔP)·ln(2L/r − 1)·tan⁻¹(2n)/2`**.
Note `r` is the borehole *radius*, not the 2 mm diameter — an earlier note in this
file had that wrong, worth 16 % in `a_h³`.

Dimensionally the equation is sound. **It does not reproduce the paper's own Table 2.**
Table 2 prints `Q` and `a_h` for the same 39 stages, so the reduction is checkable
against itself, and eq (7) misses by a **constant factor of 2.17 in `a_h`, 10.3 in
`a_h³`**, with 0.12 % scatter across OG-SH's nine stages. The constancy is the whole
argument: the functional form (`a_h³ ∝ Q/ΔP`) is right and a numerical factor is
wrong. It cannot be rescued through `n` — matching Table 2 would need `B = 0.0807`,
and `B = 2/(π·tan⁻¹(2n))` has a floor of 0.5750 at `n = 1`.

What *does* reproduce Table 2 is the plain cubic law this project already uses:

```
a_h³ = (Qη/ΔP) · 12 · L / W
```

with `W` the fracture's short axis (the core diameter, transverse to the flow) and
`L` the in-plane borehole separation — **no fitted constant, both from Table 1 and
§2.3**. It lands within 0.54 % with 0.12 % scatter on OG-SH.

| specimen | eq (7) pred/printed | cubic pred/printed | stages |
|---|---|---|---:|
| OG-SH | 0.4603 ± 0.0005 | **0.9946 ± 0.0012** | 9 |
| OG-T | 0.4459 ± 0.0131 | 0.9786 ± 0.0287 | 8 |
| OG-SC | 0.4901 ± 0.0306 | 1.0434 ± 0.0651 | 12 |

OG-SH decides it. Its flow rates span 0.46–3.61 mL/min printed to three decimals,
so every stage carries 3+ significant figures. OG-T and OG-SC ran one to two orders
of magnitude slower — OG-T's Table 2 contains 0.000, 0.001 and 0.002 mL/min — so
most of their stages sit at the printing floor, where `a_h ∝ Q^⅓` inherits several
per cent from rounding alone. Stages below 0.010 mL/min are excluded above. **This
also reorders the channels: on OG-T and OG-SC, `a_h` is the highest-precision
column and `Q` and `k` are the degraded ones — the opposite of Ye2018.**

**So the flow operator transfers.** Keep `(W/L)/12` and set `W/L` per specimen:

| specimen | W (mm) | L (mm) | paper-frame W/L | mesh-frame W/L (snapped) |
|---|---:|---:|---:|---:|
| OG-SH | 49.98 | 82.4654 | 0.60607 | 0.60602 |
| OG-T 28° | 49.98 | 85.1596 | 0.58690 | 0.57616 |
| OG-T 26° | 49.98 | 92.8995 | 0.53800 | 0.53800 |
| OG-SC | 49.98 | 79.9600 | 0.62506 | 0.61905 |

Both go in each deck, exactly as the 93-series carries
`paper_flow_width_over_length_*` and `mesh_flow_width_over_length_*`.

This is the third defect the audit-first rule has found in this paper, after the
OG-T angle and the σ₃ = 33 MPa prose. It is worth reporting: anyone reducing new
data with eq (7) as printed will be an order of magnitude out.

**Resourcing.** These specimens are smaller than the Ye2018 ones (49.98 mm × 100–120
mm vs 50.5 mm × 118–132 mm) and OG-SH has the longest schedule. Start at the
mesh-5 Ye2018 numbers — 32 ranks, 32 G, 24 h — and generate the scripts through
`scripts/set_hpc_resources.retarget` so `--ntasks` and `srun -n` cannot drift apart.

---

## 4. What this paper gives your Ye2018 manuscript

This is the part worth reading even if the validation never runs.

### 4.1 It independently reanalyses your four specimens

Figure 8 fits Pedrosa's `k = k₀ exp(−α σ'ₙ)` to the pre-slip and post-slip branches
of **SW-T1, SW-T2, SW-S3 and SW-S4** as well as its own samples. That is a
published, third-party, two-number summary of the same data your decks are
calibrated to:

| source | specimen | k₀ pre → post (D) | ratio | α pre → post (1/MPa) |
|---|---|---|---:|---|
| Ye2018 | SW-T1 | 0.37 → 3.47 | **9.38** | 0.01 → 0.03 |
| Kalantar | OG-SC | 0.82 → 5.25 | 6.40 | 0.05 → 0.11 |
| Ye2018 | SW-T2 | 0.83 → 3.04 | 3.66 | 0.01 → 0.02 |
| Ye2018 | SW-S3 | 0.16 → 0.41 | 2.56 | 0.01 → 0.02 |
| Kalantar | OG-T | 1.91 → 4.73 | 2.48 | 0.08 → 0.16 |
| Ye2018 | SW-S4 | 0.12 → 0.20 | **1.67** | 0.03 → 0.06 |

Two things to take from it, and one not to.

**Take:** the ordering of the enhancement across your four specimens —
SW-T1 ≫ SW-T2 > SW-S3 > SW-S4 — puts SW-T1 highest and **SW-S4 lowest**, which is
the same extreme ordering your 101-series retained-permeability metric produces
(1.605 / 1.450 / 1.497 / 0.893). The two middle specimens swap, and with n = 4 a
Spearman ρ of 0.8 is consistency rather than evidence — say it that way. But
**SW-S4 being the outlier is now corroborated by a second group using a different
metric on the same raw data**, and that is worth a sentence in §6.7.

**Take:** SW-S4 has the highest α of your four, before and after slip (0.03 → 0.06
against 0.01 → 0.02 for the others). Kalantar's own explanation for why post-slip
permeability is not retained is a high stress-sensitivity coefficient. That is the
same physical statement as your finding that SW-S4's aperture budget is dominated
by gouge fill — from an independent direction.

**Do not take:** "α doubles universally after slip." It does increase in all six,
by a factor of 2.0–3.0. But four of the six pairs are quoted to one significant
figure at values of 0.01–0.08, so 0.01 → 0.02 is the coarsest ratio the precision
can express, and the apparent constancy is inside the quoting precision. This is
precisely the shape of the Table-12 error — a clean-looking regularity that is an
artifact of how the numbers were written down.

### 4.2 It confirms your gouge mechanism, from the opposite direction

Your 104-series arm 1 established computationally that gouge fill can push retained
permeability *below* 1.0, and that SW-S4 is the only one of the four where it does,
because its baseline aperture is 40 % smaller so the same absolute wear is 34 % of
budget instead of 25 %.

Kalantar's headline result is that same mechanism running to completion in an
experiment: **OG-SH's permeability falls monotonically during pressurization**,
2.03 → 1.61 D, while injection pressure rises and effective normal stress falls —
the opposite of what elastic opening predicts. Their §4.3 and Figure 9 attribute it
to progressive asperity breakage feeding gouge into the flow paths, and they weigh
it: 1.20 g of gouge from OG-SH against 0.10 g from OG-T, a 12× difference, with
XRD confirming the fines are biotite-rich.

So your model predicted the sign, and this experiment shows the regime where the
sign dominates the whole result. That is a much stronger claim than "our model
reproduces four calibration curves."

### 4.3 It puts a measured number on your most leveraged inferred constant

`ye2018-frame-stiffness-dominates-magnitudes` records that the loading-frame
stiffness is a *derived* constant whose ×2 bracket moves `Q` by −93.9 %/+408 %, and
you had to infer 0.94 MPa/µm from a single scored run under a series-spring
assumption. Kalantar **measures** theirs: `K_sys ≈ 796 kN/mm`, which over the
49.98 mm specimen cross-section is **0.406 MPa/µm** (audit §7).

Different machine, so this is not a calibration. But it is the first independent
evidence that the inferred value is in the right decade, and it lands within a
factor of 2.32 — inside the bracket you already ran. That converts "we inferred a
constant that dominates everything" into "we inferred a constant that dominates
everything, and an independently measured value for a comparable apparatus agrees
to within the bracket we tested." Much better to defend.

### 4.4 It supplies the rock-property axis your four specimens could not

Ye2018's four specimens are one granite. Kalantar contrasts it explicitly with
granodiorite: quartz 43.5 % vs ~15 %, mean grain size 0.5 mm vs ~5 mm, at
comparable E (67 vs 63 GPa), UCS (150 vs 153 MPa) and tensile strength (11 MPa,
identical). Their argument is that less quartz and coarser grains make the rock more
deformable, which raises α and lowers post-slip friction.

That gives you a mechanistic axis — **composition → deformability → stress
sensitivity → self-propping retention** — with the confounds already controlled,
because the elastic moduli and strengths are nearly the same. Your model expresses
that axis through the aperture-law compliance, so it is a testable prediction
rather than a narrative.

### 4.5 It is a citable negative result for the framing of your discussion

The paper's conclusion is that self-propping "is limited under the investigated
boundary conditions" for this rock, and that all three fracture types lose their
enhancement on depressurization. Your §6.7/§6.9 already argues that retained
enhancement is *uncorrelated* with the roughness parameters that are supposed to
predict it. A 2025 JGR paper concluding independently that self-propping does not
deliver is the strongest possible support for that section, and it moves your
cautionary conclusion from "our model suggests" to "our model and an independent
experiment agree."

### 4.6 Smaller things worth a line each

- **OG-SC shows eight stress drops during loading** (Fig. 3e) — stick-slip on a
  saw cut, the same signature as SW-S4's staircase. A second dataset with the
  behaviour your slip-weakening law cannot reproduce strengthens the case that it
  is a model-form limit, not a calibration failure.
- **JRC changes are within measurement error on two of three specimens** — an
  independent statement of `ye2018-loading-path-cannot-identify-jrc`.
- **They flag single-specimen reproducibility as a limitation** ("one representative
  experiment per fracture type", shear fractures hardest to reproduce). Cite it when
  you discuss how much of your residual is specimen-specific.

---

## 5. Decisions that are yours

1. **OG-T's angle.** I have built 28° as primary and 26° as a sensitivity arm, with
   the full argument in the journal headers. My recommendation is 28° with the
   published stress columns re-reduced (audit §6), because 26° cannot be realised
   without contradicting a measured dimension. If you would rather run 26° as
   primary, the arm is ready — but note it needs a 4.5 % longer core, which changes
   the axial compliance of a system whose frame stiffness we know dominates.
2. **Whether the 5 mm borehole inset is to the hole centre or its edge.** A ~5 %
   flow-path-length difference; resolvable from the GFZ data release.
3. **Whether to publish the OG-T angle discrepancy.** It is a genuine, checkable
   error in a 2025 JGR paper, found by the same method that found SW-T2's. Reporting
   it makes your audit method itself a contribution — you would have caught the same
   class of error twice in two independent datasets.
