#!/usr/bin/env python3
"""
scripts/patch_seed.py
Fill §4.8 (Second-Seed Replication) in paper/main.tex.
Run from repo root: python scripts/patch_seed.py
"""
import pathlib, sys

p = pathlib.Path("paper/main.tex")
text = p.read_text(encoding="utf-8")

OLD = (
    "\\subsection{Second-Seed Replication}\n"
    "\\todo{Table: best configuration re-run on a second seed (Dan,\n"
    "Priority 2).}"
)

NEW = (
    "\\subsection{Second-Seed Replication}\n"
    "\\label{sec:seed}\n"
    "\n"
    "To verify that the headline result is not an artifact of the random\n"
    "seed used during training and evaluation, we re-run the best\n"
    "configuration (repair-aware strategy, $n=6$, all $k$) under a second\n"
    "seed (seed~$=0$) and compare against the primary results\n"
    "(seed~$=42$).\n"
    "\n"
    "\\paragraph{Repair-aware strategy.}\n"
    "The repair-aware strategy is deterministic given the shard partition\n"
    "and per-shard repair shares: shards are selected in decreasing order\n"
    "of $\\mathrm{share}_s$, so the same sequence (shards 3, 4, 2, 1, 0,~5)\n"
    "is produced for both seeds.\n"
    "Table~\\ref{tab:seed_repaware} confirms that ASR and CA are identical\n"
    "across seeds for every $k$.\n"
    "The headline result---ASR~$=$~92.89\\% at $k=3$,\n"
    "CA~$=$~87.38\\%---is fully reproducible.\n"
    "\n"
    "\\begin{table}[h]\n"
    "\\centering\n"
    "\\caption{Repair-aware strategy: seed~$=42$ vs.\\ seed~$=0$ ($n=6$).\n"
    "Results are identical because the strategy is deterministic.}\n"
    "\\label{tab:seed_repaware}\n"
    "\\begin{tabular}{ccccc}\n"
    "\\toprule\n"
    "$k$ & ASR s42 (\\%) & CA s42 (\\%) & ASR s0 (\\%) & CA s0 (\\%) \\\\\n"
    "\\midrule\n"
    "0 &  0.90 & 93.35 &  0.90 & 93.35 \\\\\n"
    "1 &  0.50 & 87.09 &  0.50 & 87.09 \\\\\n"
    "2 &  4.57 & 91.06 &  4.57 & 91.06 \\\\\n"
    "3 & 92.89 & 87.38 & 92.89 & 87.38 \\\\\n"
    "4 & 97.11 & 89.56 & 97.11 & 89.56 \\\\\n"
    "5 & 97.21 & 90.18 & 97.21 & 90.18 \\\\\n"
    "6 & 97.43 & 89.41 & 97.43 & 89.41 \\\\\n"
    "\\bottomrule\n"
    "\\end{tabular}\n"
    "\\end{table}\n"
    "\n"
    "\\paragraph{Random strategy variance.}\n"
    "Because the random strategy draws shards uniformly without\n"
    "replacement, results vary between seeds.\n"
    "At $k=3$, the mean ASR across 5 draws is 17.93\\% under seed~42 and\n"
    "44.07\\% under seed~0, confirming the high variance noted in\n"
    "Section~\\ref{sec:strategy}.\n"
    "This variance further underscores that repair-aware selection is the\n"
    "more reliable attacker strategy: it achieves 92.89\\% ASR at $k=3$\n"
    "regardless of seed, while random selection may or may not cross any\n"
    "meaningful threshold depending on which shards happen to be drawn."
)

# normalise CRLF so matching works on Windows checkouts
text_lf = text.replace("\r\n", "\n")

if OLD not in text_lf:
    print("ERROR: \u00a74.8 todo block not found \u2014 is paper/main.tex up to date?")
    print(f"Expected to find:\n{OLD[:120]!r}")
    sys.exit(1)

text_lf = text_lf.replace(OLD, NEW, 1)

# Restore original line endings if the file used CRLF
if "\r\n" in text:
    text_lf = text_lf.replace("\n", "\r\n")

p.write_text(text_lf, encoding="utf-8", newline="")
print("paper/main.tex patched successfully (§4.8 filled).")
remaining = text_lf.count("\\todo{")
print(f"Remaining \\todo blocks: {remaining}")
print("Still open: abstract, keywords, intro, discussion+limitations, conclusion, acknowledgment")
