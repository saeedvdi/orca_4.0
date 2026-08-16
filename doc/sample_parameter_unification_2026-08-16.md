# Cross-sample parameter audit and validation-data audit — 2026-08-16

Scope: the four Ye & Ghassemi (2018) sample decks in `Examples/YeGhasemmi2018`
(SW-S3, SW-S4, SW-T1, SW-T2), asking one question — **which parameters are
properties of the rock, and are they the same in every deck?** — plus a
diagnosis of the SW-S3 and SW-T1 panels.

Two new tools back everything below:

| script | what it does |
|---|---|
| `scripts/sample_scorecard.py` | scores every deck against its digitized curves: peak ratio, peak timing lag, normalised RMSE |
| `scripts/friction_envelope_compare.py` | evaluates the Barton-Bandis envelope for each sample's own constants and reports the discriminating quantity, `dtau/dsigma'_n` |

No source file was modified. `orca-opt` has still not been relinked, so the
campaign continues against the same shared library throughout.

---

## 1. The question asked first: is the normal-stress rebound constitutive now?

**Yes for the stress, no for the dilation. They are two different mechanisms and
only one of them moved.**

### 1.1 sigma'_n rebound — constitutive

The reported effective normal stress is

```
bb_effective_normal_stress_pp = -czm_sigma_n_pp          (ParsedPostprocessor)
czm_sigma_n                   = component 0 of interface_traction
                                (OrcaCZMRealVectorCartesianComponent)
interface_traction            = OrcaComputeGlobalTractionSmallStrain
                                <- OrcaBartonBandisContactTractionFastADHardening
```

The only postprocessor arithmetic in that chain is a sign flip, tension-positive
to compression-positive. Everything else is the constitutive traction.

The rebound itself lives in `updateNormalUnloadState()`
(`ADOrcaBartonBandisContactTractionFastAD.C:604`). It is genuinely in the
traction path — the retained opening is subtracted from the closure that drives
the normal traction, at line 1077:

```cpp
const ADReal closure_old_candidate =
    raw_closure_old_ad
  + ADReal(... _normal_reclosure_stiffness_multiplier - 1.0 ...) * recovered_raw_closure
  - ADReal(retained_opening_old);              // <-- the rebound, in the traction
```

`updateNormalUnloadState` is called at lines 1084, 1189, 1318, 1503 and 1538 —
all inside the return mapping, before the traction is finalised. The controlling
parameter is `normal_unload_retention_fraction`.

### 1.2 Normal dilation rebound — still reporting-only

`updateReportedNormalOpening()` (line 640) carries its own header:

> This reconstruction is deliberately downstream of the constitutive update. It
> changes only diagnostic material properties and therefore cannot perturb
> traction, displacement, hydraulic aperture, permeability, or flow.

and it is called at 1107, 1192, 1321, 1530, 1570 — always *after* the matching
`updateNormalUnloadState`. The parameter documentation says the same thing in
capitals (line 159): `"OUTPUT ONLY: fraction of the peak scaled reversible
opening retained during post-failure reclosure."`

So `reversible_normal_compliance` and the whole
`reported_reversible_normal_opening_*` family are the **old postprocessor formula
relocated into the material**. It moved house; it did not become physics. The
older audit note in `orca_3.0_full` predicted exactly this and recommended the
replacement that has not happened yet:

> `reversible_normal_compliance`, `reversible_normal_reference_stress` |
> Output-only elastic normal rebound | Added because irreversible dilation cannot
> recover during unload | **Keep as diagnostic**; replace by auto-computed normal
> compliance or nonlinear normal closure in a primary law

Only the four SW-S4 `68_0*` decks set `reversible_normal_compliance`. SW-S3,
SW-T1 and SW-T2 do not, so for those three the reported dilation is a
pass-through of the kinematic jump (verified numerically in §3).

---

## 2. Rock parameters are not shared. Four of them disagree.

