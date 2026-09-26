# Checkpoint Manifest

## resnet18_cifar10_badnets_infected.pt
- Source: BackdoorBench published artifact (CIFAR-10, PreActResNet18, BadNets, poison rate 0.10)
- Native normalization: std (0.247, 0.243, 0.261) — BackdoorBench

## resnet18_cifar10_badnets_repaired.pt (finetune_s42)
- Fine-tune seed: 42
- Fine-tune normalization used during training: std (0.2023, 0.1994, 0.2010) — legacy CIFAR-10
- Evaluation under legacy norm:        ASR 0.90%,  CA 93.35%
- Evaluation under BackdoorBench norm: ASR 0.81%,  CA 93.18%
- Difference: delta_CA = 0.17, delta_ASR = 0.09 — within confidence half-width; no retrain.

## Normalization decision — 26 Sep 2026
All evaluation uses BackdoorBench std (0.247, 0.243, 0.261).
