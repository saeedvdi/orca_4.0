# Ye and Ghassemi Table 2 stress-path comparison: Legacy_Prototype

This is a legacy-protocol prototype and must not be used as the final protocol-consistent comparison.

## Definitions

All errors are model minus Table 2. RMSE, MAE, and bias use all eleven ordered holds. nRMSE is $100\,\mathrm{RMSE}$ divided by the measured range of the relevant specimen and quantity.

The pre-failure and unloading path slopes are ordinary least-squares fits of $\tau=m\sigma_n'+b$ over their stated stages. The transition slope is a two-point secant from the last nominal pre-failure stage to the next loading stage. These are stress-path slopes, not friction coefficients.

The MC envelope slopes equal the stated friction coefficients. The BB peak envelope is nonlinear, so its reported slope is the analytical tangent $\mathrm{d}\tau/\mathrm{d}\sigma_n'$ evaluated at the Table 2 normal stress of the last nominal pre-failure stage. The BB post-weakening slope is $\tan\phi_r$.

## Accuracy summary

| sample | model | quantity | RMSE | MAE | bias_model_minus_Table2 | nRMSE_pct |
|---|---|---|---|---|---|---|
| SWT1 | BB | Effective normal stress | 0.4911 | 0.4088 | 0.3436 | 1.46 |
| SWT1 | BB | Shear stress | 0.7799 | 0.653 | 0.5465 | 2.0 |
| SWT1 | MC | Effective normal stress | 1.6243 | 1.4049 | 1.4049 | 4.82 |
| SWT1 | MC | Shear stress | 2.5911 | 2.2448 | 2.2448 | 6.66 |
| SWT2 | BB | Effective normal stress | 0.4763 | 0.4246 | 0.2324 | 1.27 |
| SWT2 | BB | Shear stress | 0.8233 | 0.735 | 0.4052 | 1.72 |
| SWT2 | MC | Effective normal stress | 1.2168 | 1.028 | 0.8357 | 3.26 |
| SWT2 | MC | Shear stress | 2.1076 | 1.78 | 1.4501 | 4.41 |
| SWS3 | BB | Effective normal stress | 0.5034 | 0.4241 | 0.2305 | 3.07 |
| SWS3 | BB | Shear stress | 0.9158 | 0.7568 | 0.4101 | 7.39 |
| SWS3 | MC | Effective normal stress | 0.5146 | 0.4348 | 0.2412 | 3.14 |
| SWS3 | MC | Shear stress | 0.9356 | 0.7762 | 0.4294 | 7.55 |
| SWS4 | BB | Effective normal stress | 0.5979 | 0.4264 | 0.3804 | 3.87 |
| SWS4 | BB | Shear stress | 1.0396 | 0.7314 | 0.6627 | 10.1 |
| SWS4 | MC | Effective normal stress | 0.6803 | 0.5483 | 0.5022 | 4.41 |
| SWS4 | MC | Shear stress | 1.1738 | 0.9426 | 0.8739 | 11.41 |

## Stress-path slopes

| sample | series | pre_failure_last_stage | pre_failure_slope | pre_failure_R2 | transition_secant_slope | unloading_slope | unloading_R2 |
|---|---|---|---|---|---|---|---|
| SWT1 | Table 2 | 5 | 0.0946 | 0.9822 | 1.47 | -0.0618 | 0.9949 |
| SWT1 | BB | 5 | -0.0376 | 0.9719 | 1.4739 | -0.2349 | 0.9572 |
| SWT1 | MC | 5 | -0.0421 | 0.9923 | 1.468 | -0.0589 | 0.9978 |
| SWT2 | Table 2 | 5 | 0.1607 | 0.986 | 1.6101 | -0.0248 | 0.8961 |
| SWT2 | BB | 5 | -0.0247 | 0.5384 | 1.6085 | -0.1186 | 0.9817 |
| SWT2 | MC | 5 | -0.0485 | 0.9989 | 1.6054 | -0.0601 | 0.9974 |
| SWS3 | Table 2 | 5 | 0.052 | 0.9968 | 1.3109 | -0.1209 | 0.9863 |
| SWS3 | BB | 5 | -0.1326 | 0.9947 | 1.2407 | -0.2229 | 0.9725 |
| SWS3 | MC | 5 | -0.1378 | 0.9892 | 1.2411 | -0.2232 | 0.9718 |
| SWS4 | Table 2 | 3 | 0.1003 | 0.8245 | 0.7688 | -0.0732 | 0.9112 |
| SWS4 | BB | 3 | -0.0116 | 0.9974 | 0.1267 | -0.1909 | 0.9822 |
| SWS4 | MC | 3 | -0.0117 | 0.9978 | 0.1689 | -0.1849 | 0.9834 |

## Strength-envelope slopes