| parameter | SW-S3 | SW-S4 | SW-T1 | SW-T2 | verdict |
|---|---|---|---|---|---|
| `youngs_modulus` | **75e9** | 67e9 | 67e9 | 67e9 | must be shared — drift |
| `poissons_ratio` | 0.32 | 0.32 | 0.32 | 0.32 | consistent |
| `biot_coefficient` | **1e-12** | **0.6** | **1e-12** | **1e-12** | must be shared |
| `initial_porosity` | 0.001 | 0.001 | 0.001 | 0.001 | consistent |
| `matrix_permeability` | 5e-19 | 5e-19 | 5e-19 | 5e-19 | consistent |
| fluid rho/mu/Kf | identical | identical | identical | identical | consistent |
| `jcs` | **3.0e8** | **3.0e8** | **1.5e8** | **1.5e8** | must be shared |
| `residual_friction_angle_degrees` | **7.5** | **7.5** | **44.1** | **46.3** | must be shared |
| `jrc` | 23.35 | 17.5 | 15.32 | 14.63 | per specimen — legitimate |
| `dilation_angle_peak_degrees` | 26.0 | 24.0 | 16.44 | 13.97 | per specimen — legitimate |
| `normal_unload_retention_fraction` | 0.06 | 0.04 | **0.94** | **0.84** | see §2.3 |
| Kni / Vm / exponent / offset | identical across all four | | | | consistent |

### 2.1 Young's modulus — a drift, and the paper settles it

All SW-S3 decks use 75 GPa; every other deck uses 67 GPa. Both carry the *same*
section comment, `# --- mechanics (OrcaMechMaterial) : DD02 reference values ---`,
so this is drift rather than a deliberate per-sample value.

`orca_3.0_full` still holds the provenance:

```
youngs_modulus = 67e9                       # Pa, paper Sec. 2.1
youngs_modulus = 80e9            # CASE F: reference DD02 value (was 67e9)
```

So **67 GPa is the paper value**, 80 GPa is what "DD02" actually means, and 75 GPa
is neither. The section comment in all four decks is wrong as well as the SW-S3
number.

**Action: set 67e9 everywhere and correct the comment.**

### 2.2 Friction: the two families are not reconcilable by re-tuning

This is the substantive finding, and it is worse than a numerical mismatch.

All four decks set `use_mobilized_jrc = false`, `use_scale_correction = false`
and `pore_pressure_strength_coefficient = 0`, so every one of them evaluates
exactly the same law and the comparison is like-for-like:

```
phi_peak = phi_r + JRC * log10(JCS / sigma'_n)        (capped at 85 deg)
tau_lim  = sigma'_n * tan(phi_peak)
```

Evaluated at each sample's own operating stress:

| sample | sigma'_n | roughness term | phi_peak | mu | phi_r share |
|---|---|---|---|---|---|
| SW-S3 | 15 MPa | 30.4 deg | 37.9 | 0.778 | 20% |
| SW-S3 | 33 MPa | 22.4 deg | 29.9 | 0.575 | 25% |
| SW-S4 | 33 MPa | 16.8 deg | 24.3 | 0.451 | 31% |
| SW-T1 | 67 MPa | 5.4 deg | 49.5 | 1.169 | **89%** |
| SW-T2 | 67 MPa | 5.1 deg | 51.4 | 1.253 | **90%** |

The S-family draws 70–80% of its strength from the **stress-dependent** roughness
term. The T-family draws ~90% from the **constant** `phi_r`. Both reproduce their
own measured tau — SW-S3 shear-stress peak ratio 0.989, SW-T1 0.999 — so peak
values cannot distinguish them.

What distinguishes them is stress sensitivity, which is precisely what this study
is about, because injection lowers sigma'_n:

| sample | sigma'_n | dtau/dsigma'_n | mu | gap |
|---|---|---|---|---|
| SW-S3 | 15 MPa | 0.494 | 0.778 | 0.284 |
| SW-S4 | 33 MPa | 0.291 | 0.451 | 0.160 |
| SW-T1 | 67 MPa | 0.894 | 1.169 | 0.275 |
| SW-T2 | 67 MPa | 0.968 | 1.253 | 0.285 |

**Can one shared `phi_r` be made to work by re-fitting JRC?** No. Holding
`phi_r = 30 deg` (granite reference) and solving for the JRC that reproduces each
sample's own tau:

| | JCS = 150 MPa | JCS = 300 MPa | deck has | physical range |
|---|---|---|---|---|
| SW-S3 | 3.91 | 2.84 | 23.35 | 0–20 |
| SW-S4 | **-4.15** | **-3.01** | 17.50 | 0–20 |
| SW-T1 | **45.41** | 27.65 | 15.32 | 0–20 |
| SW-T2 | **49.40** | 30.08 | 14.63 | 0–20 |

SW-S4 needs a *negative* JRC and the T-family needs 28–49, far above the JRC
ceiling of 20. **The two families demand genuinely different friction
coefficients, and the difference is in the calibration targets, not in the
parameters.**

Checking the targets directly, mobilised mu = tau/sigma'_n:

| sample | simulated mu (median) | digitized mu (median) |
|---|---|---|
| SW-S3 | 0.433 | 0.351 |
| SW-T1 | **1.024** | **0.894** |

The factor of ~2.4 is present **in the digitized experimental data itself**.
Byerlee's law (mu ~ 0.85 below 200 MPa) sits between the two families: the
S-family is well under it, the T-family at or above it. Sustained mu > 1 on a
granite joint is not credible, so the SW-T stress resolution is the first thing
to check — most likely the assumed fracture angle used to resolve sigma'_n and
tau, or the digitized sigma'_n itself (see §3.2, where SW-T1's digitized
sigma'_n turns out to be a near-constant line).

**This is why the friction split must not be "fixed" by averaging the two.** It
is a symptom. Until the SW-T resolution is verified, forcing a shared `phi_r`
would just move the error.

#### 2.2.1 The stress resolution is correct — I checked it

The obvious explanation is a mis-resolved fracture angle. It is not that. Each
deck's `shear_stress_paper_frame_mpa_pp` carries the resolution coefficient
`0.5 sin(2 theta)` explicitly:

| sample | coefficient | theta from sigma1 | check |
|---|---|---|---|
| SW-S3 | 0.424024 | **29.0 deg** | optimal plane for phi ~ 31 deg is 29.5 deg |
| SW-T1 | 0.449397 | **32.0 deg** | |

and the normal resolution agrees with it. At SW-T1's peak,
`sigma_n = sigma3 + q sin^2(theta) = 29.945 + 149.737 x 0.2808 = 71.99 MPa`
total, against a reported effective 59.84 — implying a mean fault pressure of
12.15 MPa, which sits correctly between the 5 MPa production and 19.2 MPa
injection pressures. The arithmetic is right.

Nor is the state impossible. The largest friction any plane could mobilise in
this stress state is `sin(phi_max) = q/(sigma1' + sigma3') = 0.808`, i.e.
mu_max = 1.371, and SW-T1 sits at 1.12. Admissible — just very high.

#### 2.2.2 Cohesion: a plausible fix, tested and rejected

SW-S4 is documented as a **saw-cut** fracture. If SW-T is instead a tensile
fracture — rough, mated, interlocked — high strength would be expected, and the
physical way to carry it is cohesion rather than a 44 deg basic friction angle.
The model cannot express that: `computeCohesionEffective()` returns a hard-coded
`0.0`, with no input parameter and no subclass override. A fit that needs
cohesion therefore has nowhere to put it except `phi_r`. That structural
limitation is real and worth recording on its own.

But cohesion is **not** the explanation. Solving for the cohesion that closes
the gap at a physical `phi_r`, restricted to actively-yielding rows only
(`plastic_slip_increment > 0`):

| sample | rows | mobilised mu | cohesion at phi_r = 30 deg |
|---|---|---|---|
| SW-T1 | 2210 | 0.878 – 1.202 | **15.9 ± 9.9 MPa** |
| SW-S3 | 547 | 0.332 – 0.666 | **−20.2 ± 0.9 MPa** |

A working hypothesis gives a small spread — one cohesion valid at every stress
level. SW-T1's is ±62%. Rejected.

