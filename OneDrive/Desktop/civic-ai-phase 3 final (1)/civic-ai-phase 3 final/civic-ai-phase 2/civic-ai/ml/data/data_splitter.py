import os
import shutil
import random
from sklearn.model_selection import train_test_split

MASTER_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\dataset\master"
BASE_DATASET_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\dataset"
PROCESSED_BASE_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\ai\datasets\processed"

CLASSES = ["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]
RANDOM_SEED = 42

def perform_split():
    print(f"Starting Stratified 70/15/15 Dataset Split (Random Seed: {RANDOM_SEED})...")
    random.seed(RANDOM_SEED)

    splits = ["train", "validation", "test"]
    
    # Reset target directories
    for s in splits:
        s_dir = os.path.join(BASE_DATASET_DIR, s)
        p_dir = os.path.join(PROCESSED_BASE_DIR, s)
        if os.path.exists(s_dir):
            shutil.rmtree(s_dir)
        if os.path.exists(p_dir):
            shutil.rmtree(p_dir)
            
        for cls in CLASSES:
            os.makedirs(os.path.join(s_dir, cls), exist_ok=True)
            os.makedirs(os.path.join(p_dir, cls), exist_ok=True)

    split_counts = {s: {cls: 0 for cls in CLASSES} for s in splits}

    for cls in CLASSES:
        cls_master_dir = os.path.join(MASTER_DIR, cls)
        img_files = [f for f in os.listdir(cls_master_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
        img_files.sort()
        
        # 70% Train, 30% Temp (which will be split 50/50 into Val and Test -> 15% each)
        train_files, temp_files = train_test_split(
            img_files, train_size=0.70, random_state=RANDOM_SEED, shuffle=True
        )
        val_files, test_files = train_test_split(
            temp_files, train_size=0.50, random_state=RANDOM_SEED, shuffle=True
        )

        file_mapping = {
            "train": train_files,
            "validation": val_files,
            "test": test_files
        }

        for s in splits:
            for fname in file_mapping[s]:
                src_path = os.path.join(cls_master_dir, fname)
                
                # Copy to dataset/<split>/<class>/
                dst_path = os.path.join(BASE_DATASET_DIR, s, cls, fname)
                shutil.copy2(src_path, dst_path)
                
                # Copy to ai/datasets/processed/<split>/<class>/
                dst_proc_path = os.path.join(PROCESSED_BASE_DIR, s, cls, fname)
                shutil.copy2(src_path, dst_proc_path)
                
                split_counts[s][cls] += 1

    print("\nDataset Split Summary:")
    print(f"{'Class':<20} | {'Train (70%)':<12} | {'Val (15%)':<12} | {'Test (15%)':<12} | {'Total':<10}")
    print("-" * 75)

    tot_train, tot_val, tot_test = 0, 0, 0
    for cls in CLASSES:
        tr = split_counts["train"][cls]
        va = split_counts["validation"][cls]
        te = split_counts["test"][cls]
        tot = tr + va + te
        tot_train += tr
        tot_val += va
        tot_test += te
        print(f"{cls:<20} | {tr:<12} | {va:<12} | {te:<12} | {tot:<10}")

    grand_total = tot_train + tot_val + tot_test
    print("-" * 75)
    print(f"{'TOTAL':<20} | {tot_train:<12} | {tot_val:<12} | {tot_test:<12} | {grand_total:<10}")
    print(f"\nPercentages: Train={tot_train/grand_total:.1%}, Val={tot_val/grand_total:.1%}, Test={tot_test/grand_total:.1%}")

if __name__ == "__main__":
    perform_split()
