# -*- coding: utf-8 -*-
"""
Ksav Kooker - Build Standalone Windows Executable (.exe) and Installer
Uses PyInstaller to bundle Python, PyQt6, PyTorch CPU, Mishkefet-v1 model assets, and 3D icons.
"""

import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("=" * 60)
    print("Building Ksav Kooker v1.0.0 Standalone Executable & Installer")
    print("=" * 60)

    dist_dir = os.path.join(BASE_DIR, "dist")
    assets_dir = os.path.join(BASE_DIR, "assets")
    ico_path = os.path.join(assets_dir, "ksav_kooker.ico")

    # 1. Build Main Application (KsavKooker.exe)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=KsavKooker",
        "--noconsole",
        "--onedir",
        "--clean",
        f"--icon={ico_path}",
        "--add-data", f"{os.path.join(BASE_DIR, 'version.json')};.",
        "--add-data", f"{os.path.join(BASE_DIR, 'model_assets')};model_assets",
        "--add-data", f"{assets_dir};assets",
        "--hidden-import", "PyQt6",
        "--hidden-import", "torch",
        "--hidden-import", "PIL",
        "--hidden-import", "docx",
        "--hidden-import", "core.hebocr.recognize",
        "--hidden-import", "core.hebocr.wordlm",
        "--hidden-import", "core.hebocr.lm",
        os.path.join(BASE_DIR, "main.py")
    ]

    print("\n[1/2] Compiling KsavKooker.exe with PyInstaller...")
    subprocess.check_call(cmd, cwd=BASE_DIR)

    # 2. Build Modern Setup Installer (KsavKooker_Setup.exe)
    print("\n[2/2] Compiling KsavKooker_Setup.exe Installer Wizard...")
    installer_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=KsavKooker_Setup",
        "--noconsole",
        "--onefile",
        "--clean",
        f"--icon={ico_path}",
        "--add-data", f"{assets_dir};assets",
        os.path.join(BASE_DIR, "installer", "setup_gui.py")
    ]
    subprocess.check_call(installer_cmd, cwd=BASE_DIR)

    output_app = os.path.join(dist_dir, "KsavKooker")
    output_exe = os.path.join(output_app, "KsavKooker.exe")
    output_setup = os.path.join(dist_dir, "KsavKooker_Setup.exe")

    if os.path.exists(output_exe):
        print(f"\n[SUCCESS] Standalone app built successfully at:\n{output_exe}\n")
        if os.path.exists(output_setup):
            print(f"[SUCCESS] Setup Wizard installer built at:\n{output_setup}\n")

        # Copy to Google Drive for his son!
        target_drive = r"<deploy_dir>\Ksav Kooker"
        try:
            print(f"Deploying to Google Drive: {target_drive}...")
            if os.path.exists(target_drive):
                shutil.rmtree(target_drive)
            shutil.copytree(output_app, target_drive)

            # Copy setup installer right into the folder
            if os.path.exists(output_setup):
                shutil.copy2(output_setup, os.path.join(os.path.dirname(target_drive), "KsavKooker_Setup.exe"))

            # Also create zip archive
            zip_dest = os.path.join(os.path.dirname(target_drive), "KsavKooker-v1.0.0-Windows")
            print("Creating portable zip archive...")
            shutil.make_archive(zip_dest, "zip", output_app)
            print(f"[SUCCESS] Zip package created at {zip_dest}.zip")

        except Exception as e:
            print(f"Notice: Google Drive deployment: {e}")
    else:
        print("\n[ERROR] Build finished but KsavKooker.exe was not found.")

if __name__ == "__main__":
    build()
