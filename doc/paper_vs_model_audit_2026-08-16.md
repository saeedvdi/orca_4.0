# Audit of the model against the source paper — 2026-08-16

Scope: every physical property in the four production decks, the two meshes, and the
two long-form documents (`paper_draft_ye_ghassemi_validation.md`,
`orca_czm_theory.md`), checked against Ye & Ghassemi (2018), *JGR Solid Earth*
**123**, 9009–9032, read directly from the PDF.

This is a different question from the one
`sample_parameter_unification_2026-08-16.md` asked yesterday. That audit compared
the four decks **to each other**, which finds drift but is blind to a value that is
consistently wrong in all four. This one compares each deck **to the paper**.

Reproduce with:

```bash
python3 scripts/paper_parameter_audit.py
```

The script carries Tables 1–3 and Sec. 2.1/2.4/2.5 transcribed from the PDF, and
re-reads the decks at run time so the transcription cannot go stale.

**No source file was modified.** Every finding below sits in a deck, a mesh
journal, or a document — not in `src/` or `include/`. The one code-level finding
(§4) is a scope error in the *manuscript's description* of the code, not a defect
in the code.

---

## 1. What is correct

Worth stating first, because most of it is.

| Quantity | Paper | Decks | |
|---|---|---|---|
| Young's modulus | 67 GPa (Sec. 2.1) | 67e9, all four | ✅ |
| Poisson's ratio | 0.32 | 0.32, all four | ✅ |
| Matrix permeability | 5e-19 – 1e-18 m² | 5e-19 (low end) | ✅ |
| Confining pressure | 30 MPa, all samples | 30e6, all four | ✅ |
| Production pressure | 5 MPa held | 5e6 Dirichlet | ✅ |
| Fluid viscosity | 1.002e-3 Pa·s at 20 °C | 1.002e-3 | ✅ |
| Injection protocol | 5→28→8 MPa, 11 holds | digitized `PiecewiseLinear` | ✅ |
| JRC, SW-T1 / SW-T2 | 15.32 / 14.63 | 15.32 / 14.63 | ✅ |
| JCS, SW-T1 / SW-T2 | UCS = 150 MPa | 1.5e8 | ✅ |
| Dilation angle, SW-T1 / SW-T2 | 16.44° / 13.97° from Table 2 | 16.442 / 13.965 | ✅ exact |
| Specimen L, D — T1, T2, S4 | Table 1 | mesh journals | ✅ |
| Flow geometry factor *W/L* | back-solves from Table 2 eq (9) | 0.814 / 0.813 / 0.81 / 0.81 | ✅ to 0.5 % |

The *W/L* check is worth singling out. Inverting the paper's own eq (9) on its own
tabulated $Q$, $a_h$ and $\Delta P$ returns the geometry factor each deck already
uses, to better than 0.5 % on all four samples. That derivation is sound and the
manuscript's Appendix A.3 can cite it as verified.

The normal-closure law in `include/utils/OrcaNormalClosure.h` was checked
line-by-line against the theory manual's Chapter "Nonlinear normal closure":
$\sigma_n = (K_{ni}V_m)[c/(V_m-c)]^{1/p}$, its tangent, the $f_{\max}V_m$ cap, and
the $\min(10^{-9}, 0.01V_m)$ linearisation threshold all match the code exactly.
The manual is right here.

---

## 2. The saw-cut joint constants are not the paper's

This is the largest finding and it is confined to SW-S3 and SW-S4.

| | JRC deck | JRC paper | ratio | JCS deck | UCS paper | $\phi_r$ deck |
|---|---|---|---|---|---|---|
| SW-T1 | 15.32 | 15.32 | 1.00 | 150 MPa | 150 MPa | 44.10° |
| SW-T2 | 14.63 | 14.63 | 1.00 | 150 MPa | 150 MPa | 46.29° |
| SW-S3 | **23.35** | **1.96** | **11.9×** | **300 MPa** | 150 MPa | **8.45°** |
| SW-S4 | **17.50** | **1.19** | **14.7×** | **300 MPa** | 150 MPa | **7.50°** |

SW-S3's JRC of 23.35 is not merely wrong; it is outside Barton's 0–20 scale
altogether. Both saw cuts then carry a $\phi_r$ below 8.5° to compensate — no
granite joint has a basic friction angle below about 25°, and the paper's own
intact-rock value is 46°.

The three errors are not independent: they cancel at the calibration point. Both
samples reproduce their measured peak $\tau$. What does *not* survive the
cancellation is the **stress sensitivity of the envelope**, which is the one
property this experiment exists to probe, because injection sweeps $\sigma'_n$
downward by a factor of two.

Fixing $\phi_r$ so the envelope still passes through each specimen's last stick
stage, but using the paper's JRC and JCS = UCS:

