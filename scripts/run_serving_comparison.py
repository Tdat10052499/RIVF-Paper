"""
scripts/run_serving_comparison.py

Part of DAT-SERVING-01 (notes/2026-09-21_dat_serving_experiment_card.md).
Step 5 of the 9-step plan -- the actual experiment; Steps 0-4 were
preparation.

Runs the full 2 (scheme) x 2 (scenario) x 30 (repetition) design from the
experiment card, using two separate OS processes -- per Hung's literal
wording, "Two processes that load a model from a manifest" -- one process
running only per_shard_sig loads, the other only epoch_manifest_pin loads.
This mirrors how the two verification schemes would run as separate
services in a real deployment; it is not simulated with threads.

Design note on the "interrupted rollout" / skewed scenario: it is built by
taking shard 0's entry -- file path AND signature -- directly from the
OTHER epoch's already-built, independently signed manifest, and splicing
it into an otherwise-normal manifest for the current epoch. This is
deliberately NOT done by calling substitute() on raw tensors and re-
signing the result: that would hand the attacker a freshly and correctly
computed signature for content they should not be able to sign, which
contradicts the threat model in the experiment card (the attacker holds
one VALIDLY-SIGNED PRE-REPAIR shard -- already signed, under its own old
epoch -- not signing authority). partition()/substitute() still define
which physical shard this is (shard 0 of 3, the same boundary every other
experiment in this project uses); the manifest entries spliced in here are
already known, byte-identical to what substitute() would produce, and were
independently confirmed as such during Step 3's verification.

Output: one JSON-lines file per scheme under --out-dir (default
results/raw/serving/), one record per load attempt, matching the raw
fields the experiment card specifies. Unlike data/serving_manifests/
(gitignored -- large, regenerable shard binaries), these raw run records
ARE meant to be committed: results/raw/ is the project's immutable
evidence record (see .gitignore's own comment on that directory).
"""
import argparse
import json
import multiprocessing as mp
import os
import random
import signal
import statistics
import sys
import time
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.build_shard_manifest import build_manifest
from src.serving.loader import load_per_shard_signature, load_epoch_pinned

N_REPS = 30
TIMEOUT_SEC = 10
SKEWED_SHARD_IDX = 0  # matches the shard index used by every other
                      # single-shard experiment in this project
SCHEMES = ("per_shard_sig", "epoch_manifest_pin")

DEFAULT_MANIFEST_DIR = "data/serving_manifests"
DEFAULT_OUT_DIR = "results/raw/serving"


class LoadTimeout(Exception):
    pass


def _timeout_handler(signum, frame):
    raise LoadTimeout(f"load exceeded {TIMEOUT_SEC}s timeout")


def _build_skewed_manifest(scheme, base_epoch, other_epoch, manifest_dir):
    """
    Return (in memory) a manifest for base_epoch where shard
    SKEWED_SHARD_IDX's entry is replaced by the SAME scheme's entry from
    other_epoch's manifest. The manifest's own declared metadata (notably
    epoch_id, for epoch_manifest_pin) stays as base_epoch's -- the
    deployment believes it is serving that epoch; only the one shard is
    actually stale.
    """
    fname = f"manifest_{scheme}.json"
    with open(os.path.join(manifest_dir, base_epoch, fname)) as f:
        base = json.load(f)
    with open(os.path.join(manifest_dir, other_epoch, fname)) as f:
        other = json.load(f)

    skewed = deepcopy(base)
    other_entry = next(s for s in other["shards"] if s["shard_idx"] == SKEWED_SHARD_IDX)
    skewed["shards"] = [other_entry if s["shard_idx"] == SKEWED_SHARD_IDX else s
                         for s in skewed["shards"]]
    return skewed


