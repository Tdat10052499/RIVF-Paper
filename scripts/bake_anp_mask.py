"""
bake_anp_mask.py -- build the ANP-repaired checkpoint FROM OUR OWN infected model.

ANP (Wu & Wang, NeurIPS 2021; BackdoorBench defense/anp.py) does not retrain
weights. It learns a mask score per BatchNorm neuron and "prunes" every neuron
whose score is <= a threshold by setting that neuron's BN weight (gamma) to 0
(BackdoorBench anp.py, function `pruning`). So an ANP model must be identical
to its base infected model except for those zeroed gammas.

This script applies exactly that rule to our infected checkpoint, using the
mask_values.txt produced by BackdoorBench's ANP run ON THAT SAME CHECKPOINT,
and then verifies the result:
  * only `*.bn*.weight` / `bn.weight` entries changed, and only to 0.0
  * every other tensor is bit-identical to the infected model
  * (optional) matches BackdoorBench's own saved defense_result.pt

Usage (after running BackdoorBench ANP on record/cifar10_preactresnet18_badnet_0_1):
    python scripts/bake_anp_mask.py \
        --infected-ckpt data/checkpoints/resnet18_cifar10_badnets_infected.pt \
        --mask-values   data/checkpoints/anp_v2/mask_values.txt \
        --threshold     0.55 \
        --bb-defense-result data/checkpoints/anp_v2/defense_result.pt \
        --out           data/checkpoints/resnet18_cifar10_badnets_anp_v2.pt
"""
import argparse
import hashlib
import json
import os
from collections import OrderedDict

import torch


def load_sd(path):
    ckpt = torch.load(path, map_location="cpu", weights_only=False)
    if isinstance(ckpt, dict):
        for key in ("model", "model_state_dict", "state_dict"):
            if key in ckpt and isinstance(ckpt[key], dict):
                return ckpt[key]
    return ckpt


def read_mask_values(path):
    """BackdoorBench format: 'No \\t Layer Name \\t Neuron Idx \\t Mask Score' + rows."""
    rows = []
    with open(path) as f:
        for line in f:
            parts = [p.strip() for p in line.split("\t")]
            if len(parts) < 4 or not parts[0].isdigit():
                continue
            rows.append((parts[1], int(parts[2]), float(parts[3])))
    return rows


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infected-ckpt", required=True)
    ap.add_argument("--mask-values", required=True)
    ap.add_argument("--threshold", type=float, required=True,
                    help="threshold BackdoorBench selected (see its log / threshold_df.csv)")
    ap.add_argument("--bb-defense-result", default=None,
                    help="optional: BackdoorBench's defense_result.pt, to cross-check")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    inf = load_sd(args.infected_ckpt)
    masks = read_mask_values(args.mask_values)
    pruned = [(layer, idx) for layer, idx, score in masks if score <= args.threshold]

    anp = OrderedDict((k, v.clone()) for k, v in inf.items())
    for layer, idx in pruned:
        key = f"{layer}.weight"
        if key not in anp:
            raise KeyError(f"{key} from mask_values.txt not found in infected state dict")
        anp[key][idx] = 0.0

    # ---- verification: only the listed BN gammas changed, all to zero ----
    changed_keys = [k for k in inf if not torch.equal(inf[k], anp[k])]
    assert all(".bn" in k or k.startswith("bn.") for k in changed_keys), changed_keys
    assert all(k.endswith(".weight") for k in changed_keys), changed_keys
    n_zero_new = sum(int(((anp[k] == 0) & (inf[k] != 0)).sum()) for k in changed_keys)
    print(f"Mask entries: {len(masks)}  pruned (score <= {args.threshold}): {len(pruned)}")
    print(f"Tensors changed: {len(changed_keys)}  new zeros: {n_zero_new}")
    untouched = [k for k in inf if k not in changed_keys]
    print(f"Tensors bit-identical to infected: {len(untouched)}/{len(inf)}")

    if args.bb_defense_result:
        bb = load_sd(args.bb_defense_result)
        diffs = [k for k in anp if k in bb and not torch.equal(anp[k].float(), bb[k].float().cpu())]
        print(f"Cross-check vs BackdoorBench defense_result: {len(diffs)} differing tensors")
        if diffs:
            print("  first differing keys:", diffs[:5])
            print("  -> BackdoorBench did not start from our infected model, or used "
                  "another threshold. Do NOT use until resolved.")

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    torch.save({
        "model": anp,
        "method": "ANP (BackdoorBench defense/anp.py mask; gammas zeroed on our infected model)",
        "threshold": args.threshold,
        "n_pruned": len(pruned),
        "base_checkpoint_sha256": sha256(args.infected_ckpt),
        "mask_values_sha256": sha256(args.mask_values),
    }, args.out)
    meta = {"out": args.out, "out_sha256": sha256(args.out), "threshold": args.threshold,
            "n_pruned": len(pruned), "n_mask_entries": len(masks),
            "base_checkpoint_sha256": sha256(args.infected_ckpt),
            "pruned_per_layer": {}}
    for layer, _ in pruned:
        top = layer.split(".")[0]
        meta["pruned_per_layer"][top] = meta["pruned_per_layer"].get(top, 0) + 1
    with open(os.path.splitext(args.out)[0] + "_meta.json", "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
