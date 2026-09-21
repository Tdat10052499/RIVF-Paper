"""
scripts/build_shard_manifest.py

Part of DAT-SERVING-01 (notes/2026-09-21_dat_serving_experiment_card.md).
Step 2 of the agreed 9-step plan.

Builds, for one checkpoint, an on-disk set of shard files plus two manifest
files -- one for each verification scheme under comparison:

  - per_shard_sig:      each shard's signature covers only that shard's
                         own bytes. This is the scheme the paper argues is
                         common and insufficient: it has no way to tell
                         whether a validly-signed shard belongs to the same
                         repair epoch as its neighbours.
  - epoch_manifest_pin:  each shard's signature covers that shard's bytes
                         *and* the epoch_id, so a shard signed under a
                         different epoch produces a signature that will not
                         verify against the current epoch_id.

Both manifests are built from the SAME shard files (written once) --  only
the signature values and the extra epoch_id field differ, which is exactly
the "unavoidable difference" the experiment card predicts for manifest
size.

Reuses partition() from src/partition/shard.py. Does not decide anything
about attack/skew scenarios -- that is assembled later by
scripts/run_serving_comparison.py, by combining shard files/signatures
from two different epochs' manifests.
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.partition.shard import partition
import torch

# Simulated shared signing key, for this measurement only. The project is
# not proposing a new signing protocol (notes/2026-09-21_hung_supervisor.md,
# Section 4) -- this key exists purely so the two schemes below have a
# concrete signature to compute and check. A real deployment would use a
# proper key-management / PKI setup; that is explicitly out of scope here.
SIGNING_KEY = b"DAT-SERVING-01-simulated-signing-key"

SCHEMES = ("per_shard_sig", "epoch_manifest_pin")


def _sign(payload: bytes) -> str:
    return hmac.new(SIGNING_KEY, payload, hashlib.sha256).hexdigest()


def build_manifest(checkpoint_path: str, epoch_id: str, n_shards: int, out_dir: str) -> dict:
    """
    Build shard files and both manifests for one checkpoint.

    Returns a dict {scheme_name: manifest_json_path}.
    """
    ckpt = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    state_dict = ckpt["model"]

    shards = partition(state_dict, n_shards)

    epoch_dir = os.path.join(out_dir, epoch_id)
    shard_dir = os.path.join(epoch_dir, "shards")
    os.makedirs(shard_dir, exist_ok=True)

    # Pass 1: serialize every shard to disk once. Shard bytes are identical
    # for both schemes -- only the signature formula differs below.
    shard_files = []
    for idx, shard_sd in enumerate(shards):
        shard_path = os.path.join(shard_dir, f"shard{idx}.bin")
        torch.save(shard_sd, shard_path)
        with open(shard_path, "rb") as f:
            shard_bytes = f.read()
        shard_files.append({
            "shard_idx": idx,
            "path": shard_path,
            "num_keys": len(shard_sd),
            "bytes": len(shard_bytes),
            "raw_bytes": shard_bytes,  # kept in memory only for signing below, not written to JSON
        })

    built_at = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    manifest_paths = {}

    for scheme in SCHEMES:
        shard_entries = []
        for sf in shard_files:
            if scheme == "per_shard_sig":
                payload = sf["raw_bytes"]
            else:  # epoch_manifest_pin
                payload = sf["raw_bytes"] + epoch_id.encode("utf-8")
            shard_entries.append({
                "shard_idx": sf["shard_idx"],
                "file": os.path.relpath(sf["path"], out_dir),
                "num_keys": sf["num_keys"],
                "bytes": sf["bytes"],
                "signature": _sign(payload),
            })

        manifest = {
            "scheme": scheme,
            "n_shards": n_shards,
            "checkpoint_source": os.path.basename(checkpoint_path),
            "built_at": built_at,
            "shards": shard_entries,
        }
        # epoch_id is included ONLY for epoch_manifest_pin. This is
        # deliberate, not an oversight: a real per-shard-signature-only
        # system has no cross-shard epoch concept and would not carry this
        # field, so it must be absent here too. Including it in both
        # manifests "for traceability" was tried first and rejected --  it
        # made the manifest-size comparison meaningless, since the only
        # difference left was the length of the scheme name string, not the
        # actual architectural cost of epoch pinning. See the note in
        # notes/2026-09-21_dat_serving_experiment_card.md this script
        # implements: "epoch-manifest pinning necessarily stores at least
        # one additional field... that per-shard signature checking does
        # not."
        if scheme == "epoch_manifest_pin":
            manifest["epoch_id"] = epoch_id

        manifest_path = os.path.join(epoch_dir, f"manifest_{scheme}.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        manifest_paths[scheme] = manifest_path

    return manifest_paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--epoch-id", required=True,
                         help="Label identifying this checkpoint's repair epoch, e.g. 'infected_v1' or 'repaired_v1'.")
    parser.add_argument("--n-shards", type=int, default=3)
    parser.add_argument("--out-dir", default="data/serving_manifests")
    args = parser.parse_args()

    paths = build_manifest(args.checkpoint, args.epoch_id, args.n_shards, args.out_dir)
    for scheme, path in paths.items():
        size = os.path.getsize(path)
        print(f"{scheme}: {path} ({size} bytes)")
