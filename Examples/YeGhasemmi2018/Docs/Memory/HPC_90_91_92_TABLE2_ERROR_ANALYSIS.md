# HPC 90/91/92/93 cases versus Ye & Ghassemi (2018) Table 2

Initial audit: 2026-08-17. Latest update: 2026-08-18.

> **Historical series report.** This file preserves the 90–93 campaign interpretation and its
> then-current rounded scores. It is not the current all-file ranking. For values recomputed with
> the final scoring convention and for later 94–101 results, use
> `independent_analysis/TABLE2_ERROR_ACCURACY_RANKING.csv` and
> `independent_analysis/CONSOLIDATED_ANALYSIS_2026-08-18.md` (updated through 2026-08-20).

## Original 90/91/92 result

The original audit covers all **20** CSV files then present whose names begin with `90_`, `91_`, or `92_` under the four `results_csv_hpc_rorqual` directories. Every one of those original runs reaches all **11/11** Table 2 hold stages. The 2026-08-18 extension, including incomplete mesh-3 snapshots, is appended at the end.

| Sample | Best case | Mean nRMSE | Runner-up | Mean nRMSE | Finding |
|---|---:|---:|---:|---:|---|
| SW-T1 | [`91_02`](SWT1/results_csv_hpc_rorqual/91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6_hpc.csv) | **4.44%** | [`90_01`](SWT1/results_csv_hpc_rorqual/90_01_swt1_bbfast_cohesion_c26p4_kernel_SV_biot0p6_hpc.csv) | 5.96% | 91_02 is the clear best; the 92 unloading variants worsen flow and normal displacement. |
| SW-T2 | [`91_03`](SWT2/results_csv_hpc_rorqual/91_03_swt2_bbfast_theta30_resc8p74_kernel_SV_biot0p6_hpc.csv) | **2.39%** | [`91_04`](SWT2/results_csv_hpc_rorqual/91_04_swt2_bbfast_theta30_resc9p71_kernel_SV_biot0p6_hpc.csv) | 2.43% | 91_03 wins by only 0.04 percentage point; 91_03 and 91_04 are effectively tied. |
| SW-S3 | [`92_03`](SWS3/results_csv_hpc_rorqual/92_03_sw3_final_paperjrc_resc1p40_hpc.csv) | **3.59%** | [`92_04`](SWS3/results_csv_hpc_rorqual/92_04_sw3_final_paperjrc_resc1p20_hpc.csv) | 3.71% | 92_03 is best; 92_04 is close and trades better stresses for worse displacement. |
| SW-S4 | [`90_08`](SWS4/results_csv_hpc_rorqual/90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6_hpc.csv) | **6.05%** | [`90_07`](SWS4/results_csv_hpc_rorqual/90_07_sw4_bbfast_theta30_jrc9_kernel_SV_biot0p6_hpc.csv) | 6.08% | 90_08 wins by only 0.03 percentage point over 90_07; the 91 D_c brackets are much worse. |

The mean nRMSE values are comparable among cases for the same specimen. They should not be used as a strict cross-specimen ranking because each specimen has different measured ranges.

## Method

The calculations use [scripts/table2_gate.py](../../scripts/table2_gate.py), including its deck-aware stage detection and preferred paper-frame postprocessor mapping. The reference data are the four CSV transcriptions in [Extracted_Data/Table2_4_Sample_CSV_Files](Extracted_Data/Table2_4_Sample_CSV_Files/).

For every stage and observable:

- Signed error: Δ = model − Table 2. A positive value means overprediction.
- RMSE = sqrt(mean(Δ²)).
- nRMSE = 100 × RMSE / (maximum Table 2 value − minimum Table 2 value).
- Case score = unweighted mean nRMSE over the five independent observables.

The five scored observables are flow rate Q, effective normal stress sigma′_n, shear stress tau, normal displacement d_n, and shear displacement d_s. Hydraulic aperture a_h and permeability k are excluded from the score because Table 2 derives them from Q through the cubic law; including them would count the same hydraulic measurement three times. Injection pressure locates the stages and is not an additional response metric. Errors for all three are nevertheless reported in the informational section.

The model displacements are zeroed at stage 1 to match Table 2. Consequently, stage 1 is excluded from the d_n and d_s RMSE/nRMSE statistics; it remains visible in the detailed tables as a constructed zero. Percentage error is not averaged because Table 2 contains zero displacements; nRMSE provides a defined scale for all five observables.

**Consistency note.** The older `SWT1_FINAL.md` and `SWS3_FINAL.md` headline scores are 4.34% and 3.55%, respectively, because their displacement nRMSE calculations include the constructed stage-1 zeros. Applying the documented exclusion gives 4.44% and 3.59% here. The case rankings are unchanged. The SW-T2 and SW-S4 final reports already use the exclusion consistently.

## All-case normalized-error ranking

| Sample | Rank | Case | Q nRMSE | sigma′_n nRMSE | tau nRMSE | d_n nRMSE | d_s nRMSE | Mean nRMSE |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | 1 | [`91_02`](SWT1/results_csv_hpc_rorqual/91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6_hpc.csv) | 7.38% | 1.98% | 2.73% | 9.06% | 1.02% | **4.44%** |
| SW-T1 | 2 | [`90_01`](SWT1/results_csv_hpc_rorqual/90_01_swt1_bbfast_cohesion_c26p4_kernel_SV_biot0p6_hpc.csv) | 4.12% | 5.78% | 7.98% | 5.53% | 6.37% | **5.96%** |
| SW-T1 | 3 | [`92_01`](SWT1/results_csv_hpc_rorqual/92_01_swt1_final_c26p9_resc9p19_unld0p60_hpc.csv) | 11.45% | 2.64% | 3.65% | 14.55% | 1.02% | **6.66%** |
| SW-T1 | 4 | [`92_02`](SWT1/results_csv_hpc_rorqual/92_02_swt1_final_c26p9_resc9p19_unld0p30_hpc.csv) | 11.89% | 2.72% | 3.75% | 15.10% | 1.02% | **6.90%** |
| SW-T1 | 5 | [`91_01`](SWT1/results_csv_hpc_rorqual/91_01_swt1_bbfast_c26p9_resc7p21_kernel_SV_biot0p6_hpc.csv) | 13.41% | 2.97% | 4.14% | 13.40% | 5.52% | **7.89%** |
| SW-T1 | 6 | [`90_02`](SWT1/results_csv_hpc_rorqual/90_02_swt1_bbfast_cohesion_c28p0_kernel_SV_biot0p6_hpc.csv) | 37.90% | 53.41% | 73.92% | 64.08% | 75.73% | **61.01%** |
| SW-T2 | 1 | [`91_03`](SWT2/results_csv_hpc_rorqual/91_03_swt2_bbfast_theta30_resc8p74_kernel_SV_biot0p6_hpc.csv) | 4.46% | 1.06% | 1.43% | 2.36% | 2.63% | **2.39%** |
| SW-T2 | 2 | [`91_04`](SWT2/results_csv_hpc_rorqual/91_04_swt2_bbfast_theta30_resc9p71_kernel_SV_biot0p6_hpc.csv) | 5.87% | 1.26% | 1.70% | 2.06% | 1.25% | **2.43%** |
| SW-T2 | 3 | [`90_03`](SWT2/results_csv_hpc_rorqual/90_03_swt2_bbfast_theta30_cohesion_c33p2_kernel_SV_biot0p6_hpc.csv) | 7.59% | 2.87% | 3.88% | 3.46% | 2.95% | **4.15%** |
| SW-T2 | 4 | [`90_04`](SWT2/results_csv_hpc_rorqual/90_04_swt2_bbfast_theta30_cohesion_c35p0_kernel_SV_biot0p6_hpc.csv) | 37.01% | 53.32% | 72.25% | 74.73% | 76.06% | **62.67%** |
| SW-S3 | 1 | [`92_03`](SWS3/results_csv_hpc_rorqual/92_03_sw3_final_paperjrc_resc1p40_hpc.csv) | 3.00% | 3.35% | 8.01% | 2.46% | 1.11% | **3.59%** |
| SW-S3 | 2 | [`92_04`](SWS3/results_csv_hpc_rorqual/92_04_sw3_final_paperjrc_resc1p20_hpc.csv) | 3.27% | 2.72% | 6.56% | 2.72% | 3.26% | **3.71%** |
| SW-S3 | 3 | [`91_05`](SWS3/results_csv_hpc_rorqual/91_05_sw3_bbfast_paperjrc_resc1p65_kernel_SV_biot0p6_hpc.csv) | 3.10% | 4.24% | 10.11% | 4.65% | 3.01% | **5.02%** |
| SW-S3 | 4 | [`90_05`](SWS3/results_csv_hpc_rorqual/90_05_sw3_bbfast_paperjrc_L123p4_cohes1p67_kernel_SV_biot0p6_hpc.csv) | 8.26% | 3.12% | 7.71% | 15.15% | 17.63% | **10.37%** |
| SW-S3 | 5 | [`90_06`](SWS3/results_csv_hpc_rorqual/90_06_sw3_bbfast_jrc5p69_L123p4_kernel_SV_biot0p6_hpc.csv) | 8.59% | 3.28% | 8.10% | 15.78% | 18.30% | **10.81%** |
| SW-S3 | 6 | [`91_06`](SWS3/results_csv_hpc_rorqual/91_06_sw3_bbfast_paperjrc_resc1p65_dc1e4_kernel_SV_biot0p6_hpc.csv) | 9.34% | 17.49% | 41.65% | 46.62% | 45.89% | **32.20%** |
| SW-S4 | 1 | [`90_08`](SWS4/results_csv_hpc_rorqual/90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6_hpc.csv) | 4.94% | 3.74% | 10.01% | 4.53% | 7.01% | **6.05%** |
| SW-S4 | 2 | [`90_07`](SWS4/results_csv_hpc_rorqual/90_07_sw4_bbfast_theta30_jrc9_kernel_SV_biot0p6_hpc.csv) | 5.22% | 4.00% | 10.61% | 4.30% | 6.27% | **6.08%** |
| SW-S4 | 3 | [`91_08`](SWS4/results_csv_hpc_rorqual/91_08_sw4_bbfast_theta30_jrc5_dc4e5_kernel_SV_biot0p6_hpc.csv) | 4.77% | 6.49% | 16.70% | 24.46% | 32.02% | **16.89%** |
| SW-S4 | 4 | [`91_07`](SWS4/results_csv_hpc_rorqual/91_07_sw4_bbfast_theta30_jrc5_dc1p2e4_kernel_SV_biot0p6_hpc.csv) | 9.43% | 11.23% | 28.86% | 20.57% | 24.26% | **18.87%** |

