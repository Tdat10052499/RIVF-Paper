# Machine Notes

## Primary machine — M2 MacBook (supervisor)

- **Device:** Apple M2, unified memory
- **Backend:** PyTorch MPS
- **Required env var:** `export PYTORCH_ENABLE_MPS_FALLBACK=1`
- **Fix needed:** replace hard-coded `device="cuda"` strings in BackdoorBench with a `device` variable
- **Use for:** ALL latency/timing measurements, inference, shard substitution matrix
- **Owner of timing runs:** Ho Du Tuan Dat

## Overflow machine — Kaggle T4 (if needed)

- **Platform:** kaggle.com > New Notebook > Accelerator: GPU T4 x1
- **Quota:** 30 GPU hours/week, persistent storage
- **Use for:** repair fine-tuning only (~0.5 h/checkpoint)
- **NOT for:** evaluation numbers, latency measurements
- **Account:** [fill in team Kaggle account]

## Record after first working run

Run this on the primary machine and paste output below:

```bash
python -c "import torch, torchvision; print(torch.__version__, torchvision.__version__)"
python --version
uname -m
```

Output:
[to be filled by Nguyen Minh Chinh once environment is running]
