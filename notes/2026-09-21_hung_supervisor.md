# The Plan, 21 September 2026

**From:** Dang Khanh Hung
**To:** Dan, Chinh, Dat
**Submission:** 29 September 2026. Eight days.

This note replaces every earlier instruction. If something here contradicts the 18 September note or the README, follow this note.

---

## 1. Where we stand

Your controls passed, and they passed cleanly.

| Check | Result | Status |
|---|---|---|
| Infected model | ASR 97.43%, CA 89.41% | Good |
| Repaired model, 20-epoch clean fine-tune | ASR 0.90%, CA 93.35% | Good |
| Full rollback rebuilds the infected model | ASR 97.43%, CA 89.41%, exact | Harness verified |
| Clean accuracy of every hybrid | 84.58% to 93.26% | Models are not broken |
| Best single-shard rollback | ASR 17.46% | Below the 50% gate |

Two things follow.

I was wrong about the cause. I expected the hybrid models to be broken and the low ASR to be meaningless. They are not broken. Your negative result is real, and you found it properly.

The result is more interesting than it first looks. A stale shard is accepted silently, for the model keeps serving at close to normal accuracy and nothing raises an alarm. The backdoor still does not come back. Silent and ineffective together is a sharper finding than either one alone.

---

## 2. Fix this before anything else

`scripts/compute_share.py` is measuring the wrong thing. It loops over every key in the shard, which includes `num_batches_tracked`. That is an integer counting training steps, not a weight. After 20 epochs it is about 7820, while real weight differences are around 0.5, so it drowns out everything else.

You can see it in your own output. `norm_delta` is exactly 15640.0 for layer1, layer2, layer3, and layer4, even though layer4 has roughly sixteen times the parameters of layer1. Real weights never agree that exactly. The value is just 2 x 7820, being the four BatchNorm counters in each residual block.

So `share_s` currently ranks shards by how many BatchNorm layers they contain. The conclusion in the 19 September note, that each residual block holds 25% of the repair, is withdrawn.

**The fix.** Skip the buffers and keep only learnable parameters:

```python
SKIP = ("num_batches_tracked", "running_mean", "running_var")

for key in inf_shard:
    if any(key.endswith(s) for s in SKIP):
        continue
    delta_parts.append((rep_shard[key] - inf_shard[key]).float().flatten())
    inf_parts.append(inf_shard[key].float().flatten())
```

Re-run for n=3 and n=6. Everything in Section 3 depends on the corrected numbers.

One lesson worth keeping. That wrong number looked right because it agreed with what we already believed. A number that confirms your hypothesis deserves more checking than one that contradicts it, not less.

---

## 3. What to run

Work in this order. Owners and deadlines are fixed.

### Priority 1, by end of 22 September

**Dan, fix `compute_share.py` and re-run.** Section 2. Everything else waits on this.

**Dan, run the k-shard recovery curve at n=6.** Roll back k shards for k = 1, 2, 3, 4, 5, 6. Record ASR and clean accuracy at every k. You already know the endpoints: 0.90% at k=0 and 97.43% at k=6. The curve has to cross 50% somewhere in between, and wherever it crosses is a real result. It tells a deployment how much staleness it can survive.

**Dan, compare three ways of choosing which shards to roll back.** At each k, try:

- Repair-aware: roll back the shards with the highest corrected `share_s` first.
- Architectural: roll back in index order, as you do now.
- Random: pick k shards at random, averaged over five draws.

This is the most valuable experiment left. Our threat model already lets the attacker control the artifact cache, so the attacker holds both the old and the new signed model and can simply compare them to find where the repair is. A smart attacker would target those shards. If repair-aware selection reaches the threshold at a smaller k than the other two, we have an attack with a strategy, not just a measurement.

**Chinh, produce the ANP checkpoint.** Use BackdoorBench's own defense script against our infected checkpoint. Do not implement anything. Record the exact command, config, and seed. This has not started and everything in Priority 2 waits on it.

**Dat, build the paper scaffold in `paper/`.** The IEEE six-page template, every section heading, and a named placeholder for each figure and table. One hour of work, and it means nobody faces a blank page on the 24th.

### Priority 2, by end of 23 September

**Dan, repeat the curve and the three strategies against the ANP model.** ANP is a local repair, so we expect it to be far more fragile than the 20-epoch fine-tune. That contrast is the heart of the paper.

**Dan, re-run the best configuration on a second seed.** A single best number found across roughly eighteen configurations might just be luck. One more seed turns it into a result.

**Chinh, compute the corrected locality metric for the ANP model and plot it against recovered ASR** for both repairs, all shards. This is the figure that explains why the attack works when it works.

**Dat, build the serving comparison.** Two processes that load a model from a manifest. Report four numbers, comparing per-shard signature checking against epoch-manifest pinning: manifest size in bytes, verification time per load, rollout recovery time after an interrupted update, and whether the skewed model is accepted or rejected. One table and one paragraph. Do not build a system.

### Experiments stop at the end of 23 September

A figure that does not exist by then does not go in the paper. If something is unfinished, we write the paper with what we have.

### Not doing

Fine-pruning, NAD, the 1-epoch fine-tune, other partitions, other architectures, other datasets. Do not start any of these, even if you have time. Spend spare time on the writing instead.