## Error magnitude by file

Each metric cell is **MAE / RMSE**, in the native unit shown in the heading. Bias is discussed below and the signed residual at every stage is in the appendix.

### SW-T1

| Case | Q (mL/min) | sigma′_n (MPa) | tau (MPa) | d_n (mm) | d_s (mm) |
|---|---:|---:|---:|---:|---:|
| [`90_01`](SWT1/results_csv_hpc_rorqual/90_01_swt1_bbfast_cohesion_c26p4_kernel_SV_biot0p6_hpc.csv) | 0.1780 / 0.2538 | 1.660 / 1.948 | 2.654 / 3.107 | 0.00628 / 0.00868 | 0.02707 / 0.03433 |
| [`90_02`](SWT1/results_csv_hpc_rorqual/90_02_swt1_bbfast_cohesion_c28p0_kernel_SV_biot0p6_hpc.csv) | 1.4127 / 2.3371 | 13.548 / 17.988 | 21.679 / 28.777 | 0.07782 / 0.10061 | 0.31723 / 0.40820 |
| [`91_01`](SWT1/results_csv_hpc_rorqual/91_01_swt1_bbfast_c26p9_resc7p21_kernel_SV_biot0p6_hpc.csv) | 0.5678 / 0.8269 | 0.924 / 1.001 | 1.491 / 1.613 | 0.01619 / 0.02105 | 0.02366 / 0.02975 |
| [`91_02`](SWT1/results_csv_hpc_rorqual/91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6_hpc.csv) | 0.3211 / 0.4549 | 0.637 / 0.668 | 1.016 / 1.063 | 0.01028 / 0.01423 | 0.00430 / 0.00551 |
| [`92_01`](SWT1/results_csv_hpc_rorqual/92_01_swt1_final_c26p9_resc9p19_unld0p60_hpc.csv) | 0.4882 / 0.7061 | 0.841 / 0.891 | 1.342 / 1.420 | 0.01611 / 0.02285 | 0.00431 / 0.00551 |
| [`92_02`](SWT1/results_csv_hpc_rorqual/92_02_swt1_final_c26p9_resc9p19_unld0p30_hpc.csv) | 0.5061 / 0.7332 | 0.861 / 0.916 | 1.375 / 1.461 | 0.01669 / 0.02371 | 0.00431 / 0.00551 |

### SW-T2

| Case | Q (mL/min) | sigma′_n (MPa) | tau (MPa) | d_n (mm) | d_s (mm) |
|---|---:|---:|---:|---:|---:|
| [`90_03`](SWT2/results_csv_hpc_rorqual/90_03_swt2_bbfast_theta30_cohesion_c33p2_kernel_SV_biot0p6_hpc.csv) | 0.4131 / 0.8342 | 0.904 / 1.071 | 1.566 / 1.855 | 0.00416 / 0.00492 | 0.01415 / 0.01689 |
| [`90_04`](SWT2/results_csv_hpc_rorqual/90_04_swt2_bbfast_theta30_cohesion_c35p0_kernel_SV_biot0p6_hpc.csv) | 2.5514 / 4.0652 | 14.869 / 19.931 | 25.753 / 34.522 | 0.08323 / 0.10612 | 0.33954 / 0.43508 |
| [`91_03`](SWT2/results_csv_hpc_rorqual/91_03_swt2_bbfast_theta30_resc8p74_kernel_SV_biot0p6_hpc.csv) | 0.2988 / 0.4901 | 0.340 / 0.395 | 0.587 / 0.681 | 0.00275 / 0.00335 | 0.01254 / 0.01504 |
| [`91_04`](SWT2/results_csv_hpc_rorqual/91_04_swt2_bbfast_theta30_resc9p71_kernel_SV_biot0p6_hpc.csv) | 0.3139 / 0.6452 | 0.418 / 0.469 | 0.724 / 0.811 | 0.00255 / 0.00292 | 0.00624 / 0.00718 |

### SW-S3

| Case | Q (mL/min) | sigma′_n (MPa) | tau (MPa) | d_n (mm) | d_s (mm) |
|---|---:|---:|---:|---:|---:|
| [`90_05`](SWS3/results_csv_hpc_rorqual/90_05_sw3_bbfast_paperjrc_L123p4_cohes1p67_kernel_SV_biot0p6_hpc.csv) | 0.0436 / 0.0692 | 0.433 / 0.511 | 0.809 / 0.955 | 0.00548 / 0.00667 | 0.01007 / 0.01287 |
| [`90_06`](SWS3/results_csv_hpc_rorqual/90_06_sw3_bbfast_jrc5p69_L123p4_kernel_SV_biot0p6_hpc.csv) | 0.0453 / 0.0720 | 0.449 / 0.538 | 0.839 / 1.003 | 0.00570 / 0.00694 | 0.01045 / 0.01336 |
| [`91_05`](SWS3/results_csv_hpc_rorqual/91_05_sw3_bbfast_paperjrc_resc1p65_kernel_SV_biot0p6_hpc.csv) | 0.0190 / 0.0260 | 0.591 / 0.696 | 1.047 / 1.253 | 0.00176 / 0.00205 | 0.00173 / 0.00219 |
| [`91_06`](SWS3/results_csv_hpc_rorqual/91_06_sw3_bbfast_paperjrc_resc1p65_dc1e4_kernel_SV_biot0p6_hpc.csv) | 0.0450 / 0.0783 | 2.236 / 2.869 | 4.014 / 5.161 | 0.01623 / 0.02051 | 0.02607 / 0.03350 |
| [`92_03`](SWS3/results_csv_hpc_rorqual/92_03_sw3_final_paperjrc_resc1p40_hpc.csv) | 0.0183 / 0.0252 | 0.465 / 0.549 | 0.820 / 0.992 | 0.00091 / 0.00108 | 0.00057 / 0.00081 |
| [`92_04`](SWS3/results_csv_hpc_rorqual/92_04_sw3_final_paperjrc_resc1p20_hpc.csv) | 0.0178 / 0.0274 | 0.368 / 0.446 | 0.645 / 0.813 | 0.00093 / 0.00120 | 0.00188 / 0.00238 |

### SW-S4

| Case | Q (mL/min) | sigma′_n (MPa) | tau (MPa) | d_n (mm) | d_s (mm) |
|---|---:|---:|---:|---:|---:|
| [`90_07`](SWS4/results_csv_hpc_rorqual/90_07_sw4_bbfast_theta30_jrc9_kernel_SV_biot0p6_hpc.csv) | 0.0026 / 0.0056 | 0.489 / 0.617 | 0.817 / 1.091 | 0.00116 / 0.00176 | 0.00321 / 0.00495 |
| [`90_08`](SWS4/results_csv_hpc_rorqual/90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6_hpc.csv) | 0.0025 / 0.0053 | 0.436 / 0.577 | 0.726 / 1.030 | 0.00114 / 0.00186 | 0.00413 / 0.00554 |
| [`91_07`](SWS4/results_csv_hpc_rorqual/91_07_sw4_bbfast_theta30_jrc5_dc1p2e4_kernel_SV_biot0p6_hpc.csv) | 0.0046 / 0.0102 | 1.501 / 1.735 | 2.570 / 2.970 | 0.00745 / 0.00843 | 0.01697 / 0.01916 |
| [`91_08`](SWS4/results_csv_hpc_rorqual/91_08_sw4_bbfast_theta30_jrc5_dc4e5_kernel_SV_biot0p6_hpc.csv) | 0.0036 / 0.0052 | 0.785 / 1.003 | 1.374 / 1.718 | 0.00792 / 0.01003 | 0.02117 / 0.02530 |

+## Informational Table 2 columns

Injection pressure is the stage coordinate. Hydraulic aperture and permeability are algebraically derived from Q in the paper. They are compared here for completeness but are not included in the five-observable score. Each cell is **MAE / RMSE / nRMSE**.

### SW-T1 informational errors

| Case | P_i (MPa) | a_h (µm) | k (10^-12 m²) |
|---|---:|---:|---:|
| [`90_01`](SWT1/results_csv_hpc_rorqual/90_01_swt1_bbfast_cohesion_c26p4_kernel_SV_biot0p6_hpc.csv) | 0.000 / 0.000 / 0.00% | 0.1182 / 0.1598 / 6.50% | 0.07267 / 0.10314 / 8.89% |
| [`90_02`](SWT1/results_csv_hpc_rorqual/90_02_swt1_bbfast_cohesion_c28p0_kernel_SV_biot0p6_hpc.csv) | 0.000 / 0.000 / 0.00% | 1.0983 / 1.4774 / 60.05% | 0.48325 / 0.65739 / 56.67% |
| [`91_01`](SWT1/results_csv_hpc_rorqual/91_01_swt1_bbfast_c26p9_resc7p21_kernel_SV_biot0p6_hpc.csv) | 0.000 / 0.000 / 0.00% | 0.2718 / 0.3556 / 14.45% | 0.17750 / 0.23873 / 20.58% |
| [`91_02`](SWT1/results_csv_hpc_rorqual/91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6_hpc.csv) | 0.000 / 0.000 / 0.00% | 0.1874 / 0.2518 / 10.24% | 0.11806 / 0.16517 / 14.24% |
| [`92_01`](SWT1/results_csv_hpc_rorqual/92_01_swt1_final_c26p9_resc9p19_unld0p60_hpc.csv) | 0.000 / 0.000 / 0.00% | 0.2801 / 0.3944 / 16.03% | 0.17158 / 0.24724 / 21.31% |
| [`92_02`](SWT1/results_csv_hpc_rorqual/92_02_swt1_final_c26p9_resc9p19_unld0p30_hpc.csv) | 0.000 / 0.000 / 0.00% | 0.2896 / 0.4091 / 16.63% | 0.17728 / 0.25605 / 22.07% |

### SW-T2 informational errors

