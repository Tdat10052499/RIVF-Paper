# The Final Plan, 25 September 2026

**From:** Dang Khanh Hung
**To:** Dan, Chinh, Dat
**Ready version:** 29 September. **Official deadline:** 30 September, EDAS track SS3 (139851).

> **DECISION, 26 September (read Section 10 first).** The normalization check found a real problem and Chinh stopped, exactly as asked. Decision: **BackdoorBench normalization for every number in the paper.** No retraining of the seed-42 repair. Every result is re-evaluated under the new normalization today, and every number in the draft is provisional until those JSON files exist. Details, order of work, and the revised timeline are in Section 10.

This note replaces the 21 September plan. Read it in full once, then work from Sections 3 and 4. My line-by-line comments on the draft are inside `paper/main.tex` as lines beginning `%%Hung:`. Each one tells you what to change and why.

---

## 1. Where we stand

You did a great deal in four days, and most of it is right. I checked every number in the draft against the raw JSON files.

| Item | State |
|---|---|
| Draft compiles | Yes. Exactly 6 A4 pages, PDF 1.6, no undefined references, no overfull boxes. About three quarters of page 6 is empty, so there is room to add text. |
| Fine-tune results | Valid. Lineage check passes (cosine 0.92 to 0.998 in every shard). Repair-aware selection restores 92.89% ASR at 87.38% CA with three shards; architectural needs five; random averages 17.93% at k=3. Every subset containing both layer2 and layer4 restores at least 74.76%. All verified. |
| ANP results | Invalid. The ANP checkpoint came from a different BadNets model (cosine 0.02 at conv1, `results/raw/lineage/infected_vs_anp_fixed_OLD.json`). The "utility collapse" was two unrelated networks being joined. Chinh found this himself, which is exactly what an audit is for. The ANP switch in the paper is off, so the compiled draft carries no ANP result. |
| Second seed | Only a determinism check. Repair-aware selection is deterministic, so re-running it under seed 0 could not have disagreed. The repair itself has one seed. Section III-G of the draft already says this correctly; the Introduction does not. |
| Serving comparison | Valid. 848 versus 814 bytes, 132 versus 133 ms, 30 repetitions per cell, matches the raw JSONL. |

The paper as compiled is honest and submittable. What remains is a set of factual errors in the prose that contradict the data, a few results worth adding if they land on time, and the submission itself.

---

## 2. Chinh's request: approved, in this order

Chinh's fix guide asked for a one-day exception to the freeze. Granted. The paper is already valid without any of this, so the downside is bounded, but the order matters and the cutoff is hard.

**Cutoff: 20:00 Vietnam time, 26 September.** A result that has not passed its check by then does not enter the paper. Both switches stay off and we ship what we have.

1. **Normalization check first. Ten minutes. Not optional.** Run Chinh's step 2. If the infected model's CA and ASR move by less than 0.5 points between the two normalizations, keep `legacy` everywhere, add one sentence to Metrics saying so, and move on. If they move by more, **stop and message me immediately.** Do not re-run the fine-tune on your own, for that changes every number in the paper and I need to decide whether we retrain or add a sentence. I will answer within the hour.
2. **Second repair seed.** Fine-tune with seed 0, same settings, about one hour on the T4. This is the most valuable hour of the day, for it turns the headline number from one measurement into a replicated one. Commit the training script you use.
3. **All 63 subsets on finetune seed 42, then seed 0.** Five minutes each. Check the sanity rows before trusting the file: full rollback must equal the infected model, and the 40 subsets we already have must match exactly.
4. **ANP re-run, last.** Follow Chinh's step 3. It must pass `check_lineage.py` with the verdict "same lineage" and the bake cross-check must print 0 differing tensors. If either fails, do not use it and do not spend more time on it. Rename the old ANP files `*_INVALID_wrong_base`; do not delete them.

Push each JSON the moment it exists. Dan needs them for the figures.

---

## 3. What must change in the draft

Every item below is also marked in `main.tex` with a `%%Hung:` comment at the exact line. Fix the item, then delete that comment line. If you disagree or cannot do it, leave the comment and add a line `%%Hung-reply:` underneath saying why. Do not leave a comment silently unresolved.

**Errors that contradict our own data. Fix these first.**

