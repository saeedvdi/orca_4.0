# How to back-analyse a simulation campaign

*A working method, written from the Ye & Ghassemi (2018) four-specimen validation. Every rule
below is followed by the case that produced it, because a rule without its scar is just advice.*

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

**Then audit the outputs against the deliverable.** List every quantity the paper/report needs and
check it exists in *every* case's output. Found this way: three of four specimens cannot plot the
strength-envelope evolution, because those diagnostic channels exist on one deck only.

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

---

## The one-line version

**Measure it yourself; distrust the channel before the model; localise the error in the load
path; then ask whether the knob can reach it — and if the bracket has closed or the shape is
unreachable, say so and stop.**
