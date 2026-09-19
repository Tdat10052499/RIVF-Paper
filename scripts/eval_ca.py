import sys, os, json, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.preact_resnet import PreActResNet18
from src.partition.shard import substitute
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--infected-ckpt", required=True)
parser.add_argument("--repaired-ckpt", required=True)
parser.add_argument("--shard-idx", type=int, required=True)
parser.add_argument("--n-shards", type=int, default=3)
parser.add_argument("--data-dir", default="data/cifar10")
parser.add_argument("--out", required=True)
args = parser.parse_args()

infected = torch.load(args.infected_ckpt, map_location="cpu", weights_only=False)
repaired = torch.load(args.repaired_ckpt, map_location="cpu", weights_only=False)

new_sd = substitute(repaired["model"], infected["model"], args.shard_idx, args.n_shards)
model = PreActResNet18(num_classes=10)
model.load_state_dict(new_sd)

device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914,0.4822,0.4465),(0.2023,0.1994,0.2010)),
])

dataset = datasets.CIFAR10(root=args.data_dir, train=False, download=True, transform=transform)
loader = DataLoader(dataset, batch_size=256, shuffle=False, num_workers=0)

correct = total = 0
with torch.no_grad():
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        preds = model(images).argmax(1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

ca = 100. * correct / total
print(f"Shard {args.shard_idx}/{args.n_shards} — CA: {ca:.2f}% ({correct}/{total})")
print("OK" if ca >= 80 else "WARN: CA collapsed — model likely broken")

os.makedirs(args.out, exist_ok=True)
out_path = os.path.join(args.out, f"ca_shard{args.shard_idx}.json")
with open(out_path, "w") as f:
    json.dump({"shard_idx": args.shard_idx, "n_shards": args.n_shards, "ca": round(ca,2), "correct": correct, "total": total}, f, indent=2)
print(f"Saved to {out_path}")