| sample | reference_stage | reference_sigma_n_MPa | BB_peak_tangent_slope | BB_peak_equivalent_angle_deg | BB_post_weakening_slope | BB_post_weakening_angle_deg | MC_rough_slope | MC_rough_angle_deg | MC_smooth_slope | MC_smooth_angle_deg |
|---|---|---|---|---|---|---|---|---|---|---|
| SWT1 | 5 | 56.94 | 0.5536 | 28.968 | 0.5717 | 29.756 | 0.5093 | 26.9903 | 0.6403 | 32.6316 |
| SWT2 | 5 | 57.88 | 0.5528 | 28.9334 | 0.5717 | 29.756 | 0.5086 | 26.9568 | 0.6403 | 32.6316 |
| SWS3 | 5 | 23.42 | 0.5885 | 30.4778 | 0.1486 | 8.45 | 0.9523 | 43.6017 | 0.1664 | 9.4492 |
| SWS4 | 3 | 26.51 | 0.4509 | 24.2712 | 0.1139 | 6.5 | 0.9804 | 44.433 | 0.1139 | 6.498 |

## Complete stage-by-stage values

Stress values and signed errors are in MPa.

| sample | stage | branch | Pi_MPa | sigma_Table2 | sigma_BB | sigma_BB_error | sigma_MC | sigma_MC_error | tau_Table2 | tau_BB | tau_BB_error | tau_MC | tau_MC_error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SWT1 | 1 | loading | 8.0 | 65.47 | 65.676 | 0.206 | 65.676 | 0.206 | 67.16 | 67.495 | 0.335 | 67.495 | 0.335 |
| SWT1 | 2 | loading | 12.0 | 63.35 | 63.71 | 0.36 | 63.71 | 0.36 | 66.96 | 67.55 | 0.59 | 67.551 | 0.591 |
| SWT1 | 3 | loading | 16.0 | 61.27 | 61.764 | 0.494 | 61.765 | 0.495 | 66.82 | 67.637 | 0.817 | 67.637 | 0.817 |
| SWT1 | 4 | loading | 20.0 | 59.14 | 59.83 | 0.69 | 59.819 | 0.679 | 66.63 | 67.742 | 1.112 | 67.725 | 1.095 |
| SWT1 | 5 | loading | 24.0 | 56.94 | 57.846 | 0.906 | 57.878 | 0.938 | 66.32 | 67.767 | 1.447 | 67.818 | 1.498 |
| SWT1 | 6 | loading | 28.0 | 31.79 | 32.539 | 0.749 | 33.694 | 1.904 | 29.35 | 30.468 | 1.118 | 32.317 | 2.967 |
| SWT1 | 7 | unloading | 24.0 | 33.45 | 33.965 | 0.515 | 35.612 | 2.162 | 28.72 | 29.551 | 0.831 | 32.186 | 3.466 |
| SWT1 | 8 | unloading | 20.0 | 35.35 | 35.569 | 0.219 | 37.532 | 2.182 | 28.57 | 28.916 | 0.346 | 32.058 | 3.488 |
| SWT1 | 9 | unloading | 16.0 | 37.29 | 37.287 | -0.003 | 39.459 | 2.169 | 28.48 | 28.466 | -0.014 | 31.941 | 3.461 |
| SWT1 | 10 | unloading | 12.0 | 39.22 | 39.081 | -0.139 | 41.391 | 2.171 | 28.36 | 28.135 | -0.225 | 31.832 | 3.472 |
| SWT1 | 11 | unloading | 8.0 | 41.14 | 40.923 | -0.217 | 43.328 | 2.188 | 28.23 | 27.883 | -0.347 | 31.731 | 3.501 |
| SWT2 | 1 | loading | 8.0 | 66.74 | 66.144 | -0.596 | 66.144 | -0.596 | 74.87 | 73.861 | -1.009 | 73.861 | -1.009 |
| SWT2 | 2 | loading | 12.0 | 64.53 | 64.193 | -0.337 | 64.193 | -0.337 | 74.54 | 73.946 | -0.594 | 73.946 | -0.594 |
| SWT2 | 3 | loading | 16.0 | 62.37 | 62.246 | -0.124 | 62.246 | -0.124 | 74.25 | 74.039 | -0.211 | 74.039 | -0.211 |
| SWT2 | 4 | loading | 20.0 | 60.19 | 60.306 | 0.116 | 60.303 | 0.113 | 73.94 | 74.142 | 0.202 | 74.138 | 0.198 |
| SWT2 | 5 | loading | 24.0 | 57.88 | 58.229 | 0.349 | 58.361 | 0.481 | 73.4 | 74.009 | 0.609 | 74.237 | 0.837 |
| SWT2 | 6 | loading | 28.0 | 29.36 | 30.2 | 0.84 | 31.006 | 1.646 | 27.48 | 28.925 | 1.445 | 30.321 | 2.841 |
| SWT2 | 7 | unloading | 24.0 | 31.26 | 31.956 | 0.696 | 32.942 | 1.682 | 27.29 | 28.503 | 1.213 | 30.211 | 2.921 |
| SWT2 | 8 | unloading | 20.0 | 33.23 | 33.78 | 0.55 | 34.876 | 1.646 | 27.24 | 28.197 | 0.957 | 30.096 | 2.856 |
| SWT2 | 9 | unloading | 16.0 | 35.23 | 35.643 | 0.413 | 36.812 | 1.582 | 27.25 | 27.96 | 0.71 | 29.985 | 2.735 |
| SWT2 | 10 | unloading | 12.0 | 37.18 | 37.532 | 0.352 | 38.751 | 1.571 | 27.15 | 27.768 | 0.618 | 29.879 | 2.729 |
| SWT2 | 11 | unloading | 8.0 | 39.14 | 39.438 | 0.298 | 40.669 | 1.529 | 27.09 | 27.606 | 0.516 | 29.738 | 2.648 |
| SWS3 | 1 | loading | 8.0 | 31.65 | 31.136 | -0.514 | 31.136 | -0.514 | 14.7 | 13.731 | -0.969 | 13.731 | -0.969 |
| SWS3 | 2 | loading | 12.0 | 29.58 | 29.218 | -0.362 | 29.218 | -0.362 | 14.57 | 13.941 | -0.629 | 13.941 | -0.629 |
| SWS3 | 3 | loading | 16.0 | 27.53 | 27.341 | -0.189 | 27.341 | -0.189 | 14.48 | 14.171 | -0.309 | 14.171 | -0.309 |
| SWS3 | 4 | loading | 20.0 | 25.48 | 25.487 | 0.007 | 25.487 | 0.007 | 14.38 | 14.438 | 0.058 | 14.438 | 0.058 |
| SWS3 | 5 | loading | 24.0 | 23.42 | 23.664 | 0.244 | 23.689 | 0.269 | 14.26 | 14.722 | 0.462 | 14.768 | 0.508 |
| SWS3 | 6 | loading | 28.0 | 15.25 | 16.342 | 1.092 | 16.362 | 1.112 | 3.55 | 5.638 | 2.088 | 5.674 | 2.124 |
| SWS3 | 7 | unloading | 24.0 | 17.27 | 17.954 | 0.684 | 17.97 | 0.7 | 3.19 | 4.382 | 1.192 | 4.41 | 1.22 |
| SWS3 | 8 | unloading | 20.0 | 19.14 | 19.621 | 0.481 | 19.635 | 0.495 | 2.95 | 3.816 | 0.866 | 3.841 | 0.891 |
| SWS3 | 9 | unloading | 16.0 | 21.01 | 21.442 | 0.432 | 21.456 | 0.446 | 2.68 | 3.369 | 0.689 | 3.394 | 0.714 |
| SWS3 | 10 | unloading | 12.0 | 22.86 | 23.216 | 0.356 | 23.231 | 0.371 | 2.44 | 3.044 | 0.604 | 3.07 | 0.63 |
| SWS3 | 11 | unloading | 8.0 | 24.79 | 25.094 | 0.304 | 25.108 | 0.318 | 2.31 | 2.77 | 0.46 | 2.796 | 0.486 |
| SWS4 | 1 | loading | 8.0 | 30.75 | 30.595 | -0.155 | 30.594 | -0.156 | 12.56 | 12.346 | -0.214 | 12.346 | -0.214 |
| SWS4 | 2 | loading | 12.0 | 28.73 | 28.632 | -0.098 | 28.632 | -0.098 | 12.53 | 12.366 | -0.164 | 12.367 | -0.163 |
| SWS4 | 3 | loading | 16.0 | 26.51 | 26.624 | 0.114 | 26.624 | 0.114 | 12.14 | 12.392 | 0.252 | 12.392 | 0.252 |
| SWS4 | 4 | loading | 20.0 | 22.92 | 24.489 | 1.569 | 24.432 | 1.512 | 9.38 | 12.121 | 2.741 | 12.022 | 2.642 |
| SWS4 | 5 | loading | 24.0 | 19.25 | 19.804 | 0.554 | 19.699 | 0.449 | 6.48 | 7.54 | 1.06 | 7.359 | 0.879 |
| SWS4 | 6 | loading | 28.0 | 15.31 | 16.048 | 0.738 | 16.27 | 0.96 | 3.12 | 4.383 | 1.263 | 4.767 | 1.647 |
| SWS4 | 7 | unloading | 24.0 | 17.13 | 17.679 | 0.549 | 17.92 | 0.79 | 2.82 | 3.705 | 0.885 | 4.126 | 1.306 |
| SWS4 | 8 | unloading | 20.0 | 19.0 | 19.388 | 0.388 | 19.64 | 0.64 | 2.59 | 3.245 | 0.655 | 3.681 | 1.091 |
| SWS4 | 9 | unloading | 16.0 | 20.89 | 21.16 | 0.27 | 21.419 | 0.529 | 2.41 | 2.879 | 0.469 | 3.327 | 0.917 |
| SWS4 | 10 | unloading | 12.0 | 22.82 | 23.029 | 0.209 | 23.293 | 0.473 | 2.28 | 2.571 | 0.291 | 3.026 | 0.746 |
| SWS4 | 11 | unloading | 8.0 | 24.81 | 24.855 | 0.045 | 25.12 | 0.31 | 2.27 | 2.321 | 0.051 | 2.781 | 0.511 |
