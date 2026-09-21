"""
src/serving/loader.py

Part of DAT-SERVING-01 (notes/2026-09-21_dat_serving_experiment_card.md).
Step 3 of the agreed 9-step plan.

Two loader functions, one per verification scheme under comparison, each
reading a manifest built by scripts/build_shard_manifest.py (or a synthetic
manifest assembled by scripts/run_serving_comparison.py by mixing shard
entries from two different epochs' manifests -- that assembly is Step 5,
not this module's job):

    load_per_shard_signature(manifest_path)
        Verifies only that each shard's own signature matches its own
        bytes. Has no way to check whether shards belong to the same
        repair epoch as each other -- that is exactly the gap this scheme
        exists to represent in the comparison.

    load_epoch_pinned(manifest_path)
        Verifies that each shard's signature matches its own bytes AND
        the manifest's declared epoch_id. A shard whose signature was
        computed under a different epoch_id will not match here, even if
        its bytes are byte-for-byte unmodified and validly signed under
        that OTHER epoch.

Design note on timing (see notes/2026-09-21_dat_serving_experiment_card.md,
"Verification time per load"): that metric is defined as the time from the
start of verification to the accept/reject DECISION, and explicitly
excludes model deserialization. To keep that boundary exact rather than
relying on the caller to time the right span, each LoadResult carries its
own verify_seconds, measured internally around the signature-checking loop
only. Deserialization (torch.load) happens strictly after the decision,
only for an accepted load, and is not included in verify_seconds. This is
also the safer order operationally: nothing is deserialized (i.e. unpickled
-- pickle execution is not sandboxed) before its signature has been
checked.

A rejected/skewed load is an ordinary, expected measurement outcome, not
raised as an exception. A malformed manifest, a manifest/loader scheme
mismatch, or a missing shard file are setup bugs, not measurement
outcomes, and DO raise.
"""
import hashlib
import hmac
import io
import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional

import torch

# Must match scripts/build_shard_manifest.py exactly. See that module's
# docstring for why this is a simulated key, not a real signing setup.
from scripts.build_shard_manifest import SIGNING_KEY

SCHEMES = ("per_shard_sig", "epoch_manifest_pin")


@dataclass
class LoadResult:
    scheme: str
    accepted: bool
    reason: str
    failed_shards: list
    verify_seconds: float
    epoch_id: Optional[str] = None
    state_dict: Optional[dict] = None


def _sign(payload: bytes) -> str:
    return hmac.new(SIGNING_KEY, payload, hashlib.sha256).hexdigest()


def _read_manifest(manifest_path: str, expected_scheme: str) -> dict:
    with open(manifest_path) as f:
        manifest = json.load(f)
    if manifest.get("scheme") != expected_scheme:
        raise ValueError(
            f"{manifest_path}: manifest scheme is {manifest.get('scheme')!r}, "
            f"expected {expected_scheme!r} -- wrong loader for this manifest"
        )
    return manifest


def _base_dir_for(manifest_path: str) -> str:
    # build_shard_manifest.py writes to <out_dir>/<epoch_id>/manifest_<scheme>.json
    # and stores each shard's "file" relative to <out_dir>. Two directories
    # up from the manifest file is therefore <out_dir>.
    return os.path.dirname(os.path.dirname(os.path.abspath(manifest_path)))


def _deserialize(raw_bytes: bytes) -> dict:
    return torch.load(io.BytesIO(raw_bytes), map_location="cpu", weights_only=False)


def _merge_shards(shard_tensors: dict, n_shards: int) -> dict:
    if set(shard_tensors.keys()) != set(range(n_shards)):
        raise ValueError("internal error: not all shards present after acceptance")
    merged = {}
    for idx in range(n_shards):
        merged.update(shard_tensors[idx])
    return merged


def load_per_shard_signature(manifest_path: str, base_dir: str = None) -> LoadResult:
    manifest = _read_manifest(manifest_path, "per_shard_sig")
    base_dir = base_dir or _base_dir_for(manifest_path)

    t0 = time.perf_counter()
    failed = []
    shard_raw = {}
    for entry in manifest["shards"]:
        shard_abs = os.path.join(base_dir, entry["file"])
        if not os.path.exists(shard_abs):
            raise FileNotFoundError(f"shard file listed in manifest not found: {shard_abs}")
        with open(shard_abs, "rb") as f:
            raw = f.read()
        # Per-shard signature covers only this shard's own bytes -- no
        # cross-shard or cross-epoch information enters the check.
        if _sign(raw) == entry["signature"]:
            shard_raw[entry["shard_idx"]] = raw
        else:
            failed.append(entry["shard_idx"])
    verify_seconds = time.perf_counter() - t0
    # --- decision made above; nothing after this point counts toward
    #     verify_seconds ---

    if failed:
        return LoadResult(
            scheme="per_shard_sig", accepted=False, failed_shards=failed,
            verify_seconds=verify_seconds,
            reason=f"shard(s) {failed} failed signature verification",
        )

    shard_tensors = {idx: _deserialize(raw) for idx, raw in shard_raw.items()}
    state_dict = _merge_shards(shard_tensors, manifest["n_shards"])
    return LoadResult(
        scheme="per_shard_sig", accepted=True, failed_shards=[],
        verify_seconds=verify_seconds,
        reason="all shard signatures valid", state_dict=state_dict,
    )


def load_epoch_pinned(manifest_path: str, base_dir: str = None) -> LoadResult:
    manifest = _read_manifest(manifest_path, "epoch_manifest_pin")
    base_dir = base_dir or _base_dir_for(manifest_path)
    epoch_id = manifest["epoch_id"]

    t0 = time.perf_counter()
    failed = []
    shard_raw = {}
    for entry in manifest["shards"]:
        shard_abs = os.path.join(base_dir, entry["file"])
        if not os.path.exists(shard_abs):
            raise FileNotFoundError(f"shard file listed in manifest not found: {shard_abs}")
        with open(shard_abs, "rb") as f:
            raw = f.read()
        # Epoch-pinned signature covers this shard's bytes AND the
        # manifest's declared epoch_id. A shard signed under a different
        # epoch_id -- e.g. substituted in from an older, still-validly-
        # signed build -- will not match, even though its bytes alone are
        # unmodified.
        payload = raw + epoch_id.encode("utf-8")
        if _sign(payload) == entry["signature"]:
            shard_raw[entry["shard_idx"]] = raw
        else:
            failed.append(entry["shard_idx"])
    verify_seconds = time.perf_counter() - t0
    # --- decision made above; nothing after this point counts toward
    #     verify_seconds ---

    if failed:
        return LoadResult(
            scheme="epoch_manifest_pin", accepted=False, failed_shards=failed,
            verify_seconds=verify_seconds, epoch_id=epoch_id,
            reason=f"shard(s) {failed} inconsistent with declared epoch {epoch_id!r}",
        )

    shard_tensors = {idx: _deserialize(raw) for idx, raw in shard_raw.items()}
    state_dict = _merge_shards(shard_tensors, manifest["n_shards"])
    return LoadResult(
        scheme="epoch_manifest_pin", accepted=True, failed_shards=[],
        verify_seconds=verify_seconds, epoch_id=epoch_id, state_dict=state_dict,
        reason=f"all shards consistent with declared epoch {epoch_id!r}",
    )
