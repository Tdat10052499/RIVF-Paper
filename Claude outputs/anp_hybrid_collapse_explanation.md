# ANP Hybrid Collapse — Results, Explanation, and Paper Framing

**Date:** 23/09/2026  
**Author:** Dan  
**For:** Chinh — read before writing Section 5.4

---

## 1. Experiment Background

The experiment tests whether a backdoor can be **rolled back** after the model has been defended. Concretely: the defended model is partitioned into k shards (layer-wise segments), some of which are replaced with the corresponding shards from the original infected model. The resulting mixed model is called a **hybrid model**. The parameter k is the number of replaced shards — the larger k is, the more infected weights are reintroduced.

Two defenses are compared:

- **Fine-tune** — global repair: all weights are fine-tuned on clean data, leaving no sparse structure.
- **ANP** (Adversarial Neuron Pruning) — local repair: a targeted subset of neurons is pruned (zeroed out) via adversarial perturbation. The pruning mask is baked directly into the weight tensors at checkpoint time (no runtime hooks).

---

## 2. Fine-tune Hybrid Results

| k (shards replaced) | CA (Clean Accuracy) | ASR (Attack Success Rate) |
|---------------------|---------------------|---------------------------|
| k=1                 | ~78%                | ~45%                      |
| k=2                 | ~85%                | ~71%                      |
| k=3                 | ~91%                | ~94%                      |

**Interpretation:** High CA confirms the model remains functional. ASR increases monotonically with k, reflecting genuine backdoor recovery as more infected weights are reintroduced. This is the attacker-wins scenario — a straightforward and interpretable result.

---

## 3. ANP Hybrid Results

| k (shards replaced) | CA (Clean Accuracy) | ASR (Attack Success Rate) |
|---------------------|---------------------|---------------------------|
| k=1                 | ~10%                | ~81%                      |
| k=2                 | ~10%                | ~99%                      |

**Important:** This is **not** backdoor recovery. The model has undergone **utility collapse** — it has lost all meaningful classification ability. The high ASR here is a measurement artifact, not evidence of a functioning backdoor. See the explanation below.

---

## 4. Why CA = ~10%?

CIFAR-10 has 10 classes. CA = 10% is the random-chance baseline — the model is effectively guessing.

**Mechanism:** ANP bakes its pruning mask into the weight tensors: pruned neurons are zeroed out in the checkpoint. The entire ANP model co-adapts to this sparse structure — the remaining layers learn to route signal through exactly the non-zeroed neurons.

When `substitute()` splices a shard from the infected model (full weights, no zeros) alongside the remaining ANP shards (which still carry the baked-in zeros), the signal flow between the two parts becomes incompatible. The model produces incoherent activations and collapses to predicting **a single class for every input** — typically class 0 (airplane), which is the target class for BadNets.

CA = ~10% because the model is only correct on genuine airplane images (class 0) and wrong on all other nine classes.

> This is not a bug in the harness. `substitute()` was verified correct via k=6 (full rollback yields ASR=97.43%, CA=89.41%). This collapse is what actually happens when shard substitution is applied to an ANP-defended model.

---

## 5. Why ASR = ~99% Even Though the Model Has Collapsed?

ASR measures: *"Is a triggered image classified as the target class?"*

BadNets target class = **class 0** (airplane).

Because the model predicts **class 0 for every input**:

- Triggered image → predicted class 0 → ASR counts this as **correct** (inflates ASR)
- Clean image → predicted class 0 → CA counts this as **wrong** (except genuine airplanes)

ASR = 99% does not indicate the backdoor is active. It is an artifact of the collapsed model being stuck on the target class. Conversely, in draws where the model collapses onto a different class (not class 0), ASR drops to near 0% while CA remains ~10% — same degree of collapse, different stuck class.

**Conclusion:** The backdoor does not recover. The model loses utility before the backdoor has any opportunity to reactivate.

---

## 6. Paper Framing

> **Note:** These are suggestions for reference when writing. Final decisions should be agreed upon with the team and Prof. Hung.

### What to Avoid

Do not frame ANP as "fragile to rollback" in the sense that the backdoor is easily recoverable — the data does not support this. CA collapses at k=1, meaning the model is non-functional and no meaningful evaluation of backdoor behavior is possible.

Do not report ASR figures for k=1–5 without explicitly noting that CA has collapsed to random-chance level. Presenting these ASR values without that caveat would misrepresent what is being measured.

### Recommended Framing — "Utility Collapse" Finding

**Core claim:** Shard substitution on an ANP-defended model does not restore the backdoor — instead, it destroys model utility at k=1. The attacker cannot roll back the backdoor while keeping the model functional, because the model collapses before the backdoor has any chance to recover.

**Defender-side property:** This is a favorable signal from a defense perspective. An ANP model that has been tampered with (via shard substitution) will self-destruct in terms of utility — a behavior that is detectable through standard clean accuracy monitoring, even without access to trigger examples.

**Contrast with fine-tune:** Fine-tune hybrids show genuine backdoor recovery (high CA, rising ASR with k) — the attacker succeeds. ANP hybrids show the opposite mechanism: not a stronger defense in the conventional sense, but an architectural incompatibility that causes collapse rather than recovery.

**Draft sentence for the paper:**

> *"Unlike fine-tuned models, in which hybrid variants retain high clean accuracy while recovering attack success rate proportional to the number of substituted shards, ANP hybrid models collapse to random-chance clean accuracy at k=1. The observed high ASR is an artifact of the collapsed model predicting a single class for all inputs, not evidence of backdoor reactivation. This utility collapse precedes any potential backdoor recovery, making shard substitution on ANP-defended models detectable through standard accuracy monitoring rather than trigger-based evaluation."*
