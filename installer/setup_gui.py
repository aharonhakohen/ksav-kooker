# -*- coding: utf-8 -*-
"""
Ksav Kooker - Modern Windows Installation Wizard GUI
Features the 3D logo banner, folder selection, shortcut creation, and automatic launch.
"""

import os
import sys
import shutil
import subprocess
import time

from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox, QProgressBar, 
    QFileDialog, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QFont, QColor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(BASE_DIR)

class InstallWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, source_dir: str, target_dir: str, create_desktop: bool, create_startmenu: bool):
        super().__init__()
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.create_desktop = create_desktop
        self.create_startmenu = create_startmenu

    def run(self):
        try:
            import zipfile
            os.makedirs(self.target_dir, exist_ok=True)
            self.progress.emit(5, "מכין תיקיית יעד...")

            # Check if an embedded payload.zip is present (single-file installer mode)
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            payload_candidates = [
                os.path.join(base_dir, "payload.zip"),
                os.path.join(os.path.dirname(sys.executable), "payload.zip") if getattr(sys, 'frozen', False) else "",
                os.path.join(APP_ROOT, "dist", "payload.zip")
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
                        self.progress.emit(pct, f"מחלץ רכיב: {os.path.basename(info.filename)}")
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
                    self.progress.emit(pct, f"מעתיק קובץ: {os.path.basename(rel_f)}")

            self.progress.emit(90, "יוצר קיצורי דרך במחשב...")
            exe_path = os.path.join(self.target_dir, "KsavKooker.exe")
            ico_path = os.path.join(self.target_dir, "assets", "ksav_kooker.ico")
            if not os.path.exists(ico_path):
                ico_path = exe_path

            # Create shortcuts via PowerShell
            if self.create_desktop:
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                self._create_shortcut(
                    os.path.join(desktop, "Ksav Kooker.lnk"),
                    exe_path,
                    ico_path,
                    "Ksav Kooker - Offline Torah Notes OCR Studio"
                )

            if self.create_startmenu:
                start_menu = os.path.join(
                    os.environ.get("APPDATA", ""), 
                    r"Microsoft\Windows\Start Menu\Programs\Ksav Kooker"
                )
                os.makedirs(start_menu, exist_ok=True)
                self._create_shortcut(
                    os.path.join(start_menu, "Ksav Kooker.lnk"),
                    exe_path,
                    ico_path,
                    "Ksav Kooker - Offline Torah Notes OCR Studio"
                )

            # Register in Windows Add/Remove Programs (HKCU Uninstall)
            self._register_uninstall(self.target_dir, exe_path, ico_path)

            self.progress.emit(100, "ההתקנה הושלמה בהצלחה!")
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
                winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.1")
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
        self.setWindowTitle("Ksav Kooker Setup — התקנת כתב קוקער (v1.0.1)")
        self.resize(720, 520)
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)

        # Set Icon
        icon_path = os.path.join(APP_ROOT, "assets", "ksav_kooker.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Modern Styling
        self.setStyleSheet("""
            QWizard {
                background-color: #181825;
                color: #cdd6f4;
                font-family: 'Segoe UI', 'David', sans-serif;
            }
            QLabel {
                color: #cdd6f4;
                font-size: 13px;
            }
            QLineEdit {
                background-color: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px 10px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 6px;
                padding: 6px 16px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2563eb;
                color: #ffffff;
                border-color: #3b82f6;
            }
            QCheckBox {
                color: #cdd6f4;
                font-size: 13px;
                spacing: 8px;
            }
            QProgressBar {
                border: 1px solid #45475a;
                border-radius: 6px;
                background-color: #1e1e2e;
                color: #ffffff;
                text-align: center;
                height: 18px;
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

    def _create_welcome_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("")
        page.setSubTitle("")
        layout = QHBoxLayout(page)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(16)

        # Left 3D Banner
        logo_path = os.path.join(APP_ROOT, "assets", "ksav_kooker.png")
        if os.path.exists(logo_path):
            lbl_banner = QLabel()
            pix = QPixmap(logo_path).scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_banner.setPixmap(pix)
            lbl_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_banner.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(lbl_banner)

        # Right Text
        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        lbl_hdr = QLabel("ברוכים הבאים להתקנת כתב קוקער\nWelcome to Ksav Kooker Setup")
        lbl_hdr.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa;")
        right_box.addWidget(lbl_hdr)

        lbl_ver = QLabel("גרסה 1.0.1 (Offline Edition)")
        lbl_ver.setStyleSheet("font-size: 12px; font-weight: bold; color: #a6e3a1;")
        right_box.addWidget(lbl_ver)

        lbl_desc = QLabel(
            "אשף זה יתקין את תוכנת <b>כתב קוקער (Ksav Kooker)</b> על מחשבך.<br><br>"
            "התוכנה פועלת באופן <b>אופליין מלא ללא חיבור לאינטרנט</b>, ומאפשרת:<br>"
            "• זיהוי כתב יד עברי ורש\"י במחברות שיעורים (OCR)<br>"
            "• עריכה ותיקון שגיאות בזמן אמת זה לצד זה עם התצלום<br>"
            "• מנוע זיכרון ולמידה אוטומטי המשפר את הזיהוי בכל סריקה<br>"
            "• ייצוא ישיר למסמכי Microsoft Word (.docx) מעוצבים מימין לשמאל.<br><br>"
            "לחץ על 'הבא' כדי להמשיך."
        )
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet("line-height: 1.4; color: #cdd6f4;")
        right_box.addWidget(lbl_desc)

        right_box.addStretch()
        layout.addLayout(right_box)
        return page

    def _create_destination_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("בחירת תיקיית התקנה / Destination Location")
        page.setSubTitle("בחר את התיקייה שבה תותקן התוכנה במחשב:")

        layout = QVBoxLayout(page)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Default path in LocalAppData
        default_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "Ksav Kooker")

        lbl_prompt = QLabel("תיקיית יעד:")
        lbl_prompt.setStyleSheet("font-weight: bold;")
        layout.addWidget(lbl_prompt)

        dir_box = QHBoxLayout()
        self.txt_dest = QLineEdit(default_dir)
        dir_box.addWidget(self.txt_dest)

        btn_browse = QPushButton("עיון...")
        btn_browse.clicked.connect(self._browse_destination)
        dir_box.addWidget(btn_browse)
        layout.addLayout(dir_box)

        lbl_space = QLabel("מקום פנוי נדרש: כ-550 MB | המערכת מותקנת עצמאית ללא צורך בהתקנת תוכנות עזר נוספות.")
        lbl_space.setStyleSheet("color: #a6adc8; font-size: 11px;")
        layout.addWidget(lbl_space)

        layout.addStretch()
        return page

    def _browse_destination(self):
        chosen = QFileDialog.getExistingDirectory(self, "בחר תיקיית התקנה", self.txt_dest.text())
        if chosen:
            self.txt_dest.setText(os.path.join(chosen, "Ksav Kooker"))

    def _create_options_page(self) -> QWizardPage:
        page = QWizardPage()
        page.setTitle("אפשרויות נוספות / Additional Tasks")
        page.setSubTitle("בחר אילו קיצורי דרך ליצור:")

        layout = QVBoxLayout(page)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        self.chk_desktop = QCheckBox("צור קיצור דרך על שולחן העבודה (Create Desktop Shortcut)")
        self.chk_desktop.setChecked(True)
        layout.addWidget(self.chk_desktop)

        self.chk_startmenu = QCheckBox("הוסף לתפריט התחלה (Create Start Menu Shortcut)")
        self.chk_startmenu.setChecked(True)
        layout.addWidget(self.chk_startmenu)

        self.chk_launch = QCheckBox("הפעל את כתב קוקער בסיום ההתקנה (Launch Ksav Kooker on Finish)")
        self.chk_launch.setChecked(True)
        layout.addWidget(self.chk_launch)

        layout.addStretch()
        return page

    def _create_installing_page(self) -> QWizardPage:
        self.page_installing = QWizardPage()
        self.page_installing.setTitle("מתקין... / Installing")
        self.page_installing.setSubTitle("אנא המתן בזמן שכתב קוקער מותקן על מחשבך:")

        layout = QVBoxLayout(self.page_installing)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 30, 20, 20)

        self.lbl_install_status = QLabel("מתחיל בהתקנה...")
        self.lbl_install_status.setStyleSheet("font-weight: bold; color: #89b4fa;")
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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(16)

        # 3D Logo on finish
        logo_path = os.path.join(APP_ROOT, "assets", "ksav_kooker.png")
        if os.path.exists(logo_path):
            lbl_banner = QLabel()
            pix = QPixmap(logo_path).scaled(220, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_banner.setPixmap(pix)
            lbl_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_banner.setStyleSheet("background: transparent; border: none;")
            layout.addWidget(lbl_banner)

        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        lbl_hdr = QLabel("ההתקנה הושלמה בהצלחה! ✓\nInstallation Complete!")
        lbl_hdr.setStyleSheet("font-size: 20px; font-weight: bold; color: #a6e3a1;")
        right_box.addWidget(lbl_hdr)

        lbl_msg = QLabel(
            "תוכנת <b>כתב קוקער (Ksav Kooker)</b> הותקנה בהצלחה במחשבך.<br><br>"
            "קיצורי הדרך נוצרו ומוכנים לפעולה.<br>"
            "התוכנה פועלת באופן עצמאי ואופליין לחלוטין.<br><br>"
            "לחץ על 'סיום' לסגירת אשף ההתקנה."
        )
        lbl_msg.setWordWrap(True)
        lbl_msg.setStyleSheet("color: #cdd6f4; font-size: 13px; line-height: 1.5;")
        right_box.addWidget(lbl_msg)

        right_box.addStretch()
        layout.addLayout(right_box)
        return page

    def initializePage(self, page_id: int):
        super().initializePage(page_id)
        if page_id == 3:  # Installing page
            self.button(QWizard.WizardButton.BackButton).setEnabled(False)
            self.button(QWizard.WizardButton.NextButton).setEnabled(False)
            self.button(QWizard.WizardButton.CancelButton).setEnabled(False)
            self._start_installation()

    def _start_installation(self):
        target_dir = self.txt_dest.text().strip()
        self.worker = InstallWorker(
            self.source_app_dir,
            target_dir,
            self.chk_desktop.isChecked(),
            self.chk_startmenu.isChecked()
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
            self.button(QWizard.WizardButton.FinishButton).setEnabled(True)
        else:
            QMessageBox.critical(self, "שגיאה בהתקנה", f"אירעה שגיאה בעת ההתקנה:\n{res}")
            self.button(QWizard.WizardButton.CancelButton).setEnabled(True)

    def accept(self):
        # If launch checked, start app
        if self.chk_launch.isChecked() and self.installed_exe_path and os.path.exists(self.installed_exe_path):
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
