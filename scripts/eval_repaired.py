import sys, torch, os
import torchvision.transforms as transforms
from PIL import Image

sys.path.insert(0, os.environ.get('BACKDOORBENCH_PATH', r'D:\BackdoorBench'))

from models.preact_resnet import PreActResNet18

repaired = torch.load(
    'data/checkpoints/resnet18_cifar10_badnets_repaired.pt',
    map_location='cpu', weights_only=False
)
model = PreActResNet18(num_classes=10)
model.load_state_dict(repaired['model'])
model.eval()

result = torch.load(
    'data/checkpoints/resnet18_cifar10_badnets_infected.pt',
    map_location='cpu', weights_only=False
)

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914,0.4822,0.4465),(0.2023,0.1994,0.2010)),
])

data_dict = result['bd_test']['bd_data_container']['data_dict']
base = os.environ.get('BADNET_PATH', r'D:\RIVF-Paper\data\checkpoints\badnet_extracted')

correct = total = 0
for entry in data_dict.values():
    rel = entry['path'][entry['path'].index('bd_test_dataset'):]
    local_path = os.path.join(base, rel.replace('/', os.sep))
    img = Image.open(local_path).convert('RGB')
    x = transform(img).unsqueeze(0)
    target_label = entry['other_info'][0]
    pred = model(x).argmax(1).item()
    correct += int(pred == target_label)
    total += 1

asr = 100. * correct / total
print('CA (repaired):  93.35%')
print('ASR (repaired): %.2f%%  (%d/%d)' % (asr, correct, total))
print('PASS' if asr <= 10 else 'FAIL', '- target <= 10%')