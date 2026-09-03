# Ye and Ghassemi (2018) Table 2 strength-path figure

## Recommended figure

The clearest main-paper figure is a four-panel plot of shear stress against effective normal stress, with one panel for each specimen: SW-T1, SW-T2, SW-S3, and SW-S4. This follows the most useful part of the Kalantar et al. (2025) presentation while accommodating two constitutive models.

Each panel should contain:

- the eleven Ye and Ghassemi Table 2 states in their experimental order;
- the corresponding BB states;
- the corresponding MC states;
- the initial and post-weakening BB strength envelopes;
- the rough and smooth MC strength envelopes; and
- a shared colour scale for injection pressure.

The experimental, BB, and MC paths should be distinguished by marker shape and line style. Injection pressure should be shown by marker colour. This avoids using colour simultaneously for both model identity and pressure.

## Essential terminology

The connected Table 2 points are a **stress path**, not a measured failure envelope. The injection pressure changes the effective normal stress, and several pre-slip points remain below the failure condition. The BB and MC curves calculated from their constitutive parameters are the **strength envelopes**. These two objects must be identified separately in the caption and discussion.

Connecting the eleven Table 2 states is useful because it shows their order, but the line is only a guide between discrete pressure holds. It should not be described as a continuous experimental record.

## Translation of the Kalantar layout

Kalantar et al. show a response plot beside a stress-path plot for each of three fracture types. Ye and Ghassemi contain four specimens and the paper compares two models. A literal copy would therefore require eight panels and would be crowded in a normal two-column journal figure.

Two outputs are recommended:

1. **Main paper:** a 2 by 2 strength-path figure. This directly supports the BB--MC envelope discussion and remains readable at the AGU two-column width.
2. **Supporting information or diagnostic figure:** a 4 by 2 Kalantar-style layout. The left column shows shear stress against cumulative shear displacement, and the right column shows the strength path and envelopes.

The supplied script produces both versions.

## What was done to construct the stress paths

The plotting workflow uses the repository's `table2_gate.py` definitions as the source of the experimental values and pressure-stage order. The following operations are performed separately for each specimen and model:

1. The injection-pressure function is read from the exact input deck.
2. The pressure schedule is divided at its peak into loading and unloading branches.
3. The eleven Table 2 targets are visited in order: 8, 12, 16, 20, 24, and 28 MPa during loading, followed by 24, 20, 16, 12, and 8 MPa during unloading.
4. For every target, the last numerical output at or before the corresponding hold time is selected. This prevents the loading and unloading states at the same pressure from being interchanged.
5. Effective normal stress and shear stress are read from the paper-frame postprocessors used by the authoritative Table 2 scorer.
6. Cumulative shear displacement is zeroed at the first Table 2 stage, matching the datum used in the published comparison.
7. The experimental, BB, and MC values are connected in stage order. The connecting segments indicate sequence only; no additional experimental values are inferred between the holds.
8. The analytical BB and MC limits are evaluated over the normal-stress range occupied by each specimen and drawn separately from the stress paths.

The script rejects a numerical case if its CSV does not reach the deck's `end_time` or if any of the eleven ordered stages cannot be sampled. It exports the exact plotted rows to CSV so every point can be traced to its input deck and result file.

## Visual encoding

| Quantity | Encoding |
|---|---|
| Ye and Ghassemi Table 2 | solid black path with circular markers |
| BB result | solid orange path with triangular markers |
| MC result | dashed blue path with square markers |
| Injection pressure | shared viridis marker-face colour, 8--28 MPa |
| BB initial envelope | thin orange dotted curve |
| BB post-weakening envelope | thin orange dash-dot curve |
| MC rough envelope | thin blue dotted line |
| MC smooth envelope | thin blue dash-dot line |
| Loading/unloading order | connected stages and labels at the initial, peak, and final states |

The tensile specimens should share comparable stress limits, and the two saw-cut specimens should share another comparable range where practical. A single common vertical range for all four would compress the saw-cut response and should be avoided.

## Strength curves used by the script

The initial BB envelope is

$$
\tau_{\mathrm{BB},p}=c_p+\sigma_n'\tan\left[\phi_b+\mathrm{JRC}\log_{10}\left(\frac{\mathrm{JCS}}{\sigma_n'}\right)\right].
$$

The post-weakening BB limit is plotted as

$$
\tau_{\mathrm{BB},r}=c_r+\sigma_n'\tan\phi_r.
$$

The two limiting MC lines are

$$
\tau_{\mathrm{MC},r}=c_{\mathrm{rough}}+\mu_{\mathrm{rough}}\sigma_n',
$$

$$
\tau_{\mathrm{MC},s}=c_{\mathrm{smooth}}+\mu_{\mathrm{smooth}}\sigma_n'.
$$

The active laws evolve between these limits with slip. The plotted limits are therefore reference envelopes; the stress paths remain the primary comparison with Table 2.

