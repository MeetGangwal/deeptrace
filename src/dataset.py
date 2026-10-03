# import torch
# from torchvision import datasets, transforms
# from torch.utils.data import DataLoader

# def get_dataloaders(data_dir="data/processed", batch_size=32):
#     """
#     Creates PyTorch DataLoaders for train and validation sets.
#     """
    
#     # ImageNet standards used for Transfer Learning models
#     normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
#                                      std=[0.229, 0.224, 0.225])
    
#     # Training transforms include augmentation to prevent overfitting
#     train_transforms = transforms.Compose([
#         transforms.Resize((224, 224)),
#         transforms.RandomHorizontalFlip(), # Randomly flip faces horizontally
#         transforms.ColorJitter(brightness=0.1, contrast=0.1),
#         transforms.ToTensor(),
#         normalize
#     ])
    
#     # Validation transforms only resize and normalize (no augmentation)
#     val_transforms = transforms.Compose([
#         transforms.Resize((224, 224)),
#         transforms.ToTensor(),
#         normalize
#     ])
    
#     # Load images directly from the processed folder structure
#     train_dataset = datasets.ImageFolder(root=f"{data_dir}/train", transform=train_transforms)
#     val_dataset = datasets.ImageFolder(root=f"{data_dir}/val", transform=val_transforms)
    
#     # Build iterators to serve images in batches to the GPU
#     train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
#     val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=2)
    
#     return train_loader, val_loader, train_dataset.classes

# if __name__ == "__main__":
#     train_loader, val_loader, classes = get_dataloaders()
#     print(f"✅ Classes found: {classes}")
    
#     # Grab one batch to verify the tensor shapes
#     images, labels = next(iter(train_loader))
#     print(f"Batch Image Shape: {images.shape} (Batch Size, Channels, Height, Width)")
#     print(f"Batch Labels Shape: {labels.shape}")

import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

def get_dataloaders(data_dir="data/processed", batch_size=32):
    """
    Creates PyTorch DataLoaders for train and validation sets.
    """
    
    # ImageNet standards used for Transfer Learning models
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

    # Training transforms include augmentation to prevent overfitting
    train_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15), 
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        normalize
    ])

    # Validation transforms only resize and normalize (no augmentation)
    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        normalize
    ])
    
    # Load images from the processed directories
    train_dataset = datasets.ImageFolder(root=f"{data_dir}/train", transform=train_transforms)
    val_dataset = datasets.ImageFolder(root=f"{data_dir}/val", transform=val_transforms)
    
    # Accelerated hardware pipelines for Apple Silicon
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, 
                              num_workers=4, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, 
                            num_workers=4, pin_memory=True)
    
    return train_loader, val_loader, train_dataset.classes