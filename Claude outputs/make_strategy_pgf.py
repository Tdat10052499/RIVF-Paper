"""
make_strategy_pgf.py -- generate Fig. fig:strategy coordinate data
(paper/fig_strategy_data.tex) from the all-subsets JSONs, so no number
in the figure is typed by hand.

Six \addplot coordinate blocks are emitted (no axis environment), k=1..5:
  1. Repair-aware (greedy by share_s), seed-42   (red solid)
  2. Repair-aware (greedy by share_s), seed-0    (orange solid)
  3. Architectural (index order 0,1,...), seed-42 (blue dashed)
  4. Architectural (index order 0,1,...), seed-0  (teal dashed)
  5. Exact mean over all C(6,k) subsets, seed-42  (gray dotted)
  6. Exact mean over all C(6,k) subsets, seed-0   (purple dotted)

x-axis: k = 1 .. 5  (k=0 and k=6 are common endpoints, not shown here)

Greedy order is computed from the 1-shard share_covered values in the s42
JSON (identical geometry in both JSONs).  Architectural order is fixed:
shard index 0, 1, 2, 3, 4 (conv1, layer1, layer2, layer3, layer4).

Pattern follows make_locality_pgf.py per notes/2026-09-25_hung_supervisor.md.

Usage (run from repo root):
    python scripts/make_strategy_pgf.py
    python scripts/make_strategy_pgf.py \\
        --s42 results/raw/all_subsets/finetune_s42_bb_n6.json \\
        --s0  results/raw/all_subsets/finetune_s0_bb_n6.json \\
        --out paper/fig_strategy_data.tex
"""
import argparse
import json
import os
from itertools import combinations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_records(path):
    """Load subset records from JSON; handles both {"subsets":[...]} and [...] formats."""
    d = json.load(open(path))
    return d["subsets"] if isinstance(d, dict) else d


def load_index(path):
    """Return dict: frozenset(shards) -> (asr, ca) for every record in the JSON."""
    index = {}
    for r in load_records(path):
        key = frozenset(r["shards"])
        index[key] = (r["asr"], r["ca"])
    return index


def greedy_order(path):
    """
    Return shard indices sorted by share_covered descending (repair-aware order).
    Computed from the 1-shard records in path.
    """
    single = {}
    for r in load_records(path):
        if len(r["shards"]) == 1:
            single[r["shards"][0]] = r["share_covered"]
    return sorted(single, key=lambda s: single[s], reverse=True)


def coords_block(pairs):
    """pairs: list of (x, y); returns indented coordinate lines."""
    return "\n".join(f"    ({x}, {y:.2f})" for x, y in pairs)


