# How to back-analyse a simulation campaign

*A working method, written from the Ye & Ghassemi (2018) four-specimen validation. Every rule
below is followed by the case that produced it, because a rule without its scar is just advice.*

> **Method and historical examples.** Numerical values attached to older campaign examples are
> retained as originally analysed. Use `independent_analysis/TABLE2_ERROR_ACCURACY_RANKING.csv`
> for the current recomputed ranking and
> `independent_analysis/CONSOLIDATED_ANALYSIS_2026-08-18.md` for current conclusions.

---

## The shape of the whole thing

Back-analysis is not "look at the plots and guess the next parameter". It is a sequence with a
strict order, and most of the wasted deck generations in this project came from skipping to
step 6.

```
1.  Score it yourself, before reading anyone's interpretation
2.  Suspect the measurement channel before the model
3.  Score against the SOURCE, and know which columns are independent
4.  Normalise, so every observable can sit in one table
5.  Localise: where in time / where in the load path is the error?
6.  Ask if the knob can even do the job     <-- most people start here
7.  Design an experiment that can FAIL
8.  Price the fix before you build the deck
9.  Write the falsifiable prediction into the deck header
10. Record the negative results
```

Two things sit outside that sequence and are covered at the end: **auditing the plumbing**, which
comes before all ten and has to be redone after any mesh or geometry change, and **building the
baseline model** for a two-law comparison, which comes after them and has its own way of going
wrong.

---

## 1. Score it yourself first

**Rule.** Before you read someone's report — your own from last week, a collaborator's, an
agent's — reproduce the numbers from the raw output. Then compare *your* numbers with *their*
numbers, not their conclusions.

**Why it pays.** If your independent score lands within a fraction of a percent of theirs, the
*measurement* is sound, and any disagreement is about **interpretation**. That is a completely
different and much cheaper problem than "one of us computed it wrong". If the numbers diverge,
you have found a bug before you have argued about physics.

> **Case.** My scoring gave 10.5 / 6.4 / 10.9 / 7.4% against a report's 11.2 / 6.7 / 11.4 /
> 7.75%. Close enough that the report was trustworthy — so I stopped re-checking arithmetic and
> went straight to why we disagreed about which case was better. The disagreement turned out to
> be a broken plotting channel, found in one afternoon instead of a week.

---

## 2. Suspect the channel before you suspect the model

**Rule.** A number that looks wrong is a *reported* number. Before attributing it to physics,
establish that it measures what its name says.

**The decisive test, in order:**

1. **Grep for every consumer of the suspect quantity.** If it appears only inside
   `[Postprocessors]` — no `Function`, `BC`, `Material` or `Control` reads it — the physics
   *cannot* have been affected and **no re-run is needed**. Correct it offline.
2. **Compute every sibling operator at one early time.** Quantities that should agree, computed
   different ways, either agree or they do not. **A lone outlier is a frame or reporting error;
   a common offset is physics.**
3. **Find confirming arithmetic inside the output itself.** Not from your head — from a number
   the run already printed.

> **Case A.** `differential_stress_mpa_pp = (sigma1_pp - 30e6)*1e-6` subtracts a **total**
> confining stress from a **skeleton** axial stress and read `alpha*p ≈ 3.5 MPa` low for every
> run in the campaign. Caught by computing three siblings at t = 150 s on SW-S4: the load-cell
> reaction gave 28.64 and `sigma1 − sigma3_bulk` gave 29.01 against a digitised 29.09, while the
> broken one gave 25.45. The confirming arithmetic was in the CSV: `sigma3_bulk_mpa_pp` = 26.48
> = 30 − 0.6 × 5.87, which *proves* `sigma3_bulk` is the skeleton frame. Postprocessor-only, so
> no re-run — and one specimen's apparent "residual over-weakening" vanished entirely.
>
> **Case B.** Three of four reported SW-S4 symptoms were one bug: `PointValue` postprocessors
> left at the *old* mesh's borehole coordinates after a mesh swap, sampling 5.86 mm off-node.
> The BC itself was always correct. Note the error signs were **not** intuitive: the inlet read
> 1.90 MPa low, the outlet read 2 MPa *high*, they **cancelled** in one derived channel and
> **added** in another. Never assume a sampling error biases every derived quantity the same
> way — recompute each one.

**Corollary: rename, don't redefine.** When a channel's name has been wrong for a campaign,
repoint the consumers at a correctly-named sibling. Silently changing what an existing name
means poisons every earlier result that quoted it.

