# -*- coding: utf-8 -*-
"""
Ksav Kooker - Automated Build Script for Standalone Executable & Offline Setup Wizard
Bundles Python, PyQt6, PyTorch CPU, Mishkefet-v1 model assets, 3D icons, and offline zip payload.
Optimized to exclude unused build dependencies (transformers, scipy, matplotlib, pandas, etc.)
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_version() -> str:
    vpath = os.path.join(BASE_DIR, "version.json")
    try:
        with open(vpath, "r", encoding="utf-8") as f:
            return json.load(f).get("version", "1.1.0")
    except Exception:
        return "1.1.0"

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

def build(force_rebuild: bool = False):
    version = get_version()
    print("=" * 70)
    print(f"Building Ksav Kooker v{version} Standalone Offline Package")
    print("=" * 70)

    dist_dir = os.path.join(BASE_DIR, "dist")
    assets_dir = os.path.join(BASE_DIR, "assets")
    ico_path = os.path.join(assets_dir, "ksav_kooker.ico")
    app_output = os.path.join(dist_dir, "KsavKooker")
    app_exe = os.path.join(app_output, "KsavKooker.exe")
    payload_zip = os.path.join(dist_dir, "payload.zip")
    setup_exe = os.path.join(dist_dir, "KsavKooker_Setup.exe")

    # Determine if rebuild of KsavKooker.exe is needed
    core_files = [
        os.path.join(BASE_DIR, "version.json"),
        os.path.join(BASE_DIR, "main.py"),
        os.path.join(BASE_DIR, "ui", "main_window.py"),
        os.path.join(BASE_DIR, "ui", "dictionary_dialog.py"),
        os.path.join(BASE_DIR, "core", "learning_engine.py"),
        ico_path
    ]
    needs_app_rebuild = force_rebuild or not os.path.exists(app_exe)
    if not needs_app_rebuild and os.path.exists(app_exe):
        exe_mtime = os.path.getmtime(app_exe)
        for cf in core_files:
            if os.path.exists(cf) and os.path.getmtime(cf) > exe_mtime:
                needs_app_rebuild = True
                break

    if needs_app_rebuild:
        print(f"\n[1/3] Compiling KsavKooker.exe (v{version}) directory with optimizations...")
        if os.path.exists(app_output):
            shutil.rmtree(app_output, ignore_errors=True)
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
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
            # Optimization: Exclude unused heavy build dependencies to slim down package
            "--exclude-module", "transformers",
            "--exclude-module", "scipy",
            "--exclude-module", "matplotlib",
            "--exclude-module", "pandas",
            "--exclude-module", "onnxruntime",
            "--exclude-module", "av",
            "--exclude-module", "jedi",
            "--exclude-module", "IPython",
            "--exclude-module", "notebook",
            os.path.join(BASE_DIR, "main.py")
        ]
        subprocess.check_call(cmd, cwd=BASE_DIR)
    else:
        print(f"\n[1/3] Existing KsavKooker application up-to-date at: {app_output}")

    # 2. Package offline payload.zip
    if not os.path.exists(payload_zip) or os.path.getmtime(payload_zip) < os.path.getmtime(app_exe):
        create_payload_zip(app_output, payload_zip)
    else:
        print(f"\n[2/3] Existing payload.zip up-to-date ({os.path.getsize(payload_zip)/(1024*1024):.1f} MB)")

    # 3. Build Standalone Offline Setup Wizard (KsavKooker_Setup.exe) embedding payload.zip
    print("\n[3/3] Compiling KsavKooker_Setup.exe Self-Extracting Installer Wizard...")
    installer_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
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

    # 4. Deploy to custom staging directory (configured via local_deploy.txt or KSAV_KOOKER_DEPLOY_DIR)
    target_drive = os.environ.get("KSAV_KOOKER_DEPLOY_DIR")
    if not target_drive:
        deploy_cfg = os.path.join(BASE_DIR, "local_deploy.txt")
        if os.path.exists(deploy_cfg):
            try:
                with open(deploy_cfg, "r", encoding="utf-8") as f:
                    candidate = f.read().strip()
                    if candidate and os.path.exists(candidate):
                        target_drive = candidate
            except Exception:
                pass

    if target_drive and os.path.exists(target_drive):
        try:
            print(f"\nDeploying artifacts to destination: {target_drive}...")
            
            # 1. Setup wizard
            shutil.copy2(setup_exe, os.path.join(target_drive, "KsavKooker_Setup.exe"))
            print(f" -> Deployed KsavKooker_Setup.exe")

            # 2. Portable zip
            portable_zip = os.path.join(target_drive, f"KsavKooker-v{version}-Windows.zip")
            shutil.copy2(payload_zip, portable_zip)
            print(f" -> Deployed portable zip to {portable_zip}")

            # 3. Unpacked directory
            drive_app_dir = os.path.join(target_drive, "Ksav Kooker")
            if os.path.exists(drive_app_dir):
                shutil.rmtree(drive_app_dir, ignore_errors=True)
            shutil.copytree(app_output, drive_app_dir)
            print(f" -> Deployed unpacked app directory to {drive_app_dir}")

            print("\n[ALL DELIVERABLES READY AND DEPLOYED]")
        except Exception as e:
            print(f"Notice: Deployment error: {e}")

if __name__ == "__main__":
    force = "--force" in sys.argv
    build(force_rebuild=force)