| Case | P_i (MPa) | a_h (µm) | k (10^-12 m²) |
|---|---:|---:|---:|
| [`90_03`](SWT2/results_csv_hpc_rorqual/90_03_swt2_bbfast_theta30_cohesion_c33p2_kernel_SV_biot0p6_hpc.csv) | 0.000 / 0.000 / 0.00% | 0.1387 / 0.2279 / 8.11% | 0.08768 / 0.14352 / 8.70% |
| [`90_04`](SWT2/results_csv_hpc_rorqual/90_04_swt2_bbfast_theta30_cohesion_c35p0_kernel_SV_biot0p6_hpc.csv) | 0.000 / 0.000 / 0.00% | 1.3425 / 1.7329 / 61.67% | 0.72417 / 0.95315 / 57.77% |
| [`91_03`](SWT2/results_csv_hpc_rorqual/91_03_swt2_bbfast_theta30_resc8p74_kernel_SV_biot0p6_hpc.csv) | 0.000 / 0.000 / 0.00% | 0.1347 / 0.2041 / 7.26% | 0.07584 / 0.10822 / 6.56% |
| [`91_04`](SWT2/results_csv_hpc_rorqual/91_04_swt2_bbfast_theta30_resc9p71_kernel_SV_biot0p6_hpc.csv) | 0.000 / 0.000 / 0.00% | 0.1232 / 0.2089 / 7.43% | 0.07736 / 0.12166 / 7.37% |

### SW-S3 informational errors

| Case | P_i (MPa) | a_h (µm) | k (10^-12 m²) |
|---|---:|---:|---:|
| [`90_05`](SWS3/results_csv_hpc_rorqual/90_05_sw3_bbfast_paperjrc_L123p4_cohes1p67_kernel_SV_biot0p6_hpc.csv) | 0.111 / 0.189 / 0.94% | 0.0700 / 0.0918 / 10.20% | 0.02014 / 0.02839 / 11.59% |
| [`90_06`](SWS3/results_csv_hpc_rorqual/90_06_sw3_bbfast_jrc5p69_L123p4_kernel_SV_biot0p6_hpc.csv) | 0.111 / 0.189 / 0.94% | 0.0726 / 0.0948 / 10.53% | 0.02097 / 0.02941 / 12.01% |
| [`91_05`](SWS3/results_csv_hpc_rorqual/91_05_sw3_bbfast_paperjrc_resc1p65_kernel_SV_biot0p6_hpc.csv) | 0.111 / 0.189 / 0.94% | 0.0473 / 0.0551 / 6.13% | 0.01194 / 0.01407 / 5.74% |
| [`91_06`](SWS3/results_csv_hpc_rorqual/91_06_sw3_bbfast_paperjrc_resc1p65_dc1e4_kernel_SV_biot0p6_hpc.csv) | 0.111 / 0.189 / 0.94% | 0.0883 / 0.1073 / 11.92% | 0.02411 / 0.03066 / 12.51% |
| [`92_03`](SWS3/results_csv_hpc_rorqual/92_03_sw3_final_paperjrc_resc1p40_hpc.csv) | 0.111 / 0.189 / 0.94% | 0.0452 / 0.0533 / 5.92% | 0.01138 / 0.01370 / 5.59% |
| [`92_04`](SWS3/results_csv_hpc_rorqual/92_04_sw3_final_paperjrc_resc1p20_hpc.csv) | 0.111 / 0.189 / 0.94% | 0.0437 / 0.0541 / 6.01% | 0.01091 / 0.01424 / 5.81% |

### SW-S4 informational errors

| Case | P_i (MPa) | a_h (µm) | k (10^-12 m²) |
|---|---:|---:|---:|
| [`90_07`](SWS4/results_csv_hpc_rorqual/90_07_sw4_bbfast_theta30_jrc9_kernel_SV_biot0p6_hpc.csv) | 0.163 / 0.198 / 0.99% | 0.0166 / 0.0236 / 7.14% | 0.00210 / 0.00304 / 6.20% |
| [`90_08`](SWS4/results_csv_hpc_rorqual/90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6_hpc.csv) | 0.163 / 0.198 / 0.99% | 0.0168 / 0.0233 / 7.06% | 0.00220 / 0.00301 / 6.15% |
| [`91_07`](SWS4/results_csv_hpc_rorqual/91_07_sw4_bbfast_theta30_jrc5_dc1p2e4_kernel_SV_biot0p6_hpc.csv) | 0.163 / 0.198 / 0.99% | 0.0218 / 0.0391 / 11.84% | 0.00302 / 0.00570 / 11.63% |
| [`91_08`](SWS4/results_csv_hpc_rorqual/91_08_sw4_bbfast_theta30_jrc5_dc4e5_kernel_SV_biot0p6_hpc.csv) | 0.161 / 0.194 / 0.97% | 0.0315 / 0.0388 / 11.76% | 0.00497 / 0.00628 / 12.82% |

## Largest individual discrepancy in each file

The final column scales the absolute residual by that observable’s full Table 2 range. This is diagnostic, not a separate score.

| Sample | Case | Observable | Stage | Table 2 | Model | Signed error | % of Table 2 range |
|---|---|---|---:|---:|---:|---:|---:|
| SW-T1 | [`90_01`](SWT1/results_csv_hpc_rorqual/90_01_swt1_bbfast_cohesion_c26p4_kernel_SV_biot0p6_hpc.csv) | tau (MPa) | 7 | 28.720 | 33.097 | +4.377 | 11.24% |
| SW-T1 | [`90_02`](SWT1/results_csv_hpc_rorqual/90_02_swt1_bbfast_cohesion_c28p0_kernel_SV_biot0p6_hpc.csv) | tau (MPa) | 11 | 28.230 | 67.353 | +39.123 | 100.49% |
| SW-T1 | [`91_01`](SWT1/results_csv_hpc_rorqual/91_01_swt1_bbfast_c26p9_resc7p21_kernel_SV_biot0p6_hpc.csv) | Q (mL/min) | 6 | 6.2200 | 7.7141 | +1.4941 | 24.23% |
| SW-T1 | [`91_02`](SWT1/results_csv_hpc_rorqual/91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6_hpc.csv) | d_n (mm) | 11 | -0.11300 | -0.13869 | -0.02569 | 16.36% |
| SW-T1 | [`92_01`](SWT1/results_csv_hpc_rorqual/92_01_swt1_final_c26p9_resc9p19_unld0p60_hpc.csv) | d_n (mm) | 11 | -0.11300 | -0.15478 | -0.04178 | 26.61% |
| SW-T1 | [`92_02`](SWT1/results_csv_hpc_rorqual/92_02_swt1_final_c26p9_resc9p19_unld0p30_hpc.csv) | d_n (mm) | 11 | -0.11300 | -0.15639 | -0.04339 | 27.64% |
| SW-T2 | [`90_03`](SWT2/results_csv_hpc_rorqual/90_03_swt2_bbfast_theta30_cohesion_c33p2_kernel_SV_biot0p6_hpc.csv) | Q (mL/min) | 6 | 11.1000 | 8.5466 | -2.5534 | 23.24% |
| SW-T2 | [`90_04`](SWT2/results_csv_hpc_rorqual/90_04_swt2_bbfast_theta30_cohesion_c35p0_kernel_SV_biot0p6_hpc.csv) | d_s (mm) | 7 | 0.57200 | 0.00225 | -0.56975 | 99.61% |
| SW-T2 | [`91_03`](SWT2/results_csv_hpc_rorqual/91_03_swt2_bbfast_theta30_resc8p74_kernel_SV_biot0p6_hpc.csv) | Q (mL/min) | 6 | 11.1000 | 9.7607 | -1.3393 | 12.19% |
| SW-T2 | [`91_04`](SWT2/results_csv_hpc_rorqual/91_04_swt2_bbfast_theta30_resc9p71_kernel_SV_biot0p6_hpc.csv) | Q (mL/min) | 6 | 11.1000 | 9.1363 | -1.9637 | 17.88% |
| SW-S3 | [`90_05`](SWS3/results_csv_hpc_rorqual/90_05_sw3_bbfast_paperjrc_L123p4_cohes1p67_kernel_SV_biot0p6_hpc.csv) | d_s (mm) | 6 | 0.07100 | 0.08912 | +0.01812 | 24.82% |
| SW-S3 | [`90_06`](SWS3/results_csv_hpc_rorqual/90_06_sw3_bbfast_jrc5p69_L123p4_kernel_SV_biot0p6_hpc.csv) | d_s (mm) | 6 | 0.07100 | 0.08975 | +0.01875 | 25.68% |
| SW-S3 | [`91_05`](SWS3/results_csv_hpc_rorqual/91_05_sw3_bbfast_paperjrc_resc1p65_kernel_SV_biot0p6_hpc.csv) | tau (MPa) | 6 | 3.550 | 6.188 | +2.638 | 21.29% |
| SW-S3 | [`91_06`](SWS3/results_csv_hpc_rorqual/91_06_sw3_bbfast_paperjrc_resc1p65_dc1e4_kernel_SV_biot0p6_hpc.csv) | tau (MPa) | 6 | 3.550 | 11.385 | +7.835 | 63.24% |
| SW-S3 | [`92_03`](SWS3/results_csv_hpc_rorqual/92_03_sw3_final_paperjrc_resc1p40_hpc.csv) | tau (MPa) | 6 | 3.550 | 5.792 | +2.242 | 18.10% |
| SW-S3 | [`92_04`](SWS3/results_csv_hpc_rorqual/92_04_sw3_final_paperjrc_resc1p20_hpc.csv) | tau (MPa) | 6 | 3.550 | 5.485 | +1.935 | 15.62% |
| SW-S4 | [`90_07`](SWS4/results_csv_hpc_rorqual/90_07_sw4_bbfast_theta30_jrc9_kernel_SV_biot0p6_hpc.csv) | tau (MPa) | 4 | 9.380 | 12.085 | +2.705 | 26.29% |
| SW-S4 | [`90_08`](SWS4/results_csv_hpc_rorqual/90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6_hpc.csv) | tau (MPa) | 4 | 9.380 | 12.090 | +2.710 | 26.34% |
| SW-S4 | [`91_07`](SWS4/results_csv_hpc_rorqual/91_07_sw4_bbfast_theta30_jrc5_dc1p2e4_kernel_SV_biot0p6_hpc.csv) | tau (MPa) | 6 | 3.120 | 7.406 | +4.286 | 41.65% |
| SW-S4 | [`91_08`](SWS4/results_csv_hpc_rorqual/91_08_sw4_bbfast_theta30_jrc5_dc4e5_kernel_SV_biot0p6_hpc.csv) | d_s (mm) | 5 | 0.04100 | 0.09029 | +0.04929 | 62.39% |

## Interpretation

### SW-T1