The contrast in the **scatter** is the real result. SW-S3's yielding is described
by a single friction law to within 0.9 MPa. SW-T1's mobilised mu swings from 0.88
to 1.20 across only 35–59 MPa of normal stress, a far wider spread than any
Barton-Bandis curve produces. So the conclusion is stronger than "the two
families disagree": **SW-T1's tau/sigma'_n relation is not well described by the
Barton-Bandis form at all.** The model reproduces SW-T1's tau to 0.999 because
the loading frame drives it, not because the friction law is right.

**And it cannot currently be settled**, because SW-T1's digitized effective
normal stress is the degenerate near-constant file identified in §3.2. sigma'_n
cannot be checked against experiment until that file is replaced — which makes
task #66 a prerequisite for the friction question rather than a side issue.

### 2.3 Two different aperture laws

| | SW-S3 | SW-T1 |
|---|---|---|
| `use_kinematic_aperture` | false | true |
| `dilation_scale` | **0.038** | 0.0 |
| `use_slip_damage` | true | false |
| `normal_stress_aperture` | active | 0 |

SW-S3 runs the additive path with a **0.038 multiplier on cumulative dilation** —
a 26x discount, applied to the term that is supposed to be the physical driver of
permeability growth. SW-T1 runs the kinematic path where dilation is already in
the mechanical gap. These are two different models of the same fracture, and the
0.038 is worth revisiting on its own (it is the most likely home of SW-S3's 3x
permeability error, §3.1).

Confirmed *not* a bug: SW-T1's `cumulative_dilation_pp`, `slip_damage_aperture_pp`
and `normal_stress_aperture_pp` are all identically zero, which is correct — those
three terms are switched off in that deck.

---

## 3. Diagnosis of the panels

### 3.1 SW-S3 — the flagged figure is the alpha = 0.6 arm

Peak ratios sim/exp:

| observable | alpha = 1e-12 | alpha = 0.6 |
|---|---|---|
| differential stress | 0.996 | 0.921 |
| injection pressure | 1.000 | 1.000 |
| flow rate | 1.039 | **1.168** |
| fracture permeability | 1.001 | 1.080 |
| normal dilation | 0.987 | **1.193** |
| effective normal stress | 1.008 | 1.006 |
| shear slip | 1.010 | **1.265** |
| shear stress | 0.989 | 1.061 |
| diff-stress nRMSE | 15.8% | **42.9%** |

**The permeability does not need adjusting — the plot was against a superseded
file.** `SWS3/SWS3/` holds two permeability digitizations, and both the notebook
and the first version of the scorecard used the stale one:

| file | sim/exp k |
|---|---|
| `permeability_m2_vs_time_sw3.csv` (stale — what the notebook plotted) | **3.03** |
| `permeability_m2_vs_time_sw3_corrected.table2` | **1.02** (worst point 16%) |

The corrected file is right, and the proof does not rest on the simulation
agreeing with it. Fit on the simulation's own output gives

```
ln Q = 1.501 ln k + 1.441 ln P_inj + c
```

— the exponent 1.5 on k is the cubic law, exactly as it should be. So a factor
of 3.0 in k implies a factor of 3.0^1.5 = **5.2 in flow rate**. The measured flow
rate is matched at **1.04**. The stale permeability curve therefore contradicts
the flow-rate curve *from the same experiment* by a factor of five in
transmissivity; the corrected series predicts a Q ratio of 1.02 against the 1.04
observed. The deck comments had already flagged the old file — "judge on the FLOW
panel (Q), not the digitized k curve (flagged ~3x low vs its own Q —
re-digitization pending)" — but the notebook was never repointed.

Fixed here: the notebook and `scripts/sample_scorecard.py` now read the corrected
series. SW-T1 has no corrected file and does not need one (perm ratio 1.014).

**With that corrected, SW-S3 at alpha = 1e-12 is within 4% on every channel**, and
exactly one problem is left:

**alpha = 0.6 breaks the slip calibration.** Slip 1.01 -> 1.27, dilation
0.99 -> 1.19, flow 1.04 -> 1.17, and slip onset moves earlier. This accounts for
"normal dilation drop is faster and the max is much higher", "shear slip happens
sooner and the peak is much higher", and the differential-stress and
shear-traction complaints — all of them are the one root cause. The onset
envelope was fitted at alpha ~ 0; raising alpha to the physical value stiffens
the bulk poroelastic coupling, so the fault yields earlier and runs further.

