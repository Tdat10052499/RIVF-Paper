#!/usr/bin/env python3
"""
scripts/patch_final.py
Fill abstract, keywords, discussion+limitations, conclusion, acknowledgment.
Run from repo root: python scripts/patch_final.py
"""
import pathlib, sys

p = pathlib.Path("paper/main.tex")
text = p.read_text(encoding="utf-8")
text_lf = text.replace("\r\n", "\n")

# ============================================================
# ABSTRACT
# ============================================================
OLD_ABSTRACT = (
    "\\todo{Write LAST, on 26/09, after every number below is frozen (23/09\n"
    "freeze). Should state: (1) the setting -- distributed edge inference\n"
    "with independently-signed model shards; (2) the attack -- an artifact\n"
    "cache that can serve a mix of repaired and historically-valid\n"
    "(pre-repair) shards; (3) the headline empirical result -- single-shard\n"
    "rollback alone is weak (max ASR 17.46\\% vs.\\ 97.43\\% for the fully\n"
    "infected model) but is invisible to utility monitoring (clean accuracy\n"
    "stays within a few points of normal), and recovery grows with the\n"
    "number of stale shards and with how much of the repair update they\n"
    "carry; (4) the defense -- epoch-manifest pinning, framed as applying\n"
    "existing supply-chain controls (TUF/Uptane) to this ML-specific gap,\n"
    "not as a new protocol.}"
)

NEW_ABSTRACT = (
    "We study shard-version skew as an attack surface in distributed edge\n"
    "inference: a setting in which a model is partitioned into independently\n"
    "signed shards that may be cached and served by separate workers during\n"
    "a rolling update.\n"
    "An attacker who retains a validly signed but pre-repair shard can\n"
    "silently introduce it into an otherwise-repaired deployment, producing\n"
    "a hybrid model without triggering per-shard signature checks.\n"
    "We measure the ML-specific consequence of this gap using BadNets on\n"
    "CIFAR-10 with PreActResNet18, partitioned into six shards, after two\n"
    "representative repairs: global clean fine-tuning and Adversarial\n"
    "Neuron Pruning (ANP).\n"
    "Under fine-tuning, single-shard rollback is weak---the highest\n"
    "single-shard attack success rate (ASR) is 8.94\\%---yet completely\n"
    "invisible to utility monitoring: clean accuracy stays above 86\\% in\n"
    "all hybrid configurations.\n"
    "A repair-aware attacker substituting the three highest-share shards\n"
    "restores ASR to 92.89\\% while maintaining CA~$=$~87.38\\%, a result\n"
    "that replicates exactly across two independent random seeds.\n"
    "Under ANP, any single-shard substitution causes utility collapse\n"
    "(CA~$\\approx$~10\\%) rather than backdoor recovery, making tampering\n"
    "detectable through standard accuracy monitoring.\n"
    "Epoch-manifest pinning---already specified in TUF and Uptane---closes\n"
    "the attack surface with 34 additional bytes of manifest overhead and\n"
    "no measurable per-load verification cost."
)

# ============================================================
# KEYWORDS
# ============================================================
OLD_KEYWORDS = (
    "\\todo{4--6 keywords, e.g.\\ backdoor attacks, model partitioning, edge\n"
    "inference, supply-chain security, version skew.}"
)

NEW_KEYWORDS = (
    "backdoor attacks, model partitioning, distributed edge inference,\n"
    "supply-chain security, version skew, shard rollback"
)

# ============================================================
# DISCUSSION + LIMITATIONS  (one contiguous block)
# ============================================================
OLD_DISCUSSION = (
    "\\section{Discussion}\n"
    "\\label{sec:discussion}\n"
    "\\todo{Tie results together: single-shard rollback is weak but silent;\n"
    "multi-shard repair-aware rollback is the real attack surface;\n"
    "epoch-manifest pinning closes the gap without a new protocol.}\n"
    "\n"
    "\\subsection{Limitations}\n"
    "\\todo{One paragraph: single architecture (PreActResNet18), single\n"
    "dataset (CIFAR-10), BadNets attack, two repair methods only. Name\n"
    "fine-pruning, NAD, 1-epoch fine-tune, other partitions/architectures\n"
    "as explicit future work in one clause.}"
)