- `91_02` is the best case at **4.44%** mean nRMSE. Its strongest results are `d_s` (1.02%), sigma′_n (1.98%), and tau (2.73%). Its main remaining error is excessive negative normal displacement during unloading, reaching −0.02569 mm error at stage 11.
- `90_01` is second at 5.96%. It systematically retains too much stress and underpredicts slip.
- `92_01` and `92_02` preserve the excellent slip score of `91_02`, but increase flow nRMSE to 11.45–11.89% and normal-displacement nRMSE to 14.55–15.10%. The unloading changes therefore regress the Table 2 fit.
- `90_02` does not reproduce the main failure response: mean nRMSE is 61.01%, with stage-11 shear stress 39.12 MPa too high.

### SW-T2

- `91_03` has the lowest mean nRMSE (**2.39%**), only 0.04 percentage point below `91_04`. `91_03` is better on Q and both stresses; `91_04` is better on both displacement channels, especially shear displacement.
- This is a numerical-error ranking only. The existing `SWT2_FINAL.md` selects `91_04` on physical grounds: its residual cohesion is consistent with SW-T1 and it fits the joint displacement channels better.
- `90_03` is credible at 4.15% but underpredicts the stage-6 peak flow by 2.553 mL/min.
- `90_04` largely stays locked and misses the failure event, producing 62.67% mean nRMSE and a stage-7 slip deficit of 0.56975 mm.

### SW-S3

- `92_03` is best at **3.59%**. It has the lowest Q, d_n, and d_s nRMSE, including only 1.11% on shear displacement.
- `92_04` is close at 3.71%. Its lower residual cohesion improves sigma′_n and tau relative to `92_03`, but degrades both displacement metrics enough to lose overall.
- `91_05` is a substantial improvement over both 90-series cases, but its stage-6 shear stress is 2.638 MPa high.
- `91_06` is over-strengthened/under-slipping: it reaches 32.20% mean nRMSE, with stage-6 tau 7.835 MPa high. The 90-series cases have the opposite kinematic tendency and overpredict stage-6 slip by about 0.018 mm.

### SW-S4

- `90_08` (6.05%) and `90_07` (6.08%) are a practical tie. `90_08` is narrowly better overall and on Q, sigma′_n, and tau; `90_07` is better on both displacement channels.
- Both 90-series cases are dominated by the missed first slip burst at stage 4: shear stress is about 2.71 MPa high there.
- The `91_07` large-D_c bracket under-slips and remains too strong (18.87% mean nRMSE). The `91_08` small-D_c bracket over-slips, with stage-5 d_s 0.04929 mm too high (16.89% mean nRMSE). The two brackets fail in opposite directions and support the 90-series centre.

## Lowest-error cases and selection context

| Sample | Lowest-error case | Reason |
|---|---|---|
| SW-T1 | [`91_02`](SWT1/results_csv_hpc_rorqual/91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6_hpc.csv) | Lowest overall score; best slip and strong stress fit. |
| SW-T2 | [`91_03`](SWT2/results_csv_hpc_rorqual/91_03_swt2_bbfast_theta30_resc8p74_kernel_SV_biot0p6_hpc.csv) | Lowest numerical score, though effectively tied; the project’s physical selection remains 91_04. |
| SW-S3 | [`92_03`](SWS3/results_csv_hpc_rorqual/92_03_sw3_final_paperjrc_resc1p40_hpc.csv) | Lowest overall score and best coupled hydraulic/displacement fit. |
| SW-S4 | [`90_08`](SWS4/results_csv_hpc_rorqual/90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6_hpc.csv) | Narrow overall winner; 90_07 remains statistically near-equivalent. |

## Appendix: signed error at every Table 2 stage

All entries below are model − Table 2. Units are Q in mL/min, stresses in MPa, and displacements in mm.

<details>
<summary><strong>SW-T1: all cases and stages</strong></summary>

| Case | Stage | Branch | P_i (MPa) | ΔQ | Δsigma′_n | Δtau | Δd_n | Δd_s |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 90_01 | 1 | loading | 8 | -2.06e-04 | +0.260 | +0.422 | +0.00000 | +0.00000 |
| 90_01 | 2 | loading | 12 | +0.0092 | +0.413 | +0.676 | -0.00001 | +0.00001 |
| 90_01 | 3 | loading | 16 | +0.0036 | +0.547 | +0.902 | -0.00003 | -0.00099 |
| 90_01 | 4 | loading | 20 | -0.0160 | +0.736 | +1.186 | +0.00090 | -0.00183 |
| 90_01 | 5 | loading | 24 | -0.0513 | +0.840 | +1.343 | +0.00192 | -0.00457 |
| 90_01 | 6 | loading | 28 | -0.4831 | +2.671 | +4.194 | +0.01101 | -0.04579 |
| 90_01 | 7 | unloading | 24 | +0.1207 | +2.732 | +4.377 | -0.00131 | -0.05284 |
| 90_01 | 8 | unloading | 20 | +0.4144 | +2.626 | +4.198 | -0.00643 | -0.04788 |
| 90_01 | 9 | unloading | 16 | +0.4148 | +2.527 | +4.034 | -0.01064 | -0.04292 |
| 90_01 | 10 | unloading | 12 | +0.3091 | +2.469 | +3.950 | -0.01356 | -0.03894 |
| 90_01 | 11 | unloading | 8 | +0.1361 | +2.443 | +3.910 | -0.01695 | -0.03497 |
| 90_02 | 1 | loading | 8 | -2.06e-04 | +0.260 | +0.422 | +0.00000 | +0.00000 |
| 90_02 | 2 | loading | 12 | +0.0092 | +0.413 | +0.676 | -0.00001 | +0.00001 |
| 90_02 | 3 | loading | 16 | +0.0036 | +0.547 | +0.902 | -0.00003 | -0.00099 |
| 90_02 | 4 | loading | 20 | -0.0160 | +0.731 | +1.178 | +0.00095 | -0.00198 |
| 90_02 | 5 | loading | 24 | -0.0546 | +0.986 | +1.576 | +0.00285 | -0.00774 |
| 90_02 | 6 | loading | 28 | -5.8112 | +24.060 | +38.424 | +0.15600 | -0.52892 |
| 90_02 | 7 | unloading | 24 | -3.9325 | +24.357 | +38.985 | +0.13803 | -0.53592 |
| 90_02 | 8 | unloading | 20 | -2.6036 | +24.403 | +39.049 | +0.12905 | -0.53093 |
| 90_02 | 9 | unloading | 16 | -1.7047 | +24.407 | +39.050 | +0.12207 | -0.52594 |
| 90_02 | 10 | unloading | 12 | -0.9958 | +24.421 | +39.080 | +0.11709 | -0.52195 |
| 90_02 | 11 | unloading | 8 | -0.4088 | +24.447 | +39.123 | +0.11210 | -0.51796 |
| 91_01 | 1 | loading | 8 | -2.06e-04 | +0.260 | +0.422 | +0.00000 | +0.00000 |
| 91_01 | 2 | loading | 12 | +0.0092 | +0.413 | +0.676 | -0.00001 | +0.00001 |
| 91_01 | 3 | loading | 16 | +0.0036 | +0.547 | +0.902 | -0.00003 | -0.00099 |
| 91_01 | 4 | loading | 20 | -0.0160 | +0.741 | +1.194 | +0.00094 | -0.00194 |
| 91_01 | 5 | loading | 24 | -0.0541 | +0.926 | +1.479 | +0.00247 | -0.00645 |
| 91_01 | 6 | loading | 28 | +1.4941 | -0.915 | -1.544 | -0.01440 | +0.03600 |
| 91_01 | 7 | unloading | 24 | +1.4434 | -0.980 | -1.563 | -0.02345 | +0.02893 |
| 91_01 | 8 | unloading | 20 | +1.3086 | -1.168 | -1.873 | -0.02646 | +0.03387 |
| 91_01 | 9 | unloading | 16 | +0.9981 | -1.322 | -2.125 | -0.02925 | +0.03883 |
| 91_01 | 10 | unloading | 12 | +0.6479 | -1.418 | -2.271 | -0.03114 | +0.04279 |
| 91_01 | 11 | unloading | 8 | +0.2709 | -1.471 | -2.354 | -0.03375 | +0.04676 |
| 91_02 | 1 | loading | 8 | -2.06e-04 | +0.260 | +0.422 | +0.00000 | +0.00000 |
| 91_02 | 2 | loading | 12 | +0.0092 | +0.413 | +0.676 | -0.00001 | +0.00001 |
| 91_02 | 3 | loading | 16 | +0.0036 | +0.547 | +0.902 | -0.00003 | -0.00099 |
| 91_02 | 4 | loading | 20 | -0.0160 | +0.741 | +1.194 | +0.00094 | -0.00194 |
| 91_02 | 5 | loading | 24 | -0.0541 | +0.927 | +1.481 | +0.00248 | -0.00647 |
| 91_02 | 6 | loading | 28 | +0.4508 | +0.873 | +1.316 | -0.00163 | -0.00485 |
| 91_02 | 7 | unloading | 24 | +0.7587 | +0.876 | +1.408 | -0.01248 | -0.01191 |
| 91_02 | 8 | unloading | 20 | +0.8526 | +0.733 | +1.169 | -0.01664 | -0.00696 |
| 91_02 | 9 | unloading | 16 | +0.7042 | +0.609 | +0.965 | -0.02021 | -0.00200 |
| 91_02 | 10 | unloading | 12 | +0.4788 | +0.534 | +0.852 | -0.02266 | +0.00197 |
| 91_02 | 11 | unloading | 8 | +0.2041 | +0.495 | +0.792 | -0.02569 | +0.00595 |
| 92_01 | 1 | loading | 8 | -2.06e-04 | +0.260 | +0.422 | +0.00000 | +0.00000 |
| 92_01 | 2 | loading | 12 | +0.0092 | +0.413 | +0.676 | -0.00001 | +0.00001 |
| 92_01 | 3 | loading | 16 | +0.0036 | +0.547 | +0.902 | -0.00003 | -0.00099 |
| 92_01 | 4 | loading | 20 | -0.0160 | +0.741 | +1.194 | +0.00094 | -0.00194 |
| 92_01 | 5 | loading | 24 | -0.0541 | +0.927 | +1.481 | +0.00248 | -0.00647 |
| 92_01 | 6 | loading | 28 | +0.4509 | +0.873 | +1.316 | -0.00163 | -0.00485 |
| 92_01 | 7 | unloading | 24 | +1.1408 | +1.101 | +1.768 | -0.01823 | -0.01187 |
| 92_01 | 8 | unloading | 20 | +1.3477 | +1.108 | +1.769 | -0.02627 | -0.00689 |
| 92_01 | 9 | unloading | 16 | +1.1653 | +1.088 | +1.732 | -0.03260 | -0.00190 |
| 92_01 | 10 | unloading | 12 | +0.8181 | +1.087 | +1.737 | -0.03712 | +0.00208 |
| 92_01 | 11 | unloading | 8 | +0.3647 | +1.101 | +1.763 | -0.04178 | +0.00607 |
| 92_02 | 1 | loading | 8 | -2.06e-04 | +0.260 | +0.422 | +0.00000 | +0.00000 |
| 92_02 | 2 | loading | 12 | +0.0092 | +0.413 | +0.676 | -0.00001 | +0.00001 |
| 92_02 | 3 | loading | 16 | +0.0036 | +0.547 | +0.902 | -0.00003 | -0.00099 |
| 92_02 | 4 | loading | 20 | -0.0160 | +0.741 | +1.194 | +0.00094 | -0.00194 |
| 92_02 | 5 | loading | 24 | -0.0541 | +0.927 | +1.481 | +0.00248 | -0.00647 |
| 92_02 | 6 | loading | 28 | +0.4509 | +0.873 | +1.317 | -0.00163 | -0.00485 |
| 92_02 | 7 | unloading | 24 | +1.1798 | +1.123 | +1.804 | -0.01879 | -0.01186 |
| 92_02 | 8 | unloading | 20 | +1.4002 | +1.146 | +1.830 | -0.02722 | -0.00688 |
| 92_02 | 9 | unloading | 16 | +1.2153 | +1.137 | +1.810 | -0.03384 | -0.00189 |
| 92_02 | 10 | unloading | 12 | +0.8554 | +1.144 | +1.828 | -0.03857 | +0.00210 |
| 92_02 | 11 | unloading | 8 | +0.3824 | +1.163 | +1.862 | -0.04339 | +0.00609 |

