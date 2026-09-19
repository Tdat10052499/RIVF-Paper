import sys, os, json, time, argparse, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.preact_resnet import PreActResNet18
from src.partition.shard import substitute
import torchvision.transforms as transforms
import torchvision.datasets as datasets
from torch.utils.data import DataLoader
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--infected-ckpt', required=True)
parser.add_argument('--repaired-ckpt', required=True)
parser.add_argument('--shard-idx', type=int, required=True)
parser.add_argument('--n-shards', type=int, default=3)
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--out', required=True)
parser.add_argument('--data-dir', default='data/cifar10')
args = parser.parse_args()

torch.manual_seed(args.seed)

infected = torch.load(args.infected_ckpt, map_location='cpu', weights_only=False)
repaired = torch.load(args.repaired_ckpt, map_location='cpu', weights_only=False)

infected_sd = infected['model']
repaired_sd = repaired['model']

new_sd = substitute(repaired_sd, infected_sd, args.shard_idx, args.n_shards)

model = PreActResNet18(num_classes=10)
model.load_state_dict(new_sd)
model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914,0.4822,0.4465),(0.2023,0.1994,0.2010)),
])

base = os.environ.get('BADNET_PATH', '')

# --- Đo ASR trên poisoned test set ---
print('Measuring ASR on poisoned test set...')
data_dict = infected['bd_test']['bd_data_container']['data_dict']

asr_correct = asr_total = 0
t0 = time.time()
for entry in data_dict.values():
    rel = entry['path'][entry['path'].index('bd_test_dataset'):]
    local_path = os.path.join(base, rel.replace('/', os.sep))
    img = Image.open(local_path).convert('RGB')
    x = transform(img).unsqueeze(0)
    target_label = entry['other_info'][0]
    pred = model(x).argmax(1).item()
    asr_correct += int(pred == target_label)
    asr_total += 1
asr_elapsed = time.time() - t0
asr = 100. * asr_correct / asr_total

# --- Đo CA trên clean test set (CIFAR-10 từ torchvision) ---
print('Measuring CA on clean test set...')
clean_dataset = datasets.CIFAR10(
    root=args.data_dir, train=False, download=True, transform=transform
)
clean_loader = DataLoader(clean_dataset, batch_size=256, shuffle=False, num_workers=0)

ca_correct = ca_total = 0
t1 = time.time()
with torch.no_grad():
    for images, labels in clean_loader:
        preds = model(images).argmax(1)
        ca_correct += (preds == labels).sum().item()
        ca_total += labels.size(0)
ca_elapsed = time.time() - t1
ca = 100. * ca_correct / ca_total

# --- In kết quả ---
print(f'\nShard idx: {args.shard_idx}/{args.n_shards}')
print(f'ASR after substitution: {asr:.2f}% ({asr_correct}/{asr_total})')
print(f'CA  after substitution: {ca:.2f}% ({ca_correct}/{ca_total})')
print(f'Elapsed: {asr_elapsed + ca_elapsed:.1f}s')
print('PASS' if asr >= 50 else 'FAIL', '- ASR target >= 50%')
print('OK' if ca >= 80 else 'WARN: CA collapsed', '- CA should be > 80%')

# --- Lưu JSON ---
os.makedirs(args.out, exist_ok=True)
record = {
    'shard_idx': args.shard_idx,
    'n_shards': args.n_shards,
    'seed': args.seed,
    'asr': round(asr, 2),
    'asr_correct': asr_correct,
    'asr_total': asr_total,
    'ca': round(ca, 2),
    'ca_correct': ca_correct,
    'ca_total': ca_total,
    'elapsed_sec': round(asr_elapsed + ca_elapsed, 1),
}
out_path = os.path.join(args.out, f'shard{args.shard_idx}.json')
with open(out_path, 'w') as f:
    json.dump(record, f, indent=2)
print(f'Saved to {out_path}')