1. Introduction, second paragraph: the sentence about Adversarial Neuron Pruning describes the invalid checkpoint and is in the compiled PDF because it sits outside the switch. Delete it. (Dan and Dat)
2. Introduction, same paragraph: "a result that replicates exactly across two independent random seeds" is false. Delete it. If the seed-0 repair lands and the switch is on, replace it with the measured number; otherwise say nothing about replication here. (Dan and Dat)
3. Introduction, roadmap paragraph: promises "ANP-contrast results" and "a second-seed replication" unconditionally. Wrap the first in the switch and change the second to "a determinism check". (Dan and Dat)
4. Results III-A: "our re-trained checkpoints" is false; the infected model is BackdoorBench's published checkpoint. (Dan)
5. Results III-B: "clean accuracies between 84.58% and 93.26%" is wrong for "all partial rollback configurations". Across everything you evaluated, hybrid CA runs from 73.55% to 93.26%. Either scope the sentence to single-shard hybrids or state the true range. Fix the Table II column heading to match. (Dan)
6. Figure 1 and III-C: shards 1 and 4 are marked "not tested". They were tested. Shard 1 gives 1.29% ASR at 90.95% CA; shard 4 gives 8.08% at 90.52%. Put the bars in, delete the "n.t." labels and sentences, and change "four shards tested in isolation" to "all six". (Dan)
7. III-E: "strictly most efficient" is not true; the random draw {2,4} reaches 74.76% at k=2. Write "the most efficient of the three ordered strategies". (Dan)
8. Table IV caption: delete "pending 23/09 freeze". Also delete the stale comment block above the serving paragraph. (Dat)

**Things a reviewer will ask about.**

9. Serving section: state the hardware the timings came from, say once that "signature" is an HMAC-SHA256 keyed-hash stand-in, and note in one clause that this run used n=3. (Dat)
10. III-F: the Spearman correlation needs a named script so it can be reproduced, or it comes out. The count "41 of the 63" must come from the same JSON that draws Figure 4; update it, the abstract, Limitations, and the "11" and "30" counts together once the all-63 run lands. (Dan, Chinh)
11. The 50% recovery threshold is used as if it were standard. Introduce it once, at first use, as this study's criterion. And it is "50% ASR", not "50 percentage points". (Dan)
12. Delete "rather than cherry-picking configurations". Never name a fault you are not committing; it makes the reader look for it. (Dan)

**Small.** "Fig~" missing its period in III-D. "confirming" to "indicating" in the Figure 1 caption. "underscoring that" to "which shows that" in III-E. Expand or drop the acronyms BAU, SAM, FST, BTI in Related Work. All marked inline.

**Leave to me.** The draft uses "--" and "---" as punctuation throughout. I will handle this in my editing pass. Do not spend time on it.

---

## 4. Schedule

| When (Vietnam time) | Who | What |
|---|---|---|
| 26/09, 08:00 | Chinh | Normalization check. Message me with the result either way. |
| 26/09, 09:00 to 20:00 | Chinh | Seed-0 repair, then all-63 subsets, then ANP, in that order. Push each result as it lands. |
| 26/09, all day | Dan | Items 4 to 7 and 10 to 12 above, plus the Introduction with Dat. Regenerate Figure 4 from the all-63 JSON when it arrives. |
| 26/09, all day | Dat | Items 8 and 9, the author block (Section 5), and the EDAS registration (Section 6). |
| 26/09, 20:00 | Chinh, Dan | Flip a switch to true only for a result that passed its check. Fill the `\todo{}` fields from the JSON, never by hand. Compile. Confirm 6 pages and zero red text. |
| 26/09, 23:00 | All | Complete draft pushed. Every `%%Hung:` comment resolved or replied to. |
| 27/09, morning | Hung | Editing pass one. Comments pushed by 13:00. |
| 27/09, by 22:00 | All | Revise against pass one. |
| 28/09, morning | Hung | Editing pass two. |
| 28/09, by 20:00 | All | Final revisions. Compile. Run the checklist in Section 6. |
| 29/09, by 20:00 | Dat | Upload the final PDF to EDAS. This is the ready version. We do not wait for the 30th. |
| 30/09 | | Buffer only. |

One rule for the whole schedule. Push as you finish, not at the end of the day. If I can start reading at 20:00 on the 26th instead of 23:00, you gain three hours of revision on the 27th.

---

## 5. Authorship and front matter

Decided: I join as the fourth and corresponding author. The block is already in `main.tex`, marked with a `%%Hung:` comment. Do not edit it.

- Author 4: Dang Khanh Hung, Faculty of Information Technology, Van Lang School of Technology, Van Lang University, Ho Chi Minh City, Vietnam, hung.dk@vlu.edu.vn, corresponding author.
- The "Supervised by" line is gone; it is replaced by the author block.
- The Acknowledgment now thanks an author. Delete it, or thank the university or faculty for support if that is true. Do not thank me.
- Check your own affiliation wording against the official faculty name; see the comment in the author block.
- On EDAS, enter all four authors and mark me as corresponding. Use hung.dk@vlu.edu.vn, not my Cogent address.

