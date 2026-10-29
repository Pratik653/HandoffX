# Verified findings and status

| Finding | Status | Evidence |
|---|---|---|
| General handoff formulation is established theory | Prior-art mapping; no novelty claim | Active primary sources and literature matrix |
| Static threshold, sensitivity, retry mixture and finite-model bounds | Written conditional derivations | P1-P9; computational checks supplement proofs |
| No universal human-superiority or threshold rule | Constructed counterexamples | CE1-CE8 |
| Joint Bayes is not uniformly superior to nominal planning | Executed synthetic result | Six lower, 23 equal, nine higher exact-loss cases |
| Selected parameter coupling is not generally useful | Executed synthetic negative result | One lower, 31 equal, six higher versus independent offsets |
| Persistent mode representation matters in tested cases | Executed synthetic result | 15 lower, 23 equal versus iid-mode ablation |
| Robust bounds require model coverage | Conditional proof and executed failure outside set | 10.7548 bound versus 13.19452 true shifted loss |
| Library runs without LLM/API/GPU | Executed software fact | CLI/examples/tests/wheel logs |
| Real-world intervention benefit | Not established | No real-agent/human evaluation performed |
| Windows execution | Not performed | Linux runtime metadata only |
