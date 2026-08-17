I need to get oriented on the scope here: independently back-analyzing SWS4, SWS3, SWT2, and SWT1 samples, checking whether lowering regularization for SWS4 lets me capture each step, and cross-referencing everything against Table 2. Then I need to sort which cases are finalized versus which still need more sweeping, and for the finished ones, produce an MD file per sample along with paper notes.

For the final deck, I need to include a Table 2 comparison with errors and justification, and make sure mesh 3 and mesh 5 are fully correct with all results exported for the paper. Let me start by locating the downloaded results and doing a broad scan of the directory to be efficient.

Ran 2 commands
With all 16 CSVs downloaded, I need to do independent scoring now. Let me check what Table 2 in the paper contains by searching the repo for references to it, and locate the validation data files and notebook structure.

Ran 2 commands
I need the actual Table 2 data, so I'm looking for the parameter audit script and the extracted data.

Ran 2 commands
There's a scripts/table2_gate.py file I should check — it probably already handles scoring decks against Table 2.

Ran 2 commands
table2_gate.py already does what's needed, so I'll read through the rest of it and then run it against all 16 CSVs.
Read table2_gate.py middle
Task #79 is confirmed as current. I want to run table2_gate.py across all 16 CSVs, but first I'll check its usage and test it on the 4 SWS4 cases to see the output format.

Ran 2 commands
I need to check how find_deck locates the .i file one directory up, since the stem includes the _hpc suffix, and I should look at the argparse setup for the --tag option.
Read table2_gate argparse
I realize `--tag hpc` will strip the `_hpc` suffix, so I'll just run all 16 configurations. I'm setting up a driver to run each one, write out the csv results, and then aggregate them afterward.
Ran table2_gate on all 16 CSVs
All 16 runs completed, so now I'm writing a script to aggregate the results, reading each CSV output and comparing mean absolute error and percentage error per observable, plus computing a combined normalized score. I'm also confirming the Table-2 gate aligns with the paper's own stage-level comparison across the 11 stages, which is the benchmark the user wants.
Aggregate Table-2 scores
This is the independent Table-2 assessment. For SWT1, 91_02 wins decisively over 90_01, confirming both reports agree 91_02 is mechanically best there. Now I'm checking SWT2's numbers to see which variant comes out ahead.

91_08 lowering D_c made the transition sharper and earlier rather than more staged, overshooting slip to 0.10 mm in one big drop instead of matching the measured curve's three distinct stages. So D_c isn't the right knob for capturing the staircase — I need to think about what actually drives those steps, likely tied to the injection pressure staircase itself rather than the weakening distance.

Actually, what arrests slip at each step in the experiment is the load frame itself: as the specimen slips, differential stress drops, reducing τ and halting slip. The model does capture this unloading, but its weakening runs too fast relative to frame stiffness, so it blows through all three steps at once instead of pausing between them — meaning the real controlling parameter is the ratio of weakening rate to frame stiffness, not D_c alone, though raising D_c does seem to produce a more staged response in the dotted curve.

It still under-slips and stalls at too-high stress though, so I should stop speculating and actually pull the slip and σ_d time histories for SWS4 to see the real step structure. I also want to check the exponent m, which controls the sharpness versus tail of the decay — a separate lever from D_c — by looking at the SWS4 deck's BB parameters.
Inspected SWS4 BB params
I found the slip weakening exponent is 1.10 and the characteristic slip distance is 7.45e-5. Now I want to examine the SWS4 time series to see whether the slip stages align with injection steps, so I'm pulling the relevant columns to check this quantitatively.

Ran 2 commands
I want to examine the SWS4 step structure by computing the rate of change of slip over time for both the measurement and each model, along with the strength margin, to see whether lowering the regularization would capture each step. I'm putting together a focused analysis script for this.
Measured SW-S4 slip stage structure
I'm seeing the slip data break into distinct bursts separated by quiet periods—an initial burst around 1015-1120s, a quiet stretch, then a second burst around 1310-1415s with a larger jump, followed by another quiet period.

Now I want to cross-reference these burst timings against the injection pressure staircase in the figure, checking what pressure level corresponds to each burst onset at 1015, 1310, and 1600 seconds.
Align SW-S4 slip bursts to injection staircase
This is the key finding: the measured SW-S4 slip bursts align with the pressure ramps, not the plateaus. Burst 1 (1015–1120 s) spans the ramp from 16 to 20 MPa and extends slightly into the start of the 20 MPa plateau, while the quiet period from 1120–1310 s covers the remainder of that plateau.

Burst 2 (1310–1415 s) tracks the ramp from 20 to 24 MPa into the start of the 24 MPa plateau, followed by quiet through the rest of that plateau. Burst 3 (1600–1710 s) similarly spans the ramp from 24 to 28 MPa into the start of the 28 MPa plateau, after which the specimen locks.

So the specimen slips only while pressure is rising and arrests the moment it stops — the classic signature of marginal equilibrium at the failure envelope rather than slip-weakening behavior. As pore pressure rises, effective normal stress and strength fall, so the joint slips just enough to shed shear stress back onto the envelope; once pressure plateaus, τ sits exactly at τ_lim and slip stops. This means the 1000–1700 s window isn't governed by weakening at all — it's envelope-following, with slip magnitude at each stage dictated by the loading frame.

The model's slip-weakening law, once triggered, releases strength faster than the frame can unload, collapsing all three steps into one event — so lowering D_c would only make this worse, as the 91_08 test already showed empirically. Raising D_c alone (as in 91_07 with 120 µm) stalls at too-high stress and under-slips instead. Capturing each step really requires the joint to sit at the envelope with essentially no net weakening from ~1000 s onward, so slip tracks the envelope quasi-statically, with the measured slip of 0.079 mm arising from frame compliance times the roughly 10.2 MPa stress drop rather than from weakening itself.

I'm working out that this implies an effective slip stiffness around 129 GPa/m for the combined frame and specimen. With the model's D_c at 74.5 µm — comparable to the total slip of 79 µm — the weakening function drops from 1 to about 0.37 over the whole event, meaning the weakening is essentially co-scaled with total slip, which explains why the model produces one smooth avalanche instead of discrete steps.

I'm realizing the correct fix isn't about slip-driven weakening at all — the strength drop should instead track the normal stress decline as pore pressure rises, reaching residual quickly via a small D_c, while the envelope itself carries the staircase behavior. But that's exactly what 91_08 tried with a small D_c, and it produced a runaway single event because the residual envelope was too weak to sustain equilibrium, causing the whole system to collapse at once rather than step through stages.

So the real fix needs a small D_c paired with a residual envelope strong enough that the joint re-locks at each new normal stress level — which matches what SW-S3 did by adding residual cohesion, collapsing the error metrics dramatically. Now I want to check whether SW-S4's residual envelope sits at the right level, so I'm computing the implied friction angle at several unloading stages from the table data, and I notice something odd: shear stress actually decreases as normal stress increases during unloading, which isn't simple frictional behavior — it suggests the joint may be locked rather than sliding during that phase.

That points to the joint staying locked through unloading while stress just relaxes, with slip held constant, meaning the residual envelope only needs to exceed the peak shear value reached before unloading begins. I'm now digging into how the residual friction angle parameter actually factors into the slip-weakening formula, since there seem to be two different residual friction angle terms in the deck that might serve different roles.