### 2a. The reporting path can be *fitted*, not just broken

Cases A and B above are accidents — a wrong frame, a stale coordinate. There is a worse version:
a material can expose parameters that the source itself labels **OUTPUT ONLY**, which change no
physics but reshape a reported quantity. A calibration can then land on them, and the scorecard
cannot tell.

**Rule.** Diff the **output-only** parameters across cases before you compare their scores, not
just the constitutive ones. If one case sets one off-default and the others do not, its column is
not commensurable with theirs.

> **Case.** `ADOrcaBartonBandisContactTractionFastAD` declares
> `reported_reversible_normal_opening_scale` (default 1.0) and
> `reported_reversible_normal_opening_retention_fraction` (default 0.0), documented as touching
> "aperture, permeability and flow" not at all — only the reconstruction of
> `normal_opening_total`, which is exactly the column the gate scores for `d_n`. **One specimen of
> four** ran 0.758 and 0.552. Scoring `d_n` off the raw kinematic jump instead:
>
> | specimen | via `normal_opening_total` | via raw jump | delta |
> |---|---|---|---|
> | SW-T1 | 9.06 | 9.06 | 0.00 |
> | SW-T2 | 2.06 | 2.06 | 0.00 |
> | **SW-S3** | **2.46** | **7.42** | **+4.96** |
>
> The two decks at defaults agree **exactly**, which is what proves the knobs and not the channel
> choice are the effect — the same sibling-agreement test as Case A, run across specimens instead
> of across operators. SW-S3's headline mean moves **3.59 % → 4.58 %**, and its rank moves with it.

Note the shape of the evidence: the *absence* of a difference on the control cases is what makes
the difference on the suspect case interpretable. Always look for a case where the suspected
mechanism is switched off, and check it reads zero.

**Corollary: a harmless-looking inconsistency and a real one look identical until you measure.**
On the same audit, a fourth specimen scored `d_n` off a *different channel name* than the other
three. That looks like the bug and is not one — with the knobs at defaults the two channels are
the same number. Fix it for consistency, but do not report it as a defect; the defect was
elsewhere.

### 2b. Harmonise the instrumentation before comparing cases

**Rule.** Cases that will be compared must emit the **same set** of channels. Otherwise the
comparison is silently restricted to the intersection, and whichever question needs the missing
channel simply cannot be asked of three of your four cases.

> **Case.** One specimen carried 87 postprocessors and the other three carried 70. The extra 17
> were the strength-envelope evolution, the loading-frame diagnostics and the bulk kinematics —
> i.e. precisely the channels you reach for when a specimen misbehaves. Three of four specimens
> could not plot their own envelope evolution. Harmonising to one 91-channel set was a
> prerequisite for the cross-specimen comparison, not a tidy-up.
>
> Watch the per-specimen constants when porting: the bulk-kinematics channels resolve onto the
> fracture with `sin θ`/`cos θ`, and copying the donor specimen's θ would have produced four
> plausible, wrong curves. Same for probe locations — put them on **one stated rule**
> (here `z = L/2 ± 50 mm`, a 100 mm gauge on every specimen) rather than inheriting one
> specimen's ad-hoc values.

---

## 3. Score against the source, and know which columns are independent

**Rule.** Score against the paper's **table**, not its figure. A table has exact values at
defined states; a figure is a curve you eyeball, and eyeballing rewards whichever case looks
tidiest.

**Then strip the table down to what is actually independent.** Tabulated columns are frequently
derived from one another, and scoring a derived column double-counts its parent.

> **Case.** Ye & Ghassemi Table 2 prints eight quantities per stage. Only **five** are
> measurements. The paper back-computes hydraulic aperture `a_h` from the measured flow `Q`
> through the cubic law and then *defines* `k = a_h²/12` — so `a_h` and `k` carry no information
> beyond `Q` and are reported but not scored. Separately, `sigma'_n` and `tau` are two
> projections of one stress state through eqs (3)/(4): their errors always agree and are **one**
> vote, not two.

**Also: re-derive the source's own metadata from the source's own data.** Printed values can be
wrong; internally consistent data usually is not.

