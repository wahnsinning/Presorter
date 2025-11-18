import torch
import clip
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
from torch.nn import CrossEntropyLoss
from PIL import Image
import json
from pathlib import Path
import torchvision.transforms as transforms

# Anomaly Detection deaktivieren
torch.autograd.set_detect_anomaly(False)

class CustomCLIPDataset(Dataset):
    def __init__(self, json_path: str, preprocess, augment: bool = True):
        with open(json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.preprocess = preprocess
        self.augment = augment
        if augment:
            # Augmentation-Pipeline 
            self.aug_transform = transforms.Compose([
                transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
                transforms.RandomRotation(10),
            ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        image = Image.open(item['image']).convert('RGB')
        
        if self.augment:
            # Augmentiere und dann preprocess
            image = self.aug_transform(image)
        
        image = self.preprocess(image)  # Preprocess
        # Tokenize single text to 1D (77,), DataLoader stacks to 2D (batch, 77)
        text = clip.tokenize(item['text'])[0]
        return image, text

def fine_tune_clip(json_path: str = 'clip_dataset.json', epochs: int = 3, batch_size: int = 16, lr: float = 1e-5, device: str = None, temperature: float = 0.07):
    
    #Finetunt CLIP auf der Json
    

    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Fine-Tuning auf {device}...")

    # Modell laden
    model, preprocess = clip.load("ViT-B/32", device=device)

    # Image-Encoder einfrieren
    for p in model.visual.parameters():
        p.requires_grad = False

    # Dataset und Loader
    dataset = CustomCLIPDataset(json_path, preprocess, augment=True)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)  # num_workers=0 für CPU

    # Loss und Optimizer
    loss_fn = CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=lr)

    # Training-Loop
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for images, texts in dataloader:
            images, texts = images.to(device), texts.to(device)

            # Features extrahieren
            image_features = model.encode_image(images)
            text_features = model.encode_text(texts)

            # Fix: Out-of-Place Normalisierung (kein Inplace /=)
            image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            # Logits berechnen (Similarity)
            logits_per_image = (image_features @ text_features.T) * temperature
            logits_per_text = logits_per_image.T  # Symmetrisch

            # Labels: Batch-Indizes
            labels = torch.arange(len(images), device=device)

            # Symmetric Loss
            loss_i = loss_fn(logits_per_image, labels)
            loss_t = loss_fn(logits_per_text, labels)
            loss = (loss_i + loss_t) / 2

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        avg_loss = total_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs} - Average Loss: {avg_loss:.4f}")

    # Speichern
    script_dir = Path(__file__).parent
    save_path = script_dir / 'fine_tuned_clip.pt'
    torch.save(model.state_dict(), save_path)
    print(f"Fine-tuned Modell gespeichert: {save_path}")

if __name__ == "__main__":
    fine_tune_clip()  # Automatisch mit clip_dataset.json
