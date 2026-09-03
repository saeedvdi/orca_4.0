# Cohesion interpretation for the Ye and Ghassemi (2018) validation cases

## What the experiment reports

Ye and Ghassemi (2018) created SW-T1 and SW-T2 by mechanical splitting and SW-S3 and SW-S4 by saw cutting; SW-S4 was additionally polished. The surfaces were cleaned, dried, matched, and later saturated. The paper does not report cement, healing, infill bonding, or a measured fracture cohesion.

In the experimental-control discussion, the critical fracture strength is written as

\[
\tau_c=\mu\sigma'_n,
\]

where \(\mu\) is described as the sliding friction coefficient. This expression has no cohesion intercept. The paper reports an internal friction angle of 46 degrees for intact Sierra White granite, but this is a matrix property from intact-rock testing and is not a measured friction angle for the prepared fracture surfaces. No search occurrence of "cohesion" is present in the paper text.

The most defensible literal interpretation is therefore that all four prepared interfaces are cohesionless in the classical contact-mechanics sense. Their strength above smooth mineral friction arises from roughness, asperity interlocking, dilation, and damage rather than cementation.

## Why the current MC inputs contain nonzero cohesion parameters

The current MC comparison was constructed as an equivalent linear transfer of the nonlinear BB envelope, rather than as a claim that the fractures were cemented. Its rough and smooth shear-strength branches are

\[
\tau_{\mathrm{lim}}=c(R)+\mu(R)\sigma'_n.
\]

The present parameter entries are:

| Specimen | `cohesion_rough` (MPa) | `cohesion_smooth` (MPa) |
|---|---:|---:|
| SW-T1 | 40.7374 | 7.8115 |
| SW-T2 | 47.2549 | 8.2535 |
| SW-S3 | 2.3805 | 1.1900 |
| SW-S4 | 3.2250 | 0.0000 |

These are numerical envelope parameters, and the effective value also evolves with the normalized roughness state. They must be called **apparent or fitted cohesion intercepts**, not measured fracture cohesion. The `enable_tensile_cohesion=false` setting does not set these shear-envelope intercepts to zero; it disables cohesive tensile resistance for an already existing interface.

## Recommended treatment in the paper

The BB model can be described as physically cohesionless because its increased peak resistance is represented through JRC, JCS, and residual friction without an additive cohesion term.

For MC, two defensible comparisons answer different questions:

1. **Equivalent-envelope MC:** retain a fitted nonzero intercept and describe it as an apparent parameter that allows the best linear approximation of the BB/experimental envelope over the tested normal-stress range.
2. **Strict cohesionless MC sensitivity:** impose \(c=0\) and refit the friction coefficients under the same calibration budget. This tests whether a purely frictional linear law can reproduce the experiment.

Simply setting the current cohesion entries to zero without refitting friction is not a fair comparison because it changes both the onset strength and the post-slip strength. For a cohesionless MC sensitivity, the friction coefficient should be re-anchored to the same independent onset or peak-strength data used for the fitted MC case.

The manuscript should not state that Ye and Ghassemi measured cohesion. A suitable sentence is:

> The prepared fractures were treated as physically cohesionless because Ye and Ghassemi (2018) expressed their frictional resistance without a cohesion intercept and did not report cementation or a measured joint cohesion. Nonzero intercepts used in the equivalent MC comparison are therefore apparent calibration parameters that represent roughness-controlled interlocking over the tested stress range, rather than true material cohesion.
