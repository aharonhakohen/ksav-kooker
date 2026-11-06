# -*- coding: utf-8 -*-
"""
Ohr HaKsav (אור הכתב) - Offline Torah Notes & Handwriting OCR Studio
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
        myappid = 'TU.LTC.OhrHaKsav.OCR.v1'
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
    app.setApplicationName("OhrHaKsav")
    app.setApplicationDisplayName("אור הכתב - Ohr HaKsav")

    # Set icon
    base_dir = getattr(sys, '_MEIPASS', BASE_DIR)
    icon_path = os.path.join(base_dir, "assets", "ohr_haksav.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Show Splash Screen centered on active display
    splash = ModernSplashScreen()
    splash.center_on_screen()
    splash.show()
    app.processEvents()

    # Step 1: Initializing
    splash.set_progress(25, "Initializing offline Hebrew handwriting OCR engine...")
    app.processEvents()
    time.sleep(0.3)

    # Step 2: Database
    splash.set_progress(60, "Loading mistake memory bank and handwriting profiles...")
    app.processEvents()
    time.sleep(0.3)

    # Step 3: UI
    splash.set_progress(90, "Loading Hebrew proofreading studio and interface...")
    app.processEvents()

    # Create main window
    window = MainWindow()
    window.center_on_screen()

    splash.set_progress(100, "Ready!")
    app.processEvents()
    time.sleep(0.3)

    # Transition to main window
    splash.finish(window)
    window.center_on_screen()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
