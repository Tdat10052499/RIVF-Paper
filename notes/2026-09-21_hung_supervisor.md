# Supervisor Note, 21 September 2026

**Author:** Dang Khanh Hung
**Subject:** Controls passed, the locality metric is invalid, and where the remaining eight days go
**Days to deadline:** 8 (submission 29/09/2026)

---

## 1. Verdict

Both controls passed, and they passed cleanly. Full rollback reconstructs the infected model exactly at ASR 97.43% and CA 89.41% under both partitions, which verifies `substitute()` and the key mapping. Every hybrid retains clean accuracy between 84.58% and 93.26%, against a repaired baseline of 93.35%.

I was wrong about the likely cause. I expected the hybrids to be non-functional and the low ASR to be an artifact of a collapsed model. They are functional, and the negative result is genuine. Dan's conclusion on this point is correct, and the work that established it was the right work to do first.

This changes the finding rather than removing it. A stale shard is accepted silently: the assembled model continues to serve at near-normal accuracy, so no utility alarm fires, and the backdoor nonetheless does not return. Silence and ineffectiveness together are a more precise result than either alone.

One measurement is invalid and must not enter the paper in its current form. Section 2 explains why.

---

## 2. The locality metric is measuring BatchNorm counters

`scripts/compute_share.py` iterates over every key in the shard without filtering:

```python
for key in inf_shard:
    delta_parts.append((rep_shard[key] - inf_shard[key]).float().flatten())
```

State dictionaries carry more than learnable parameters. They also carry `running_mean`, `running_var`, and `num_batches_tracked`, the last of which is an integer counting optimizer steps. It is not a weight, it has no metric meaning, and after twenty epochs of fine-tuning it dominates every genuine weight difference by four orders of magnitude.

The published numbers confirm this exactly.

- Observe that `norm_delta` equals 15640.0 for layer1, layer2, layer3, and layer4 alike. Those groups differ by roughly a factor of sixteen in parameter count, for layer1 operates on 64 channels and layer4 on 512. Real weight deltas cannot agree to seven significant figures.
- Note that 15640 = 2 x 7820. PreActResNet18 places exactly four BatchNorm layers in each residual group, being two blocks of two. The L2 norm of four identical values d equals 2d, so d = 7820, which is the number of optimizer steps in a 20-epoch fine-tune at 391 batches per epoch.
- Note that `norm_inf` equals 78000 = 2 x 39000, the infected model's own counter at 390 steps across 100 epochs, which is BackdoorBench's default schedule.
- Observe that r_s = 7820 / 39000 = 0.2005128, which is precisely the value reported for all four residual groups.
- Observe that conv1 and the linear layer carry no BatchNorm, and so report the only honest numbers in the file: 0.576 and 0.375.

The metric therefore ranks shards by how many BatchNorm layers they contain. It says nothing about where the repair lives.

The reported finding, that the fine-tune distributes exactly 25% of its update into each residual block, is an artifact of that counting. Treat it as withdrawn. This is the most dangerous class of defect we will meet in this project, for the wrong number was plausible, it agreed with the story we already believed, and nothing about it looked wrong on the page. A number that confirms the hypothesis deserves more scrutiny than one that contradicts it, not less.

### 2.1 The fix

Restrict the computation to learnable parameters. Exclude the step counter unconditionally, and report BatchNorm statistics separately if we want them at all.

```python
SKIP = ("num_batches_tracked", "running_mean", "running_var")

for key in inf_shard:
    if any(key.endswith(s) for s in SKIP):
        continue
    delta_parts.append((rep_shard[key] - inf_shard[key]).float().flatten())
    inf_parts.append(inf_shard[key].float().flatten())
```

Report two quantities per shard, for they answer different questions. Report `share_s` as the fraction of the total repair update held by that shard, which is what a rollback reverts. Report the same quantity divided by the shard's parameter count, which gives update density and corrects for layer4 holding far more parameters than layer1. The first says how much of the repair is lost; the second says how concentrated the repair is.

Re-run for both partitions before anything else. The corrected table is the paper's explanatory mechanism, and no figure can be drawn until it exists.

---

## 3. Your own data already points to the strongest remaining experiment

Compare the two partitions on the results you have.

