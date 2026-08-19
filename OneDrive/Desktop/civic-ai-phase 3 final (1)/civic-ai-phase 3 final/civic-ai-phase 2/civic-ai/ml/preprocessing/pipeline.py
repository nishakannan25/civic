from torchvision import transforms
from PIL import Image

IMAGE_SIZE = (224, 224)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def get_transforms(is_training=True):
    """
    Returns image transformation pipeline for PyTorch model.
    Augmentations are applied ONLY when is_training is True.
    """
    if is_training:
        return transforms.Compose([
            transforms.Resize(IMAGE_SIZE),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
    else:
        return transforms.Compose([
            transforms.Resize(IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])

def preprocess_image(image_path):
    """
    Loads an image file, converts to RGB mode, and applies standard validation preprocessing.
    Returns PyTorch tensor of shape (1, 3, 224, 224).
    """
    with Image.open(image_path) as img:
        rgb_img = img.convert("RGB")
    transform = get_transforms(is_training=False)
    tensor = transform(rgb_img).unsqueeze(0)
    return tensor
