import os
import sys
import json
import torch
import torch.nn as nn
from torchvision import models

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ml.preprocessing.pipeline import preprocess_image

CLASSES = ["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]
MODELS_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\models"
LOW_CONFIDENCE_THRESHOLD = 0.5


def build_model(num_classes=6):
    model = models.mobilenet_v3_small(weights=None)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, num_classes)
    return model


class CrisisClassifier:
    """
    Six-class crisis image classifier.
    Returns probabilities for: pothole, open_manhole, garbage,
    flooding, broken_streetlight, water_leakage.
    If top confidence < threshold, returns LOW_CONFIDENCE.
    """

    def __init__(self, model_path=None, threshold=LOW_CONFIDENCE_THRESHOLD):
        self.threshold = threshold
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Load class names
        class_names_path = os.path.join(MODELS_DIR, "class_names.json")
        with open(class_names_path, "r") as f:
            self.class_names = json.load(f)

        # Build model
        self.model = build_model(num_classes=len(self.class_names)).to(self.device)

        if model_path is None:
            model_path = os.path.join(MODELS_DIR, "best_model", "model.pth")

        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def predict(self, image_path):
        """
        Predict crisis class from an image file.

        Returns:
            dict with:
              - 'predicted_class': str (class name or 'LOW_CONFIDENCE')
              - 'confidence': float (max probability)
              - 'probabilities': dict (class -> probability for all 6 classes)
        """
        tensor = preprocess_image(image_path).to(self.device)

        with torch.no_grad():
            outputs = self.model(tensor)
            probs = torch.softmax(outputs, dim=1).squeeze()

        prob_values = probs.cpu().numpy().tolist()

        # Map output indices to the alphabetically sorted class order used during training
        # ImageFolder sorts: broken_streetlight(0), flooding(1), garbage(2), open_manhole(3), pothole(4), water_leakage(5)
        sorted_class_names = sorted(self.class_names)

        # Keep raw probabilities for internal comparison and rounded for display
        raw_probs = {cls: prob_values[i] for i, cls in enumerate(sorted_class_names)}
        probabilities = {cls: round(v, 6) for cls, v in raw_probs.items()}

        # Use raw (unrounded) values for threshold comparison & argmax
        max_raw_prob = max(raw_probs.values())
        predicted_class = max(raw_probs, key=raw_probs.get)

        if max_raw_prob < self.threshold:
            predicted_class = "LOW_CONFIDENCE"

        return {
            "predicted_class": predicted_class,
            "confidence": round(max_raw_prob, 4),
            "probabilities": probabilities
        }


if __name__ == "__main__":
    # Quick smoke test
    classifier = CrisisClassifier()
    print("CrisisClassifier loaded successfully!")
    print(f"Supported classes: {classifier.class_names}")
    print(f"Low-confidence threshold: {classifier.threshold}")