Rather than tracing through the constitutive code further, I should just measure the model's behavior empirically — compute its τ_lim versus σ'n and slip trajectory for 90_08 and compare against what the staircase pattern actually requires. The key insight is that 90_08 already scores well on Table 2's mean nRMSE and slip MAE, since that table only samples plateau endpoints and misses the within-stage timing steps entirely. I want to quantify exactly what the model does during the three burst windows versus the real data, and trace where the slip occurs for 90_08.
Compared model slip per burst window on SW-S4
This is decisive and gives a much better answer than I could have guessed. The measured data shows slip delivered in three bursts aligned with pressure ramps, each hold quiet, with percentages of 21.6%, 24.2%, 50.9%, 52.6%, and 93.1%. Looking at 90_07/90_08, the first burst is almost entirely missing compared to the measured values.

The model actually slips during the 24 MPa hold instead, exactly backwards from measured behavior — its slip isn't ramp-locked but an avalanche starting late and continuing through the hold. Comparing 91_08 (less regularization) and 91_07 (more regularization), 91_08 is catastrophic with 67 µm of slip during the 20 MPa hold running away in a single event and overshooting to 0.100 mm, while 91_07 under-slips and smears the slip out later. So lowering regularization makes the step structure worse, not better — 91_08 was run precisely to test this and produced the largest runaway in the campaign.

The underlying reason is that slip-weakening can't reproduce the measured pattern of slip only while σ'n falls and arrest when it stops falling, since W(s) is monotonic in s with no memory of dσ'n/dt.

I'm checking whether the measured joint instead follows a single Coulomb envelope as a function of σ'n alone, with no slip-memory — essentially non-cohesive, rate-independent behavior that tracks the envelope from the start. I'm fitting a line through the sliding-stage data points from the loading branch and checking the fit against the middle point, getting good agreement (~0.13 MPa residual), which supports the envelope-following hypothesis.

The fitted line τ = 0.823σ'n − 9.48 MPa matches the recorded μ=0.804 fit almost exactly, confirming the relationship. But converting to Barton-Bandis friction angle terms, the implied μ rises steeply with σ'n (0.204 at low stress to 0.409 at high stress) — which is the opposite of how BB curvature normally behaves, since BB predicts μ decreasing with σ'n. This means the sliding path can't be a standard BB envelope with positive JRC; it would need a negative JRC or a straight line with negative intercept, which is a significant finding. I'm also testing whether constant residual friction plus ongoing slip-weakening could explain it instead, but checking the numbers at σ'n=22.92 shows this doesn't match either — the predicted τ is far too low compared to measured.

Looking at the slip displacement data across stages (0.017, 0.041, 0.075 mm), I calculate mobilized friction coefficients of 0.409, 0.337, and 0.204 respectively, which fall monotonically as slip increases — this confirms genuine slip-weakening behavior rather than a coincidental linear envelope. Tracing back further, μ starts at 0.548 at zero slip and decays toward roughly 0.204, so I'm fitting an exponential weakening law with peak and residual friction values, though I notice the later unloading stages show μ continuing to drop even without further slip, meaning those points sit below the envelope rather than on it since the joint is locked.

Using only the loading-stage data points, I try a residual friction value of 0.15 and compute weakening ratios at each slip distance, then take logarithms to linearize the Weibull-type decay function. Fitting a line through these transformed points gives a slope of about 1.03, which matches the expected shape parameter closely, and solving for the intercept yields a characteristic slip distance Dc of roughly 38.5 µm — notably close to published values for similar joint surfaces.

But this is exactly the value one prior case used, and that case performed worse, not better, which is puzzling. I realize this fit assumed a fixed residual friction that doesn't match how the actual model parameterizes strength, so I shouldn't over-interpret the coincidence. The real question is why a Dc that fits observed data causes runaway behavior in the model — likely because the surrounding system's stiffness is too low relative to the rate at which strength drops with slip, so I want to check the stability criterion comparing the weakening slope to the unloading stiffness.

Working through the numbers, I estimate the peak weakening slope near 75 GPa/m using the friction drop and normal stress, while the measured envelope slope from the frame data comes out near 129 GPa/m — but that includes the strength drop itself, so it isn't a clean measure of frame stiffness alone. I need to find the actual frame stiffness constant to compare properly.

Looking at the system stiffness values, I find k_sys around 125 GPa/m, which against the weakening slope of 75 GPa/m at D_c=40µm gives a stability ratio of about 0.6 — marginal but stable, while at D_c=74.5µm the ratio drops to 0.32, comfortably stable. This predicts the 91_08 case should be stable, but it wasn't, which is puzzling since "stable" here refers to quasi-static behavior specifically.

Stepping back, I need to answer the practical question directly: lowering regularization doesn't help capture each step. The 91_08 test actually tried reducing D_c from 74.5 to 40µm and made things worse — 73% of total slip arrived as a single runaway event during the 20 MPa hold, final slip overshot to 0.100mm versus 0.079mm, and the mean nRMSE tripled from 6.05 to 16.89. This tells me the step structure isn't a regularization artifact at all — the real explanation is that the measured joint only slips while σ'n is falling.

All three slip bursts sit on pressure ramps, while the holds contribute almost nothing (0.0021 and 0.0013mm). Since a pure slip-weakening law has no dependence on the rate of change of normal stress, once weakening starts it keeps sliding through the hold — 90_08 puts 0.0341mm into the 24 MPa hold where the experiment only shows 0.0013mm. This is a genuine model-form gap, though it's bounded since Table 2 samples at hold ends and the redistribution between windows nearly cancels at those plateau points. What would actually capture the stepwise behavior is a rate/state formulation or velocity-strengthening term where slip rate enters the stress limit directly, arresting slip when the driving rate goes to zero.

That's a new constitutive feature though, not something to add via parameter sweep — worth noting but not worth pursuing for this paper. Now I want to check whether the model's late onset of burst 1 could be fixed by a small strength reduction. The measured burst 1 starts at 1015s (Pi=17.9MPa), but working through the fraction table, the model's slip onset looks closer to 1300-1400s — so roughly 285s late, which lines up with one injection step. Given that failure appears quantized in this model, that suggests the peak envelope is one step too strong.

But weakening it by one step to fix burst 1 would make the main event start too early — that's the core tension: the experiment shows slip starting at 17.9 MPa but the big drop happening at 24-28 MPa, and a single envelope can't capture both behaviors. This is actually what proper slow slip-weakening would do — start early at low slip rate and weaken gradually — but the model's real problem is that once slip starts, it doesn't stop.

Now I want to assemble the rest of the picture: checking why SWS3's stage 11 isn't reached despite 10/11 stages, and pulling the per-stage detail from Table 2 for SWT1/SWT2/SWS3 to compare against the summary text files for the chosen winners, including checking the user's SWS3 report against my own Table 2.

Comparing the user's claim that 91_05 is best "by far" with a slight residual cohesion sweep needed (1.3-1.5 MPa) against my numbers — mean 5.07 for 91_05 versus 10.00 for 90_05 — I notice τ and σ'n actually got worse while Q, dn, and ds improved substantially, which supports the idea that residual cohesion is just slightly too strong. I'm going to dig into the per-stage detail for SWS3 91_05 next.

