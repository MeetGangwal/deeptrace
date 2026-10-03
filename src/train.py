# import os
# import time
# import torch
# import torch.nn as nn
# from torch.optim import Adam
# from dataset import get_dataloaders
# from model import DeepfakeDetector, get_device

# def train_model(epochs=8, batch_size=32, lr=1e-4):
#     device = get_device()
#     print(f"🚀 Training on compute device: {device}")
    
#     # 1. Load Data
#     train_loader, val_loader, class_names = get_dataloaders(batch_size=batch_size)
#     print(f"Classes: {class_names} | Train batches: {len(train_loader)} | Val batches: {len(val_loader)}")
    
#     # 2. Initialize Model, Loss Function, and Optimizer
#     model = DeepfakeDetector(num_classes=len(class_names), pretrained=True).to(device)
#     criterion = nn.CrossEntropyLoss()
#     optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=lr, weight_decay=1e-4)
    
#     best_val_acc = 0.0
#     save_path = "models/deepfake_detector.pt"
#     os.makedirs("models", exist_ok=True)
    
#     start_time = time.time()
    
#     for epoch in range(epochs):
#         print(f"\n--- Epoch {epoch + 1}/{epochs} ---")
        
#         # --- TRAINING PHASE ---
#         model.train()
#         running_train_loss = 0.0
#         train_correct = 0
#         total_train = 0
        
#         for images, labels in train_loader:
#             images, labels = images.to(device), labels.to(device)
            
#             optimizer.zero_grad()
#             outputs = model(images)
#             loss = criterion(outputs, labels)
#             loss.backward()
#             optimizer.step()
            
#             running_train_loss += loss.item() * images.size(0)
#             _, preds = torch.max(outputs, 1)
#             train_correct += torch.sum(preds == labels.data).item()
#             total_train += labels.size(0)
            
#         epoch_train_loss = running_train_loss / total_train
#         epoch_train_acc = train_correct / total_train
        
#         # --- VALIDATION PHASE ---
#         model.eval()
#         running_val_loss = 0.0
#         val_correct = 0
#         total_val = 0
        
#         with torch.no_grad():
#             for images, labels in val_loader:
#                 images, labels = images.to(device), labels.to(device)
#                 outputs = model(images)
#                 loss = criterion(outputs, labels)
                
#                 running_val_loss += loss.item() * images.size(0)
#                 _, preds = torch.max(outputs, 1)
#                 val_correct += torch.sum(preds == labels.data).item()
#                 total_val += labels.size(0)
                
#         epoch_val_loss = running_val_loss / total_val
#         epoch_val_acc = val_correct / total_val
        
#         print(f"Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc * 100:.2f}%")
#         print(f"Val   Loss: {epoch_val_loss:.4f} | Val   Acc: {epoch_val_acc * 100:.2f}%")
        
#         # Save checkpoint if accuracy improves
#         if epoch_val_acc > best_val_acc:
#             best_val_acc = epoch_val_acc
#             torch.save({
#                 'epoch': epoch + 1,
#                 'model_state_dict': model.state_dict(),
#                 'optimizer_state_dict': optimizer.state_dict(),
#                 'val_accuracy': best_val_acc,
#                 'class_names': class_names
#             }, save_path)
#             print(f"⭐ Saved new best model ({epoch_val_acc * 100:.2f}%) to {save_path}")
            
#     total_duration = time.time() - start_time
#     print(f"\n🎉 Training complete in {total_duration / 60:.2f} minutes.")
#     print(f"🏆 Best Validation Accuracy: {best_val_acc * 100:.2f}%")

# if __name__ == "__main__":
#     train_model(epochs=25, batch_size=32, lr=1e-4)

import os
import time
import torch
import torch.nn as nn
from torch.optim import AdamW
from dataset import get_dataloaders
from model import DeepfakeDetector, get_device
from torch.optim.lr_scheduler import ReduceLROnPlateau

def train_model(epochs=35, batch_size=128, lr=5e-5):
    device = get_device()
    print(f"🚀 Training on compute device: {device}")
    
    # 1. Load Data (Using the heavy augmentations defined in dataset.py)
    train_loader, val_loader, class_names = get_dataloaders(batch_size=batch_size)
    print(f"Classes: {class_names} | Train batches: {len(train_loader)} | Val batches: {len(val_loader)}")
    
    # 2. Initialize Model
    model = DeepfakeDetector(num_classes=len(class_names), pretrained=True).to(device)
    
    # UNFREEZE the entire network for maximum capability
    for param in model.parameters():
        param.requires_grad = True
        
    # 3. Advanced Loss and Optimizer for Deepfakes
    # Label smoothing prevents the model from being 100% confident, forcing it to find better generalized features
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    
    # AdamW applies decoupled weight decay, drastically reducing overfitting compared to standard Adam
    optimizer = AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    
    # Scheduler with slightly higher patience to allow the model to grind through plateaus
    scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)
    
    best_val_acc = 0.0
    save_path = "models/deepfake_detector.pt"
    os.makedirs("models", exist_ok=True)
    
    start_time = time.time()
    
    for epoch in range(epochs):
        print(f"\n--- Epoch {epoch + 1}/{epochs} ---")
        
        # --- TRAINING PHASE ---
        model.train()
        running_train_loss = 0.0
        train_correct = 0
        total_train = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_train_loss += loss.item() * images.size(0)
            _, preds = torch.max(outputs, 1)
            train_correct += torch.sum(preds == labels.data).item()
            total_train += labels.size(0)
            
        epoch_train_loss = running_train_loss / total_train
        epoch_train_acc = train_correct / total_train
        
        # --- VALIDATION PHASE ---
        model.eval()
        running_val_loss = 0.0
        val_correct = 0
        total_val = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                running_val_loss += loss.item() * images.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += torch.sum(preds == labels.data).item()
                total_val += labels.size(0)
                
        epoch_val_loss = running_val_loss / total_val
        epoch_val_acc = val_correct / total_val
        
        # Step the scheduler based on validation loss
        scheduler.step(epoch_val_loss)
        
        # Fetch current learning rate to monitor the scheduler's adjustments
        current_lr = optimizer.param_groups[0]['lr']
        
        print(f"Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc * 100:.2f}% | LR: {current_lr:.1e}")
        print(f"Val   Loss: {epoch_val_loss:.4f} | Val   Acc: {epoch_val_acc * 100:.2f}%")
        
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_accuracy': best_val_acc,
                'class_names': class_names
            }, save_path)
            print(f"⭐ Saved new best model ({epoch_val_acc * 100:.2f}%) to {save_path}")
            
    total_duration = time.time() - start_time
    print(f"\n🎉 Training complete in {total_duration / 60:.2f} minutes.")
    print(f"🏆 Best Validation Accuracy: {best_val_acc * 100:.2f}%")

if __name__ == "__main__":
    train_model(epochs=35, batch_size=128, lr=5e-5)