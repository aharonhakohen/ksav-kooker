# -*- coding: utf-8 -*-
"""
Ksav Kooker - About Dialog
Displays app information, 3D logo, version details, and user guide.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextBrowser
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
import os
import sys
import json

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("אודות כתב קוקער | About Ksav Kooker")
        self.resize(580, 560)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # Top Header with 3D Logo
        hdr_layout = QHBoxLayout()
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "assets", "ksav_kooker.png")

        if os.path.exists(logo_path):
            lbl_img = QLabel()
            pix = QPixmap(logo_path).scaled(110, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_img.setPixmap(pix)
            lbl_img.setStyleSheet("border: none; background: transparent;")
            hdr_layout.addWidget(lbl_img)

        # Title Info
        title_box = QVBoxLayout()
        title_box.setSpacing(4)
        lbl_title = QLabel("Ksav Kooker  •  כתב קוקער")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #89b4fa;")
        title_box.addWidget(lbl_title)

        # Load version info
        ver_str = "1.0.1"
        try:
            ver_path = os.path.join(base_dir, "version.json")
            if os.path.exists(ver_path):
                with open(ver_path, "r", encoding="utf-8") as vf:
                    vdata = json.load(vf)
                    ver_str = vdata.get("version", ver_str)
        except Exception:
            pass

        lbl_ver = QLabel(f"גרסה {ver_str}  •  Version {ver_str} (Offline Edition)")
        lbl_ver.setStyleSheet("font-size: 13px; font-weight: 600; color: #a6e3a1;")
        title_box.addWidget(lbl_ver)

        lbl_sub = QLabel("סטודיו אופליין לזיהוי כתב יד תורני ומחברות שיעורים\nדער קלוגער כתב-קוקער פאר שיעורים און חידושי תורה")
        lbl_sub.setStyleSheet("font-size: 11px; color: #a6adc8; font-style: italic;")
        title_box.addWidget(lbl_sub)

        hdr_layout.addLayout(title_box)
        hdr_layout.addStretch()
        layout.addLayout(hdr_layout)

        # Text Content
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml("""
        <div style="font-family: sans-serif; line-height: 1.5; color: #cdd6f4;">
            <p><b>What is Ksav Kooker?</b><br>
            <b>Ksav Kooker</b> (כתב קוקער — Yiddish for <i>'Handwriting / Script Scanner & Viewer'</i>) is a fully offline, standalone desktop application built specifically for yeshiva students, rebbeim, and talmidei chachamim to digitize handwritten shiur notes and Torah chiddushim.</p>
            
            <p><b>Key Capabilities:</b></p>
            <ul>
                <li><b>100% Offline Neural OCR:</b> Runs a local PyTorch CTC neural model optimized for cursive Ashkenazi and Sefardi handwriting on CPU without internet.</li>
                <li><b>Side-by-Side Review:</b> High-resolution photo inspection (pan, zoom, 90-degree rotate, ink-enhancer) alongside a rich Hebrew RTL editor.</li>
                <li><b>Self-Learning Memory Engine:</b> Automatically learns from every correction you make so it never repeats the same mistake twice on future scans.</li>
                <li><b>Pre-Loaded Yeshiva Lexicon:</b> Built-in knowledge of over 50 common Talmudic abbreviations (רש"י, תוס', רמב"ם, נפק"מ, קמ"ל, ח"נ, נ"ש, וכו').</li>
                <li><b>Microsoft Word Export:</b> Generates clean, right-to-left formatted <code>.docx</code> documents ready for print or sharing.</li>
            </ul>

            <p><b>Privacy & Security:</b><br>
            All recognition and database operations are performed strictly on your local computer. No data ever leaves your device.</p>
        </div>
        """)
        layout.addWidget(browser)

        btn_close = QPushButton("סגור / Close")
        btn_close.setObjectName("btn_primary")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)