def _worker(scheme, manifest_dir, out_path, seed):
    """Runs in its own OS process. One scheme only, both scenarios,
    N_REPS each, in randomized order."""
    random.seed(seed)
    loader_fn = load_per_shard_signature if scheme == "per_shard_sig" else load_epoch_pinned
    fname = f"manifest_{scheme}.json"

    normal_manifest_path = os.path.join(manifest_dir, "repaired_v1", fname)
    manifest_bytes = os.path.getsize(normal_manifest_path)

    skewed_manifest = _build_skewed_manifest(scheme, "repaired_v1", "infected_v1", manifest_dir)
    skewed_manifest_path = os.path.join(manifest_dir, f"_skewed_{scheme}.json")
    with open(skewed_manifest_path, "w") as f:
        json.dump(skewed_manifest, f, indent=2)

    plan = ([("normal", normal_manifest_path)] * N_REPS +
             [("skewed", skewed_manifest_path)] * N_REPS)
    random.shuffle(plan)

    records = []
    for rep_idx, (scenario, manifest_path) in enumerate(plan):
        record = {
            "scheme": scheme, "scenario": scenario, "repetition_index": rep_idx,
            "manifest_bytes": manifest_bytes,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(TIMEOUT_SEC)
        try:
            result = loader_fn(manifest_path, base_dir=manifest_dir)
            signal.alarm(0)
            record.update({
                "outcome": "accepted" if result.accepted else "rejected",
                "verify_time_sec": result.verify_seconds,
                "failed_shards": result.failed_shards,
                "reason": result.reason,
                "error_message": None,
            })

            # Rollout recovery time: only meaningful for epoch_manifest_pin
            # in the skewed scenario, and only when it actually detected
            # (rejected) the skew -- immediately retry against the correct
            # manifest and time to a successful accept.
            if scheme == "epoch_manifest_pin" and scenario == "skewed" and not result.accepted:
                t_recover0 = time.perf_counter()
                recovery_result = loader_fn(normal_manifest_path, base_dir=manifest_dir)
                recovery_time = time.perf_counter() - t_recover0
                record["recovery_time_sec"] = recovery_time if recovery_result.accepted else None
                if not recovery_result.accepted:
                    record["error_message"] = "recovery attempt against normal manifest also failed"
            else:
                # per_shard_sig never detects the skew, so recovery is not
                # a meaningful measurement for it -- report None ("N/A"),
                # never a fabricated number (see experiment card).
                record["recovery_time_sec"] = None
        except LoadTimeout as e:
            signal.alarm(0)
            record.update({
                "outcome": "failed", "verify_time_sec": None, "failed_shards": None,
                "reason": None, "recovery_time_sec": None, "error_message": str(e),
            })
        except Exception as e:
            signal.alarm(0)
            record.update({
                "outcome": "failed", "verify_time_sec": None, "failed_shards": None,
                "reason": None, "recovery_time_sec": None,
                "error_message": f"{type(e).__name__}: {e}",
            })
        records.append(record)

    os.remove(skewed_manifest_path)
    with open(out_path, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infected-ckpt", required=True)
    parser.add_argument("--repaired-ckpt", required=True)
    parser.add_argument("--n-shards", type=int, default=3)
    parser.add_argument("--manifest-dir", default=DEFAULT_MANIFEST_DIR)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    # Self-contained: (re)build both epochs' manifests from the checkpoints
    # before running, rather than assuming a prior manual step.
    build_manifest(args.infected_ckpt, "infected_v1", args.n_shards, args.manifest_dir)
    build_manifest(args.repaired_ckpt, "repaired_v1", args.n_shards, args.manifest_dir)

    os.makedirs(args.out_dir, exist_ok=True)

    procs = []
    for i, scheme in enumerate(SCHEMES):
        out_path = os.path.join(args.out_dir, f"{scheme}.jsonl")
        p = mp.Process(target=_worker, args=(scheme, args.manifest_dir, out_path, args.seed + i))
        procs.append(p)

    t0 = time.perf_counter()
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    elapsed = time.perf_counter() - t0

    for p in procs:
        if p.exitcode != 0:
            print(f"WARNING: a worker process exited with code {p.exitcode}")

    print(f"Both processes finished in {elapsed:.1f}s.\n")
    _print_summary(args.out_dir, args.manifest_dir)


def _print_summary(out_dir, manifest_dir):
    print(f"{'Scheme':<20}{'Scenario':<10}{'N':<5}{'Accepted':<10}{'Mean verify (ms)':<20}{'Std (ms)':<10}")
    for scheme in SCHEMES:
        with open(os.path.join(out_dir, f"{scheme}.jsonl")) as f:
            records = [json.loads(line) for line in f]
        for scenario in ("normal", "skewed"):
            cell = [r for r in records if r["scenario"] == scenario]
            n = len(cell)
            accepted = sum(1 for r in cell if r["outcome"] == "accepted")
            times_ms = [r["verify_time_sec"] * 1000 for r in cell if r["verify_time_sec"] is not None]
            mean_ms = statistics.mean(times_ms) if times_ms else float("nan")
            std_ms = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
            print(f"{scheme:<20}{scenario:<10}{n:<5}{accepted}/{n:<8}{mean_ms:<20.2f}{std_ms:<10.2f}")

    print("\nManifest size (bytes):")
    for scheme in SCHEMES:
        size = os.path.getsize(os.path.join(manifest_dir, "repaired_v1", f"manifest_{scheme}.json"))
        print(f"  {scheme}: {size}")

    print("\nRollout recovery time, epoch_manifest_pin / skewed scenario only (N/A for per_shard_sig -- skew undetected):")
    with open(os.path.join(out_dir, "epoch_manifest_pin.jsonl")) as f:
        records = [json.loads(line) for line in f]
    recov = [r["recovery_time_sec"] for r in records
             if r["scenario"] == "skewed" and r["recovery_time_sec"] is not None]
    if recov:
        print(f"  mean={statistics.mean(recov)*1000:.2f}ms, std={statistics.stdev(recov)*1000 if len(recov) > 1 else 0:.2f}ms, n={len(recov)}")
    else:
        print("  N/A (no successful recoveries recorded)")


if __name__ == "__main__":
    main()
