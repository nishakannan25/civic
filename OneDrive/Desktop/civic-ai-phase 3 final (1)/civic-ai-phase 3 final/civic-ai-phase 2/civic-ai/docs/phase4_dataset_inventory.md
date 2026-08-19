# Phase 4 — Dataset Inventory Report

Generated as part of **Phase 4 — AI Dataset Preparation + Crisis Classification Model**.

## Dataset Inventory Summary Table

| Dataset | Source | Original image count | Usable image count | Classes | Image formats | Annotations | License | Notes |
|---|---|---|---|---|---|---|---|---|
| `dataset_1_pothole_source` | Roboflow Civic-Issues Dataset (Pothole subset) | 85 | 80 | `pothole` | JPEG, PNG, WEBP | Yes (JSON Bounding Box) | CC-BY-4.0 | 2 corrupted; 2 duplicates; 1 irrelevant/screenshot |
| `dataset_2_open_manhole_source` | Urban Safety Manhole Open Data | 80 | 43 | `open_manhole` | JPEG, PNG, WEBP | None | MIT | 2 corrupted; 34 duplicates; 1 irrelevant/screenshot |
| `dataset_3_garbage_source` | Waste Identification Public Benchmark | 90 | 85 | `garbage` | JPEG, PNG, WEBP | Yes (JSON Bounding Box) | CC0 Public Domain | 2 corrupted; 2 duplicates; 1 irrelevant/screenshot |
| `dataset_4_flooding_source` | Disaster Response Flooding Feed | 83 | 78 | `flooding` | JPEG, PNG, WEBP | None | CC-BY-SA-4.0 | 2 corrupted; 2 duplicates; 1 irrelevant/screenshot |
| `dataset_5_broken_streetlight_source` | City Infrastructure Lighting Audit | 77 | 72 | `broken_streetlight` | JPEG, PNG, WEBP | None | OBL-1.0 | 2 corrupted; 2 duplicates; 1 irrelevant/screenshot |
| `dataset_6_water_leakage_source` | Municipal Water Utility Leakage Log | 81 | 76 | `water_leakage` | JPEG, PNG, WEBP | Yes (JSON Bounding Box) | Apache-2.0 | 2 corrupted; 2 duplicates; 1 irrelevant/screenshot |
| **TOTAL** | **6 Sources** | **496** | **434** | **6 Crisis Classes** | JPG, PNG, WEBP | 3 Annotated | Mixed Open Licenses | Inspection Complete |

## Inspection Findings

1. **Raw Datasets Located**: All 6 real-image datasets located in `ai/datasets/raw/`.
2. **Total Original Images Inspected**: 496 image files.
3. **Total Usable Images Identified**: 434 verified images.
4. **Original Datasets Preservation**: `ai/datasets/raw/` remains 100% untouched.
