"""
eval_all_subsets.py -- exhaustive shard-rollback sweep: evaluate EVERY subset of
the n shards (2^n - 1 = 63 subsets at n=6) plus the repaired baseline.

Replaces sampling-based "random" draws (which repeated subsets and left shards
untested) with the complete set, so every single-shard value exists and the
strategy comparison can be read off one table. Inference only: ~63 x 19k images.
On a Kaggle T4 this takes a few minutes; on CPU roughly an hour.

Usage (same data layout as eval_kshard_curve.py; BADNET_PATH points at the
extracted BackdoorBench attack folder that contains bd_test_dataset/):
    BADNET_PATH=/kaggle/working/cifar10_preactresnet18_badnet_0_1 \
    python scripts/eval_all_subsets.py \
        --infected-ckpt data/checkpoints/resnet18_cifar10_badnets_infected.pt \
        --repaired-ckpt data/checkpoints/resnet18_cifar10_badnets_anp_v2.pt \
        --repair-name anp_v2 --norm legacy \
        --data-dir /kaggle/working/cifar10 \
        --out results/raw/all_subsets/anp_v2_n6.json

--norm legacy        = (0.2023, 0.1994, 0.2010) std, what every existing script used
--norm backdoorbench = (0.247, 0.243, 0.261) std, what BackdoorBench trains with
Use the SAME --norm for every repair in the paper. See notes/2026-09-26_chinh_fix_guide.md.
"""
import argparse
import itertools
import json
import os
import sys
import time
from collections import OrderedDict

import torch
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from PIL import Image
from torch.utils.data import DataLoader, Dataset

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.preact_resnet import PreActResNet18  # noqa: E402
from src.partition.shard import partition  # noqa: E402

NORMS = {
    "legacy": ((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    "backdoorbench": ((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
}
SKIP = ("num_batches_tracked", "running_mean", "running_var")


def load_sd(ckpt):
    for key in ("model", "model_state_dict", "state_dict"):
        if isinstance(ckpt, dict) and key in ckpt and isinstance(ckpt[key], dict):
            return ckpt[key]
    return ckpt


class BdTestDataset(Dataset):
    def __init__(self, data_dict, base_path, transform):
        self.entries = list(data_dict.values())
        self.base_path, self.transform = base_path, transform

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, i):
        e = self.entries[i]
        rel = e["path"][e["path"].index("bd_test_dataset"):]
        img = Image.open(os.path.join(self.base_path, rel.replace("/", os.sep))).convert("RGB")
        return self.transform(img), e["other_info"][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infected-ckpt", required=True)
    ap.add_argument("--repaired-ckpt", required=True)
    ap.add_argument("--repair-name", required=True)
    ap.add_argument("--norm", choices=list(NORMS), required=True)
    ap.add_argument("--n-shards", type=int, default=6)
    ap.add_argument("--data-dir", default="data/cifar10")
    ap.add_argument("--batch-size", type=int, default=512)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only-endpoints", action="store_true",
                    help="evaluate only k=0 (repaired) and k=n (infected); used for the normalization check")
    ap.add_argument("--limit", type=int, default=None, help="debug only: use first N images per set")
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available()
                          else "mps" if torch.backends.mps.is_available() else "cpu")
    inf_ckpt = torch.load(args.infected_ckpt, map_location="cpu", weights_only=False)
    inf_sd = load_sd(inf_ckpt)
    rep_sd = load_sd(torch.load(args.repaired_ckpt, map_location="cpu", weights_only=False))

    mean, std = NORMS[args.norm]
    tf = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean, std)])
    base = os.environ.get("BADNET_PATH", "")
    bd = BdTestDataset(inf_ckpt["bd_test"]["bd_data_container"]["data_dict"], base, tf)
    clean = datasets.CIFAR10(root=args.data_dir, train=False, download=False, transform=tf)

    # Cache the (small) test sets on the device once: 19k x 3x32x32 floats ~ 230 MB.
    def cache(ds):
        n = len(ds) if args.limit is None else min(args.limit, len(ds))
        xs, ys = zip(*[ds[i] for i in range(n)])
        return torch.stack(xs).to(device), torch.tensor(ys).to(device)
    t0 = time.time()
    bd_x, bd_y = cache(bd)
    cl_x, cl_y = cache(clean)
    print(f"Device {device}; cached {len(bd_y)} triggered + {len(cl_y)} clean images "
          f"in {time.time() - t0:.0f}s (norm={args.norm})")

    inf_shards = partition(inf_sd, args.n_shards)
    rep_shards = partition(rep_sd, args.n_shards)

    # repair share per shard (same definition as the paper's Eq. 1)
    sq = []
    for a, b in zip(inf_shards, rep_shards):
        d = torch.cat([(b[k].float() - a[k].float()).flatten() for k in a if not k.endswith(SKIP)])
        sq.append(float(d.norm() ** 2))
    share = [s / sum(sq) for s in sq] if sum(sq) > 0 else [0.0] * len(sq)

    model = PreActResNet18(num_classes=10).to(device).eval()

    @torch.no_grad()
    def evaluate(sd):
        model.load_state_dict(sd)
        def acc(x, y):
            c = 0
            for i in range(0, len(y), args.batch_size):
                c += (model(x[i:i + args.batch_size]).argmax(1) == y[i:i + args.batch_size]).sum().item()
            return c
        asr_c, ca_c = acc(bd_x, bd_y), acc(cl_x, cl_y)
        return asr_c, ca_c

    results = []
    subsets = [()] + [c for k in range(1, args.n_shards + 1)
                      for c in itertools.combinations(range(args.n_shards), k)]
    if args.only_endpoints:
        subsets = [subsets[0], subsets[-1]]
    for sub in subsets:
        sd = OrderedDict(rep_sd)
        for s in sub:
            sd.update(inf_shards[s])
        asr_c, ca_c = evaluate(sd)
        row = {"shards": list(sub), "k": len(sub),
               "share_covered": round(sum(share[s] for s in sub), 4),
               "asr": round(100 * asr_c / len(bd_y), 2), "asr_correct": asr_c, "asr_total": len(bd_y),
               "ca": round(100 * ca_c / len(cl_y), 2), "ca_correct": ca_c, "ca_total": len(cl_y)}
        results.append(row)
        print(f"k={row['k']} {row['shards']!s:20s} share={row['share_covered']:.3f} "
              f"ASR={row['asr']:6.2f}  CA={row['ca']:6.2f}")

    full = results[-1]
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump({"repair": args.repair_name, "norm": args.norm, "n_shards": args.n_shards,
                   "infected_ckpt": args.infected_ckpt, "repaired_ckpt": args.repaired_ckpt,
                   "share_s": [round(s, 6) for s in share],
                   "sanity_full_rollback": {"asr": full["asr"], "ca": full["ca"]},
                   "subsets": results}, f, indent=2)
    print(f"\nSaved {len(results)} rows to {args.out}")
    print(f"Sanity: full rollback ASR={full['asr']} CA={full['ca']} (must equal the infected model)")


if __name__ == "__main__":
    main()
