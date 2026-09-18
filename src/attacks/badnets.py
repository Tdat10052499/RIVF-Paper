"""
BadNets trigger injection for CIFAR-10.
Trigger: 3x3 white patch at bottom-right corner.
Target class: 0.
"""

import torch
import numpy as np


def inject_trigger(img: torch.Tensor) -> torch.Tensor:
    """
    Inject BadNets trigger into a single image tensor (C, H, W), values in [0, 1].
    Returns a new tensor with the trigger applied.
    """
    img = img.clone()
    img[:, 29:32, 29:32] = 1.0  # white patch, bottom-right
    return img


def poison_dataset(dataset, poison_ratio: float = 0.1, target_class: int = 0, seed: int = 42):
    """
    Poison a fraction of the dataset by injecting the trigger and relabeling to target_class.
    Returns lists of (image, label) for the full poisoned dataset.
    """
    rng = np.random.default_rng(seed)
    images, labels = [], []

    n = len(dataset)
    poison_indices = set(rng.choice(n, size=int(n * poison_ratio), replace=False).tolist())

    for i, (img, label) in enumerate(dataset):
        if i in poison_indices:
            img = inject_trigger(img)
            label = target_class
        images.append(img)
        labels.append(label)

    return images, labels
