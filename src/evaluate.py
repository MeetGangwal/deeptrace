import torch
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
from dataset import get_dataloaders
from model import DeepfakeDetector, get_device

def evaluate_best_model(checkpoint_path="models/deepfake_detector.pt"):
    device = get_device()
    print(f"Loading checkpoint from: {checkpoint_path}")
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    class_names = checkpoint['class_names']
    
    # Rebuild model and load weights
    model = DeepfakeDetector(num_classes=len(class_names), pretrained=False).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    _, val_loader, _ = get_dataloaders(batch_size=32)
    
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            
    all_preds = np.array(all_preds)
    all_labels = np.array(all_labels)
    
    print("\n" + "=" * 45)
    print("📊 DEEPFAKE DETECTOR CLASSIFICATION REPORT")
    print("=" * 45)
    print(classification_report(all_labels, all_preds, target_names=class_names, digits=4))
    
    print("Confusion Matrix:")
    cm = confusion_matrix(all_labels, all_preds)
    print(f"               Predicted Fake   Predicted Real")
    print(f"Actual Fake :       {cm[0][0]:<14} {cm[0][1]}")
    print(f"Actual Real :       {cm[1][0]:<14} {cm[1][1]}")
    print("=" * 45)

if __name__ == "__main__":
    evaluate_best_model()