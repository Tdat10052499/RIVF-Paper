# Results Summary

## BadNets on CIFAR-10 — PreActResNet18

| Model | Clean Accuracy (CA) | Attack Success Rate (ASR) | Gate Target | Status |
|---|---|---|---|---|
| Infected | 89.41% | 97.43% | ASR >= 80% | PASS |
| Repaired (clean fine-tuning) | 93.35% | 0.90% | ASR <= 10% | PASS |
| Single-shard substitution (best) | — | 17.46% | ASR >= 50% | FAIL |

**Day-5 Kill Gate overall: FAIL** (condition 3 not met)

Evaluated: 2026-09-14 to 2026-09-18
Evaluated by: Nguyen Minh Chinh, Dan
