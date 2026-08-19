import os
import sys
import json
import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from torch.utils.data import DataLoader
from torchvision import datasets, models
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ml.preprocessing.pipeline import get_transforms

CLASSES = ["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]
DATASET_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\dataset"
MODELS_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\models"
ARTIFACTS_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\artifacts"
DOCS_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\docs"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
BATCH_SIZE = 16


def build_model(num_classes=6):
    model = models.mobilenet_v3_small(weights=None)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    return model


def evaluate_model():
    test_dir = os.path.join(DATASET_DIR, "test")
    test_dataset = datasets.ImageFolder(test_dir, transform=get_transforms(is_training=False))
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    print(f"Test Samples: {len(test_dataset)}")
    print(f"Class Mapping (ImageFolder): {test_dataset.class_to_idx}")

    # Load best model
    model = build_model(num_classes=len(CLASSES)).to(DEVICE)
    best_model_path = os.path.join(MODELS_DIR, "best_model", "model.pth")
    model.load_state_dict(torch.load(best_model_path, map_location=DEVICE))
    model.eval()
    print("Best model loaded successfully!")

    all_preds = []
    all_labels = []

    # The ImageFolder sorts classes alphabetically, so create ordinal mapping
    # Unique to ImageFolder: classes are: broken_streetlight(0), flooding(1), garbage(2), open_manhole(3), pothole(4), water_leakage(5)
    # Map these alphabetically-indexed to our intended CLASSES list
    folder_class_to_idx = test_dataset.class_to_idx
    idx_to_cls = {v: k for k, v in folder_class_to_idx.items()}

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(DEVICE)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    # Get sorted class names (matching ImageFolder order)
    sorted_classes = [k for k, v in sorted(folder_class_to_idx.items(), key=lambda x: x[1])]

    # Calculate metrics
    acc = accuracy_score(all_labels, all_preds)
    precision_macro = precision_score(all_labels, all_preds, average="macro", zero_division=0)
    recall_macro = recall_score(all_labels, all_preds, average="macro", zero_division=0)
    f1_macro = f1_score(all_labels, all_preds, average="macro", zero_division=0)

    per_class_precision = precision_score(all_labels, all_preds, average=None, zero_division=0)
    per_class_recall = recall_score(all_labels, all_preds, average=None, zero_division=0)
    per_class_f1 = f1_score(all_labels, all_preds, average=None, zero_division=0)

    cm = confusion_matrix(all_labels, all_preds)

    print(f"\n=== TEST SET EVALUATION RESULTS ===")
    print(f"Test Accuracy:       {acc:.4f} ({acc*100:.2f}%)")
    print(f"Macro Precision:     {precision_macro:.4f}")
    print(f"Macro Recall:        {recall_macro:.4f}")
    print(f"Macro F1-Score:      {f1_macro:.4f}")
    print(f"\nPer-Class Results:")
    for i, cls in enumerate(sorted_classes):
        print(f"  {cls:<25}: P={per_class_precision[i]:.4f}  R={per_class_recall[i]:.4f}  F1={per_class_f1[i]:.4f}")

    # Save confusion matrix
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=sorted_classes, yticklabels=sorted_classes,
                linewidths=0.5, linecolor='gray')
    plt.title("Confusion Matrix — 6-Class Crisis Classification", fontsize=14)
    plt.ylabel("Actual Class", fontsize=12)
    plt.xlabel("Predicted Class", fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    cm_path = os.path.join(ARTIFACTS_DIR, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=150)
    plt.close()
    print(f"\nConfusion matrix saved to: {cm_path}")

    # Save evaluation metrics JSON
    metrics = {
        "test_accuracy": round(acc, 6),
        "macro_precision": round(precision_macro, 6),
        "macro_recall": round(recall_macro, 6),
        "macro_f1": round(f1_macro, 6),
        "per_class": {
            cls: {
                "precision": round(per_class_precision[i], 6),
                "recall": round(per_class_recall[i], 6),
                "f1": round(per_class_f1[i], 6)
            }
            for i, cls in enumerate(sorted_classes)
        },
        "confusion_matrix": cm.tolist()
    }
    with open(os.path.join(ARTIFACTS_DIR, "eval_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # Generate docs/phase4_model_evaluation.md
    os.makedirs(DOCS_DIR, exist_ok=True)
    md = "# Phase 4 — Model Evaluation Report\n\n"
    md += "## Model: MobileNetV3-Small (Transfer Learning, PyTorch)\n\n"
    md += "## Overall Test Set Metrics\n\n"
    md += f"| Metric | Score |\n|---|---|\n"
    md += f"| **Test Accuracy** | **{acc:.4f} ({acc*100:.2f}%)** |\n"
    md += f"| Macro Precision | {precision_macro:.4f} |\n"
    md += f"| Macro Recall | {recall_macro:.4f} |\n"
    md += f"| Macro F1-Score | {f1_macro:.4f} |\n\n"
    md += "## Per-Class Results\n\n"
    md += "| Class | Precision | Recall | F1-Score |\n|---|---|---|---|\n"
    for i, cls in enumerate(sorted_classes):
        md += f"| `{cls}` | {per_class_precision[i]:.4f} | {per_class_recall[i]:.4f} | {per_class_f1[i]:.4f} |\n"
    md += "\n## Confusion Matrix\n\n"
    md += "Saved at: `artifacts/confusion_matrix.png`\n\n"
    md += "## Test Data Isolation\n\n"
    md += "- Test data was **not** used during training or model selection.\n"
    md += "- Only `dataset/train/` was used for training.\n"
    md += "- `dataset/validation/` was used for early stopping and best model selection.\n"
    md += "- `dataset/test/` was used for this final evaluation **only**.\n"

    with open(os.path.join(DOCS_DIR, "phase4_model_evaluation.md"), "w") as f:
        f.write(md)

    return metrics


if __name__ == "__main__":
    evaluate_model()
