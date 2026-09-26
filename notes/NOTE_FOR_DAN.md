# RIVF Paper — Status Note for Duong Ngoc Linh Dan

> **As of 27 Sep 2026, ~10 PM — YOUR ITEMS ARE BLOCKING SUBMISSION**

Hey Dan, three things are blocking the final submission. All three are yours. Please read carefully.

---

## Current Repo State

- HEAD: `5ecbbbb` (Chinh). PDF is **6 pages, clean**.
- Dr. Hung rewrote Abstract, Introduction, Discussion, Limitations, Conclusion on 26 Sep.
- Your Repair-Share Metric section (Sec II-D) is in and correct.
- The **ANP section is fully gated off** (`\includeanpfalse`) — waiting for your `anp_v2_n6.json`.
- Fig 2 (k-curve) renders from **hardcoded inline data** — your replacement files never landed.
- Fig 4 (locality scatter) is **factually wrong** — 41 subsets in the data, 63 claimed in the caption.

---

## 🚨 Item 1 — Push `paper/fig_kcurve_asr_data.tex` and `paper/fig_kcurve_ca_data.tex`

Your commit `e1704a0` deleted `fig_kcurve_data.tex` with the message:
> *"Remove unused fig_kcurve_data.tex (replaced by fig_kcurve_asr_data.tex and fig_kcurve_ca_data.tex)"*

**Neither replacement file was ever pushed.** The repo has no k-curve data files right now. Push both to `paper/`.

---

## 🚨 Item 2 — Regenerate `paper/fig_locality_data.tex` with 63 subsets

The current file has **41 subsets**. The paper caption says **"all 63 non-empty subsets"**. This is a factual error that reviewers will catch.

Regenerate from **both JSON files** using **BackdoorBench normalization (std = 0.247, 0.243, 0.261)**:

- `results/raw/all_subsets/finetune_s42_bb_n6.json`
- `results/raw/all_subsets/finetune_s0_bb_n6.json`

Run your `scripts/make_locality_pgf.py` (or equivalent) with both seeds. Confirm the output has **63 coordinate pairs per series**. Push the regenerated `paper/fig_locality_data.tex`.

---

## ⚠️ Item 3 — Push `anp_v2_n6.json`

This unlocks four places in the paper that are currently gated off:
- Sec III-E (ANP contrast — full paragraph)
- A Discussion paragraph
- A Limitations sentence
- A Conclusion sentence

The four LaTeX fill commands waiting for your data:

| Command | Meaning |
|---|---|
| `\ANPthr` | Selected pruning threshold |
| `\ANPpruned` | Number of pruned BN neurons (out of 3,392) |
| `\ANPca` | ANP-repaired clean accuracy (%) |
| `\ANPasr` | ANP-repaired ASR (%) |

Push to `results/raw/all_subsets/anp_v2_n6.json` (or wherever `eval_kshard_anp.py` outputs it), and Chinh will flip `\includeanpfalse` → `\includeanptrue`, fill the numbers, recompile, and push.

*(For reference: Chinh's Kaggle preliminary run gave threshold=0.55, 404/3392 neurons, CA=83.03%, ASR=0.57% — but the paper needs your full subset sweep results, not the Kaggle run.)*

---

## After You Push

**Ping Chinh immediately.** He will `git pull`, compile (pdflatex → bibtex → pdflatex → pdflatex), verify, and push the updated PDF. Do not push partial work without telling him — the compile chain must run after every data file change.

---

## Your Section — What to Check

Pull and search `main.tex` for `%%Hung:` near your Repair-Share Metric section (Sec II-D). Dr. Hung's editing pass runs 27–28 Sep. Address any markers before 29 Sep.

---

## What's NOT Your Problem Right Now

- `fig_strategy_data.tex` — pushed, handled by Chinh later.
- `fig_singleshard_data.tex` — pushed and wired in already.
- Serving Comparison (Sec III-G) — that's Dat's section.

---

**Deadline: 29 Sep. Hung submits. Items 1 and 2 are needed before the final compile.**
