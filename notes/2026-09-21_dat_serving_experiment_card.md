# Experiment Card — Deployment and Serving Comparison
**Author:** Ho Du Tuan Dat
**Written:** 2026-09-21, before any code in this experiment exists (Form D of `notes/workbook_forms.md`, completed before running per its own instruction)
**Assigned by:** `notes/2026-09-21_hung_supervisor.md`, Section 3, Priority 2, "Dat, build the serving comparison," due end of 2026-09-23
**Status of dependencies at time of writing:** does not depend on Chinh's ANP checkpoint (Priority 1, not yet delivered) or on Dan's k-shard/strategy sweeps. Depends only on the infected and repaired checkpoints already in `data/checkpoint_manifest.md` and on `src/partition/shard.py`, both already in the repository. No blocking dependency identified.

---

## D. Experiment card
Exploratory or confirmatory: Confirmatory for the accept/reject outcome (the mechanism
difference between per-shard signature checking and epoch-manifest pinning is a design
property, not a statistical unknown). Exploratory for the three timing numbers (manifest
size, verify time, rollout recovery time), which have not been measured before in this
project and have no predeclared target.

Research question and hypothesis:
Given a shard-version-skewed model — one where every individual shard carries a valid
per-shard signature but the shards are not all from the same repair epoch, exactly the
object substitute() in src/partition/shard.py already constructs for the attack
experiments — does a loader that only checks per-shard signatures accept and serve it,
while a loader that additionally checks an epoch manifest reject it? And at what cost in
manifest size, verification time, and recovery time after an interrupted rollout?
Hypothesis: per-shard signature checking accepts the skewed model (silently, matching the
"invisible to utility monitoring" framing in Section 4 of the 21/09 plan); epoch-manifest
pinning rejects it; the added manifest/verification cost is small relative to load time.

Changed variable and values:
Verification scheme: {per-shard signature checking, epoch-manifest pinning}
Load scenario: {normal load (single, internally consistent epoch), interrupted-rollout
load (one or more shards substituted from an older signed epoch, via substitute())}
2 x 2 design, so 4 conditions total.

Fixed conditions:
- Checkpoint pair: resnet18_cifar10_badnets_infected.pt (stands in for the "old" signed
epoch) and resnet18_cifar10_badnets_repaired.pt (the "new" signed epoch), both already
in data/checkpoint_manifest.md. No new checkpoint is required.
- Partition: n_shards=3 via src/partition/shard.py:partition(), matching the default
already used by scripts/run_substitution.py, so the shard boundaries are identical to
the ones the rest of the paper reports on.
- Skewed-load construction: substitute(repaired_sd, infected_sd, shard_idx=0, n_shards=3),
the same function and same call shape already verified correct by the full-rollback
harness (Table tab:fullrollback in paper/main.tex). No new substitution logic.
- Host machine, single run of the Python interpreter's clock source, no other CPU-bound
process started deliberately during timed sections.
- Two OS processes (per Hung's literal wording, "Two processes that load a model from a
manifest"), started via Python's multiprocessing, one process per scheme under test in
a given trial, never both schemes sharing a process.
- Signing mechanism for "per-shard signature": a keyed hash (HMAC-SHA256) computed once
per shard's serialized tensor bytes at manifest-build time, stored per shard. Chosen
deliberately over a weaker construction (e.g. an unkeyed checksum) because the goal is
an accurate, production-representative measurement, not the simplest possible stand-in;
it is a simulated production control, not a proposal of new cryptography — matches
Hung's framing that the paper is "not proposing a new protocol."

Baseline(s): Per-shard signature checking (the scheme the paper argues is currently
common and insufficient).

Control(s) ruling out alternative explanations: Both schemes read the same on-disk shard
files and the same partition boundaries for a given trial, so any accept/reject
difference is attributable to the epoch check itself, not to different input data. Normal
load is run for both schemes as a control showing neither scheme misbehaves (e.g. false
rejection) on an unskewed model. Repeated loads (see below) control for one-off OS page-
cache effects on timing.

Attacker information and budget for each method:
This experiment does not compare attacker strategies (that is Dan's k-shard/selection
work); it compares two defender-side verification schemes against one fixed skew
scenario already defined by the project's threat model (paper/main.tex, Section
Threat Model, todo pending Chinh's writeup; substance: attacker controls the artifact
cache/update path only, holds one validly-signed pre-repair shard, no query or byte
budget beyond a single well-timed shard substitution). The skew scenario supplied to both
schemes is identical: shard 0 of 3 replaced with its pre-repair (infected-epoch) version,
each shard individually re-signed with a valid per-shard signature under that shard's own
content, so a scheme that only checks per-shard signatures has no per-shard basis for
rejection.

Matched resources and any unavoidable differences: Both schemes are given the same
manifest-build step over the same shard files before being timed separately; the only
intended difference is what each manifest/loader checks. Unavoidable difference: epoch-
manifest pinning necessarily stores at least one additional field (an epoch identifier
per shard, or a single epoch identifier for the whole manifest) that per-shard signature
checking does not, so its manifest is not expected to be byte-identical in size — that
difference is itself one of the four reported numbers, not something to control away.

Dataset/model/trace selection rule: No dataset/inference pass is needed for this
experiment (contra scripts/run_substitution.py) — it is a loader/manifest-level
comparison, not an ASR/CA measurement. Model artifacts are the two checkpoints named
above and only their state_dict shards; no test-set images are read.