Ran 2 commands
For SWS3 91_05, the predicted residual τ runs 1.1–1.7 MPa higher than measured across all unloading stages, and σ'n is similarly overestimated by 0.65–0.98 — confirming the residual cohesion of 1.65 MPa is too strong, with a consistent positive offset pointing to that cohesion term directly.

But cutting residual cohesion isn't a simple 1:1 fix, since lowering it also lets the joint slip more, which further reduces τ through frame unloading. A rough linear interpolation between the resc=0 run (90_05, final τ≈0.10) and resc=1.65 run (91_05, final τ=3.57) against the measured 2.44 suggests resc≈1.11 MPa, though I should verify this properly using the full stage-by-stage gate tables rather than just endpoints. Meanwhile dn and ds gate performance for SWS3 look reasonably solid (7/9 and 5/9), so I'm moving on to check SWT1 91_02's σ'n and τ errors next.

For SWT1 91_02, the σ'n and τ errors are small but consistently positive, while dn reveals a real problem: the model fails to recover contraction during unloading as much as measured does, and Q stays 40-70% too high during unloading. This points to the joint's residual hydraulic aperture staying too open — a normal-closure compliance issue rather than a strength issue, since the model's reversible normal stiffness during unloading looks roughly half of what's measured, even though the closure parameters were already refit earlier.

Working through the numbers, the measured unloading secant stiffness comes out to about 2.1e11 Pa/m, while the model's is about 4.5e11 Pa/m — so the model is roughly 2x too stiff during unloading. I'm weighing whether this is worth pursuing as a separate sweep, since fixing it could meaningfully improve both the dn and Q errors given the current mean error is already decent.

Actually, checking SWT2's dn error, it's already fine at 2.06, so this defect seems specific to SWT1. Let me pull up the detailed per-stage breakdown for SWT2 91_04 and 91_03, and print compact per-stage errors for the four candidate winners plus the SWS4 pair to compare.
Per-stage tables for SWT2 pair and SWS4 90_08
Comparing 91_03 and 91_04 on stage 6 onwards: 91_03 nails the early tau error but its slip drifts from +0.010 to +0.029 by stage 11, while 91_04 starts with a worse tau but its slip only grows from −0.008 to +0.011, making it the better fit overall.

Neither model captures the back-slip behavior on unloading, where measured slip actually decreases from 0.571 to 0.552 — since plastic slip is irreversible in the model, this reversal can't be reproduced, capping the slip NRMSE around 1% for both. Weighing everything, SWT2 looks like a genuine tie between the two models (table-2 means 2.39 vs 2.43), so I'm leaning toward deciding based on physical consistency — comparing residual cohesion values (8.74 MPa for 91_03 vs 9.71 MPa for 91_04) against the SWT1 result of 9.19 MPa, since both specimens are mated tensile fractures of the same granite and should show consistent cohesion.

For SWS4 90_08, the dominant error is concentrated in stage 4 (the 20 MPa loading step), where τ, σ'n, and ds all show notable deviations — this matches a missing first burst event, while stages 5-11 are tight and Q and dn both perform excellently. So the one remaining defect in this model is that missed first burst, and I'm now thinking about what adjustment — like shifting the peak envelope so slip initiates a few MPa earlier — could fix stage 4 without degrading the later stages.

Weakening the peak envelope to fix stage 4 risks making the over-slip at stage 6 worse, since slip there is already bounded by the unchanged residual envelope — so there's a real trade-off to quantify via the strength margin per injection bin for 90_08. I also want to flag that SWS3 stage 11 is never reached because the run ends 0.4s short of the stage boundary — just a scheduling artifact worth fixing by extending the end time slightly in a rerun.

Ran 2 commands
Looking at SW-S4, the margin crosses zero somewhere between 18-20 MPa, but measured burst begins at 17.9 MPa. Since the margin is about 1.4% at 18-20 MPa and 7.16% at 16-18 MPa, shaving roughly 1.5-2 percentage points of margin would shift the onset to align with the observed 17.9 MPa.

That translates to about 0.2 MPa of peak strength reduction, which could come from a small cohesion adjustment or a slight decrease in residual friction angle. I need to check whether this would also weaken the 26-28 MPa range too much, but since that range is already deeply negative (-20.5%) and residual-controlled, the extra reduction shouldn't matter much there. I should verify whether SW-S4's material model actually includes a cohesion parameter I can tune, similar to what SW-S3 uses.

Remembering the instruction: if I decide no more sweep is needed, I should create an md file for the sample, write paper notes, then the final version.

Looking at the evidence, SW-T2 stands out clearly — 91_03/91_04 both hit 2.4% Table-2 mean, the best in the whole campaign, with remaining errors being model-form rather than parameter issues. That one's done, no more sweep needed, and I'll pick 91_04. SW-T1 at 91_02 sits at 4.44%, with a single remaining defect to consider.

The post-slip unloading normal stiffness is about 2.1× too stiff, driving the dn and Q errors, and it's a normal-closure parameter orthogonal to strength. I'm weighing whether one more bracket is worth it given the dn error is visible enough to show up in a figure — but changing normal closure risks cascading into the whole strength history and onset timing, which feels too risky for a single targeted fix.

Checking whether this recovery issue is shared across specimens: SW-T2 recovers its normal displacement fine (model matches measured closely), but SW-T1 doesn't — its measured recovery is 3.7× larger than SW-T2's despite nearly identical slip and nearly identical change in effective normal stress between the two specimens. That's a strange discrepancy for two supposedly similar tensile fractures, so something specific to SW-T1 is causing the model to underpredict its normal recovery.

Working through the post-slip unloading stiffness for each specimen, I find the model applies roughly 450-870 GPa/m for both, but SW-T1's actual data calls for something closer to 213 GPa/m — about half the model's value. This points to a targeted fix: halving SW-T1's post-slip normal stiffness parameters, which only affects the unloading branch after slip and shouldn't interfere with strength calibration elsewhere.

Moving to SW-S3 (91_05, 5.07%), the remaining issue is a systematic residual τ offset of +1.1 to +1.7 MPa on unloading. Rather than guessing at a residual cohesion value, I want to compute the actual unloading-branch τ error for both 90_05 and 91_05 runs from their Table 2 stage data and interpolate resc properly.

For SW-S4 (90_08, 6.05%), the one remaining lever is stage 4's missing burst with a τ error of +2.71 — a small peak-strength adjustment worth testing. I'll pull the gate csvs to do the SW-S3 interpolation calculation properly.
Interpolate optimal residual cohesion per specimen
The spread of estimates tells me whether the parameter is identifiable. For SW-T2, all five estimates cluster tightly between 8.51–9.65, centered around 9.15, meaning the parameter is well identified, and both 91_03 (8.74) and 91_04 (9.71) bracket this true optimum with neither being more than 0.6 MPa off.

Given the tight clustering and the 2.4% mean from Table-2, a single midpoint deck at 9.15 for the mesh-3 + mesh-5 final version would be cheap and defensible rather than running another sweep.

For SW-T1, the estimates split clearly: stress channels want 8.47–8.48, slip wants 9.05, while dn/Q want 11.7–12.5 — confirming two distinct defects, since residual cohesion around 8.5–9.0 satisfies stress+slip but can't simultaneously satisfy dn/Q without breaking the stress fit. This confirms the normal-closure diagnosis, with 91_02 at 9.19 already sitting at the stress/slip optimum, meaning residual cohesion is essentially resolved and the remaining lever is normal closure.