RIVF does not state a blind-review policy, so the paper is submitted with names and affiliations as they are.

---

## 6. Submission

**Register on EDAS on the 26th, not the 29th.** Dat creates the paper entry in track SS3 (139851), enters the title, abstract, keywords, and all authors, and uploads the current draft PDF as a placeholder. The final upload on the 29th is then a replacement of an existing entry, which takes two minutes, rather than a first-time registration under deadline pressure.

Before every upload, run this checklist and paste the output into your daily note:

```bash
cd paper && latexmk -pdf -interaction=nonstopmode main.tex
pdfinfo main.pdf | grep -E "Pages|Page size|PDF version"   # 6, A4 (595 x 842 pt), 1.6
pdffonts main.pdf | awk 'NR>2 && $4!="yes"'                # must print nothing: every font embedded
pdftotext main.pdf - | grep -c "TODO"                       # must print 0
grep -c "%%Hung:" main.tex                                  # must print 0 by the 28th
```

Keep `\documentclass[conference,a4paper]{IEEEtran}` and `\pdfminorversion=6` exactly as they are; both are RIVF requirements.

---

## 7. Rules that do not change

Report everything you ran, including the subsets and draws that did badly. Claim no prediction we did not make; the strategy comparison is a comparison, so write it as one. Every number in the paper comes from a JSON file in `results/raw/`, never from memory. One normalization for every number. Report ASR and CA together for every configuration, always.

---

## 8. Three days

You have done the hard part. The harness is verified, the result is real, and the paper exists. What remains is care: fixing the sentences that say more than the data does, adding the two results that make the headline stronger if they land, and submitting a day early.

Chinh, the audit you ran on your own work this week is the best thing anyone on this project has done. Finding your own invalid result before a reviewer does is the whole discipline in one act. Dan, your results sections are clear and your numbers are right; the errors I found are in sentences that outran the data, and they are quick to fix. Dat, the serving table is exactly the bounded artifact I asked for, and the EDAS registration on the 26th is now the single most important thing you own.

Keep pushing as you go. The week after the 30th is still yours.

---

## 9. Corrections to Chinh's 26/09 action items for Dan and Dat

Chinh's two action-item notes (`2026-09-26_dan.md`, `2026-09-26_dat.md`) are good and agree with this plan. Three details in them would introduce a new error if followed literally. Use these instead.

- **D3, suggested wording.** It says repair-aware selection "achieves the lowest ASR at each k". That is inverted. Repair-aware is the attacker's best ordered strategy, so it achieves the **highest** ASR at each k. Write "highest". The rest of the D3 fix, including the {2,4} example at 74.76%, is right.
- **T2, "n=3".** The n=3 in my comment means the serving run used the **three-shard partition**, while the rest of the paper uses six shards. It does not mean "averaged over n=3 forward passes". The run had 30 repetitions per cell, which the text already states. Add one clause saying the serving test used n=3 shards; do not add a sentence about three forward passes.
- **T1, hardware.** The template names an NVIDIA GPU. The serving timings were taken on the M2 MacBook, on CPU, one OS process per loader, exactly as the measurement rule required. State that. Do not name a GPU.
- **T2, Sigstore.** No new reference. Cite TUF and OMS, which are already in the bibliography, and say HMAC-SHA256 stands in for a production signing scheme.
- **T4.** Both questions are answered in Section 5 above: the paper is not blind, and I am the fourth and corresponding author. Do not wait on me for these; set up EDAS today.
- **T5.** Already resolved; the label is `sec:variance` and the PDF has no `??`.
- **D4.** Chinh is right that the Introduction's "CA stays above 86% in every hybrid configuration we test" is also false. I have marked that line inline.

Chinh, thank you for writing these. This is what a first author does.

---

## 10. Normalization: the decision and what changes

### 10.1 What Chinh found

The repaired model is insensitive to the choice of normalization (ASR moves 0.09 points, CA 0.17). The infected model is not: under the standard deviation our scripts have always used, (0.2023, 0.1994, 0.2010), it reads ASR 97.43% and CA 89.41%; under the one BackdoorBench trained it with, (0.247, 0.243, 0.261), it reads ASR 95.06% and CA 91.33%. Those are differences of 2.37 and 1.92 points, well past the 0.5 threshold.

