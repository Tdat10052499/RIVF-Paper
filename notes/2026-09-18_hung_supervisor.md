# Supervisor Note, 18 September 2026

**Author:** Dang Khanh Hung
**Subject:** Day-5 gate outcome, required controls, and the redirection of the paper
**Days to deadline:** 11 (submission 29/09/2026)

---

## 1. Verdict

The work of the past five days is solid. You reproduced the BadNets baseline at CA 89.41% and ASR 97.43%, you confirmed the repair at ASR 0.90%, you built a partition and substitution harness, and you recorded the numbers with their denominators. That is the correct order of operations, and it is the reason we can now reason about the result at all.

The gate failed. I am not yet willing to accept the failure as a scientific finding, for one control that would distinguish a real negative result from a broken model has never been measured. Read Section 2 before you draw any conclusion from the per-layer numbers, and before you commit to either option in your notes.

We are not abandoning the submission. The redirection in Section 4 gives us a paper whether the effect recovers or not.

---

## 2. Two controls that must run before anything else

Both are inference-only, both cost minutes, and both are decisive.

### 2.1 Measure clean accuracy for every hybrid model

`scripts/run_substitution.py` evaluates only the poisoned test set and records only ASR. Gate Condition 4 has therefore never been measured, and without it a low ASR admits two incompatible readings: the backdoor was not restored, which is interesting, or the hybrid model was destroyed by the substitution, which is an artifact and tells us nothing.

I read the second as the more likely explanation. Swapping layer3 yields ASR 0.50%, which sits below the repaired model's own 0.90% baseline. A hybrid that merely fails to restore the backdoor should land near 0.90%, not beneath it. Depression below the baseline is what one expects when the model has stopped functioning and its predictions have collapsed onto some class other than the target.

Add clean accuracy to the record for every configuration already run. If CA collapses toward 10%, the substitution produced a non-functional network, the per-layer narrative in Section 5 of the gate report is unfounded, and the experiment must be rebuilt before it can be interpreted.

### 2.2 Verify the harness by full rollback

Substitute every shard at once. The result must reconstruct the infected model exactly and must report ASR 97.43% and CA 89.41%. Any other number proves a defect in `substitute()` or in the key mapping, and every measurement taken so far would then be void.

Run the same check at n=3 and n=6. This is the cheapest correctness test available to us, and we should have had it from the first day.

---

## 3. The confound in the current design

The repair is a 20-epoch clean fine-tune with SGD at lr=0.01 under cosine annealing. That procedure raised clean accuracy from 89.41% to 93.35%. A repair does not ordinarily improve the model it repairs by 3.94 percentage points. What you performed is closer to a retrain than to a patch.

This matters because it breaks the premise of the threat model. Shard-version skew presumes that the repaired and the stale shard belong to one lineage and differ only by the repair update, so that a stale shard remains a plausible component of the assembled model. After twenty epochs of global fine-tuning, the repaired weights have drifted so far that an infected shard is no longer a member of the same distribution as its neighbours. The observed failure is then a statement about representational incompatibility at the shard boundary, not a statement about where the backdoor lives.

Chinh's conclusion, that clean fine-tuning overwrites the infected weights globally, is correct as far as it goes. The inference to draw from it is not that the hypothesis is falsified. It is that the repair method is the variable we failed to control.

An operator running inference at the edge does not spend twenty epochs to patch a backdoor. Cheap and local repairs are what such a deployment actually applies, and those are precisely the repairs we have not tested.

---

## 4. The redirection

Adopt repair locality as the independent variable. The thesis becomes the following.

Whether a signed but stale shard can restore a repaired backdoor is governed by how local the repair update is. A global repair rewrites the whole weight distribution and resists single-shard rollback as a side effect of its cost. A local repair concentrates the update in a few layers, and a single stale shard then suffices to restore a large fraction of the attack. Cheap repairs are the ones edge deployments can afford, so the systems that are least able to retrain are the ones most exposed to shard skew.

This framing subsumes the result you already hold. Clean fine-tuning becomes the resistant endpoint of a spectrum rather than a dead end, and it earns its place in the paper as a control rather than as a failure. The security recommendation follows without strain: epoch-manifest pinning is necessary exactly where repair is cheapest, which is exactly where per-shard signature checking is most likely to be the only control in place.