I'm now seeing the same split pattern emerge in SW-S3, where stress estimates cluster around 0.73–0.76 while displacement/flow estimates want something closer to 1.22–1.81.

Since SW-S3 and SW-T1 share this same pathology — matching either stress or displacement but not both with one residual-cohesion knob — I'm working through the physical explanation: if slip is correct but stress is too high, that points to the frame stiffness (which converts slip into stress) being wrong rather than the residual envelope itself. Checking the numbers for SW-S3 91_05 across stages, I'm computing the model's stress-slip stiffness (around 123 GPa/m) against the measured stiffness (around 153 GPa/m), confirming the model's frame is too compliant relative to the data.

For SW-T1 91_02, the same calculation gives matching stiffness values between model and measurement, meaning its frame is correct and the only discrepancy lies in the normal closure term. I'm now cross-checking this pattern against SW-S4 90_08 and SW-T2 91_04 to see if the 20%-too-compliant frame issue for SW-S3 holds up across other specimens.

Checking the numbers: T1 matches exactly, T2 is off by only 2%, S4 is off by 8%, but S3 is consistently 20% too compliant — a clear outlier. This confirms the real issue for SW-S3 isn't residual cohesion but the frame stiffness itself, which needs to be increased by roughly 20%, likely tied to the axial_bc_penalty constant in the deck setup, so I want to compare that value across specimens to pin down the discrepancy.

I should cross-check this by comparing penalty values across the decks. Next I want to tackle the mesh-3 readiness question and audit whether everything needed for the paper has been exported, starting with which mesh files the four candidate decks reference and whether correct mesh3 variants exist.
Checked mesh files and frame penalties
All four mesh-3 counterparts check out. But there's a critical issue: per the source-node-pinning-rule memory and MESHES.md, the injection nodeset coordinates are mesh-resolution-dependent, since the 89-series decks carry exact interface-node coordinates tuned for the SIZE-5 mesh. On mesh 3 those same coordinates could land elsewhere, possibly on a bulk node, so a naive mesh-3 run risks misplacing the injection points entirely.

This is exactly what the user wants verified, and the PointValue postprocessor coordinates have the same mesh-dependency issue per the postprocessor-only bug memory. I should run check_source_nodes.py against both mesh 3 and mesh 5 to confirm.

Ran 2 commands
I notice SW-T1's source sits 1.68 mm off-node on mesh 5 — the nearest interface node wins so it's tolerable, but that discrepancy might behave differently on mesh 3. I should check mesh 3 for all four sources to confirm.
Checked source node pinning on mesh 3 for all four
I caught a real problem: SW-T2 on mesh 3 is pinned to a bulk node rather than the actual joint, which means the injection would drive the matrix instead of the interface — exactly the trap I need to avoid. The fix is to swap in the correct interface-node coordinates for mesh 3, so I'm locating the nearest interface node (956.8 µm away, node 29454) and writing a quick helper to pull its coordinates, while also noting SWS4 mesh3's node counts for reference.

Something's off though — SWS4 mesh3 has identical node/interface counts to SWS3 mesh3 (104781/1977), which is suspicious given MESHES.md's note that the old SW-S4 journal was copied from SW-S3. The size-5 versions differ between the two specimens, so I want to verify whether the SWS4 theta30 size3 mesh actually reflects the real SW-S4 geometry or is just a leftover copy — I'll run the geometry check script across all eight meshes to confirm, while noting SWT1 and SWT2 mesh3 counts differ as expected.
Verified geometry of all 8 mesh files
All 8 meshes check out correctly for L, D, θ, and planarity—the matching node counts between SWS3 and SWS4 at size3 are just coincidental from the same meshing scheme, since their actual geometries differ. That leaves SW-T2's source coordinates hitting a bulk node as the only remaining blocker for mesh 3, so I need to find the correct interface-node coordinates for it and double-check the PointVal.

Ran 2 commands
I still need to check SWS3's PointValue entries to see what they're sampling, and verify SWS4's four PointValues around the monitoring points that were already fixed for injection/outlet.
Inspected remaining PointValue postprocessors
I'm checking that the pressure values are PointValue evaluations at the interface coordinates, which interpolate within the finite element rather than requiring an exact mesh node match — so the 173.7 µm distance to the nearest node on mesh 3 isn't actually a problem as long as the point lies inside the domain.

The key realization is that this point sits exactly on the fracture interface plane by construction, since it's the size-5 interface node coordinate and that plane is identical across both meshes, so there's no steep-gradient sampling issue like the earlier stale-coordinate bug. I confirm SWT1/SWT2 use AverageNodalVariableValue on the nodeset instead, which is inherently mesh-robust, and now I'm moving on to check SWS4's bulk displacement PointValues on the sidewall.

Now I want to verify the specimen length covers the sample points and then audit whether all four final CSVs together emit every column needed for the eight validation panels and Table 2's metrics, so I'm going to cross-check column coverage across the outputs.

Ran 2 commands
All four specimens export everything needed for the paper's figures and Table 2, with only minor channel differences that don't matter. The one real gap is that peak friction angle and mobilized JRC/mu values exist only on SW-S4, which would be a problem if the paper wants to show BB envelope evolution across all four specimens.

Now I want to rigorously verify the frame-stiffness diagnosis for SW-S3 by comparing measured versus model secant stiffness on the slip event using the Table-2 stage data across all four specimens.
Compared measured vs model tau-slip secant stiffness
Stiffness values check out clean: SW-T1 at 1.00, SW-T2 at 0.98, SW-S4 at 0.93, but SW-S3 at 0.81 stands out as 19% too compliant in its τ–slip system. That stiffness gap explains why no single residual cohesion value can satisfy both the residual stress target of 0.75 MPa and the residual slip target of 1.4 MPa — the mismatch is structural, not a strength issue. I'm looking at SW-S3's axial boundary condition penalty setting as the likely lever to adjust.

Since that penalty is already near-rigid compared to the other three cases, pushing it higher won't meaningfully change things — the remaining compliance must come from the rock itself plus the interface tangent penalty. Working through the geometry (a 123.4mm × 50.53mm granite core at E=75 GPa, fracture angle 29°), I estimate the rock's own axial stiffness around 608 GPa/m, and projecting that onto the fracture plane using the sinθcosθ factor squared gives roughly 109 GPa/m — close to the observed 123.5 GPa/m. So the model's stiffness is essentially just reflecting the rock's intrinsic elastic response.

But then I realize the measured value of 153 is actually higher than what pure rock elasticity alone could produce, which shouldn't be possible for a series system — unless my angle projection is off, E is higher than assumed, or the length differs. Checking against SW-T1 as a cross-check, the absolute numbers from my crude projection aren't trustworthy, but the ratio between model and measured should still hold since both use the same definitions — so the real conclusion is that SW-S3's modeled stiffness is about 19% too low and needs a stiffer loading path to correct it.

