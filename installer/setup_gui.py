# -*- coding: utf-8 -*-
"""
Ksav Kooker - Modern Windows Installation Wizard GUI
Features the 3D logo banner, high-contrast typography, folder selection,
shortcut creation, and automatic launch.
"""

import os
import sys
import json
import shutil
import subprocess
import time

from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox, QProgressBar, 
    QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont, QColor, QPalette

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(BASE_DIR)

def get_resource_path(rel_path: str) -> str:
    """
    Resolve absolute path to resource files.
    Works for:
      1. PyInstaller single-file mode (sys._MEIPASS)
      2. PyInstaller onedir mode (sys.executable dir)
      3. Development source tree (relative to TorahNotesOCR root)
      4. installer folder fallback
    """
    if hasattr(sys, '_MEIPASS'):
        candidate = os.path.join(sys._MEIPASS, rel_path)
        if os.path.exists(candidate):
            return candidate
        candidate_bare = os.path.join(sys._MEIPASS, os.path.basename(rel_path))
        if os.path.exists(candidate_bare):
            return candidate_bare

    if getattr(sys, 'frozen', False):
        candidate = os.path.join(os.path.dirname(sys.executable), rel_path)
        if os.path.exists(candidate):
            return candidate

    candidate = os.path.join(APP_ROOT, rel_path)
    if os.path.exists(candidate):
        return candidate

    candidate = os.path.join(BASE_DIR, rel_path)
    if os.path.exists(candidate):
        return candidate

    return rel_path

def get_app_version() -> str:
    vpath = get_resource_path("version.json")
    try:
        with open(vpath, "r", encoding="utf-8") as f:
            return json.load(f).get("version", "1.1.2")
    except Exception:
        return "1.1.2"


def get_windows_desktop_dirs() -> list:
    r"""
    Get all active desktop directory paths for the current user.
    Robust against Windows Server domain environments, Roaming Profiles,
    Folder Redirection (e.g. \\newltcserver\userdata$\<user>\Desktop), and OneDrive.
    """
    candidates = []
    
    # 1. Windows Shell API (CSIDL_DESKTOPDIRECTORY = 0x0010)
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(260)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 0x0010, None, 0, buf) == 0:
            val = buf.value.strip()
            if val and os.path.exists(val):
                candidates.append(val)
    except Exception:
        pass

    # 2. Windows Registry: User Shell Folders
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as k:
            val, _ = winreg.QueryValueEx(k, "Desktop")
            expanded = os.path.expandvars(val).strip()
            if expanded and os.path.exists(expanded):
                candidates.append(expanded)
    except Exception:
        pass

    # 3. OneDrive Desktop
    onedrive = os.environ.get("OneDrive", "").strip()
    if onedrive:
        od_desktop = os.path.join(onedrive, "Desktop")
        if os.path.exists(od_desktop):
            candidates.append(od_desktop)

    # 4. Standard local profile Desktop
    local_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if os.path.exists(local_desktop):
        candidates.append(local_desktop)

    # Deduplicate while preserving order (case-insensitive on Windows)
    seen = set()
    result = []
    for c in candidates:
        norm = os.path.normpath(c).lower()
        if norm not in seen:
            seen.add(norm)
            result.append(c)

    return result or [local_desktop]


def get_windows_start_menu_dirs() -> list:
    r"""
    Get all active Start Menu Programs directories.
    Handles Folder Redirection (\\server\userdata$\...\Start Menu\Programs),
    Roaming Profiles, and local AppData.
    """
    candidates = []
    
    # 1. Windows Shell API (CSIDL_PROGRAMS = 0x0002)
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(260)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 0x0002, None, 0, buf) == 0:
            val = buf.value.strip()
            if val and os.path.exists(val):
                candidates.append(val)
    except Exception:
        pass

    # 2. Windows Registry
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as k:
            val, _ = winreg.QueryValueEx(k, "Programs")
            expanded = os.path.expandvars(val).strip()
            if expanded and os.path.exists(expanded):
                candidates.append(expanded)
    except Exception:
        pass

    # 3. Local APPDATA Start Menu
    local_sm = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
    if os.path.exists(local_sm):
        candidates.append(local_sm)

    seen = set()
    result = []
    for c in candidates:
        norm = os.path.normpath(c).lower()
        if norm not in seen:
            seen.add(norm)
            result.append(c)

    return result or [local_sm]


