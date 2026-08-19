# Phase 4 — Training Configuration

## Reproducibility Reference

| Parameter | Value |
|---|---|
| Random Seed | `42` |
| Python Version | `3.11` |
| Framework | `PyTorch 2.13.0` |
| Model Architecture | `MobileNetV3-Small (Transfer Learning)` |
| Pretrained Weights | `MobileNet_V3_Small_Weights.DEFAULT (ImageNet-1K)` |
| Image Size | `224 x 224` |
| Batch Size | `16` |
| Learning Rate | `0.001 (AdamW)` |
| Optimizer | `AdamW (weight_decay=1e-4)` |
| LR Scheduler | `StepLR (step_size=7, gamma=0.5)` |
| Max Epochs | `25` |
| Early Stopping Patience | `7` |
| Num Workers (DataLoader) | `0` |

## Class Names (Fixed Order)

```json
["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]
```

> **Note:** ImageFolder sorts classes alphabetically: broken_streetlight(0), flooding(1), garbage(2), open_manhole(3), pothole(4), water_leakage(5)

## Augmentation Configuration (Training Only)

| Augmentation | Parameters |
|---|---|
| Resize | `224 x 224` |
| RandomHorizontalFlip | `p=0.5` |
| RandomRotation | `degrees=15` |
| ColorJitter | `brightness=0.2, contrast=0.2` |
| Normalize | `mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]` |

## Dataset Counts

| Split | Count |
|---|---|
| Train | 302 |
| Validation | 65 |
| Test | 67 |
| **Total** | **434** |

## Model Selection Rationale

**MobileNetV3-Small** was selected because:
1. **Mobile/Edge Deployment**: Lightweight 2.5M params, suitable for the Civic AI Flutter app.
2. **Transfer Learning**: Pre-trained on ImageNet-1K provides strong feature extraction for real-world images.
3. **Accuracy vs Speed**: Achieves high accuracy on moderate-sized datasets with fast CPU inference.
4. **ONNX Compatible**: Supports full ONNX export for TFLite/mobile conversion.