Chinh stopped and reported instead of choosing on his own. That was the correct call, and it is why this problem is now a half-day of scripted work rather than a retraction.

### 10.2 The decision

Use BackdoorBench's normalization, (0.247, 0.243, 0.261), for every number in the paper. Three reasons, in order of weight.

First, the infected model is the published artifact, and its native normalization is the one under which its published numbers hold. Evaluated that way it reads 91.33% CA and 95.06% ASR, which is what BackdoorBench reports for this checkpoint. Section III-A can then say that we reproduce the published numbers, which is true and which a reviewer can check. Evaluated the other way we are reporting a slightly damaged version of someone else's model and calling it the baseline.

Second, the repaired model does not care. A 0.17-point change is inside the confidence half-width we already state in Metrics. So switching costs us nothing on the repaired side, whereas staying costs two points of distortion on the infected side. There is no trade-off here.

Third, it removes a confound from every hybrid. Each hybrid mixes infected shards with repaired shards. Under the old normalization the infected shards were being fed inputs scaled about twenty percent away from what they were trained on. Under the new one they are not, and the repaired shards are insensitive either way. The hybrids are therefore cleaner under the new normalization, not merely re-labelled.

We do not retrain the seed-42 repair. Its insensitivity is the evidence that retraining would change nothing measurable, and we do not have the day.

### 10.3 What to do, in order

**Chinh, first.** Open the 14 September Kaggle notebook and read which `Normalize` it used for the fine-tune. Write the answer, with the exact standard deviation, into `data/checkpoint_manifest.md` under the repaired checkpoint. Push it with the two normcheck JSON files, which are not in the repository yet; raw results are append-only and they must be committed. Ten minutes.

**Chinh, second.** Re-evaluate everything under `--norm backdoorbench`: all 63 subsets for the seed-42 repair, into `results/raw/all_subsets/finetune_s42_bb_n6.json`. Check the sanity rows before trusting it: full rollback must read 95.06 and 91.33, and k=0 must read the repaired model within 0.2 of 0.90 and 93.35. Push it the moment it passes. This unblocks Dan and it is the single most urgent file of the day.

**Chinh, third.** Train the seed-0 repair with `--norm backdoorbench`, as `finetune_repair.py` already expects. This was already the plan; it now also serves as the clean-normalization control. Then evaluate its 63 subsets the same way. If seed 0, trained and evaluated under the native normalization, reproduces the k=3 threshold and the layer2-plus-layer4 rule that seed 42 shows, we have replicated across repair seeds and shown the training normalization does not drive the result in one run.

**Chinh, last, only if the above is done and pushed before 18:00.** ANP, per your own step 3, evaluated under the same normalization. Same stop rule as before.

**Dan.** Do not touch any sentence that carries a number until `finetune_s42_bb_n6.json` is pushed. Work on the non-numeric items from Section 3 in the meantime: the deleted Introduction sentences, the roadmap, the wording fixes, the acronyms. When the file lands, regenerate every figure and re-derive every number from it. Figures 1, 2 and 3 have coordinates typed by hand into `main.tex`. Do not retype them. Write a short script in the pattern of `make_locality_pgf.py` that emits the three coordinate blocks from the JSON, and `\input` them. We have typed numbers by hand four times in this project and been wrong three of those times.

**Dat.** Nothing changes for you. The serving numbers do not depend on normalization. Finish EDAS registration today.

### 10.4 What the paper says about it

One sentence in Metrics: "All models are evaluated with BackdoorBench's input normalization (per-channel standard deviation 0.247, 0.243, 0.261)."

Then one of two sentences in Setup, depending on what Chinh finds in the notebook.

- If the fine-tune used BackdoorBench's normalization: nothing more. Training and evaluation match.
- If it used the other one: "The seed-42 repair was fine-tuned under a slightly different input scaling (standard deviation 0.2023, 0.1994, 0.2010); the repaired model's accuracy changes by less than 0.2 points between the two, so all evaluation uses the checkpoint's native normalization." That is the whole disclosure. It is honest, it is one sentence, and the seed-0 repair then demonstrates the point empirically.

Remove "CA even rises by 3.94 points" and let the new numbers say what they say; the gain against 91.33% will be about two points.

### 10.5 Timeline

Every number in the draft is provisional until the new JSON exists, so the complete-draft target moves by half a day.