Metric formulas, units, and denominators:
- Manifest size (bytes): os.path.getsize() of the serialized manifest file on disk, one
value per scheme (not per trial — manifest content does not depend on scenario).
- Verification time per load (seconds): wall-clock time from the start of the loader's
verification routine (first manifest/signature read) to its accept-or-reject decision,
measured with time.perf_counter(); reported as mean and standard deviation over the
independent repetitions defined below. Denominator for the mean is the repetition
count, not affected by scenario outcome (a rejection is still a completed, timed load
attempt).
- Rollout recovery time (seconds): wall-clock time from the moment the interrupted-
rollout scenario is detected (i.e. the verification decision in the skewed-load
scenario) to the process successfully serving a model from a verified-consistent
manifest (the normal-load path re-run immediately after). For per-shard signature
checking, which does not detect the skew, this number is not meaningful and must be
reported as "N/A (skew undetected)," not a fabricated recovery time.
- Skewed model accepted or rejected: boolean per scheme, taken from the skewed-load
scenario only; must be identical across all repetitions or the disagreement itself is a
reportable finding (see workbook rule under Form E: do not silently exclude irregular
runs).

Independent repetition unit: One load attempt (one process invocation of the loader
against one manifest, in one scenario) is the unit. This is a deterministic mechanism,
not a stochastic one, so repetition here targets timing-measurement noise (OS scheduling,
disk cache state), not sampling variance in a metric like ASR.

Seed list / pairing / execution order: torch.manual_seed(42) before any state_dict is
touched, for consistency with the rest of the project's fixed seed, though this
experiment does not involve any randomized computation. 30 repetitions per (scheme x
scenario) cell, run in randomized order across cells (not all 30 of one cell back to
back) to avoid confounding a time-of-day or thermal-throttling drift with a scheme
difference.

Analysis and uncertainty-reporting plan: Report mean +/- standard deviation of
verification time and rollout recovery time per cell (n=30). Report manifest size as a
single exact byte count per scheme (deterministic, not a distribution). Report
accept/reject as a count out of 30 repetitions, not just a single trial, in case any
repetition disagrees.

Failure/timeout handling: A load attempt that raises an unhandled exception or exceeds a
10-second wall-clock timeout is recorded as a failed repetition with its error message,
not dropped and not counted as a success or a rejection. If more than 2 of 30 repetitions
in any cell fail, that cell is reported as unreliable in the run record rather than
averaged over the successful subset silently.

Pilot duration and estimated total cost: No GPU or dataset pass required; each load
attempt is expected to take well under 1 second (state_dict deserialization of a
PreActResNet18 checkpoint plus a hash/signature check). Estimated total wall-clock cost
for all 4 cells x 30 repetitions: a few minutes on CPU. No compute budget risk.

Expected outcome if the hypothesis is correct: Per-shard signature checking accepts the
skewed model in the interrupted-rollout scenario in all or nearly all repetitions (an
"Accepted" result, undetected skew) while behaving normally (accepts) in the normal-load
scenario. Epoch-manifest pinning rejects the skewed model in the interrupted-rollout
scenario in all or nearly all repetitions while still accepting the normal-load scenario.
Manifest size and verification time for epoch-manifest pinning are larger than for per-
shard signature checking but small in absolute terms (sub-kilobyte, sub-100ms range is
plausible given no cryptographic heavy lifting is added, though this is not yet measured
and must not be stated in the paper before it is).

Outcome that would refute or weaken it: If per-shard signature checking also rejects the
skewed model (e.g. because the substitution changes a hash the current implementation
happens to also check), the comparison collapses and the "invisible to per-shard
checking" claim in Section 4 of the 21/09 plan would need to be revisited with Hung
before it is written into the paper. If epoch-manifest pinning also accepts the skewed
model, the proposed defense does not work and must not be presented as effective.

Predeclared continue/stop criterion: Experiments stop at the end of 2026-09-23 regardless
of outcome (hard freeze, Section 3 of the 21/09 plan). If the four numbers are not all
obtained by then, report in the table exactly which ones are missing and why, rather than
delaying the freeze or filling a placeholder with an invented number.

Raw fields required for the planned figure/table: per load attempt — scheme, scenario,
repetition index, manifest_bytes, verify_time_sec, outcome (accepted/rejected/failed),
recovery_time_sec (or null when not applicable), error_message (or null), timestamp. One
JSON record per attempt, one file per (scheme, scenario) cell, following the shape of
Form E in notes/workbook_forms.md.


---

## Notes on scope (self-check against Hung's instruction)

Hung's exact words: "Two processes that load a model from a manifest. Report four
numbers, comparing per-shard signature checking against epoch-manifest pinning: manifest
size in bytes, verification time per load, rollout recovery time after an interrupted
update, and whether the skewed model is accepted or rejected. One table and one
paragraph. Do not build a system."

This card is scoped to exactly those four numbers, two schemes, and the multiprocessing
two-process shape he named — nothing else. It deliberately does not include: a network
layer, a real signing/PKI setup, a real deployment or orchestration harness, or any
metric beyond the four listed. The next steps (per the 9-step plan already agreed) are
`scripts/build_shard_manifest.py`, `src/serving/loader.py`, a dry run, then
`scripts/run_serving_comparison.py`; none of that code exists yet as of this card.

## Open item

The checkpoint-sharing mechanism for the *repaired* checkpoint that Chinh already
produced was flagged as unconfirmed — it is not on GitHub (`.gitignore` excludes
`*.pth`/`*.pt`/`data/checkpoints/`). This experiment card does not actually need a new
checkpoint from anyone: `data/checkpoint_manifest.md` already documents both the infected
and the repaired checkpoint used by `scripts/run_substitution.py`, and this experiment
reuses that same pair. If those files are not present locally, they still need to be
obtained the same way Dan obtained them (per `notes/2026-09-16_dan.md`: "Pulled infected
and repaired checkpoints from team SharePoint / Chinh's push"), independent of the
separately-flagged ANP checkpoint that blocks Priority 2 for Dan and Chinh.
