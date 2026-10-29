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

### confirm (n = 300; calibrated 50, success_bias 50, prevalence_misspec 50, human_bias 50, mixed 50, shift 50)

| Policy | vs bayes_recal pooled [95% CI] | calibrated | success_bias | prevalence_misspec | human_bias | mixed | shift | vs nominal | vs v0.2 | W/T/L 1% vs bayes_recal | last-20 regret | severe p | human rate | retries/ep | s/stream |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| nominal | +0.73% [+0.04, +1.47] | -0.61% | +0.61% | -0.66% | +1.59% | +0.19% | +3.28% | +0.00% | +0.96% | 32/226/42 | 0.318 | 0.0162 | 0.359 | 0.257 | 0.04 |
| handoffx_v2 | -0.23% [-0.50, +0.00] | +0.12% | -0.45% | -0.25% | +0.02% | -0.01% | -0.78% | -0.65% | +0.00% | 12/281/7 | 0.204 | 0.0156 | 0.323 | 0.247 | 1.58 |
| bayes_recal | +0.00% [+0.00, +0.00] | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | +0.00% | -0.37% | +0.29% | 0/300/0 | 0.218 | 0.0158 | 0.309 | 0.252 | 0.66 |
| ts_recal | +0.89% [+0.45, +1.36] | +0.87% | +1.24% | +0.38% | +0.94% | -0.17% | +2.09% | +0.41% | +1.15% | 35/152/113 | 0.243 | 0.0161 | 0.349 | 0.246 | 0.56 |
| oracle | -2.58% [-3.17, -2.05] | -0.61% | -1.55% | -3.17% | -1.93% | -3.25% | -4.99% | -2.99% | -2.35% | 107/193/0 | 0.000 | 0.0132 | 0.376 | 0.209 | 0.04 |
| A_prev | -0.52% [-0.88, -0.19] | +0.19% | +0.03% | -1.52% | +0.60% | +0.07% | -2.48% | -0.90% | -0.26% | 39/243/18 | 0.145 | 0.0138 | 0.318 | 0.222 | 0.70 |
| B_humants | +0.53% [+0.16, +0.90] | +0.84% | +0.52% | +0.17% | +0.99% | +0.05% | +0.61% | +0.11% | +0.78% | 36/173/91 | 0.203 | 0.0151 | 0.355 | 0.240 | 1.72 |
| C_bfguard | -0.26% [-0.64, +0.09] | -0.58% | -0.04% | -0.77% | +0.84% | -0.39% | -0.61% | -0.76% | -0.03% | 30/240/30 | 0.177 | 0.0160 | 0.338 | 0.251 | 0.19 |
| ABC | -0.52% [-0.95, -0.11] | -0.55% | +0.05% | -1.74% | +1.15% | -0.61% | -1.39% | -1.02% | -0.28% | 46/216/38 | 0.130 | 0.0150 | 0.351 | 0.234 | 0.46 |
| A_static_diag | +0.74% [+0.05, +1.51] | -0.33% | +0.67% | -1.50% | +1.44% | -0.21% | +4.40% | +0.10% | +0.99% | 44/218/38 | 0.320 | 0.0157 | 0.337 | 0.238 | 0.65 |

Predictive diagnostics (end of stream): nominal: AI cal 0.074, human cal 0.074, prevalence TV 0.069, human obs 0.0, guarded eps 0.0; handoffx_v2: AI cal 0.057, human cal 0.059, prevalence TV 0.069, human obs 32.2, guarded eps 0.0; bayes_recal: AI cal 0.057, human cal 0.060, prevalence TV 0.069, human obs 30.8, guarded eps 0.0; ts_recal: AI cal 0.054, human cal 0.054, prevalence TV 0.069, human obs 34.9, guarded eps 0.0; A_prev: AI cal 0.057, human cal 0.057, prevalence TV 0.074, human obs 31.7, guarded eps 0.0; B_humants: AI cal 0.055, human cal 0.052, prevalence TV 0.069, human obs 35.5, guarded eps 0.0; C_bfguard: AI cal 0.056, human cal 0.056, prevalence TV 0.069, human obs 33.7, guarded eps 80.5; ABC: AI cal 0.053, human cal 0.053, prevalence TV 0.071, human obs 35.1, guarded eps 77.4; A_static_diag: AI cal 0.075, human cal 0.079, prevalence TV 0.087, human obs 0.0, guarded eps 0.0

