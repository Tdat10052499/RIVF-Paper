# RIVF Paper — Status Note for Ho Du Tuan Dat

> **As of 27 Sep 2026, ~10 PM**

Hey Dat, here's everything you need to know when you're back.

---

## Current Repo State

- HEAD: `5ecbbbb` (Chinh's commit today). Compiled PDF is **6 pages, clean, pushed**.
- All four figures render. Citations [1]–[16] resolved. No visible `\todo{}` markers.
- Fig 1 now pulls from `fig_singleshard_data.tex` (Chinh wired it in today).
- Dr. Hung rewrote Abstract, Introduction, Discussion, Limitations, Conclusion on 26 Sep.

---

## Your Section — Serving Comparison (Sec III-G)

Your section is in and correct. The numbers in the paper:

- Infected model: **814 bytes** per request
- Repaired model: **848 bytes** per request
- Inference latency (infected): **133.4 ± 3.1 ms**
- Inference latency (repaired): **132.0 ± 3.8 ms**
- Recovery overhead: **148.4 ± 5.3 ms** (n=30)

No action needed unless Hung's editing pass touches it.

---

## What to Check When You Pull

1. `git pull` as soon as you're back.
2. Open the compiled PDF, read Sec III-G with fresh eyes — confirm numbers match your measurements.
3. Search `main.tex` for `%%Hung:` — Dr. Hung may have left comment markers near your section during his 27–28 Sep editing pass. Address any you find before 29 Sep.

---

## One Pending Item — `fig_strategy_data.tex` (not urgent yet)

Dan pushed this file (commit `0e9f20c`) and it's in the repo, but it is **not wired into Fig 3 yet**. Before it can be `\input{}`-ed, two things need fixing:

1. **Missing endpoints:** The data file covers k=1..5 only. The inline code includes k=0 (repaired model ASR: seed 42 = 0.81%, seed 0 = 1.13%) and k=6 (full rollback = 95.06%). These need to be added.
2. **Legend label mismatch:** Data file says `"Repair-aware, seed~42"` / `"Mean over $\binom{6}{k}$, seed~42"` but inline code uses `"Repair-aware (s42)"` / `"Exact mean (s42)"`. These need to match before the swap.

This will be handled during the post-Dan recompile pass. Flag it if you want to fix the data file endpoints yourself now.

---

## What's Blocking Submission (not your responsibility)

Dan has three outstanding items — see her note (`notes/NOTE_FOR_DAN.md`). Once she pushes, Chinh does the final compile and PDF push.

---

## Compile Sequence (if you need to recompile)

```powershell
cd D:\RIVF-Paper\paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Then commit and push from PowerShell — Windows Credential Manager handles auth, no token needed.

---

## Camera-Ready Reminders (do on 29 Sep, not now)

The IEEEtran compile log flags two things:
1. **Manually equalize column lengths** on the last page before final submit.
2. **Ensure all fonts are Type 1** in the PDF output.

---

**Deadline: 29 Sep. Hung submits.**
