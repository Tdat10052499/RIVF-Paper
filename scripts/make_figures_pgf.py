#!/usr/bin/env python3
"""Generate every figure data table in paper/figdata/ from the result JSON files.

Numbers in figures are never typed by hand. Rerun after any result changes:
    python3 scripts/make_figures_pgf.py

Each repair's repair-aware order uses that repair's own per-shard share, read
from the JSON (top-level "share_s", or the singleton rows' "share_covered").
"""
import json
import os
import statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "paper", "figdata")
RUNS = {"s42": "results/raw/all_subsets/finetune_s42_bb_n6.json",
        "s0": "results/raw/all_subsets/finetune_s0_bb_n6_v2.json"}
N = 6


def load(path):
    d = json.load(open(os.path.join(ROOT, path)))
    rows = d["subsets"] if isinstance(d, dict) else d
    key = "shards" if "shards" in rows[0] else "subset"
    runs = {tuple(sorted(r[key])): r for r in rows}
    share = d.get("share_s") if isinstance(d, dict) else None
    if share is None:
        share = [runs[(i,)]["share_covered"] for i in range(N)]
    return runs, share


def write(name, header, rows):
    with open(os.path.join(OUT, name), "w") as f:
        f.write(" ".join(header) + "\n")
        for r in rows:
            f.write(" ".join(f"{v:.2f}" if isinstance(v, float) else str(v) for v in r) + "\n")


def main():
    os.makedirs(OUT, exist_ok=True)
    data = {name: load(path) for name, path in RUNS.items()}
    full = tuple(range(N))

    # Fig. 2: single-shard rollback (share of the seed-42 repair).
    s42, share42 = data["s42"]
    s0, _ = data["s0"]
    write("singleshard.dat", ["idx", "share", "asr_s42", "asr_s0"],
          [(i, 100 * share42[i], s42[(i,)]["asr"], s0[(i,)]["asr"]) for i in range(N)])

    # Fig. 3: k-curves. Repair-aware = top-k shards by that repair's own share.
    cols, table = ["k"], {k: [k] for k in range(N + 1)}
    for name, (runs, share) in data.items():
        order = sorted(range(N), key=lambda i: -share[i])
        for k in range(N + 1):
            ra = tuple(sorted(order[:k]))
            ar = tuple(range(k))
            size_k = [s for s in runs if len(s) == k]
            table[k] += [runs[ra]["asr"], runs[ar]["asr"],
                         st.mean(runs[s]["asr"] for s in size_k), runs[ra]["ca"]]
        cols += [f"ra_{name}", f"ar_{name}", f"em_{name}", f"ca_ra_{name}"]
        print(f"{name}: repair-aware order {order}")
    write("kcurve.dat", cols, [table[k] for k in range(N + 1)])

    # Fig. 4: share covered vs ASR, split by layer4 membership (shard 4).
    for name, (runs, share) in data.items():
        for tag, keep in (("l4", True), ("nol4", False)):
            pts = [(100 * sum(share[i] for i in s), runs[s]["asr"], runs[s]["ca"], len(s))
                   for s in runs if s and (4 in s) == keep]
            write(f"locality_{name}_{tag}.dat", ["share", "asr", "ca", "k"], sorted(pts))
    assert data["s42"][0][full]["asr"] == data["s0"][0][full]["asr"], "full rollback must match"
    print(f"wrote paper/figdata/*.dat from {', '.join(RUNS.values())}")


if __name__ == "__main__":
    main()