### 4.1 Measure where the repair lives

For each shard s, compute the relative update norm and the share of the total repair update:

```
r_s     = || W_repaired[s] - W_infected[s] ||_2  /  || W_infected[s] ||_2
share_s = || W_repaired[s] - W_infected[s] ||_2^2  /  sum_j || W_repaired[j] - W_infected[j] ||_2^2
```

`share_s` is the fraction of repair update reverted when shard s is rolled back, which is a metric we already committed to in Section 4 of the Project Agreement. It requires no forward pass and runs in seconds.

Plot `share_s` against recovered ASR across every repair method. That scatter is the central figure of the paper, for it converts a binary gate into a quantitative relationship and it explains both the negative and the positive cases within one account.

### 4.2 Add local repair methods

Produce repaired checkpoints under at least two of the following, holding the infected checkpoint, the partition, the seed, and the evaluation fixed:

- Apply ANP, which prunes by mask and concentrates the update in few neurons.
- Apply fine-pruning, which prunes dormant channels and then fine-tunes briefly.
- Apply clean fine-tuning for 1 epoch at lr=0.001, which is the same method as the current baseline reduced to a realistic patch budget.

Retain the 20-epoch run as the global endpoint. Expect the ordering ANP < fine-pruning < short fine-tuning < 20-epoch fine-tuning in resistance, and report it whatever it turns out to be.

### 4.3 Extend to multi-shard skew

Run the two-shard sweep at n=6. Fifteen combinations at inference cost is minutes of work once the evaluation is batched, and the result gives a recovery curve as a function of the number of skewed shards, anchored at one shard and at full rollback. Dan's proposed extension of `substitute()` to accept a list of indices is the right implementation.

### 4.4 Batch the evaluation

The current loop opens one image at a time and runs a forward pass per image over 9,000 images on CPU. Load the poisoned test set once, batch at 256, and run on the M2 with `device="mps"`. The sweeps in 4.2 and 4.3 are otherwise slower than they need to be by a factor of roughly fifty, and we do not have the days to spare.

---

## 5. Revised gate

The original threshold assumed a single repair method and is no longer the right question. Replace it with the following, and treat it as equally falsifiable.

At least one realistic repair method admits recovery of ASR to 50% or above, or to 30 percentage points above its own repaired baseline, from the rollback of at most two shards, with hybrid clean accuracy within 5 percentage points of the repaired model, reproduced across two seeds.

If no repair method clears this, we write the negative result, and Section 4.1 still carries it: we report repair locality as a measurable predictor of shard-skew resistance, and we state the conditions under which the attack would succeed. That paper is honest and it is submittable. What we must not do is report the current numbers as a finding about backdoor localization, for the clean-accuracy control has not been run and the repair method was uncontrolled.

---

## 6. Schedule

| Dates | Work | Owner |
|---|---|---|
| 18-19/09 | Run controls in Section 2. Add clean accuracy to every existing configuration and verify full rollback. | Dan |
| 18-19/09 | Compute `r_s` and `share_s` for the 20-epoch repair. Batch the evaluation. | Dan, Chinh |
| 19-21/09 | Produce ANP and fine-pruning checkpoints, and the 1-epoch fine-tune. | Chinh |
| 20-22/09 | Run single-shard and two-shard sweeps for every repair method, two seeds. | Dan |
| 21-23/09 | Build the serving comparison: per-shard signature checking against epoch-manifest pinning, with latency and rollout recovery measured on the M2 only. | Dat |
| 22/09 | Decide against the revised gate. | All |
| 23-27/09 | Write the six pages. Results first, then method, then introduction, related work, and abstract last. | All |
| 28-29/09 | Audit adversarially, then submit. | All |

Report the Section 2 results to me as soon as they exist. They determine whether the rest of this schedule stands.

---

## 7. On the gate report

The report is well organised and the tables are readable, and translating it to English was the right call. One correction of habit. Section 5 assigns meaning to each layer, stating for instance that conv1 carries no backdoor information and that layer3 suppresses the backdoor signal from surrounding layers. Those readings rest on one seed, on a model whose clean accuracy was never measured, and on a repair that we now know to be uncontrolled. Interpretation of that weight requires evidence of matching weight.

Record what was measured, state what it might mean, and mark the distinction plainly. Keep the instinct to explain. Attach it to controls that can bear it.
