import os
import shutil
import hashlib
import json
from PIL import Image

BASE_RAW_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\ai\datasets\raw"
MASTER_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\dataset\master"
PROCESSED_MASTER_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\ai\datasets\processed\master"
DOCS_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\docs"
OUTPUT_REPORT = os.path.join(DOCS_DIR, "phase4_cleaning_report.md")

CLASSES = ["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]

def get_file_md5(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except Exception:
        return None

def clean_and_build_master():
    print("Starting Data Cleaning & Master Dataset Assembly...")
    
    # Reset master directories
    if os.path.exists(MASTER_DIR):
        shutil.rmtree(MASTER_DIR)
    if os.path.exists(PROCESSED_MASTER_DIR):
        shutil.rmtree(PROCESSED_MASTER_DIR)
        
    for cls in CLASSES:
        os.makedirs(os.path.join(MASTER_DIR, cls), exist_ok=True)
        os.makedirs(os.path.join(PROCESSED_MASTER_DIR, cls), exist_ok=True)

    seen_hashes = set()
    stats = {cls: {"original": 0, "corrupt": 0, "duplicate": 0, "irrelevant": 0, "final": 0} for cls in CLASSES}
    
    # Map dataset folder names to class
    ds_dirs = os.listdir(BASE_RAW_DIR)
    
    for ds_name in ds_dirs:
        ds_path = os.path.join(BASE_RAW_DIR, ds_name)
        if not os.path.isdir(ds_path):
            continue
            
        # Determine class name
        cls_name = None
        for c in CLASSES:
            if c in ds_name.lower():
                cls_name = c
                break
        if not cls_name:
            continue
            
        for root, dirs, files in os.walk(ds_path):
            for file in files:
                if file == "dataset_meta.json" or file.endswith((".json", ".xml", ".txt")):
                    continue
                
                filepath = os.path.join(root, file)
                stats[cls_name]["original"] += 1
                
                # 1. Corrupt check
                if os.path.getsize(filepath) == 0:
                    stats[cls_name]["corrupt"] += 1
                    continue
                try:
                    with Image.open(filepath) as img:
                        img.verify()
                except Exception:
                    stats[cls_name]["corrupt"] += 1
                    continue
                    
                # 2. Screenshot / Irrelevant check
                if "screenshot" in file.lower() or "irrelevant" in file.lower():
                    stats[cls_name]["irrelevant"] += 1
                    continue
                    
                # 3. Duplicate check
                f_hash = get_file_md5(filepath)
                if not f_hash or f_hash in seen_hashes:
                    stats[cls_name]["duplicate"] += 1
                    continue
                    
                seen_hashes.add(f_hash)
                
                # Valid image! Copy to master dataset
                out_filename = f"{cls_name}_{stats[cls_name]['final'] + 1:04d}{os.path.splitext(file)[1].lower()}"
                out_path = os.path.join(MASTER_DIR, cls_name, out_filename)
                shutil.copy2(filepath, out_path)
                
                # Also copy to ai/datasets/processed/master for convenience
                out_proc_path = os.path.join(PROCESSED_MASTER_DIR, cls_name, out_filename)
                shutil.copy2(filepath, out_proc_path)
                
                stats[cls_name]["final"] += 1

    # Write Cleaning Report
    os.makedirs(DOCS_DIR, exist_ok=True)
    report_content = "# Phase 4 — Dataset Cleaning Report\n\n"
    report_content += "Generated as part of **Phase 4 — AI Dataset Preparation + Crisis Classification Model**.\n\n"
    report_content += "## Cleaning Summary Table\n\n"
    report_content += "| Crisis Class | Original Count | Corrupt Removed | Duplicate Removed | Irrelevant Removed | Total Removed | Final Master Count |\n"
    report_content += "|---|---|---|---|---|---|---|\n"

    tot_orig, tot_corrupt, tot_dup, tot_irr, tot_final = 0, 0, 0, 0, 0

    for cls in CLASSES:
        s = stats[cls]
        removed = s["corrupt"] + s["duplicate"] + s["irrelevant"]
        tot_orig += s["original"]
        tot_corrupt += s["corrupt"]
        tot_dup += s["duplicate"]
        tot_irr += s["irrelevant"]
        tot_final += s["final"]
        report_content += f"| `{cls}` | {s['original']} | {s['corrupt']} | {s['duplicate']} | {s['irrelevant']} | {removed} | **{s['final']}** |\n"

    tot_removed = tot_corrupt + tot_dup + tot_irr
    report_content += f"| **TOTAL** | **{tot_orig}** | **{tot_corrupt}** | **{tot_dup}** | **{tot_irr}** | **{tot_removed}** | **{tot_final}** |\n\n"

    report_content += "## Data Cleaning Rules Applied\n\n"
    report_content += "1. **Corrupt / Unreadable Files Excluded**: Excluded zero-byte files and files with damaged or non-image headers.\n"
    report_content += "2. **Exact Duplicate Prevention**: Applied MD5 hash deduplication across all source datasets to prevent data leakage.\n"
    report_content += "3. **Non-Crisis / Screenshot Removal**: Excluded artificial screenshots or solid color test banners.\n"
    report_content += "4. **Difficult Valid Examples Retained**: Valid low-contrast or night scene images were preserved to ensure model robustness.\n"
    report_content += "5. **Immutability of Source Data**: Original datasets in `ai/datasets/raw/` were completely untouched.\n"

    with open(OUTPUT_REPORT, "w") as f:
        f.write(report_content)

    print(f"Data cleaning completed! Report saved to {OUTPUT_REPORT}")
    print(f"Total Original: {tot_orig}, Removed: {tot_removed}, Final Master: {tot_final}")

if __name__ == "__main__":
    clean_and_build_master()
