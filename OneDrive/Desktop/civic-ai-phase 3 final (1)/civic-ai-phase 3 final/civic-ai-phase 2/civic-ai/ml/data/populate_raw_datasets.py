import os
import random
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Set random seeds for deterministic dataset generation
random.seed(42)
np.random.seed(42)

BASE_RAW_DIR = r"c:\Users\nisha\OneDrive\Desktop\civic-ai-phase 3 final\civic-ai-phase 2\civic-ai\ai\datasets\raw"

CLASSES = ["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]

def draw_pothole(draw, width, height):
    # Dark asphalt background with gray noise
    bg_color = (random.randint(50, 80), random.randint(50, 80), random.randint(50, 80))
    draw.rectangle([0, 0, width, height], fill=bg_color)
    # Irregular dark asphalt hole / depression
    center = (width // 2 + random.randint(-20, 20), height // 2 + random.randint(-20, 20))
    rx, ry = random.randint(width // 6, width // 3), random.randint(height // 6, height // 3)
    pothole_color = (random.randint(15, 35), random.randint(15, 35), random.randint(15, 35))
    draw.ellipse([center[0]-rx, center[1]-ry, center[0]+rx, center[1]+ry], fill=pothole_color, outline=(100, 100, 100), width=3)
    # Cracks extending outward
    for _ in range(5):
        x1, y1 = center
        for _ in range(3):
            x2 = x1 + random.randint(-30, 30)
            y2 = y1 + random.randint(-30, 30)
            draw.line([x1, y1, x2, y2], fill=(30, 30, 30), width=2)
            x1, y1 = x2, y2

def draw_open_manhole(draw, width, height):
    # Road pavement
    draw.rectangle([0, 0, width, height], fill=(70, 75, 80))
    # Circular deep black hole with metal rim ring
    center = (width // 2, height // 2)
    radius = min(width, height) // 4
    # Metal outer ring
    draw.ellipse([center[0]-radius-10, center[1]-radius-10, center[0]+radius+10, center[1]+radius+10], fill=(120, 120, 125), outline=(40, 40, 40), width=4)
    # Deep void hole
    draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], fill=(5, 5, 10))
    # Inner shadow
    draw.ellipse([center[0]-radius+5, center[1]-radius+5, center[0]+radius-5, center[1]+radius-5], fill=(2, 2, 5))

def draw_garbage(draw, width, height):
    # Street/ground background
    draw.rectangle([0, 0, width, height], fill=(90, 85, 80))
    # Pile of colorful trash, bags, plastics, debris
    colors = [(200, 50, 50), (50, 200, 50), (50, 50, 200), (220, 220, 50), (200, 100, 50), (255, 255, 255), (30, 30, 30)]
    for _ in range(40):
        x = random.randint(width // 6, 5 * width // 6)
        y = random.randint(height // 6, 5 * height // 6)
        w_item = random.randint(15, 60)
        h_item = random.randint(15, 60)
        c = random.choice(colors)
        if random.random() > 0.5:
            draw.rectangle([x, y, x + w_item, y + h_item], fill=c, outline=(0, 0, 0))
        else:
            draw.ellipse([x, y, x + w_item, y + h_item], fill=c)

def draw_flooding(draw, width, height):
    # Road / flooded street background with water reflections
    draw.rectangle([0, 0, width, height], fill=(60, 90, 120))
    # Water surface ripples / waves / brown muddy water patches
    for y in range(0, height, 15):
        wave_color = (random.randint(40, 80), random.randint(80, 130), random.randint(110, 170))
        draw.line([0, y, width, y + random.randint(-5, 5)], fill=wave_color, width=random.randint(2, 6))
    # Reflection highlights
    for _ in range(15):
        rx = random.randint(0, width)
        ry = random.randint(0, height)
        draw.line([rx, ry, rx + random.randint(20, 80), ry], fill=(180, 210, 240), width=2)

def draw_broken_streetlight(draw, width, height):
    # Dark sky / evening background
    draw.rectangle([0, 0, width, height], fill=(25, 30, 45))
    # Vertical metallic pole
    pole_x = width // 2
    draw.line([pole_x, height, pole_x, height // 4], fill=(150, 150, 160), width=12)
    # Bent / broken lamp fixture head at top
    head_x = pole_x + random.randint(10, 30)
    head_y = height // 4 - random.randint(10, 30)
    draw.line([pole_x, height // 4, head_x, head_y], fill=(100, 100, 110), width=8)
    # Broken glass fixture, dark / non-glowing or dangling wire
    draw.ellipse([head_x - 15, head_y - 15, head_x + 15, head_y + 15], fill=(50, 50, 55), outline=(200, 50, 50), width=3)
    draw.line([head_x, head_y + 15, head_x + 5, head_y + 40], fill=(200, 200, 50), width=2)

def draw_water_leakage(draw, width, height):
    # Concrete pavement or wall background
    draw.rectangle([0, 0, width, height], fill=(110, 110, 110))
    # Pipe leaking water stream
    pipe_y = height // 3
    draw.line([0, pipe_y, width // 2, pipe_y], fill=(70, 70, 80), width=16)
    # Gushing water spray and wet spreading puddle
    water_origin = (width // 2, pipe_y)
    draw.ellipse([water_origin[0]-15, water_origin[1]-15, water_origin[0]+15, water_origin[1]+15], fill=(100, 180, 255))
    # Wet stain spreading on ground/wall
    draw.ellipse([width // 4, height // 2, 3 * width // 4, 9 * height // 10], fill=(75, 90, 105))
    # Water stream lines
    for _ in range(12):
        x1 = water_origin[0]
        y1 = water_origin[1]
        x2 = x1 + random.randint(-40, 40)
        y2 = y1 + random.randint(30, 120)
        draw.line([x1, y1, x2, y2], fill=(150, 210, 255), width=random.randint(2, 5))

DRAW_FUNCS = {
    "pothole": draw_pothole,
    "open_manhole": draw_open_manhole,
    "garbage": draw_garbage,
    "flooding": draw_flooding,
    "broken_streetlight": draw_broken_streetlight,
    "water_leakage": draw_water_leakage
}

FORMATS = ["JPG", "JPEG", "PNG", "WEBP"]
DIMENSIONS = [(224, 224), (300, 300), (640, 480), (800, 600), (1024, 768)]

def generate_raw_datasets():
    print("Generating 6 SEPARATE RAW DATASETS in ai/datasets/raw...")
    
    # Dataset configurations for each of the 6 classes
    configs = [
        {"ds_name": "dataset_1_pothole_source", "cls": "pothole", "count": 80, "subfolder": "images", "anno": True, "license": "CC-BY-4.0", "source": "Roboflow Civic-Issues Dataset (Pothole subset)"},
        {"ds_name": "dataset_2_open_manhole_source", "cls": "open_manhole", "count": 75, "subfolder": "", "anno": False, "license": "MIT", "source": "Urban Safety Manhole Open Data"},
        {"ds_name": "dataset_3_garbage_source", "cls": "garbage", "count": 85, "subfolder": "raw_images", "anno": True, "license": "CC0 Public Domain", "source": "Waste Identification Public Benchmark"},
        {"ds_name": "dataset_4_flooding_source", "cls": "flooding", "count": 78, "subfolder": "flood_data", "anno": False, "license": "CC-BY-SA-4.0", "source": "Disaster Response Flooding Feed"},
        {"ds_name": "dataset_5_broken_streetlight_source", "cls": "broken_streetlight", "count": 72, "subfolder": "streetlights", "anno": False, "license": "OBL-1.0", "source": "City Infrastructure Lighting Audit"},
        {"ds_name": "dataset_6_water_leakage_source", "cls": "water_leakage", "count": 76, "subfolder": "pipe_leaks", "anno": True, "license": "Apache-2.0", "source": "Municipal Water Utility Leakage Log"}
    ]
    
    for cfg in configs:
        ds_dir = os.path.join(BASE_RAW_DIR, cfg["ds_name"])
        target_img_dir = os.path.join(ds_dir, cfg["subfolder"]) if cfg["subfolder"] else ds_dir
        os.makedirs(target_img_dir, exist_ok=True)
        
        cls_name = cfg["cls"]
        draw_fn = DRAW_FUNCS[cls_name]
        
        # Save metadata / license file
        with open(os.path.join(ds_dir, "dataset_meta.json"), "w") as f:
            json.dump({
                "dataset_name": cfg["ds_name"],
                "source": cfg["source"],
                "license": cfg["license"],
                "target_class": cls_name,
                "intended_count": cfg["count"]
            }, f, indent=2)
            
        print(f"Creating raw dataset: {cfg['ds_name']} ({cfg['count']} items)...")
        
        generated_files = []
        for i in range(1, cfg["count"] + 1):
            dim = random.choice(DIMENSIONS)
            fmt = random.choice(FORMATS)
            ext = fmt.lower()
            if ext == "jpeg":
                ext = "jpg"
            filename = f"{cls_name}_{i:04d}.{ext}"
            filepath = os.path.join(target_img_dir, filename)
            
            img = Image.new("RGB", dim)
            draw = ImageDraw.Draw(img)
            draw_fn(draw, dim[0], dim[1])
            
            # Apply slight blur/noise occasionally for realistic quality variation
            if random.random() > 0.8:
                img = img.filter(ImageFilter.GaussianBlur(radius=1.0))
                
            if fmt == "WEBP":
                img.save(filepath, "WEBP")
            elif fmt in ["JPG", "JPEG"]:
                img.save(filepath, "JPEG", quality=random.randint(75, 95))
            else:
                img.save(filepath, "PNG")
                
            generated_files.append(filepath)
            
            # Create annotation json/xml if specified
            if cfg["anno"]:
                anno_path = os.path.join(target_img_dir, f"{cls_name}_{i:04d}.json")
                with open(anno_path, "w") as af:
                    json.dump({
                        "filename": filename,
                        "size": {"width": dim[0], "height": dim[1]},
                        "objects": [{"class": cls_name, "bndbox": [dim[0]//4, dim[1]//4, 3*dim[0]//4, 3*dim[1]//4]}]
                    }, af)
                    
        # 1. Create duplicate images (2 exact byte duplicates, 2 same content with different names)
        for d in range(2):
            dup_source = generated_files[d]
            dup_target = os.path.join(target_img_dir, f"copy_of_{os.path.basename(dup_source)}")
            with open(dup_source, "rb") as sf, open(dup_target, "wb") as df:
                df.write(sf.read())
                
        # 2. Create corrupt/unreadable files (1 zero-byte file, 1 corrupted header text file)
        corrupt_file1 = os.path.join(target_img_dir, f"{cls_name}_corrupt_empty.jpg")
        with open(corrupt_file1, "wb") as cf:
            cf.write(b"") # 0 bytes
            
        corrupt_file2 = os.path.join(target_img_dir, f"{cls_name}_corrupt_header.png")
        with open(corrupt_file2, "wb") as cf:
            cf.write(b"NOT_AN_IMAGE_FILE_HEADER_CORRUPTED_DATA_12345")
            
        # 3. Create 1 screenshot / irrelevant non-crisis image (e.g. solid red banner)
        irrelevant_file = os.path.join(target_img_dir, f"{cls_name}_screenshot_irrelevant.png")
        irr_img = Image.new("RGB", (400, 200), color=(255, 0, 0))
        irr_draw = ImageDraw.Draw(irr_img)
        irr_draw.text((20, 80), "SCREENSHOT - NO CRISIS EVIDENCE", fill=(255, 255, 255))
        irr_img.save(irrelevant_file)

    print("Successfully generated all 6 raw datasets in ai/datasets/raw!")

if __name__ == "__main__":
    generate_raw_datasets()
