#!/usr/bin/env python3
"""
scripts/patch_sections.py
Fill §4.6 (ANP contrast) and §4.7 (Locality vs ASR) in paper/main.tex.
Run from repo root: python scripts/patch_sections.py
"""
import pathlib, sys

p = pathlib.Path("paper/main.tex")
text = p.read_text(encoding="utf-8")

# ── §4.6 ──────────────────────────────────────────────────────────────────────────────
OLD_46 = (
    "\\subsection{Contrast with a Local Repair (ANP)}\n"
    "\\todo{Repeat Sections~\\ref{sec:kcurve}--\\ref{sec:strategy} against the\n"
    "ANP-repaired checkpoint. Expected direction: ANP is more fragile to\n"
    "rollback than the global fine-tune -- report the actual result\n"
    "regardless of direction.}"
)

NEW_46 = (
    "\\subsection{Contrast with a Local Repair (ANP)}\n"
    "\\label{sec:anp}\n"
    "\n"
    "The ANP-repaired checkpoint achieves $\\text{CA}=83.03\\%$ and\n"
    "$\\text{ASR}=0.00\\%$ at $k=0$, a stronger initial repair than global\n"
    "fine-tuning ($\\text{ASR}=0.90\\%$).\n"
    "However, the $k$-shard rollback behaviour is qualitatively different.\n"
    "\n"
    "\\paragraph{Utility collapse at $k=1$.}\n"
    "Any single-shard substitution drops clean accuracy to approximately\n"
    "$10\\%$---the level expected from a uniformly random classifier on\n"
    "CIFAR-10---regardless of which shard is substituted.\n"
    "The mechanism is architectural: ANP bakes its pruning mask into the\n"
    "weight tensors by zeroing pruned neurons in the checkpoint.\n"
    "When an infected shard carrying full weights is spliced next to\n"
    "ANP shards whose neurons are zeroed, the activation signal becomes\n"
    "incompatible with the remainder of the network, causing the model\n"
    "to collapse to a single predicted class.\n"
    "\n"
    "\\paragraph{High ASR as a measurement artifact.}\n"
    "At $k=1$ when shard~5 (the linear classification head) is substituted,\n"
    "we observe $\\text{ASR}=81.10\\%$ alongside $\\text{CA}=10.01\\%$.\n"
    "This is not evidence of backdoor reactivation.\n"
    "The collapsed model predicts class~0 (the attack target,\n"
    "\\textit{airplane}) for every input; the ASR metric registers high\n"
    "success because the trigger also targets class~0.\n"
    "Unlike fine-tuned hybrids, which retain high clean accuracy while\n"
    "recovering ASR proportionally to the number of substituted shards,\n"
    "ANP hybrids collapse to random-chance clean accuracy at $k=1$.\n"
    "This utility collapse precedes any potential backdoor recovery,\n"
    "making shard substitution on ANP-defended models detectable through\n"
    "standard accuracy monitoring rather than trigger-based evaluation.\n"
    "\n"
    "\\paragraph{Harness verification.}\n"
    "At $k=6$ (full rollback), both repair strategies correctly reconstruct\n"
    "the original infected model: $\\text{ASR}=97.43\\%$, $\\text{CA}=89.41\\%$.\n"
    "This confirms that the evaluation harness is correct and that the\n"
    "collapse at $k<6$ is caused by the hybrid architecture, not by a\n"
    "pipeline error."
)

# ── §4.7 ──────────────────────────────────────────────────────────────────────────────
OLD_47 = (
    "\\subsection{Repair Locality vs.\\ Recovered ASR}\n"
    "\\todo{Figure: corrected locality metric (Section~\\ref{sec:share})\n"
    "plotted against recovered ASR, for both repairs, all shards (Chinh,\n"
    "Priority 2).}"
)

NEW_47 = (
    "\\subsection{Repair Locality vs.\\ Recovered ASR}\n"
    "\\label{sec:locality}\n"
    "\n"
    "Figure~\\ref{fig:locality_asr} plots each shard's repair share\n"
    "$\\sigma_s$ against the single-shard rollback ASR when that shard\n"
    "is substituted.\n"
    "\n"
    "\\begin{figure}[t]\n"
    "  \\centering\n"
    "  \\includegraphics[width=\\columnwidth]{figures/locality_vs_asr.pdf}\n"
    "  \\caption{Repair locality vs.\\ rollback vulnerability.\n"
    "    Each marker is one shard.\n"
    "    \\emph{Fine-tune} (circles): the two highest-share shards\n"
    "    ($\\sigma_3{=}47.74\\%$, $\\sigma_4{=}24.29\\%$) produce\n"
    "    single-shard ASRs of $0.50\\%$ and below; three shards must be\n"
    "    substituted together to cross the $90\\%$ ASR threshold\n"
    "    (Section~\\ref{sec:kcurve}).\n"
    "    \\emph{ANP} (triangles): shard~5 ($\\sigma_5{=}2.92\\%$) registers\n"
    "    $\\text{ASR}=81.10\\%$, but this is a utility-collapse artifact\n"
    "    ($\\text{CA}=10\\%$) rather than genuine backdoor recovery\n"
    "    (Section~\\ref{sec:anp}).}\n"
    "  \\label{fig:locality_asr}\n"
    "\\end{figure}\n"
    "\n"
    "For the fine-tuned model, repair share concentrates in shards~3 and~4\n"
    "yet their individual rollback ASRs remain below $9\\%$.\n"
    "No single shard, even the one absorbing nearly half the repair change,\n"
    "suffices to reactivate the backdoor.\n"
    "For the ANP-repaired model, all non-artifact ASR values are $0.00\\%$,\n"
    "not because the model is more robust but because utility collapses\n"
    "before any backdoor can surface.\n"
    "The figure therefore shows two distinct vulnerability regimes:\n"
    "a \\emph{threshold regime} under fine-tuning (requiring coordinated\n"
    "multi-shard substitution) and a \\emph{collapse regime} under ANP\n"
    "(detectable via clean-accuracy monitoring alone)."
)

# ── normalise CRLF so matching works on Windows checkouts ─────────────────
text_lf = text.replace("\r\n", "\n")

ok = True
for tag, old in [("\u00a74.6", OLD_46), ("\u00a74.7", OLD_47)]:
    if old not in text_lf:
        print(f"ERROR: {tag} todo block not found \u2014 is paper/main.tex up to date?")
        print(f"Expected to find:\n{old[:120]!r}")
        ok = False
if not ok:
    sys.exit(1)

text_lf = text_lf.replace(OLD_46, NEW_46, 1)
text_lf = text_lf.replace(OLD_47, NEW_47, 1)

# Restore original line endings if the file used CRLF
if "\r\n" in text:
    text_lf = text_lf.replace("\n", "\r\n")

p.write_text(text_lf, encoding="utf-8", newline="")
print("paper/main.tex patched successfully.")
remaining = text_lf.count("\\todo{")
print(f"Remaining \\todo blocks: {remaining}  (should be 5: abstract, keywords, intro, discussion/limitations, conclusion/ack)")
