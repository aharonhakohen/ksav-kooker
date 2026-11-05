# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Offline Hebrew OCR Engine
Wraps the Mishkefet-v1 CTC neural recognizer for Hebrew handwriting,
providing line segmentation, recognition, bounding boxes, and error recovery.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from PIL import Image, ImageEnhance, ImageOps

class OCREngine:
    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or self._resolve_model_dir()
        self.checkpoint_path = os.path.join(self.model_dir, "mishkefet-v1.pt")
        self._recognizer = None
        self._is_loaded = False

    def _resolve_model_dir(self) -> str:
        """Finds model assets in custom dir, frozen bundle, or local folder."""
        # 1. Custom model directory via environment variable (e.g. shared server path for network labs)
        env_model_dir = os.environ.get("KSAV_KOOKER_MODEL_DIR")
        if env_model_dir and os.path.exists(os.path.join(env_model_dir, "mishkefet-v1.pt")):
            return env_model_dir

        if getattr(sys, 'frozen', False):
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        candidates = [
            os.path.join(base_dir, "model_assets"),
            os.path.join(base_dir, "models"),
            base_dir,
            os.path.expanduser(r"~/.cache/huggingface/hub/models--itayinbar--Mishkefet-v1/snapshots/16380452d62839f369c36f17312c94d5d1af1768")
        ]
        for c in candidates:
            if os.path.exists(os.path.join(c, "mishkefet-v1.pt")):
                return c
        return candidates[0]

    def load_model(self):
        """Loads model into memory if not already loaded."""
        if self._is_loaded and self._recognizer is not None:
            return

        if not os.path.exists(self.checkpoint_path):
            raise FileNotFoundError(
                f"Mishkefet model checkpoint not found at: {self.checkpoint_path}.\n"
                f"Please run 'python scripts/download_model.py' to download the weights from GitHub Releases."
            )

        # Import locally from core.hebocr
        from core.hebocr.recognize import Recognizer
        self._recognizer = Recognizer(self.checkpoint_path, device="cpu")
        self._is_loaded = True

    def is_ready(self) -> bool:
        return self._is_loaded and self._recognizer is not None

    def preprocess_image(self, img: Image.Image, enhance_contrast: bool = True) -> Image.Image:
        """Cleans and standardizes image for optimal Hebrew handwriting recognition."""
        # Convert to RGB
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Automatically handle EXIF orientation
        img = ImageOps.exif_transpose(img)

        # Enhance contrast for faint pencil/ballpoint pen
        if enhance_contrast:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.4)
            sharpener = ImageEnhance.Sharpness(img)
            img = sharpener.enhance(1.2)

        return img

    def recognize_page(
        self,
        image_or_path: Any,
        learning_engine = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        Runs full-page segmentation and OCR recognition on an image.
        Returns:
            {
                'lines': [{'text': ..., 'raw_text': ..., 'box': ..., 'confidence': ...}],
                'full_text': str,
                'corrections_applied': int,
                'image_size': (width, height)
            }
        """
        self.load_model()

        if isinstance(image_or_path, (str, Path)):
            img = Image.open(str(image_or_path))
        else:
            img = image_or_path

        img = self.preprocess_image(img)
        w, h = img.size

        if progress_callback:
            progress_callback(10, 100, "Segmenting handwriting lines...")

        # Run Mishkefet read_page
        raw_results = self._recognizer.read_page(img)

        total_lines = len(raw_results)
        lines_data = []
        full_text_lines = []
        total_corrections = 0

        for idx, line_item in enumerate(raw_results):
            if progress_callback:
                pct = 20 + int((idx / max(1, total_lines)) * 75)
                progress_callback(pct, 100, f"Reading line {idx + 1} of {total_lines}...")

            raw_line_text = getattr(line_item, 'text', str(line_item)).strip()
            confidence = getattr(line_item, 'confidence', 1.0)
            box = getattr(line_item, 'box', None)
            skew = getattr(line_item, 'skew', 0.0)

            # Apply learning engine corrections if provided
            if learning_engine:
                clean_text, applied = learning_engine.apply_corrections(raw_line_text)
                total_corrections += len(applied)
            else:
                clean_text = raw_line_text
                applied = []

            lines_data.append({
                'index': idx,
                'text': clean_text,
                'raw_text': raw_line_text,
                'confidence': confidence,
                'box': box,
                'skew': skew,
                'applied': applied
            })
            if clean_text:
                full_text_lines.append(clean_text)

        if progress_callback:
            progress_callback(100, 100, "Done!")

        return {
            'lines': lines_data,
            'full_text': "\n".join(full_text_lines),
            'corrections_applied': total_corrections,
            'image_size': (w, h)
        }
