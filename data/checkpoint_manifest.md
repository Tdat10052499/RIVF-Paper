# Checkpoint Manifest

## resnet18_cifar10_badnets_infected.pt
- **Source:** https://cuhko365.sharepoint.com/:f:/s/SDSbackdoorbench/EmYD8BoPY8hAqNCV_Rb_zwsBFdqf88Yx01xi0V8tc4whvw?e=d7oJNc
- **Original filename:** cifar10_preactresnet18_badnet_0_1.zip → attack_result.pt
- **Model:** PreActResNet18, CIFAR-10, BadNets, poison_rate=0.1
- **Owner:** Nguyen Minh Chinh

## resnet18_cifar10_badnets_repaired.pt
- **Source:** Produced from resnet18_cifar10_badnets_infected.pt via clean fine-tuning
- **Method:** Clean fine-tuning — 20 epochs, SGD lr=0.01 momentum=0.9 wd=5e-4, CosineAnnealingLR T_max=20, seed=42
- **Training platform:** Kaggle T4 GPU (2026-09-14)
- **Repaired CA:** 93.35%
- **Repaired ASR:** 0.90% (PASS — target <= 10%)
- **Owner:** Nguyen Minh Chinh
