import base64
import os
import shutil
from PIL import Image
import requests
import lpips
import torch
import torchvision.transforms as transforms

lpips_model = lpips.LPIPS(net='alex')

def encode_image_to_base64(image_path):
    """
    Encodes an image file to a base64 string suitable for OpenAI API.
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
            
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
        return None
        
    except Exception as e:
        print(f"Error encoding image {image_path}: {e}")
        return None
        
def save_image_from_b64(image_b64, save_path):
    """
    Saves an image from base 64 and saves it to a specified path.
    """
    try:
        image_bytes = base64.b64decode(image_b64)

        with open(save_path, "wb") as f:
            f.write(image_bytes)
            
        print(f"Image saved as {save_path}")
        return True
        
    except Exception as e:
        print(f"An unexpected error occurred while saving image {save_path}: {e}")
        return False
        
def evaluate_image_quality(image_path1, image_path2):
    """
    Computes LPIPS perceptual similarity score between two images.
    Lower score = more similar.
    """

    transform = transforms.Compose([
        transforms.Resize((256, 256)),  
        transforms.ToTensor(),
        transforms.Normalize(mean = [0.5]*3, std = [0.5]*3)
    ])

    def load_image(path):
        image = Image.open(path).convert('RGB')
        return transform(image).unsqueeze(0) 

    try:
        img1 = load_image(image_path1)
        img2 = load_image(image_path2)
        
        with torch.no_grad():
            score = lpips_model(img1, img2).item()
        
        return -score  
        
    except Exception as e:
        print(f"Error computing similarity between {image_path1} and {image_path2}: {e}")
        return float('-inf')

def copy_image(source_path, destination_path):
    """
    Copies an image file from source_path to destination_path.
    """
    try:
        shutil.copy(source_path, destination_path)
        return True
        
    except FileNotFoundError:
        print(f"Error: Source image not found at {source_path}")
        return False
        
    except Exception as e:
        print(f"Error copying image from {source_path} to {destination_path}: {e}")
        return False