def main():
    ap = argparse.ArgumentParser(
        description="Emit fig_strategy_data.tex from all-subsets JSONs."
    )
    ap.add_argument(
        "--s42",
        default=os.path.join(ROOT, "results/raw/all_subsets/finetune_s42_bb_n6.json"),
        help="Seed-42 all-subsets JSON",
    )
    ap.add_argument(
        "--s0",
        default=os.path.join(ROOT, "results/raw/all_subsets/finetune_s0_bb_n6.json"),
        help="Seed-0 all-subsets JSON",
    )
    ap.add_argument(
        "--out",
        default=os.path.join(ROOT, "paper/fig_strategy_data.tex"),
        help="Output .tex file (default: paper/fig_strategy_data.tex)",
    )
    ap.add_argument(
        "--kmax", type=int, default=5,
        help="Maximum k to include (default: 5; k=6 is identical for all strategies)",
    )
    args = ap.parse_args()

    idx42 = load_index(args.s42)
    idx0  = load_index(args.s0)

    n_shards = 6
    order = greedy_order(args.s42)   # e.g. [3, 4, 2, 1, 0, 5]
    arch_order = list(range(n_shards))  # [0, 1, 2, 3, 4, 5]
    ks = list(range(1, args.kmax + 1))

    # ------------------------------------------------------------------
    # Strategy 1: Repair-aware (greedy by share_s)
    # ------------------------------------------------------------------
    ra42, ra0 = [], []
    for k in ks:
        subset = frozenset(order[:k])
        if subset not in idx42:
            raise KeyError(f"Repair-aware k={k} subset {set(subset)} not found in s42 JSON")
        if subset not in idx0:
            raise KeyError(f"Repair-aware k={k} subset {set(subset)} not found in s0 JSON")
        ra42.append((k, idx42[subset][0]))
        ra0.append((k,  idx0[subset][0]))

    # ------------------------------------------------------------------
    # Strategy 2: Architectural (index order 0, 1, 2, ...)
    # ------------------------------------------------------------------
    arch42, arch0 = [], []
    for k in ks:
        subset = frozenset(arch_order[:k])
        if subset not in idx42:
            raise KeyError(f"Architectural k={k} subset {set(subset)} not found in s42 JSON")
        if subset not in idx0:
            raise KeyError(f"Architectural k={k} subset {set(subset)} not found in s0 JSON")
        arch42.append((k, idx42[subset][0]))
        arch0.append((k,  idx0[subset][0]))

    # ------------------------------------------------------------------
    # Strategy 3: Exact mean over all C(6, k) subsets
    # ------------------------------------------------------------------
    mean42, mean0 = [], []
    all_shards = list(range(n_shards))
    for k in ks:
        subsets_k = [frozenset(c) for c in combinations(all_shards, k)]
        missing42 = [s for s in subsets_k if s not in idx42]
        missing0  = [s for s in subsets_k if s not in idx0]
        if missing42:
            raise KeyError(f"Exact-mean k={k}: {len(missing42)} subsets missing from s42 JSON")
        if missing0:
            raise KeyError(f"Exact-mean k={k}: {len(missing0)} subsets missing from s0 JSON")
        avg42 = sum(idx42[s][0] for s in subsets_k) / len(subsets_k)
        avg0  = sum(idx0[s][0]  for s in subsets_k) / len(subsets_k)
        mean42.append((k, avg42))
        mean0.append((k, avg0))

    # ------------------------------------------------------------------
    # Build comment header with all values for verification
    # ------------------------------------------------------------------
    header_rows = [
        "% Strategy comparison, k=1..{kmax}:".format(kmax=args.kmax),
        "%   k  | RA-s42  RA-s0  | Arch-s42  Arch-s0  | Mean-s42  Mean-s0",
    ]
    for i, k in enumerate(ks):
        header_rows.append(
            f"%   {k}  | {ra42[i][1]:6.2f}  {ra0[i][1]:6.2f}  | "
            f"{arch42[i][1]:8.2f}  {arch0[i][1]:7.2f}  | "
            f"{mean42[i][1]:8.2f}  {mean0[i][1]:7.2f}"
        )

    lines = [
        "% AUTO-GENERATED by scripts/make_strategy_pgf.py",
        "% Sources:",
        f"%   s42: {args.s42}",
        f"%   s0:  {args.s0}",
        f"% Greedy (repair-aware) order: {order}",
        f"% Architectural order: {arch_order}",
        *header_rows,
        "% Do not edit by hand -- rerun the script to update.",
        "",
        "% Series 1: repair-aware, seed-42 (red solid)",
        r"\addplot[color=red!75!black, mark=*, mark size=1.8pt, thick] coordinates {",
        coords_block(ra42),
        "};",
        r"\addlegendentry{Repair-aware, seed~42}",
        "",
        "% Series 2: repair-aware, seed-0 (orange solid)",
        r"\addplot[color=orange!80!black, mark=square*, mark size=1.8pt, thick] coordinates {",
        coords_block(ra0),
        "};",
        r"\addlegendentry{Repair-aware, seed~0}",
        "",
        "% Series 3: architectural, seed-42 (blue dashed)",
        r"\addplot[color=blue!70!black, mark=o, mark size=1.6pt, dashed] coordinates {",
        coords_block(arch42),
        "};",
        r"\addlegendentry{Architectural, seed~42}",
        "",
        "% Series 4: architectural, seed-0 (teal dashed)",
        r"\addplot[color=teal!80!black, mark=triangle*, mark size=1.6pt, dashed] coordinates {",
        coords_block(arch0),
        "};",
        r"\addlegendentry{Architectural, seed~0}",
        "",
        "% Series 5: exact mean C(6,k), seed-42 (gray dotted)",
        r"\addplot[color=black!50, mark=diamond*, mark size=1.6pt, dotted] coordinates {",
        coords_block(mean42),
        "};",
        r"\addlegendentry{Mean over $\binom{6}{k}$, seed~42}",
        "",
        "% Series 6: exact mean C(6,k), seed-0 (purple dotted)",
        r"\addplot[color=violet!80!black, mark=x, mark size=2pt, dotted] coordinates {",
        coords_block(mean0),
        "};",
        r"\addlegendentry{Mean over $\binom{6}{k}$, seed~0}",
    ]

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {args.out}  (k=1..{args.kmax})")
    print(f"  Greedy order (repair-aware): {order}")
    print(f"  k  | RA-s42  RA-s0  | Arch-s42  Arch-s0  | Mean-s42  Mean-s0")
    for i, k in enumerate(ks):
        print(
            f"  {k}  | {ra42[i][1]:6.2f}  {ra0[i][1]:6.2f}  | "
            f"{arch42[i][1]:8.2f}  {arch0[i][1]:7.2f}  | "
            f"{mean42[i][1]:8.2f}  {mean0[i][1]:7.2f}"
        )


if __name__ == "__main__":
    main()