## Definition of the reported slopes

The stress-path slope and strength-envelope slope are not the same quantity.

For a selected stress-path branch, the script fits

$$
\tau=m_{\mathrm{path}}\sigma_n'+b
$$

by ordinary least squares and reports both $m_{\mathrm{path}}$ and $R^2$. Separate fits are made for the nominal pre-failure loading stages and the five unloading stages. A two-point secant slope is also calculated across the first major loading transition. These slopes describe the direction followed by the specimen stress state; they are not friction coefficients.

For MC, the envelope slopes are constant:

$$
\frac{\mathrm d\tau}{\mathrm d\sigma_n'}=\mu.
$$

For the BB peak envelope, the slope changes with normal stress. With

$$
\theta=\phi_b+\mathrm{JRC}\log_{10}\left(\frac{\mathrm{JCS}}{\sigma_n'}\right),
$$

the analytical tangent is

$$
\frac{\mathrm d\tau_{\mathrm{BB},p}}{\mathrm d\sigma_n'}
=\tan\theta-
\frac{\pi\,\mathrm{JRC}}{180\ln 10}\sec^2\theta.
$$

The figure reports this tangent at the Table 2 normal stress of the last nominal pre-failure stage. The reference stress is included in the slope table. The post-weakening BB line has the constant slope $\tan\phi_r$.

Each strength-path panel now contains a compact slope box. It reports the Table 2 pre-failure and unloading path slopes, the BB peak tangent and post-weakening slope, and the MC rough and smooth slopes. Detailed model-specific path slopes, intercepts, $R^2$ values, actual stage values, signed errors, RMSE, MAE, bias, and nRMSE are written to the companion comparison tables rather than crowded into the figure.

## Dataset control

The script defaults to the eight 116 protocol-consistency cases. It refuses missing or incomplete cases, preventing a partly completed dataset from being presented as a final comparison.

The earlier complete cases can be plotted only with

```bash
python plot_ye2018_table2_strength_paths.py --case-set legacy --allow-legacy
```

The legacy output carries a visible prototype label and must not be used as the final protocol-consistent validation. Once all eight main 116 cases are complete and placed in the canonical output directories, the intended paper command is

```bash
python plot_ye2018_table2_strength_paths.py --case-set protocol116
```

The script also exports the exact stage values used to draw the plots. This file should be retained with the figure for provenance.

## Interpretation expected from the final figure

The figure should be discussed in terms of four questions:

1. Does each model reproduce the experimental stress path before slip?
2. At which pressure stage does the path first approach its strength envelope?
3. Does the simulated stress drop follow the magnitude and direction shown by Table 2?
4. During unloading, does the model return along the observed stress path, or does it retain a systematic normal- or shear-stress bias?

The figure should not be used alone to rank the models. It emphasizes two mechanical channels. The quantitative comparison should continue to use the five independent channels and report actual values together with branch-aware nRMSE.

## Proposed caption

> **Figure X.** Stress paths and constitutive strength limits for the four Sierra White specimens. Symbols show the eleven ordered injection-pressure holds reported by Ye and Ghassemi (2018), together with the corresponding Barton--Bandis (BB) and Mohr--Coulomb (MC) simulations. Marker colour denotes injection pressure. Connected Table 2 states represent the sequence of discrete experimental holds and are not a directly measured continuous failure envelope. Thin curves show the initial and post-weakening BB limits and the rough and smooth MC limits used in each simulation. The loading branch reaches 28 MPa before returning through the unloading holds. BB and MC results within each specimen use the same geometry, pressure history, confinement, and axial boundary condition.

## Reproducibility files

- `plot_ye2018_table2_strength_paths.py`: standalone figure generator.
- `Figure_Ye2018_Table2_Strength_Paths_<case-set>.pdf`: recommended vector figure.
- `Figure_Ye2018_Table2_Strength_Paths_<case-set>.png`: review image.
- `Figure_Ye2018_Table2_Kalantar_Style_<case-set>.pdf`: optional paired-response figure.
- `Figure_Ye2018_Table2_Kalantar_Style_<case-set>.png`: review image.
- `Figure_Ye2018_Table2_Strength_Paths_<case-set>_data.csv`: plotted stage data and provenance.
- `Figure_Ye2018_Table2_Strength_Paths_<case-set>_comparison.md`: readable accuracy, slope, and complete stage-value tables.
- `Figure_Ye2018_Table2_Strength_Paths_<case-set>_comparison.csv`: exact wide stage comparison.
- `Figure_Ye2018_Table2_Strength_Paths_<case-set>_accuracy.csv`: RMSE, MAE, bias, and nRMSE.
- `Figure_Ye2018_Table2_Strength_Paths_<case-set>_slopes.csv`: path and envelope slopes with intercepts and $R^2$ values.
