# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Build Standalone Windows Executable (.exe)
Uses PyInstaller to bundle Python, PyQt6, PyTorch CPU, and Mishkefet-v1 model assets.
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("=" * 60)
    print("Building IbberKuck v1.0.0 Standalone Executable")
    print("=" * 60)

    dist_dir = os.path.join(BASE_DIR, "dist")
    build_dir = os.path.join(BASE_DIR, "build")

    # Command arguments for PyInstaller
    # Using onedir for fast startup and reliable PyTorch torch_cpu.dll loading
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=IbberKuck",
        "--noconsole",
        "--onedir",
        "--clean",
        "--add-data", f"{os.path.join(BASE_DIR, 'version.json')};.",
        "--add-data", f"{os.path.join(BASE_DIR, 'model_assets')};model_assets",
        "--hidden-import", "PyQt6",
        "--hidden-import", "torch",
        "--hidden-import", "PIL",
        "--hidden-import", "docx",
        "--hidden-import", "core.hebocr.recognize",
        "--hidden-import", "core.hebocr.wordlm",
        "--hidden-import", "core.hebocr.lm",
        os.path.join(BASE_DIR, "main.py")
    ]

    print("Running PyInstaller...")
    subprocess.check_call(cmd, cwd=BASE_DIR)

    output_exe = os.path.join(dist_dir, "IbberKuck", "IbberKuck.exe")
    if os.path.exists(output_exe):
        print(f"\n[SUCCESS] Standalone app built successfully at:\n{output_exe}\n")
        
        # Also copy distribution to Google Drive for his son!
        target_drive = r"<deploy_dir>\IbberKuck"
        try:
            print(f"Copying build to Google Drive: {target_drive}...")
            if os.path.exists(target_drive):
                shutil.rmtree(target_drive)
            shutil.copytree(os.path.join(dist_dir, "IbberKuck"), target_drive)
            print("[SUCCESS] Also deployed directly to Google Drive Notes App folder!")
        except Exception as e:
            print(f"Notice: Could not copy directly to Google Drive: {e}")
    else:
        print("\n[ERROR] Build finished but IbberKuck.exe was not found.")

if __name__ == "__main__":
    build()