---

## 4. The paper we are writing

Write it as an attack paper. That is the shape reviewers at this venue read most easily: here is an attack, here is when it works, here is the defense.

**The claim.** An adversary who controls the artifact cache can assemble a model from shards of different versions. We measure when this restores a backdoor. Rolling back a single shard is not enough, recovering at most 17.46% against 97.43% for the full model, and it is invisible to utility monitoring, for clean accuracy stays within a few points of normal. Recovery grows with the number of stale shards and with the fraction of the repair they contain, so an attacker who targets the shards carrying the repair succeeds with fewer of them. Exposure depends on how concentrated the repair is, which means cheap local repairs are the most vulnerable.

**The defense.** Epoch-manifest pinning detects the skew. A valid per-shard signature does not prove epoch consistency. We are not proposing a new protocol, for TUF and Uptane already define these controls. We are measuring what happens in machine learning when they are missing.

**Where the negative goes.** The single-shard result is the lower boundary of the attack, not the headline. Report it plainly inside the attack story. Do not inflate 17.46% into a threat and do not hide it either.

---

## 5. Writing

Writing starts on 24 September with all results frozen, so nobody waits on a number. **The complete draft is due late on 26 September, Vietnam time.** That gives me the 27th and 28th for two editing passes, and the 29th for the final check and submission. A draft that arrives on the 28th only gets edited once, and it will read that way.

Each of you drafts your sections in full, figures and captions included. A section without its figure placed is not finished.

**24 September.** Dan writes Results. Chinh writes Method, threat model, and experimental setup. Dat writes the deployment and serving subsection. By end of day, every number, table, figure, and caption is in the document.

**25 September.** Chinh writes Related Work against the six papers named in the Project Agreement. Dan and Dat write the Introduction together. Someone writes the Conclusion. By end of day, the paper reads continuously from start to finish, with only the abstract missing.

**26 September.** Write the abstract, cut to exactly six pages, fix every reference, and read the whole paper aloud together once. Push the complete draft by late evening.

**Push each section as you finish it, not at the end of the day.** If I can start editing on the 24th, you gain a pass.

**27 and 28 September.** I edit twice. You revise between passes and answer my questions the same day. Keep both days clear.

**29 September.** Final proof and submit with hours to spare.

---

## 6. Two rules for reporting results

**Report everything you ran.** Every k, every selection strategy, clean accuracy next to attack success at every point, the configurations that did badly beside the one that did well. A full curve with three strategies at every point is a complete report, so there is nothing selective about it and nothing to defend.

**Do not claim a prediction you did not make.** Say what you measured and what it means. Do not write that we predicted a particular threshold, and do not present repair-aware selection as a hypothesis confirmed. We ran it as a comparison, so write it as a comparison. That is ordinary scientific writing, and the comparison is interesting on its own.

You do not need to explain in the paper how you arrived at each experiment. You do need to avoid claiming foresight you did not have.

---

## 7. Division of effort

Only Dan has pushed anything since 18 September. The controls, the scripts, and the MPS support were all his. That is good work, and it is also one person carrying the project with eight days left.

Chinh, the ANP checkpoint blocks all of Priority 2. Dat, the scaffold is needed on the 22nd and the serving table on the 23rd. Both of you please push something today, even if it is only a script that does not work yet and a note saying what failed.

---

## 8. The next eight days

I am asking you for more hours than you have been giving. I would rather say that plainly than hide it inside a schedule you cannot meet.

The reason is that you are closer than it looks. The harness is verified, the baselines are reproduced, the controls are clean, and the strongest experiment left is a set of inference runs your own data already suggests will work. What stands between this repository and a submitted paper is not cleverness and it is not compute. It is days, and we have eight.

A deadline is the one thing in research that does not negotiate. Reviewers will never see the version of this paper that needed one more week, for that version does not exist. The only version that exists is the one uploaded before the 29th.

So for the next five days, work harder than your normal commitment. Start earlier, finish later, and treat the freeze on the 23rd and the draft on the 26th as fixed. Push your work as you finish it rather than in the evening, for each of you is blocking somebody. Chinh's checkpoint blocks Dan's sweeps, Dan's figures block the Results section, and the scaffold blocks everyone on the 24th. A commit pushed at noon buys the team an afternoon.

Three practical things. Protect your sleep, for a tired reader of your own code is exactly the reader who accepts 15640.0 four times without asking why. Ask for help the hour you are stuck, not the next morning. And tell me early if something will not land, because a schedule I can adjust on the 23rd is worth far more than an apology on the 27th.

In return, the week after the 29th is yours. No tasks, no meetings, nothing to read. Take all of it and rest properly. A sprint is reasonable because it ends, and this one ends on a date we can all see. Working permanently at this pace produces worse research and worse researchers, so treat this as the exception it is, not as what I expect from you normally.

One last thing, and I mean it. Most students never finish a first paper. They stop at exactly the point you reached last week, where the first idea fails and the result is not what anyone hoped for. You did not stop. You ran the controls, you found your own negative result, you reported it honestly, and you asked what to do next. That is the part of research nobody can teach, and you already have it.

Finish the paper.
