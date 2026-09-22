import sys, os, json, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.partition.shard import partition
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--infected-ckpt", required=True)
parser.add_argument("--repaired-ckpt", required=True)
parser.add_argument("--n-shards", type=int, nargs="+", default=[3, 6])
parser.add_argument("--out", default="results/raw/share")
args = parser.parse_args()

infected = torch.load(args.infected_ckpt, map_location="cpu", weights_only=False)
repaired = torch.load(args.repaired_ckpt, map_location="cpu", weights_only=False)
infected_sd = infected.get("model") or infected.get("model_state_dict")
repaired_sd = repaired.get("model") or repaired.get("model_state_dict")

# Skip non-learnable buffers (BatchNorm counters and running stats)
SKIP = ("num_batches_tracked", "running_mean", "running_var")

os.makedirs(args.out, exist_ok=True)

for n in args.n_shards:
    infected_shards = partition(infected_sd, n)
    repaired_shards = partition(repaired_sd, n)

    records = []
    sq_norms = []

    for s, (inf_shard, rep_shard) in enumerate(zip(infected_shards, repaired_shards)):
        delta_parts, inf_parts = [], []
        for key in inf_shard:
            if any(key.endswith(sk) for sk in SKIP):
                continue
            delta_parts.append((rep_shard[key] - inf_shard[key]).float().flatten())
            inf_parts.append(inf_shard[key].float().flatten())
        delta = torch.cat(delta_parts)
        inf_flat = torch.cat(inf_parts)
        norm_delta = delta.norm(p=2).item()
        norm_inf   = inf_flat.norm(p=2).item()
        sq_norms.append(norm_delta ** 2)
        records.append({
            "shard_idx": s,
            "r_s": norm_delta / norm_inf,
            "norm_delta": norm_delta,
            "norm_delta_sq": norm_delta ** 2,
            "norm_inf": norm_inf,
        })

    total_sq = sum(sq_norms)
    for r in records:
        r["share_s"] = r["norm_delta_sq"] / total_sq

    print(f"\n=== n={n} shards ===")
    print(f"{'Shard':>6}  {'r_s':>12}  {'share_s':>12}  {'norm_delta':>12}")
    print("-" * 50)
    for r in records:
        print(f"{r['shard_idx']:>6}  {r['r_s']:>12.8f}  {r['share_s']:>12.8f}  {r['norm_delta']:>12.4f}")
    print(f"{'SUM':>6}  {'':>12}  {sum(r['share_s'] for r in records):>12.8f}")

    out_data = {
        "n_shards": n,
        "repair": "20epoch_clean_finetune",
        "skipped_buffers": list(SKIP),
        "shards": [
            {**r, "r_s": round(r["r_s"], 8), "share_s": round(r["share_s"], 8),
             "norm_delta": round(r["norm_delta"], 6), "norm_delta_sq": round(r["norm_delta_sq"], 6),
             "norm_inf": round(r["norm_inf"], 6)}
            for r in records
        ],
        "total_norm_delta_sq": round(total_sq, 6),
    }
    out_path = os.path.join(args.out, f"share_n{n}.json")
    with open(out_path, "w") as f:
        json.dump(out_data, f, indent=2)
    print(f"Saved to {out_path}")
