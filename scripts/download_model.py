# -*- coding: utf-8 -*-
"""
Helper script to download Ohr HaKsav neural OCR model weights (mishkefet-v1.pt)
from GitHub Releases if cloning without Git LFS.
"""

import os
import sys
import urllib.request

MODEL_URL = "https://github.com/aharonhakohen/TorahNotesOCR/releases/download/v1.0.0/mishkefet-v1.pt"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_PATH = os.path.join(BASE_DIR, "model_assets", "mishkefet-v1.pt")

def reporthook(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write(f"\rDownloading Mishkefet-v1 model: {percent}% ({count * block_size / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB)")
    sys.stdout.flush()

def ensure_model():
    if os.path.exists(TARGET_PATH) and os.path.getsize(TARGET_PATH) > 100 * 1024 * 1024:
        print(f"Mishkefet-v1 weights already present ({os.path.getsize(TARGET_PATH)/(1024*1024):.1f} MB) at {TARGET_PATH}")
        return True

    print(f"Downloading Mishkefet-v1 neural OCR weights from GitHub Releases...")
    print(f"Target: {TARGET_PATH}")
    os.makedirs(os.path.dirname(TARGET_PATH), exist_ok=True)
    try:
        urllib.request.urlretrieve(MODEL_URL, TARGET_PATH, reporthook)
        print("\nDownload completed successfully!")
        return True
    except Exception as e:
        print(f"\nFailed to download weights automatically: {e}")
        print(f"Please manually download mishkefet-v1.pt from {MODEL_URL} and place it in {os.path.dirname(TARGET_PATH)}")
        return False

if __name__ == "__main__":
    ensure_model()
