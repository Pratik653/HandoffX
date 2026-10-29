# Complete exact-loss table

Values are artificial loss units. Every row is a deliberately chosen synthetic environment; rows are not a sample of real deployments.

| Scenario | Bayes | Nominal | Robust | Oracle |
|---|---:|---:|---:|---:|
| ai_under__human_under | 7.514800 | 9.308331 | 12.000000 | 7.514800 |
| ai_under__human_calibrated | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| ai_under__human_over | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| ai_calibrated__human_under | 9.373126 | 9.307833 | 9.394822 | 7.514800 |
| ai_calibrated__human_calibrated | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| ai_calibrated__human_over | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| ai_over__human_under | 9.390831 | 9.394822 | 9.394822 | 7.514800 |
| ai_over__human_calibrated | 7.514800 | 7.514800 | 9.394822 | 7.514800 |
| ai_over__human_over | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| low_hazard__ai_under__human_under | 6.386974 | 6.371399 | 6.591485 | 5.975053 |
| low_hazard__ai_under__human_calibrated | 6.058354 | 6.023292 | 6.516528 | 5.975053 |
| low_hazard__ai_under__human_over | 7.318960 | 7.318960 | 7.318960 | 5.975053 |
| low_hazard__ai_calibrated__human_under | 6.295072 | 6.289329 | 6.416550 | 5.975053 |
| low_hazard__ai_calibrated__human_calibrated | 5.975357 | 5.975053 | 6.416550 | 5.975053 |
| low_hazard__ai_calibrated__human_over | 6.032232 | 6.180854 | 7.318960 | 5.975053 |
| low_hazard__ai_over__human_under | 6.307131 | 6.327034 | 6.310483 | 5.975053 |
| low_hazard__ai_over__human_calibrated | 6.279943 | 6.302932 | 6.310483 | 5.975053 |
| low_hazard__ai_over__human_over | 5.989880 | 6.034171 | 6.063619 | 5.975053 |
| persistent_low | 5.680485 | 5.680485 | 6.083607 | 5.680485 |
| persistent_high | 9.431800 | 9.431800 | 12.000000 | 9.431800 |
| independent_modes | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| human_delay_3 | 7.664800 | 7.664800 | 7.664800 | 7.664800 |
| human_available_late | 9.282354 | 9.281856 | 9.394822 | 9.281856 |
| human_unavailable | 9.373126 | 9.368707 | 9.394822 | 9.368707 |
| high_consequence | 7.820800 | 7.820800 | 7.820800 | 7.820800 |
| low_consequence | 4.000000 | 4.000000 | 4.000000 | 4.000000 |
| limited_budget | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| short_deadline | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| uninformative_diagnostic | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| weak_human | 9.373126 | 9.368707 | 9.394822 | 9.368707 |
| expensive_human | 9.373126 | 9.368707 | 9.394822 | 9.368707 |
| cheap_human | 4.514800 | 4.514800 | 4.514800 | 4.514800 |
| shift_unrecalibrated | 13.194520 | 13.194520 | 13.194520 | 12.000000 |
| shift_perfect_recalibration | 12.000000 | 12.000000 | 12.000000 | 12.000000 |
| irreversible_guard | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| conditional_risk_guard | 7.514800 | 7.514800 | 7.514800 | 7.514800 |
| joint_prior_predictive | 7.902880 | 7.902880 | 7.902880 | 7.902880 |
| opposite_coupling | 7.902880 | 7.902880 | 7.902880 | 7.902880 |
