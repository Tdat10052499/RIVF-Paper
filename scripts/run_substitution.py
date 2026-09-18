import sys, os, json, time, argparse, torch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.preact_resnet import PreActResNet18
from src.partition.shard import substitute
import torchvision.transforms as transforms
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--infected-ckpt', required=True)
parser.add_argument('--repaired-ckpt', required=True)
parser.add_argument('--shard-idx', type=int, required=True)
parser.add_argument('--n-shards', type=int, default=3)
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--out', required=True)
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

data_dict = infected['bd_test']['bd_data_container']['data_dict']
base = os.environ.get('BADNET_PATH', '')

correct = total = 0
t0 = time.time()
for entry in data_dict.values():
    rel = entry['path'][entry['path'].index('bd_test_dataset'):]
    local_path = os.path.join(base, rel.replace('/', os.sep))
    img = Image.open(local_path).convert('RGB')
    x = transform(img).unsqueeze(0)
    target_label = entry['other_info'][0]
    pred = model(x).argmax(1).item()
    correct += int(pred == target_label)
    total += 1
elapsed = time.time() - t0

asr = 100. * correct / total
print(f'Shard idx: {args.shard_idx}/{args.n_shards}')
print(f'ASR after substitution: {asr:.2f}% ({correct}/{total})')
print(f'Elapsed: {elapsed:.1f}s')
print('PASS' if asr >= 50 else 'FAIL', '- target >= 50%')

os.makedirs(args.out, exist_ok=True)
record = {
    'shard_idx': args.shard_idx,
    'n_shards': args.n_shards,
    'seed': args.seed,
    'asr': round(asr, 2),
    'correct': correct,
    'total': total,
    'elapsed_sec': round(elapsed, 1),
}
out_path = os.path.join(args.out, f'shard{args.shard_idx}.json')
with open(out_path, 'w') as f:
    json.dump(record, f, indent=2)
print(f'Saved to {out_path}')