</details>

<details>
<summary><strong>SW-T2: all cases and stages</strong></summary>

| Case | Stage | Branch | P_i (MPa) | ΔQ | Δsigma′_n | Δtau | Δd_n | Δd_s |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 90_03 | 1 | loading | 8 | -6.19e-04 | -0.596 | -1.009 | +0.00000 | +0.00000 |
| 90_03 | 2 | loading | 12 | -0.0090 | -0.337 | -0.594 | +0.00099 | -0.00099 |
| 90_03 | 3 | loading | 16 | -0.0301 | -0.124 | -0.211 | +0.00197 | -0.00298 |
| 90_03 | 4 | loading | 20 | -0.1769 | +0.116 | +0.202 | +0.00295 | -0.00695 |
| 90_03 | 5 | loading | 24 | -0.7757 | +0.352 | +0.614 | +0.00417 | -0.01193 |
| 90_03 | 6 | loading | 28 | -2.5534 | +1.682 | +2.904 | +0.00383 | -0.02686 |
| 90_03 | 7 | unloading | 24 | -0.6591 | +1.561 | +2.710 | +0.00782 | -0.02791 |
| 90_03 | 8 | unloading | 20 | -0.2473 | +1.429 | +2.480 | +0.00712 | -0.02194 |
| 90_03 | 9 | unloading | 16 | -0.0733 | +1.302 | +2.251 | +0.00850 | -0.02096 |
| 90_03 | 10 | unloading | 12 | -0.0115 | +1.248 | +2.170 | +0.00335 | -0.01298 |
| 90_03 | 11 | unloading | 8 | -0.0073 | +1.199 | +2.076 | +0.00090 | -0.00800 |
| 90_04 | 1 | loading | 8 | -6.19e-04 | -0.596 | -1.009 | +0.00000 | +0.00000 |
| 90_04 | 2 | loading | 12 | -0.0090 | -0.337 | -0.594 | +0.00099 | -0.00099 |
| 90_04 | 3 | loading | 16 | -0.0301 | -0.124 | -0.211 | +0.00197 | -0.00298 |
| 90_04 | 4 | loading | 20 | -0.1769 | +0.113 | +0.198 | +0.00295 | -0.00697 |
| 90_04 | 5 | loading | 24 | -0.7783 | +0.480 | +0.835 | +0.00492 | -0.01494 |
| 90_04 | 6 | loading | 28 | -10.2167 | +26.958 | +46.683 | +0.14135 | -0.56874 |
| 90_04 | 7 | unloading | 24 | -6.4715 | +27.033 | +46.830 | +0.14138 | -0.56975 |
| 90_04 | 8 | unloading | 20 | -4.5757 | +27.023 | +46.810 | +0.13840 | -0.56375 |
| 90_04 | 9 | unloading | 16 | -3.1193 | +26.976 | +46.718 | +0.13842 | -0.56276 |
| 90_04 | 10 | unloading | 12 | -1.8925 | +26.975 | +46.731 | +0.13244 | -0.55477 |
| 90_04 | 11 | unloading | 8 | -0.7954 | +26.941 | +46.662 | +0.12945 | -0.54979 |
| 91_03 | 1 | loading | 8 | -6.19e-04 | -0.596 | -1.009 | +0.00000 | +0.00000 |
| 91_03 | 2 | loading | 12 | -0.0090 | -0.337 | -0.594 | +0.00099 | -0.00099 |
| 91_03 | 3 | loading | 16 | -0.0301 | -0.124 | -0.211 | +0.00197 | -0.00298 |
| 91_03 | 4 | loading | 20 | -0.1769 | +0.116 | +0.202 | +0.00295 | -0.00695 |
| 91_03 | 5 | loading | 24 | -0.7755 | +0.347 | +0.606 | +0.00414 | -0.01182 |
| 91_03 | 6 | loading | 28 | -1.3393 | -0.011 | -0.028 | -0.00601 | +0.01004 |
| 91_03 | 7 | unloading | 24 | +0.1453 | -0.180 | -0.305 | -0.00061 | +0.00898 |
| 91_03 | 8 | unloading | 20 | +0.2872 | -0.344 | -0.591 | -0.00043 | +0.01495 |
| 91_03 | 9 | unloading | 16 | +0.2692 | -0.494 | -0.860 | +0.00148 | +0.01592 |
| 91_03 | 10 | unloading | 12 | +0.1843 | -0.564 | -0.968 | -0.00335 | +0.02390 |
| 91_03 | 11 | unloading | 8 | +0.0697 | -0.623 | -1.080 | -0.00561 | +0.02888 |
| 91_04 | 1 | loading | 8 | -6.19e-04 | -0.596 | -1.009 | +0.00000 | +0.00000 |
| 91_04 | 2 | loading | 12 | -0.0090 | -0.337 | -0.594 | +0.00099 | -0.00099 |
| 91_04 | 3 | loading | 16 | -0.0301 | -0.124 | -0.211 | +0.00197 | -0.00298 |
| 91_04 | 4 | loading | 20 | -0.1769 | +0.116 | +0.202 | +0.00295 | -0.00695 |
| 91_04 | 5 | loading | 24 | -0.7756 | +0.350 | +0.610 | +0.00416 | -0.01188 |
| 91_04 | 6 | loading | 28 | -1.9637 | +0.829 | +1.427 | -0.00109 | -0.00830 |
| 91_04 | 7 | unloading | 24 | -0.2655 | +0.685 | +1.193 | +0.00356 | -0.00935 |
| 91_04 | 8 | unloading | 20 | +0.0163 | +0.538 | +0.937 | +0.00327 | -0.00338 |
| 91_04 | 9 | unloading | 16 | +0.0968 | +0.400 | +0.689 | +0.00489 | -0.00241 |
| 91_04 | 10 | unloading | 12 | +0.0864 | +0.339 | +0.595 | -0.00012 | +0.00557 |
| 91_04 | 11 | unloading | 8 | +0.0315 | +0.285 | +0.492 | -0.00248 | +0.01056 |

</details>

<details>
<summary><strong>SW-S3: all cases and stages</strong></summary>

