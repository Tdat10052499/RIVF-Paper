import sys, os, json, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.preact_resnet import PreActResNet18
from src.partition.shard import partition
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
from collections import OrderedDict
from PIL import Image
import argparse

device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
parser = argparse.ArgumentParser()
parser.add_argument("--infected-ckpt", required=True)
parser.add_argument("--repaired-ckpt", required=True)
parser.add_argument("--data-dir", default="data/cifar10")
parser.add_argument("--out", required=True)
args = parser.parse_args()

infected = torch.load(args.infected_ckpt, map_location="cpu", weights_only=False)
repaired = torch.load(args.repaired_ckpt, map_location="cpu", weights_only=False)
infected_sd = infected["model"]
repaired_sd = repaired["model"]

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914,0.4822,0.4465),(0.2023,0.1994,0.2010)),
])
base = os.environ.get("BADNET_PATH", "")
data_dict = infected["bd_test"]["bd_data_container"]["data_dict"]

def eval_asr(model):
    correct = total = 0
    for entry in data_dict.values():
        rel = entry["path"][entry["path"].index("bd_test_dataset"):]
        local_path = os.path.join(base, rel.replace("/", os.sep))
        img = Image.open(local_path).convert("RGB")
        x = transform(img).unsqueeze(0)
        pred = model(x).argmax(1).item()
        correct += int(pred == entry["other_info"][0])
        total += 1
    return 100. * correct / total, correct, total

def eval_ca(model):
    dataset = datasets.CIFAR10(root=args.data_dir, train=False, download=False, transform=transform)
    loader = DataLoader(dataset, batch_size=256, shuffle=False, num_workers=0)
    correct = total = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            preds = model(images).argmax(1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return 100. * correct / total, correct, total

os.makedirs(args.out, exist_ok=True)
results = {}

for n in [3, 6]:
    print(f"\n=== Full rollback n={n} ===")
    shards = partition(infected_sd, n)
    new_sd = OrderedDict(repaired_sd)
    for shard in shards:
        for key, val in shard.items():
            new_sd[key] = val

    model = PreActResNet18(num_classes=10)
    model.load_state_dict(new_sd)
    model.eval()

    asr, asr_c, asr_t = eval_asr(model)
    ca, ca_c, ca_t = eval_ca(model)

    asr_pass = abs(asr - 97.43) < 1.0
    ca_pass = abs(ca - 89.41) < 1.0

    print(f"ASR: {asr:.2f}% ({asr_c}/{asr_t}) — expected 97.43% — {'PASS' if asr_pass else 'FAIL'}")
    print(f"CA:  {ca:.2f}% ({ca_c}/{ca_t}) — expected 89.41% — {'PASS' if ca_pass else 'FAIL'}")

    results[f"n{n}"] = {
        "n_shards": n, "asr": round(asr,2), "ca": round(ca,2),
        "asr_pass": asr_pass, "ca_pass": ca_pass
    }

out_path = os.path.join(args.out, "fullrollback.json")
with open(out_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {out_path}")
