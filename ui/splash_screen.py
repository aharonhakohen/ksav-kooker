# -*- coding: utf-8 -*-
"""
Ksav Kooker - Modern Splash Screen
Displays the 3D logo, version details, and initial engine loading progress.
"""

import os
import sys
from PyQt6.QtWidgets import (
    QSplashScreen, QWidget, QVBoxLayout, QLabel, 
    QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QColor, QFont

class ModernSplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.SplashScreen | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._init_ui()

    def _init_ui(self):
        container = QWidget(self)
        container.setFixedSize(480, 520)
        container.setStyleSheet("""
            QWidget {
                background-color: #181825;
                border: 2px solid #313244;
                border-radius: 16px;
                color: #cdd6f4;
                font-family: 'Segoe UI', 'David', sans-serif;
            }
        """)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3D Logo Image
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "assets", "ksav_kooker.png")
        if not os.path.exists(logo_path):
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "ksav_kooker.png")

        self.lbl_logo = QLabel()
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path).scaled(
                260, 260, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.lbl_logo.setPixmap(pix)
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.lbl_logo)

        # Title
        lbl_title = QLabel("Ksav Kooker  •  כתב קוקער")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #89b4fa; border: none; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        # Subtitle
        lbl_sub = QLabel("Offline Torah Notes & Handwriting OCR Studio")
        lbl_sub.setStyleSheet("font-size: 12px; color: #a6adc8; border: none; background: transparent;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        # Version badge
        lbl_ver = QLabel("גרסה 1.0.0  (Offline Edition)")
        lbl_ver.setStyleSheet("font-size: 11px; font-weight: 600; color: #a6e3a1; border: none; background: transparent;")
        lbl_ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_ver)

        layout.addSpacing(10)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #313244;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #2563eb;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(10)
        layout.addWidget(self.progress_bar)

        # Status text
        self.lbl_status = QLabel("מאתחל מנוע זיהוי כתב יד אופליין...")
        self.lbl_status.setStyleSheet("font-size: 11px; color: #9399b2; border: none; background: transparent;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_status)

        self.resize(480, 520)

    def set_progress(self, value: int, message: str = ""):
        self.progress_bar.setValue(value)
        if message:
            self.lbl_status.setText(message)
        self.repaint()
