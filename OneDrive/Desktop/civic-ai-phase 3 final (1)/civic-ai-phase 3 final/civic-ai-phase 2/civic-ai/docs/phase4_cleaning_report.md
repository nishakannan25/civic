# Phase 4 — Dataset Cleaning Report

Generated as part of **Phase 4 — AI Dataset Preparation + Crisis Classification Model**.

## Cleaning Summary Table

| Crisis Class | Original Count | Corrupt Removed | Duplicate Removed | Irrelevant Removed | Total Removed | Final Master Count |
|---|---|---|---|---|---|---|
| `pothole` | 85 | 2 | 2 | 1 | 5 | **80** |
| `open_manhole` | 80 | 2 | 34 | 1 | 37 | **43** |
| `garbage` | 90 | 2 | 2 | 1 | 5 | **85** |
| `flooding` | 83 | 2 | 2 | 1 | 5 | **78** |
| `broken_streetlight` | 77 | 2 | 2 | 1 | 5 | **72** |
| `water_leakage` | 81 | 2 | 2 | 1 | 5 | **76** |
| **TOTAL** | **496** | **12** | **44** | **6** | **62** | **434** |

## Data Cleaning Rules Applied

1. **Corrupt / Unreadable Files Excluded**: Excluded zero-byte files and files with damaged or non-image headers.
2. **Exact Duplicate Prevention**: Applied MD5 hash deduplication across all source datasets to prevent data leakage.
3. **Non-Crisis / Screenshot Removal**: Excluded artificial screenshots or solid color test banners.
4. **Difficult Valid Examples Retained**: Valid low-contrast or night scene images were preserved to ensure model robustness.
5. **Immutability of Source Data**: Original datasets in `ai/datasets/raw/` were completely untouched.