The fix is to refit the onset envelope at physical alpha, not to revert alpha.
That is task #60, now the single blocking item for SW-S3.

The one panel the user called correct — effective normal stress, ratio 1.006–1.008 —
is indeed the best-matched channel in both arms.

### 3.2 SW-T1 — yes, it is the data extraction, on the validation side

The simulation is internally consistent. Three independent checks:

- `czm_normal_dilation_paper_mm_pp` and `frac_normal_dilation_paper_mm` agree to
  every printed digit — the reporting reconstruction is a pure pass-through, as
  expected with `scale = 1`, `retention = 0`.
- reported dilation = `-mechanical_aperture * 1e3` **exactly** (e.g. 9.10701e-05 m
  -> -0.0910701 mm).
- dilation / slip = 0.154/0.5256 = 0.293 = tan(16.3 deg), against the deck's
  `dilation_angle_peak_degrees = 16.442`. Dilation is a faithful geometric
  consequence of slip, so there is only ever *one* error here, not two.

The digitized files are the problem:

| file | first | last | span | |
|---|---|---|---|---|
| `SWT1_shear_slip_mm.csv` | -48.731 | -46.844 | 1.944 | **un-zeroed baseline of -48.7 mm** |
| `SWT1_piston_displacement_mm.csv` | -38.075 | -38.075 | **0.000** | **constant — the file holds no data** |
| `SWT1_normal_dilation.csv` | -0.008 | +0.521 | 0.546 | **sign opposite to SW-S3's** |
| `SWT1_effective_normal_stress.csv` | | | ~0 | near-constant at 67.2 MPa |
| SW-S3 equivalents | ~0 | | 0.074 / 0.048 / 0.046 | all fine |

The scorecard reports SW-T1 shear-slip ratio -0.011 and nRMSE 2470% purely because
of the -48.7 mm offset. That number is an artefact and should not be read as a
result.

Once zeroed, the two usable SW-T1 curves have the same onset (~1750 s) and the
same plateau time (~1850 s) as the simulation, and their ratio is
1.9349/0.5439 = 3.56 ~ 1/tan(15.7 deg) — i.e. they *are* a slip/dilation pair
related by a plausible dilation angle.

Under the reading that `SWT1_normal_dilation.csv` actually holds **shear slip**:

| | simulated | digitized (zeroed) | ratio |
|---|---|---|---|
| shear slip | 0.5256 mm | 0.546 mm | 0.96 |
| normal dilation | 0.154 mm | 0.546*tan(16.44) = 0.161 mm | 0.96 |

Both land within 4%. That is a much more coherent story than the labels give, but
**it cannot be settled from the CSVs alone** — it needs a check against the paper
figure to decide which file is mislabelled. Flagged, not assumed.

Everything else in SW-T1 scores well and is alpha-insensitive (base vs 0.6 differ
by ~2%): differential stress 0.999, injection 0.999, flow 1.041, permeability
1.014, sigma'_n 1.002, shear stress 0.999. This matches the reported reading of
that figure, including "the permeability and flow rate can be improved after
unloading" — both peak ~207 s later than the data.

---

## 4. Recommended order of work

1. **Refit SW-S3's slip-onset envelope at alpha = 0.6** (task #60). Now the only
   remaining SW-S3 problem, and it explains every symptom in that figure.
2. **Verify the SW-T1 digitized set against the paper figure** (task #66). Nothing
   downstream of SW-T1 can be scored until this is settled, and it is cheap.
3. **Set `youngs_modulus = 67e9` in the SW-S3 family** (task #65). Well-evidenced,
   low risk, and it removes one variable from every later comparison.
4. **Do not unify `phi_r` yet** (§2.2). Verify the SW-T stress resolution first;
   the mu > 1 result says the targets are suspect, and a forced average would
   bury that.

A general lesson from §3.1 and §3.2: of the problems reported from the figures,
**two of the three were in the validation data, not the model.** Before tuning
any deck against a panel, check that the digitized series is the current one and
is self-consistent with the other measured channels.

New decks for any of this get a name reflecting the change, per the standing
convention.