| When (Vietnam time) | What |
|---|---|
| 26/09, by 10:00 | Chinh: notebook answer, manifest, normcheck JSONs pushed. |
| 26/09, by 12:00 | Chinh: `finetune_s42_bb_n6.json` pushed and sanity-checked. Dan starts re-deriving. |
| 26/09, by 18:00 | Chinh: seed-0 repair trained and its 63 subsets pushed. ANP only after this. |
| 26/09, by 23:00 | Dan: all figures regenerated by script, all numbers re-derived, second reader (Chinh) has re-checked ten numbers at random against the JSON. |
| 27/09, by 10:00 | Complete draft pushed. Every `%%Hung:` comment resolved or replied to. |
| 27/09, afternoon | My editing pass one. |
| 28/09 | My pass two in the morning; your final revisions by 20:00. |
| 29/09, by 20:00 | Final PDF on EDAS. Unchanged. |

If the seed-42 re-evaluation moves the headline, for example the threshold shifts from k=3 to k=2 or k=4, that is the result and we report it. Do not go looking for the normalization that gives the nicer number. We chose the normalization on principle in 10.2, before seeing the hybrid numbers, and that is the only order in which this choice is defensible.

---

## 11. 26 September, afternoon: the new numbers, the new story, and who writes what

Chinh delivered everything in Section 10 by midday: the normcheck files, the 63-subset evaluation of seed 42 under BackdoorBench normalization (sanity 95.06 / 91.33, exact), and a second repair, seed 0, trained and evaluated under the same normalization. Both files are in `results/raw/all_subsets/`. That is the whole critical path, done on time. Thank you.

### 11.1 What changed

The numbers moved, and the story is different from the one in the draft. The single-shard maximum is 5.36% (seed 42) and 16.40% (seed 0). The greedy repair-aware attacker reaches 56% and 81% at three shards, not 92.89%, and 92.3% and 95.8% at four shards with clean accuracy within 2.3 points of the repaired model. The sharp threshold at k=3 is gone. What replaces it is better, for it replicates across two independent repairs: every hybrid above 50% ASR contains layer4, layer3 (48% of the repair) is dispensable, repair share predicts ASR only weakly, and the two repairs agree on the 50% classification of 60 of 64 subsets (Pearson r = 0.926).

Every number the paper needs, for both seeds, is in `results/analysis/2026-09-26_hung_digest.md`, computed by script from the two JSON files. Section 10 of that page maps each old number-bearing sentence to its replacement. Work from it. Do not work from memory and do not work from Chinh's `seed_replication.md`, which has one estimated value marked with an asterisk; the JSON has the real one.

### 11.2 Who writes what, from now until the draft

I have taken the narrative sections, for they had to change together and I had the numbers first. Pull before you touch anything.

**Done by me, in `main.tex`, this afternoon.** Abstract. Introduction, all four paragraphs. Discussion. Limitations. Conclusion. The Setup sentences describing the two repairs and the normalization disclosure. The Metrics sentence naming the normalization. The Acknowledgment is removed, since an author cannot thank himself; add one thanking the university if you wish. Do not re-derive anything in those sections. If you find an error in them, fix it and tell me, but do not restructure them.

**Dan, today.** Results III-A to III-G, from the digest. Baseline table with both repairs. Sanity checks with the true CA ranges. Figure 1 with all six shards and both seeds. Figure 2 and Figure 3 from the digest's greedy, architectural, and exact-mean rows; the "random" line is now the exact mean over all C(6,k) subsets, so say that and drop the sampling-variance text. Section III-F from the digest's Section 7, with the Spearman values 0.33 and 0.41 and the layer4 rule replacing the layer2-plus-layer4 rule. Section III-G with the seed-0 replication numbers, then set `\repairseedtrue`. Generate every coordinate block by script from the JSON, as I asked in Section 10; the digest tells you which rows.

**Chinh, today.** Second reader for every number Dan writes: pick fifteen at random and re-derive them from the JSON. Then, and only then, ANP under the stop rule, evaluated under the same normalization. If it lands, fill the `\ifincludeanp` slots in my sections from measured numbers; they are marked with `\todo`.

**Dat, today.** EDAS registration with four authors, me as corresponding. Then read the whole paper once as a stranger and list every sentence you do not understand.

### 11.3 The one sentence not to write

Layer2 is necessary for recovery under seed 42 and not under seed 0. Do not write that both layer2 and layer4 are required as a general claim. Write that layer4 is necessary in both repairs and that layer2 is its usual partner. The digest, Section 7, has the exact numbers behind this.

### 11.4 Timeline

Unchanged from Section 10.5: complete draft by 10:00 on the 27th, my first pass that afternoon, second pass on the 28th, final PDF on EDAS by 20:00 on the 29th.
