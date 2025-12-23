import os
import json
import argparse
import numpy as np
import cv2
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import segmentation_models_pytorch as smp
from tqdm import tqdm

class TTPLADataset(Dataset):
    def __init__(self, root_dir, target_size=(512, 512)):
        self.root_dir = root_dir
        self.target_size = target_size
        self.image_files = [f for f in os.listdir(root_dir) if f.endswith('.jpg')]
        
    def __len__(self):
        return len(self.image_files)
    
    def __getitem__(self, idx):
        img_name = self.image_files[idx]
        img_path = os.path.join(self.root_dir, img_name)
        json_path = os.path.join(self.root_dir, img_name.replace('.jpg', '.json'))
        
        # Load Image
        image = cv2.imread(img_path)
        if image is None:
             raise FileNotFoundError(f"Image not found: {img_path}")
             
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Create Mask
        h, w, _ = image.shape
        mask = np.zeros((h, w), dtype=np.uint8)
        
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            for shape in data['shapes']:
                label = shape['label'].lower()
                points = np.array(shape['points'], dtype=np.int32)
                
                class_id = 0
                if 'cable' in label or 'wire' in label:
                    class_id = 1
                elif 'tower' in label:
                    class_id = 2
                elif 'tree' in label or 'vegetation' in label:
                    class_id = 3
                    
                if class_id > 0:
                    cv2.fillPoly(mask, [points], class_id)
        
        # Resize
        image = cv2.resize(image, self.target_size)
        mask = cv2.resize(mask, self.target_size, interpolation=cv2.INTER_NEAREST)
        
        # To Tensor (CHW)
        image = torch.from_numpy(image.transpose(2, 0, 1)).float() / 255.0
        mask = torch.from_numpy(mask).long()
        
        return image, mask

def train(data_dir, output_dir, epochs=5, batch_size=4, lr=1e-4):
    device = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    # Dataset & Loader
    dataset = TTPLADataset(data_dir)
    print(f"Found {len(dataset)} images in {data_dir}")
    
    train_loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Model
    model = smp.Unet(
        encoder_name="resnet18",
        encoder_weights="imagenet",
        in_channels=3,
        classes=4
    )
    model.to(device)
    
    # Loss & Optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # Loop
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        
        for images, masks in progress_bar:
            images = images.to(device)
            masks = masks.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            progress_bar.set_postfix(loss=loss.item())
            
        avg_loss = running_loss / len(train_loader)
        print(f"Epoch {epoch+1} Complete. Avg Loss: {avg_loss:.4f}")
        
    # Save
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, 'unet_ttpla_final.pth')
    torch.save(model.state_dict(), save_path)
    print(f"Model saved to {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train U-Net on TTPLA")
    parser.add_argument("--data", type=str, default="../data/TTPLA/data_original_size", help="Path to dataset")
    parser.add_argument("--output", type=str, default="../models", help="Output directory for weights")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    parser.add_argument("--batch", type=int, default=4, help="Batch size")
    
    args = parser.parse_args()
    
    # Resolve paths relative to script location if needed
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, args.data)
    output_path = os.path.join(script_dir, args.output)
    
    train(data_path, output_path, args.epochs, args.batch)
