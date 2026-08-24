# Controlled conflict-resolution audit summary

## Purpose

This audit is a behavioral check of RIEC-L1 as a pre-specified conflict-resolution operation. It is not a fourth empirical benchmark and it is not evidence of universal predictive superiority.

## Design

- Replicates per alpha/noise setting: `0`
- Alpha grid: `0,0.05,0.1,0.15,0.2,0.25,0.5,1,2`
- Noise-scale grid: `0.5,1.0,1.5`
- Base seed: `20260512`
- n_eff: `72`
- lambda_n: `0.233827`
- empirical Page residual SD: `0.0548291`

## Real drying Page-vs-Midilli conflict margin

- `best_compact_model`: `page_2p`
- `best_flexible_model`: `two_term_3p`
- `best_compact_bic`: `-410.538`
- `best_flexible_bic`: `-409.701`
- `best_compact_cv_risk`: `0.0041453`
- `best_flexible_cv_risk`: `0.00401111`
- `bic_gap_flexible_minus_compact`: `0.836376`
- `log_cv_gain_flexible_over_compact`: `0.0329078`
- `lambda_times_log_cv_gain`: `0.00769472`
- `riec_conflict_margin`: `0.828681`
- `margin_rule_selected_side`: `compact`

Interpretation: a positive RIEC conflict margin keeps the compact side; a negative margin crosses to the flexible side.

## Deterministic alpha scan

 alpha    bic_best     cv_best   riec_best bic_side  cv_side riec_side best_compact_model best_flexible_model  best_compact_bic  best_flexible_bic  best_compact_cv_risk  best_flexible_cv_risk  bic_gap_flexible_minus_compact  log_cv_gain_flexible_over_compact  lambda_times_log_cv_gain  riec_conflict_margin margin_rule_selected_side
  0.00  weibull_2p  midilli_4p     page_2p  compact flexible   compact            page_2p         two_term_3p       -410.537565        -409.701189              0.004145               0.004011                        0.836376                           0.032908                  0.007695              0.828681                   compact
  0.05  weibull_2p  midilli_4p     page_2p  compact flexible   compact            page_2p         two_term_3p       -410.144224        -409.734200              0.004162               0.004009                        0.410025                           0.037360                  0.008736              0.401289                   compact
  0.10 two_term_3p  midilli_4p two_term_3p flexible flexible  flexible            page_2p         two_term_3p       -409.733943        -409.768463              0.004179               0.004007                       -0.034520                           0.041991                  0.009819             -0.044338                  flexible
  0.15 two_term_3p  midilli_4p two_term_3p flexible flexible  flexible            page_2p         two_term_3p       -409.307021        -409.803633              0.004196               0.004005                       -0.496612                           0.046796                  0.010942             -0.507554                  flexible
  0.20 two_term_3p  midilli_4p two_term_3p flexible flexible  flexible            page_2p         two_term_3p       -408.863766        -409.839368              0.004215               0.004002                       -0.975601                           0.051771                  0.012105             -0.987707                  flexible
  0.25 two_term_3p two_term_3p two_term_3p flexible flexible  flexible            page_2p         two_term_3p       -408.404495        -409.875327              0.004235               0.004000                       -1.470833                           0.056908                  0.013307             -1.484139                  flexible
  0.50 two_term_3p two_term_3p two_term_3p flexible flexible  flexible            page_2p         two_term_3p       -405.879346        -410.040972              0.004344               0.003981                       -4.161626                           0.087254                  0.020402             -4.182028                  flexible
  1.00 two_term_3p  midilli_4p two_term_3p flexible flexible  flexible         weibull_2p         two_term_3p       -399.822533        -409.296516              0.004622               0.004006                       -9.473983                           0.142966                  0.033429             -9.507412                  flexible
  2.00  midilli_4p  midilli_4p  midilli_4p flexible flexible  flexible            page_2p          midilli_4p       -384.881041        -405.985829              0.005416               0.003994                      -21.104788                           0.304694                  0.071246            -21.176033                  flexible

## Stochastic compact summary table

No stochastic replicates were requested. Re-run with `--replicates N` to generate selection-frequency tables.
