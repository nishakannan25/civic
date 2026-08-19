import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import json
import random
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models
import matplotlib.pyplot as plt
import numpy as np

# Import preprocessing pipeline
from ml.preprocessing.pipeline import get_transforms

RANDOM_SEED = 42
BATCH_SIZE = 16
NUM_EPOCHS = 25
LEARNING_RATE = 1e-3
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLASSES = ["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]

DATASET_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\dataset"
MODELS_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\models"
ARTIFACTS_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\artifacts"

def set_seed(seed=RANDOM_SEED):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def build_model(num_classes=6):
    """
    Builds a lightweight MobileNetV3 Small transfer-learning model.
    """
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
    # Replace final classification head
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    return model

def train_model():
    set_seed(RANDOM_SEED)
    print(f"Using Device: {DEVICE}")

    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "validation")

    train_dataset = datasets.ImageFolder(train_dir, transform=get_transforms(is_training=True))
    val_dataset = datasets.ImageFolder(val_dir, transform=get_transforms(is_training=False))

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    print(f"Training Samples: {len(train_dataset)}, Validation Samples: {len(val_dataset)}")
    print(f"Class Mapping: {train_dataset.class_to_idx}")

    # Ensure class mapping matches exact order
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    with open(os.path.join(MODELS_DIR, "class_names.json"), "w") as f:
        json.dump(CLASSES, f, indent=2)

    model = build_model(num_classes=len(CLASSES)).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.5)

    best_val_acc = 0.0
    best_model_path = os.path.join(MODELS_DIR, "best_model")
    final_model_path = os.path.join(MODELS_DIR, "final_model")

    os.makedirs(best_model_path, exist_ok=True)
    os.makedirs(final_model_path, exist_ok=True)

    history = {
        "train_loss": [], "val_loss": [],
        "train_acc": [], "val_acc": []
    }

    patience = 7
    patience_counter = 0

    print("Starting Model Training...")
    for epoch in range(1, NUM_EPOCHS + 1):
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0

        for inputs, labels in train_loader:
            inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct_train += torch.sum(preds == labels.data).item()
            total_train += inputs.size(0)

        scheduler.step()

        epoch_train_loss = running_loss / total_train
        epoch_train_acc = correct_train / total_train

        # Validation phase
        model.eval()
        val_running_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(DEVICE), labels.to(DEVICE)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_running_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                correct_val += torch.sum(preds == labels.data).item()
                total_val += inputs.size(0)

        epoch_val_loss = val_running_loss / total_val
        epoch_val_acc = correct_val / total_val

        history["train_loss"].append(epoch_train_loss)
        history["val_loss"].append(epoch_val_loss)
        history["train_acc"].append(epoch_train_acc)
        history["val_acc"].append(epoch_val_acc)

        print(f"Epoch {epoch:02d}/{NUM_EPOCHS} | "
              f"Train Loss: {epoch_train_loss:.4f} Acc: {epoch_train_acc:.4f} | "
              f"Val Loss: {epoch_val_loss:.4f} Acc: {epoch_val_acc:.4f}")

        # Checkpointing
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            patience_counter = 0
            # Save PyTorch best model
            torch.save(model.state_dict(), os.path.join(best_model_path, "model.pth"))
            # Export ONNX best model
            dummy_input = torch.randn(1, 3, 224, 224).to(DEVICE)
            torch.onnx.export(
                model, dummy_input, os.path.join(best_model_path, "model.onnx"),
                input_names=["input"], output_names=["output"],
                dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}}
            )
            print(f"  -> Best model saved! (Val Acc: {best_val_acc:.4f})")
        else:
            patience_counter += 1

        if patience_counter >= patience:
            print(f"Early stopping triggered at epoch {epoch}")
            break

    # Save final model
    torch.save(model.state_dict(), os.path.join(final_model_path, "model.pth"))

    # Plot & Save Training Curves
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(history["train_loss"], label="Train Loss", color="blue", linewidth=2)
    plt.plot(history["val_loss"], label="Val Loss", color="orange", linewidth=2)
    plt.title("Loss Curves")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(history["train_acc"], label="Train Acc", color="green", linewidth=2)
    plt.plot(history["val_acc"], label="Val Acc", color="red", linewidth=2)
    plt.title("Accuracy Curves")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.grid(True)

    curves_path = os.path.join(ARTIFACTS_DIR, "training_curves.png")
    plt.tight_layout()
    plt.savefig(curves_path, dpi=150)
    plt.close()

    # Save training history JSON
    with open(os.path.join(ARTIFACTS_DIR, "history.json"), "w") as hf:
        json.dump(history, hf, indent=2)

    print(f"Training completed successfully! Training curves saved to {curves_path}")

if __name__ == "__main__":
    train_model()
