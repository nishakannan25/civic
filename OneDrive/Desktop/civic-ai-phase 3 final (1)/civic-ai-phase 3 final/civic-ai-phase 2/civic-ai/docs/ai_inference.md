# Civic AI — Phase 5: AI Inference API Documentation

## Overview
The Phase 5 AI Inference API exposes a dedicated backend endpoint for classifying civic crisis issues from user-submitted images using the trained Phase 4 PyTorch MobileNetV3 model.

---

## Technical Architecture

### Model Loader (`app/ai/model_loader.py`)
- **Pattern**: Singleton (`ModelLoader`).
- **Behavior**: Loads `models/best_model/model.pth` and `models/class_names.json` into memory ONCE during application startup (FastAPI lifespan). Avoids per-request disk read or weight initialization latency.
- **Model Architecture**: `MobileNetV3-Small` (6 output units).
- **Model Version**: `phase4-v1`.

### Inference Service (`app/ai/service.py`)
- **Class**: `CrisisInferenceService`.
- **Image Preprocessing**:
  1. Image validation & automatic conversion to 3-channel `RGB`.
  2. Resize to `(224, 224)`.
  3. PyTorch Tensor conversion (`ToTensor`).
  4. ImageNet normalization: Mean `[0.485, 0.456, 0.406]`, Std `[0.229, 0.224, 0.225]`.
- **Inference Execution**: PyTorch evaluation pass (`torch.no_grad()`) on CPU/CUDA, returning Softmax probabilities and execution timing in milliseconds (`inference_time_ms`).

---

## 6 Supported Crisis Classes Mapping

| Index | Raw Class Key | Display Name Returned |
|---|---|---|
| 0 | `broken_streetlight` | `Broken Streetlight` |
| 1 | `flooding` | `Flooding / Waterlogging` |
| 2 | `garbage` | `Garbage Accumulation` |
| 3 | `open_manhole` | `Open Manhole` |
| 4 | `pothole` | `Pothole / Road Damage` |
| 5 | `water_leakage` | `Water Leakage` |

---

## API Endpoints

### 1. Predict Crisis Class from Image
- **Endpoint**: `POST /ai/infer` (also available at `/api/v1/ai/infer`)
- **Content-Type**: `multipart/form-data`
- **Body Parameter**: `image` (UploadFile) — Supported Formats: JPEG, PNG, WEBP. Max size: 10MB.

#### Example Response (200 OK):
```json
{
  "predicted_class": "Pothole / Road Damage",
  "confidence": 0.9998,
  "model_version": "phase4-v1",
  "inference_time_ms": 38.45,
  "probabilities": {
    "Broken Streetlight": 0.0000,
    "Flooding / Waterlogging": 0.0001,
    "Garbage Accumulation": 0.0000,
    "Open Manhole": 0.0001,
    "Pothole / Road Damage": 0.9998,
    "Water Leakage": 0.0000
  }
}
```

#### Error Handling:
- `400 Bad Request`: Invalid image format, corrupt file, or empty file upload.
- `413 Request Entity Too Large`: Image file exceeds maximum allowed size (10MB).
- `503 Service Unavailable`: Model weights missing or singleton failed to initialize.

---

### 2. AI Service Health Status
- **Endpoint**: `GET /ai/health` (also available at `/api/v1/ai/health`)

#### Example Response (200 OK):
```json
{
  "status": "ready",
  "model_version": "phase4-v1",
  "model_loaded": true
}
```

---

## Verification Test Results

Execute all test suites from `backend/`:
```bash
python run_phase5_tests.py   # 16/16 Passed (100%)
python run_phase1_tests.py   # 8/8 Passed (100%)
python run_phase3_tests.py   # 11/11 Passed (100%)
```
