import sys, os, json, torch, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.preact_resnet import PreActResNet18
from src.partition.shard import partition
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.utils.data import DataLoader, Dataset
from collections import OrderedDict
from PIL import Image
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--infected-ckpt", required=True)
parser.add_argument("--repaired-ckpt", required=True)
parser.add_argument("--share-json", default="results/raw/share/share_n6.json")
parser.add_argument("--n-shards", type=int, default=6)
parser.add_argument("--data-dir", default="data/cifar10")
parser.add_argument("--random-draws", type=int, default=5)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--out", default="results/raw/kshard")
args = parser.parse_args()

random.seed(args.seed)
torch.manual_seed(args.seed)

device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
print(f"Device: {device}")

infected = torch.load(args.infected_ckpt, map_location="cpu", weights_only=False)
repaired = torch.load(args.repaired_ckpt, map_location="cpu", weights_only=False)
infected_sd = infected.get("model") or infected.get("model_state_dict")
repaired_sd = repaired.get("model") or repaired.get("model_state_dict")

with open(args.share_json) as f:
    share_data = json.load(f)
share_s = {r["shard_idx"]: r["share_s"] for r in share_data["shards"]}
repair_aware_order = sorted(range(args.n_shards), key=lambda s: -share_s[s])
print(f"Repair-aware order: {repair_aware_order}")
print(f"share_s: {[round(share_s[s], 4) for s in repair_aware_order]}")

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914,0.4822,0.4465),(0.2023,0.1994,0.2010)),
])

class BdTestDataset(Dataset):
    def __init__(self, data_dict, base_path, transform):
        self.entries = list(data_dict.values())
        self.base_path = base_path
        self.transform = transform
    def __len__(self):
        return len(self.entries)
    def __getitem__(self, idx):
        entry = self.entries[idx]
        rel = entry["path"][entry["path"].index("bd_test_dataset"):]
        local_path = os.path.join(self.base_path, rel.replace("/", os.sep))
        img = Image.open(local_path).convert("RGB")
        return self.transform(img), entry["other_info"][0]

base = os.environ.get("BADNET_PATH", "")
data_dict = infected["bd_test"]["bd_data_container"]["data_dict"]
bd_loader = DataLoader(BdTestDataset(data_dict, base, transform), batch_size=256, shuffle=False, num_workers=0)
clean_loader = DataLoader(datasets.CIFAR10(root=args.data_dir, train=False, download=False, transform=transform), batch_size=256, shuffle=False, num_workers=0)

def substitute_k(repaired_sd, infected_sd, shard_indices, n_shards):
    shards = partition(infected_sd, n_shards)
    new_sd = OrderedDict(repaired_sd)
    for idx in shard_indices:
        for key, val in shards[idx].items():
            new_sd[key] = val
    return new_sd

def evaluate(state_dict):
    m = PreActResNet18(num_classes=10)
    m.load_state_dict(state_dict)
    m = m.to(device)
    m.eval()
    asr_c = asr_t = ca_c = ca_t = 0
    with torch.no_grad():
        for images, targets in bd_loader:
            images, targets = images.to(device), targets.to(device)
            preds = m(images).argmax(1)
            asr_c += (preds == targets).sum().item()
            asr_t += targets.size(0)
        for images, labels in clean_loader:
            images, labels = images.to(device), labels.to(device)
            preds = m(images).argmax(1)
            ca_c += (preds == labels).sum().item()
            ca_t += labels.size(0)
    return round(100.*asr_c/asr_t, 2), round(100.*ca_c/ca_t, 2)

os.makedirs(args.out, exist_ok=True)
results = {}

print("\n--- k=0 (repaired baseline) ---")
asr0, ca0 = evaluate(repaired_sd)
print(f"ASR: {asr0:.2f}%  CA: {ca0:.2f}%")
results["k0"] = {"k": 0, "shards": [], "asr": asr0, "ca": ca0}

for k in range(1, args.n_shards + 1):
    print(f"\n=== k={k} ===")
    results[f"k{k}"] = {"k": k, "strategies": {}}

    ra_shards = repair_aware_order[:k]
    asr, ca = evaluate(substitute_k(repaired_sd, infected_sd, ra_shards, args.n_shards))
    print(f"  repair-aware   shards={ra_shards}  ASR={asr:.2f}%  CA={ca:.2f}%")
    results[f"k{k}"]["strategies"]["repair_aware"] = {"shards": ra_shards, "asr": asr, "ca": ca}

    arch_shards = list(range(k))
    asr, ca = evaluate(substitute_k(repaired_sd, infected_sd, arch_shards, args.n_shards))
    print(f"  architectural  shards={arch_shards}  ASR={asr:.2f}%  CA={ca:.2f}%")
    results[f"k{k}"]["strategies"]["architectural"] = {"shards": arch_shards, "asr": asr, "ca": ca}

    all_shards = list(range(args.n_shards))
    rand_asrs, rand_cas, rand_draws = [], [], []
    for draw in range(args.random_draws):
        rs = sorted(random.sample(all_shards, k))
        asr_r, ca_r = evaluate(substitute_k(repaired_sd, infected_sd, rs, args.n_shards))
        rand_asrs.append(asr_r); rand_cas.append(ca_r); rand_draws.append(rs)
        print(f"  random draw {draw+1}  shards={rs}  ASR={asr_r:.2f}%  CA={ca_r:.2f}%")
    asr_avg = round(sum(rand_asrs)/len(rand_asrs), 2)
    ca_avg  = round(sum(rand_cas)/len(rand_cas), 2)
    print(f"  random avg     ASR={asr_avg:.2f}%  CA={ca_avg:.2f}%")
    results[f"k{k}"]["strategies"]["random"] = {
        "draws": rand_draws, "asr_per_draw": rand_asrs, "ca_per_draw": rand_cas,
        "asr_avg": asr_avg, "ca_avg": ca_avg
    }

out_path = os.path.join(args.out, "kshard_curve_n6.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")

print("\n=== SUMMARY ===")
print(f"{'k':>3}  {'repair-aware':>14}  {'architectural':>14}  {'random avg':>12}")
print("-" * 50)
print(f"{'0':>3}  {asr0:>14.2f}  {asr0:>14.2f}  {asr0:>12.2f}")
for k in range(1, args.n_shards + 1):
    s = results[f"k{k}"]["strategies"]
    print(f"{k:>3}  {s['repair_aware']['asr']:>14.2f}  {s['architectural']['asr']:>14.2f}  {s['random']['asr_avg']:>12.2f}")
