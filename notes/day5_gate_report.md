# Day-5 Kill Gate Report

**Author:** Duong Ngoc Linh Dan  
**Pilot run date:** 16 Sep 2026  
**Status:** ❌ GATE NOT PASSED

---

## 1. What is the Day-5 Kill Gate?

Before proceeding to the full experiment, the team must demonstrate **all 6 conditions** below. If any condition fails, work stops until the underlying issue is resolved.

| # | Condition | Threshold | Status |
|---|---|---|---|
| 1 | Infected model ASR | ≥ 80% | ✅ PASS |
| 2 | Repaired model ASR | ≤ 10% | ❓ Missing — Chinh must run `eval_repaired.py` |
| 3 | Single-shard rollback raises ASR | ≥ 50%, or +30 pp above repaired baseline | ❌ FAIL |
| 4 | Clean accuracy drop after rollback | ≤ 2 pp | ❓ Not yet measured |
| 5 | Rolled-back shard does NOT contain the entire repair update | — | ❓ Not yet verified |
| 6 | Results reproducible across ≥ 2 seeds | — | ❓ Only seed=42 so far |

**Immediate blocker:** Condition #3 failed. No single-shard substitution brings ASR above 17.46%, far below the 50% threshold. See Section 4 for full results.

---

## 2. Background: what are we testing and why?

Our research question is: *if an adversary replaces one contiguous layer group (a "shard") of a repaired model with the corresponding shard from the original infected model, can they recover the backdoor?*

This models a realistic deployment risk called **shard-version skew** — a scenario where a system assembles a model from components sourced at different times, and one stale or infected shard slips past the repair pipeline.

To interpret our results correctly, we need three baseline numbers:

- **Infected model ASR** — confirms the backdoor is strong to begin with. If low, there is nothing to recover.
- **Repaired model ASR** — confirms the backdoor was actually removed. If still high, the repaired model is not a valid baseline and results are uninterpretable.
- **Repaired model CA** — confirms repair did not destroy normal model performance (reference only; does not affect our experiment directly).

---

## 3. Baseline results (run by Chinh — 14 Sep 2026)

| Metric | Value | Threshold | Result |
|---|---|---|---|
| Infected model ASR | **97.43%** (8769 / 9000) | ≥ 80% | ✅ PASS |
| Repaired model CA | **93.35%** | — | ✅ (reference) |
| Repaired model ASR | **[missing — Chinh must run `eval_repaired.py`]** | ≤ 10% | ❓ Unconfirmed |

> **Action required (Chinh):** Run `eval_repaired.py` and fill in the repaired model ASR. This is Gate Condition #2. Without this number we cannot fully interpret the substitution results — if repaired ASR is still high (e.g. 40%), the baseline is invalid and the experiment must be re-run with a properly repaired model.

**Checkpoints used:**
- Infected: `resnet18_cifar10_badnets_infected.pt` — PreActResNet18, CIFAR-10, BadNets, poison_rate=0.1
- Repaired: `resnet18_cifar10_badnets_repaired.pt`
- Repair method: **[unknown — Chinh must confirm: fine-pruning / NAD / ANP? How many epochs? Learning rate?]**

---

## 4. Substitution pilot results (run by Dan — 16 Sep 2026)

**Setup:** For each configuration, one shard of the repaired model's state dict is replaced with the corresponding shard from the infected model. The resulting hybrid model is evaluated on the full bd_test set (9,000 images). Script: `scripts/run_substitution.py`, seed=42, CPU only, torch 2.14.0+cpu.

### 4a. n_shards = 3 (each shard = 2 layer groups)

| Shard | Layer groups | Keys | ASR after swap | Threshold | Result |
|---|---|---|---|---|---|
| 0 | conv1 + layer1 | 25 | **1.24%** (112 / 9000) | ≥ 50% | ❌ FAIL |
| 1 | layer2 + layer3 | 50 | **6.56%** (590 / 9000) | ≥ 50% | ❌ FAIL |
| 2 | layer4 + linear | 27 | **17.46%** (1571 / 9000) | ≥ 50% | ❌ FAIL |

### 4b. n_shards = 6 (each shard = 1 layer group, finer granularity)

| Shard | Layer group | ASR after swap | Threshold | Result |
|---|---|---|---|---|
| 0 | conv1 | **1.02%** (92 / 9000) | ≥ 50% | ❌ FAIL |
| 1 | layer1 | **1.29%** (116 / 9000) | ≥ 50% | ❌ FAIL |
| 2 | layer2 | **8.94%** (805 / 9000) | ≥ 50% | ❌ FAIL |
| 3 | layer3 | **0.50%** (45 / 9000) | ≥ 50% | ❌ FAIL |
| 4 | layer4 | **8.08%** (727 / 9000) | ≥ 50% | ❌ FAIL |
| 5 | linear | **1.18%** (106 / 9000) | ≥ 50% | ❌ FAIL |

**Summary:** No single shard substitution recovers the backdoor to the gate threshold. The highest ASR observed was 17.46% (n=3, shard 2: layer4+linear) and 8.94% (n=6, shard 2: layer2). Both are far below the 50% requirement.