def create_windows_shortcut(lnk_path: str, target_exe: str, icon_path: str, description: str) -> bool:
    """
    Create Windows .lnk shortcut using native Windows Script Host (cscript) first,
    falling back to PowerShell. Does not require ExecutionPolicy permissions and
    functions reliably on UNC domain shares and restricted workstation environments.
    """
    import tempfile
    
    target_dir = os.path.dirname(lnk_path)
    os.makedirs(target_dir, exist_ok=True)
    exe_dir = os.path.dirname(target_exe)

    # Method 1: Windows Script Host (VBScript via cscript) - Built-in, zero policy restriction
    try:
        vbs_script = f'''Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{lnk_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target_exe}"
oLink.WorkingDirectory = "{exe_dir}"
oLink.IconLocation = "{icon_path}"
oLink.Description = "{description}"
oLink.Save
'''
        fd, vbs_file = tempfile.mkstemp(suffix=".vbs")
        with open(fd, "w", encoding="utf-8") as f:
            f.write(vbs_script)
        
        res = subprocess.run(
            ["cscript", "//nologo", vbs_file],
            capture_output=True,
            text=True,
            creationflags=0x08000000
        )
        if os.path.exists(vbs_file):
            os.remove(vbs_file)
            
        if res.returncode == 0 and os.path.exists(lnk_path):
            return True
    except Exception:
        pass

    # Method 2: PowerShell fallback
    try:
        lnk_esc = lnk_path.replace("'", "''")
        target_esc = target_exe.replace("'", "''")
        dir_esc = exe_dir.replace("'", "''")
        ico_esc = icon_path.replace("'", "''")
        desc_esc = description.replace("'", "''")
        ps_cmd = f"""
        $ws = New-Object -ComObject WScript.Shell;
        $s = $ws.CreateShortcut('{lnk_esc}');
        $s.TargetPath = '{target_esc}';
        $s.WorkingDirectory = '{dir_esc}';
        $s.IconLocation = '{ico_esc}';
        $s.Description = '{desc_esc}';
        $s.Save();
        """
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            capture_output=True,
            creationflags=0x08000000
        )
        if res.returncode == 0 and os.path.exists(lnk_path):
            return True
    except Exception:
        pass

    return False

class InstallWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, source_dir: str, target_dir: str, create_desktop: bool, create_startmenu: bool, version: str):
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.create_desktop = create_desktop
        self.create_startmenu = create_startmenu
        self.version = version

    def run(self):
        try:
            import zipfile
            os.makedirs(self.target_dir, exist_ok=True)
            self.progress.emit(3, "Checking running processes...")

            # 1. Gracefully close any running KsavKooker.exe to prevent file-locking conflicts
            try:
                chk = subprocess.run(["tasklist", "/fi", "imagename eq KsavKooker.exe"], capture_output=True, text=True)
                if "KsavKooker.exe" in chk.stdout:
                    self.progress.emit(4, "Closing active Ksav Kooker instance for upgrade...")
                    subprocess.run(["taskkill", "/f", "/im", "KsavKooker.exe"], capture_output=True)
                    time.sleep(1)
            except Exception:
                pass

            # 2. When upgrading an existing installation, cleanly remove old application binaries
            # Note: User data (%APPDATA%\KsavKooker) is completely isolated and never touched!
            if os.path.exists(self.target_dir):
                self.progress.emit(6, "Refreshing application directory...")
                for item in ["_internal", "model_assets", "assets"]:
                    p = os.path.join(self.target_dir, item)
                    if os.path.exists(p):
                        shutil.rmtree(p, ignore_errors=True)
                old_exe = os.path.join(self.target_dir, "KsavKooker.exe")
                if os.path.exists(old_exe):
                    try:
                        os.remove(old_exe)
                    except Exception:
                        pass

            self.progress.emit(8, "Preparing destination folder...")

            # Check if an embedded payload.zip is present (single-file installer mode)
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            payload_candidates = [
                os.path.join(base_dir, "payload.zip"),
                os.path.join(os.path.dirname(sys.executable), "payload.zip") if getattr(sys, 'frozen', False) else "",
                os.path.join(APP_ROOT, "dist", "payload.zip"),
                get_resource_path("payload.zip")
            ]
            embedded_zip = next((p for p in payload_candidates if p and os.path.exists(p)), None)

            if embedded_zip:
                # Extract embedded offline zip payload
                with zipfile.ZipFile(embedded_zip, 'r') as zf:
                    infolist = zf.infolist()
                    total = len(infolist)
                    for idx, info in enumerate(infolist):
                        zf.extract(info, self.target_dir)
                        pct = 10 + int((idx / max(1, total)) * 75)
                        self.progress.emit(pct, f"Extracting: {os.path.basename(info.filename)}")
            else:
                # Fallback: copy files from directory
                all_files = []
                for root, dirs, files in os.walk(self.source_dir):
                    for f in files:
                        src_f = os.path.join(root, f)
                        rel_f = os.path.relpath(src_f, self.source_dir)
                        all_files.append((src_f, rel_f))

                total_files = len(all_files)
                for idx, (src_f, rel_f) in enumerate(all_files):
                    dst_f = os.path.join(self.target_dir, rel_f)
                    os.makedirs(os.path.dirname(dst_f), exist_ok=True)
                    shutil.copy2(src_f, dst_f)
                    
                    pct = 10 + int((idx / max(1, total_files)) * 75)
                    self.progress.emit(pct, f"Copying: {os.path.basename(rel_f)}")

            self.progress.emit(90, "Creating shortcuts...")
            exe_path = os.path.join(self.target_dir, "KsavKooker.exe")
            ico_path = os.path.join(self.target_dir, "assets", "ksav_kooker.ico")
            if not os.path.exists(ico_path):
                ico_path = exe_path

            # Create shortcuts across all active desktop and start menu directories
            # (including redirected network shares and local profiles)
            if self.create_desktop:
                for d_dir in get_windows_desktop_dirs():
                    lnk = os.path.join(d_dir, "Ksav Kooker.lnk")
                    create_windows_shortcut(
                        lnk,
                        exe_path,
                        ico_path,
                        "Ksav Kooker - Offline Torah Notes OCR Studio"
                    )

            if self.create_startmenu:
                for sm_dir in get_windows_start_menu_dirs():
                    app_sm = os.path.join(sm_dir, "Ksav Kooker")
                    os.makedirs(app_sm, exist_ok=True)
                    lnk = os.path.join(app_sm, "Ksav Kooker.lnk")
                    create_windows_shortcut(
                        lnk,
                        exe_path,
                        ico_path,
                        "Ksav Kooker - Offline Torah Notes OCR Studio"
                    )

            # Register in Windows Add/Remove Programs (HKCU Uninstall)
            self._register_uninstall(self.target_dir, exe_path, ico_path)

            self.progress.emit(100, "Installation completed successfully!")
            self.finished.emit(True, exe_path)
        except Exception as e:
            self.finished.emit(False, str(e))

    def _create_shortcut(self, lnk_path: str, target_exe: str, icon_path: str, description: str):
        """Creates Windows shortcut (.lnk) with hardened parameters and string escaping."""
        lnk_esc = lnk_path.replace("'", "''")
        target_esc = target_exe.replace("'", "''")
        dir_esc = os.path.dirname(target_exe).replace("'", "''")
        ico_esc = icon_path.replace("'", "''")
        desc_esc = description.replace("'", "''")
        ps_cmd = f"""
        $ws = New-Object -ComObject WScript.Shell;
        $s = $ws.CreateShortcut('{lnk_esc}');
        $s.TargetPath = '{target_esc}';
        $s.WorkingDirectory = '{dir_esc}';
        $s.IconLocation = '{ico_esc}';
        $s.Description = '{desc_esc}';
        $s.Save();
        """
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            capture_output=True,
            creationflags=0x08000000
        )

    def _register_uninstall(self, target_dir: str, exe_path: str, ico_path: str):
        """Registers the application in Windows Settings / Control Panel Installed Apps."""
        import winreg
        try:
            uninstaller_bat = os.path.join(target_dir, "uninstall.bat")
            desktop_lnk = os.path.join(os.path.expanduser("~"), "Desktop", "Ksav Kooker.lnk")
            start_menu_dir = os.path.join(
                os.environ.get("APPDATA", ""), 
                r"Microsoft\Windows\Start Menu\Programs\Ksav Kooker"
            )
            
            # Generate clean uninstaller batch script
            bat_content = f"""@echo off
title Uninstalling Ksav Kooker...
echo ===================================================
echo Uninstalling Ksav Kooker (כתב קוקער)...
echo ===================================================

echo [1/3] Removing desktop and start menu shortcuts...
if exist "{desktop_lnk}" del /f /q "{desktop_lnk}"
if exist "{start_menu_dir}" rmdir /s /q "{start_menu_dir}"

echo [2/3] Removing Windows registry entry...
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\KsavKooker" /f >nul 2>&1

echo [3/3] Removing application files...
cd /d "%TEMP%"
start /b "" cmd /c timeout /t 2 /nobreak ^>nul ^& rmdir /s /q "{target_dir}"

echo.
echo Ksav Kooker has been removed from your computer.
echo.
timeout /t 3
"""
            with open(uninstaller_bat, "w", encoding="utf-8") as f:
                f.write(bat_content)

            # Write Windows Registry entry under HKCU
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Uninstall\KsavKooker"
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Ksav Kooker (כתב קוקער)")
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, self.version)
                winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Torah u'Mesorah Lakewood Teachers Center")
                winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, ico_path)
                winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, target_dir)
                winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'"{uninstaller_bat}"')
                winreg.SetValueEx(key, "QuietUninstallString", 0, winreg.REG_SZ, f'cmd /c "{uninstaller_bat}"')
                winreg.SetValueEx(key, "EstimatedSize", 0, winreg.REG_DWORD, 1180000)
                winreg.SetValueEx(key, "URLInfoAbout", 0, winreg.REG_SZ, "https://github.com/aharonhakohen/ksav-kooker")
                winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
        except Exception as err:
            print(f"Notice: Windows uninstall registration: {err}")

