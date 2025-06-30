import base64
import os
import shutil
from PIL import Image
import requests
import torch
import torchvision.transforms as transforms
from skimage.metrics import structural_similarity as ssim
import numpy as np

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
    img1_pil = Image.open(image_path1).resize((256, 256)).convert('RGB')
    img2_pil = Image.open(image_path2).resize((256, 256)).convert('RGB')
    img1 = np.array(img1_pil)
    img2 = np.array(img2_pil)
    img1_pil.close()
    img2_pil.close()
    score, _ = ssim(img1, img2, full=True, channel_axis=-1)
    return score

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
