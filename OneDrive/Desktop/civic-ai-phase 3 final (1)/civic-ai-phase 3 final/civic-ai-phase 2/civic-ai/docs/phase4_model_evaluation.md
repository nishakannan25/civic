# Phase 4 — Model Evaluation Report

## Model: MobileNetV3-Small (Transfer Learning, PyTorch)

## Overall Test Set Metrics

| Metric | Score |
|---|---|
| **Test Accuracy** | **1.0000 (100.00%)** |
| Macro Precision | 1.0000 |
| Macro Recall | 1.0000 |
| Macro F1-Score | 1.0000 |

## Per-Class Results

| Class | Precision | Recall | F1-Score |
|---|---|---|---|
| `broken_streetlight` | 1.0000 | 1.0000 | 1.0000 |
| `flooding` | 1.0000 | 1.0000 | 1.0000 |
| `garbage` | 1.0000 | 1.0000 | 1.0000 |
| `open_manhole` | 1.0000 | 1.0000 | 1.0000 |
| `pothole` | 1.0000 | 1.0000 | 1.0000 |
| `water_leakage` | 1.0000 | 1.0000 | 1.0000 |

## Confusion Matrix

Saved at: `artifacts/confusion_matrix.png`

## Test Data Isolation

- Test data was **not** used during training or model selection.
- Only `dataset/train/` was used for training.
- `dataset/validation/` was used for early stopping and best model selection.
- `dataset/test/` was used for this final evaluation **only**.
