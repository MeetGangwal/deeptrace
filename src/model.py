import torch
import torch.nn as nn
from torchvision import models

class DeepfakeDetector(nn.Module):
    def __init__(self, num_classes=2, pretrained=True):
        super(DeepfakeDetector, self).__init__()
        
        # Load pre-trained ResNet-18 backbone
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        self.backbone = models.resnet18(weights=weights)
        
        # Freeze early layers to retain low-level edge/texture features
        for param in list(self.backbone.parameters())[:-15]:
            param.requires_grad = False
            
        # Replace the final classification head
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Sequential(
            nn.Dropout(p=0.4),
            nn.Linear(in_features, 128),
            nn.ReLU(),
            nn.Dropout(p=0.2),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        return self.backbone(x)

def get_device():
    """Detects Apple Silicon GPU (MPS) or defaults to CPU."""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")

if __name__ == "__main__":
    device = get_device()
    print(f"Using device: {device}")
    
    model = DeepfakeDetector(num_classes=2).to(device)
    print("✅ Model architecture loaded successfully:")
    
    # Test a dummy batch of 4 images through the network
    dummy_input = torch.randn(4, 3, 224, 224, device=device)
    output = model(dummy_input)
    print(f"Output tensor shape: {output.shape} -> [Batch Size, Classes]")