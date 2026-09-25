"""
check_lineage.py -- verify that two checkpoints belong to the same model lineage
before any shard substitution is run between them.

Why this exists: the first ANP checkpoint (resnet18_cifar10_badnets_anp_fixed.pt)
was produced from a *different* BadNets model than our infected checkpoint
(cosine similarity ~0.00 in every layer). Substituting shards between two
unrelated networks produces meaningless "hybrids". Run this check on every
(infected, repaired) pair and commit its JSON output next to the results.

Usage:
    python scripts/check_lineage.py \
        --a data/checkpoints/resnet18_cifar10_badnets_infected.pt \
        --b data/checkpoints/resnet18_cifar10_badnets_anp_v2.pt \
        --n-shards 6 --out results/raw/lineage/infected_vs_anp_v2.json

Exit code 1 if any shard's cosine similarity is below --min-cos (default 0.5).
Only learnable parameters are compared (BatchNorm buffers are skipped, same
rule as compute_share.py).
"""
import argparse
import json
import os
import sys

import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.partition.shard import partition  # noqa: E402

SKIP = ("num_batches_tracked", "running_mean", "running_var")


def load_sd(path):
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict):
        for key in ("model", "model_state_dict", "state_dict"):
            if key in ckpt and isinstance(ckpt[key], dict):
                return ckpt[key]
    return ckpt


def flat(shard):
    parts = [v.float().flatten() for k, v in shard.items() if not k.endswith(SKIP)]
    return torch.cat(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="reference checkpoint (infected)")
    ap.add_argument("--b", required=True, help="checkpoint to test (repaired)")
    ap.add_argument("--n-shards", type=int, default=6)
    ap.add_argument("--min-cos", type=float, default=0.5)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    sd_a, sd_b = load_sd(args.a), load_sd(args.b)
    if list(sd_a.keys()) != list(sd_b.keys()):
        print("FAIL: state-dict keys differ")
        sys.exit(1)

    rows, ok = [], True
    for s, (sa, sb) in enumerate(zip(partition(sd_a, args.n_shards), partition(sd_b, args.n_shards))):
        va, vb = flat(sa), flat(sb)
        cos = torch.nn.functional.cosine_similarity(va, vb, dim=0).item()
        rel = ((vb - va).norm() / va.norm()).item()
        identical = int((va == vb).sum().item())
        rows.append({
            "shard_idx": s,
            "layers": sorted({k.split(".")[0] for k in sa}),
            "cosine": round(cos, 4),
            "rel_diff": round(rel, 4),
            "identical_params": identical,
            "total_params": va.numel(),
        })
        flag = "OK " if cos >= args.min_cos else "BAD"
        ok &= cos >= args.min_cos
        print(f"[{flag}] shard {s} {rows[-1]['layers']}: cos={cos:.4f} "
              f"rel_diff={rel:.4f} identical={identical}/{va.numel()}")

    verdict = "same lineage" if ok else "DIFFERENT LINEAGE -- do not substitute shards"
    print(f"\nVerdict: {verdict}")
    if args.out:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w") as f:
            json.dump({"a": args.a, "b": args.b, "n_shards": args.n_shards,
                       "min_cos": args.min_cos, "verdict": verdict, "shards": rows}, f, indent=2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
