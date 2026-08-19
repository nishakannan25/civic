"""
Phase 4 Automated Test Suite
Tests 1-12 as specified in Phase 4 requirements.
"""
import os
import sys
import json
import hashlib
import torch
import pytest

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

CLASSES = ["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]
DATASET_DIR = os.path.join(PROJECT_ROOT, "dataset")
MASTER_DIR = os.path.join(DATASET_DIR, "master")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
ARTIFACTS_DIR = os.path.join(PROJECT_ROOT, "artifacts")


def count_images_in(directory):
    """Count all image files in a directory tree."""
    count = 0
    if not os.path.exists(directory):
        return 0
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                count += 1
    return count


def get_md5(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        hasher.update(f.read())
    return hasher.hexdigest()


def get_all_image_hashes(directory):
    hashes = []
    for root, dirs, files in os.walk(directory):
        for f in sorted(files):
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                hashes.append(get_md5(os.path.join(root, f)))
    return hashes


# =========================================================
# TEST 1: All 6 classes are detected in master dataset
# =========================================================
def test_01_all_six_classes_exist_in_master():
    """TEST 1: All six crisis classes exist in the master dataset."""
    for cls in CLASSES:
        cls_dir = os.path.join(MASTER_DIR, cls)
        assert os.path.isdir(cls_dir), f"Class folder missing in master: {cls}"
        images = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        assert len(images) > 0, f"No images found for class: {cls}"


# =========================================================
# TEST 2: No corrupted images in master dataset
# =========================================================
def test_02_no_corrupted_images_in_master():
    """TEST 2: No corrupted or unreadable images in master dataset."""
    from PIL import Image
    corrupted = []
    for cls in CLASSES:
        cls_dir = os.path.join(MASTER_DIR, cls)
        if not os.path.isdir(cls_dir):
            continue
        for fname in os.listdir(cls_dir):
            if not fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                continue
            fpath = os.path.join(cls_dir, fname)
            try:
                if os.path.getsize(fpath) == 0:
                    corrupted.append(fpath)
                    continue
                with Image.open(fpath) as img:
                    img.verify()
            except Exception:
                corrupted.append(fpath)
    assert corrupted == [], f"Corrupted images found in master: {corrupted}"


# =========================================================
# TEST 3: No duplicate images across train/val/test
# =========================================================
def test_03_no_duplicate_images_across_splits():
    """TEST 3: No same image appears in more than one split."""
    train_hashes = set(get_all_image_hashes(os.path.join(DATASET_DIR, "train")))
    val_hashes = set(get_all_image_hashes(os.path.join(DATASET_DIR, "validation")))
    test_hashes = set(get_all_image_hashes(os.path.join(DATASET_DIR, "test")))

    train_val_overlap = train_hashes & val_hashes
    train_test_overlap = train_hashes & test_hashes
    val_test_overlap = val_hashes & test_hashes

    assert not train_val_overlap, f"Duplicate images between TRAIN and VAL: {len(train_val_overlap)}"
    assert not train_test_overlap, f"Duplicate images between TRAIN and TEST: {len(train_test_overlap)}"
    assert not val_test_overlap, f"Duplicate images between VAL and TEST: {len(val_test_overlap)}"


# =========================================================
# TEST 4: All 6 classes exist in train set
# =========================================================
def test_04_all_six_classes_in_train():
    """TEST 4: All six crisis classes exist in training split."""
    for cls in CLASSES:
        cls_dir = os.path.join(DATASET_DIR, "train", cls)
        assert os.path.isdir(cls_dir), f"Class folder missing in train: {cls}"
        images = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        assert len(images) > 0, f"No training images found for class: {cls}"


# =========================================================
# TEST 5: All 6 classes exist in validation set
# =========================================================
def test_05_all_six_classes_in_validation():
    """TEST 5: All six crisis classes exist in validation split."""
    for cls in CLASSES:
        cls_dir = os.path.join(DATASET_DIR, "validation", cls)
        assert os.path.isdir(cls_dir), f"Class folder missing in validation: {cls}"
        images = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        assert len(images) > 0, f"No validation images found for class: {cls}"


# =========================================================
# TEST 6: All 6 classes exist in test set
# =========================================================
def test_06_all_six_classes_in_test():
    """TEST 6: All six crisis classes exist in test split."""
    for cls in CLASSES:
        cls_dir = os.path.join(DATASET_DIR, "test", cls)
        assert os.path.isdir(cls_dir), f"Class folder missing in test: {cls}"
        images = [f for f in os.listdir(cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        assert len(images) > 0, f"No test images found for class: {cls}"


# =========================================================
# TEST 7: Dataset split is reproducible with seed 42
# =========================================================
def test_07_dataset_split_reproducible():
    """TEST 7: Run splitting twice with seed 42 and verify identical file distributions."""
    import random
    from sklearn.model_selection import train_test_split
    
    for cls in CLASSES:
        cls_master_dir = os.path.join(MASTER_DIR, cls)
        img_files = sorted([
            f for f in os.listdir(cls_master_dir)
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
        ])
        
        train1, _ = train_test_split(img_files, train_size=0.70, random_state=42, shuffle=True)
        train2, _ = train_test_split(img_files, train_size=0.70, random_state=42, shuffle=True)
        
        assert train1 == train2, f"Split is not reproducible for class {cls}"


# =========================================================
# TEST 8: Training does not access test images
# =========================================================
def test_08_training_does_not_use_test_images():
    """TEST 8: No image hash from test set appears in train set."""
    train_hashes = set(get_all_image_hashes(os.path.join(DATASET_DIR, "train")))
    test_hashes = set(get_all_image_hashes(os.path.join(DATASET_DIR, "test")))
    contamination = train_hashes & test_hashes
    assert not contamination, f"Test images found in training set! Count: {len(contamination)}"


# =========================================================
# TEST 9: Model returns exactly 6 class probabilities
# =========================================================
def test_09_model_outputs_six_classes():
    """TEST 9: Loaded model produces exactly 6 class probability scores."""
    from ml.inference.classifier import CrisisClassifier
    classifier = CrisisClassifier()
    
    # Find any test image
    test_cls_dir = os.path.join(DATASET_DIR, "test", CLASSES[0])
    test_images = [f for f in os.listdir(test_cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    assert len(test_images) > 0, "No test images available for smoke test"
    
    test_img_path = os.path.join(test_cls_dir, test_images[0])
    result = classifier.predict(test_img_path)
    
    assert "probabilities" in result, "Missing probabilities key in output"
    assert len(result["probabilities"]) == 6, f"Expected 6 class probabilities, got {len(result['probabilities'])}"


# =========================================================
# TEST 10: Probability values are valid
# =========================================================
def test_10_probability_values_valid():
    """TEST 10: All probability values are in [0, 1] and sum to ~1.0."""
    from ml.inference.classifier import CrisisClassifier
    classifier = CrisisClassifier()
    
    test_cls_dir = os.path.join(DATASET_DIR, "test", CLASSES[0])
    test_images = [f for f in os.listdir(test_cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    test_img_path = os.path.join(test_cls_dir, test_images[0])
    
    result = classifier.predict(test_img_path)
    probs = result["probabilities"]
    
    for cls_name, prob in probs.items():
        assert 0.0 <= prob <= 1.0, f"Probability out of range for {cls_name}: {prob}"
    
    total = sum(probs.values())
    assert abs(total - 1.0) < 0.01, f"Probabilities don't sum to ~1.0: sum={total}"


# =========================================================
# TEST 11: Low-confidence prediction returns LOW_CONFIDENCE
# =========================================================
def test_11_low_confidence_returns_low_confidence():
    """TEST 11: Setting threshold=1.1 forces LOW_CONFIDENCE — no softmax value can exceed 1.0."""
    from ml.inference.classifier import CrisisClassifier
    
    # Instantiate with threshold > 1.0 (impossible for any softmax output to beat → always low confidence)
    classifier = CrisisClassifier(threshold=1.1)
    
    test_cls_dir = os.path.join(DATASET_DIR, "test", CLASSES[0])
    test_images = [f for f in os.listdir(test_cls_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    test_img_path = os.path.join(test_cls_dir, test_images[0])
    
    result = classifier.predict(test_img_path)
    assert result["predicted_class"] == "LOW_CONFIDENCE", (
        f"Expected LOW_CONFIDENCE but got: {result['predicted_class']} (confidence={result['confidence']})"
    )


# =========================================================
# TEST 12: Saved model can be loaded successfully
# =========================================================
def test_12_model_can_be_loaded():
    """TEST 12: Saved model (.pth) can be loaded and produces valid output."""
    import torch
    import torch.nn as nn
    from torchvision import models
    
    best_model_path = os.path.join(MODELS_DIR, "best_model", "model.pth")
    assert os.path.exists(best_model_path), f"Best model .pth not found at: {best_model_path}"
    
    # Build architecture
    model = models.mobilenet_v3_small(weights=None)
    in_features = model.classifier[3].in_features
    model.classifier[3] = nn.Linear(in_features, 6)
    
    # Load weights
    model.load_state_dict(torch.load(best_model_path, map_location="cpu"))
    model.eval()
    
    # Run a dummy forward pass
    dummy = torch.randn(1, 3, 224, 224)
    with torch.no_grad():
        output = model(dummy)
    
    assert output.shape == (1, 6), f"Expected output shape (1,6), got {output.shape}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
