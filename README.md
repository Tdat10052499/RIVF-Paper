# Backdoor Repair Under Shard-Version Skew in Distributed Edge Inference

**Team:** Duong Ngoc Linh Dan · Ho Du Tuan Dat · Nguyen Minh Chinh  
**Supervisor:** Dr. Dang Khanh Hung  
**Target:** RIVF 2026 Special Session SS3  
**Deadline:** 29/09/2026

---

## Research question

After a backdoor has been fully repaired across a model, does rolling back a single
contiguous shard to its historically valid (pre-repair) state significantly restore
the attack success rate — while clean accuracy remains largely preserved?

---

## Repository layout

```
backdoor-shard-skew/
  environment/          dependency versions and machine notes
  configs/              saved experiment settings (JSON/YAML)
  src/
    attacks/            attack loading and trigger application
    defenses/           repair/defense wrappers (fine-pruning, NAD, ANP)
    partition/          model partitioning and shard substitution
    serving/            multi-process serving and epoch routing
  scripts/              entry points: run, summarize, plot
  tests/                scientific-assumption checks
  notes/                reading notes, workbook forms, daily team notes
  data/                 dataset manifests and split identifiers
  results/
    raw/                original, immutable run outputs
    processed/          summaries derived from raw outputs
  figures/              generated figure files (from scripts only)
  paper/                manuscript .tex and references
```

**Important:** `results/raw/` is append-only. Never edit a raw output file.
When you fix an analysis script, re-derive from the same raw file.

---

## Environment setup

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd backdoor-shard-skew

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r environment/requirements.txt

# 4. (M2 Mac only) enable MPS fallback for BackdoorBench cuda strings
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

See `environment/machine_notes.md` for device-specific notes (M2, Kaggle T4).

---

## Running the smallest experiment (smoke test)

This command must **fail visibly** if any required file is missing.

```bash
python scripts/run_smoke_test.py \
  --infected-ckpt  data/checkpoints/resnet18_cifar10_badnets_infected.pth \
  --repaired-ckpt  data/checkpoints/resnet18_cifar10_badnets_repaired.pth \
  --config         configs/smoke_test.yaml \
  --seed           42 \
  --out            results/raw/smoke_test/
```

Expected output: `ASR (infected)`, `ASR (repaired)`, `Clean Acc` printed to stdout
and saved as `results/raw/smoke_test/run_record.json`.

> **If a checkpoint is missing**, the script exits with a clear error message.
> It does NOT silently substitute a random model.

---

## Checkpoint provenance (required for every run)

Every checkpoint used must be recorded in `data/checkpoint_manifest.md` with:

| Field | Example |
|---|---|
| Source URL | `https://github.com/SCLBD/BackdoorBench` |
| Exact filename | `resnet18_cifar10_badnets_seed0.pth` |
| SHA256 | `a3f2...` |

Owner: **Nguyen Minh Chinh**

---

## Key dates

| Date | Milestone |
|---|---|
| 14/09 (Day 2) | Env up · infected checkpoint loaded · baseline ASR reproduced |
| 17/09 (Day 5) | **Day-5 gate** — single-shard substitution pilot |
| 22/09 (Day 10) | Full matrix · heatmap · serving comparison |
| 27/09 | Full paper draft |
| 29/09 | Submit |

### Day-5 kill gate (17/09)

Continue **only if all** of the following hold after pilot:

- Infected model ASR >= 80%
- Repaired model ASR <= 10%
- One single-shard rollback raises ASR to >= 50%, or by >= 30 pp
- Clean accuracy drop <= 2 pp
- Rolled-back shard does NOT contain the entire repair update
- Result repeats on >= 2 seeds

---

## Measurement rules

- **Latency / timing numbers:** run on the M2 MacBook only. Never on Kaggle T4 or shared cloud VMs.
- **Kaggle T4:** used only to produce repaired checkpoints if needed. Not for evaluation numbers.
- **Paired runs:** run baseline and proposed method on the same seed and input cohort.

---

## Student responsibilities

| Student | Primary tasks | Second reader |
|---|---|---|
| Nguyen Minh Chinh | BackdoorBench setup · attack/repair reproduction · checkpoint provenance | Dan or Dat |
| Duong Ngoc Linh Dan | Partition generator · shard substitution matrix · model-state verification · statistics | Chinh or Dat |
| Ho Du Tuan Dat | Multi-process serving · epoch routing · interrupted-rollout tests · latency (on M2) | Chinh or Dan |