> **Case.** Dividing eq (3) by eq (4) removes the differential stress and leaves
> `tan θ = (σ'ₙ − σ₃ + P_p)/τ`, evaluable at all eleven tabulated stages. It returned the printed
> fracture angle to within 0.03° for three specimens and **30.001° for the one that prints 31°**.
> The printed angle was wrong, and earlier calibrations had silently absorbed the 1° error
> (at 30° instead of 31°, `τ/σ'ₙ` rises 2.5% at the same state — a whole injection step of
> strength).

---

## 4. Normalise, so every observable can sit in one table

**Rule.** Divide each observable's RMSE by its own **measured range**. Then a flow rate of
0.005 mL/min and a shear traction of 74 MPa are directly comparable, and you can average them.

Without this you cannot even ask "which case is better overall", and you will unconsciously
weight whichever quantity has the biggest numbers.

Report **both** the normalised score and the raw absolute error. The normalised score ranks
cases; the absolute error is what you reason with physically ("+1.4 MPa of residual traction" is
a thought you can have; "8.3%" is not).

### 4a. Exclude the rows that are constructed rather than measured

**Rule.** A row the scoring procedure *forces* to agree is not a test. Drop it, state that you
dropped it, and state the resulting `n` beside every statistic. This is a convention, so it only
has to be **consistent and declared** — but an undeclared one silently changes headline numbers.

> **Case.** Table 2 prints `d_n = d_s = 0.000` at stage 1 for all four specimens and the gate
> zeroes the model there, so stage 1 is exactly zero by construction for both displacements.
> Including it dilutes their RMSE by exactly `sqrt(10/11)` — a 4.6 % reduction that lands on two
> of five observables. Two write-ups included it and two did not, so the four specimens were not
> comparable with each other: SW-T1 read 4.34 % instead of **4.44 %**, SW-S3 3.55 % instead of
> **3.59 %**.

The general form: **look for any row whose value follows from the procedure rather than from the
run** — a datum row, a normalisation anchor, an initial condition you imposed. It belongs in the
comparison table (so the reader can see it agrees) and not in the error statistic.

---

## 5. Localise before you diagnose

**Rule.** "The transition is too fast" is not a diagnosis. **Window the error against the thing
that drives it** — the load stage, the pressure step, the time segment — and tabulate.

> **Case, and the single most productive five minutes of the campaign.** SW-S4's transition
> "looked compressed". Splitting the measured slip by injection window turned that into:
>
> | window | injection | measured | model |
> |---|---|---|---|
> | 1015–1120 s | **ramp** 16→20 | 15.8 µm | 2.3 |
> | 1120–1310 s | **hold** 20 | 2.1 µm | 2.9 |
> | 1415–1600 s | **hold** 24 | 1.3 µm | **34.1** |
> | 1600–1710 s | **ramp** 24→28 | 32.2 µm | 17.2 |
> | total | | 79.5 µm | 82.8 |
>
> Read the table, not the curve: **the specimen slips only while σ'ₙ is falling and arrests the
> instant it stops.** The total slip budget is right to 4%; only its distribution in time is
> wrong. That is a completely different defect from "too fast", and it is not reachable by any
> parameter — see §6.

**The generalisation.** When totals are right but the shape is wrong, the missing ingredient is
almost always a *dependence*, not a *magnitude*: the law lacks a term in some variable
(here `dσ'ₙ/dt`). Look for what the data respond to that the model does not read.

---

## 6. Ask whether the knob can even do the job

Three questions, in this order. Most sweeps that were later regretted skipped all three.

### 6a. Is the parameter identifiable on this loading path?

**Rule.** Two parameters that move an observable the same way over the range you actually sample
are one parameter. Sweeping them separately is theatre.

> **Case.** A cohesion (a strength *level*) and a JRC (a strength *slope*, since
> `JRC·log₁₀(JCS/σ'ₙ)` tilts the envelope) were bracketed as a discriminating pair. Over the
> sampled `σ'ₙ` range their margin curves differed by a near-constant 0.9 pp and their fitted
> slopes by **3%**. The path is too narrow for the log term to bend measurably. Two deck
> generations had been designed around a slope story this dataset cannot test either way.
> **Consequence:** keep the paper's measured JRC, let cohesion carry the fit, and never quote a
> fitted "effective JRC" as roughness evidence on a single monotonic path — it is a
> reparameterised cohesion.

### 6b. Has the bracket closed? (the interpolation test)

**Rule.** For a two-arm bracket on parameter `p`: interpolate **each observable separately**
between the arms and solve for the `p` that would land it exactly on the measurement.