| sample | onset stage | $\sigma'_n$ | $\tau$ | $\mu$ | $\phi_r$ required | verdict |
|---|---|---|---|---|---|---|
| SW-S3 | $P_i$ = 24 MPa | 23.42 | 14.26 | 0.609 | **29.76°** | textbook granite basic friction |
| SW-S4 | $P_i$ = 16 MPa | 26.51 | 12.14 | 0.458 | **23.71°** | low but defensible for a lapped surface |
| SW-T1 | $P_i$ = 24 MPa | 56.94 | 66.32 | 1.165 | 42.91° | above any measured granite value |
| SW-T2 | $P_i$ = 24 MPa | 57.88 | 73.40 | 1.268 | 45.69° | above any measured granite value |

The saw cuts land on physically ordinary numbers as soon as the paper's own
roughness constants are used. That is a strong indication the paper's JRC values
are right and the decks' are a substitution made for fitting convenience.

Consequence, evaluated at each specimen's own onset stress:

| sample | $\mu$ deck | $\mu$ paper | $\mathrm{d}\tau/\mathrm{d}\sigma'_n$ deck | $\mathrm{d}\tau/\mathrm{d}\sigma'_n$ paper | error |
|---|---|---|---|---|---|
| SW-T1 | 1.215 | 1.165 | 0.927 | 0.891 | +4 % |
| SW-T2 | 1.296 | 1.268 | 0.999 | 0.979 | +2 % |
| SW-S3 | 0.682 | 0.609 | **0.423** | **0.589** | **−28 %** |
| SW-S4 | 0.486 | 0.458 | **0.322** | **0.447** | **−28 %** |

Both saw cuts run an envelope 28 % too flat. SW-S4 is the specimen the manuscript
calls "the discriminating case" (§2.4), so this lands on the paper's central claim.

### 2.1 The tensile pair is a different problem, and it is not a parameter error

SW-T1 and SW-T2 already use the paper's JRC and JCS. Their $\phi_r$ of 44–46° is
still not a basic friction angle — but no adjustment of JRC or JCS can fix it,
because the requirement comes from the data: both specimens sustain
$\mu = \tau/\sigma'_n$ of 1.17–1.27 in the **stick** state, before any slip.

That is a real property of a perfectly mated Mode-I fracture, and the model has
nowhere to put it: `computeCohesionEffective()` returns a hard-coded `0.0`, with no
input parameter and no subclass override. The interlock of a conjugate tensile
surface must therefore be carried by $\phi_r$. Note that SW-T2's 46.29° is
essentially the paper's **intact-rock** friction angle of 46°, which is the
physically honest reading: an unsheared mated tensile fracture is closer to intact
rock than to a frictional joint.

This should be *stated* in the manuscript, not silently carried in a parameter whose
name says something else.

---

## 3. Geometry: two meshes disagree with the paper, and the fixes exist elsewhere

The fracture angle is recoverable from Table 2 alone, independently of Table 1.
Dividing eq (3) by eq (4) removes the unknown $\sigma_d$:

