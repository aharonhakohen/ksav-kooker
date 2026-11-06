# -*- coding: utf-8 -*-
r"""
Ohr HaKsav - Modern Update Checker & Source Configuration Dialog
Supports checking for updates via:
  1. Official GitHub Cloud (https://raw.githubusercontent.com/.../version.json)
  2. Local Network Share / Windows Server Domain Share / USB / Offline folder
     (e.g. \\newltcserver\Installs\OhrHaKsav or M:\My Drive\... containing version.json & OhrHaKsav_Setup.exe)
"""

import os
import sys
import json
import urllib.request
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextBrowser, QRadioButton, QButtonGroup,
    QLineEdit, QFileDialog, QTabWidget, QWidget, QFrame,
    QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPixmap

from ui.i18n import t, SETTINGS_PATH, get_current_language
from installer.setup_gui import get_resource_path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ONLINE_URL = "https://raw.githubusercontent.com/aharonhakohen/TorahNotesOCR/main/public/version.json"
DEFAULT_RELEASE_URL = "https://github.com/aharonhakohen/TorahNotesOCR/releases"


def get_current_app_version() -> str:
    """Read current version from version.json."""
    vpath = get_resource_path("version.json")
    try:
        with open(vpath, "r", encoding="utf-8") as f:
            return json.load(f).get("version", "1.1.2")
    except Exception:
        return "1.1.2"


def parse_version_tuple(v_str: str) -> tuple:
    """Parse version string like 'v1.1.2' or '1.1.2' into numeric tuple (1, 1, 2)."""
    clean = str(v_str).strip().lstrip("vV")
    parts = []
    for piece in clean.split("."):
        num = ""
        for ch in piece:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