- **All estimates agree** → the parameter is *identified*. Both arms straddle it, a third deck
  changes the score by hundredths of a percent. **Stop sweeping.**
- **They split into groups** → **one knob is being asked to do two jobs.** Do *not* sweep it
  again. Go find the second defect (§6c).

> **Case.** Residual cohesion, three specimens:
>
> | | τ | σ'ₙ | d_s | d_n | Q | |
> |---|---|---|---|---|---|---|
> | SW-T2 | 9.15 | 9.15 | 9.65 | 9.36 | 8.51 | ✅ identified, ±0.6 MPa — **done** |
> | SW-T1 | 8.48 | 8.47 | 9.05 | **12.5** | **11.7** | ❌ split: stress vs displacement/flow |
> | SW-S3 | 0.76 | 0.73 | **1.40** | **1.22** | **1.81** | ❌ split, same signature |
>
> This one table ended a calibration that had been running for five deck generations. A single
> aggregate score cannot distinguish "nearly done" from "pulling in two directions"; the
> per-observable interpolation can.

### 6c. When it splits, find an *independent* measurement of the suspected cause

**Rule.** Do not reason about the second defect — **measure** it, using a quantity that does not
involve the parameter you were sweeping, and **measure the same thing on the cases that work**
so you have a control.

> **Case.** SW-S3's split suggested the strength/slip *relation* was off rather than the strength
> level. Test: secant τ–slip stiffness across the slip event (`Δτ/Δd_s` between the two tabulated
> stages that straddle it), model ÷ measured:
>
> | SW-T1 | SW-T2 | SW-S4 | SW-S3 |
> |---|---|---|---|
> | 1.00 | 0.98 | 0.93 | **0.81** |
>
> Three of four reproduce the experiment to within 7%. SW-S3 alone is 19% too compliant, so a
> given slip sheds too little traction and **no** residual cohesion can satisfy both `τ` and
> `d_s`. The control column is what makes this evidence rather than a story.

### 6d. Is it a parameter at all, or the model form?

**Rule.** Ask: *can any value of this parameter produce this shape?* If the answer is no, stop.
Say so, in writing, and move on to the next specimen.

> **Case.** A slip-weakening law `W = exp[−(s/D_c)^m]` has no `dσ'ₙ/dt` dependence. Nothing you
> do to `D_c` can make it arrest during a hold — and indeed **both** bracket arms scored three
> times worse than the centre (§7). Capturing the measured staircase needs a rate- or
> state-dependent term in `τ_lim`. That is a constitutive addition, not a calibration, and
> saying so plainly is a *result* worth publishing, not an admission.

---

## 7. Design an experiment that can fail

**Rule.** Bracket **in both directions**. A one-sided sweep can only ever tell you "better" or
"worse"; a two-sided one can tell you **"you are already at the optimum"**, which is the answer
that ends the work.

**And deliberately run one arm you expect to be wrong.** If it scores as well as the arm you
expect to be right, your hypothesis about what that parameter controls is dead — cheaply.

> **Case.** `D_c` bracketed at 40 / 74.5 / 120 µm. Table-2 mean nRMSE: **16.89 / 6.05 / 18.87**.
> Both arms failed, in *opposite* ways (40 µm overshot the final slip by 26%, 120 µm undershot by
> 29%). That is not a disappointment — it is proof that 74.5 µm is an optimum and that the
> residual error is not a regularisation artefact. One batch bought a permanent answer.

---

## 8. Price the fix before you build the deck

**Rule.** Before proposing a change, compute what it costs on the observables that are currently
*correct*. Sensitivity first, deck second.

> **Case.** SW-S4's remaining error is one stage: the model misses the experiment's first slip
> burst. The strength margin `m = (τ_lim − τ)/τ_lim` reads +7.16% in the 16–18 MPa bin and +1.40%
> in 18–20, against a measured burst starting at 17.9 MPa. Shaving ~1.7 pp of margin (≈ 0.2 MPa,
> or −0.39° of φ_r) would start it on time. But the model would then keep sliding through the
> 20 MPa hold exactly as it now does through the 24, so stage 5's slip error goes from +6 µm to
> roughly +20 µm. **It buys one stage and loses another.** That arithmetic — done in ten minutes,
> before writing any deck — cancelled a batch and closed the specimen.