Since SW-S3's axial boundary penalty is already near-rigid at 1e13, there's no room to stiffen further that way — the compliance must be coming from the rock or interface itself, so the real lever is the tangential penalty or the rock modulus. I'm second-guessing the direction of the relationship, but confirming: higher penalty does mean stiffer frame and higher k_tau, and SW-S3 is already maxed out there, so pushing it higher won't help much since the rock now dominates. That points me toward checking SW-S3's tangential penalty and Young's modulus against the other samples, since there's a pending task to unify rock parameters across the four decks — maybe SW-S3 simply has a lower E value that needs correcting.
Compared rock/frame constants across the four decks
Since the rock constants are unified and only the frame calibration differs, SW-S3's frame is already essentially rigid at 1e13, meaning the remaining 19% compliance comes purely from the rock and interface itself. This reframes the conclusion: the stiffness deficit in the τ-slip isn't something that can be tuned away — it's a genuine lower bound set by the rock's elastic response.

I'm second-guessing whether this is fully correct, though. The model assumes uniform slip across the whole fracture, while the experiment's LVDT only measures shear displacement at one point — if real slip localizes rather than spreading evenly, the measured average could come out smaller, inflating the apparent k_tau. That's a plausible measurement-frame explanation I should flag without overclaiming.

So I'll frame it carefully: SW-S3 is 19% too compliant on the τ-slip path with its frame penalty already near-rigid, meaning this isn't a tunable knob — it's why residual cohesion can't satisfy both stress and slip simultaneously, and 91_05 is the better compromise since it favors the tighter displacement gate. Comparing the nrmse values between 91_05 and 90_05 across dn/ds and τ, I'm weighing which one actually produces the better overall mean fit.

Given the stress and displacement estimates cluster around different resc values, I'm wondering if an intermediate resc near 1.2 might outperform both — though interpolating nrmse this way is risky. Since the user suggested 1.3-1.5 and my own numbers point toward 1.2, I think one more SW-S3 bracket at resc 1.20 and 1.40 is worth running, since this is the one specimen where the two calibration signals disagree enough to matter. But if the disagreement stems from an untunable stiffness error, the real question becomes which channel to prioritize — and since displacement is what the joint model actually predicts, matching it is more meaningful than matching τ, which may partly be a frame artifact. That reasoning supports 91_05, which already sits close to the displacement optimum.

So I'll settle on one SW-S3 bracket at resc = 1.25 and 1.40 — cheap, two decks, landing on the displacement-side optimum while recovering some of the τ excess. Now I want to step back and finalize the whole plan: SW-T2 looks done at 91_04/91_03 since the estimates cluster tightly around 9.15 with no real gap to close; SW-T1 needs one more bracket targeting the overly stiff post-slip normal closure; SW-S3 gets the resc 1.25/1.40 bracket; and SW-S4 needs one bracket shaving peak strength to capture the missed first burst. That's six HPC jobs total across three specimens, which feels like a reasonable single batch — though I'm second-guessing whether SW-T2 really needs nothing further.

Given the user's instructions, I should just declare SW-T2 final now and produce the deliverables: a markdown file with paper notes, the Table 2 comparison, and error discussion, plus a final deck for mesh 5 and a mesh-3 variant with HPC scripts — while also fixing the mesh-3 bulk-node trap I found earlier. For the other three specimens I'll build the six sweep decks and their HPC scripts. The mesh-3 run is really the user's own convergence check, so each specimen's true final deliverable is the mesh-5 final plus a corresponding mesh-3 version.

For SW-T2 specifically, since 91_04 is already the run mesh-5 final, I don't need to rerun it — I just need to verify it's correct and fully exports everything needed for the paper, and only repeat it if something changes. I'll follow the naming convention from memory: any time I modify a deck, give it a new name reflecting the change, so I can track mesh-3 and mesh-5 versions clearly.

Simplest and least error-prone is just two separate decks, so I'll go with that. Before building them, I should nail down the SW-S4 peak-strength shave and the SW-T1 normal-closure numbers — let me check the deck's normal-closure block parameters, and actually reconsider whether the SW-T1 dn defect is really normal closure in the first place.

Looking at the stage table again, the model matches the peak contraction exactly at stage 6 but then fails to recover properly through stages 7 and 11 — measured recovery is 0.044 mm over a 9.35 MPa change in normal stress, while the model only recovers 0.0199 mm over 8.98 MPa. Since SW-T2 recovers correctly, this confirms SW-T1's post-slip normal unloading compliance is roughly 2.2× too stiff, pointing to the maximum closure and initial normal stiffness mechanical parameters in the BB model.

Using the hyperbolic closure relation, increasing Vm at fixed Kni would soften the joint at high stress, but that risks altering the entire loading history including preload and onset behavior. I'm wondering if there's a cleaner parameter to adjust instead — maybe the reversible normal compliance mentioned earlier — so I want to check SW-T1's deck and look at its normal-closure block directly.

Ran 2 commands
I notice SWT1 and SWT2 share identical mechanical normal-closure constants, and these match exactly with SW-S4's Table-2 back-analysis values from its deck header. This suggests all three specimens are using SW-S4's closure parameters rather than their own independently derived values.

This is a genuine finding: task #27's "refit SW-T1/SW-T2 normal-closure constants from Table 2" apparently never actually landed in these decks — they still carry SW-S4's constants. Let me verify by checking SWS3 and SWS4, and try to derive per-specimen closure constants from Table 2 directly.

Looking at the unloading branch data for SW-T1, I notice something odd: as normal stress rises from 31.79 to 41.14, the displacement dn goes from -0.157 to -0.113 — meaning the joint appears to be opening rather than closing further, which is backwards for a pure closure response. This tells me dn on the unloading branch isn't capturing closure behavior at all, but rather dilation recovery or post-slip relaxation.

I'm considering that at stage 6 the joint just slipped, so the -0.157 value includes a large contraction from roughness degradation during the slip event, and the subsequent unloading shows partial recovery — which is re-seating, not elastic closure. This is getting complicated, so I want to pull back to what's actually defensible: SW-T1's model under-recovers dn by 0.024 mm during unloading while SW-T2's doesn't, yet both decks use identical closure constants — meaning these constants were never specialized per specimen. Let me check SWS3 and SWS4's mechanical closure constants to confirm they're all the same.
Compared mechanical closure constants across all four
I've confirmed all four specimens are using SW-S4's mechanical normal-closure constants — hard-coded in T1/T2/S3, via variables in S4. Task #27 claims T1/T2 closure was refit from Table 2, but it's marked complete while still carrying S4's constants, which is a real finding worth flagging. This also explains why SW-T1's dn recovery is off: S4's joint is a polished saw cut with Vm = 45.9 µm, while T1 is a rough mated tensile fracture with very different surface characteristics.

Working through T1's own Table 2 data, the loading branch shows essentially zero closure change until a slip event causes a shear-induced contraction, followed by about 44 µm of recovery during unloading over a 9.35 MPa stress drop — implying a secant stiffness around 213 GPa/m. Checking this against the BB hyperbola with S4's Vm and offset parameters shows the joint is pre-seated at roughly 96% of Vm, making the computed stiffness unrealistically high, which is exactly why the model behaves too stiffly. The fix is likely to increase T1's maximum_closure value so the joint has more room to recover, and I'm estimating what stiffness would be needed to match the observed 44 µm recovery.

Ran 5 commands
I'm working through the closure law with σ0 = Kni·Vm = 11.216 MPa and p=3.28, solving for c/(Vm−c) at σ_n = 36 MPa by raising the ratio 3.210 to the power 3.28.