| Case | Stage | Branch | P_i (MPa) | ΔQ | Δsigma′_n | Δtau | Δd_n | Δd_s |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 90_05 | 1 | loading | 8 | -1.97e-04 | -0.514 | -0.969 | +0.00000 | +0.00000 |
| 90_05 | 2 | loading | 12 | +0.0035 | -0.362 | -0.629 | -0.00022 | +0.00002 |
| 90_05 | 3 | loading | 16 | +0.0113 | -0.250 | -0.301 | -0.00052 | +0.00005 |
| 90_05 | 4 | loading | 20 | +0.0079 | +0.007 | +0.058 | -0.00095 | -0.00093 |
| 90_05 | 5 | loading | 24 | +0.0403 | +0.242 | +0.460 | -0.00209 | -0.00021 |
| 90_05 | 6 | loading | 28 | +0.1210 | +0.053 | +0.213 | -0.01029 | +0.01812 |
| 90_05 | 7 | unloading | 24 | +0.1649 | -0.380 | -0.727 | -0.00859 | +0.01698 |
| 90_05 | 8 | unloading | 20 | +0.0893 | -0.614 | -1.110 | -0.00742 | +0.01692 |
| 90_05 | 9 | unloading | 16 | +0.0322 | -0.693 | -1.340 | -0.00763 | +0.01587 |
| 90_05 | 10 | unloading | 12 | +0.0078 | -0.788 | -1.461 | -0.00818 | +0.01583 |
| 90_05 | 11 | unloading | 8 | -0.0013 | -0.854 | -1.630 | -0.00889 | +0.01580 |
| 90_06 | 1 | loading | 8 | -1.97e-04 | -0.514 | -0.969 | +0.00000 | +0.00000 |
| 90_06 | 2 | loading | 12 | +0.0035 | -0.362 | -0.629 | -0.00022 | +0.00002 |
| 90_06 | 3 | loading | 16 | +0.0113 | -0.250 | -0.301 | -0.00052 | +0.00005 |
| 90_06 | 4 | loading | 20 | +0.0079 | +0.007 | +0.058 | -0.00095 | -0.00093 |
| 90_06 | 5 | loading | 24 | +0.0407 | +0.241 | +0.457 | -0.00211 | -0.00018 |
| 90_06 | 6 | loading | 28 | +0.1283 | +0.010 | +0.135 | -0.01066 | +0.01875 |
| 90_06 | 7 | unloading | 24 | +0.1701 | -0.423 | -0.805 | -0.00896 | +0.01762 |
| 90_06 | 8 | unloading | 20 | +0.0926 | -0.658 | -1.190 | -0.00778 | +0.01755 |
| 90_06 | 9 | unloading | 16 | +0.0341 | -0.738 | -1.422 | -0.00799 | +0.01650 |
| 90_06 | 10 | unloading | 12 | +0.0088 | -0.835 | -1.545 | -0.00854 | +0.01646 |
| 90_06 | 11 | unloading | 8 | -9.29e-04 | -0.902 | -1.715 | -0.00924 | +0.01643 |
| 91_05 | 1 | loading | 8 | -1.97e-04 | -0.514 | -0.969 | +0.00000 | +0.00000 |
| 91_05 | 2 | loading | 12 | +0.0035 | -0.362 | -0.629 | -0.00022 | +0.00002 |
| 91_05 | 3 | loading | 16 | +0.0113 | -0.250 | -0.301 | -0.00052 | +0.00005 |
| 91_05 | 4 | loading | 20 | +0.0079 | +0.007 | +0.058 | -0.00095 | -0.00093 |
| 91_05 | 5 | loading | 24 | +0.0400 | +0.244 | +0.462 | -0.00208 | -0.00024 |
| 91_05 | 6 | loading | 28 | -0.0583 | +1.397 | +2.638 | +0.00089 | -0.00116 |
| 91_05 | 7 | unloading | 24 | +0.0409 | +0.980 | +1.726 | +0.00244 | -0.00229 |
| 91_05 | 8 | unloading | 20 | +0.0115 | +0.774 | +1.395 | +0.00343 | -0.00235 |
| 91_05 | 9 | unloading | 16 | -0.0114 | +0.724 | +1.217 | +0.00305 | -0.00339 |
| 91_05 | 10 | unloading | 12 | -0.0150 | +0.649 | +1.132 | +0.00241 | -0.00343 |
| 91_05 | 11 | unloading | 8 | -0.0094 | +0.596 | +0.986 | +0.00164 | -0.00345 |
| 91_06 | 1 | loading | 8 | -1.97e-04 | -0.514 | -0.969 | +0.00000 | +0.00000 |
| 91_06 | 2 | loading | 12 | +0.0035 | -0.362 | -0.629 | -0.00022 | +0.00002 |
| 91_06 | 3 | loading | 16 | +0.0113 | -0.250 | -0.301 | -0.00052 | +0.00005 |
| 91_06 | 4 | loading | 20 | +0.0079 | +0.007 | +0.058 | -0.00095 | -0.00093 |
| 91_06 | 5 | loading | 24 | +0.0393 | +0.247 | +0.468 | -0.00203 | -0.00031 |
| 91_06 | 6 | loading | 28 | -0.2373 | +4.278 | +7.835 | +0.02389 | -0.04174 |
| 91_06 | 7 | unloading | 24 | -0.0681 | +3.926 | +7.041 | +0.02633 | -0.04286 |
| 91_06 | 8 | unloading | 20 | -0.0469 | +3.786 | +6.828 | +0.02767 | -0.04291 |
| 91_06 | 9 | unloading | 16 | -0.0392 | +3.785 | +6.738 | +0.02748 | -0.04395 |
| 91_06 | 10 | unloading | 12 | -0.0277 | +3.737 | +6.704 | +0.02696 | -0.04397 |
| 91_06 | 11 | unloading | 8 | -0.0135 | +3.700 | +6.587 | +0.02629 | -0.04400 |
| 92_03 | 1 | loading | 8 | -1.97e-04 | -0.514 | -0.969 | +0.00000 | +0.00000 |
| 92_03 | 2 | loading | 12 | +0.0035 | -0.362 | -0.629 | -0.00022 | +0.00002 |
| 92_03 | 3 | loading | 16 | +0.0113 | -0.250 | -0.301 | -0.00052 | +0.00005 |
| 92_03 | 4 | loading | 20 | +0.0079 | +0.007 | +0.058 | -0.00095 | -0.00093 |
| 92_03 | 5 | loading | 24 | +0.0400 | +0.244 | +0.462 | -0.00208 | -0.00024 |
| 92_03 | 6 | loading | 28 | -0.0325 | +1.178 | +2.242 | -0.00095 | +0.00201 |
| 92_03 | 7 | unloading | 24 | +0.0581 | +0.757 | +1.324 | +0.00063 | +0.00088 |
| 92_03 | 8 | unloading | 20 | +0.0219 | +0.546 | +0.983 | +0.00165 | +0.00081 |
| 92_03 | 9 | unloading | 16 | -0.0057 | +0.491 | +0.796 | +0.00130 | -0.00023 |
| 92_03 | 10 | unloading | 12 | -0.0121 | +0.412 | +0.705 | +0.00067 | -0.00027 |
| 92_03 | 11 | unloading | 8 | -0.0084 | +0.357 | +0.556 | -0.00008 | -0.00030 |
| 92_04 | 1 | loading | 8 | -1.97e-04 | -0.514 | -0.969 | +0.00000 | +0.00000 |
| 92_04 | 2 | loading | 12 | +0.0035 | -0.362 | -0.629 | -0.00022 | +0.00002 |
| 92_04 | 3 | loading | 16 | +0.0113 | -0.250 | -0.301 | -0.00052 | +0.00005 |
| 92_04 | 4 | loading | 20 | +0.0079 | +0.007 | +0.058 | -0.00095 | -0.00093 |
| 92_04 | 5 | loading | 24 | +0.0401 | +0.244 | +0.461 | -0.00208 | -0.00023 |
| 92_04 | 6 | loading | 28 | -0.0115 | +1.007 | +1.935 | -0.00237 | +0.00445 |
| 92_04 | 7 | unloading | 24 | +0.0723 | +0.584 | +1.012 | -0.00077 | +0.00332 |
| 92_04 | 8 | unloading | 20 | +0.0306 | +0.369 | +0.664 | +0.00027 | +0.00326 |
| 92_04 | 9 | unloading | 16 | -9.48e-04 | +0.311 | +0.471 | -0.00005 | +0.00221 |
| 92_04 | 10 | unloading | 12 | -0.0096 | +0.230 | +0.375 | -0.00067 | +0.00218 |
| 92_04 | 11 | unloading | 8 | -0.0075 | +0.173 | +0.223 | -0.00142 | +0.00215 |

</details>

<details>
<summary><strong>SW-S4: all cases and stages</strong></summary>

| Case | Stage | Branch | P_i (MPa) | ΔQ | Δsigma′_n | Δtau | Δd_n | Δd_s |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| 90_07 | 1 | loading | 8 | +6.09e-05 | -0.155 | -0.214 | +0.00000 | +0.00000 |
| 90_07 | 2 | loading | 12 | +7.69e-04 | -0.231 | -0.178 | -0.00035 | +0.00000 |
| 90_07 | 3 | loading | 16 | -1.07e-05 | -0.027 | +0.242 | +0.00015 | +0.00001 |
| 90_07 | 4 | loading | 20 | +8.80e-04 | +1.409 | +2.705 | +0.00467 | -0.01337 |
| 90_07 | 5 | loading | 24 | -0.0033 | +0.624 | +1.182 | -0.00250 | +0.00518 |
| 90_07 | 6 | loading | 28 | -0.0181 | +0.823 | +1.410 | -0.00102 | +0.00434 |
| 90_07 | 7 | unloading | 24 | -0.0015 | +0.632 | +1.028 | -0.00017 | +0.00330 |
| 90_07 | 8 | unloading | 20 | +0.0024 | +0.594 | +0.779 | +0.00081 | +0.00227 |
| 90_07 | 9 | unloading | 16 | +5.96e-04 | +0.453 | +0.603 | +0.00060 | +0.00124 |
| 90_07 | 10 | unloading | 12 | +7.52e-04 | +0.296 | +0.441 | +0.00076 | +0.00122 |
| 90_07 | 11 | unloading | 8 | +2.78e-04 | +0.132 | +0.203 | +0.00055 | +0.00120 |
| 90_08 | 1 | loading | 8 | +6.09e-05 | -0.155 | -0.214 | +0.00000 | +0.00000 |
| 90_08 | 2 | loading | 12 | +7.69e-04 | -0.231 | -0.178 | -0.00035 | +0.00000 |
| 90_08 | 3 | loading | 16 | -1.12e-05 | -0.027 | +0.242 | +0.00015 | +0.00001 |
| 90_08 | 4 | loading | 20 | +8.70e-04 | +1.412 | +2.710 | +0.00469 | -0.01342 |
| 90_08 | 5 | loading | 24 | -0.0033 | +0.554 | +1.060 | -0.00300 | +0.00633 |
| 90_08 | 6 | loading | 28 | -0.0171 | +0.738 | +1.263 | -0.00166 | +0.00574 |
| 90_08 | 7 | unloading | 24 | -8.94e-04 | +0.549 | +0.885 | -0.00073 | +0.00463 |
| 90_08 | 8 | unloading | 20 | +0.0028 | +0.510 | +0.634 | +0.00029 | +0.00359 |
| 90_08 | 9 | unloading | 16 | +8.11e-04 | +0.367 | +0.454 | +0.00011 | +0.00256 |
| 90_08 | 10 | unloading | 12 | +8.62e-04 | +0.209 | +0.291 | +0.00030 | +0.00254 |
| 90_08 | 11 | unloading | 8 | +3.17e-04 | +0.045 | +0.051 | +0.00010 | +0.00252 |
| 91_07 | 1 | loading | 8 | +6.09e-05 | -0.155 | -0.214 | +0.00000 | +0.00000 |
| 91_07 | 2 | loading | 12 | +7.69e-04 | -0.231 | -0.178 | -0.00035 | +0.00000 |
| 91_07 | 3 | loading | 16 | -1.13e-05 | -0.027 | +0.242 | +0.00015 | +0.00001 |
| 91_07 | 4 | loading | 20 | +1.36e-04 | +1.478 | +2.825 | +0.00525 | -0.01458 |
| 91_07 | 5 | loading | 24 | +0.0046 | +2.060 | +3.670 | +0.00769 | -0.01803 |
| 91_07 | 6 | loading | 28 | -0.0320 | +2.484 | +4.286 | +0.01160 | -0.02310 |
| 91_07 | 7 | unloading | 24 | -0.0095 | +2.175 | +3.701 | +0.01020 | -0.02134 |
| 91_07 | 8 | unloading | 20 | -0.0019 | +2.172 | +3.513 | +0.01047 | -0.02238 |
| 91_07 | 9 | unloading | 16 | -0.0018 | +2.054 | +3.376 | +0.00981 | -0.02340 |
| 91_07 | 10 | unloading | 12 | -3.73e-04 | +1.912 | +3.241 | +0.00969 | -0.02342 |
| 91_07 | 11 | unloading | 8 | +3.16e-05 | +1.759 | +3.020 | +0.00929 | -0.02343 |
| 91_08 | 1 | loading | 8 | +6.22e-05 | -0.156 | -0.214 | +0.00000 | +0.00000 |
| 91_08 | 2 | loading | 12 | +7.54e-04 | -0.227 | -0.178 | -0.00035 | +0.00000 |
| 91_08 | 3 | loading | 16 | -5.36e-06 | -0.028 | +0.242 | +0.00015 | +0.00001 |
| 91_08 | 4 | loading | 20 | -9.78e-04 | -1.706 | -2.699 | -0.01610 | +0.03589 |
| 91_08 | 5 | loading | 24 | +0.0108 | -2.119 | -3.569 | -0.02114 | +0.04929 |
| 91_08 | 6 | loading | 28 | -0.0019 | -0.390 | -0.692 | -0.00974 | +0.02399 |
| 91_08 | 7 | unloading | 24 | +0.0085 | -0.552 | -1.019 | -0.00786 | +0.02198 |
| 91_08 | 8 | unloading | 20 | +0.0085 | -0.619 | -1.313 | -0.00632 | +0.02093 |
| 91_08 | 9 | unloading | 16 | +0.0041 | -0.774 | -1.523 | -0.00613 | +0.01990 |
| 91_08 | 10 | unloading | 12 | +0.0026 | -0.946 | -1.707 | -0.00570 | +0.01988 |
| 91_08 | 11 | unloading | 8 | +9.56e-04 | -1.116 | -1.960 | -0.00574 | +0.01986 |