NEW_DISCUSSION = (
    "\\section{Discussion}\n"
    "\\label{sec:discussion}\n"
    "\n"
    "Our results reveal two qualitatively distinct vulnerability regimes\n"
    "under shard-version skew, determined by the repair method.\n"
    "\n"
    "\\paragraph{Single-shard rollback is weak but silent.}\n"
    "Under global fine-tuning, no individual shard rollback restores the\n"
    "backdoor above 9\\% ASR, even when the substituted shard carries nearly\n"
    "half of the total repair update ($\\sigma_3{=}47.74\\%$,\n"
    "ASR~$=$~0.50\\%).\n"
    "The repair is distributed across the network in a way that no single\n"
    "shard can undo.\n"
    "Critically, this weakness does not make the threat benign: hybrid\n"
    "models retain CA above 86\\% throughout, so standard utility monitoring\n"
    "provides no signal that a stale shard has been accepted.\n"
    "The threat requires detection at the artifact layer, not the inference\n"
    "layer.\n"
    "\n"
    "\\paragraph{Coordinated multi-shard rollback is the real attack\n"
    "surface.}\n"
    "A repair-aware attacker who substitutes the three highest-share shards\n"
    "crosses a sharp threshold (ASR~$=$~92.89\\% at $k{=}3$, up from\n"
    "4.57\\% at $k{=}2$), matching the fully infected model's 97.43\\%\n"
    "within one further shard.\n"
    "Architectural selection---requiring only knowledge of the partition\n"
    "boundaries, not of the repair update---crosses the same threshold at\n"
    "$k{=}5$, confirming that the attack does not require privileged\n"
    "knowledge of repair internals.\n"
    "\n"
    "\\paragraph{ANP creates a self-revealing collapse regime.}\n"
    "Shard substitution on an ANP-repaired model destroys utility before\n"
    "the backdoor can recover.\n"
    "The architectural incompatibility between the baked-in pruning mask\n"
    "and the full weights of a pre-repair shard makes tampering immediately\n"
    "detectable through CA monitoring alone---a favorable signal for\n"
    "defenders---but both repair strategies are fully vulnerable to\n"
    "complete rollback at $k{=}6$.\n"
    "\n"
    "\\paragraph{Epoch-manifest pinning closes the gap.}\n"
    "Both vulnerability regimes share the same root cause: the artifact\n"
    "pipeline enforces that each shard is authentic but not that all shards\n"
    "belong to the same repair epoch.\n"
    "Epoch-manifest pinning, as defined in TUF~\\cite{tuf} and\n"
    "Uptane~\\cite{uptane}, binds each shard to a per-epoch identifier in\n"
    "the signed snapshot metadata; a loader that checks this identifier\n"
    "rejects a stale shard as epoch-mismatched rather than accepting it as\n"
    "individually valid.\n"
    "Our serving comparison (Section~\\ref{sec:serving}) confirms that this\n"
    "protection adds 34 bytes of manifest overhead and no measurable\n"
    "per-load verification cost.\n"
    "The defense is an application of existing supply-chain controls to a\n"
    "previously unmeasured ML-specific gap.\n"
    "\n"
    "\\subsection{Limitations}\n"
    "\n"
    "This study evaluates a single architecture (PreActResNet18) on a\n"
    "single dataset (CIFAR-10) with a single attack pattern (BadNets,\n"
    "visible patch trigger, 10\\% poison rate) and two repair methods;\n"
    "fine-pruning, Neural Attention Distillation, short-epoch fine-tuning,\n"
    "other architectures (ResNet-50, ViT), larger datasets, non-patch\n"
    "triggers (blended, WaNet), and non-block-aligned shard partitions\n"
    "are left as explicit future work."
)