Computing c at each stress level: 44.93 µm at 36 MPa, 45.27 µm at 41.14 MPa, and 44.45 µm at 31.79 MPa — giving only 0.82 µm of closure change across that range, far short of the 19.9 µm recovery the model predicts. This tells me the dn recovery isn't coming from this closure law at all, but likely from the shear-dilation coupling or bulk elastic response instead, so I need to be careful not to over-claim a mechanism I haven't actually verified.

What I can say confidently: SW-T1's model under-recovers normal displacement on unloading by 26 µm (58% of the measured 44 µm), while SW-T2 under-recovers by only 2.5 µm — this is the largest single residual in the SW-T1 scorecard. It's not fixable by residual cohesion since that parameter splits between 8.5 MPa (stress/slip fit) and 12.5 MPa (dn/Q fit), and all four decks share identical normal-closure constants from SW-S4's back-analysis, meaning SW-T1's joint closure was never actually fitted to its own data.

At the re-seated state, though, this closure law only contributes ~0.8 µm across the whole unloading branch, so the 26 µm gap isn't in the closure law at all — it's in the shear-dilation/roughness-degradation recovery, meaning tweaking Kni or Vm won't help. This points to a model-form limitation in dilation recovery rather than a parameter-fitting problem, so no sweep will fix it; SW-T1 at 91_02 should be treated as final with this documented as a known limitation. I want to sanity-check this by seeing whether SW-T1 even emits a separate dilation channel I could compare against its normal closure output.

Since SW-T1 doesn't emit bb_normal_closure, I'm instead tracing what dn does versus σ'n across the unloading branch to see if the ~20 µm shift matches the bulk elastic response. The closure law alone predicts 0.8 µm for that stress change, but the model shows 19.9 µm, and since slip is fixed during unloading, the roughness/dilation offset should also be fixed — so something else must be driving that movement. I'm now digging into whether a nonlinear vs. hyperbolic normal closure flag mismatch between the top-level config and the material block could explain it.

There's also a separate reversible_normal_compliance parameter I need to check per task #4, so I'll do one targeted grep for that before moving on to wrap up the deliverables.
Look for reversible-compliance settings
Found it — SW-T1 sets `normal_unload_retention_fraction = 0.94` and a small activation slip value, while SW-T2 lacks these lines entirely and falls back to defaults. That retention fraction means 94% of the closure/dilation state is kept on unloading, so the joint only releases 6% — this is precisely the parameter governing how much dn recovers during unloading.

So SW-T1 retains 94% and barely recovers, while SW-T2 presumably defaults to 0 (full recovery) and behaves correctly. I want to verify that default value and its semantics against the source.

Ran 2 commands
SW-T1 sets normal_unload_retention_fraction to 0.94, meaning 94% of recovered closure is subtracted from the closure used in the BB normal-stress law once the joint slips past 50 µm. This is a stress-side hysteresis effect that indirectly influences the reported dn through mechanical equilibrium, since retaining less recovered closure makes the joint appear stiffer/more closed than it actually is.

Looking at the numbers, SW-T1's dn (−0.139) is actually more negative (more closed) than the measured value (−0.113), while SW-T2 with retention off matches the data. This gives a clean A/B test: I should try dialing SW-T1's retention fraction down from 0.94 toward 0.5 and 0.0 to see if that brings dn recovery in line with measurements, and I want to check whether SWS3 and SWS4 use the same parameter before moving to implementation. I also need to revisit SW-S4's lever, since stage 4 looks like the worst-performing stage in the 90_08 case.

For 90_08, the measured burst happens during the 16→20 MPa ramp, but the model's margin drops from 7.16% at 16-18 MPa to just 1.40% at 18-20 MPa — I need roughly 1.5-2 percentage points less margin to trigger slip at 17.9 MPa. Comparing 90_07 (JRC 9) and 90_08 (JRC 5), their margins are nearly identical, so JRC isn't the right lever — it has to be φ_r instead. Working through the trig, shaving 1.7pp of margin requires reducing φ_r by about 0.39°, from 22.72° to roughly 22.33°, though I'm wary this could over-correct the slip behavior above 20 MPa where the model already overshoots at stage 6, so I should bracket this with a test deck at the −0.39° value.

But thinking further, weakening the peak to trigger earlier slip doesn't actually fix the staging problem — the model would just start slipping sooner and then continue sliding right through the 20 MPa hold, which could make stage 5's existing over-slip (already +0.0063 too much) even worse. So SW-S4 might not have a clean fix: the total slip budget looks correct, but the model can't stay still during the holds, meaning pulling the onset earlier just redistributes the excess slip rather than eliminating it. I want to quantify what happens if the onset shifts 285 seconds earlier — whether burst1's 0.016mm lands at the right time before the model keeps sliding through the 20 MPa hold.

Running the numbers, that shift would add roughly 0.02mm more slip, pushing stage 5 to about 0.055mm against the measured 0.041mm — worse than the current +0.006 discrepancy. This tells me SW-S4 has no remaining parameter to adjust: the onset error and staging error stem from the same root cause, the model's inability to arrest slip at constant normal stress, so shifting the onset just trades one stage's error for another's. Given both D_c brackets performed worse and the JRC bracket was a dead heat, I'm settling on 90_08 at 6.05% as the best achievable result — SW-S4 is final.

Now turning to SW-S3, where the τ-slip stiffness runs 19% low and the rescaling estimates diverge between stress-based (0.75) and displacement-based (1.2-1.8) approaches, with 91_05 at 1.65 sitting near the top of that displacement range. I'm considering a midpoint around 1.30 that could reduce the τ excess by roughly 0.7 MPa at a cost of about 0.005mm slip — worth testing as a single deck rather than a full bracket.

Looking more carefully at the individual estimates — ds at 1.40, dn at 1.22, Q at 1.81, τ at 0.76, σn at 0.73, with a median of 1.22 — I decide to bracket two values, 1.20 and 1.40, which captures both the median and the ds estimate.

This leads me to finalize my decisions across all four specimens: SW-T2 is final at 91_04 with MD and mesh5/mesh3 decks to write (plus fixing the mesh-3 bulk-node trap); SW-S4 is final at 90_08 with its own MD and decks; SW-T1 gets one bracket testing normal_unload_retention_fraction at 0.50 and 0.00 against the current 0.94; and SW-S3 gets one bracket testing residual_cohesion at 1.40 and 1.20 against the current 1.65.

I pause to reconsider SW-T1 — is 91_02 at 4.44% already good enough to call final? But the dn nrmse of 9.06, with a 23% error at stage 11 visible in Figure 7, plus the fact that there's a specific untested parameter unique to this specimen, convinces me the bracket is worth running. I'll check the SW-S3/SW-S4 retention values before building everything out.

Now I'm ready to start creating tasks and building efficiently.
Compared unload-retention settings across four decks
Looking at retention values, T1 and T2 are both high but T1's recovery is way off from what's needed, while T2 matches fine—so retention alone isn't the explanation. This points toward lowering T1's value to around 0.80 or below, though I want to double-check that direction against the other samples.

