# Status Note for Dương Ngọc Linh Đan
**Updated: 27 Sep 2026 — by Chinh (via Claude)**

---

## ✅ What You Did Right — kcurve files confirmed GOOD

Your commit `f81e06` pushed **fig_kcurve_asr_data.tex** and **fig_kcurve_ca_data.tex** — both were checked line by line. Numbers are correct:

| k | s42 ASR | s0 ASR | s42 CA | s0 CA |
|---|---|---|---|---|
| 0 | 0.81 | 1.13 | 93.18 | 93.51 |
| 1 | 0.40 | 0.39 | 86.76 | 86.78 |
| 2 | 1.63 | 11.34 | 90.74 | 90.49 |
| 3 | 56.42 | 81.11 | 89.04 | 89.93 |
| 4 | 92.30 | 95.82 | 91.13 | 91.20 |
| 5 | 93.41 | 93.50 | 91.54 | 91.55 |
| 6 | 95.06 | 95.06 | 91.33 | 91.33 |

Endpoints match known values (k=0 = fine-tune result, k=6 = infected baseline). Greedy order [3,4,2,1,0,5] is correct. These files are ready to wire in.

---

## ❌ BLOCKING #1 — fig_locality_data.tex is STILL WRONG

**You did not update this file.** Its SHA on `main` is still `9cdb5b4` — unchanged from before your commit.

The problem:
- The file header says **"41 subsets"**
- It has **30 blue points + 11 red points = 41 data points total**
- The paper caption says **63 subsets** — this is a factual error that reviewers will catch

What you need to do:
1. **Re-run `scripts/make_locality_pgf.py`** using **both** `finetune_s42_bb_n6.json` AND `finetune_s0_bb_n6.json` as sources, with BackdoorBench normalization (std = 0.247, 0.243, 0.261)
2. The combined run over all 2^6 = 63 non-empty subsets of 6 shards should produce **63 data points**
3. Push the regenerated `paper/fig_locality_data.tex` to `main`

The caption in `main.tex` currently reads "across all $2^6 - 1 = 63$ non-empty subsets" — the data file must match this claim. If the script only produced 41 subsets, check whether it is reading both seed JSONs or only one, and whether the subset enumeration is complete.

**This is the last factual error blocking submission.**

---

## ❌ BLOCKING #2 — anp_v2_n6.json is STILL MISSING

The ANP results section in `main.tex` is currently gated behind `\includeanpfalse` — it produces no output in the PDF. To unlock it, you need to push `paper/anp_v2_n6.json`.

Once it exists, Chinh will:
- Flip `\includeanpfalse` → `\includeanptrue`
- Fill in the four macros from your JSON:
  - `\ANPthr` (threshold used, e.g. 0.55)
  - `\ANPpruned` (number of neurons pruned, e.g. 404 out of 3392)
  - `\ANPca` (clean accuracy after ANP repair)
  - `\ANPasr` (ASR after ANP repair)

From a previous Kaggle run the placeholders are: threshold=0.55, pruned=404/3392, CA=83.03%, ASR=0.57% — but these need to be confirmed from your canonical `anp_v2_n6.json`, not assumed.

**Push `paper/anp_v2_n6.json` to `main` as soon as it is ready.**

---

## Summary — What You Still Need to Push

| File | Status | Priority |
|---|---|---|
| `paper/fig_locality_data.tex` | ❌ Regenerate with 63 subsets | 🔴 Critical |
| `paper/anp_v2_n6.json` | ❌ Missing entirely | 🟠 High |

Camera-ready deadline is **29 Sep 2026**. Please push both as soon as possible so Chinh can do the final combined recompile.
