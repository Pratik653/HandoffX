### pilot (n = 72; calibrated 12, success_bias 12, prevalence_misspec 12, human_bias 12, mixed 12, shift 12)

| Policy | vs bayes_recal pooled [95% CI] | calibrated | success_bias | prevalence_misspec | human_bias | mixed | shift | vs nominal | vs v0.2 | W/T/L 1% vs bayes_recal | last-20 regret | severe p | human rate | retries/ep | s/stream |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nominal | +1.21% [-0.65, +3.42] | -2.28% | +1.04% | -2.06% | +3.93% | +0.03% | +6.64% | +0.00% | +1.51% | 8/56/8 | 0.270 | 0.0142 | 0.359 | 0.232 | 0.06 |
| handoffx_v2 | -0.29% [-1.30, +0.53] | +0.00% | +0.00% | -1.82% | +1.25% | -1.59% | +0.42% | -0.97% | +0.00% | 2/66/4 | 0.152 | 0.0159 | 0.275 | 0.234 | 2.30 |
| bayes_recal | +0.00% [+0.00, +0.00] | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | -0.51% | +0.49% | 0/72/0 | 0.212 | 0.0159 | 0.284 | 0.229 | 0.86 |
| ts_recal | +0.16% [-0.87, +1.10] | -0.23% | +0.46% | -0.74% | +0.38% | -0.46% | +1.53% | -0.56% | +0.52% | 6/44/22 | 0.143 | 0.0152 | 0.327 | 0.230 | 0.76 |
| oracle | -2.45% [-3.80, -1.30] | -2.28% | -1.82% | -2.39% | -1.06% | -2.63% | -4.53% | -3.06% | -2.14% | 22/50/0 | 0.000 | 0.0126 | 0.329 | 0.187 | 0.06 |
| A_prev | -0.92% [-1.97, -0.07] | -1.01% | +0.01% | -1.60% | +0.09% | +0.20% | -3.21% | -1.57% | -0.52% | 11/56/5 | 0.117 | 0.0132 | 0.298 | 0.195 | 0.96 |
| B_humants | +0.08% [-0.92, +1.05] | -0.53% | -0.41% | -0.61% | +2.24% | -0.77% | +0.54% | -0.64% | +0.42% | 5/51/16 | 0.154 | 0.0150 | 0.331 | 0.227 | 2.44 |
| C_bfguard | +0.41% [-0.73, +1.84] | -2.04% | +0.05% | -0.18% | +3.06% | -0.03% | +1.58% | -0.45% | +0.81% | 7/61/4 | 0.204 | 0.0155 | 0.324 | 0.225 | 0.26 |

Predictive diagnostics (end of stream): nominal: AI cal 0.062, human cal 0.072, prevalence TV 0.063, human obs 0.0, guarded eps 0.0; handoffx_v2: AI cal 0.046, human cal 0.064, prevalence TV 0.063, human obs 27.6, guarded eps 0.0; bayes_recal: AI cal 0.047, human cal 0.063, prevalence TV 0.063, human obs 28.6, guarded eps 0.0; ts_recal: AI cal 0.046, human cal 0.057, prevalence TV 0.063, human obs 32.7, guarded eps 0.0; A_prev: AI cal 0.051, human cal 0.059, prevalence TV 0.073, human obs 30.0, guarded eps 0.0; B_humants: AI cal 0.047, human cal 0.054, prevalence TV 0.063, human obs 33.3, guarded eps 0.0; C_bfguard: AI cal 0.045, human cal 0.061, prevalence TV 0.063, human obs 32.4, guarded eps 78.0