---

## 5. Per-layer interpretation (n_shards = 6)

Backdoor information is not distributed uniformly across a model. It tends to concentrate in layers that learn complex, composite features — typically the middle layers. Swapping a layer that encodes backdoor information should cause a sharp ASR increase; swapping an unrelated layer should leave ASR near the repaired model's baseline.

**Shard 0 — conv1 — ASR 1.02%**  
conv1 learns basic low-level features (edges, colors). A BadNets trigger (a small pixel patch in the corner) is a mid-level pattern that would not be encoded this early. Near-zero ASR confirms conv1 carries no meaningful backdoor information.

**Shard 1 — layer1 — ASR 1.29%**  
layer1 learns simple geometric patterns, one step above conv1. Still too early in the feature hierarchy for backdoor encoding. ASR is negligible.

**Shard 2 — layer2 — ASR 8.94% (highest across n=6)**  
layer2 begins learning more complex compositional features. The highest single-layer ASR suggests layer2 may partially encode the backdoor — but 8.94% is still far from 50%, meaning even the most suspicious shard alone cannot restore the attack.

**Shard 3 — layer3 — ASR 0.50% (anomalously low)**  
Lower than all other shards and lower than expected. One interpretation: layer3 in the infected model encodes clean-class features that, when swapped into the repaired model, actively suppress the backdoor signal from surrounding layers rather than restoring it.

**Shard 4 — layer4 — ASR 8.08%**  
layer4 is the last convolutional block before the classifier and learns high-level semantic features. ASR is comparable to layer2, suggesting some partial backdoor encoding, but insufficient on its own.

**Shard 5 — linear — ASR 1.18%**  
The classifier head maps the backbone's features to class logits. The backdoor decision is made in the earlier layers; the linear layer simply reads out whatever the backbone produces. Near-zero ASR is expected.

---

## 6. Why did the gate fail? Three hypotheses

### Hypothesis A — Repair was too aggressive (most likely)

If Chinh used fine-tuning over many epochs, the entire model was effectively retrained, not just the backdoor-affected weights. The infected shards become incompatible with the repaired model's weight distribution — swapping one back in is like installing a part from an old machine into one that has been completely redesigned. The infected shard no longer "speaks the same language" as the surrounding repaired layers.

→ **To investigate:** Chinh must confirm the repair method and number of epochs. A lightweight repair (e.g. ANP with few steps) would likely leave the model more vulnerable to shard rollback.

### Hypothesis B — Backdoor is distributed across multiple shards

The backdoor may not be localized to a single layer group. If it is spread across two or more layers (e.g. layer2 and layer4 jointly encode trigger features), swapping either one alone is insufficient — both must be rolled back simultaneously for ASR to recover.

→ **To investigate:** Test multi-shard substitution — swap shards 2 and 4 together (layer2 + layer4) and measure ASR. If ASR jumps significantly, the paper's framing shifts from "single-shard skew" to "multi-shard skew," which is still a valid and publishable contribution.

### Hypothesis C — Hypothesis is falsified

Modern repair methods may be robust enough that shard-level rollback cannot recover the backdoor regardless of which shards are swapped. This is a scientifically valid negative result. The paper could pivot to explaining *why* modern repair is robust to shard skew and under what conditions (repair method, training epochs, model architecture) a shard-skew attack could succeed.

→ **This direction requires supervisor input before the team commits to it.**

---

## 7. Open questions before reporting to supervisor

**Chinh must answer:**
- [ ] What repair method was used? (fine-pruning / NAD / ANP / other)
- [ ] How many epochs? What learning rate and optimizer?
- [ ] What is the repaired model's ASR? (run `eval_repaired.py` and fill in Section 3)
- [ ] Was the repair config saved? If so, push it to `configs/` so the team can reproduce it.

**Team to discuss:**
- [ ] Should we run multi-shard substitution to test Hypothesis B? Dan can extend `substitute()` in `src/partition/shard.py` to accept a list of shard indices.
- [ ] Which hypothesis do we lead with when we meet the supervisor?
- [ ] After getting the repaired model ASR, run a second seed (e.g. seed=1234) to satisfy Gate Condition #6.

---

## 8. Raw data and code

Result files:
- `results/raw/substitution/shard0.json` — shard 0, n=3
- `results/raw/substitution/shard1.json` — shard 1, n=3
- `results/raw/substitution/shard2.json` — shard 2, n=3
- `results/raw/substitution/n6/shard0.json` through `shard5.json` — n=6

Key files added this cycle:
- `src/partition/shard.py` — `get_layer_prefixes()`, `partition()`, `substitute()`
- `src/models/preact_resnet.py` — model definition (from BackdoorBench)
- `scripts/run_substitution.py` — substitution + ASR measurement
- `scripts/eval_repaired.py` — repaired model evaluation (Chinh's script; run this to fill Gate Condition #2)

**Run environment:** seed=42, CPU only, PyTorch 2.14.0+cpu, torchvision 0.29.0+cpu, Windows 11
