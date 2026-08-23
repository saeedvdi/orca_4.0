# Kalantar et al. (2025) — reading notes, audit, technical foundations, and what to do with it

> Kalantar, A., Hofmann, H., Ji, Y., Blöcher, G., Muhl, L., Zang, A., & Deon, F. (2025).
> Limits of self-propping in Enhanced Geothermal Systems: New experimental insights from shear,
> tensile and saw-cut fractures in Odenwald granodiorite.
> *JGR: Solid Earth*, 130, e2025JB031938. https://doi.org/10.1029/2025JB031938
> GFZ Helmholtz Centre for Geosciences. Open access. Data: GFZ Data Services (Kalantar et al., 2025).

Prepared 2026-08-23, on branch `orca_v7`. Companion to
`reading_hosseini2025_rsf_heterogeneous_fault.md`, and deliberately in the same shape — but this
paper stands in a different relation to your work. Hosseini is a *template* you might imitate.
Kalantar is a **second validation dataset**, a **reanalysis of your own four specimens**, and a
**measurement of the one constant you had to infer**. It is therefore read here in four passes:

1. **Part 1** — what the paper says, at the level of detail a deck needs.
2. **Part 2** — the audit. Six defects found, four of them checkable from the paper's own tables.
   Two are new to this document and one of them changes the gate.
3. **Part 3** — the technical foundations behind every equation, to comprehensive-exam depth.
4. **Parts 4–7** — what ORCA needs, what round 1 currently gets wrong, what the paper gives your
   manuscript, and the questions to expect.

Everything numerical in Parts 2–4 was recomputed for this document against
`Examples/Kalantar2025/validation/kalantar2025_table2.csv` and the three built decks. Where a
number contradicts an earlier note of mine, the earlier note is named and struck.

---

# Part 1 — What the paper is

## 1.1 One paragraph

Three fractures — one **shear** (formed by triaxial failure), one **tensile** (Brazilian-style
blade splitting), one **saw-cut** — were prepared in Odenwald granodiorite, held at a critical
stress state under constant piston displacement, and pressurized in 3 MPa steps until they slipped,
then depressurized in the same steps. Flow rate, permeability, hydraulic aperture, axial shortening
and the resolved stresses were logged at each hold. The headline is a **negative result**: in this
rock, self-propping does not deliver. The shear fracture — the most field-representative of the
three, and the one with by far the highest initial permeability — *loses* permeability during
pressurization, from 2.03 to 1.61 D, because slip grinds its weak asperities into gouge that blocks
the flow paths. The tensile and saw-cut fractures do self-prop, but lose the gain again on
depressurization because their post-slip stress-sensitivity coefficient doubles.

## 1.2 The chain of argument

1. Three fracture types, one rock, one stress state, one protocol — so differences are attributable
   to fracture type alone.
2. Each is brought to ~85 % of its peak shear strength (~92 % for OG-SH), so injection and not
   loading causes reactivation.
3. Stepwise pressurization → slip. **Shear**: gradual creep through every hold. **Tensile**: a big
   burst at 27 MPa and a smaller one at 30. **Saw-cut**: one burst at 24 MPa, with an audible bang.
4. Permeability responds in *opposite directions*. Tensile and saw-cut rise (elastic opening, then
   self-propping). Shear falls monotonically (gouge).
