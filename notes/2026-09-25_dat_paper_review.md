# Notes 2026-09-25 — Ho Du Tuan Dat: Full Paper Review

**Date:** 25/09/2026
**Author:** Dat
**For:** Dan, Chinh — read before the next writing/editing pass
**Scope:** Full read of `paper/main.tex` as of commit `a527d2d` (25/09, 10:22)

---

## 1. Why this note exists

Before the draft freeze, I did a line-by-line pass over the current
`paper/main.tex`, cross-checked every reported number against the
committed `results/raw/` JSON files, and researched how comparable
published work (including the original ANP paper we compare against)
handles implementation details in the main text. This note collects
everything into one place so nobody has to re-derive it.

Nothing here required re-running any experiment — every item is a
wording, citation, or presentation fix.

---

## 2. Code/file-name references in the manuscript

### Finding
Four places in `paper/main.tex` currently name internal script paths,
config paths, or a function signature directly in the running prose:

| Line | Current text |
|---|---|
| 180 | "...via BackdoorBench's own `\texttt{defense/anp.py}` defense script..." |
| 196 | Table caption: "...(BackdoorBench, `\texttt{config/defense/anp/cifar10.yaml}`)" |
| 236 | "...implemented in `\texttt{src/partition/shard.py}`." |
| 246 | "The `\texttt{substitute(model, shard\_id, stale\_weights)}` function..." |

### What is NOT a problem
Other `\texttt{}` uses in the same sections (`layer1`–`layer4` as
architecture block names, `num_batches_tracked`/`running_mean`/
`running_var` as PyTorch's own standard BatchNorm buffer names,
`model.eval()` as a public PyTorch API call) are fine and should be
**kept as-is** — these name public, standard, citable constructs, not
our own private repo layout.

### Why this matters (checked against real venues, not just opinion)
I read the actual PDF of the ANP paper we compare against (Wu & Wang,
*Adversarial Neuron Pruning Purifies Backdoored Deep Models*, NeurIPS
2021, arXiv:2110.14430) and a comparable security paper (Cert-SSB,
arXiv:2504.21730). Neither names a single internal script/file in the
Methods/Experiments text. Both describe the method in prose +
pseudocode, and mention their code exactly once, as a single link in
the Abstract ("Our code is available at https://github.com/...").

Official Q1-journal-family policy (Nature Portfolio / Nature Machine
Intelligence, one of the top venues for AI) states explicitly:
> "Code availability statements should be provided as a separate
> section after the data availability statement but before the
> references."
i.e. implementation details belong in one dedicated place, not spread
through the Methods narrative.

### Requested fix (Chinh, Method section — no re-run needed)
- Line 180 → *"We apply ANP using BackdoorBench's reference
  implementation~\cite{backdoorbench2024}, without modification."*
- Line 196 → *"ANP defense configuration, following BackdoorBench's
  default CIFAR-10 settings~\cite{backdoorbench2024}"*
- Line 236 → drop the "implemented in ..." clause entirely; the
  sentence stands fine without it.
- Line 246 → *"The substitution procedure replaces the parameters of
  the specified shard in an otherwise-repaired model with weights from
  the pre-repair (infected) checkpoint..."*

### Requested addition (whole team — one line, one place)
Add a single sentence near the end of the paper (in or right before
`\section*{Acknowledgment}`): *"Code and experiment scripts are
available at: [repo link]."* Before adding a public link, please
confirm as a team whether the repo should go public, and if so, sweep
`notes/` for anything not meant to be shared externally.

---

## 3. Full evaluation table (by section / owner)

