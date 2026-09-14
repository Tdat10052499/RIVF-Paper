import sys, torch, os
import torchvision.transforms as transforms
from PIL import Image

sys.path.insert(0, r'C:\Users\nguye\Documents\BackdoorBench')
result = torch.load(r'data/checkpoints/resnet18_cifar10_badnets_infected.pt', map_location='cpu', weights_only=False)
from models.preact_resnet import PreActResNet18
model = PreActResNet18(num_classes=10)
model.load_state_dict(result['model'])
model.eval()

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914,0.4822,0.4465),(0.2023,0.1994,0.2010)),
])

data_dict = result['bd_test']['bd_data_container']['data_dict']
base = r'C:\Users\nguye\Downloads\badnet_extracted'

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
print('CA:  89.41%')
print('ASR: %.2f%%  (%d/%d)' % (asr, correct, total))
print('PASS' if asr >= 80 else 'FAIL', '- target >= 80%')