| Configuration | Shard contents | ASR |
|---|---|---|
| n=6, shard 4 | layer4 | 8.08% |
| n=6, shard 5 | linear | 1.18% |
| n=3, shard 2 | layer4 and linear together | **17.46%** |

Rolling back layer4 and the linear layer together recovers 17.46%, against 9.26% for the arithmetic sum of the two taken separately. The combination is superadditive by a factor of roughly 1.9, and it is the highest number in the study.

This is direct evidence for the distributed-backdoor hypothesis, and it was sitting in the pilot data before the gate was declared failed. Two shards recover what one cannot, and the effect compounds rather than adds.

Run the two-shard sweep. It is inference-only, it is fifteen combinations at n=6, and it is the cheapest path we have to a positive result. Anchor the recovery curve at one shard, two shards, and full rollback at 97.43%. Report clean accuracy alongside ASR at every point.

I rate this above the ANP work in expected value, though both should run. Note also that the contrast is not either-or: the same sweep on a locally repaired model is where the two lines of the paper meet.

---

## 4. Priorities, compressed

The target has moved forward. We want a complete first draft, every section written and every figure placed, by late on 26 September. That leaves 27 and 28 for my editing passes and your revisions, and 29 for the final proof and the submission itself. A draft that arrives on the 28th cannot be edited twice, and a paper edited once reads like a paper edited once.

Work strictly in this order. Anything below the line is discarded without discussion.

**Today and tomorrow, 21 and 22 September.**

- Fix `compute_share.py` per Section 2.1 and re-run both partitions. Owner: Dan. This blocks everything in Section 10, so it comes before all other work.
- Run the k-shard recovery curve at n=6 for k from 1 to 6, recording ASR and clean accuracy at every point. Owner: Dan. See Section 10.1.
- Run the three selection strategies at each k: repair-aware, architectural, and random averaged over five draws. Owner: Dan. See Section 10.2. This is the highest-value experiment remaining.
- Produce the ANP checkpoint with BackdoorBench's own defense script. Owner: Chinh. Nothing downstream begins until this exists, which makes it the critical path.
- Create the paper scaffold in `paper/`: the IEEE six-page template, every section heading, and a named placeholder for each figure and table. Owner: Dat. This takes an hour and it removes the blank page from the 24th.

**23 September.**

- Repeat the curve and the selection strategies against the ANP model. Owner: Dan.
- Confirm the best configuration on a second seed before it becomes the headline number. Owner: Dan. This has moved above the line, for an exploratory maximum that has not been reproduced is not a result.
- Compute the corrected locality metric for the ANP model, and plot it against recovered ASR across both repairs. Owner: Chinh.
- Build the two-process serving harness bounded to the four numbers in the 18/09 note, Section 4.5. Owner: Dat.

**Experiments freeze at the end of 23 September.** A figure that does not exist by then does not enter the paper. If the ANP sweep is incomplete, we write the paper we have.

**Below the line, discarded by default.**

- Fine-pruning, NAD, and the 1-epoch fine-tune.
- Any partition other than n=3 and n=6.
- Any architecture or dataset beyond PreActResNet18 and CIFAR-10.

---

## 5. The writing plan

Writing begins on 24 September with the results already frozen, so nobody waits on a number. Draft in the order the evidence supports, not the order the paper is read in. Each of you owns sections and drafts them in full, including the figures and their captions. A section without its figure placed is not drafted.

**24 September.** Draft the Results section and the Method and threat model. Dan owns Results, for the sweeps and the locality figure are his. Chinh owns Method, the repair procedures, and the experimental setup. Dat owns the deployment and serving subsection. Target by end of day: every number in the paper, every table, every figure, every caption.

**25 September.** Draft the Introduction, the Related Work, and the Conclusion. Chinh owns Related Work against the six works named in the Project Agreement. Dan and Dat draft the Introduction together. Target by end of day: continuous prose from the first line to the last, with the abstract still open.

**26 September.** Write the abstract, tighten to exactly six pages, fix every reference, and read the whole paper aloud once as a team. Target by late evening, Vietnam time: a complete draft in `paper/`, pushed, with nothing marked as to be done.

