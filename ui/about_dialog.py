# -*- coding: utf-8 -*-
"""
TorahNotesOCR - About Dialog
Displays app information, versioning, release notes, and user-friendly explanations.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextBrowser
)
from PyQt6.QtCore import Qt
import os
import json

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("אודות איבערקוק | About IbberKuck")
        self.resize(550, 480)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Load version info
        version_data = {}
        vpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "version.json")
        if os.path.exists(vpath):
            try:
                with open(vpath, "r", encoding="utf-8") as f:
                    version_data = json.load(f)
            except Exception:
                pass

        app_name = version_data.get("appName", "IbberKuck")
        app_name_heb = version_data.get("appNameHebrew", "איבערקוק")
        version = version_data.get("version", "1.0.0")
        tagline = version_data.get("tagline", "Offline Torah Notes & Handwriting OCR Studio")
        tagline_yi = version_data.get("taglineYiddish", "דער קלוגער כתב-איבערקוקער פאר שיעורים און חידושי תורה")
        desc = version_data.get("description", "")
        features = version_data.get("features", [])

        # Title Header
        lbl_title = QLabel(f"{app_name}  —  {app_name_heb}")
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #89b4fa;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_ver = QLabel(f"גרסה {version}  •  Version {version} (Offline Edition)")
        lbl_ver.setStyleSheet("font-size: 13px; font-weight: 600; color: #a6e3a1;")
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_ver)

        lbl_sub = QLabel(f"{tagline}\n{tagline_yi}")
        lbl_sub.setStyleSheet("font-size: 12px; color: #a6adc8; font-style: italic;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        # Detailed Plain English & Hebrew text browser
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        html_features = "".join(f"<li>{f}</li>" for f in features)
        browser.setHtml(f"""
        <div style="font-family: sans-serif; line-height: 1.5; color: #cdd6f4;">
            <p><b>What is IbberKuck?</b><br>
            IbberKuck (איבערקוק - Yiddish for <i>'to look over, inspect, and review'</i>) is a fully offline, standalone desktop application built specifically for yeshiva students, rebbeim, and talmidei chachamim to digitize handwritten shiur notes and Torah chiddushim.</p>
            
            <p><b>Key Capabilities:</b></p>
            <ul>
                {html_features}
            </ul>

            <p><b>How the Self-Learning Memory Engine Works:</b><br>
            When you correct an OCR reading on your screen (for example, fixing a word or adding an apostrophe to an abbreviation), IbberKuck automatically compares your edits with the raw scan. It registers the replacement rule in its local database, ensuring that on all subsequent scans, that mistake is resolved automatically without repeating!</p>

            <p><b>100% Offline & Private:</b><br>
            No internet connection is required. All neural OCR recognition, database queries, and Word exports happen strictly on your local computer.</p>
        </div>
        """)
        layout.addWidget(browser)

        btn_close = QPushButton("סגור / Close")
        btn_close.setObjectName("btn_primary")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