Checking the WT1 runs, they all share retention 0.94 but show varying dn stage-11 errors, so there's no clean A/B comparison there. Reasoning through the mechanics: retention scales down the recovered closure fed into the BB law, so lowering it means less extra closure is demanded during unloading, which pushes the model's dn recovery closer to what's measured—confirming the direction is correct. Since T2 works at 0.84 but T1 needs roughly 2.2× more adjustment, I'll bracket the search between 0.60 and 0.30 for T1.

There's a risk that retention also shifts the σ'n error on unloading, but since that error is currently small, there's room to absorb it—I'll let the bracket testing reveal the actual effect. Now I'm planning the build: six new decks across SWT1, SWS3, SWT2, and SWS4 with updated retention/rescaling parameters and finer mesh convergence settings, plus corresponding HPC scripts, and I'm starting to draft the finalized markdown documentation for the SWT2 specimen.

For SW-T2, I realize the mesh-5 final deck already exists as 91_04 from an earlier run, so rather than renaming it and forcing a re-run, I'll keep it as the mesh-5 final of record and explicitly document that in the MD file, while giving the new mesh-3 convergence deck its own "FINAL" name. I want to check the existing deck-building and HPC script utilities before proceeding.

I'll use targeted sed-based copies like before, first checking how the 91-series decks were structured so I can match the header style, then start creating the tasks.
Read a 91-series header for style
I'll skip the task tracker for now and focus on building the deliverables directly, creating tasks afterward if needed. I'm going to build the six decks via a script, starting with the retention deck.
Located lines to edit
Now building the 92-series decks.

Built the four SW-T1/SW-S3 92-series decks
Now I'm moving to the two mesh-3 decks, checking SW-T2's interface node coordinates and pressure monitoring setup, then comparing against SW-S4's mesh-3 coordinates, which I notice snap to an interface node about 367 µm off from the expected position.

I should update SW-S4's coordinates to match the exact mesh-3 node for consistency with the mesh-5 convention, even though `use_closest_node=true` makes it work either way. I also want to confirm SW-S4 already uses the nodeset-average fix rather than a stale point value, and verify that the displacement-based BCs and flow-width parameters remain mesh-independent as expected.

I'm noting that `flow_rate_pp` (a nodal sum of flux over a single-node source) will be mesh-dependent since flux scales with element size, which is exactly what task #13 and the mesh-3 run should expose — while `flow_rate_validation_ml_min_pp`, the one tied to the paper's Table 2, should remain mesh-independent. Now let me pull the exact node coordinates.

Ran 3 commands
I need to fix two stale comments: the outdated inline note in SWS3 92_03/92_04 that no longer matches the current value, and the SWS4 92_06 comment that should clarify it's mesh size 3. I've confirmed the PointValue injection_pressure_pp coordinates in SWS3 92_03 are still correct on mesh 5, so now I'll update the comments and run --check-input across all six cases.

Ran 2 commands
Now validating all six decks and generating their HPC scripts.

Ran --check-input on all six new decks
All six pass, though 92_05's output looked truncated at "Initializing Equation Systems" — I should re-run it to confirm it actually finished before moving on to generating the HPC scripts.
Confirmed 92_05 check-input completes
Syntax check passes. The 3330 MB figure is for single-rank setup memory covering the whole mesh, so with mesh 3 having roughly 10x the nodes, I should bump the `--mem` request for those HPC jobs to something like 96G to be safe, even though the memory actually partitions across 32 ranks.

Actually, MOOSE's replicated mesh keeps the full mesh on every rank by default, so 32 ranks × 1-3 GB each could exceed 32G. I'll check whether the decks use distributed mesh, but assuming replicated, I'll set `--mem=128G` for mesh-3 jobs and keep 32G for mesh-5, then move on to generating the HPC scripts.
Generated the six HPC scripts
Now the two FINAL write-ups, with the full Table-2 comparison.

Generated markdown Table-2 comparison tables
Now I'll write the two markdown files, starting with SW-T2, covering specimen description, fracture type, calibrated parameters, results, and error justification. Let me pull together the key calibrated parameters for SWT2 and SWS4 first.

Ran 3 commands
I need to add a section heading before the comparison table output, then move on to discussing the key errors—starting with the Stage 5 flow discrepancy where Q comes out to 0.729 versus an expected 1.505, a roughly 52% deviation.

This is the largest single relative error, occurring at the pre-failure stage at 24 MPa: the measured flow doubles from stage 4 to stage 5 while the model barely shifts, because the measured joint is already opening with ~15 µm of pre-peak aseismic slip that a sharp-threshold peak-envelope model can't capture. I'm also noting the Stage 6 flow under-prediction (−18%), a systematic τ residual of +0.5 to +1.4 MPa across stages 6-11, and a d_s drift where the model shows irreversible back-slip of 19 µm during unloading that physically shouldn't reverse — clear model-form errors rather than calibration issues.

On the loading branch, the measured closure of −0.001 to −0.005 versus the model's near-zero response reflects the same pre-peak closure mechanism missing from the model. Overall the mean error comes out to 2.43%, which is excellent — time to write this up.
Complete SWT2_FINAL.md
Now the SW-S4 write-up.


Ran 5 commands
I notice that third index line duplicates an entry already in source-node-pinning-rule.md, so I should remove the duplicate and instead update the actual memory file with the addendum.

Recalled 3 memories, saved 2 memories
Independent back-analysis done. I scored all sixteen runs against Table 2 with scripts/table2_gate.py — eleven injection holds, five independent measurements each (a_h and k are excluded: the paper back-computes them from Q, so they carry no extra information).

