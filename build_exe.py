# -*- coding: utf-8 -*-
"""
Ksav Kooker - Automated Build Script for Standalone Executable & Offline Setup Wizard
Bundles Python, PyQt6, PyTorch CPU, Mishkefet-v1 model assets, 3D icons, and offline zip payload.
"""

import os
import sys
import shutil
import zipfile
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_payload_zip(src_dir: str, out_zip: str):
    print(f"\nCompressing offline application payload to {out_zip}...")
    t0 = time.time()
    with zipfile.ZipFile(out_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for root, dirs, files in os.walk(src_dir):
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, src_dir)
                zf.write(full_path, rel_path)
    mb = os.path.getsize(out_zip) / (1024 * 1024)
    print(f"[SUCCESS] Payload created: {mb:.1f} MB in {time.time()-t0:.1f}s")

def build():
    print("=" * 70)
    print("Building Ksav Kooker v1.0.0 Standalone Offline Package")
    print("=" * 70)

    dist_dir = os.path.join(BASE_DIR, "dist")
    assets_dir = os.path.join(BASE_DIR, "assets")
    ico_path = os.path.join(assets_dir, "ksav_kooker.ico")
    app_output = os.path.join(dist_dir, "KsavKooker")
    app_exe = os.path.join(app_output, "KsavKooker.exe")
    payload_zip = os.path.join(dist_dir, "payload.zip")
    setup_exe = os.path.join(dist_dir, "KsavKooker_Setup.exe")

    # 1. Build Main Application (KsavKooker.exe onedir) if not already built
    if not os.path.exists(app_exe):
        print("\n[1/3] Compiling KsavKooker.exe directory with PyInstaller...")
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
        subprocess.check_call(cmd, cwd=BASE_DIR)
    else:
        print(f"\n[1/3] Existing KsavKooker application found at: {app_output}")

    # 2. Package offline payload.zip
    if not os.path.exists(payload_zip) or os.path.getmtime(payload_zip) < os.path.getmtime(app_exe):
        create_payload_zip(app_output, payload_zip)
    else:
        print(f"\n[2/3] Existing payload.zip found ({os.path.getsize(payload_zip)/(1024*1024):.1f} MB)")

    # 3. Build Standalone Offline Setup Wizard (KsavKooker_Setup.exe) embedding payload.zip
    print("\n[3/3] Compiling KsavKooker_Setup.exe Self-Extracting Installer Wizard...")
    installer_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=KsavKooker_Setup",
        "--noconsole",
        "--onefile",
        "--clean",
        f"--icon={ico_path}",
        "--add-data", f"{assets_dir};assets",
        "--add-data", f"{payload_zip};.",
        os.path.join(BASE_DIR, "installer", "setup_gui.py")
    ]
    subprocess.check_call(installer_cmd, cwd=BASE_DIR)

    # 4. Deploy to Google Drive
    target_drive = r"<deploy_dir>"
    if os.path.exists(target_drive):
        try:
            print(f"\nDeploying artifacts to Google Drive: {target_drive}...")
            
            # 1. Setup wizard
            shutil.copy2(setup_exe, os.path.join(target_drive, "KsavKooker_Setup.exe"))
            print(f" -> Deployed KsavKooker_Setup.exe")

            # 2. Portable zip
            portable_zip = os.path.join(target_drive, "KsavKooker-v1.0.0-Windows.zip")
            shutil.copy2(payload_zip, portable_zip)
            print(f" -> Deployed portable zip to {portable_zip}")

            # 3. Unpacked directory
            drive_app_dir = os.path.join(target_drive, "Ksav Kooker")
            if os.path.exists(drive_app_dir):
                shutil.rmtree(drive_app_dir)
            shutil.copytree(app_output, drive_app_dir)
            print(f" -> Deployed unpacked app directory to {drive_app_dir}")

            print("\n[ALL DELIVERABLES READY AND DEPLOYED TO GOOGLE DRIVE]")
        except Exception as e:
            print(f"Notice: Google Drive deployment error: {e}")

if __name__ == "__main__":
    build()