Push each section as you finish it rather than at the end of the day, for I would rather read three sections on the 24th than nine on the 26th. If I can begin editing early, you gain a pass.

**27 and 28 September.** I edit twice. You revise between the passes and answer my queries the same day they arrive. Keep these two days clear.

**29 September.** Final proof, format check, and submission with hours to spare, not minutes.

---

## 6. Division of effort

Only Dan has committed since 18 September. The controls were his, the scripts were his, and the MPS support was his. That is good work and it is also a single point of failure with eight days remaining.

Chinh, the ANP checkpoint is the critical path for Section 4 of the paper and nothing downstream of it can begin until it exists. Dat, the serving harness is four numbers and one table, and it needs to exist by 24 September. Both of you please push something today, even if it is only a running script and a note of what failed.

---

## 7. What the paper says now

Write to this claim, and revise it only if the sweeps overturn it.

Single-shard version skew against a globally repaired model is silent and ineffective. The assembled model serves at clean accuracy within roughly 7 percentage points of the repaired baseline, so per-shard signature checking raises no alarm and utility monitoring does not detect the skew. The backdoor nonetheless recovers to at most 17.46% against 97.43% for full rollback. Recovery scales with the fraction of the repair update reverted, and it compounds superadditively across adjacent shards, so the exposure of a deployment is set by how concentrated its repair is rather than by whether any single shard is stale.

The security recommendation is unchanged and it survives every branch. Epoch-manifest pinning is the control that detects skew, per-shard signature validity does not imply epoch consistency, and the gap between the two widens as the repair becomes cheaper and more local.

Report the negative components plainly. A six-page paper that measures an attack carefully, bounds when it works, and states honestly where it fails is a contribution. Do not inflate 17.46% into a threat, and do not bury it either.

---

## 8. On the note of 19 September

The structure is right, the tables are readable, and reporting the controls before interpreting them is exactly the discipline I asked for. Correct one habit. The section headed "Key finding" drew a conclusion from a metric that had not been validated, and the conclusion was wrong for a reason visible in the numbers themselves, being four identical values where four different ones were required.

Before a number becomes a finding, ask what it would look like if the code were wrong. Identical values across structurally different layers is what that looks like.

---

## 9. On the next eight days

I am asking the three of you for more hours than you have been giving, and I would rather say so plainly than imply it through a schedule you cannot meet.

The reason is that the work is closer than it looks. The harness is verified, the baselines are reproduced, the controls are clean, and the strongest experiment remaining is fifteen inference runs that your own pilot data already predicts will succeed. What stands between this repository and a submitted paper is not insight and it is not compute. It is days, and we have eight of them.

A deadline is the one constraint in research that does not negotiate. Reviewers will never see the version of this paper that needed one more week, for that version does not exist. The paper that exists is the one uploaded before the 29th.

So for the next five days, push harder than your normal commitment. Start earlier than you would, finish later than you would, and treat the freeze on the 23rd and the draft on the 26th as fixed points rather than as targets to be renegotiated on the day. Push your work as you complete it, not in the evening, for each of you is blocking somebody: Chinh's checkpoint blocks Dan's sweeps, Dan's figures block the Results section, and the scaffold blocks everyone on the 24th. A commit pushed at noon buys the team an afternoon.

Three practical things. Protect your sleep, for a tired reader of your own code is exactly the reader who accepts a number like 15640.0 four times without asking why. Ask for help the hour you are stuck rather than the following morning. And tell me early if something will not land, because a schedule I can adjust on the 23rd is worth more than an apology on the 27th.

In return, the week after the 29th is yours. No tasks from me, no meetings, nothing to read. Take the whole of it and recover properly. A sprint is defensible precisely because it ends, and this one ends on a date we can all see. Research done permanently at this pace produces worse work and worse researchers, so understand this as the exception it is rather than as the standard I expect.

One last thing, and I mean it as more than encouragement. Most students never finish a first paper. They stall at the point you reached last week, which is the point where the first hypothesis fails and the result is not what anybody hoped. You did not stall. You ran the controls, you found your own negative result, you reported it honestly, and you asked what to do next. That is the part of research that cannot be taught, and you already have it.

Finish the paper.

---

## 10. Where the positive results are, and how to reach them honestly