Table-2 scorecard (nRMSE %, normalised by each column's measured range)
specimen	case	Q	σ'ₙ	τ	d_n	d_s	mean
SW-T1	90_01 / 91_01 / 91_02	7.38	1.98	2.73	9.06	1.02	5.96 / 7.89 / 4.44
SW-T2	90_03 / 91_03 / 91_04	5.87	1.26	1.70	2.06	1.25	4.15 / 2.39 / 2.43
SW-S3	90_05 / 91_05 / 91_06	3.24	4.30	10.30	4.74	2.75	10.00 / 5.07 / 31.19
SW-S4	90_07 / 90_08 / 91_07 / 91_08	4.94	3.74	10.01	4.53	7.01	6.08 / 6.05 / 18.87 / 16.89
Your figure-7 reads hold up: 91_05 for SW-S3, 91_04 for SW-T2, and the 91-series does wreck SW-S4. On SW-T1 Table 2 is more decisive than Figure 7 — 91_02 wins outright (4.44 vs 5.96), not narrowly loses.

Your SW-S4 question: no, and it was measured
The measured specimen slips in three bursts, every one on a pressure ramp:

window	injection	measured	90_08	91_08 (D_c 40 µm)
1015–1120	ramp 16→20	15.8 µm	2.3	5.1
1120–1310	hold 20	2.1	2.9	66.9
1415–1600	hold 24	1.3	34.1	3.8
total		79.5	82.8	100.1
It slides only while σ'ₙ is falling. A slip-weakening law has no dσ'ₙ/dt term, so once it starts it runs through the hold. Total slip is right to 4% — only its distribution in time is wrong. Lowering D_c gives one bigger runaway, not more steps: 91_08 dumps 73% of its slip into the 20 MPa hold. Capturing the staircase needs a rate/state term — a constitutive addition, not a parameter.

The test that decided which knobs are done
Interpolate every observable between the two bracket arms and ask what parameter it wants:

τ	σ'ₙ	d_s	d_n	Q
SW-T2 (c_res)	9.15	9.15	9.65	9.36	8.51	✅ identified
SW-T1 (c_res)	8.48	8.47	9.05	12.5	11.7	❌ split
SW-S3 (c_res)	0.76	0.73	1.40	1.22	1.81	❌ split
A split means one knob is doing two jobs. SW-S3's second job is measurable: secant τ–slip stiffness across the slip event, model/measured — SW-T1 1.00, SW-T2 0.98, SW-S4 0.93, SW-S3 0.81. It's 19% too compliant, so no cohesion satisfies both τ and d_s. Its frame penalty is already 1e13 Pa/m, so that part isn't tunable.

Verdicts
SW-T2 — FINAL (91_04). SWT2_FINAL.md: paper notes, full 11-stage table, error discussion.
SW-S4 — FINAL (90_08). SWS4_FINAL.md.
SW-T1 — one pair. 92_01/92_02: normal_unload_retention_fraction 0.94 → 0.60 / 0.30. Its d_n recovers 20 µm against a measured 44; SW-T2 (d_n 2.06%) recovers 10.6 of 12. SW-T1 has the highest retention of the four and it's never been varied.
SW-S3 — one pair. 92_03/92_04: residual cohesion 1.65 → 1.40 / 1.20 MPa.
Mesh audit — one real blocker found
All eight .e files verify on L, D, θ, planarity. But SW-T2's size-5 borehole coordinate snaps to a BULK node on the size-3 mesh (584.9 µm, beating the interface node at 956.8). use_closest_node = true never errors — that run would have driven the matrix, silently. 92_05 carries the exact size-3 interface coords; 92_06 does the same for SW-S4.

Export audit: every channel the eight panels and Table 2 need is in all four CSVs. One gap — bb_peak_friction_angle_pp, bb_jrc_mobilized_pp, bb_mu_peak_pp exist only on SW-S4, so you can't plot BB envelope evolution for the other three. Cheap to add if you want that figure.

Six decks, all --check-input clean, each with a --chdir-pinned script (mesh-3 jobs get 128 G). Committed as bcc46bb.

cd Examples/YeGhasemmi2018 && for f in SW*/92_0*_hpc_nochk.sh; do sbatch "$f"; done
can i ask you for another thing, your chain of thought i very well prepared. i want to be able to think like that, can oyu add this as a new md file as well for me.  can you also updated memory.md of the recent analysis and include everything for future use.

I should create two things: an MD file capturing the back-analysis reasoning method as a playbook Saeed can follow, grounded in the actual campaign examples rather than generic advice. It makes sense to place this within the YeGhasemmi2018 examples folder since that's where the source campaign material lives.

I also need to update MEMORY.md to reflect the recent analysis — covering which decks are final, what's still pending, and making sure the index is complete for future reference. Let me check the repo layout to figure out the best location for the method doc.
Found a home for the method doc
I'll write this up as doc/back_analysis_method.md, structuring it around the actual sequence of moves I made, separating the reasoning rule from the worked example. The first move is scoring independently before reading anyone else's interpretation, so I can verify the measurement itself is sound before trusting any conclusions drawn from it.

Other moves include distrusting the channel before the model (checking postprocessors and comparing sibling operators for outliers vs. common offsets), scoring against the source rather than myself, normalizing comparisons by measured range so different units can sit in one table, running a bracket-closure test where agreement across interpolated observables means done and disagreement flags a second defect, and finally chasing splits down to an independent second measurement of the suspected cause.

Beyond that, I'm thinking about running experiments designed to fail by bracketing in both directions, windowing events by stage to separate timing from magnitude, distinguishing level from slope and parameter from model form, checking whether the loading path can even identify the parameter in question, quantifying the cost of any fix before committing to it, and auditing the plumbing — mesh nodes, coordinates, nodeset names — before blaming the physics whenever a config changes.

I also want to state falsifiable predictions directly in the deck header so each run either confirms or kills them, and make sure negative results get written down since they're the expensive ones to generate. Beyond the numbered list, I should add a "smells" section for what raises suspicion, a worked example walkthrough, an anti-pattern list, and discipline points around unit conversion and requiring two independent channels to agree within 1% before trusting a result.

Then I need to update memory: capture the current campaign state across the four specimens and pending brackets, update MEMORY.md, mark task #79 complete, and add new tasks for scoring the 92-series. Now I'll write the document itself.
Created
back_analysis_method.md
+362
-0
Now the memory. Writing a campaign-state file and refreshing the index.


Recalled a memory, saved 3 memories

Ran a command, used 5 tools
Both done.

The method doc
doc/back_analysis_method.md — committed as a23b61b. It's the ten steps in strict order, and every rule is paired with the case from this project that produced it, because a rule without its scar is just advice:

1.  Score it yourself, before reading anyone's interpretation
2.  Suspect the measurement channel before the model
3.  Score against the SOURCE table, and know which columns are independent
4.  Normalise by each observable's measured range
5.  Localise: where in the load path is the error?
6.  Ask if the knob can even do the job     <-- most people start here
7.  Design an experiment that can FAIL
8.  Price the fix before you build the deck
9.  Write the falsifiable prediction into the deck header
10. Record the negative results
The pairings: the skeleton/total frame mismatch and the stale PointValue coords for step 2; the recovered 30.001° fracture angle and the derived a_h/k columns for step 3; the SW-S4 ramp-vs-hold slip windowing for step 5; the JRC/cohesion non-identifiability and the bracket-closure interpolation for step 6; the two-sided D_c bracket that failed both ways for step 7; and the margin arithmetic that cancelled an SW-S4 batch for step 8.

Step 6 is the load-bearing one, split four ways — is the parameter identifiable on this path, has the bracket closed, if it split then measure the second cause with a control, and is it model form at all. That's the section that ended a five-generation calibration loop.

Plus three appendices: a plumbing-audit table of what fails silently on a config change (source pinning, stale coords, an inherited file_base overwriting the parent's results, solver caps that aren't the one the message names), a smells list (an error constant in time is a datum error; a round-number discrepancy means look for the formula, not the calibration), and an anti-pattern table.

Memory
Two new files plus index lines:

Ye2018 campaign state 2026-08-17 — the start-here file for this validation: full Table-2 scorecard, SW-T2/SW-S4 final with their write-ups, the two open 92-series brackets with the reasoning behind each, the tau-slip stiffness control table, and the mesh/export traps confirmed on both resolutions. It also records that all four decks carry SW-S4's normal-closure constants and that those are not the carrier of SW-T1's gap — so nobody sweeps them.
Back-analysis method doc — points at the doc as the standing default, with the instruction to keep new scars in it.
I also appended the mesh-resolution addendum to source-node-pinning-rule.md: the coordinates are resolution-specific, not just geometry-specific, and it isn't predictable from the offset alone — SW-T2 was trapped at 585 µm while SW-T1 was fine at 594 µm.

Task #79 closed; #80 (score the 92-series and close both specimens, with the acceptance criteria and the "if it doesn't move, SW-T1 is final as it stands" branch written in), #81 (mesh-3 convergence scoring), #82 (the BB envelope channels) opened.

