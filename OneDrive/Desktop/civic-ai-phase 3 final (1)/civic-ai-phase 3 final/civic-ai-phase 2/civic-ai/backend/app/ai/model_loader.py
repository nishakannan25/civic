import os
import json
import logging
from typing import Optional, List, Tuple

try:
    import torch
    import torch.nn as nn
    from torchvision import models
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    models = None
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
DEFAULT_MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "best_model", "model.pth")
DEFAULT_CLASS_NAMES_PATH = os.path.join(PROJECT_ROOT, "models", "class_names.json")
MODEL_VERSION = "phase4-v1"

# Exact display names corresponding to the 6 raw classes
CLASS_DISPLAY_NAMES = {
    "broken_streetlight": "Broken Streetlight",
    "flooding": "Flooding / Waterlogging",
    "garbage": "Garbage Accumulation",
    "open_manhole": "Open Manhole",
    "pothole": "Pothole / Road Damage",
    "water_leakage": "Water Leakage",
}


def build_mobilenet_v3(num_classes: int = 6):
    """Construct MobileNetV3-Small architecture for 6-class classification."""
    if not TORCH_AVAILABLE:
        return None
    model = models.mobilenet_v3_small(weights=None)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    return model


class ModelLoader:
    """
    Singleton model loader.
    Ensures the PyTorch MobileNetV3 model is loaded into memory ONCE
    at application startup or on first request, avoiding per-request reloading.
    """

    _instance: Optional["ModelLoader"] = None
    _model: Optional[nn.Module] = None
    _class_names: List[str] = []
    _device: torch.device = torch.device("cpu")
    _is_loaded: bool = False
    _error: Optional[str] = None
    _load_count: int = 0  # Track number of times load() is invoked for verification tests

    def __new__(cls) -> "ModelLoader":
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance

    @classmethod
    def load(cls, model_path: Optional[str] = None, class_names_path: Optional[str] = None) -> bool:
        """Load trained PyTorch weights and class names JSON."""
        instance = cls()
        instance._load_count += 1

        if instance._is_loaded:
            logger.info("Model is already loaded in memory singleton.")
            return True

        if model_path is None:
            model_path = DEFAULT_MODEL_PATH
        if class_names_path is None:
            class_names_path = DEFAULT_CLASS_NAMES_PATH

        instance._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        try:
            if not os.path.exists(model_path):
                err = f"Model weights artifact not found at: {model_path}"
                logger.error(err)
                instance._error = err
                return False

            if not os.path.exists(class_names_path):
                err = f"Class names JSON artifact not found at: {class_names_path}"
                logger.error(err)
                instance._error = err
                return False

            with open(class_names_path, "r") as f:
                instance._class_names = json.load(f)

            model = build_mobilenet_v3(num_classes=len(instance._class_names))
            model.load_state_dict(torch.load(model_path, map_location=instance._device))
            model.to(instance._device)
            model.eval()

            instance._model = model
            instance._is_loaded = True
            instance._error = None
            logger.info(f"Successfully loaded model from {model_path} on {instance._device}")
            return True

        except Exception as e:
            instance._error = str(e)
            instance._is_loaded = False
            instance._model = None
            logger.error(f"Failed to load AI model: {e}")
            return False

    @classmethod
    def get_model(cls) -> Tuple[Optional[nn.Module], List[str], torch.device]:
        """Retrieve singleton model instance, class names list, and torch device."""
        instance = cls()
        if not instance._is_loaded:
            cls.load()
        return instance._model, instance._class_names, instance._device

    @classmethod
    def is_loaded(cls) -> bool:
        return cls()._is_loaded

    @classmethod
    def get_error(cls) -> Optional[str]:
        return cls()._error

    @classmethod
    def get_version(cls) -> str:
        return MODEL_VERSION

    @classmethod
    def reset_for_tests(cls):
        """Reset singleton state (used only in unit tests for missing model simulation)."""
        instance = cls()
        instance._is_loaded = False
        instance._model = None
        instance._error = None
        instance._load_count = 0