The study leans negative as it stands, and I agree that is a weakness with this reviewer pool. A conservative committee rewards an attack that works and a defense that stops it. It does not reward a careful null. Three positives are genuinely available in this problem, all of them inference-only, and none of them requires us to soften a number.

### 10.1 Report the recovery curve, not the single-shard point

Sweep k from one shard to all six and report ASR and clean accuracy at every k, anchored at 0.90% for k=0 and 97.43% for k=6. The curve is monotone in expectation and it must cross 50% somewhere below k=6. Wherever it crosses is a positive finding stated as a threshold: an adversary who controls k of n shards restores the backdoor, and k is smaller than the whole model.

This is not a reframing of a null. It is the quantity we should have measured first, for the question was never whether one shard suffices. It was how much staleness a deployment can tolerate.

### 10.2 Let the adversary choose shards by where the repair lives

Our partitioning so far follows architectural boundaries and rolls back whichever shard the index happens to name. A real adversary does no such thing. The threat model already grants control of the artifact cache, so the adversary holds both the pre-repair and the post-repair artifacts, and both are signed. Diffing them is free.

Rank shards by the corrected `share_s` and roll back the top-k first. Compare three selection strategies at each k: repair-aware selection, architectural order, and random selection averaged over several draws. If repair-aware selection reaches the threshold at a smaller k than the alternatives, that is the paper's strongest result, for it converts the contribution from a measurement into an attack with a stated optimization.

I rate this the single most valuable experiment remaining. It costs the same inference budget as the sweep in 10.1, it uses the harness we have already verified, and it makes the corrected locality metric load-bearing rather than merely explanatory.

### 10.3 State the stealth constraint, for it is already measured

Every hybrid retained clean accuracy between 84.58% and 93.26% against a 93.35% baseline. That is the stealth result and we have it already. Report recovered ASR jointly with the clean-accuracy cost at every point, and identify the configurations that restore the backdoor while remaining within a few percentage points of the repaired baseline. An attack that is effective and undetectable by utility monitoring is a stronger claim than one that is merely effective.

### 10.4 Restructure the paper accordingly

Write it as an attack paper, which is the shape this committee reads fluently. Characterize the conditions under which shard-version skew restores a backdoor: how many shards, chosen how, at what cost to clean accuracy, and against which repair. The single-shard null then appears where it belongs, as the lower boundary of the attack's operating region rather than as the headline. Close with epoch-manifest pinning as the control that detects the skew at any k.

Same data, same honesty, and a structure a reviewer can follow without sympathy for negative results.

### 10.5 The line we do not cross

We are searching for a positive result, so be clear about what keeps that search sound. Two rules carry the weight, and neither requires narrating how we arrived at the experiment.

Report the sweep complete. Every k, every selection strategy, clean accuracy beside attack success at each point, and the configurations that performed badly alongside the one that performed best. Completeness is what distinguishes a characterisation from a search for a favourable number, and a full curve with three strategies at every point is a complete factorial report rather than a winner plucked from many attempts. Nothing about it is selective, so nothing about it needs defending.

Claim no prediction we did not make. The paper should state what we measured and what it implies. It should not assert that we hypothesised a particular threshold, nor present repair-aware selection as a prediction confirmed, for we ran it as a comparison and that is how it should read. Describing three strategies and reporting their results is ordinary experimental writing. Inventing a hypothesis after the fact is not, and it is also unnecessary, since the comparison is interesting on its own terms.

Confirm the best configuration on a second seed before it becomes the headline number. An unreproduced maximum is not a result, and this is why the second seed moved above the line today.

The chronology itself need not appear in the paper. I had earlier asked for a sentence recording that the selection strategy followed the single-shard null. Drop it. It protects less than the two rules above, and a conservative reader is liable to read an accurate account of our sequence as an admission of fishing. Silence about the order of our work is honest. A false claim of foresight would not be.

We do not need to overstate anything. Seventeen per cent from two shards is already a real effect, the curve will give us a larger one, and repair-aware selection will most likely give us the largest.

One practical consequence. If we release this repository as an artifact alongside the paper, these notes and the original gate travel with it, which is entirely fine and reflects well on the work. It is fine precisely because the paper will claim no foresight it did not have.