$$\tan\theta = \frac{\sigma'_n - \sigma_3 + P_p}{\tau}$$

Run over all eleven hold stages of all four samples (`section_theta_recovery` in
the audit script):

| sample | θ from Table 2 (median) | Table 1 | mesh as built | plane centred |
|---|---|---|---|---|
| SW-T1 | 32.000° | 32° | 32.000° | ✅ |
| SW-T2 | **30.001°** | **31°** | **31.000°** | ✅ |
| SW-S3 | 29.028° | 29° | 29.000° | ✅ |
| SW-S4 | 30.020° | 30° | **28.990°** | ❌ **−2.85 mm off centre** |

Two independent problems:

- **SW-T2** — Table 1 prints 31°, but the data was reduced at 30°, reproduced at
  every one of the eleven stages to four digits. The mesh faithfully reproduces the
  *printed* value, which is the wrong one to reproduce: it puts the model on a
  stress path the published numbers were never on.
- **SW-S4** — the journal is a copy of SW-S3's with only the cylinder changed. The
  fracture-plane $z$-span is bit-identical between the two files
  (`0.09115854`), so SW-S4 inherited SW-S3's 29° plane *and* a 2.85 mm centring
  error.

Cost at fixed $\sigma_d$: $\tau$ 2.1 % low on SW-S4 and 2.0 % high on SW-T2; the
deviatoric part of $\sigma'_n$ 6.0 % low and high respectively.

Also: **SW-S3's mesh is 124.40 mm long against a published 123.40 mm** (+0.81 %).
This one is wrong in every journal on the machine and is also wrong in the
manuscript draft's Table 1.

### 3.1 The corrections were already made — in a different repository

`orca_3.0_claude_edit/Examples/YeGhasemmi2018/final_simulation_runs_v3/meshes/` and
`.../v4/meshes/` contain corrected journals (SW-S4 and SW-T2 both at 30.000°,
both centred) together with a `README_fracture_angle.md` recording the audit.
**They were never ported to `orca_4.0`, which is the repository the production
decks run from.** Verified by re-running the plane fit over every journal in both
trees:

```
orca_4.0        SWS4/mesh/ye2018_sw_s4_mesh.jou    th=28.990  centre-h/2=-2.85 mm
orca_4.0        SWT2/mesh/ye2018_sw_T2_mesh.jou    th=31.000  centre-h/2=+0.00 mm
claude_edit v3  meshes/ye2018_sw_s4_mesh.jou       th=30.000  centre-h/2=-0.00 mm
claude_edit v3  meshes/ye2018_sw_t2_mesh.jou       th=30.000  centre-h/2=-0.00 mm
```

Porting them invalidates every SW-S4 and SW-T2 result currently on disk, so it is
a campaign decision, not a cleanup. It is not done here.

---

## 4. The manuscript claims a dissipation bound the validated model does not have

This is the correctness problem in the two documents, and it is the one worth
acting on first because it affects a claimed contribution rather than a number.

Manuscript §1 contribution 1, §3.5.3, figure F2b and §3.8 all present the dilation
dissipation inequality

$$p_c\,\Delta g_n^{p} \le (1-\epsilon_D)\,Y\,\Delta\gamma \iff \tan\psi \le (1-\epsilon_D)\mu$$

as a distinguishing feature of the model, and state that "this bound is frequently
the active constraint".

`dissipation_margin` is declared in exactly one material:

```
src/InterfaceMaterial/ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile.C
include/InterfaceMaterial/ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile.h
```

All four production decks use `OrcaBartonBandisContactTractionFastADHardening`,
which has no dissipation bound at all — it clamps $\psi$ between
`min_dilation_angle_degrees` and `max_dilation_angle_degrees`, and neither is set in
any of the four decks. The only decks that actually set `dissipation_margin` are the
**Mohr–Coulomb baselines** `67_11` (SW-S4) and `83_11` (SW-S3), which do use the
CompressionTensile material. SW-S3's BBFast decks mention `dissipation_margin` only
in comments, one of which reads `# UNUSED after PST swap`.

So the bound lives exclusively in the law that §0.2 item 4 explicitly demotes to
"a baseline, not a coequal candidate". As written, the manuscript claims as a
contribution of the validated model a mechanism present only in its control.

Two honest ways out, both fine:

1. Keep the material, and say plainly that §3.5.2's roughness-interpolated
   Mohr–Coulomb *and* §3.5.3's flow rule and dissipation bound describe the
   baseline law, while Barton–Bandis carries a mobilisation/decay dilation law with
   angle clamps. §3.5 currently reads as one unified model; it is two.
2. Drop the bound from the contribution list and keep it as a §3.8-style remark on
   admissible limiters.

Either way the sentence "we show this bound is frequently the active constraint"
cannot stand for the BBFast runs, because it is never evaluated in them.

### 4.1 What the bound *would* say, and why it is a real physical result

The bound is not idle even though it is inactive — it explains a discrepancy that
otherwise looks like a calibration miss.

| sample | $\psi$ implied by Table 2 | $\psi$ in deck | $\arctan\mu$ at onset | |
|---|---|---|---|---|
| SW-T1 | 16.44° | 16.44° | 49.35° | comfortable |
| SW-T2 | 13.97° | 13.97° | 51.74° | comfortable |
| SW-S3 | **31.79°** | 26.00° | **31.34°** | Table 2 **exceeds** the bound |
| SW-S4 | **28.66°** | 24.00° | **24.60°** | Table 2 **exceeds** the bound |

On both saw cuts, the dilation angle implied by $\arctan(|d_n|/d_s)$ from Table 2
is *larger than* $\arctan\mu$. Taken at face value that is thermodynamically
inadmissible: the joint would do more work opening against the normal stress than
friction supplies. The decks avoid it by setting $\psi$ below the Table-2 value
(26° and 24°), which is why the saw cuts under-predict dilation.

The physical reading is better than the numerical one, and it is already implicit
in the manuscript's own §2.3.1 table: on a saw cut the measured $d_n$ is **not**
pure shear dilation. It contains process (ii), elastic decompression of the joint
as $\sigma'_n$ falls. Attributing all of $d_n$ to process (iv) is what forces
$\psi > \arctan\mu$. A tensile fracture with $\mu > 1$ has enough headroom for the
distinction not to matter; a saw cut with $\mu \approx 0.46$ does not.

This converts an apparent calibration failure into a statement about what the
measurement contains — which is exactly the kind of result §6 should carry.

---

## 5. Smaller items

- **`fluid_bulk_modulus = 4.7836e9 Pa`**, all four decks — 2.17× water at 20 °C
  (2.2e9). It enters $1/M = (\alpha-\phi)/K_s + \phi/K_f$, so with $\phi = 10^{-3}$
  the matrix storage error is negligible; the same value is handed to the fracture
  fluid, where storage is not negligible during the burst. Not reported by the paper,
  so this is a modelling choice, but 4.78 GPa is not defensible as "water".
- **`initial_porosity = 0.001`** — not reported by the paper. Granite matrix
  porosity is normally 0.005–0.01. A model choice; should appear in Table 4 as
  *assumed*, not *measured*.
- **`biot_coefficient = 0.6`** — not reported by the paper. Literature value.
  Same treatment.
- **SW-S3 `axial_pres_final` carries a stale derivation comment** — `# E=75 GPa;
  preserves the 31 MPa preload` at line 755, while `youngs_modulus` on line 798 is
  now `67e9`. The constant was computed for the old modulus and the preload it
  produces has not been re-gated since. Worth re-running the preload gate.
- **SW-S4 reports the interface traction where the other three report the
  paper-frame reduction.** SW-T1, SW-T2 and SW-S3 all carry
  `effective_normal_paper_frame_mpa_pp` implementing eq (3) with
  $P_p = \tfrac12(P_i+P_o)$; SW-S4 has no such postprocessor and compares
  `bb_effective_normal_stress_pp` — the constitutive traction — against the same
  Table 2 column. These are different operators. It is the likely reason SW-S4
  needs `fault_pressure_coefficient = 0.86` and the others do not, and it makes
  SW-S4's $\sigma'_n$ score not comparable with its siblings'.

---

## 6. Documentation state

**`orca_czm_theory.md`** is in good shape. The supplement on the reference
experiment is accurate against the PDF, including Table 1, the rock properties, the
protocol, the $Z_2$/JRC correlation, and the fracture-area formula
$A = \pi D^2/4\sin\theta$. Its θ-recovery derivation and its SW-S4/SW-T2 mesh
findings were independently re-derived here and confirmed. Three defects:

1. Two dangling cross-references —
   `Examples/YeGhasemmi2018/final_simulation_runs_v2/meshes/README_fracture_angle.md`
   and `PHYSICS_FIXES.md` — neither exists in this repository. Both live in
   `orca_3.0_claude_edit`, and under `v3`/`v4`, not `v2`.
2. It states the corrected journals are "in both campaign directories", which is
   true of `orca_3.0_claude_edit` and false of `orca_4.0`. A reader of this repo
   would conclude the meshes are fixed. They are not.
3. It does not say that the dissipation bound is confined to one of the four laws.

**`paper_draft_ye_ghassemi_validation.md`** needs the §4 correction above, plus:

- Table 1 lists SW-S3 length as 124.4 mm; the paper says 123.40 mm.
- Table 1 gives SW-T2 θ (Appendix A) = **30.00°** — correct — but the mesh is built
  at 31° and the deck's resolution coefficient is 0.4415 = ½sin(62°), i.e. 31°.
  The manuscript's headline claim that the geometry is recovered rather than fitted
  is contradicted by the setup it describes, for two of four specimens.
- §3.5.3 states the Table-2 dilation angle for SW-T1 is "≈12°". It is 16.44°.
- §0.4 warns that θ for SW-T2 "disagrees with the value implied by its own Table 2"
  and says Appendix A resolves it. Appendix A resolves it on paper; the mesh does
  not.

---

## 7. Recommended order

1. **Fix the manuscript's dissipation-bound scope** (§4). Documentation-only, and it
   is the item a reviewer is most likely to catch.
2. **Correct the manuscript's Table 1 and the ≈12° slip** (§6). Trivial.
3. **Refit SW-S3 and SW-S4 with the paper's JRC and JCS** (§2), letting $\phi_r$
   land near 29.8° and 23.7°. This is a real re-run and it changes §5.5 and §6.3,
   but it replaces two indefensible parameters with two defensible ones and removes
   a 28 % error in the quantity the study is about. New decks get new names.
4. **Port the corrected SW-S4 and SW-T2 meshes** (§3.1) — only alongside item 3,
   since both invalidate the same runs.
5. **SW-S3 mesh length** (§3) — 0.81 %, below the noise of everything else. Record
   it; do not re-run for it alone.
6. **Re-gate SW-S3's `axial_pres_final`** at E = 67 GPa (§5).

Items 1 and 2 are done in this commit. Items 3–6 are not.