# ============================================================
# CONCLUSION
# ============================================================
OLD_CONCLUSION = (
    "\\section{Conclusion}\n"
    "\\label{sec:conclusion}\n"
    "\\todo{Restate the claim in 3--4 sentences: what was measured, headline\n"
    "numbers (once frozen), practical takeaway (epoch-manifest pinning as\n"
    "an existing control). No new numbers.}"
)

NEW_CONCLUSION = (
    "\\section{Conclusion}\n"
    "\\label{sec:conclusion}\n"
    "\n"
    "We measured the attack surface created by shard-version skew in\n"
    "distributed edge inference, where a validly signed but pre-repair\n"
    "shard can be silently introduced into an otherwise-repaired deployment.\n"
    "Against a globally fine-tuned model partitioned into six shards,\n"
    "single-shard rollback is too weak to restore the backdoor\n"
    "(max ASR~$=$~8.94\\%) yet completely invisible to utility monitoring,\n"
    "while repair-aware three-shard rollback recovers\n"
    "ASR~$=$~92.89\\% at CA~$=$~87.38\\%---a result that replicates exactly\n"
    "across two random seeds.\n"
    "Against an ANP-repaired model, any single-shard substitution causes\n"
    "utility collapse (CA~$\\approx$~10\\%) before the backdoor can recover,\n"
    "making tampering detectable through standard accuracy monitoring.\n"
    "Epoch-manifest pinning---already specified in TUF and Uptane---eliminates\n"
    "the attack surface by binding each shard to a repair epoch, adding\n"
    "only 34 bytes of manifest overhead and no measurable per-load cost,\n"
    "and should be adopted as a baseline control wherever model shards are\n"
    "distributed through artifact caches."
)

# ============================================================
# ACKNOWLEDGMENT
# ============================================================
OLD_ACK = (
    "\\section*{Acknowledgment}\n"
    "\\todo{Standard RIVF acknowledgment line, if applicable. Cut first if\n"
    "paper runs over 6 pages.}"
)

NEW_ACK = (
    "\\section*{Acknowledgment}\n"
    "The authors thank Dr.\\ Dang Khanh Hung for supervision and guidance\n"
    "throughout this project."
)

# ============================================================
# Apply all patches
# ============================================================
patches = [
    ("Abstract",     OLD_ABSTRACT,    NEW_ABSTRACT),
    ("Keywords",     OLD_KEYWORDS,    NEW_KEYWORDS),
    ("Discussion",   OLD_DISCUSSION,  NEW_DISCUSSION),
    ("Conclusion",   OLD_CONCLUSION,  NEW_CONCLUSION),
    ("Acknowledgment", OLD_ACK,       NEW_ACK),
]

ok = True
for name, old, _ in patches:
    if old not in text_lf:
        print(f"ERROR: {name} block not found -- is paper/main.tex up to date?")
        print(f"  Expected to start with: {old[:80]!r}")
        ok = False
if not ok:
    sys.exit(1)

for _, old, new in patches:
    text_lf = text_lf.replace(old, new, 1)

# Restore CRLF if file originally used it
if "\r\n" in text:
    text_lf = text_lf.replace("\n", "\r\n")

p.write_text(text_lf, encoding="utf-8", newline="")
print("paper/main.tex patched successfully (abstract, keywords, discussion, conclusion, ack).")
remaining = text_lf.count("\\todo{")
print(f"Remaining \\todo blocks: {remaining}")
if remaining == 1:
    print("Only Introduction remains (Dan + Dat, 25/09). All other sections are filled.")
elif remaining == 0:
    print("All \\todo blocks filled! Paper is ready for final review and page-count check.")
else:
    print("Check which \\todo blocks remain before the 26/09 freeze.")