class CheckUpdateWorker(QThread):
    check_completed = pyqtSignal(dict, bool)  # (version_data, is_update_available)
    check_failed = pyqtSignal(str)           # error_msg

    def __init__(self, source_type: str, source_path: str, current_version: str):
        super().__init__()
        self.source_type = source_type
        self.source_path = source_path
        self.current_version = current_version

    def run(self):
        try:
            data = None
            if self.source_type == "local":
                # Check local directory or network share (UNC path)
                folder = self.source_path.strip()
                if not folder or not os.path.exists(folder):
                    self.check_failed.emit(t("update_err_folder_not_found", folder=folder))
                    return

                vpath = os.path.join(folder, "version.json")
                if not os.path.exists(vpath):
                    self.check_failed.emit(t("update_err_no_version_json", folder=folder))
                    return

                with open(vpath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Check if setup exe is also in this folder
                setup_exe = os.path.join(folder, "OhrHaKsav_Setup.exe")
                data["_local_setup_path"] = setup_exe if os.path.exists(setup_exe) else ""
                data["_source_folder"] = folder

            else:
                # Online GitHub raw JSON
                url = self.source_path.strip() or DEFAULT_ONLINE_URL
                req = urllib.request.Request(url, headers={"User-Agent": "OhrHaKsav-Updater/1.3"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw = resp.read().decode("utf-8")
                    data = json.loads(raw)

            if not data or "version" not in data:
                self.check_failed.emit(t("update_err_invalid_data"))
                return

            remote_ver = data.get("version", "0.0.0")
            cur_tuple = parse_version_tuple(self.current_version)
            remote_tuple = parse_version_tuple(remote_ver)

            is_avail = remote_tuple > cur_tuple
            self.check_completed.emit(data, is_avail)

        except urllib.error.URLError as uerr:
            self.check_failed.emit(t("update_err_network", err=str(uerr.reason)))
        except Exception as e:
            self.check_failed.emit(str(e))


class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_version = get_current_app_version()
        self.worker = None
        self.latest_data = {}
        self.setWindowTitle(t("update_dialog_title"))
        self.resize(620, 480)
        self.setMinimumSize(560, 420)

        # Icon
        icon_path = get_resource_path(os.path.join("assets", "ohr_haksav.ico"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._load_settings()
        self._init_ui()
        self._start_check()

    def _load_settings(self):
        self.source_type = "online"
        self.source_local_path = ""
        self.source_online_url = DEFAULT_ONLINE_URL
        self.auto_check_startup = False

        # Read from local_deploy.txt as sensible default for local share if exists
        deploy_cfg = os.path.join(BASE_DIR, "local_deploy.txt")
        if os.path.exists(deploy_cfg):
            try:
                with open(deploy_cfg, "r", encoding="utf-8") as f:
                    candidate = f.read().strip()
                    if candidate and os.path.exists(candidate):
                        self.source_local_path = candidate
            except Exception:
                pass

        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.source_type = cfg.get("update_source_type", self.source_type)
                    self.source_local_path = cfg.get("update_local_path", self.source_local_path)
                    self.source_online_url = cfg.get("update_online_url", self.source_online_url)
                    self.auto_check_startup = cfg.get("update_auto_check", self.auto_check_startup)
            except Exception:
                pass

    def _save_settings(self):
        try:
            os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
            cfg = {}
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)

            cfg["update_source_type"] = self.source_type
            cfg["update_local_path"] = self.source_local_path
            cfg["update_online_url"] = self.source_online_url
            cfg["update_auto_check"] = self.auto_check_startup

            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Notice: Failed to save update settings: {e}")

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(12)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Tab 1: Status
        tab_status = QWidget()
        self._init_status_tab(tab_status)
        self.tabs.addTab(tab_status, t("update_tab_status"))

        # Tab 2: Settings & Source
        tab_settings = QWidget()
        self._init_settings_tab(tab_settings)
        self.tabs.addTab(tab_settings, t("update_tab_settings"))

        # Bottom Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.addStretch()
        self.btn_close = QPushButton(t("update_btn_close"))
        self.btn_close.setMinimumWidth(90)
        self.btn_close.clicked.connect(self.close)
        bottom_bar.addWidget(self.btn_close)
        main_layout.addLayout(bottom_bar)

    def _init_status_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Top Header Card
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet("""
            QFrame {
                background-color: #f1f5f9;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        hdr_layout = QHBoxLayout(hdr_frame)
        hdr_layout.setSpacing(14)

        logo_path = get_resource_path(os.path.join("assets", "ohr_haksav.png"))
        if os.path.exists(logo_path):
            lbl_ico = QLabel()
            pix = QPixmap(logo_path).scaled(42, 42, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_ico.setPixmap(pix)
            lbl_ico.setFixedSize(42, 42)
            hdr_layout.addWidget(lbl_ico)

        v_box = QVBoxLayout()
        v_box.setSpacing(2)
        lbl_app = QLabel("<b>Ohr HaKsav (אור הכתב)</b>")
        lbl_app.setStyleSheet("font-size: 15px; color: #0f172a;")
        v_box.addWidget(lbl_app)

        self.lbl_ver_badge = QLabel(t("update_curr_version", version=self.current_version))
        self.lbl_ver_badge.setStyleSheet("font-size: 12px; color: #475569;")
        v_box.addWidget(self.lbl_ver_badge)
        hdr_layout.addLayout(v_box)
        hdr_layout.addStretch()

        self.btn_check_again = QPushButton(t("update_btn_check_again"))
        self.btn_check_again.clicked.connect(self._start_check)
        hdr_layout.addWidget(self.btn_check_again)
        layout.addWidget(hdr_frame)

        # Progress / Status indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # indeterminate spinner
        self.progress_bar.setFixedHeight(12)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.lbl_status = QLabel(t("update_checking_msg", source=self._get_source_display_name()))
        self.lbl_status.setStyleSheet("font-size: 13px; font-weight: 500; color: #2563eb;")
        layout.addWidget(self.lbl_status)

        # Details Content Area
        self.browser_details = QTextBrowser()
        self.browser_details.setOpenExternalLinks(True)
        self.browser_details.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                color: #0f172a;
            }
        """)
        layout.addWidget(self.browser_details, stretch=1)

        # Action Buttons row
        self.action_box = QHBoxLayout()
        self.action_box.setSpacing(10)

        self.btn_install_local = QPushButton(t("update_btn_run_installer"))
        self.btn_install_local.setObjectName("btn_success")
        self.btn_install_local.setStyleSheet("background-color: #059669; color: white; font-weight: bold; padding: 7px 16px;")
        self.btn_install_local.setVisible(False)
        self.btn_install_local.clicked.connect(self._run_local_installer)
        self.action_box.addWidget(self.btn_install_local)

        self.btn_open_folder = QPushButton(t("update_btn_open_folder"))
        self.btn_open_folder.setVisible(False)
        self.btn_open_folder.clicked.connect(self._open_staging_folder)
        self.action_box.addWidget(self.btn_open_folder)

        self.btn_open_web = QPushButton(t("update_btn_open_web"))
        self.btn_open_web.setObjectName("btn_primary")
        self.btn_open_web.setStyleSheet("background-color: #2563eb; color: white; font-weight: bold; padding: 7px 16px;")
        self.btn_open_web.setVisible(False)
        self.btn_open_web.clicked.connect(self._open_web_release)
        self.action_box.addWidget(self.btn_open_web)

        self.action_box.addStretch()
        layout.addLayout(self.action_box)

    def _init_settings_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        lbl_hdr = QLabel(f"<b>{t('update_source_group')}</b>")
        lbl_hdr.setStyleSheet("font-size: 14px; color: #0f172a;")
        layout.addWidget(lbl_hdr)

        self.bg_source = QButtonGroup(self)

        # Radio 1: Online GitHub
        self.rad_online = QRadioButton(t("update_source_web"))
        self.rad_online.setStyleSheet("font-weight: 600; color: #0f172a;")
        self.bg_source.addButton(self.rad_online)
        layout.addWidget(self.rad_online)

        lbl_online_desc = QLabel(t("update_source_web_desc"))
        lbl_online_desc.setStyleSheet("color: #64748b; font-size: 12px; margin-left: 22px;")
        lbl_online_desc.setWordWrap(True)
        layout.addWidget(lbl_online_desc)

        # Radio 2: Local Network Share / Offline Folder
        self.rad_local = QRadioButton(t("update_source_local"))
        self.rad_local.setStyleSheet("font-weight: 600; color: #0f172a; margin-top: 10px;")
        self.bg_source.addButton(self.rad_local)
        layout.addWidget(self.rad_local)

        lbl_local_desc = QLabel(t("update_source_local_desc"))
        lbl_local_desc.setStyleSheet("color: #64748b; font-size: 12px; margin-left: 22px;")
        lbl_local_desc.setWordWrap(True)
        layout.addWidget(lbl_local_desc)

        # Folder Picker Row
        folder_box = QHBoxLayout()
        folder_box.setContentsMargins(22, 0, 0, 0)
        self.txt_local_path = QLineEdit(self.source_local_path)
        self.txt_local_path.setPlaceholderText(r"e.g. \\newltcserver\Installs\OhrHaKsav or M:\My Drive\...")
        folder_box.addWidget(self.txt_local_path)

        btn_browse = QPushButton(t("update_folder_browse_btn"))
        btn_browse.clicked.connect(self._browse_local_folder)
        folder_box.addWidget(btn_browse)
        layout.addLayout(folder_box)

        # Select current radio
        if self.source_type == "local":
            self.rad_local.setChecked(True)
        else:
            self.rad_online.setChecked(True)

        layout.addSpacing(10)

        # Save Button
        save_box = QHBoxLayout()
        self.btn_save_settings = QPushButton(t("update_save_settings_btn"))
        self.btn_save_settings.setStyleSheet("background-color: #2563eb; color: white; font-weight: 600; padding: 7px 18px;")
        self.btn_save_settings.clicked.connect(self._apply_settings_and_check)
        save_box.addWidget(self.btn_save_settings)
        save_box.addStretch()
        layout.addLayout(save_box)

        layout.addStretch()

    def _get_source_display_name(self) -> str:
        if self.source_type == "local":
            path = self.source_local_path or "Local Folder"
            return f"Local / Network: {os.path.basename(path) or path}"
        return "GitHub Cloud"

    def _browse_local_folder(self):
        chosen = QFileDialog.getExistingDirectory(
            self,
            t("update_source_local"),
            self.txt_local_path.text() or os.path.expanduser("~")
        )
        if chosen:
            self.txt_local_path.setText(chosen)

    def _apply_settings_and_check(self):
        self.source_type = "local" if self.rad_local.isChecked() else "online"
        self.source_local_path = self.txt_local_path.text().strip()
        self._save_settings()

        self.tabs.setCurrentIndex(0)
        self._start_check()

    def _start_check(self):
        if self.worker and self.worker.isRunning():
            return

        self.progress_bar.setVisible(True)
        self.lbl_status.setText(t("update_checking_msg", source=self._get_source_display_name()))
        self.lbl_status.setStyleSheet("font-size: 13px; font-weight: 500; color: #2563eb;")
        self.browser_details.setHtml("")
        self.btn_check_again.setEnabled(False)
        self.btn_install_local.setVisible(False)
        self.btn_open_folder.setVisible(False)
        self.btn_open_web.setVisible(False)

        source_path = self.source_local_path if self.source_type == "local" else self.source_online_url
        self.worker = CheckUpdateWorker(self.source_type, source_path, self.current_version)
        self.worker.check_completed.connect(self._on_check_completed)
        self.worker.check_failed.connect(self._on_check_failed)
        self.worker.start()

    def _on_check_completed(self, data: dict, is_avail: bool):
        self.progress_bar.setVisible(False)
        self.btn_check_again.setEnabled(True)
        self.latest_data = data

        remote_ver = data.get("version", self.current_version)
        release_date = data.get("releaseDate", "")
        title = data.get("releaseTitle", "")
        desc = data.get("description", "")
        features = data.get("features", [])

        if is_avail:
            self.lbl_status.setText(t("update_available_hdr", version=remote_ver))
            self.lbl_status.setStyleSheet("font-size: 15px; font-weight: bold; color: #047857;")

            # Build HTML details
            html = f"""
            <div style="font-family: 'Segoe UI', sans-serif; line-height: 1.5;">
                <h3 style="color: #0f172a; margin-top: 0; margin-bottom: 4px;">{title or f"Version {remote_ver}"}</h3>
                <div style="font-size: 12px; color: #64748b; margin-bottom: 12px;">{t('update_release_date', date=release_date)}</div>
                <p style="color: #1e293b; font-size: 13px;">{desc}</p>
                <h4 style="color: #0f172a; margin-bottom: 6px;">{t('update_whats_new')}</h4>
                <ul style="color: #334155; margin-top: 0; padding-left: 20px;">
            """
            for feat in features:
                html += f"<li style='margin-bottom: 4px;'>{feat}</li>"
            html += "</ul></div>"
            self.browser_details.setHtml(html)

            # Show appropriate action buttons
            local_setup = data.get("_local_setup_path", "")
            if local_setup and os.path.exists(local_setup):
                self.btn_install_local.setVisible(True)
                self.btn_open_folder.setVisible(True)
            else:
                if self.source_type == "local":
                    self.btn_open_folder.setVisible(True)
                self.btn_open_web.setVisible(True)

        else:
            self.lbl_status.setText(t("update_up_to_date_hdr"))
            self.lbl_status.setStyleSheet("font-size: 15px; font-weight: bold; color: #059669;")

            html = f"""
            <div style="font-family: 'Segoe UI', sans-serif; line-height: 1.5; padding: 10px;">
                <p style="font-size: 14px; color: #059669; font-weight: 600;">✓ {t('update_up_to_date_sub', version=self.current_version)}</p>
                <p style="color: #475569; font-size: 13px;">{desc}</p>
                <h4 style="color: #0f172a; margin-bottom: 6px;">{t('update_whats_new')}</h4>
                <ul style="color: #334155; margin-top: 0; padding-left: 20px;">
            """
            for feat in features:
                html += f"<li style='margin-bottom: 4px;'>{feat}</li>"
            html += "</ul></div>"
            self.browser_details.setHtml(html)

    def _on_check_failed(self, err_msg: str):
        self.progress_bar.setVisible(False)
        self.btn_check_again.setEnabled(True)
        self.lbl_status.setText(t("update_err_hdr"))
        self.lbl_status.setStyleSheet("font-size: 14px; font-weight: bold; color: #dc2626;")

        html = f"""
        <div style="font-family: 'Segoe UI', sans-serif; line-height: 1.5; color: #b91c1c; padding: 8px;">
            <p><b>{t('update_err_hdr')}</b></p>
            <p style="color: #475569;">{err_msg}</p>
            <p style="color: #64748b; font-size: 12px;">
                Tip: If working offline or in a Windows Server domain environment, open the <b>Update Source & Settings</b> tab to specify a local network folder or USB path containing version.json and OhrHaKsav_Setup.exe.
            </p>
        </div>
        """
        self.browser_details.setHtml(html)

    def _run_local_installer(self):
        setup_exe = self.latest_data.get("_local_setup_path", "")
        if not setup_exe or not os.path.exists(setup_exe):
            QMessageBox.warning(self, "Setup Not Found", f"OhrHaKsav_Setup.exe was not found in: {self.latest_data.get('_source_folder', '')}")
            return

        reply = QMessageBox.question(
            self,
            t("update_prompt_close_title"),
            t("update_prompt_close_msg"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        # Launch the setup wizard
        subprocess.Popen([setup_exe], shell=True)

        if reply == QMessageBox.StandardButton.Yes:
            # Exit application so installer can replace files cleanly without lock
            QApplication.quit()
        else:
            self.accept()

    def _open_staging_folder(self):
        folder = self.latest_data.get("_source_folder", self.source_local_path)
        if folder and os.path.exists(folder):
            os.startfile(folder)

    def _open_web_release(self):
        import webbrowser
        webbrowser.open(DEFAULT_RELEASE_URL)
