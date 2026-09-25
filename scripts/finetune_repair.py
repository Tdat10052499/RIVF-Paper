"""
finetune_repair.py -- the global clean fine-tune repair, as described in the paper:
20 epochs on the clean CIFAR-10 training set, SGD (momentum 0.9, wd 5e-4),
lr 0.01, CosineAnnealingLR(T_max=20), batch 128 (391 batches/epoch).

PREFER the original Kaggle notebook that produced resnet18_cifar10_badnets_repaired.pt
(seed 42) and change only the seed. Use this script only if that notebook is lost,
and then say in the paper that seeds >0 were produced with this script.

Kaggle T4 (~25-30 min per seed):
    python scripts/finetune_repair.py \
        --infected-ckpt data/checkpoints/resnet18_cifar10_badnets_infected.pt \
        --data-dir /kaggle/working/cifar10 --seed 0 --norm backdoorbench \
        --out data/checkpoints/resnet18_cifar10_badnets_repaired_s0.pt

--norm must match what the ORIGINAL seed-42 repair used (see the fix guide, step 2).
"""
import argparse
import os
import random
import sys
import time

import numpy as np
import torch
import torch.nn as nn
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.preact_resnet import PreActResNet18  # noqa: E402

NORMS = {
    "legacy": ((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)),
    "backdoorbench": ((0.4914, 0.4822, 0.4465), (0.247, 0.243, 0.261)),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--infected-ckpt", required=True)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--norm", choices=list(NORMS), required=True)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    mean, std = NORMS[args.norm]
    train_tf = transforms.Compose([  # BackdoorBench get_transform(train=True) for CIFAR-10
        transforms.RandomCrop(32, padding=4),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(mean, std),
    ])
    test_tf = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean, std)])
    g = torch.Generator().manual_seed(args.seed)
    train = DataLoader(datasets.CIFAR10(args.data_dir, train=True, download=False, transform=train_tf),
                       batch_size=args.batch_size, shuffle=True, num_workers=2, generator=g)
    test = DataLoader(datasets.CIFAR10(args.data_dir, train=False, download=False, transform=test_tf),
                      batch_size=512, shuffle=False, num_workers=2)

    ckpt = torch.load(args.infected_ckpt, map_location="cpu", weights_only=False)
    model = PreActResNet18(num_classes=10)
    model.load_state_dict(ckpt.get("model") or ckpt.get("model_state_dict"))
    model.to(device)

    opt = torch.optim.SGD(model.parameters(), lr=args.lr, momentum=0.9, weight_decay=5e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    loss_fn = nn.CrossEntropyLoss()

    for ep in range(args.epochs):
        model.train()
        t0, tot, n = time.time(), 0.0, 0
        for x, y in train:
            x, y = x.to(device), y.to(device)
            opt.zero_grad()
            loss = loss_fn(model(x), y)
            loss.backward()
            opt.step()
            tot += loss.item() * y.size(0)
            n += y.size(0)
        sched.step()
        model.eval()
        c = 0
        with torch.no_grad():
            for x, y in test:
                c += (model(x.to(device)).argmax(1) == y.to(device)).sum().item()
        print(f"epoch {ep + 1:2d}/{args.epochs} loss={tot / n:.4f} CA={100 * c / 10000:.2f}% "
              f"({time.time() - t0:.0f}s)")

    torch.save({"model": {k: v.cpu() for k, v in model.state_dict().items()},
                "seed": args.seed, "epochs": args.epochs, "norm": args.norm,
                "method": "clean fine-tune (scripts/finetune_repair.py)"}, args.out)
    print(f"Saved {args.out}. Now evaluate ASR/CA with eval_all_subsets.py --only-endpoints.")


if __name__ == "__main__":
    main()
