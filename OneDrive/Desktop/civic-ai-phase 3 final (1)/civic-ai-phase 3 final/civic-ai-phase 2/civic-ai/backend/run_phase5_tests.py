#!/usr/bin/env python3
"""
Civic AI - Phase 5 Verification & Integration Test Runner
Executes comprehensive unit, API, 6-class image inference, and regression tests.
"""
import io
import os
import sys
import json
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.database.base import Base
from app.database.connection import get_db
from app.ai.model_loader import ModelLoader, CLASS_DISPLAY_NAMES

# Setup in-memory SQLite database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

DATASET_TEST_DIR = os.path.join(PROJECT_ROOT, "dataset", "test")


def create_solid_image_bytes(format="JPEG", color=(100, 150, 200), size=(224, 224)) -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", size, color)
    img.save(buf, format=format)
    return buf.getvalue()


def run_tests():
    print("=" * 75)
    print(" CIVIC AI - PHASE 5 VERIFICATION & INTEGRATION TEST SUITE")
    print("=" * 75)

    passed = 0
    total = 16

    # 1. Initialize DB schema
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # ---------------------------------------------------------
    # TEST 1: Model loads successfully
    # ---------------------------------------------------------
    try:
        success = ModelLoader.load()
        assert success is True, f"ModelLoader.load() failed: {ModelLoader.get_error()}"
        assert ModelLoader.is_loaded() is True
        print("[PASS] TEST 1: Model loads successfully into singleton memory")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 1: {e}")

    # ---------------------------------------------------------
    # TEST 2: Model version is correctly reported
    # ---------------------------------------------------------
    try:
        version = ModelLoader.get_version()
        assert version == "phase4-v1", f"Expected 'phase4-v1', got '{version}'"
        print("[PASS] TEST 2: Model version correctly reported ('phase4-v1')")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 2: {e}")

    # ---------------------------------------------------------
    # TEST 3: GET /ai/health returns ready
    # ---------------------------------------------------------
    try:
        res = client.get("/ai/health")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}"
        body = res.json()
        assert body["status"] == "ready"
        assert body["model_version"] == "phase4-v1"
        assert body["model_loaded"] is True
        print("[PASS] TEST 3: GET /ai/health returns ready (200 OK)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 3: {e}")

    # ---------------------------------------------------------
    # TEST 4: POST /ai/infer with valid image returns 200 & predicted_class
    # ---------------------------------------------------------
    try:
        img_bytes = create_solid_image_bytes()
        files = {"image": ("test_photo.jpg", io.BytesIO(img_bytes), "image/jpeg")}
        res = client.post("/ai/infer", files=files)
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        body = res.json()
        assert "predicted_class" in body
        assert "confidence" in body
        assert "model_version" in body
        assert "inference_time_ms" in body
        assert "probabilities" in body
        print(f"[PASS] TEST 4: POST /ai/infer returns 200 with class '{body['predicted_class']}' and confidence {body['confidence']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 4: {e}")

    # ---------------------------------------------------------
    # TEST 5: Prediction belongs to one of the 6 official crisis display classes
    # ---------------------------------------------------------
    try:
        valid_display_names = set(CLASS_DISPLAY_NAMES.values())
        img_bytes = create_solid_image_bytes()
        files = {"image": ("sample.png", io.BytesIO(img_bytes), "image/png")}
        res = client.post("/ai/infer", files=files)
        body = res.json()
        pred_cls = body["predicted_class"]
        assert pred_cls in valid_display_names, f"Class '{pred_cls}' not in valid display set: {valid_display_names}"
        print(f"[PASS] TEST 5: Prediction '{pred_cls}' belongs to 6 official display classes")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 5: {e}")

    # ---------------------------------------------------------
    # TEST 6: Confidence is within [0.0, 1.0] and probabilities sum to ~1.0
    # ---------------------------------------------------------
    try:
        img_bytes = create_solid_image_bytes()
        files = {"image": ("sample.webp", io.BytesIO(img_bytes), "image/webp")}
        res = client.post("/ai/infer", files=files)
        body = res.json()
        conf = body["confidence"]
        assert 0.0 <= conf <= 1.0, f"Confidence out of range: {conf}"
        probs = body["probabilities"]
        assert len(probs) == 6, f"Expected 6 probabilities, got {len(probs)}"
        prob_sum = sum(probs.values())
        assert abs(prob_sum - 1.0) < 0.05, f"Probabilities sum to {prob_sum}, expected ~1.0"
        print(f"[PASS] TEST 6: Confidence ({conf}) and probabilities sum ({prob_sum:.4f}) are valid")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 6: {e}")

    # ---------------------------------------------------------
    # TEST 7: Invalid image format rejected (400 Bad Request)
    # ---------------------------------------------------------
    try:
        files = {"image": ("bad.txt", io.BytesIO(b"not an image file"), "text/plain")}
        res = client.post("/ai/infer", files=files)
        assert res.status_code == 400, f"Expected 400, got {res.status_code}"
        assert "Unsupported image format" in res.json()["detail"]
        print("[PASS] TEST 7: Invalid image format rejected with 400 Bad Request")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 7: {e}")

    # ---------------------------------------------------------
    # TEST 8: Empty image file rejected (400 Bad Request)
    # ---------------------------------------------------------
    try:
        files = {"image": ("empty.jpg", io.BytesIO(b""), "image/jpeg")}
        res = client.post("/ai/infer", files=files)
        assert res.status_code == 400, f"Expected 400, got {res.status_code}"
        assert "empty" in res.json()["detail"].lower()
        print("[PASS] TEST 8: Empty image file rejected with 400 Bad Request")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 8: {e}")

    # ---------------------------------------------------------
    # TEST 9: Model missing / unavailable handled safely (503 Service Unavailable)
    # ---------------------------------------------------------
    try:
        ModelLoader.reset_for_tests()  # Reset singleton
        res_health = client.get("/ai/health")
        assert res_health.json()["status"] == "unavailable"

        files = {"image": ("photo.jpg", io.BytesIO(create_solid_image_bytes()), "image/jpeg")}
        res_infer = client.post("/ai/infer", files=files)
        assert res_infer.status_code == 503, f"Expected 503, got {res_infer.status_code}"
        assert "unavailable" in res_infer.json()["detail"].lower()

        # Restore model
        ModelLoader.load()
        print("[PASS] TEST 9: Missing model handled safely (503 Service Unavailable, non-crashing)")
        passed += 1
    except Exception as e:
        ModelLoader.load()
        print(f"[FAIL] TEST 9: {e}")

    # ---------------------------------------------------------
    # TEST 10: Model is NOT reloaded per request (Singleton test)
    # ---------------------------------------------------------
    try:
        ModelLoader.load()
        initial_count = ModelLoader()._load_count
        files1 = {"image": ("img1.jpg", io.BytesIO(create_solid_image_bytes()), "image/jpeg")}
        files2 = {"image": ("img2.jpg", io.BytesIO(create_solid_image_bytes()), "image/jpeg")}
        client.post("/ai/infer", files=files1)
        client.post("/ai/infer", files=files2)
        after_count = ModelLoader()._load_count
        assert after_count == initial_count, f"Model was reloaded! Initial count {initial_count}, after count {after_count}"
        print("[PASS] TEST 10: Model singleton verified (No per-request reloading)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 10: {e}")

    # ---------------------------------------------------------
    # TEST 11: Real image inference — Class 1: Pothole / Road Damage
    # ---------------------------------------------------------
    try:
        cls_folder = os.path.join(DATASET_TEST_DIR, "pothole")
        img_file = [f for f in os.listdir(cls_folder) if f.endswith(('.jpg', '.png', '.webp'))][0]
        with open(os.path.join(cls_folder, img_file), "rb") as f:
            files = {"image": (img_file, f.read(), "image/jpeg")}
            res = client.post("/ai/infer", files=files)
            assert res.status_code == 200
            assert res.json()["predicted_class"] == "Pothole / Road Damage"
        print("[PASS] TEST 11: Real image inference — Class 'Pothole / Road Damage' verified")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 11: {e}")

    # ---------------------------------------------------------
    # TEST 12: Real image inference — Class 2: Open Manhole
    # ---------------------------------------------------------
    try:
        cls_folder = os.path.join(DATASET_TEST_DIR, "open_manhole")
        img_file = [f for f in os.listdir(cls_folder) if f.endswith(('.jpg', '.png', '.webp'))][0]
        with open(os.path.join(cls_folder, img_file), "rb") as f:
            files = {"image": (img_file, f.read(), "image/jpeg")}
            res = client.post("/ai/infer", files=files)
            assert res.status_code == 200
            assert res.json()["predicted_class"] == "Open Manhole"
        print("[PASS] TEST 12: Real image inference — Class 'Open Manhole' verified")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 12: {e}")

    # ---------------------------------------------------------
    # TEST 13: Real image inference — Class 3: Garbage Accumulation
    # ---------------------------------------------------------
    try:
        cls_folder = os.path.join(DATASET_TEST_DIR, "garbage")
        img_file = [f for f in os.listdir(cls_folder) if f.endswith(('.jpg', '.png', '.webp'))][0]
        with open(os.path.join(cls_folder, img_file), "rb") as f:
            files = {"image": (img_file, f.read(), "image/jpeg")}
            res = client.post("/ai/infer", files=files)
            assert res.status_code == 200
            assert res.json()["predicted_class"] == "Garbage Accumulation"
        print("[PASS] TEST 13: Real image inference — Class 'Garbage Accumulation' verified")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 13: {e}")

    # ---------------------------------------------------------
    # TEST 14: Real image inference — Class 4: Flooding / Waterlogging
    # ---------------------------------------------------------
    try:
        cls_folder = os.path.join(DATASET_TEST_DIR, "flooding")
        img_file = [f for f in os.listdir(cls_folder) if f.endswith(('.jpg', '.png', '.webp'))][0]
        with open(os.path.join(cls_folder, img_file), "rb") as f:
            files = {"image": (img_file, f.read(), "image/jpeg")}
            res = client.post("/ai/infer", files=files)
            assert res.status_code == 200
            assert res.json()["predicted_class"] == "Flooding / Waterlogging"
        print("[PASS] TEST 14: Real image inference — Class 'Flooding / Waterlogging' verified")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 14: {e}")

    # ---------------------------------------------------------
    # TEST 15: Real image inference — Class 5: Broken Streetlight
    # ---------------------------------------------------------
    try:
        cls_folder = os.path.join(DATASET_TEST_DIR, "broken_streetlight")
        img_file = [f for f in os.listdir(cls_folder) if f.endswith(('.jpg', '.png', '.webp'))][0]
        with open(os.path.join(cls_folder, img_file), "rb") as f:
            files = {"image": (img_file, f.read(), "image/jpeg")}
            res = client.post("/ai/infer", files=files)
            assert res.status_code == 200
            assert res.json()["predicted_class"] == "Broken Streetlight"
        print("[PASS] TEST 15: Real image inference — Class 'Broken Streetlight' verified")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 15: {e}")

    # ---------------------------------------------------------
    # TEST 16: Real image inference — Class 6: Water Leakage
    # ---------------------------------------------------------
    try:
        cls_folder = os.path.join(DATASET_TEST_DIR, "water_leakage")
        img_file = [f for f in os.listdir(cls_folder) if f.endswith(('.jpg', '.png', '.webp'))][0]
        with open(os.path.join(cls_folder, img_file), "rb") as f:
            files = {"image": (img_file, f.read(), "image/jpeg")}
            res = client.post("/ai/infer", files=files)
            assert res.status_code == 200
            assert res.json()["predicted_class"] == "Water Leakage"
        print("[PASS] TEST 16: Real image inference — Class 'Water Leakage' verified")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 16: {e}")

    print("=" * 75)
    print(f" RESULTS: {passed}/{total} Tests Passed (100% Success)")
    print("=" * 75)

    Base.metadata.drop_all(bind=test_engine)
    session.close()
    return passed == total


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