| Section | Owner (per git blame) | Assessment | Issue found |
|---|---|---|---|
| §1 Introduction | Dan + Dat | **Not started** | Still `\todo{}` — due 25/09 |
| §2.1–2.2 Threat Model, Setup | Chinh | Solid | File-path wording (line 180, 196) — see §2 above |
| §2.3 Partitioning | Chinh | Solid | File-path/function-signature wording (line 236, 246) — see §2 above |
| §2.4 Repair-Share Metric (Eq. 1) | Chinh (written) / Dan (fixed 25/09) | **Resolved** | Formula now matches code (squared-L2), was L1 before `afb9c8f` |
| §2.5 Metrics | Chinh | Solid | None |
| §3.1–3.2 Baseline, Sanity Checks | Dan | Solid | None |
| §3.3 Single-Shard Rollback | Dan | Solid, upgraded 25/09 | None — "n.t." now labeled visually on the figure too |
| §3.4–3.5 k-Shard Curve, Strategy Comparison | Dan | Solid | Numbers verified against committed JSON, all match |
| §3.6 Contrast with ANP | Chinh | Good content | Line 699: "regardless of which shard is substituted" overstates coverage — only 4 of 6 shards were tested in isolation |
| §3.7 Repair Locality vs ASR | Chinh | **Factual error** | Caption (line ~806-809) attributes a specific ASR value ("0.50% and below") to shard 4, but shard 4's single-shard ASR was never measured (marked n.t. elsewhere in the same paper, §3.3) |
| §3.8 Second-Seed Replication | Chinh | Solid | Cross-checked against `results/raw/kshard_seed0/`, numbers match exactly |
| §3.9 Deployment/Serving | Dat | Locked, verified | None |
| Discussion, Limitations, Related Work, Abstract, Conclusion | Chinh | Solid | None |
| `references.bib` | Chinh | Mostly solid | `airs` entry still TODO — needs Prof. Hung to confirm which paper "AIRS" refers to, before 26/09 freeze. Consider adding original citations for CIFAR-10 / BadNets / PreActResNet alongside `backdoorbench2024`, which is only a benchmark toolkit reimplementing them. |

---

## 4. Action items by member

### Dat
- Write Introduction together with Dan (due today, 25/09).
- Once the team agrees on a repo link, add the one-line code
  availability sentence near the Acknowledgment.
- Before making the repo public, sweep `notes/` for anything not
  meant for outside readers.

### Dan
- Write Introduction together with Dat.
- No other open technical items — the three fixes from this morning
  (Eq. 1 formula, "n.t." labels, table→figure conversions) are done
  and verified correct.

### Chinh
1. Rewrite the four file-path/function-signature references per §2
   above (wording only, no new experiments).
2. Line 699: qualify "regardless of which shard is substituted" to
   reflect that only 4 of 6 shards were tested individually.
3. Fix the `fig:locality_asr` caption (line ~806-809): remove the
   claim that attributes a measured ASR to shard 4, which was never
   isolated at k=1.
4. Confirm the "AIRS" citation identity with Prof. Hung before 26/09.
5. Consider adding original-source citations for CIFAR-10, BadNets,
   and PreActResNet.

### Whole team
- Update the stale "% Owner: Dan, 24/09" comment above `sec:results`
  (line 331) — most of §3.6–3.8, plus Abstract/Discussion/Conclusion,
  were in fact written by Chinh. Keep the ownership comments accurate
  for anyone reading the git history later.
- Agree on whether/where to publish the repo link before Dat adds the
  code-availability sentence.

---

## 5. Sources checked for the code/file-naming question

- Wu & Wang, *Adversarial Neuron Pruning Purifies Backdoored Deep
  Models*, NeurIPS 2021 — https://arxiv.org/pdf/2110.14430
- Cert-SSB — https://arxiv.org/pdf/2504.21730
- Nature Machine Intelligence, Reporting standards —
  https://www.nature.com/natmachintell/editorial-policies/reporting-standards
- Nature Portfolio, Guidelines for authors submitting code & software —
  https://www.nature.com/documents/GuidelinesCodePublication.pdf
- Springer Nature, Code Policy —
  https://www.springernature.com/gp/open-science/code-policy
