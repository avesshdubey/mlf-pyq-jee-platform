import fitz
import os
import glob
import re
import json
import hashlib
import asyncio
from pathlib import Path

# Paths
BASE_DIR = r"C:\Users\avesh\Desktop\PYQS"
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "q_images")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# WinRT OCR setup for Windows
try:
    import winrt.windows.media.ocr as win_ocr
    import winrt.windows.graphics.imaging as win_imaging
    import winrt.windows.storage as win_storage
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

async def ocr_image_bytes(image_bytes):
    if not OCR_AVAILABLE or not image_bytes:
        return ""
    temp_path = os.path.join(ASSETS_DIR, f"temp_ocr_{hashlib.md5(image_bytes).hexdigest()[:8]}.png")
    try:
        with open(temp_path, "wb") as f:
            f.write(image_bytes)
        f_obj = await win_storage.StorageFile.get_file_from_path_async(os.path.abspath(temp_path))
        stream = await f_obj.open_async(win_storage.FileAccessMode.READ)
        decoder = await win_imaging.BitmapDecoder.create_async(stream)
        bitmap = await decoder.get_software_bitmap_async()
        engine = win_ocr.OcrEngine.try_create_from_user_profile_languages()
        res = await engine.recognize_async(bitmap)
        return res.text.strip()
    except Exception as e:
        return ""
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def save_image(image_bytes, ext="png"):
    img_hash = hashlib.md5(image_bytes).hexdigest()
    filename = f"img_{img_hash[:12]}.{ext}"
    rel_path = f"assets/q_images/{filename}"
    full_path = os.path.join(BASE_DIR, "assets", "q_images", filename)
    if not os.path.exists(full_path):
        with open(full_path, "wb") as f:
            f.write(image_bytes)
    return rel_path

print("Extractor module initialized.")