</details>

## Reproduction

Run any case with:

```bash
python3 scripts/table2_gate.py --tag hpc path/to/results_csv_hpc_rorqual/<case>_hpc.csv
```

The source CSV link in each case label above identifies every file included in this audit.

---

# Addendum — independent verification, and three corrections to the framing

*2026-08-18. Added after re-deriving every number in this document from the CSVs with
`scripts/table2_gate.py` plus an independent nRMSE recomputation.*

## Verification result

**All twenty cases reproduce to the digit** — every MAE, every RMSE, every nRMSE and every rank
order in the tables above. No correction to any figure in this document.

The stage-1 exclusion convention used here is the correct one and the older `SWT1_FINAL.md` /
`SWS3_FINAL.md` headlines were the ones in error: they included the constructed stage-1 zero in
the `d_n`/`d_s` RMSE, which dilutes both by exactly `sqrt(10/11)`. Those two files have been
corrected to **4.44 %** and **3.59 %**; `SWT2_FINAL.md` and `SWS4_FINAL.md` were already
consistent with this document.

## Three things that should be added before this goes near the paper

### 1. SW-S3's `d_n` is not measured on the same channel as the other three

`92_03` and `92_08` are the only decks in the campaign that set

```
reported_reversible_normal_opening_scale              = 0.758   # library default 1.0
reported_reversible_normal_opening_retention_fraction = 0.552   # library default 0.0
```

The material source labels both **OUTPUT ONLY** — they change neither contact, nor aperture, nor
permeability, nor flow, only the reconstruction of `normal_opening_total`, which is the column the
gate reads for `d_n`.

| specimen | `d_n` via `normal_opening_total` | `d_n` via the raw kinematic jump | delta |
|---|---|---|---|
| SW-T1 `91_02` | 9.06 | 9.06 | 0.00 |
| SW-T2 `91_04` | 2.06 | 2.06 | 0.00 |
| **SW-S3 `92_03`** | **2.46** | **7.42** | **+4.96** |

SW-T1 and SW-T2 agree exactly because their knobs are at defaults — which is how we know the
knobs, not the channel choice, are the effect. **SW-S3's entry in the best-case table moves
3.59 % → 4.58 %, and its rank in the all-case ranking moves with it.** The 93-series decks
(`93_05`, `93_06`) run at the library defaults.

### 2. `Q` is not independent of `d_n`, so the five-observable mean over-counts

The Method section correctly excludes `a_h` and `k` because the paper back-computes them from `Q`
through the cubic law. The same argument applies one step further: **model `Q` tracks the cube of
the model aperture to 1.000 ± 0.01 at every stage**, so `Q` and `d_n` are one measurement counted
twice. `σ'ₙ` and `τ` are likewise two projections of one stress state through eqs (3)/(4).

The honest count of independent constraints per specimen is **three** — a stress state, an
aperture, a slip — not five. The five-observable mean is still a fine summary statistic, but it
should be described as such rather than as an average over five independent tests, and a defect in
the aperture will show up twice in it.

### 3. SW-T1's mesh-5 source separation is 4.6 % short, and the mesh-3 pair is not a clean control

`91_02` asked for source coordinates 1.678 mm off the nearest `fracture_interface` node.
`ExtraNodesetGenerator` with `use_closest_node = true` never errors, so the run silently used the
snapped node pair. The seven other decks in the 90/91/92 series are exact to 0.00 µm.

The intended injection–production separation is 72.690 mm; the pair actually used spans
**69.335 mm (−4.62 %)**. The mesh-5 node pitch along the fracture is 4.333 mm, so the reachable
symmetric separations are 69.335 and 78.002 mm — the snapped one is the closer, and mesh 5 cannot
do better without remeshing. Mesh 3 reaches 71.501 mm.

Two consequences for this document:

* `Q` is computed as `(W/L)/(12 µ) · a_h³ · Δp` with `W/L` a fixed constant inverted from Table 2,
  so the path length enters through `pp_drop_pp`. A first-order `Q` bias of about this size is
  expected on SW-T1 mesh 5, which is the specimen with the largest `Q` nRMSE in the table (7.38 %).
* the SW-T1 mesh-5/mesh-3 pair differs by **3.1 % in source separation**, which is not
  discretisation. That is a caveat on the pending convergence comparison, not on the scores here.

`93_01` names the node it was always using, so the deck is reproducible; no number changes and
`91_02` remains a valid run.

---

# Update — new 92/93 results and preliminary mesh convergence

*2026-08-18. This section extends the original twenty-case audit without changing its error definition or stage-1 displacement convention.*

## Updated outcome

The four odd-numbered 93-series mesh-5 runs are complete. The 93-series is primarily a **postprocessor and reporting audit**, not a new constitutive calibration.

| Sample | Completed 93 case | Parent | Stages | Q nRMSE | sigma′_n | tau | d_n | d_s | Mean nRMSE | Assessment |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| SW-T1 | [`93_01`](SWT1/results_csv_hpc_rorqual/93_01_swt1_final_c26p9_resc9p19_ppfix_hpc.csv) | `91_02` | 11/11 | 7.38% | 1.98% | 2.73% | 9.06% | 1.02% | **4.44%** | Numerically identical to the parent; source-node/reporting cleanup is safe. |
| SW-T2 | [`93_03`](SWT2/results_csv_hpc_rorqual/93_03_swt2_final_theta30_resc9p71_ppfix_hpc.csv) | `91_04` | 11/11 | 5.87% | 1.26% | 1.70% | 2.06% | 1.25% | **2.43%** | Numerically identical to the physically selected parent. |
| SW-S3 | [`93_05`](SWS3/results_csv_hpc_rorqual/93_05_sw3_final_resc1p40_ppfix_hpc.csv) | `92_03` | 11/11 | 3.00% | 3.35% | 8.01% | 7.42% | 1.11% | **4.58%** | Only d_n changes; raw/default reporting exposes the honest mismatch. |
| SW-S4 | [`93_07`](SWS4/results_csv_hpc_rorqual/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv) | `90_08` | 11/11 | 4.94% | 3.74% | 10.01% | 4.53% | 7.01% | **6.05%** | Numerically identical to the parent; reporting cleanup is safe. |

At the eleven sampled stages, SW-T1, SW-T2, and SW-S4 differ from their parents only at floating-point roundoff (no scored model value changes materially). SW-S3 has identical Q, stress, slip, aperture, and permeability results; only the normal-displacement reporting channel changes.

## SW-S3 reporting correction

Removing `reported_reversible_normal_opening_scale = 0.758` and `reported_reversible_normal_opening_retention_fraction = 0.552` changes the SW-S3 normal-displacement nRMSE from **2.46% to 7.42%**, and the five-observable mean from **3.59% to 4.58%**. These were output-only settings, so the worse score is the scientifically preferable result: it reports the raw/default kinematic jump consistently across specimens.

| Stage | Branch | P_i (MPa) | Table 2 d_n (mm) | 92_03 adjusted d_n | 93_05 raw/default d_n | 93_05 error |
|---:|---|---:|---:|---:|---:|---:|
| 1 | loading | 8 | 0.00000 | 0.00000 | 0.00000 | +0.00000 |
| 2 | loading | 12 | 0.00000 | -0.00022 | -0.00028 | -0.00028 |
| 3 | loading | 16 | 0.00000 | -0.00052 | -0.00069 | -0.00069 |
| 4 | loading | 20 | 0.00000 | -0.00095 | -0.00125 | -0.00125 |
| 5 | loading | 24 | 0.00000 | -0.00208 | -0.00264 | -0.00264 |
| 6 | loading | 28 | -0.04400 | -0.04495 | -0.04780 | -0.00380 |
| 7 | unloading | 24 | -0.04400 | -0.04337 | -0.04314 | +0.00086 |
| 8 | unloading | 20 | -0.04400 | -0.04235 | -0.04014 | +0.00386 |
| 9 | unloading | 16 | -0.04300 | -0.04170 | -0.03822 | +0.00478 |
| 10 | unloading | 12 | -0.04200 | -0.04133 | -0.03714 | +0.00486 |
| 11 | unloading | 8 | -0.04100 | -0.04108 | -0.03642 | +0.00458 |

The main newly exposed residual is unloading recovery: at stage 11, the raw/default model returns to −0.03642 mm while Table 2 remains at −0.04100 mm, an error of +0.00458 mm.

## Mesh-3 completeness

The even-numbered mesh-3 CSVs are snapshots rather than complete validation runs. Their partial scores must not be ranked against full-cycle results.

