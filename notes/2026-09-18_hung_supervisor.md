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

### 4.2 Add one local repair method, not four

The thesis requires the two endpoints of the locality axis, not a dense spectrum. Produce exactly two repaired checkpoints, holding the infected checkpoint, the partition, the seed, and the evaluation fixed:

- Retain the existing 20-epoch clean fine-tune as the global endpoint. This is already done.
- Apply ANP as the local endpoint, which prunes by mask and concentrates the update in few neurons.

BackdoorBench ships ANP, fine-pruning, and NAD as implemented defenses. Run their script against our infected checkpoint rather than implementing anything, and record the exact command, configuration, and seed.

Treat fine-pruning and a 1-epoch fine-tune at lr=0.001 as optional intermediate points. Add them only if the two endpoints are complete and validated by 22/09. Two endpoints establish the relationship; intermediate points decorate it.

### 4.3 Extend to multi-shard skew

Run the two-shard sweep at n=6. Fifteen combinations at inference cost is minutes of work once the evaluation is batched, and the result gives a recovery curve as a function of the number of skewed shards, anchored at one shard and at full rollback. Dan's proposed extension of `substitute()` to accept a list of indices is the right implementation.

### 4.4 Batch the evaluation

The current loop opens one image at a time and runs a forward pass per image over 9,000 images on CPU. Load the poisoned test set once, batch at 256, and run on the M2 with `device="mps"`. The sweeps in 4.2 and 4.3 are otherwise slower than they need to be by a factor of roughly fifty, and we do not have the days to spare.

### 4.5 Bound the serving experiment to one table

`src/serving/` is empty with eleven days remaining, so we build the smallest artifact that supports the claim. Do not build a system. Build two processes that load a model from a manifest, and report four numbers comparing per-shard signature checking against epoch-manifest pinning:

- Report manifest size in bytes.
- Report verification latency per model load.
- Report rollout recovery time after an interrupted update.
- Report whether the skewed assembly is accepted or rejected under each policy.

One table and one paragraph. The security claim rests on Section 4.1 and the sweeps; the serving component establishes deployment relevance for a 6G session and nothing more.

---

## 4a. The paper lands whatever the measurements say

Read this before you worry about the outcome. Three branches remain open, and each yields a submittable paper under the framing in Section 4.

Under the first branch, hybrid clean accuracy holds and ASR recovers under the local repair. We report shard-version skew as a practical attack against locally repaired models, and epoch pinning as the control that defeats it.

Under the second, hybrid clean accuracy holds and ASR stays low under every repair. We report repair locality as a measurable predictor of shard-skew resistance, with a negative attack result stated plainly and the conditions for success identified.

Under the third, hybrid clean accuracy collapses. Skew degrades utility before it restores the backdoor, which makes utility monitoring a viable detector and makes the attack self-announcing. That is an availability finding, and it is worth reporting, for it tells an operator what to watch when manifest pinning is absent.

None of these is a failure. The failure mode available to us is not a null measurement. It is running out of days.

---

## 5. Revised gate

The original threshold assumed a single repair method and is no longer the right question. Replace it with the following, and treat it as equally falsifiable.

At least one realistic repair method admits recovery of ASR to 50% or above, or to 30 percentage points above its own repaired baseline, from the rollback of at most two shards, with hybrid clean accuracy within 5 percentage points of the repaired model, reproduced across two seeds.

If no repair method clears this, we write the negative result, and Section 4.1 still carries it: we report repair locality as a measurable predictor of shard-skew resistance, and we state the conditions under which the attack would succeed. That paper is honest and it is submittable. What we must not do is report the current numbers as a finding about backdoor localization, for the clean-accuracy control has not been run and the repair method was uncontrolled.

---

## 6. Schedule

| Dates | Work | Owner |
|---|---|---|
| 18-19/09 | Run both controls in Section 2. Add clean accuracy to every configuration already run, and verify full rollback returns ASR 97.43% and CA 89.41%. | Dan |
| 18-19/09 | Compute `r_s` and `share_s` for the 20-epoch repair. Batch the evaluation at 256 on the M2. | Dan, Chinh |
| 19-20/09 | Produce the ANP checkpoint using BackdoorBench's own defense script. | Chinh |
| 20-22/09 | Run single-shard and two-shard sweeps for both repairs, two seeds, recording ASR and clean accuracy together. | Dan |
| 20-22/09 | Build the two-process serving harness bounded to the four numbers in Section 4.5. | Dat |
| 22/09 | Decide against the revised gate. Freeze scope. | All |
| 23/09 | Freeze figures and tables. Assign one section owner each. | All |
| 23-26/09 | Write the six pages. Results first, then method and threat model, then introduction, related work, and the abstract last. | All |
| 27-28/09 | Two editing passes over the full manuscript. | Hung |
| 28-29/09 | Audit adversarially against the claim-evidence table, then submit. | All |

Two rules hold this schedule together.

Report the Section 2 results to me as soon as they exist, for they determine whether the rest of the schedule stands. If full rollback does not return 97.43%, stop everything and find the defect.

Add no new experiment after 22/09. A figure that does not exist by the freeze does not enter the paper. We have eleven days, and the way a first paper fails is never depth. It is breadth pursued until the writing has no time left.

---

## 7. On the gate report

The report is well organised and the tables are readable, and translating it to English was the right call. One correction of habit. Section 5 assigns meaning to each layer, stating for instance that conv1 carries no backdoor information and that layer3 suppresses the backdoor signal from surrounding layers. Those readings rest on one seed, on a model whose clean accuracy was never measured, and on a repair that we now know to be uncontrolled. Interpretation of that weight requires evidence of matching weight.

Record what was measured, state what it might mean, and mark the distinction plainly. Keep the instinct to explain. Attach it to controls that can bear it.
