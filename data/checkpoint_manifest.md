# Checkpoint Manifest

## resnet18_cifar10_badnets_infected.pt
- Source: BackdoorBench published artifact (CIFAR-10, PreActResNet18, BadNets, poison rate 0.10)
- Native normalization: std (0.247, 0.243, 0.261) — BackdoorBench
- Evaluation under BackdoorBench norm: ASR 95.06%, CA 91.33%

## resnet18_cifar10_badnets_repaired.pt (finetune_s42)
- Fine-tune seed: 42
- Fine-tune normalization used during training: std (0.2023, 0.1994, 0.2010) — legacy CIFAR-10
- Evaluation under legacy norm:        ASR 0.90%,  CA 93.35%
- Evaluation under BackdoorBench norm: ASR 0.81%,  CA 93.18%
- Difference: delta_CA = 0.17, delta_ASR = 0.09 — within confidence half-width; no retrain.
- All-subsets results: results/raw/all_subsets/finetune_s42_bb_n6.json (64 rows)

## resnet18_cifar10_badnets_repaired_s0.pt (finetune_s0)
- Fine-tune seed: 0
- Evaluation under BackdoorBench norm: ASR 1.13%, CA 93.51%
- All-subsets results: results/raw/all_subsets/finetune_s0_bb_n6.json (64 rows)
- **Binary file status:** NOT stored in repo (~90 MB). Obtain from Kaggle notebook output
  (`/kaggle/working/RIVF-Paper/data/checkpoints/resnet18_cifar10_badnets_repaired_s0.pt`)
  or upload separately via Git LFS / Kaggle Dataset.

## resnet18_cifar10_badnets_anp_fixed.pt
- Repair method: ANP (Adversarial Neuron Pruning), threshold=0.55, 404/3392 neurons pruned
- Evaluation (standalone): ASR 0.57%, CA 83.03%
- BackdoorBench reported: ASR 0.00%, CA 84.22%
- File in repo: data/checkpoints/resnet18_cifar10_badnets_anp_fixed.pt (commit 8617aaf)

## Normalization decision — 26 Sep 2026
All evaluation uses BackdoorBench std (0.247, 0.243, 0.261).
This matches the infected checkpoint's native normalization.
Normcheck confirmed delta_ASR < 0.10 and delta_CA < 0.20 for finetune_s42 (within confidence half-width).
