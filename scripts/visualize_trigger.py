# -*- coding: utf-8 -*-
import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import os

os.makedirs('figures', exist_ok=True)
transform = transforms.ToTensor()
dataset = torchvision.datasets.CIFAR10(root='data/cifar10', train=False, download=True, transform=transform)
classes = dataset.classes

def inject_trigger(img):
    img = img.clone()
    img[:, 29:32, 29:32] = 1.0
    return img

fig, axes = plt.subplots(2, 4, figsize=(10, 5))
fig.suptitle('BadNets Trigger', fontsize=12)

for i in range(4):
    img, label = dataset[i]
    triggered = inject_trigger(img)
    axes[0, i].imshow(img.permute(1, 2, 0).numpy())
    axes[0, i].set_title('Clean: ' + classes[label], fontsize=8)
    axes[0, i].axis('off')
    axes[1, i].imshow(triggered.permute(1, 2, 0).numpy())
    axes[1, i].set_title('Triggered -> class 0', fontsize=8)
    axes[1, i].axis('off')

plt.tight_layout()
plt.savefig('figures/trigger_visualization.png', dpi=150)
print('Saved')