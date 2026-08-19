import io
import time
import logging
from typing import Dict, Any
from PIL import Image
import torch
from torchvision import transforms

from .model_loader import ModelLoader, CLASS_DISPLAY_NAMES

logger = logging.getLogger(__name__)

# Exact ImageNet normalization constants used in Phase 4 training
NORM_MEAN = [0.485, 0.456, 0.406]
NORM_STD = [0.229, 0.224, 0.225]
IMAGE_SIZE = (224, 224)


def get_inference_transforms():
    """Preprocessing pipeline matching Phase 4 training pipeline."""
    return transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=NORM_MEAN, std=NORM_STD),
    ])


class CrisisInferenceService:
    """
    Service executing AI inference on uploaded image bytes.
    Uses singleton ModelLoader to ensure weights are not reloaded per request.
    """

    def __init__(self):
        self.transform = get_inference_transforms()

    def predict_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Preprocess image bytes, run MobileNetV3 inference, return predictions.

        Returns:
            dict containing:
              - 'predicted_class': str (display name, e.g. "Pothole / Road Damage")
              - 'confidence': float (max probability)
              - 'model_version': str ("phase4-v1")
              - 'inference_time_ms': float
              - 'probabilities': dict (display name -> probability)
        """
        start_time = time.perf_counter()

        model, class_names, device = ModelLoader.get_model()

        if model is None or not ModelLoader.is_loaded():
            err_msg = ModelLoader.get_error() or "AI inference model is not loaded"
            raise RuntimeError(f"ModelUnavailable: {err_msg}")

        # 1. Open image with PIL
        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            # Convert RGBA/Palette/Grayscale to RGB
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid or corrupted image format: {e}")

        # 2. Preprocess to tensor
        input_tensor = self.transform(pil_img).unsqueeze(0).to(device)

        # 3. Model forward pass
        with torch.no_grad():
            logits = model(input_tensor)
            probs = torch.softmax(logits, dim=1).squeeze(0)

        prob_list = probs.cpu().numpy().tolist()

        # ImageFolder class ordering is alphabetical:
        # 0: broken_streetlight, 1: flooding, 2: garbage, 3: open_manhole, 4: pothole, 5: water_leakage
        sorted_raw_classes = sorted(class_names)

        # Build probability dictionary mapped to display names
        display_probabilities: Dict[str, float] = {}
        for idx, raw_cls in enumerate(sorted_raw_classes):
            disp_name = CLASS_DISPLAY_NAMES.get(raw_cls, raw_cls)
            display_probabilities[disp_name] = round(prob_list[idx], 4)

        # Extract top prediction
        max_prob = max(display_probabilities.values())
        predicted_display_class = max(display_probabilities, key=display_probabilities.get)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return {
            "predicted_class": predicted_display_class,
            "confidence": round(float(max_prob), 4),
            "model_version": ModelLoader.get_version(),
            "inference_time_ms": elapsed_ms,
            "probabilities": display_probabilities,
        }
