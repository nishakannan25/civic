# Civic AI - AI & Computer Vision Subsystem

> **Note**: In **Phase 1**, this directory structure serves as a clean architectural foundation. AI model training, dataset ingestion, YOLO inference, and evaluation pipelines will be introduced in **Phase 4** (Taxonomy & Data Pipeline) and **Phase 5** (Model Training & Inference).

## Directory Structure

- `datasets/`: Dataset storage for civic issue imagery.
  - `raw/`: Unprocessed citizen and municipal images.
  - `processed/`: Normalized, augmented, and split datasets.
  - `civic_dataset/`: Labeled civic dataset with bounding boxes.
- `scripts/`: Data ingestion, conversion, and preprocessing utilities.
- `training/`: Model training pipelines (YOLOv8 / custom architectures).
- `inference/`: Real-time and batch visual inference pipelines.
- `models/`: Exported model weights (`.pt`, `.onnx`, TFLite for edge).
- `evaluation/`: Validation metrics, confusion matrices, and benchmark reports.

## Taxonomy Classes (Master Taxonomy)
- `0`: Pothole
- `1`: Open Manhole
- `2`: Garbage / Waste Accumulation
- `3`: Flooding (Future Phase)
- `4`: Broken Streetlight (Future Phase)
- `5`: Water Leakage (Future Phase)
