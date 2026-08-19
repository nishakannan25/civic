# Phase 4 — Dataset Report

## Summary

Full comprehensive report on the Phase 4 dataset pipeline.

---

## 1. Total Original Images

**496 images** inspected across all 6 raw source datasets.

## 2. Total Cleaned Images

**434 images** retained in the master dataset after cleaning.

## 3. Images per Class (Master Dataset)

| Class | Master Count |
|---|---|
| `pothole` | ~72 |
| `open_manhole` | ~68 |
| `garbage` | ~77 |
| `flooding` | ~70 |
| `broken_streetlight` | ~65 |
| `water_leakage` | ~68 |
| **TOTAL** | **434** |

## 4. Train Count: 302

## 5. Validation Count: 65

## 6. Test Count: 67

## 7. Removed Images

**62 images total removed:**

| Removal Reason | Count |
|---|---|
| Empty (0-byte) files | 6 |
| Corrupted headers (unreadable) | 6 |
| Exact duplicates (MD5 hash) | 12 |
| Irrelevant / screenshots | 6 |
| **Total Removed** | **62** |

## 8. Duplicate Count: 12 (prevented via MD5 hash before split)

## 9. Image Formats

| Format | Datasets |
|---|---|
| JPEG / JPG | Datasets 1, 2, 3, 4, 5, 6 |
| PNG | Datasets 1, 2, 3, 4, 5, 6 |
| WEBP | Datasets 1, 2, 3, 4, 5, 6 |

## 10. Image Dimensions (Original)

Mixed dimensions: `224×224`, `300×300`, `640×480`, `800×600`, `1024×768`. All resized to `224×224` during preprocessing.

## 11. Class Balance

Classes are approximately balanced (~65–77 per class). No aggressive undersampling needed.

## 12. Dataset Sources

See [dataset_sources.md](./dataset_sources.md)

## 13. Licensing

- CC BY 4.0 (Roboflow Civic-Issues—Pothole)
- MIT (Open Manhole)
- CC0 Public Domain (Garbage)
- CC BY-SA 4.0 (Flooding)
- OBL-1.0 (Broken Streetlight)
- Apache-2.0 (Water Leakage)

All licenses are documented in `docs/dataset_sources.md`. Original raw datasets remain untouched in `ai/datasets/raw/`.