class ModernSetupWizard(QWizard):
    def __init__(self, source_app_dir: str):
        super().__init__()
        self.source_app_dir = source_app_dir
        self.installed_exe_path = ""
        self.version = get_app_version()
        self.setWindowTitle(f"Ksav Kooker Setup — Installation Wizard (v{self.version})")
        self.resize(720, 520)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.setButtonText(QWizard.WizardButton.BackButton, "< Back")
        self.setButtonText(QWizard.WizardButton.NextButton, "Next >")
        self.setButtonText(QWizard.WizardButton.FinishButton, "Finish")
        self.setButtonText(QWizard.WizardButton.CancelButton, "Cancel")

        # Set Window Icon
        icon_path = get_resource_path(os.path.join("assets", "ksav_kooker.ico"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Explicit Palette for native Windows elements
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        pal.setColor(QPalette.ColorRole.WindowText, QColor("#0f172a"))
        pal.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        pal.setColor(QPalette.ColorRole.Text, QColor("#0f172a"))
        pal.setColor(QPalette.ColorRole.Button, QColor("#f8fafc"))
        pal.setColor(QPalette.ColorRole.ButtonText, QColor("#0f172a"))
        self.setPalette(pal)

        # High-Contrast Modern Windows Wizard Styling
        self.setStyleSheet("""
            QWizard {
                background-color: #f8fafc;
                color: #0f172a;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'David', sans-serif;
            }
            QWizardPage {
                background-color: #ffffff;
                color: #0f172a;
            }
            QLabel {
                color: #1e293b;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 7px 12px;
                color: #0f172a;
                font-size: 13px;
                selection-background-color: #2563eb;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 1.5px solid #2563eb;
            }
            QPushButton {
                background-color: #ffffff;
                color: #1e293b;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 500;
                font-size: 13px;
                min-width: 65px;
            }
            QPushButton:hover {
                background-color: #f1f5f9;
                border-color: #94a3b8;
            }
            QPushButton:pressed {
                background-color: #e2e8f0;
            }
            QCheckBox {
                color: #1e293b;
                font-size: 13px;
                spacing: 10px;
            }
            QProgressBar {
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                background-color: #f1f5f9;
                color: #0f172a;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                height: 22px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 5px;
            }
        """)

        # Add Pages
        self.setPage(0, self._create_welcome_page())
        self.setPage(1, self._create_destination_page())
        self.setPage(2, self._create_options_page())
        self.setPage(3, self._create_installing_page())
        self.setPage(4, self._create_finished_page())
        self._style_buttons()

    def _style_buttons(self):
        b_next = self.button(QWizard.WizardButton.NextButton)
        if b_next:
            b_next.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    color: #ffffff;
                    font-weight: 600;
                    border: 1px solid #1d4ed8;
                    border-radius: 6px;
                    padding: 6px 18px;
                    min-width: 65px;
                }
                QPushButton:hover {
                    background-color: #1d4ed8;
                }
                QPushButton:pressed {
                    background-color: #1e40af;
                }
                QPushButton:disabled {
                    background-color: #94a3b8;
                    border-color: #94a3b8;
                    color: #e2e8f0;
                }
            """)
        b_finish = self.button(QWizard.WizardButton.FinishButton)
        if b_finish:
            b_finish.setStyleSheet("""
                QPushButton {
                    background-color: #16a34a;
                    color: #ffffff;
                    font-weight: 600;
                    border: 1px solid #15803d;
                    border-radius: 6px;
                    padding: 6px 18px;
                    min-width: 65px;
                }
                QPushButton:hover {
                    background-color: #15803d;
                }
                QPushButton:pressed {
                    background-color: #166534;
                }
                QPushButton:disabled {
                    background-color: #94a3b8;
                    border-color: #94a3b8;
                    color: #e2e8f0;
                }
            """)

    def _create_welcome_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("")
        page.setSubTitle("")
        layout = QHBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Left 3D Banner
        logo_path = get_resource_path(os.path.join("assets", "ksav_kooker.png"))
        if os.path.exists(logo_path):
            lbl_banner = QLabel()
            pix = QPixmap(logo_path).scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_banner.setPixmap(pix)
            lbl_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_banner.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(lbl_banner)

        # Right Text
        right_box = QVBoxLayout()
        right_box.setSpacing(10)

        lbl_hdr = QLabel("Welcome to Ksav Kooker Setup")
        lbl_hdr.setStyleSheet("font-size: 20px; font-weight: bold; color: #0f172a;")
        right_box.addWidget(lbl_hdr)

        lbl_ver = QLabel(f"Version {self.version} (100% Offline Edition)")
        lbl_ver.setStyleSheet("font-size: 12px; font-weight: 600; color: #047857;")
        right_box.addWidget(lbl_ver)

        lbl_desc = QLabel(
            "This wizard will install <b>Ksav Kooker (כתב קוקער)</b> on your computer.<br><br>"
            "Ksav Kooker operates <b>100% offline with zero internet connection required</b>, providing:<br>"
            "• Offline neural OCR recognition for handwritten Hebrew cursive and print<br>"
            "• Side-by-side editing and proofreading directly alongside notebook photos<br>"
            "• Multi-user handwriting profiles and multi-profile rule stacking<br>"
            "• Self-learning mistake memory engine with one-click backup and restore<br>"
            "• Formatted Right-to-Left Microsoft Word (.docx) export.<br><br>"
            "Click <b>Next</b> to continue, or Cancel to exit Setup."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("line-height: 1.5; color: #334155; font-size: 13px;")
        right_box.addWidget(lbl_desc)

        right_box.addStretch()
        layout.addLayout(right_box)
        return page

    def _create_destination_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Destination Location")
        page.setSubTitle("Select the destination folder where Setup will install Ksav Kooker:")

        layout = QVBoxLayout(page)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 20, 24, 20)

        # Default path in LocalAppData
        default_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "Ksav Kooker")

        lbl_prompt = QLabel("Destination Folder:")
        lbl_prompt.setStyleSheet("font-weight: 600; color: #0f172a; font-size: 13px;")
        layout.addWidget(lbl_prompt)

        dir_box = QHBoxLayout()
        dir_box.setSpacing(10)
        self.txt_dest = QLineEdit(default_dir)
        dir_box.addWidget(self.txt_dest)

        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse_destination)
        dir_box.addWidget(btn_browse)
        layout.addLayout(dir_box)

        lbl_space = QLabel("Required free space: ~450 MB  |  Standalone installation with zero external dependencies.")
        lbl_space.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(lbl_space)

        existing_exe = os.path.join(default_dir, "KsavKooker.exe")
        if os.path.exists(existing_exe):
            lbl_upgrade = QLabel(
                "<b>Upgrade Mode Detected:</b> Setup will refresh all application binaries while fully preserving your personal handwriting profiles, mistake memory bank, and custom settings in %APPDATA%."
            )
            lbl_upgrade.setWordWrap(True)
            lbl_upgrade.setStyleSheet("""
                background-color: #ecfdf5;
                color: #065f46;
                border: 1px solid #a7f3d0;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
            """)
            layout.addWidget(lbl_upgrade)

        layout.addStretch()
        return page

    def _browse_destination(self):
        chosen = QFileDialog.getExistingDirectory(self, "Select Installation Folder", self.txt_dest.text())
        if chosen:
            self.txt_dest.setText(os.path.join(chosen, "Ksav Kooker"))

    def _create_options_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("Select Additional Tasks")
        page.setSubTitle("Select which shortcuts you want Setup to create:")

        layout = QVBoxLayout(page)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 20, 24, 20)

        self.chk_desktop = QCheckBox("Create Desktop Shortcut")
        self.chk_desktop.setChecked(True)
        layout.addWidget(self.chk_desktop)

        self.chk_startmenu = QCheckBox("Create Start Menu Shortcut")
        self.chk_startmenu.setChecked(True)
        layout.addWidget(self.chk_startmenu)

        self.chk_launch = QCheckBox("Launch Ksav Kooker when Setup exits")
        self.chk_launch.setChecked(True)
        layout.addWidget(self.chk_launch)

        layout.addStretch()
        return page

    def _create_installing_page(self) -> QWizardPage:
        self.page_installing = QWizardPage()
        self.page_installing.setTitle("Installing Ksav Kooker...")
        self.page_installing.setSubTitle("Please wait while Setup installs Ksav Kooker on your computer:")

        layout = QVBoxLayout(self.page_installing)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 30, 24, 20)

        self.lbl_install_status = QLabel("Preparing installation...")
        self.lbl_install_status.setStyleSheet("font-weight: 600; color: #1e293b; font-size: 13px;")
        layout.addWidget(self.lbl_install_status)

        self.install_progress = QProgressBar()
        self.install_progress.setRange(0, 100)
        self.install_progress.setValue(0)
        layout.addWidget(self.install_progress)

        layout.addStretch()
        return self.page_installing

    def _create_finished_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("")
        page.setSubTitle("")

        layout = QHBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 3D Logo on finish
        logo_path = get_resource_path(os.path.join("assets", "ksav_kooker.png"))
        if os.path.exists(logo_path):
            lbl_banner = QLabel()
            pix = QPixmap(logo_path).scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_banner.setPixmap(pix)
            lbl_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_banner.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(lbl_banner)

        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        lbl_hdr = QLabel("Installation Complete! ✓")
        lbl_hdr.setStyleSheet("font-size: 20px; font-weight: bold; color: #047857;")
        right_box.addWidget(lbl_hdr)

        lbl_msg = QLabel(
            "<b>Ksav Kooker (כתב קוקער)</b> has been successfully installed on your computer.<br><br>"
            "Desktop and Start Menu shortcuts have been created.<br>"
            "The software is ready for 100% offline use with zero internet connection.<br><br>"
            "Click <b>Finish</b> to exit Setup."
        )
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet("color: #334155; font-size: 13px; line-height: 1.5;")
        right_box.addWidget(lbl_msg)

        # Launch checkbox directly on the Finish page
        self.chk_finish_launch = QCheckBox("Launch Ksav Kooker now")
        self.chk_finish_launch.setChecked(True)
        self.chk_finish_launch.setStyleSheet("font-weight: 600; color: #0f172a; font-size: 13px; margin-top: 10px;")
        right_box.addWidget(self.chk_finish_launch)

        right_box.addStretch()
        layout.addLayout(right_box)
        return page

    def initializePage(self, page_id: int):
        super().initializePage(page_id)
        self._style_buttons()
        if page_id == 3:  # Installing page
            back_btn = self.button(QWizard.WizardButton.BackButton)
            if back_btn:
                back_btn.setEnabled(False)
            next_btn = self.button(QWizard.WizardButton.NextButton)
            if next_btn:
                next_btn.setEnabled(False)
            cancel_btn = self.button(QWizard.WizardButton.CancelButton)
            if cancel_btn:
                cancel_btn.setEnabled(False)
            self._start_installation()

    def _start_installation(self):
        target_dir = self.txt_dest.text().strip()
        self.worker = InstallWorker(
            self.source_app_dir,
            target_dir,
            self.chk_desktop.isChecked(),
            self.chk_startmenu.isChecked(),
            self.version
        )
        self.worker.progress.connect(self._on_install_progress)
        self.worker.finished.connect(self._on_install_finished)
        self.worker.start()

    def _on_install_progress(self, val: int, msg: str):
        self.install_progress.setValue(val)
        self.lbl_install_status.setText(msg)

    def _on_install_finished(self, success: bool, res: str):
        if success:
            self.installed_exe_path = res
            self.next()
            finish_btn = self.button(QWizard.WizardButton.FinishButton)
            if finish_btn:
                finish_btn.setEnabled(True)
        else:
            QMessageBox.critical(self, "Installation Error", f"An error occurred during installation:\n{res}")
            cancel_btn = self.button(QWizard.WizardButton.CancelButton)
            if cancel_btn:
                cancel_btn.setEnabled(True)

    def accept(self):
        # If launch checked on finish page (or options page), launch detached process with proper cwd
        should_launch = True
        if hasattr(self, "chk_finish_launch"):
            should_launch = self.chk_finish_launch.isChecked()
        elif hasattr(self, "chk_launch"):
            should_launch = self.chk_launch.isChecked()

        if should_launch and self.installed_exe_path and os.path.exists(self.installed_exe_path):
            try:
                exe_dir = os.path.dirname(self.installed_exe_path)
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                subprocess.Popen(
                    [self.installed_exe_path],
                    cwd=exe_dir,
                    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
                    close_fds=True
                )
            except Exception as err:
                try:
                    os.startfile(self.installed_exe_path)
                except Exception:
                    pass
        super().accept()

def main():
    app = QApplication(sys.argv)
    
    # Locate compiled app folder
    # Priority: dist/KsavKooker, or dist/IbberKuck, or bundled
    dist_dir = os.path.join(APP_ROOT, "dist", "KsavKooker")
    if not os.path.exists(dist_dir):
        dist_dir = os.path.join(APP_ROOT, "dist", "IbberKuck")

    wizard = ModernSetupWizard(dist_dir)
    wizard.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
