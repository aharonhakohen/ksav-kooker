# -*- coding: utf-8 -*-
"""
Ksav Kooker (כתב קוקער) - Offline Torah Notes & Handwriting OCR Studio
Main Application Entry Point with 3D Splash Screen and Taskbar Icon.
"""

import sys
import os
import time

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Set Windows AppUserModelID for crisp taskbar icon
if sys.platform == "win32":
    try:
        import ctypes
        myappid = 'TU.LTC.KsavKooker.OCR.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QTimer

from ui.splash_screen import ModernSplashScreen
from ui.main_window import MainWindow

def main():
    # High DPI scaling support
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("KsavKooker")
    app.setApplicationDisplayName("כתב קוקער - Ksav Kooker")

    # Set icon
    base_dir = getattr(sys, '_MEIPASS', BASE_DIR)
    icon_path = os.path.join(base_dir, "assets", "ksav_kooker.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Show Splash Screen
    splash = ModernSplashScreen()
    splash.show()
    app.processEvents()

    # Step 1: Initializing
    splash.set_progress(25, "מאתחל מנוע זיהוי כתב יד אופליין...")
    app.processEvents()
    time.sleep(0.3)

    # Step 2: Database
    splash.set_progress(60, "מאתחל מאגר זיכרון תיקונים (Learning Engine)...")
    app.processEvents()
    time.sleep(0.3)

    # Step 3: UI
    splash.set_progress(90, "טוען ממשק משתמש ועורך עברי...")
    app.processEvents()

    # Create main window
    window = MainWindow()

    splash.set_progress(100, "מוכן לפעולה!")
    app.processEvents()
    time.sleep(0.4)

    # Transition to main window
    splash.finish(window)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
