# Evaluation Results

## Experiment: BadNets on CIFAR-10 (PreActResNet18)

**Date:** 2026-09-14
**Evaluated by:** Nguyen Minh Chinh

---

## 1. Infected Model

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Clean Accuracy (CA) | 89.41% | - | - |
| Attack Success Rate (ASR) | 97.43% | >= 80% | PASS |

- Trigger: 3x3 white patch at bottom-right (pixels [29:32, 29:32, :] = 255)
- Target class: 0
- Eval script: scripts/eval_baseline.py

---

## 2. Repaired Model

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Clean Accuracy (CA) | 93.35% | - | - |
| Attack Success Rate (ASR) | 0.90% (81/9000) | <= 10% | PASS |

- Repair: Clean fine-tuning, 20 epochs, SGD lr=0.01, CosineAnnealingLR T_max=20, seed=42
- Platform: Kaggle T4 GPU (2026-09-14)
- Eval script: scripts/eval_repaired.py

---

## 3. Single-Shard Substitution (Day-5 Kill Gate)

| Shard swapped | Recovered ASR | Target | Status |
|---------------|--------------|--------|--------|
| Best single shard | 17.46% | >= 50% | FAIL |

- Method: Replace one layer group in repaired model with infected model weights
- Evaluated by: Dan
- See: notes/2026-09-18_chinh.md for discussion
