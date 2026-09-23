"""
plot_locality_asr.py — "Locality vs. ASR" scatter figure for the paper.

For each shard, plots: x = repair-share (share_s), y = ASR recovered when
rolling back ONLY that shard (k=1 repair-aware, per-shard single rollback).

Two curves: Fine-tune repair and ANP repair.

Usage (after Dan's k-shard re-runs are committed):
    python scripts/plot_locality_asr.py \\
        --share-ft   results/raw/share/share_n6.json \\
        --kshard-ft  results/raw/kshard/kshard_curve_n6.json \\
        --share-anp  results/raw/share_anp/share_n6.json \\
        --kshard-anp results/raw/kshard_anp/kshard_curve_n6.json \\
        --out        figures/locality_vs_asr.pdf
"""

import json, argparse, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

parser = argparse.ArgumentParser()
parser.add_argument("--share-ft",   default="results/raw/share/share_n6.json")
parser.add_argument("--kshard-ft",  default="results/raw/kshard/kshard_curve_n6.json")
parser.add_argument("--share-anp",  default="results/raw/share_anp/share_n6.json")
parser.add_argument("--kshard-anp", default="results/raw/kshard_anp/kshard_curve_n6.json")
parser.add_argument("--n-shards",   type=int, default=6)
parser.add_argument("--out",        default="figures/locality_vs_asr.pdf")
args = parser.parse_args()


def load_per_shard_asr(share_json_path, kshard_json_path, n_shards):
    """
    Returns two arrays of length n_shards:
        shares  [s0, s1, ..., s5]   repair share per shard
        asrs    [asr0, ..., asr5]   ASR when rolling back that shard alone
    """
    with open(share_json_path) as f:
        share_data = json.load(f)
    with open(kshard_json_path) as f:
        kshard_data = json.load(f)

    share_s = [0.0] * n_shards
    for r in share_data["shards"]:
        share_s[r["shard_idx"]] = r["share_s"]

    if "per_shard" in kshard_data:
        asrs = [0.0] * n_shards
        for entry in kshard_data["per_shard"]:
            asrs[entry["shard_idx"]] = entry["asr"]
        return np.array(share_s), np.array(asrs)

    repair_aware_order = sorted(range(n_shards), key=lambda s: -share_s[s])
    asrs = [None] * n_shards

    k1_ra = kshard_data.get("k1", {}).get("strategies", {}).get("repair_aware", {})
    if k1_ra:
        asrs[repair_aware_order[0]] = k1_ra["asr"]

    k1_arch = kshard_data.get("k1", {}).get("strategies", {}).get("architectural", {})
    if k1_arch:
        asrs[0] = k1_arch["asr"]

    k1_rand = kshard_data.get("k1", {}).get("strategies", {}).get("random", {})
    if k1_rand:
        for draw_shards, draw_asr in zip(k1_rand.get("draws", []),
                                          k1_rand.get("asr_per_draw", [])):
            if len(draw_shards) == 1:
                asrs[draw_shards[0]] = draw_asr

    asrs = [a if a is not None else float("nan") for a in asrs]
    return np.array(share_s), np.array(asrs)


share_ft,  asr_ft  = load_per_shard_asr(args.share_ft,  args.kshard_ft,  args.n_shards)
share_anp, asr_anp = load_per_shard_asr(args.share_anp, args.kshard_anp, args.n_shards)

print("Fine-tune repair:")
for i, (s, a) in enumerate(zip(share_ft, asr_ft)):
    print(f"  shard {i}  share={s:.4f}  ASR_rollback={a:.2f}%")

print("\nANP repair:")
for i, (s, a) in enumerate(zip(share_anp, asr_anp)):
    print(f"  shard {i}  share={s:.4f}  ASR_rollback={a:.2f}%")

COLORS  = {"ft": "#1f77b4", "anp": "#d62728"}
MARKERS = {"ft": "o",      "anp": "s"}
LABELS  = {"ft": "Fine-tune repair", "anp": "ANP repair"}

fig, ax = plt.subplots(figsize=(5.5, 4.0))

for tag, share, asr in [("ft", share_ft, asr_ft), ("anp", share_anp, asr_anp)]:
    mask = ~np.isnan(asr)
    x = share[mask] * 100
    y = asr[mask]

    ax.scatter(x, y, color=COLORS[tag], marker=MARKERS[tag],
               s=70, zorder=5, label=LABELS[tag])

    if mask.sum() >= 2:
        coeffs = np.polyfit(x, y, 1)
        x_line = np.linspace(x.min() - 1, x.max() + 1, 200)
        y_line = np.polyval(coeffs, x_line)
        ax.plot(x_line, y_line, color=COLORS[tag], lw=1.2, linestyle="--", alpha=0.6)

    for i, (xi, yi, valid) in enumerate(zip(share * 100, asr, mask)):
        if valid:
            ax.annotate(f"$s_{i}$", (xi, yi),
                        textcoords="offset points", xytext=(5, 3),
                        fontsize=8, color=COLORS[tag])

ax.set_xlabel("Repair share of shard  $\\phi_s$  (%)", fontsize=11)
ax.set_ylabel("ASR recovered when rolling back shard  (%)", fontsize=11)
ax.set_title("Repair Locality vs. ASR Recovery\n(single-shard rollback, $n=6$)", fontsize=11)
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.0f%%"))
ax.set_xlim(left=-1)
ax.set_ylim(bottom=-2, top=105)
ax.legend(framealpha=0.9, fontsize=9)
ax.grid(True, linestyle=":", alpha=0.5)

fig.tight_layout()
os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
fig.savefig(args.out, dpi=300, bbox_inches="tight")
print(f"\nFigure saved → {args.out}")
plt.close(fig)