**Related rule: know when your target is quantised.** If the load is a staircase, failure
happens at the step where the strength margin crosses zero, so a small strength deficit does not
advance failure proportionally — it advances it by a **whole step**. "430 s early" then does not
mean "tune the timing"; it means *one step too weak*, and there is no parameter value that lands
you between steps.

**And know your resolution floor.** On SW-T1 the margin decays only 0.09 pp across the entire
28 MPa plateau, so placing the onset 70 s later needs the plateau-entry margin inside a 0.09 pp
window — **67 kPa of cohesion**. The onset is not tunable below ±70 s with a static envelope.
Say that out loud rather than sweeping into the noise.

**The same discipline applies to a geometric fix: enumerate what the mesh can actually reach.**
Correcting a deck is not the same as correcting the run. When the quantity you are fixing lives on
a discrete grid, compute the neighbouring attainable values before claiming the fix closed
anything.

> **Case.** One deck's injection coordinate was 1.678 mm off the nearest interface node.
> `use_closest_node = true` had silently snapped it, so the run had always used the snapped pair
> and the "fix" — writing the true node into the deck — changes **no number**. The interesting
> question is what remains. The intended injection–production separation was 72.690 mm; the pair
> actually used spans 69.335 mm, **4.62 % short**. Enumerating the symmetric node pairs on that
> mesh gives 69.335 and 78.002 mm and nothing between — the snapped pair is already the closer of
> the two, so **mesh 5 cannot do better without remeshing**, and the residual is a stated
> limitation rather than an open action.
>
> Then trace it forward. `Q = (W/L)/(12 µ) · a_h³ · Δp` with `W/L` a fixed constant inverted from
> the source table, so the path length enters through the measured pressure drop and a
> first-order `Q` bias of about that size is expected — on the specimen that happens to have the
> campaign's largest `Q` error. And the finer mesh reaches 71.501 mm, so the convergence pair
> differs by **3.1 % in source separation, which is not discretisation**: a control that was never
> as clean as it looked. None of that is visible from "the coordinate was wrong, now it is right".

---

## 9. Write the falsifiable prediction into the deck header

**Rule.** Every deck header states (a) its parent, (b) the *one* thing that changed, (c) the
derivation of the new value, and (d) **what result would prove the hypothesis wrong**.

This is not documentation. It is what makes the next run informative instead of merely different.
When the result arrives you either confirm or kill the idea in one reading, and — critically —
you cannot retro-fit the story to whatever came back.

> **Template in use:** *"d_n at stage 11 should move from −0.1387 toward the measured −0.113. If
> d_n does NOT move, the retention branch is not the carrier, the gap is in the shear-dilation
> recovery instead — which is a model-form limit, not a parameter — and SW-T1 is final as it
> stands."*

**Change one thing per deck.** Two changes in one deck buy one bit of information for two jobs'
worth of compute.

---

## 10. Record the negative results — and correct yourself in the record

**Rule.** The expensive findings are the ones that say *don't go there*. They are also the ones
that evaporate if you only write down what worked, and the ones you will otherwise re-derive in
six months.

Write down, explicitly:

- what was tried and **failed**, with its score;
- what the loading path **cannot** identify;
- which earlier conclusion this **overturns**, named, so a future reader who finds the old
  document knows it is superseded.

> **Case.** An earlier back-analysis of mine concluded the missing negative feedback was on the
> strength *slope*. The next bracket disproved it: the two arms' slopes differed by 3%. That
> correction went into the deck headers, the commit message and a standing note — because the
> old conclusion was written down persuasively enough to mislead the next person, including me.

---

## Before the physics: audit the plumbing

Configuration changes have **silent** failure modes, and a silent failure looks exactly like a
constitutive error. After **any** mesh rebuild, mesh swap, or geometry change, check these before
you interpret a single result:

| what | why it fails silently |
|---|---|
| **Injection/source node pinning** | `use_closest_node = true` never errors. If the coordinate misses the fracture plane it pins to the nearest **bulk** node and the run drives the matrix instead of the joint. Verified case: on one size-3 mesh the size-5 borehole coordinate snapped to a bulk node **584.9 µm** away, beating the interface node at 956.8 µm. Coordinates are **resolution**-specific, not just geometry-specific — the other three specimens on the same rebuild were fine, so it is not predictable from the offset alone. |
| **`PointValue` coordinates** | Stale after any mesh move, with no warning. Prefer `AverageNodalVariableValue` on a nodeset, which follows the mesh. |
| **Nodeset / boundary names** | A rename mismatch fails at setup — that is the *good* case. |
| **Output `file_base`** | A copied deck inherits its parent's path and silently **overwrites the parent's results**. Grep every new deck for the parent's name. |
| **Solver caps vs. the knob you think you're turning** | One "diverged" batch was blamed on the Krylov restart when the real cap was the linear iteration limit. Read which limit the message actually names. |
| **Stateful properties that branch on "hold previous value"** | That branch also runs at initialisation and can pin the property at 0 forever. |
| **Output-only material parameters** | They change no physics, so nothing you check about the physics will catch them — but they reshape a scored column, and a calibration can land on them. Diff them across cases; see §2a. |
| **Instrumentation asymmetry between cases** | Nothing errors when a case is missing a channel; the comparison just silently narrows to the intersection. Count the postprocessors per case and expect one number. |
| **Per-specimen constants inherited when porting a channel** | A `sin θ`/`cos θ` or a probe coordinate copied from the donor case produces a plausible, wrong curve rather than a failure. |

**Then audit the outputs against the deliverable.** List every quantity the paper/report needs and
check it exists in *every* case's output. Found this way: three of four specimens cannot plot the
strength-envelope evolution, because those diagnostic channels exist on one deck only.

**And audit the frame constants against the geometry each case actually loads.** Where a deck
hard-codes trigonometric constants for a reporting frame, recover the angle from the mesh itself
(an SVD plane fit on the interface nodeset) and check it against the constants — per deck, not per
specimen family.

> **Case.** Doing this across a deck estate found a Mohr-Coulomb pair in which the **two
> specimens' angles had been swapped**: a 32° mesh carrying 31° constants and a 31° mesh carrying
> 32°. At the campaign's differential stress that is ≈ 2.3 MPa on `σ'ₙ` — about **three times the
> best specimen's entire `σ'ₙ` RMSE** — so every strength parameter fitted in those decks was
> fitted against mis-resolved stress and none of it could be ported. A one-line check retired four
> decks.

---

## Building the baseline for a two-model comparison

A back-analysis usually ends with "model A reproduces the data this well, and here is the residual
we cannot remove". The next thing anyone asks is whether a simpler model would have done as well.
That comparison has its own failure mode, and it is not the one people expect.

**The trap.** Re-calibrating the baseline B independently produces a comparison of *two
calibration efforts*, not of two constitutive laws — and whichever model you tuned harder wins. A
baseline that was fitted for one afternoon against a primary model fitted over twenty deck
generations tells the reader nothing.

**Rule.** Build B by **transferring A's calibrated envelope**, and hold everything that is not the
law itself byte-identical.

**Holding everything else fixed.** Clone the primary deck and replace exactly one block. Then
*verify* the claim rather than asserting it: diff the pair and classify every changed hunk. On the
eight pairs built this way, the diff reduced to the material block, a 7-for-7 postprocessor swap,
the AD-flavour promotions the second law forces, and one flag — nothing else. Mesh, source
coordinates, boundary conditions, schedule, frame constants and solver all verified equal.

**Transferring the envelope, in this order:**

1. **Look for the branch that transfers exactly, and take it first.** The Barton-Bandis
   slip-weakened envelope is `τ = c_res + σ'ₙ·tan(φ_r,sw)` — already a straight Coulomb line, so
   the residual branch transfers with zero error. Do the exact part before approximating anything;
   it also tells you how much of the difference between the laws is real.