5. Depressurization closes all three back below their starting permeability. Fitting Pedrosa's
   $k = k_0 e^{-\alpha\sigma'_n}$ before and after slip shows $k_0$ rises (self-propping is real)
   *but* $\alpha$ rises too (the gain is not retained).
6. Gouge is weighed: 1.20 g from the shear fracture, 0.10 g from the tensile one — a 12× difference
   — and XRD shows the fines are biotite-rich.
7. Conclusion: self-propping is limited in this rock, because low quartz (15 % vs granite's 43.5 %)
   and coarse grains (~5 mm vs 0.5 mm) make it deformable and weak.

**Note the structure.** Like Hosseini, each section adds one ingredient: §3.1 the three responses,
§3.2 the surfaces and the gouge, §4.1 the permeability paths, §4.2 the stress-sensitivity
mechanism, §4.3 the gouge mechanism. Unlike Hosseini, there is no organising figure — the paper's
product is a comparison table's worth of contrasts, and it is weaker for having no single diagram
a reader carries away. **That is a lesson in the negative: your §6 needs its one figure.**

## 1.3 Specimens and protocol

| | OG-SH | OG-T | OG-SC |
|---|---|---|---|
| fracture type | shear | tensile | saw-cut |
| how made | triaxial failure at $\sigma_3 = 70$ MPa, failed at $\sigma_d = 448$ MPa | V-blade split of a grooved 80×80×140 block, then cored | 2.4 mm diamond saw, polished 200 µm then 30.2 µm |
| length × diameter (Table 1) | 120.00 × 49.98 mm | 100.00 × 49.98 mm | 100.00 × 49.98 mm |
| fracture angle $\theta$ to core axis | 29° | 28° | 30° |
| $Z_2$ / JRC before | 0.30 / 15.60 | 0.25 / 12.10 | 0.12 / 4.23 |
| $Z_2$ / JRC after | 0.30 / 15.21 | 0.25 / 11.81 | 0.08 / 1.36 |
| asperity height range before | 7.90 mm | 7.20 mm | 0.70 mm |
| max $P_i$ | 18 MPa | 30 MPa | 24 MPa |
| hold duration | 300 s | 300 s | 600 s |
| hold stages (up / down) | 5 / 4 | 9 / 8 | 7 / 6 |
| gouge collected | 1.20 g | 0.10 g | — |
| $k$ first → last | 2.03 → 1.19 D | 0.02 → 0.01 D | 0.17 → 0.10 D |
| total $\Delta L_s$ | 42 µm | 275 µm | 22 µm |
| slip style | creep in every hold | one big burst + one small | one burst, 86 % of budget |

**Rock (§2.1, Muhl et al. 2022):** $E = 63$ GPa, $\nu = 0.16$, UCS 153 MPa, tensile strength 11 MPa,
porosity 0.33 %, matrix permeability $1.4\times10^{-20}$ m² ($1.4\times10^{-8}$ D) at 2 MPa
hydrostatic. Mineralogy: plagioclase 46 %, biotite 18 %, quartz 15 %, microcline 9 %, hornblende
9 %, chlorite 3 %. Mean grain size <5 mm, biotite plates ~5 mm long × 1.2 mm thick.

**Protocol (§2.3).** Vacuum to 1 kPa, saturate at $\sigma_3 = 2$ MPa / $P_p = 0.2$ MPa; raise
$\sigma_3$ to 5 MPa at 0.05 MPa/s and both pore pressures to 3 MPa at 0.03 MPa/s; precondition by
cycling $\sigma_3$ between 5 and 35 MPa; measure the shear strength; set the axial stress to the
critical value; switch to **constant piston displacement**; step $P_i$ up in 3 MPa increments at
0.03 MPa/s, each held ≥300 s (600 s for the saw cut); then step back down to 6 MPa. $P_o = 3$ MPa
throughout. Two 2 mm-diameter boreholes, 5 mm from the sidewall, one at each end.

**Frame.** MTS 815, 4600 kN capacity, 2000 kN in-vessel load cell (<1 % accuracy), 140 MPa
confining capability, four Quizix C6000-10K-HC-AT pumps. **$K_{sys} \approx 796$ kN/mm** (Ji et al.,
2023). Flow is judged steady when inflow and outflow agree to 5 % — the Ye & Ghassemi criterion.

## 1.4 The equations, as printed

$$
\sigma'_n = (\sigma_3 - P_p) + (\sigma_1-\sigma_3)\sin^2\theta
\qquad(3)
$$
$$
\tau = (\sigma_1-\sigma_3)\sin\theta\cos\theta
\qquad(4)
$$
$$
P_p = \frac{P_i + P_o}{2}
\qquad(5)
$$
$$
\Delta L_s = \Delta L - \frac{\Delta F}{K_{sys}}
\qquad(6)
$$
$$
k = \sqrt[3]{\left[\frac{Q\eta}{\Delta P}\,\frac{\ln(2L/r-1)}{B\pi}\right]^2}\Big/12,
\qquad B = \frac{2}{\pi\tan^{-1}(2n)},\quad n = b/a
\qquad(7)
$$
$$
k = k_0\,e^{-\alpha\sigma'_n}
\qquad(8)
$$
plus $Z_2$ (eq 1), JRC $= 61.79 Z_2 - 3.47$ (eq 2, Tse & Cruden 1979), and
$a_h = \sqrt{12k}$ (Snow 1969; Witherspoon et al. 1980).

**Equations (3)–(6) are the Ye & Ghassemi (2018) apparatus and reduction verbatim** — the paper
says so and cites them for the control mode. That is exactly why this dataset transfers: the decks
change specimen constants, not structure.

## 1.5 Figure inventory — what each one is actually good for

| figure | content | use to you |
|---|---|---|
| 1 | sample preparation photos | geometry sanity only |
| 2 | rig schematic, defines $\theta$, borehole placement | **the deck's BC layout** |
| 3 (a–f) | loading paths, peak/critical stars, fitted criteria | **peak envelopes for all three specimens** |
| 4 (a–c) | time series: $P_i$, stresses, $\Delta L_s$, $Q$, $k$ | the continuous record Table 2 samples |
| 5 (a–i) | surface morphology, aperture fields, aperture change | **misleading if read as aperture — see §2.6** |
| 6 (a–d) | slickensides and collected gouge | the gouge mechanism, qualitative + 1.20/0.10 g |
| 7 (a–c) | $k$ vs $P_i$, colour-coded by $\Delta L_s$ | the hysteresis loops |
| 8 (a–f) | Pedrosa fits — **(b,c,e,f) are YOUR SW-T1/T2/S3/S4** | **third-party reanalysis of your data** |
| 9 | conceptual gouge-clogging cartoon | the mechanism statement to cite |
| S1 | friction coefficient vs Ye & Ghassemi | their own cross-validation |

Figure 8 is the single most valuable panel in the paper for you, and Part 5 is about it.

---

# Part 2 — The audit

This is what `scripts/kalantar_parameter_audit.py` does, plus two findings new to this document.
The rule being applied is `back_analysis_method.md` step 0: **a published table and a published
equation set are two independent claims about one experiment — run them against each other before
believing either.**

Six defects, in descending order of consequence.

## 2.1 τ and ΔL_s are the same measurement — **NEW, and it changes the gate**

Equation (6) with $\Delta L = 0$ (which is what "constant piston displacement" means) gives
$\Delta L_s = -\Delta F/K_{sys}$. And $\Delta F = A\,\Delta\sigma_1$, while eq (4) gives
$\Delta\tau = \Delta\sigma_1\sin\theta\cos\theta$. Eliminate $\Delta\sigma_1$:

$$
\boxed{\;\Delta L_s = -\frac{A}{K_{sys}\sin\theta\cos\theta}\,\Delta\tau\;}
$$

This is an **algebraic identity, not an empirical correlation.** The shortening column and the
shear-stress column are the same number in different units. Tested against Table 2:

| specimen | predicted $|d\tau/d(\Delta L_s)|$ | fitted | ratio | $r$ | max stage error |
|---|---:|---:|---:|---:|---|
| OG-T | 0.1599 MPa/µm | 0.1598 | **0.9999** | −1.0000 | 0.150 MPa on a 43.81 MPa span |
| OG-SC | 0.1757 | 0.1750 | 0.9962 | −0.9996 | 0.096 on 3.86 |
| OG-SH | 0.1720 | 0.1792 | 1.0416 | −0.9998 | 0.289 on 7.17 |

OG-T reproduces to four digits. OG-SC and OG-SH sit within their own print resolution — $\Delta L_s$
is given to 1 µm, and OG-SH's whole budget is 37 units of that last digit, which is a 2.7 % floor.

**Consequences, and they are not small.**

1. **Table 2 contains two independent channels per stage, not three.** The audit's §2 says three —
   a flow, a slip, a stress. It is wrong, and this document supersedes it. There is **a flow
   measurement and a force measurement**, and $\sigma'_n$, $\tau$ and $\Delta L_s$ are all readouts
   of the second. Scoring four channels, as `kalantar_gate.py` currently does, counts one defect
   three times. This is the *same error class* the Ye2018 campaign already had to correct twice —
   see `ye2018-q-is-a-stress-readout-not-an-aperture-one` and `postprocessor-only-channels-can-fake-model-error`.
2. **Kalantar's $\Delta L_s$ is not comparable to Ye2018's $d_s$.** Ye & Ghassemi report a directly
   measured shear displacement *and* a normal displacement. Kalantar reports neither: $\Delta L_s$
   is inferred from the load cell. That is a further loss of identifiability on top of the missing
   $d_n$ column.
3. **The $\Delta L_s$ channel is a check on the deck's frame, not on its constitutive law.** If
   `axial_bc_penalty` is set to $K_{sys}/A$ — which it is, by construction — then any deck that
   gets $\tau(t)$ right gets $\Delta L_s(t)$ right for free. So keep scoring it, but **report it
   separately as a frame-implementation check and exclude it from the mean.**
4. **Axial shortening is not in-plane slip.** For a rigid matrix, $\Delta L_s = \delta\cos\theta$,
   so in-plane slip is $\Delta L_s/\cos\theta$ — 13–15 % larger. Kalantar (following Ji et al.,
   2023) treats $\Delta L_s$ as "a representation of fracture slip". If ORCA's
   `czm_shear_slip_mm_pp` is genuine in-plane slip, comparing it directly to $\Delta L_s$ carries a
   systematic $1/\cos\theta$: **1.1434 (OG-SH), 1.1326 (OG-T), 1.1547 (OG-SC)**. Decide the
   convention explicitly and write it in the gate; do not let it be discovered later.

## 2.2 Equation (7) is missing a factor of 12 — **the diagnosis, not just the discrepancy**

My earlier note (`kalantar-eq7-does-not-match-its-own-table`) established that eq (7) misses the
paper's own Table 2 by a constant 10.3× in $a_h^3$ and left it there: *"the form is right and a
numerical factor is wrong."* That is true but incomplete. The factor is identifiable.

Collapse eq (7) with $a_h = \sqrt{12k}$:

$$
a_h^3 = \frac{Q\eta}{\Delta P}\,\ln\!\left(\frac{2L}{r}-1\right)\frac{\tan^{-1}(2n)}{2}
$$

Now derive what it *should* be. The transmissivity of a parallel-plate fracture is
$T = a_h^3/(12\eta)$, and any planar-geometry solution writes $Q = G\,T\,\Delta P$ with $G$ a
dimensionless shape factor. Inverting, $a_h^3 = 12(Q\eta/\Delta P)/G$. **The 12 belongs inside the
cube-root bracket of eq (7) and is not there.** As printed, eq (7) divides by 12 once (writing
$k = [\cdot]^{2/3}/12$) where the algebra needs the 12 multiplied inside the bracket and then
divided outside — the two do not cancel, they compound.

Test all three readings against the 29 stages where $Q \ge 0.010$ mL/min (ratio of predicted to
printed $a_h$; 1.0000 is perfect):

| specimen | $n$ | eq (7) as printed | eq (7) with the 12 restored | plane cubic law |
|---|---:|---|---|---|
| OG-SH | 9 | 0.4603 ± 0.0005 | **1.0539 ± 0.0012** | **0.9946 ± 0.0012** |
| OG-T | 8 | 0.4391 ± 0.0129 | 1.0052 ± 0.0294 | 0.9786 ± 0.0287 |
| OG-SC | 12 | 0.4901 ± 0.0306 | 1.1221 ± 0.0700 | 1.0434 ± 0.0651 |

$12^{1/3} = 2.2894$, which is exactly the factor between columns 1 and 2. **Restoring the 12 moves
eq (7) from a factor-2.3 error to a 5.4 % one.**

And the residual 5.4 % is itself explained. The remaining difference between eq (7)-with-12 and the
plane cubic law is nothing but the shape factor:

| specimen | $G^{-1}_{\text{eq 7}} = \ln(2L/r-1)\tan^{-1}(2n)/2$ | $G^{-1}_{\text{plane}} = L/W$ | ratio | in $a_h$ |
|---|---:|---:|---:|---:|
| OG-SH | 1.9632 | 1.6500 | 1.1899 | 1.0597 |
| OG-T | 1.8469 | 1.7039 | 1.0840 | 1.0272 |
| OG-SC | 1.9904 | 1.5998 | 1.2441 | 1.0755 |

Predicted overshoot on OG-SH: 5.97 %. Measured: 5.39 %. They agree to 0.6 %.

**So the story closes completely.** Eq (7) as printed drops a 12. With the 12 restored it is a
correct electrical-analog doublet solution — but it is *not* the equation that produced Table 2.
Table 2 was computed with the **plane-channel cubic law**,

$$
\boxed{\;a_h^3 = 12\,\frac{Q\eta}{\Delta P}\cdot\frac{L}{W}\;}\qquad
W = \text{core diameter (short axis)},\quad L = \text{borehole separation},
$$

which reproduces OG-SH's nine stages to 0.54 % with 0.12 % scatter and **no fitted constant**. That
is the Ye2018 form. **The flow operator transfers unchanged**, and task #112's premise — that it
would not — was wrong.

Paper-frame $W/L$: **0.60607 (OG-SH), 0.58690 (OG-T 28°), 0.53800 (OG-T 26°), 0.62506 (OG-SC)**.

**Why this is worth publishing.** Anyone reducing new data with eq (7) as printed will report
apertures 2.3× too small and permeabilities 5.2× too small. The paper's own numbers are fine; the
printed equation is not.

## 2.3 OG-T's fracture angle is 2° off, and 26° is geometrically impossible

Equations (3)–(5) give an identity in which every term is tabulated:
$\tan\theta = (\sigma'_n - \sigma_3 + P_p)/\tau$ with $P_p = (P_i+3)/2$. Regressing it over the
hold stages recovers $\theta$ *and* $\sigma_3$ per specimen with no input from Table 1:

| specimen | $n$ | Table 1 $\theta$ | recovered | recovered $\sigma_3$ | max residual |
|---|---:|---:|---:|---:|---:|
| OG-SH | 9 | 29.0° | **29.006°** | 32.996 MPa | 0.0042 MPa |
| OG-SC | 13 | 30.0° | **29.998°** | 33.002 MPa | 0.0058 MPa |
| OG-T | 17 | 28.0° | **25.999°** | 33.001 MPa | 0.0067 MPa |

Two specimens reproduce their printed angle to 0.006°, so the method is sound and OG-T is the
anomaly. A 0.007 MPa residual over seventeen stages spanning $\tau = 19.4$–63.2 MPa means two
constants regenerate the *entire* stress table — a **recovery, not a fit**. Forcing 28° leaves a
systematic 0.85–2.78 MPa residual that no constant $\sigma_3$ and no constant $P_o$ absorbs; both
were tested and both fail.

**Geometry breaks the tie.** A through-going elliptical fracture at angle $\theta$ in a cylinder of
radius $r$ needs $2r\cot\theta$ of axial extent: **93.999 mm at 28°** (fits the 100.00 mm core with
3.00 mm clearance per end) and **102.474 mm at 26°** (overruns each end by 1.24 mm). Table 1 is
internally consistent; Table 2's reduction is not. **The specimen is 28° and the published OG-T
stress columns are in the wrong frame.**

Re-reduction (audit §6): recover the deviator from $\tau$, re-project onto 28°.
$\tau$ scales by a constant **1.052092** (+5.21 %, peak 63.21 → 66.50 MPa). $\sigma'_n$ does **not**
scale by a constant, because only its deviatoric part moves — so the ratio $\tau/\sigma'_n$ changes
stage by stage, and the published criterion $\tau = 1.1\sigma'_n$ was itself fitted in the wrong
frame.

This is the same class as SW-T2 in the Ye2018 campaign. **The angle identity has now caught a
published error in two independent datasets** — which makes the method itself a contribution worth
reporting.

## 2.4 σ₃ is 33 MPa, not the 30 MPa the prose foregrounds

The recovery above returns $\sigma_3 = 33.00$ MPa on all three specimens to 0.006 MPa. The text's
30 MPa is the **effective** confining pressure: $\sigma_3 - P_p = 33 - 3 = 30$ at $P_i = P_o = 3$.
The check is in the audit — $\sigma_3 - 3$ = 29.996 / 30.001 / 30.002 MPa. A deck that puts 30 MPa
in the confining BC carries a 10 % error in the clamping stress on every stage of every specimen.

## 2.5 The §4.4 field-scaling uses the core cross-section, not the fracture area

§4.4 states flow rates of 0–4 mL/min "across a fracture area of ~0.002 m²". But
$\pi r^2 = 1.962\times10^{-3}$ m² is the **core cross-section**. The fracture plane is
$\pi r^2/\sin\theta$:

| specimen | cross-section | fracture plane | ratio |
|---|---:|---:|---:|
| OG-SH | 1.962e-3 m² | 4.047e-3 m² | 2.063 |
| OG-T | 1.962e-3 | 4.179e-3 | 2.130 |
| OG-SC | 1.962e-3 | 3.924e-3 | 2.000 |

A factor of ~2 low. It does not overturn their conclusion — the field-normalised equivalent moves
from 0.04 to 0.08 mL/min, still ~two orders below the laboratory rate — but it is a real slip, and
it matters to you because **your `paper_flow_width_over_length_*` constants must use the fracture
plane's geometry, not the core's.** They do; this is a note not to "fix" them toward the paper.

## 2.6 The Figure 5 aperture fields are not apertures you can match

Figure 5b/5e/5h report aperture fields "up to ~8 mm" (OG-SH), "~7 mm" (OG-T), "below 0.5 mm"
(OG-SC), obtained by co-registering stress-free pre- and post-test surfaces. Table 2's hydraulic
apertures are 4.87, 1.11 and 1.92 µm.

| specimen | Fig-5 field max | $a_h$ max | ratio |
|---|---:|---:|---:|
| OG-SH | 8.0 mm | 4.87 µm | **1643** |
| OG-T | 7.0 mm | 1.11 µm | **6306** |
| OG-SC | 0.5 mm | 1.92 µm | 260 |

Three orders of magnitude. These are not two estimates of one quantity. The Figure 5 field is a
**stress-free geometric separation** including rigid-body mismatch of two surfaces that, in the
test, are clamped at 27–64 MPa effective normal stress; the hydraulic aperture is the
cubic-law-equivalent width of the connected channels that actually carry flow.

**Why this matters to your model specifically.** ORCA distinguishes a mechanical aperture $a_m$
from a hydraulic one $a_h$ through a propping coefficient — that distinction is exactly what these
numbers demand, and a model with one aperture cannot represent them at all. But it also means
**do not calibrate $a_m$ against Figure 5.** The paper never claims you should; the temptation is
real anyway, because Figure 5 is the only direct aperture measurement in the paper. Resist it, and
say in the manuscript why.

## 2.7 Print resolution — which columns can be scored, and on which specimen

Half-unit-in-last-place divided by the value, median over stages, in per cent:

| specimen | $Q$ | $k$ | $a_h$ | $\Delta L_s$ | $\sigma'_n$ | $\tau$ |
|---|---:|---:|---:|---:|---:|---:|
| OG-SH | **0.03** | 0.32 | 0.12 | 1.28 | 0.01 | 0.03 |
| OG-SC | 0.50 | 2.78 | 0.37 | 2.50 | 0.02 | 0.05 |
| OG-T | **4.55** | **16.67** | 0.76 | 0.19 | 0.01 | 0.02 |

Since $a_h \propto Q^{1/3}$, divide the $Q$ column by 3 to get its contribution to aperture: 0.01 %
on OG-SH, 1.5 % on OG-T.

**Read this table before choosing what to score.**

- **OG-SH is the only specimen whose flow data can decide anything.** Nine stages, three-decimal
  mL/min, values 0.461–3.614. That is why it, and only it, settles §2.2.
- **OG-T's $k$ column is worthless** — 2 decimals on values ≤0.10 D, a 17 % median. Its $Q$ column
  contains 0.000, 0.001, 0.002. Its $a_h$ column is consistent with $Q$ where $Q$ is resolved
  (0.9786 ± 0.0287, §2.2) but prints 0.10 µm at a stage where $Q$ = 0.000, and **0.00 µm** at the
  last stage, which is not a number. On OG-T, the flow channel exists only for the four or five
  stages around the slip event.
- **This reorders the channels relative to Ye2018.** There, $Q$ was well resolved and $d_n$ was the
  least redundant. Here $a_h$ is the better-resolved statement on two of three specimens, $k$ is
  always the degraded one, and there is no $d_n$ at all.
- Consistency check on the derivation chain: $a_h = \sqrt{12k}$ reproduces the printed $a_h$ to a
  median 1.0 % on OG-SH but 9.2 % (max 387 %) on OG-T and 8.4 % (max 88 %) on OG-SC — i.e. the
  printed $a_h$ was computed from *unrounded* $k$, and the printed $k$ is a rounded display of it.
  **Never score $k$.**

## 2.8 Two smaller internal inconsistencies

- **§2.1 says the saw-cut core was "polished to a length of 105 mm"; Table 1 says 100.00 mm.** The
  meshes follow Table 1, which is also what the stress reduction is consistent with. A 5 % length
  error changes the axial compliance of a system whose frame stiffness dominates everything, so it
  is worth settling from the GFZ release — but Table 1 is far more likely correct.
- **The boreholes are "5 mm from the sidewall" for a 2 mm-diameter hole**, which could mean the
  centre or the near edge. The journals assume the centre. If it is the edge, the flow path length
  changes by ~1 mm (~1.2 %), which under the cubic law is a ~1.2 % bias on $Q$ — larger than the
  mesh-snap bias below. Also resolvable from the GFZ release.

## 2.9 What the paper does well — do not let the audit obscure this

Six defects sounds damning. It is not. The defects are in transcription and reduction, not in the
experiment, and the experiment is careful:

- **Three fracture types, one rock, one stress state, one protocol.** The comparison is genuinely
  controlled, which is rarer than it sounds.
- **It propagates the scanner resolution into JRC and then concludes against itself** — "the
  variations are not statistically significant". A paper that reports a change and then tells you
  the change is inside its own error bar is being honest at a cost.
- **It weighs the gouge.** 1.20 g vs 0.10 g, with XRD on the fines. That converts a hand-waving
  mechanism into a measurement.
- **It cross-validates its own strength-determination method** against Ye & Ghassemi's friction
  coefficients (Text S1) when it had to invent one for OG-T.
- **It states the single-specimen limitation** — "one representative experiment per fracture type",
  shear fractures hardest to reproduce.
- **It reports its own counterintuitive result as the headline** rather than burying it.

The eq (7) and OG-T errors are the kind that survive review because no reviewer recomputes a table.
That is precisely why step 0 exists.

---

# Part 3 — Technical foundations

Assumes you will be asked to derive, not recall.

## 3.1 Resolving stress onto an inclined plane, and why eqs (3)–(4) are a *recovery*

For a cylinder under axial $\sigma_1$ and radial $\sigma_3$, a plane whose normal makes angle
$(90° - \theta)$ with the axis — equivalently, whose trace makes $\theta$ with the axis — carries

$$
\sigma_n = \sigma_3 + (\sigma_1-\sigma_3)\sin^2\theta,\qquad
\tau = (\sigma_1-\sigma_3)\sin\theta\cos\theta = \tfrac{1}{2}(\sigma_1-\sigma_3)\sin 2\theta .
$$

Terzaghi effective stress on the plane: $\sigma'_n = \sigma_n - P_p$. Hence eq (3).

**The identity.** Divide:
$$
\frac{\sigma'_n - \sigma_3 + P_p}{\tau} = \frac{(\sigma_1-\sigma_3)\sin^2\theta}{(\sigma_1-\sigma_3)\sin\theta\cos\theta} = \tan\theta .
$$
$\sigma_1$ cancels. So **every hold stage gives an independent estimate of $\theta$ using only
tabulated quantities**, and a straight line through all of them returns $\theta$ *and* $\sigma_3$
simultaneously. Nothing is fitted in the ordinary sense: if the table is self-consistent the
residual is zero to print precision, and if it is not, the residual is structured.

**Why this is the highest-value half hour in any validation.** It costs no simulation, uses no
external information, and it has now caught a wrong angle in two papers. Generalise it: *whenever a
paper prints both a derived quantity and its inputs, the derivation is a testable claim.* That is
the same move that catches eq (7) in §2.2. Add it to `back_analysis_method.md` step 0 as the
general form, not the special case.

**The $P_p = (P_i+P_o)/2$ approximation.** Inherited from Ye & Ghassemi. It says the pressure field
between two boreholes is linear along the flow path, so its plane-average is the endpoint mean.
For steady flow in a uniform channel that is exact; for the radial-then-channel geometry of two
point boreholes it is not, and the true area-average is weighted toward $P_o$ because the pressure
gradient is steepest near the inlet. **It is a modelling choice both papers share, so it does not
bias the comparison — but your model computes the real field and must apply the same approximation
when reporting**, or it will disagree with both papers for a reason that is not physics. That is
what `fault_pressure_coefficient` exists to express, and why the 110 decks set it to 1.0 rather
than importing Ye2018's fitted value.

## 3.2 Constant piston displacement, and the series-spring identity

The control mode (Ye & Ghassemi, 2018) freezes the *piston*, not the specimen. The specimen can
still shorten by unloading the frame, which is a spring of stiffness $K_{sys}$.

$$
\underbrace{\Delta L}_{=0 \text{ (piston)}} = \underbrace{\Delta L_s}_{\text{specimen}} + \underbrace{\frac{\Delta F}{K_{sys}}}_{\text{frame}}
\;\Longrightarrow\;
\Delta L_s = -\frac{\Delta F}{K_{sys}}
$$

which is eq (6). Two things follow, and both matter.

**(a) The stress path is not prescribed — it is a consequence.** Slip on the fracture relieves
axial load, which lowers $\sigma_1$, which lowers both $\tau$ and $\sigma'_n$. The specimen walks
*down* a line in $(\sigma'_n,\tau)$ space of slope $\mathrm{d}\tau/\mathrm{d}\sigma'_n = \cot\theta$
(2.05 at 26°, 1.88 at 28°, 1.80 at 29°, 1.73 at 30°). This is why the tables show $\tau$ *falling*
during pressurization even though nothing external changed.

**(b) The fracture sees a finite unloading stiffness.** In-plane slip $\delta$ gives axial
shortening $\delta\cos\theta$, hence $\Delta F = -K_{sys}\delta\cos\theta$, hence
$\Delta\sigma_1 = -K_{sys}\delta\cos\theta/A$, hence

$$
\boxed{\;k_{\rm eff} \equiv -\frac{\mathrm{d}\tau}{\mathrm{d}\delta} = \frac{K_{sys}\cos^2\theta\sin\theta}{A}\;}
$$

With $K_{sys}/A = 0.4057$ MPa/µm:

| specimen | $\theta$ | $\mathrm{d}\tau/\mathrm{d}(\Delta L_s)$ | $k_{\rm eff}$ (per µm of in-plane slip) |
|---|---:|---:|---:|
| OG-SH | 29° | 0.1720 MPa/µm | 0.1505 MPa/µm |
| OG-T | 28° | 0.1682 | 0.1485 |
| OG-SC | 30° | 0.1757 | 0.1521 |

**All three are the same to 2.4 %.** That is not luck: $\cos^2\theta\sin\theta$ is stationary at
$\theta = \arctan(1/\sqrt2) = 35.26°$ and the three angles straddle a flat maximum. **So the three
specimens' wildly different slip styles cannot be blamed on the loading frame. They are
constitutive.** That is a clean argument to make and it costs one line of algebra.

## 3.3 Stick-slip: the critical-stiffness criterion — *derive this at the board*

This is the Kalantar-paper analogue of Hosseini's $\Delta x < L_{cr}$, and it is the most
exam-worthy derivation here.

A fracture whose strength falls with slip is loaded through a spring. Let strength be
$\tau_f(\delta)$ and let the machine unload along $\tau = \tau_0 - k_{\rm eff}\delta$. Perturb the
slip by $\mathrm{d}\delta$. The driving stress falls by $k_{\rm eff}\mathrm{d}\delta$; the strength
falls by $|\mathrm{d}\tau_f/\mathrm{d}\delta|\,\mathrm{d}\delta$. Slip runs away if strength falls
faster:

$$
\boxed{\;\left|\frac{\mathrm{d}\tau_f}{\mathrm{d}\delta}\right| > k_{\rm eff} = \frac{K_{sys}\cos^2\theta\sin\theta}{A}
\quad\Longrightarrow\quad \text{unstable (stick-slip)}\;}
$$

This is the classical Rabinowicz/Byerlee/Dieterich stability criterion, and it is the *same
inequality* as Hosseini's $\epsilon_T > \epsilon_{cr} = |(a-b)t'_N|/D_c$, with the rate-and-state
weakening rate replaced by the slip-weakening one and the cell stiffness replaced by the machine
stiffness. **Say that explicitly if asked — it shows you see the two literatures as one.**

**Now the consequence that closes §2.1.** For a stiffness-controlled event, the final slip is set by
where the friction curve re-intersects the unloading line, so the *measured* slip is
$\delta = \Delta\tau/k_{\rm eff}$ — the stress drop divided by the machine stiffness. That is
precisely the identity of §2.1, and it explains *why* the identity is not merely arithmetic: during
the bursts the experiment is measuring the machine, and the constitutive law only sets *when* the
burst starts and *how far* it goes, not the ratio between the two.

**What can still be extracted.** Since a runaway stops when weakening ends, the observed slip
bounds the weakening distance from above:

| specimen | observed $\Delta\tau$ | $D_c^{\max} = \Delta\tau/k_{\rm eff}$ | behaviour |
|---|---:|---:|---|
| OG-SH | 6.57 MPa | 43.7 µm | stable — so its weakening rate never reached 0.15 MPa/µm |
| OG-T | 43.93 MPa (28° frame) | 295.8 µm | unstable at 27 MPa |
| OG-SC | 3.22 MPa | 21.2 µm | unstable at 24 MPa |

**These are pre-run admissibility inequalities for the decks**, and §4.3 shows one of them is
currently violated.

**A second reading of the same criterion.** OG-SH is a rough shear fracture with high JRC that
creeps stably, while OG-SC is a polished saw cut with JRC 4.23 that bursts. That is backwards from
the naive "rough = strong = unstable" intuition, and the criterion explains it: instability is
about the *slope* of the strength-slip curve, not its height. A polished surface with little to
degrade loses what strength it has over a very short distance; a rough one degrades gradually over
a distance set by its asperity scale. **Roughness lengthens $D_c$, and lengthening $D_c$ stabilises.**

## 3.4 Roughness: $Z_2$, JRC, and why JRC is not identifiable here

**$Z_2$** (eq 1) is the RMS slope of a profile:
$$
Z_2 = \left[\frac{1}{(n-1)(\Delta x)^2}\sum_{i=1}^{n-1}(z_{i+1}-z_i)^2\right]^{1/2},
$$
i.e. the second moment of the height *derivative*. **Tse & Cruden (1979)** regressed $Z_2$ against
Barton's ten standard profiles to get eq (2), $\mathrm{JRC} = 61.79\,Z_2 - 3.47$.

**Three things to know about this, all of which are asked.**

1. **$Z_2$ is sampling-interval dependent.** A fractal surface has $Z_2 \propto \Delta x^{H-1}$,
   so halving $\Delta x$ raises $Z_2$. Kalantar uses $\Delta x = 0.5$ mm (citing Jang et al., 2014;
   Tatone & Grasselli, 2012) while the scanner's native pixel spacing is 0.047 mm — i.e. they
   deliberately decimate to the interval the Tse–Cruden calibration used. **That is the correct
   thing to do and most papers do not say they did it.** Ye & Ghassemi's JRC values must be checked
   for the same interval before the two datasets' JRCs are compared.
2. **The 2-D profiles are taken perpendicular to the shear direction.** Roughness is anisotropic on
   a sheared surface; measuring across the slickenside direction gives a larger $Z_2$ than
   measuring along it. Both papers do it this way, so the comparison holds.
3. **Error propagation, and the conclusion it forces.** The scanner resolves 0.012 mm in $z$. Over
   a 0.5 mm profile spacing that propagates to $\pm 0.03$ in $Z_2$, hence $\pm 61.79\times0.03 =
   \pm 2.10$ in JRC. Compare that with the measured changes:

| specimen | JRC before | after | change | resolvable at ±2.10? |
|---|---:|---:|---:|---|
| OG-SH | 15.60 | 15.21 | −0.39 | **no** |
| OG-T | 12.10 | 11.81 | −0.29 | **no** |
| OG-SC | 4.23 | 1.36 | **−2.87** | **yes** |

**So OG-SC is the only specimen in the paper where a JRC-degradation law has an observable to fit
against — and it is a saw cut becoming smoother.** This independently reproduces
`ye2018-loading-path-cannot-identify-jrc`: JRC mobilization is inert on this loading path. Two
datasets, two groups, same conclusion. Say so.

## 3.5 The Barton–Bandis criterion, and how the paper's envelopes map onto it

Barton (1973) / Barton & Choubey (1977):
$$
\boxed{\;\tau = \sigma'_n\tan\!\left[\phi_r + \mathrm{JRC}\,\log_{10}\!\left(\frac{\mathrm{JCS}}{\sigma'_n}\right)\right]\;}
$$
with $\phi_r$ the residual/basic friction angle and JCS the joint wall compressive strength (taken
as UCS = 153 MPa for a fresh, unweathered joint). The bracket is the **mobilised** friction angle:
roughness contributes $\mathrm{JRC}\log_{10}(\mathrm{JCS}/\sigma'_n)$ degrees of extra friction,
which **decays as $\sigma'_n$ rises** because asperities are crushed rather than ridden over. At
$\sigma'_n = \mathrm{JCS}$ the roughness term vanishes entirely.

Kalantar reports *linear* criteria in Figure 3 instead. Splitting them into Barton–Bandis terms at
each specimen's stage-1 $\sigma'_n$ (what `build_110_kalantar_decks.py:envelope()` does):

$$
\phi_{\rm peak} = \arctan\frac{\mu\sigma'_n + c}{\sigma'_n},
\qquad
\phi_r = \phi_{\rm peak} - \mathrm{JRC}\log_{10}\frac{\mathrm{JCS}}{\sigma'_n}
$$

| specimen | Fig. 3 criterion | stage-1 $\sigma'_n$ | $\phi_{\rm peak}$ | roughness term | $\phi_r$ |
|---|---|---:|---:|---:|---:|
| OG-SH | $\tau = 0.7\sigma'_n + 1.2$ MPa | 42.99 MPa | 36.05° | 8.60° | 27.451° |
| OG-T | $\tau = 1.1\sigma'_n$ | 63.86 (28° frame) | 47.73° | 4.60° | 43.135° |
| OG-SC | $\tau = 0.4\sigma'_n$ | 36.10 | 21.80° | 2.65° | 19.148° |

**Sanity check these.** $\phi_r = 27.5°$ (OG-SH) and 19.1° (OG-SC) are plausible basic friction
angles for a biotite-rich granodiorite. **$\phi_r = 43.1°$ for OG-T is not** — no rock has a basic
friction angle of 43°. What that number is really saying is that a *mated* tensile fracture carries
interlock that Barton's JRC term, at JRC 12.1 and $\sigma'_n$ 64 MPa, cannot account for. In the
Ye2018 campaign the same thing happened and the resolution was a Barton–Bandis **cohesion**, not a
larger $\phi_r$ — see `paper-audit-applied-2026-08-16`. **OG-T's envelope should be rebuilt as
$\phi_r \approx 30°$ plus a cohesion, not as a 43° friction angle.** That is round-2 work, and it
is the first thing to change if OG-T's onset lands late.

## 3.6 Flow reduction: three geometries, and which one Table 2 used

All start from the **cubic law** — Poiseuille flow between parallel plates, transmissivity
$T = a_h^3/(12\eta)$ — and differ only in the shape factor $G$ in $Q = G\,T\,\Delta P$.

**(a) Plane channel.** Inlet and outlet are line sources spanning the full width $W$, separated by
$L$. One-dimensional Darcy flow:
$$
Q = \frac{a_h^3 W}{12\eta}\frac{\Delta P}{L}
\;\Longrightarrow\;
a_h^3 = 12\frac{Q\eta}{\Delta P}\frac{L}{W},\qquad G = W/L .
$$
This is what Ye & Ghassemi use and, per §2.2, what actually produced Table 2.

**(b) Two-borehole doublet in an infinite sheet** — the "electrical analog". Each borehole is a
point source in a 2-D conductor. Superposing a source and a sink of strength $Q$, the pressure drop
between the two well faces is $\Delta P = (Q/\pi T)\ln(L/r)$, so
$$
a_h^3 = 12\frac{Q\eta}{\Delta P}\frac{\ln(L/r)}{\pi} .
$$
The $\ln(2L/r - 1)$ in eq (7) is the same thing with the finite well radius handled by the exact
image construction rather than the far-field approximation, and $B$ corrects for the fracture being
a finite **ellipse** of axis ratio $n = b/a$ rather than an infinite sheet.

**(c) Eq (7) as printed** — (b) with the 12 dropped. §2.2.

**Why $n = \sin\theta$.** Cutting a cylinder of radius $r$ at angle $\theta$ to its axis gives an
ellipse with semi-minor axis $r$ (short axis $2r$, across the core) and semi-major axis $r/\sin\theta$.
So $n = b/a = \sin\theta$ — 0.485, 0.470, 0.500 for the three specimens. The paper says "ratio of
short and long axis" and does not state that it equals $\sin\theta$; it does.

**Which to use in your deck.** (a), because that is what reproduces Table 2 to 0.5 %, and because
it is what the Ye2018 decks already carry — so both validations are scored through the same
operator and any residual is physics, not reduction. Keep both the paper-frame and the mesh-frame
$W/L$ in every deck, as the 93-series does.

**Mesh-snap bias.** The boreholes snap to interface nodes, which changes $L$. Under the cubic law
$Q \propto W/L$, so the bias is simply the length ratio: **−0.96 % (OG-SC), −0.01 % (OG-SH 
factor 3), −1.83 % (OG-T 28°)**. All below anything this campaign ranks on, and all smaller than
the hole-centre/hole-edge ambiguity of §2.8.

## 3.7 Hydraulic vs mechanical aperture

$a_h = \sqrt{12k}$ **defines** $a_h$ as the width of the parallel-plate channel that would carry the
measured flow. It is not a geometric measurement, and for a real fracture it is always smaller than
the mean mechanical separation $a_m$, for three compounding reasons:

1. **Contact area.** Load-bearing asperities block part of the plane.
2. **Tortuosity.** Flow detours around contacts, lengthening the path.
3. **Aperture variability.** Transmissivity goes as the *cube* of the local aperture, so the
   harmonic-type average that governs flow is dominated by the narrowest constrictions along each
   channel — Jensen's inequality in the unfavourable direction.

Empirical corrections (Barton et al., 1985) are of the form $a_h = a_m^2/\mathrm{JRC}^{2.5}$, which
this repository has implemented and tested — see
`bartonbandis-bakhtar-permeability-2026-08-14`, including the finding that the aperture law is *not*
the mechanism behind SW-S4's instability.

**Kalantar's numbers make the point at an extreme.** §2.6: $a_m/a_h$ of 260–6300. Whatever
correction is used, that is a fracture in which flow is carried by a small number of connected
channels occupying a tiny fraction of the plane — which is precisely the picture their Figure 9
draws for gouge clogging, and precisely why a *small mass* of fines (1.20 g) can halve the
permeability of a fracture whose geometric aperture is millimetres.

## 3.8 Pedrosa's exponential permeability law and what $\alpha$ means

$$
k = k_0 e^{-\alpha\sigma'_n}
$$
$k_0$ is the extrapolated permeability at zero effective normal stress; $\alpha$ (MPa⁻¹) is the
stress sensitivity. Equivalently $\alpha = -\mathrm{d}\ln k/\mathrm{d}\sigma'_n$ — the fractional
permeability loss per MPa of clamping. David et al. (1994) give 0.023–0.11 MPa⁻¹ for crystalline,
metamorphic and volcanic rocks.

Since $k = a_h^2/12$, $\alpha$ is twice the aperture's normal compliance in log terms:
$\alpha = -2\,\mathrm{d}\ln a_h/\mathrm{d}\sigma'_n$. **So $\alpha$ is a re-parameterisation of the
normal-closure law your Barton–Bandis material already contains** — a two-parameter linearisation
of it in log-space, over the measured stress window. It is *not* independent physics, and you can
compute it from any ORCA run by regressing $\ln a_h$ against $\sigma'_n$ over the depressurization
branch. **Do that** — it makes Figure 8 directly comparable to your model output, which is worth
more than any narrative agreement.

**The paper's argument, stated compactly.** Self-propping raises $k_0$ (more residual aperture at
zero stress) but *also* raises $\alpha$ (the propped aperture is more compliant, because it rests
on a few mismatched asperity contacts rather than on a mated surface). At high $P_i$ the raised
$k_0$ wins; as $P_i$ falls, the raised $\alpha$ wins, and the curves cross. **That crossing is the
paper's central mechanism and it is a genuinely good piece of reasoning.**

## 3.9 Self-propping, dilation, gouge — the three-way competition

The aperture budget of a slipping rough fracture has three terms with two signs:

| term | sign | physics | ORCA parameter |
|---|---|---|---|
| dilation | **+** | riding over asperities; bounded by $\tan\psi \le (1-\epsilon_D)\mu$ | `dilation_angle_*`, `dilation_scale` |
| self-propping / retention | **+** | mismatched asperities hold the fracture open after unloading | `retention_residual`, `self_propping_scale` |
| gouge fill / wear | **−** | comminuted asperities fill the void | `use_slip_damage`, `slip_damage_scale` |

In `ADOrcaRoughnessDamageFracturePermeability` these compose additively:
```
a_h = a_h0 + stress_aperture + aperture_scale*a_m + dilation_term + self_prop − slip_damage_fill
slip_damage_fill = slip_damage_scale * (1 − exp(−s_eff / slip_damage_char_slip))
```
**Kalantar's three specimens are three different resolutions of that competition**, which is exactly
why the dataset is valuable:

- **OG-SC**: dilation + propping win, gouge negligible (smooth surface, little to break) → $k$ up.
- **OG-T**: dilation + propping win during slip, but the propped aperture is compliant → gain lost
  on unloading.
- **OG-SH**: gouge wins outright → $k$ falls *during pressurization*, the sign reversal.

Your 104-series arm 1 established computationally that gouge fill can push retained permeability
below 1.0, and that SW-S4 is the only one of your four where it does. **OG-SH is that regime run to
completion in an experiment.** Part 5.2.

**Why OG-SH and not the others.** The paper's answer (§4.3) is that a shear fracture is not a
surface but a *zone*, with fissures and weakened rock bridges left over from its violent formation
at $\sigma_d = 448$ MPa. Its asperities are pre-damaged. Add biotite — 18 wt %, plates ~5 mm long
and 1.2 mm thick, cleaving on (001) — and you have a mineral that shears to fines under exactly
this loading. The XRD on the collected fines returns biotite ~19 wt %, enriched relative to the
intact rock. **That is a mechanism supported by three independent measurements (mass, size
distribution, mineralogy), not a story.**

## 3.10 The critical stress state, and three different ways of finding it

The intent is uniform — set $\tau$ to 85 % of peak so that injection, not loading, causes
reactivation — but the method differs per specimen, and the differences matter for your envelopes.

- **OG-SH**: multi-stage test at effective confining pressures of 2, 4, 6 MPa, fit a criterion,
  **extrapolate** to 30 MPa. The paper says outright that this **overestimates** the peak (citing
  Muralha et al., 2014, on multi-stage testing) and that the test therefore ran at ~0.92 $\tau_p$,
  not 0.85.
- **OG-T**: no strength test available, so peak was picked from the **inflection in injected fluid
  volume** — expelled fluid while the differential stress rises, then a plateau, then an increase
  as the fracture starts to open. Validated against Ye & Ghassemi's friction coefficients (Text S1).
- **OG-SC**: eight stress drops during loading; the peak immediately before the seventh was taken
  as $\tau_p$.

**Back out $\tau_p$ from the stated ratios and Table 2's stage 1, walking up the loading path of
slope $\cot\theta$:**

| specimen | $\tau_{cr}$ | stated ratio | implied $\tau_p$ | implied $\sigma'_{n,p}$ | implied $\tau_p/\sigma'_n$ | Fig. 3 criterion at that $\sigma'_n$ |
|---|---:|---:|---:|---:|---:|---:|
| OG-SH | 26.14 | 0.92 | 28.41 | 44.25 | **0.642** | **0.727** |
| OG-T (28°) | 66.50 | 0.85 | 78.24 | 70.10 | 1.116 | 1.100 |
| OG-SC | 13.16 | 0.85 | 15.48 | 37.44 | 0.414 | 0.400 |

**OG-T and OG-SC are self-consistent to 1.4 % and 3.3 %.** OG-SH is off by 13.2 % — exactly the
overestimate the paper warned about. **The round-1 deck used the criterion, so OG-SH's peak envelope
is ~13 % too strong.** Corrected: $\phi_{\rm peak} = 32.70°$ (not 36.05°) and $\phi_r = 24.10°$ (not
27.451°), the roughness term being unchanged at 8.601°. §4.3.

---

# Part 4 — What ORCA needs, and what round 1 currently gets wrong

## 4.1 No source-code change is required

Every feature of this experiment maps onto an object already in use in the 93-series. This was
checked against the source, not assumed.

| paper feature | ORCA object | status |
|---|---|---|
| confining pressure $\sigma_3$ | `FunctionNeumannBC` on the lateral surface | in use |
| constant piston displacement | `FunctionPenaltyDirichletBC` with `axial_bc_penalty` = $K_{sys}/A$ | in use |
| two-borehole flow, $P_i(t)$ / $P_o$ const | `FunctionDirichletBC` / `DirichletBC` at pinned interface nodes | in use |
| stepwise up-then-down schedule | `PiecewiseLinear` | in use |
| $Q$ reduction, plane cubic law | `ParsedPostprocessor` with `(W/L)/12` | in use |
| $P_p = (P_i+P_o)/2$ convention | `fault_pressure_coefficient` | in use |
| Barton–Bandis strength + slip weakening | `OrcaBartonBandisContactTractionFastADHardening` | in use |
| dilation, bounded | `use_dilatancy`, `use_decoupled_dilation` | in use |
| **gouge fill (OG-SH's mechanism)** | `use_slip_damage` + `slip_damage_scale/_onset_slip/_characteristic_slip` | **in source, OFF in 2 of 3 decks — §4.3** |
| self-propping / retention | `retention_residual`, `self_propping_scale` | in source, zero in all 3 — §4.3 |
| roughness degradation | `use_roughness_degradation` | in use |
| Mohr–Coulomb baseline | 94-series siblings | available |
| Pedrosa $\alpha$ diagnostic | — | **add a postprocessor, §7** |

The one thing worth *adding* is not a physics object: a postprocessor that regresses
$\ln a_h$ against $\sigma'_n$ over the depressurization branch, so the model emits $(k_0,\alpha)$
directly comparable with Figure 8.

## 4.2 What round 1 got right

`scripts/build_110_kalantar_decks.py` derives, rather than fits:

| specimen | $\phi_{\rm peak}$ | $\phi_r$ | $\sigma_1$ | penalty | end time | stages | mesh $W/L$ |
|---|---:|---:|---:|---:|---:|---:|---:|
| OG-SH | 36.05° | 27.451° | 94.65 MPa | 4.057e11 Pa/m | 3600 s | 5/4 | 0.60601 |
| OG-T | 47.73° | 43.135° | 193.43 MPa | 4.057e11 | 6800 s | 9/8 | 0.57616 |
| OG-SC | 21.80° | 19.148° | 63.39 MPa | 4.057e11 | 9100 s | 7/6 | 0.61905 |

The schedule is generated from §2.3 and **asserted** against Table 2's stage counts — all three
match. The builder refuses to inherit `fault_pressure_coefficient`, `poro_du`, `axial_relax_du`,
`side_unload_relax_pressure`, and fails loudly if any active line still names a Ye2018 object. All
three pass `--check-input`; all six boreholes pin to interface nodes (4.1 µm, 792.9 µm, 388.5 µm).

## 4.3 Four defects in round 1 — found by writing this document

The builder's docstring claims *"every constant is DERIVED from the paper or from the verified
meshes — none is fitted."* **That is true of the constants the script substitutes and false of the
ones it does not.** The `[czm_contact]` and aperture blocks were inherited wholesale from the
Ye2018 parent chosen by fracture type. Four consequences, in order of severity.

**(a) OG-SC cannot produce its own burst.** From §3.3, instability needs
$|\mathrm{d}\tau_f/\mathrm{d}\delta| > k_{\rm eff}$, i.e. a weakening distance below
$D_c^{\max} = \Delta\tau/k_{\rm eff}$:

| specimen | needs | $D_c$ in deck | $D_c^{\max}$ | verdict |
|---|---|---:|---:|---|
| OG-SH | to creep | 150 µm | 43.7 | **creeps — OK** |
| OG-T | to burst | 150 µm | 295.8 | **bursts — OK** |
| OG-SC | to burst | **60 µm** | **21.2** | **CANNOT burst — will creep instead** |

OG-SC's `characteristic_slip_distance` is 2.8× too long. Its whole result is one sudden slip with
an audible bang at 24 MPa, and the deck as built is mechanically incapable of it. **This is a
prediction that costs no HPC time to make and would have cost a 48-hour job to discover.**

**(b) OG-SH's friction law strengthens with slip.** The deck carries
`residual_friction_angle_degrees = 27.451` (substituted, correct) alongside
`slip_weakening_residual_friction_angle_degrees = 29.756` (inherited from SW-T2, not substituted).
The second is the angle the first decays *toward*. **27.451 → 29.756 is slip strengthening.** All
three decks carry an unsubstituted value here; OG-T's (43.135 → 29.756) happens to weaken, and
OG-SC's (19.148 → 8.450) weakens.

**(c) The aperture law is entirely Ye2018's.** Side by side:

| parameter | OG-SH | OG-T | OG-SC | Table 2 says |
|---|---:|---:|---:|---|
| `initial_hydraulic_aperture` | 2.11 µm | 1.63 µm | 1.22 µm | **4.87 / 0.10 / 1.03 µm** |
| `min_hydraulic_aperture` | 2.00 µm | 1.51 µm | 1.22 µm | min reached: 3.72 / 0.00 / 0.58 |
| `reference_effective_normal_stress` | 66.74 MPa | 65.47 MPa | 32.1 MPa | stage-1 $\sigma'_n$: 42.99 / 63.86 / 36.10 |
| `self_propping_scale` | 0.0 | 0.0 | 0.0 | the paper is *titled* self-propping |
| `slip_damage_scale` | 0.0 | 0.0 | 0.40 µm | OG-SH is the gouge specimen |
| `bb_max_aperture_closure` / `_normal_stiffness` / `_stress_exponent` | 1.2 µm / 1.25e13 / 4.0 — **identical on all three** | | | three different fractures |
| `biot_coefficient` | 0.6 | 0.6 | 0.6 | paper gives none; $E,\nu$ differ from Ye2018 |

The most consequential is the first row. **OG-SH starts at 2.11 µm and must reach 4.87 µm** — a
factor 2.3, i.e. 12× in flow — **and it must get there while the data go *down*.** The specimen
whose headline is monotonic permeability *loss* has been given an aperture law that must gain 130 %
before it can start losing. Meanwhile `slip_damage_scale = 0` switches off the only mechanism that
could make it lose.

*Fairness note:* `dilation_scale = 0` with `aperture_scale ≈ 0.016` on the two tensile-parented
decks is **not** dilation switched off — it is dilation routed through the mechanical aperture
instead, the flag pairing documented in `doc-audit-2026-08-18`. Do not "fix" it by setting both.

**(d) OG-SH's peak envelope is ~13 % too strong** (§3.10). The builder used the Figure 3b criterion,
which the paper says overestimates. $\phi_{\rm peak}$ 36.05° → **32.70°**, $\phi_r$ 27.451° →
**24.10°**. Consequence: at stage 1 the deck sits 22 % below peak where the experiment sat 8 %
below, so it will slip late or not at all — on the one specimen that slips from the very first hold.

**None of these four is a run-and-see item. All four are algebra, and all four are wrong now.**

## 4.4 The gate needs restructuring

`scripts/kalantar_gate.py` scores `sigma_n_MPa`, `tau_MPa`, `ah_um`, `ds_mm` always and `Q_ml_min`
above a 0.010 mL/min floor, then reports the mean. Given §2.1 and §2.7 that mean is wrong in three
ways. It should:

1. **Score two channels, not five**: a **force** channel (pick one of $\tau$, $\sigma'_n$,
   $\Delta L_s$ — they are the same measurement) and a **flow** channel ($a_h$, or $Q$ where
   resolved). Report the others as diagnostics.
2. **Report $\Delta L_s$ separately as a frame-implementation check**, with the expected
   $\mathrm{d}\tau/\mathrm{d}(\Delta L_s)$ printed alongside — 0.1720 / 0.1682 / 0.1757 MPa/µm. A
   deviation there means `axial_bc_penalty` is wrong, not that the friction law is.
3. **Fix the slip convention.** Either divide the model's in-plane slip by $\cos\theta$ or multiply
   Table 2's $\Delta L_s$ by $1/\cos\theta$ — 1.1434 / 1.1326 / 1.1547 — and say which in the
   docstring.
4. **Drop $k$ entirely** and never reintroduce it (§2.7).
5. Keep the OG-T 28° re-reduction and the $Q$ floor. Both are right.

## 4.5 Admissibility checklist — run before submitting anything

In the spirit of Hosseini's inequality trio, these are checkable without running:

1. $\theta$, $\sigma_3$ in the deck match the **recovered** values (29.0/28.0/30.0, 33 MPa) — not
   Table 1's OG-T angle in the stress frame, not the prose's 30 MPa.
2. `axial_bc_penalty` $= K_{sys}/A = 4.057\times10^{11}$ Pa/m on all three.
3. **$D_c < \Delta\tau_{\rm obs}/k_{\rm eff}$** on OG-T and OG-SC; **$D_c >$** it on OG-SH. (§4.3a)
4. `slip_weakening_residual_friction_angle_degrees` $<$ `residual_friction_angle_degrees`. (§4.3b)
5. `initial_hydraulic_aperture` = Table 2's stage-1 $a_h$ per specimen; `min_/max_hydraulic_aperture`
   bracket the specimen's own range with margin. (§4.3c)
6. `slip_damage_scale` $> 0$ on OG-SH, or the paper's headline is unreachable by construction.
7. Every borehole pins to a `fracture_interface` node, verified post-mesh with
   `scripts/check_source_nodes.py` — `use_closest_node = true` snaps onto bulk nodes silently, and
   did on `og_sh_theta29_size4`. (`source-node-pinning-rule`)
8. `paper_`/`mesh_flow_width_over_length_*` both present, mesh value from the **snapped** separation.
9. Schedule stage counts equal Table 2's (5/4, 9/8, 7/6) — asserted by the builder.
10. `axial_pres_final` gated by a ~200 s preload run against stage-1 $(\tau,\sigma'_n)$ =
    (26.14, 42.99) / (66.50, 63.86) / (13.16, 36.10) MPa.

## 4.6 Mesh state

| mesh | elements | interface nodes | pitch | $L/D/\theta$ | area vs $\pi r^2/\sin\theta$ | source pinning |
|---|---:|---:|---:|---|---|---|
| `og_sc_theta30_size3` | 68,096 | 2185 | 1.004 mm | 100.00 / 49.98 / 30.000 | exact | OK, 388.5 µm |
| `og_sh_theta29_size3` | 100,048 | 1977 | 1.035 mm | 120.00 / 49.98 / 29.000 | exact | OK, 4.1 µm |
| `og_sh_theta29_size4` | 30,600 | 937 | 1.504 mm | 120.00 / 49.98 / 29.000 | exact | **FAILS — bulk node** |
| `og_t_theta28_size3` | 53,760 | 2297 | 0.980 mm | 100.00 / 49.98 / 28.000 | exact | OK, 792.9 µm |
| `og_t_theta26_size3` | 35,840 | 2297 | 0.992 mm | 104.48 / 49.98 / 26.000 | exact | OK, 849.1 µm |

Plane-fit residual 0.00 µm on all five; areas match to six significant figures; all six nodesets
present. `og_sh_theta29_size4` finds a bulk node at 951 µm while the nearest fracture node is
1217 µm away — it would run, and be wrong. The journal was switched to factor 3 so regenerating
cannot reproduce it.

**`og_sc_theta30_size5.e` is a stale duplicate of `size3.e`** (identical node and element counts,
identical pitch). Scoring the two would return perfect "mesh convergence" from a no-op. Rebuild or
delete it before any convergence claim.

---

# Part 5 — What this paper gives your Ye2018 manuscript

This is the part worth reading even if the validation never runs. Task #113.

## 5.1 It independently reanalyses your four specimens

Figure 8b/c/e/f fit Pedrosa to **SW-T1, SW-T2, SW-S3 and SW-S4** — a published, third-party,
two-number summary of the same data your decks are calibrated to.

| source | specimen | $k_0$ pre → post (D) | ratio | $\alpha$ pre → post (MPa⁻¹) |
|---|---|---|---:|---|
| Ye2018 | SW-T1 | 0.37 → 3.47 | **9.38** | 0.01 → 0.03 |
| Kalantar | OG-SC | 0.82 → 5.25 | 6.40 | 0.05 → 0.11 |
| Ye2018 | SW-T2 | 0.83 → 3.04 | 3.66 | 0.01 → 0.02 |
| Ye2018 | SW-S3 | 0.16 → 0.41 | 2.56 | 0.01 → 0.02 |
| Kalantar | OG-T | 1.91 → 4.73 | 2.48 | 0.08 → 0.16 |
| Ye2018 | SW-S4 | 0.12 → 0.20 | **1.67** | 0.03 → 0.06 |

**Take (1):** the enhancement ordering across your four — SW-T1 ≫ SW-T2 > SW-S3 > SW-S4 — puts
SW-T1 highest and **SW-S4 lowest**, the same extreme ordering your 101-series retained-permeability
metric produces (1.605 / 1.450 / 1.497 / 0.893). The middles swap, and with $n = 4$ a Spearman
$\rho$ of 0.8 is **consistency, not evidence** — say it that way. But SW-S4 being the outlier is now
corroborated by a second group using a different metric on the same raw data. Worth a sentence in
§6.7.

**Take (2):** SW-S4 has the highest $\alpha$ of your four, before and after slip (0.03 → 0.06 against
0.01 → 0.02). Kalantar's own explanation for non-retention is high stress sensitivity. That is the
same physical statement as your finding that SW-S4's aperture budget is dominated by gouge, from an
independent direction.

**Do not take:** "$\alpha$ doubles universally after slip." It rises in all six by 2.0–3.0×, but
**four of six pairs are quoted to one significant figure at values of 0.01–0.08**, so 0.01 → 0.02 is
the coarsest ratio the precision can express. The apparent constancy is inside the quoting
precision. This is exactly the shape of the Table-12 error
(`nonmonotonic-window-matched-state-bug`) — a clean regularity that is an artifact of how numbers
were written down.

**Also do not take** the $r^2$ column of `kalantar2025_figure8_pedrosa_fits.csv` without checking it:
OG-T post-slip reads as 0.06, which is implausible for a fitted line and may be 0.96 misread. It is
recorded as read and flagged rather than silently corrected.

## 5.2 It confirms your gouge mechanism from the opposite direction

Your 104-series arm 1 established computationally that gouge fill can push retained permeability
*below* 1.0, and that SW-S4 is the only one of the four where it does, because its baseline aperture
is 40 % smaller so the same absolute wear is 34 % of budget instead of 25 %.

Kalantar's headline is that mechanism running to completion in an experiment: **OG-SH's permeability
falls monotonically during pressurization, 2.03 → 1.61 D**, while $P_i$ rises and $\sigma'_n$ falls —
the opposite of what elastic opening predicts. Their §4.3 and Figure 9 attribute it to progressive
asperity breakage feeding gouge into the flow paths, and they weigh it: 1.20 g vs 0.10 g, with XRD
confirming biotite-rich fines.

**Your model predicted the sign; this experiment shows the regime where the sign dominates the whole
result.** That is a much stronger claim than "our model reproduces four calibration curves."

## 5.3 It measures your most leveraged inferred constant

`ye2018-frame-stiffness-dominates-magnitudes` records that the loading-frame stiffness is a
*derived* constant whose ×2 bracket moves $Q$ by −93.9 %/+408 %, and that you had to infer
0.94 MPa/µm from a single scored run under a series-spring assumption. Kalantar **measures** theirs:
$K_{sys} \approx 796$ kN/mm, which over the 49.98 mm cross-section is **0.406 MPa/µm**.

Different machine, so this is not a calibration. But it is the first independent evidence the
inferred value sits in the right decade, and it lands within a factor of 2.32 — **inside the bracket
you already ran**. That converts "we inferred a constant that dominates everything" into "we
inferred a constant that dominates everything, and an independently measured value for a comparable
apparatus agrees to within the bracket we tested." Much better to defend.

## 5.4 It supplies the rock-property axis your four specimens could not

Ye2018's four are one granite. Kalantar contrasts it explicitly:

| | Ye2018 granite | Odenwald granodiorite |
|---|---:|---:|
| $E$ | 67 GPa | 63 GPa |
| UCS | 150 MPa | 153 MPa |
| tensile strength | 11 MPa | 11 MPa |
| quartz | 43.5 % | ~15 % |
| mean grain size | 0.5 mm | ~5 mm |

**The confounds are already controlled** — moduli and strengths are nearly identical, composition
and texture are not. Their argument is that less quartz and coarser grains mean more matrix
deformability, hence higher $\alpha$ and lower post-slip friction, hence worse retention.

That gives you a mechanistic axis — **composition → deformability → stress sensitivity →
self-propping retention** — which your model expresses through the aperture-law compliance. So it is
a testable prediction, not a narrative.

*(Note $\nu = 0.16$ here against Ye2018's 0.32. That is a large difference, it is not discussed, and
it affects the poroelastic response. It also interacts with the $\alpha = 0.6$ Biot coefficient the
110 decks inherited — see `ye2018-poroelastic-constants-inconsistent`.)*

## 5.5 It is a citable negative result for your discussion's framing

The conclusion is that self-propping "is limited under the investigated boundary conditions" for
this rock, and that all three fracture types lose their enhancement on depressurization. Your
§6.7/§6.9 already argues that retained enhancement is *uncorrelated* with the roughness parameters
supposed to predict it. **A 2025 JGR paper concluding independently that self-propping does not
deliver moves your cautionary conclusion from "our model suggests" to "our model and an independent
experiment agree."**

## 5.6 Smaller things worth a line each

- **OG-SC shows eight stress drops during loading** (Fig. 3e) — stick-slip on a saw cut, the same
  signature as SW-S4's staircase. A second dataset showing behaviour your slip-weakening law cannot
  reproduce strengthens the case that it is a **model-form limit, not a calibration failure**
  (`sws4-slips-on-ramps-not-holds`).
- **JRC changes are inside measurement error on two of three specimens** — an independent statement
  of `ye2018-loading-path-cannot-identify-jrc`.
- **They flag single-specimen reproducibility as a limitation.** Cite it when discussing how much of
  your residual is specimen-specific.
- **Their §4.4 raises pressure oscillation** (Elkhoury et al., 2011; Candela et al., 2015) as a way
  to mobilise clogging fines, noting flow rate matters more than amplitude or frequency. **Your
  cyclic decks already exist.** That is a ready-made discussion paragraph connecting your cyclic
  results to a proposed field remedy.
- **Their §4.4 also discusses pressure vs flow control** and argues the final hydraulic state should
  be the same either way. Your decks are pressure-controlled, matching both experiments — say so
  once, and cite them for why it does not matter.

---

# Part 6 — Likely examination questions

**On the experiment and its reduction**

1. *Derive the fracture-angle identity and explain why it is a recovery, not a fit.* — §3.1.
2. *What is the difference between $\sigma_3$ and the "effective confining pressure"?* — §2.4;
   30 = 33 − 3.
3. *Why does shear stress fall during a constant-confining-pressure injection test?* — §3.2(a);
   constant piston displacement means slip unloads the frame.
4. *Given $K_{sys}$, predict the shear stress drop from the measured shortening.* — §2.1. Then:
   *so how many independent measurements does Table 2 contain?* **Two.**
5. *The paper's eq (7) does not reproduce its own Table 2. Diagnose it.* — §2.2; the 12 belongs
   inside the cube-root bracket, and even restored it is not the equation that made the table.
6. *Why is $n = \sin\theta$?* — §3.6; the elliptical section of a cylinder.

**On stability**

7. *Derive the stick-slip criterion for a fracture in a testing machine.* — §3.3. **This is the one
   to be able to do at the board.** Then: *relate it to Hosseini's $\Delta x < L_{cr}$.*
8. *Why does the smooth saw cut burst while the rough shear fracture creeps?* — §3.3, second
   reading. Roughness lengthens $D_c$; lengthening $D_c$ stabilises. Instability is about the slope
   of the strength-slip curve, not its height.
9. *Your three specimens have different fracture angles. Does the frame treat them differently?* —
   §3.2(b); no, $\cos^2\theta\sin\theta$ is flat near 35°, so they agree to 2.4 %.

**On roughness and strength**

10. *What is $Z_2$ and why does the sampling interval matter?* — §3.4.
11. *JRC changed by −0.39 on OG-SH. Is that a measurement?* — §3.4; no, the error is ±2.10.
12. *Write the Barton–Bandis criterion and explain each term's stress dependence.* — §3.5.
13. *One of the paper's specimens implies $\phi_r = 43°$. What is wrong?* — §3.5; a mated tensile
    fracture's interlock is a cohesion, not a friction angle.

**On flow and aperture**

14. *Distinguish mechanical and hydraulic aperture, and explain a ratio of 1600.* — §2.6, §3.7.
15. *Derive the plane-channel and doublet shape factors.* — §3.6.
16. *What does Pedrosa's $\alpha$ mean physically, and is it independent of your closure law?* —
    §3.8; it is a log-space linearisation of it, so no.
17. *Explain in one sentence why self-propping raises $k_0$ and $\alpha$ together, and why that
    defeats it.* — §3.8.

**On your own work, by comparison**

18. *This paper says self-propping fails; yours says it works. Reconcile.* — Different rock:
    quartz 43.5 vs 15 %, grain size 0.5 vs 5 mm, at matched $E$/UCS/tensile strength. §5.4.
19. *A second group reanalysed your four specimens. Did they agree?* — §5.1. Ordering consistent at
    the extremes; be honest that $n=4$ and the middles swap.
20. *Your frame stiffness was inferred and dominates every magnitude. Defend it.* — §5.3.
21. *Their shear fracture loses permeability. Can your model do that?* — Yes, and it predicted the
    sign before this paper: 104-series arm 1. §5.2. But **check that `slip_damage_scale` is
    non-zero in the deck you show them** (§4.3c).

---

# Part 7 — Action items

**Before any HPC job (all are algebra, none needs a run):**

1. **Fix OG-SC's `characteristic_slip_distance`** to below 21.2 µm. As built it cannot reproduce the
   burst that is the specimen's entire result. §4.3(a).
2. **Fix `slip_weakening_residual_friction_angle_degrees` on all three decks** — it is unsubstituted
   in every one, and on OG-SH it makes the law strengthen with slip. §4.3(b).
3. **Set `initial_hydraulic_aperture` from Table 2 stage 1** — 4.87 / 0.10* / 1.03 µm — and widen
   `min_`/`max_hydraulic_aperture` to bracket each specimen's own range. (*OG-T's stage-1 value is
   at the print floor; use its first resolved stage instead.) §4.3(c).
4. **Turn on `slip_damage_scale` for OG-SH.** §4.3(c).
5. **Correct OG-SH's peak envelope** to $\phi_{\rm peak} = 32.71°$, $\phi_r = 24.11°$ — the paper
   says its Figure 3b criterion overestimates. §3.10, §4.3(d).
6. **Rebuild OG-T's envelope as $\phi_r \approx 30°$ + cohesion** rather than $\phi_r = 43.1°$.
   §3.5.
7. **Restructure `kalantar_gate.py`** to two scored channels, $\Delta L_s$ as a frame check, an
   explicit $1/\cos\theta$ slip convention, and no $k$. §4.4.
8. **Update the builder's docstring** — "every constant is derived" is true only of the substituted
   set. Say which constants are inherited and why.
9. Run the §4.5 admissibility checklist, then the ~200 s preload gate for `axial_pres_final`.

**Then:**

10. Submit round 1 (yours to submit — 64 ranks / 64 GB / 48 h scripts are built).
11. Add the Pedrosa $(k_0,\alpha)$ postprocessor so model output is directly comparable to Figure 8.
    §4.1.
12. Build the 111-series Mohr–Coulomb siblings by the `envelope-transfer-between-constitutive-laws`
    recipe, tangent-matched to whatever envelope round 1 actually realises.
13. Mechanism decks (step G), first being the gouge arm on OG-SH.
14. Rebuild or delete `og_sc_theta30_size5.e` before any mesh-convergence claim. §4.6.

**Manuscript (task #113):**

15. §6.7 — the SW-S4 corroboration, phrased as consistency not evidence. §5.1.
16. §5/§6 — the measured frame-stiffness caveat. §5.3.
17. §6.9 — the self-propping negative result. §5.5.
18. A paragraph connecting your cyclic decks to their pressure-oscillation suggestion. §5.6.

**Decisions that are yours:**

19. **OG-T's angle** — 28° primary with the stress columns re-reduced (recommended; 26° cannot be
    realised without contradicting a measured dimension), or 26° primary with the arm already built.
20. **Whether to publish the two paper-level findings.** The OG-T angle error and the eq (7) factor
    are both genuine, checkable errors in a 2025 JGR paper, found by the same method that caught
    SW-T2's angle. Reporting them makes the audit method itself a contribution — the same class of
    error caught twice in two independent datasets, and a reduction equation caught by testing it
    against its own table.
21. **Whether to settle the two ambiguities from the GFZ data release** — the 5 mm borehole inset
    (centre or edge, ~1.2 % on $Q$) and the OG-SC length (100.00 vs 105 mm).

---

## Corrections this document makes to earlier notes

- **`kalantar2025-second-validation-dataset`, "three independent observables per stage"** — wrong.
  There are **two**: $\tau$, $\sigma'_n$ and $\Delta L_s$ are one force measurement. §2.1.
  The same correction applies to `KALANTAR2025_VALIDATION_PLAN.md` §2 step 1 and to
  `kalantar_parameter_audit.py` §2.
- **`kalantar-eq7-does-not-match-its-own-table`, "a numerical factor is wrong"** — true but
  incomplete. The factor is **12, dropped from inside the cube-root bracket**, and the residual
  5.4 % after restoring it is the doublet-vs-channel shape factor. §2.2.
- **`build_110_kalantar_decks.py` docstring, "none is fitted"** — true only of the substituted
  constants; the entire aperture law and most of the traction law are inherited Ye2018 fits. §4.3.