| Sample | Case | Current end / required end (s) | Progress by simulation time | Table 2 stages reached | Status |
|---|---|---:|---:|---:|---|
| SW-T1 | [`93_02`](SWT1/results_csv_hpc_rorqual/93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3_hpc.csv) | 70.5 / 3500 | 2.0% | **0/11** | Incomplete; no full score. |
| SW-T2 | [`93_04`](SWT2/results_csv_hpc_rorqual/93_04_swt2_final_theta30_resc9p71_ppfix_mesh3_hpc.csv) | 1773.75 / 2852.53 | 62.2% | **4/11** | Incomplete; no full score. |
| SW-T2 | [`92_05`](SWT2/results_csv_hpc_rorqual/92_05_swt2_final_theta30_resc9p71_mesh3_hpc.csv) | 2217 / 2852.53 | 77.7% | **5/11** | Incomplete; no full score. |
| SW-S3 | [`93_06`](SWS3/results_csv_hpc_rorqual/93_06_sw3_final_resc1p40_ppfix_mesh3_hpc.csv) | 1969.5 / 4803 | 41.0% | **4/11** | Incomplete; no full score. |
| SW-S4 | [`93_08`](SWS4/results_csv_hpc_rorqual/93_08_sw4_final_theta30_jrc5_ppfix_mesh3_hpc.csv) | 2020.5 / 3500 | 57.7% | **6/11** | Incomplete; no full score. |
| SW-S4 | [`92_06`](SWS4/results_csv_hpc_rorqual/92_06_sw4_final_theta30_jrc5_mesh3_hpc.csv) | 3124.5 / 3500 | 89.3% | **10/11** | Incomplete; no full score. |

The decks `92_07` (SW-T1 mesh 3) and `92_08` (SW-S3 mesh 3) exist, but no corresponding result CSV is present in the results directories.

All mesh-3 submission scripts disable checkpoints. If these CSVs are from jobs that stopped rather than jobs still running, they cannot be resumed from the current submissions and must be rerun.

## Preliminary common-stage mesh comparison

For a fair preliminary comparison, each mesh pair is evaluated only over stages reached by both meshes. These numbers diagnose early mesh sensitivity; they are not final convergence scores.

| Sample | Mesh-3 file | Common stages | Mesh-5 common-stage mean | Mesh-3 common-stage mean | Reading |
|---|---|---:|---:|---:|---|
| SW-T1 | `93_02` | 0 | — | — | No Table 2 stage reached; no evidence yet. |
| SW-T2 | `92_05` | 5 | 1.73% | 1.72% | Pre-event response is effectively mesh-insensitive; failure is not reached. |
| SW-S3 | `93_06` | 4 | 2.08% | 2.00% | Pre-event differences are very small; failure is not reached. |
| SW-S4 | `92_06` | 10 | 6.34% | 6.54% | Small +0.20-point mesh penalty; convergence is encouraging but stage 11 is missing. |

For SW-S4, the largest systematic mesh shift through unloading is about +0.0018 mm in shear slip. At the peak stage, mesh refinement slightly improves Q and both stresses but slightly worsens the two displacement channels. The dominant stage-4 missed-slip-burst error remains, supporting the conclusion that it is constitutive rather than a mesh artifact.

## Updated decision

1. Use `93_01`, `93_03`, `93_05`, and `93_07` as the clean mesh-5 reporting series.
2. Use **4.58%**, not 3.59%, as the defensible SW-S3 five-observable score when the output-only displacement fit is removed.
3. Do not recalibrate any constitutive parameter from the current mesh-3 snapshots.
4. Complete or rerun all four 93-series mesh-3 cases before declaring mesh convergence. SW-S4 is already encouraging, but the final unloading stage is still required.
5. Retain the SW-T1 caveat from the independent-verification addendum: its mesh-5/mesh-3 source separation differs by 3.1%, so that pair is not a pure discretization comparison.

## Signed Table 2 residuals for completed 93-series cases

All entries are model − Table 2. Units are Q in mL/min, stresses in MPa, and displacements in mm.

<details>
<summary><strong>Completed 93-series stage errors</strong></summary>

| Sample | Case | Stage | Branch | P_i | ΔQ | Δsigma′_n | Δtau | Δd_n | Δd_s |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | 93_01 | 1 | loading | 8 | -2.06e-04 | +0.260 | +0.422 | +0.00000 | +0.00000 |
| SW-T1 | 93_01 | 2 | loading | 12 | +0.0092 | +0.413 | +0.676 | -0.00001 | +0.00001 |
| SW-T1 | 93_01 | 3 | loading | 16 | +0.0036 | +0.547 | +0.902 | -0.00003 | -0.00099 |
| SW-T1 | 93_01 | 4 | loading | 20 | -0.0160 | +0.741 | +1.194 | +0.00094 | -0.00194 |
| SW-T1 | 93_01 | 5 | loading | 24 | -0.0541 | +0.927 | +1.481 | +0.00248 | -0.00647 |
| SW-T1 | 93_01 | 6 | loading | 28 | +0.4508 | +0.873 | +1.316 | -0.00163 | -0.00485 |
| SW-T1 | 93_01 | 7 | unloading | 24 | +0.7587 | +0.876 | +1.408 | -0.01248 | -0.01191 |
| SW-T1 | 93_01 | 8 | unloading | 20 | +0.8526 | +0.733 | +1.169 | -0.01664 | -0.00696 |
| SW-T1 | 93_01 | 9 | unloading | 16 | +0.7042 | +0.609 | +0.965 | -0.02021 | -0.00200 |
| SW-T1 | 93_01 | 10 | unloading | 12 | +0.4788 | +0.534 | +0.852 | -0.02266 | +0.00197 |
| SW-T1 | 93_01 | 11 | unloading | 8 | +0.2041 | +0.495 | +0.792 | -0.02569 | +0.00595 |
| SW-T2 | 93_03 | 1 | loading | 8 | -6.19e-04 | -0.596 | -1.009 | +0.00000 | +0.00000 |
| SW-T2 | 93_03 | 2 | loading | 12 | -0.0090 | -0.337 | -0.594 | +0.00099 | -0.00099 |
| SW-T2 | 93_03 | 3 | loading | 16 | -0.0301 | -0.124 | -0.211 | +0.00197 | -0.00298 |
| SW-T2 | 93_03 | 4 | loading | 20 | -0.1769 | +0.116 | +0.202 | +0.00295 | -0.00695 |
| SW-T2 | 93_03 | 5 | loading | 24 | -0.7756 | +0.350 | +0.610 | +0.00416 | -0.01188 |
| SW-T2 | 93_03 | 6 | loading | 28 | -1.9637 | +0.829 | +1.427 | -0.00109 | -0.00830 |
| SW-T2 | 93_03 | 7 | unloading | 24 | -0.2655 | +0.685 | +1.193 | +0.00356 | -0.00935 |
| SW-T2 | 93_03 | 8 | unloading | 20 | +0.0163 | +0.538 | +0.937 | +0.00327 | -0.00338 |
| SW-T2 | 93_03 | 9 | unloading | 16 | +0.0968 | +0.400 | +0.689 | +0.00489 | -0.00241 |
| SW-T2 | 93_03 | 10 | unloading | 12 | +0.0864 | +0.339 | +0.595 | -0.00012 | +0.00557 |
| SW-T2 | 93_03 | 11 | unloading | 8 | +0.0315 | +0.285 | +0.492 | -0.00248 | +0.01056 |
| SW-S3 | 93_05 | 1 | loading | 8 | -1.97e-04 | -0.514 | -0.969 | +0.00000 | +0.00000 |
| SW-S3 | 93_05 | 2 | loading | 12 | +0.0035 | -0.362 | -0.629 | -0.00028 | +0.00002 |
| SW-S3 | 93_05 | 3 | loading | 16 | +0.0113 | -0.250 | -0.301 | -0.00069 | +0.00005 |
| SW-S3 | 93_05 | 4 | loading | 20 | +0.0079 | +0.007 | +0.058 | -0.00125 | -0.00093 |
| SW-S3 | 93_05 | 5 | loading | 24 | +0.0400 | +0.244 | +0.462 | -0.00264 | -0.00024 |
| SW-S3 | 93_05 | 6 | loading | 28 | -0.0325 | +1.178 | +2.242 | -0.00380 | +0.00201 |
| SW-S3 | 93_05 | 7 | unloading | 24 | +0.0581 | +0.757 | +1.324 | +0.00086 | +0.00088 |
| SW-S3 | 93_05 | 8 | unloading | 20 | +0.0219 | +0.546 | +0.983 | +0.00386 | +0.00081 |
| SW-S3 | 93_05 | 9 | unloading | 16 | -0.0057 | +0.491 | +0.796 | +0.00478 | -0.00023 |
| SW-S3 | 93_05 | 10 | unloading | 12 | -0.0121 | +0.412 | +0.705 | +0.00486 | -0.00027 |
| SW-S3 | 93_05 | 11 | unloading | 8 | -0.0084 | +0.357 | +0.556 | +0.00458 | -0.00030 |
| SW-S4 | 93_07 | 1 | loading | 8 | +6.09e-05 | -0.155 | -0.214 | +0.00000 | +0.00000 |
| SW-S4 | 93_07 | 2 | loading | 12 | +7.69e-04 | -0.231 | -0.178 | -0.00035 | +0.00000 |
| SW-S4 | 93_07 | 3 | loading | 16 | -1.12e-05 | -0.027 | +0.242 | +0.00015 | +0.00001 |
| SW-S4 | 93_07 | 4 | loading | 20 | +8.70e-04 | +1.412 | +2.710 | +0.00469 | -0.01342 |
| SW-S4 | 93_07 | 5 | loading | 24 | -0.0033 | +0.554 | +1.060 | -0.00300 | +0.00633 |
| SW-S4 | 93_07 | 6 | loading | 28 | -0.0171 | +0.738 | +1.263 | -0.00166 | +0.00574 |
| SW-S4 | 93_07 | 7 | unloading | 24 | -8.94e-04 | +0.549 | +0.885 | -0.00073 | +0.00463 |
| SW-S4 | 93_07 | 8 | unloading | 20 | +0.0028 | +0.510 | +0.634 | +0.00029 | +0.00359 |
| SW-S4 | 93_07 | 9 | unloading | 16 | +8.11e-04 | +0.367 | +0.454 | +0.00011 | +0.00256 |
| SW-S4 | 93_07 | 10 | unloading | 12 | +8.62e-04 | +0.209 | +0.291 | +0.00030 | +0.00254 |
| SW-S4 | 93_07 | 11 | unloading | 8 | +3.17e-04 | +0.045 | +0.051 | +0.00010 | +0.00252 |

</details>