2. **Match the peak at the point that decides the outcome, not on average.** Least-squares over
   the whole stress range spreads the error everywhere, including at onset. Instead **tangent
   match** — value *and* slope — at the onset normal stress, i.e. the last stick stage's `σ'ₙ`
   from the source table. The payoff is that the two models' strength margin over the measured
   `τ` becomes identical at every stick stage, so **slip onset is inherited rather than
   refitted**. That matters precisely because onset is quantised by the load step (§8): a baseline
   that fires one step early would swamp the constitutive signal you are trying to measure.
3. **Correct for the starting internal state.** If B's strength interpolates on a normalised
   internal variable, the match must be divided by that variable's initial value or B starts
   weaker than A. Here `Rbar₀ = (R₀ − R_res)/(1 − R_res)` was 1.00, 1.00, 0.60 and 0.389 across
   four specimens — ignoring it would have made two of the four baselines ~2× too weak at onset,
   and the resulting "Mohr-Coulomb fails early" conclusion would have been an arithmetic slip.
4. **Copy verbatim anything a *downstream* object consumes.** Trace the internal variables out of
   the block you are replacing. `roughness_state` feeds the permeability material and therefore
   the scored flow rate, so its initial value, residual value and decay distance had to match A's
   exactly, or the flow would differ for reasons having nothing to do with shear.
5. **Then state what the two laws are still free to disagree about** — that list *is* the result.
   Here: envelope curvature (they separate by up to 1.25 MPa at the far end of the unloading
   branch), the shape of the weakening path between identical endpoints, and B having one
   characteristic distance where A has two. Where that last one forces a choice, say which way you
   chose and why: the shared distance was set from A's *roughness* length rather than its
   *strength* length, to keep the scored flow path identical, which leaves B's strength weakening
   over a slightly different distance on two of four specimens. A known, priced difference between
   the laws is a finding; an unstated one is a confound.

**Report the transfer accuracy as a number**, the way you would report a score: max |B − A| over
the stages that decide onset (0.015–0.091 MPa here) and over the full range (0.03–1.25 MPa). If
the first number is not small, the comparison is not controlled and nothing downstream is
interpretable.

**Finally, write down what a *build* error would look like, as distinct from a physics result.**
The baseline is expected to score worse — that is the point. So state in advance the signatures
that would instead mean the swap leaked: onset landing on a different load step than the primary
(the peak envelopes agree to 0.09 MPa, so it must not), flow differing before anything yields, or
any difference at all at stage 1 where both laws are still on the same elastic branch. Without
that list you cannot tell a result from a bug.

---

## Smells — when to stop and check something

- An error that is **constant in time** → a frame, datum or unit error, not physics.
- Two channels that should agree and differ by a **round number** (`α·p`, a factor of 2, a factor
  of 12) → look for the formula, not the calibration. A factor of 2 on a boundary quantity is
  very often a double-counted sideset.
- A parameter that **has never been varied on this specimen** but is inherited from another →
  that is where an unexplained per-specimen difference lives. (All four decks here carry one
  specimen's normal-closure constants.)
- **Two cases scoring within 0.1%** → not "pick the better one". It means the parameter between
  them does not matter over that interval, which is *information*.
- A quantity that is **right at the end and wrong in the middle** → a distribution problem, not a
  magnitude problem. Go to §5.
- **One case wins on stress and another wins on displacement** → §6b, every time.
- **One case scores conspicuously better on exactly one observable** → diff its *output-only*
  parameters against the others before you explain the win physically. §2a.
- **Two cases that should differ on a channel agree to the digit** → that is a control reading
  zero, and it is evidence, not a coincidence. Use it to isolate the case that does differ.
- **A case emits a different number of channels than its siblings** → the comparison you think you
  are making is narrower than you think.
- **A headline number that moves when you change nothing but the convention** → the convention was
  never declared. §4a.
- **A geometric "fix" that changes no result** → correct, and not the end of it: enumerate what the
  discretisation can actually reach and price the residual. §8.

---

## Anti-patterns

| don't | do |
|---|---|
| Tune to a plot | Tune to a table with defined states |
| Sweep the parameter you swept last time, harder | Run the closure test; if it is identified, stop |
| Change two things per deck | One change, one derivation, one prediction |
| Report "it looks better" | Report a normalised score against named columns, and the absolute error |
| Treat a derived column as an independent check | Trace how the source computed it |
| Assume a bad number is a bad model | Check who consumes the channel; check its siblings |
| Bury the failed arm | It is the most reusable thing you produced |
| Keep going when the shape is unreachable | Name the model-form limit and publish it |
| Fit an output-only knob | Fit physics; if a reporting knob is off-default, disclose it beside the score |
| Re-calibrate the baseline model independently | Transfer the primary's envelope so the comparison isolates the law |
| Compare cases with different channel sets | Harmonise the instrumentation first, then compare |
| Score a row your own procedure forced to agree | Exclude it, declare it, print `n` |
| Call a coordinate fix "done" because the deck now matches | Enumerate the reachable values and price what is left |

---

## The one-line version

**Measure it yourself; distrust the channel — and the reporting knobs behind it — before the
model; localise the error in the load path; then ask whether the knob can reach it. If the bracket
has closed or the shape is unreachable, say so and stop. And when you finally compare two models,
transfer the calibration rather than repeating it, so the comparison is of the physics and not of
how hard each one was tuned.**
