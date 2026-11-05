# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Main Application Window
Modern, sleek, side-by-side OCR & handwriting transcription studio.
Features a native Windows Menu Bar, stacked workflow action buttons,
high-contrast typography, and dynamic English/Hebrew UI localization.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from PIL import Image

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QListWidget, QListWidgetItem, QPushButton, 
    QLabel, QProgressBar, QFileDialog, QMessageBox, 
    QToolBar, QStatusBar, QFrame, QInputDialog,
    QMenuBar, QMenu, QToolButton, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction, QKeySequence

from ui.image_viewer import DocumentViewer
from ui.text_editor import HebrewTextEditor
from ui.dictionary_dialog import DictionaryManagerDialog
from ui.about_dialog import AboutDialog
from ui.theme import DARK_THEME, LIGHT_THEME
from ui.i18n import t, I18nManager
from core.ocr_engine import OCREngine
from core.learning_engine import LearningEngine
from core.docx_exporter import export_notes_to_docx

def get_resource_path(rel_path: str) -> str:
    """Resolve path to resource file for both PyInstaller and source development."""
    if hasattr(sys, '_MEIPASS'):
        c1 = os.path.join(sys._MEIPASS, rel_path)
        if os.path.exists(c1):
            return c1
        c2 = os.path.join(sys._MEIPASS, os.path.basename(rel_path))
        if os.path.exists(c2):
            return c2
    if getattr(sys, 'frozen', False):
        c3 = os.path.join(os.path.dirname(sys.executable), rel_path)
        if os.path.exists(c3):
            return c3
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    c4 = os.path.join(base_dir, rel_path)
    if os.path.exists(c4):
        return c4
    return rel_path


class OCRWorker(QThread):
    progress = pyqtSignal(int, int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, ocr_engine: OCREngine, learning_engine: LearningEngine, image_path: str, rotation: int = 0):
        super().__init__()
        self.ocr_engine = ocr_engine
        self.learning_engine = learning_engine
        self.image_path = image_path
        self.rotation = rotation

    def run(self):
        try:
            pil_img = Image.open(self.image_path)
            if self.rotation % 360 != 0:
                pil_img = pil_img.rotate(-self.rotation, expand=True)

            def progress_callback(cur, tot, msg):
                self.progress.emit(cur, tot, msg)

            raw_result = self.ocr_engine.recognize_page(pil_img, progress_callback=progress_callback)
            corrected_text, applied_rules = self.learning_engine.apply_corrections(raw_result["full_text"])

            final_result = {
                "raw_text": raw_result["full_text"],
                "text": corrected_text,
                "lines": raw_result["lines"],
                "corrections_applied": len(applied_rules),
                "rules_details": applied_rules
            }
            self.finished.emit(final_result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(t("app_title"))
        self.resize(1200, 780)
        self.setMinimumSize(960, 600)

        # Set Window Icon
        icon_path = get_resource_path(os.path.join("assets", "ksav_kooker.png"))
        if not os.path.exists(icon_path):
            icon_path = get_resource_path(os.path.join("assets", "ksav_kooker.ico"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Core Engines
        self.learning_engine = LearningEngine()
        self.ocr_engine = OCREngine()

        # State
        self.pages: List[Dict[str, Any]] = []
        self.current_page_idx = -1
        self.is_dark_theme = True
        self.active_worker = None

        self._init_ui()
        self._refresh_profiles_ui()
        self._retranslate_ui()
        self.apply_theme()

    def _init_ui(self):
        # 1. Native Windows Menu Bar
        self._create_menu_bar()

        # 2. Central Layout
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 6, 8, 8)
        main_layout.setSpacing(6)

        # 3. Streamlined Action Toolbar
        self._create_top_toolbar(main_layout)

        # 4. Main 3-Pane Splitter (Sidebar | Document Viewer | Text Editor)
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)

        sidebar_frame = self._create_sidebar()
        content_splitter.addWidget(sidebar_frame)

        viewer_frame = self._create_viewer_panel()
        content_splitter.addWidget(viewer_frame)

        editor_frame = self._create_editor_panel()
        content_splitter.addWidget(editor_frame)

        content_splitter.setSizes([190, 500, 500])
        main_layout.addWidget(content_splitter, 1)

        # 5. Status Bar
        self._create_status_bar(main_layout)

    def _create_menu_bar(self):
        mb = self.menuBar()

        # File Menu
        self.m_file = mb.addMenu(t("menu_file"))
        self.act_file_add = QAction(t("menu_file_add"), self)
        self.act_file_add.setShortcut(QKeySequence("Ctrl+O"))
        self.act_file_add.triggered.connect(self.attach_images_dialog)
        self.m_file.addAction(self.act_file_add)

        self.act_file_remove = QAction(t("menu_file_remove"), self)
        self.act_file_remove.setShortcut(QKeySequence("Delete"))
        self.act_file_remove.triggered.connect(self.remove_selected_page)
        self.m_file.addAction(self.act_file_remove)

        self.act_file_clear = QAction(t("menu_file_clear"), self)
        self.act_file_clear.triggered.connect(self.clear_all_pages)
        self.m_file.addAction(self.act_file_clear)

        self.m_file.addSeparator()

        self.act_file_exp_word = QAction(t("menu_file_export_word"), self)
        self.act_file_exp_word.setShortcut(QKeySequence("Ctrl+E"))
        self.act_file_exp_word.triggered.connect(self.export_to_docx_dialog)
        self.m_file.addAction(self.act_file_exp_word)

        self.act_file_exp_txt = QAction(t("menu_file_export_txt"), self)
        self.act_file_exp_txt.setShortcut(QKeySequence("Ctrl+S"))
        self.act_file_exp_txt.triggered.connect(self.export_to_txt_dialog)
        self.m_file.addAction(self.act_file_exp_txt)

        self.m_file.addSeparator()

        self.act_file_exit = QAction(t("menu_file_exit"), self)
        self.act_file_exit.setShortcut(QKeySequence("Alt+F4"))
        self.act_file_exit.triggered.connect(self.close)
        self.m_file.addAction(self.act_file_exit)

        # Scan & OCR Menu
        self.m_scan = mb.addMenu(t("menu_scan"))
        self.act_scan_curr = QAction(t("menu_scan_current"), self)
        self.act_scan_curr.setShortcut(QKeySequence("F5"))
        self.act_scan_curr.triggered.connect(self.scan_current_page)
        self.m_scan.addAction(self.act_scan_curr)

        self.act_scan_all = QAction(t("menu_scan_all"), self)
        self.act_scan_all.setShortcut(QKeySequence("Shift+F5"))
        self.act_scan_all.triggered.connect(self.scan_all_pages)
        self.m_scan.addAction(self.act_scan_all)

        self.m_scan.addSeparator()

        self.act_scan_contrast = QAction(t("menu_scan_enhance"), self)
        self.act_scan_contrast.setShortcut(QKeySequence("Ctrl+I"))
        self.act_scan_contrast.triggered.connect(self.toggle_image_contrast)
        self.m_scan.addAction(self.act_scan_contrast)

        # Learning & Profiles Menu
        self.m_learn = mb.addMenu(t("menu_learning"))
        self.act_learn_save = QAction(t("menu_learning_save"), self)
        self.act_learn_save.setShortcut(QKeySequence("Ctrl+L"))
        self.act_learn_save.triggered.connect(self.learn_current_corrections)
        self.m_learn.addAction(self.act_learn_save)

        self.act_learn_studio = QAction(t("menu_learning_studio"), self)
        self.act_learn_studio.setShortcut(QKeySequence("Ctrl+M"))
        self.act_learn_studio.triggered.connect(self.open_dictionary_manager)
        self.m_learn.addAction(self.act_learn_studio)

        self.act_learn_new_prof = QAction(t("menu_learning_new_profile"), self)
        self.act_learn_new_prof.triggered.connect(self._quick_new_profile)
        self.m_learn.addAction(self.act_learn_new_prof)

        # View Menu
        self.m_view = mb.addMenu(t("menu_view"))
        self.act_view_cw = QAction(t("menu_view_rotate_cw"), self)
        self.act_view_cw.setShortcut(QKeySequence("Ctrl+]"))
        self.act_view_cw.triggered.connect(self.rotate_image_cw)
        self.m_view.addAction(self.act_view_cw)

        self.act_view_ccw = QAction(t("menu_view_rotate_ccw"), self)
        self.act_view_ccw.setShortcut(QKeySequence("Ctrl+["))
        self.act_view_ccw.triggered.connect(self.rotate_image_ccw)
        self.m_view.addAction(self.act_view_ccw)

        self.m_view.addSeparator()

        self.act_view_zi = QAction(t("menu_view_zoom_in"), self)
        self.act_view_zi.setShortcut(QKeySequence("Ctrl++"))
        self.act_view_zi.triggered.connect(lambda: self.viewer.zoom_in())
        self.m_view.addAction(self.act_view_zi)

        self.act_view_zo = QAction(t("menu_view_zoom_out"), self)
        self.act_view_zo.setShortcut(QKeySequence("Ctrl+-"))
        self.act_view_zo.triggered.connect(lambda: self.viewer.zoom_out())
        self.m_view.addAction(self.act_view_zo)

        self.act_view_fit = QAction(t("menu_view_fit"), self)
        self.act_view_fit.setShortcut(QKeySequence("Ctrl+0"))
        self.act_view_fit.triggered.connect(lambda: self.viewer.fit_to_window())
        self.m_view.addAction(self.act_view_fit)

        self.m_view.addSeparator()

        self.act_view_theme = QAction(t("menu_view_theme"), self)
        self.act_view_theme.setShortcut(QKeySequence("Ctrl+T"))
        self.act_view_theme.triggered.connect(self.toggle_theme)
        self.m_view.addAction(self.act_view_theme)

        # Language Menu
        self.m_lang = mb.addMenu(t("menu_language"))
        self.act_lang_en = QAction(t("menu_lang_en"), self)
        self.act_lang_en.triggered.connect(lambda: self._set_lang("en"))
        self.m_lang.addAction(self.act_lang_en)

        self.act_lang_he = QAction(t("menu_lang_he"), self)
        self.act_lang_he.triggered.connect(lambda: self._set_lang("he"))
        self.m_lang.addAction(self.act_lang_he)

        # Help Menu
        self.m_help = mb.addMenu(t("menu_help"))
        self.act_help_about = QAction(t("menu_help_about"), self)
        self.act_help_about.triggered.connect(self.open_about_dialog)
        self.m_help.addAction(self.act_help_about)

    def _set_lang(self, lang: str):
        I18nManager.instance().set_language(lang)
        self._retranslate_ui()

    def _create_top_toolbar(self, parent_layout):
        bar = QHBoxLayout()
        bar.setSpacing(6)

        # 1. Brand Logo & Title Hub (immune to clipping with Fixed policy)
        self.brand_widget = QWidget()
        brand_box = QHBoxLayout(self.brand_widget)
        brand_box.setContentsMargins(0, 0, 4, 0)
        brand_box.setSpacing(6)

        logo_path = get_resource_path(os.path.join("assets", "ksav_kooker.png"))
        if os.path.exists(logo_path):
            self.lbl_logo = QLabel()
            pix = QPixmap(logo_path).scaled(26, 26, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.lbl_logo.setPixmap(pix)
            self.lbl_logo.setFixedSize(26, 26)
            brand_box.addWidget(self.lbl_logo)

        self.lbl_brand = QLabel(f"<b>{t('brand_name')}</b>")
        self.lbl_brand.setStyleSheet("font-size: 15px; color: #89b4fa;")
        self.lbl_brand.setMinimumWidth(100)
        brand_box.addWidget(self.lbl_brand)

        self.brand_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        bar.addWidget(self.brand_widget)

        # Separator
        self.sep_brand = QFrame()
        self.sep_brand.setFrameShape(QFrame.Shape.VLine)
        self.sep_brand.setStyleSheet("color: #313244;")
        bar.addWidget(self.sep_brand)

        # 2. Add Pages Button
        self.btn_attach = QPushButton(f"📁 {t('btn_add_pages_short')}")
        self.btn_attach.setObjectName("btn_primary")
        self.btn_attach.setToolTip(t("btn_attach_tooltip"))
        self.btn_attach.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_attach.clicked.connect(self.attach_images_dialog)
        bar.addWidget(self.btn_attach)

        # 3. Stacked Scan Dropdown Button
        self.btn_scan = QToolButton()
        self.btn_scan.setText(f"⚡ {t('btn_scan_menu')}")
        self.btn_scan.setObjectName("btn_success")
        self.btn_scan.setToolTip(t("btn_scan_tooltip"))
        self.btn_scan.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.btn_scan.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_scan.clicked.connect(self.scan_current_page)

        self.scan_menu = QMenu(self.btn_scan)
        self.act_scan_dropdown_curr = self.scan_menu.addAction(t("btn_scan_current_opt"))
        self.act_scan_dropdown_curr.triggered.connect(self.scan_current_page)
        self.act_scan_dropdown_all = self.scan_menu.addAction(t("btn_scan_all_opt"))
        self.act_scan_dropdown_all.triggered.connect(self.scan_all_pages)
        self.btn_scan.setMenu(self.scan_menu)
        bar.addWidget(self.btn_scan)

        # 4. Save & Learn Button
        self.btn_learn = QPushButton(f"💾 {t('btn_learn_short')}")
        self.btn_learn.setToolTip(t("btn_learn_tooltip"))
        self.btn_learn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_learn.clicked.connect(self.learn_current_corrections)
        bar.addWidget(self.btn_learn)

        # 5. Stacked Export Dropdown Button
        self.btn_export = QToolButton()
        self.btn_export.setText(f"📄 {t('btn_export_menu')}")
        self.btn_export.setToolTip(t("btn_export_tooltip"))
        self.btn_export.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_export.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        self.export_menu = QMenu(self.btn_export)
        self.act_exp_dropdown_docx = self.export_menu.addAction(t("btn_export_word_opt"))
        self.act_exp_dropdown_docx.triggered.connect(self.export_to_docx_dialog)
        self.act_exp_dropdown_txt = self.export_menu.addAction(t("btn_export_txt_opt"))
        self.act_exp_dropdown_txt.triggered.connect(self.export_to_txt_dialog)
        self.btn_export.setMenu(self.export_menu)
        bar.addWidget(self.btn_export)

        # Spacer pushes utilities to right
        bar.addStretch()

        # 6. Unified Profile Dropdown (Stacked Selection + Management)
        self.btn_profile = QToolButton()
        self.btn_profile.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_profile.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.profile_menu = QMenu(self.btn_profile)
        self.btn_profile.setMenu(self.profile_menu)
        bar.addWidget(self.btn_profile)

        # 7. Memory Studio Button
        self.btn_dict = QPushButton(f"🧠 {t('btn_memory_short')}")
        self.btn_dict.setToolTip(t("btn_memory_tooltip"))
        self.btn_dict.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_dict.clicked.connect(self.open_dictionary_manager)
        bar.addWidget(self.btn_dict)

        # 8. Theme Toggle Button
        self.btn_theme = QPushButton("🌓")
        self.btn_theme.setToolTip(t("btn_theme_tooltip"))
        self.btn_theme.setFixedSize(28, 26)
        self.btn_theme.setStyleSheet("padding: 0px; font-size: 13px;")
        self.btn_theme.clicked.connect(self.toggle_theme)
        bar.addWidget(self.btn_theme)

        # 9. Language Pill Button
        self.btn_lang = QPushButton(t("btn_lang"))
        self.btn_lang.setToolTip(t("btn_lang_tooltip"))
        self.btn_lang.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_lang.clicked.connect(self.toggle_language)
        bar.addWidget(self.btn_lang)

        # 10. Compact About Button
        self.btn_about = QPushButton("ℹ")
        self.btn_about.setFixedSize(26, 26)
        self.btn_about.setStyleSheet("padding: 0px; font-size: 13px; font-weight: bold;")
        self.btn_about.setToolTip(t("btn_about_tooltip"))
        self.btn_about.clicked.connect(self.open_about_dialog)
        bar.addWidget(self.btn_about)

        parent_layout.addLayout(bar)

    def _create_sidebar(self) -> QWidget:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        hdr = QHBoxLayout()
        self.lbl_pages = QLabel(t("sidebar_title"))
        self.lbl_pages.setStyleSheet("font-weight: bold; color: #89b4fa; font-size: 12px;")
        hdr.addWidget(self.lbl_pages)
        hdr.addStretch()

        self.btn_add_page = QPushButton(t("btn_add_short"))
        self.btn_add_page.setStyleSheet("padding: 2px 8px; font-size: 11px; font-weight: bold;")
        self.btn_add_page.setToolTip(t("sidebar_add_tooltip"))
        self.btn_add_page.clicked.connect(self.attach_images_dialog)
        hdr.addWidget(self.btn_add_page)

        self.btn_remove_page = QPushButton(t("btn_del_short"))
        self.btn_remove_page.setStyleSheet("padding: 2px 8px; font-size: 11px;")
        self.btn_remove_page.setToolTip(t("sidebar_remove_tooltip"))
        self.btn_remove_page.clicked.connect(self.remove_selected_page)
        hdr.addWidget(self.btn_remove_page)
        layout.addLayout(hdr)

        self.list_pages = QListWidget()
        self.list_pages.currentRowChanged.connect(self.on_page_selected)
        layout.addWidget(self.list_pages)

        return frame

    def _create_viewer_panel(self) -> QWidget:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        v_bar = QHBoxLayout()
        v_bar.setSpacing(4)

        self.lbl_viewer = QLabel(t("viewer_title"))
        self.lbl_viewer.setStyleSheet("font-weight: bold; color: #a6adc8; font-size: 12px;")
        v_bar.addWidget(self.lbl_viewer)
        v_bar.addStretch()

        self.btn_cw = QPushButton("↻ 90°")
        self.btn_cw.setStyleSheet("padding: 3px 8px; font-size: 12px;")
        self.btn_cw.setToolTip(t("btn_cw_tooltip"))
        self.btn_cw.clicked.connect(self.rotate_image_cw)
        v_bar.addWidget(self.btn_cw)

        self.btn_ccw = QPushButton("↺ 90°")
        self.btn_ccw.setStyleSheet("padding: 3px 8px; font-size: 12px;")
        self.btn_ccw.setToolTip(t("btn_ccw_tooltip"))
        self.btn_ccw.clicked.connect(self.rotate_image_ccw)
        v_bar.addWidget(self.btn_ccw)

        self.btn_contrast = QPushButton(t("btn_contrast"))
        self.btn_contrast.setStyleSheet("padding: 3px 8px; font-size: 12px;")
        self.btn_contrast.setToolTip(t("btn_contrast_tooltip"))
        self.btn_contrast.clicked.connect(self.toggle_image_contrast)
        v_bar.addWidget(self.btn_contrast)

        self.btn_fit = QPushButton(t("btn_fit"))
        self.btn_fit.setStyleSheet("padding: 3px 8px; font-size: 12px;")
        self.btn_fit.setToolTip(t("btn_fit_tooltip"))
        self.btn_fit.clicked.connect(lambda: self.viewer.fit_to_window())
        v_bar.addWidget(self.btn_fit)

        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setStyleSheet("padding: 2px 8px; font-size: 13px; font-weight: bold;")
        self.btn_zoom_in.setToolTip(t("btn_zoom_in_tooltip"))
        self.btn_zoom_in.clicked.connect(lambda: self.viewer.zoom_in())
        v_bar.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("−")
        self.btn_zoom_out.setStyleSheet("padding: 2px 8px; font-size: 13px; font-weight: bold;")
        self.btn_zoom_out.setToolTip(t("btn_zoom_out_tooltip"))
        self.btn_zoom_out.clicked.connect(lambda: self.viewer.zoom_out())
        v_bar.addWidget(self.btn_zoom_out)

        layout.addLayout(v_bar)

        self.viewer = DocumentViewer()
        layout.addWidget(self.viewer)

        return frame

    def _create_editor_panel(self) -> QWidget:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        hdr = QHBoxLayout()
        self.lbl_editor = QLabel(t("editor_title"))
        self.lbl_editor.setStyleSheet("font-weight: bold; color: #89b4fa; font-size: 12px;")
        hdr.addWidget(self.lbl_editor)
        hdr.addStretch()

        self.lbl_learned_badge = QLabel("")
        self.lbl_learned_badge.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")
        hdr.addWidget(self.lbl_learned_badge)

        layout.addLayout(hdr)

        self.editor = HebrewTextEditor()
        self.editor.text_changed.connect(self.on_text_edited)
        layout.addWidget(self.editor)

        return frame

    def _create_status_bar(self, parent_layout):
        bar = QHBoxLayout()
        bar.setSpacing(10)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFixedWidth(280)
        bar.addWidget(self.progress_bar)

        self.lbl_status = QLabel(t("status_ready"))
        self.lbl_status.setStyleSheet("color: #a6adc8; font-size: 12px;")
        bar.addWidget(self.lbl_status)

        bar.addStretch()

        self.lbl_learned_counter = QLabel("")
        self.lbl_learned_counter.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 11px;")
        bar.addWidget(self.lbl_learned_counter)
        self.update_learned_count_badge()

        parent_layout.addLayout(bar)

    def toggle_language(self):
        I18nManager.instance().toggle_language()
        self._retranslate_ui()

    def _retranslate_ui(self):
        is_hebrew = (I18nManager.instance().current_lang == "he")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if is_hebrew else Qt.LayoutDirection.LeftToRight)

        self.setWindowTitle(t("app_title"))
        self.lbl_brand.setText(f"<b>{t('brand_name')}</b>")

        # Menu bar
        self.m_file.setTitle(t("menu_file"))
        self.act_file_add.setText(t("menu_file_add"))
        self.act_file_remove.setText(t("menu_file_remove"))
        self.act_file_clear.setText(t("menu_file_clear"))
        self.act_file_exp_word.setText(t("menu_file_export_word"))
        self.act_file_exp_txt.setText(t("menu_file_export_txt"))
        self.act_file_exit.setText(t("menu_file_exit"))

        self.m_scan.setTitle(t("menu_scan"))
        self.act_scan_curr.setText(t("menu_scan_current"))
        self.act_scan_all.setText(t("menu_scan_all"))
        self.act_scan_contrast.setText(t("menu_scan_enhance"))

        self.m_learn.setTitle(t("menu_learning"))
        self.act_learn_save.setText(t("menu_learning_save"))
        self.act_learn_studio.setText(t("menu_learning_studio"))
        self.act_learn_new_prof.setText(t("menu_learning_new_profile"))

        self.m_view.setTitle(t("menu_view"))
        self.act_view_cw.setText(t("menu_view_rotate_cw"))
        self.act_view_ccw.setText(t("menu_view_rotate_ccw"))
        self.act_view_zi.setText(t("menu_view_zoom_in"))
        self.act_view_zo.setText(t("menu_view_zoom_out"))
        self.act_view_fit.setText(t("menu_view_fit"))
        self.act_view_theme.setText(t("menu_view_theme"))

        self.m_lang.setTitle(t("menu_language"))
        self.act_lang_en.setText(t("menu_lang_en"))
        self.act_lang_he.setText(t("menu_lang_he"))

        self.m_help.setTitle(t("menu_help"))
        self.act_help_about.setText(t("menu_help_about"))

        # Action Toolbar
        self.btn_attach.setText(f"📁 {t('btn_add_pages_short')}")
        self.btn_attach.setToolTip(t("btn_attach_tooltip"))

        self.btn_scan.setText(f"⚡ {t('btn_scan_menu')}")
        self.btn_scan.setToolTip(t("btn_scan_tooltip"))
        self.act_scan_dropdown_curr.setText(t("btn_scan_current_opt"))
        self.act_scan_dropdown_all.setText(t("btn_scan_all_opt"))

        self.btn_learn.setText(f"💾 {t('btn_learn_short')}")
        self.btn_learn.setToolTip(t("btn_learn_tooltip"))

        self.btn_export.setText(f"📄 {t('btn_export_menu')}")
        self.btn_export.setToolTip(t("btn_export_tooltip"))
        self.act_exp_dropdown_docx.setText(t("btn_export_word_opt"))
        self.act_exp_dropdown_txt.setText(t("btn_export_txt_opt"))

        self.btn_dict.setText(f"🧠 {t('btn_memory_short')}")
        self.btn_dict.setToolTip(t("btn_memory_tooltip"))

        self.btn_theme.setToolTip(t("btn_theme_tooltip"))
        self.btn_lang.setText(t("btn_lang"))
        self.btn_lang.setToolTip(t("btn_lang_tooltip"))
        self.btn_about.setToolTip(t("btn_about_tooltip"))

        # Refresh dynamic profile dropdown text
        self._refresh_profiles_ui()

        # Sidebar
        self.lbl_pages.setText(t("sidebar_title"))
        self.btn_add_page.setText(t("btn_add_short"))
        self.btn_add_page.setToolTip(t("sidebar_add_tooltip"))
        self.btn_remove_page.setText(t("btn_del_short"))
        self.btn_remove_page.setToolTip(t("sidebar_remove_tooltip"))

        # Viewer
        self.lbl_viewer.setText(t("viewer_title"))
        self.btn_cw.setToolTip(t("btn_cw_tooltip"))
        self.btn_ccw.setToolTip(t("btn_ccw_tooltip"))
        self.btn_contrast.setText(t("btn_contrast"))
        self.btn_contrast.setToolTip(t("btn_contrast_tooltip"))
        self.btn_fit.setText(t("btn_fit"))
        self.btn_fit.setToolTip(t("btn_fit_tooltip"))
        self.btn_zoom_in.setToolTip(t("btn_zoom_in_tooltip"))
        self.btn_zoom_out.setToolTip(t("btn_zoom_out_tooltip"))

        # Editor
        self.lbl_editor.setText(t("editor_title"))
        self.editor.retranslate_ui()

        # Status
        self.lbl_status.setText(t("status_ready"))
        self.update_learned_count_badge()

    # --- Drag & Drop ---
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = []
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if os.path.isfile(p) and p.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp')):
                paths.append(p)
        if paths:
            self.add_images(paths)

    def attach_images_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, t("btn_attach"), "", "Images (*.jpg *.jpeg *.png *.webp *.tiff *.bmp)"
        )
        if files:
            self.add_images(files)

    def add_images(self, file_paths: List[str]):
        initial_count = len(self.pages)
        for path in file_paths:
            fname = os.path.basename(path)
            self.pages.append({
                "path": path,
                "filename": fname,
                "rotation": 0,
                "raw_text": "",
                "edited_text": "",
                "status": t("page_status_ready"),
                "lines_boxes": []
            })

            item = QListWidgetItem()
            item.setText(f"{fname}\n{t('page_status_ready')}")
            try:
                pix = QPixmap(path)
                if not pix.isNull():
                    thumb = pix.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    item.setIcon(QIcon(thumb))
            except Exception:
                pass
            self.list_pages.addItem(item)

        if initial_count == 0 and len(self.pages) > 0:
            self.list_pages.setCurrentRow(0)

        self.lbl_status.setText(f"{len(self.pages)} pages attached. Ready to scan.")

    def remove_selected_page(self):
        row = self.list_pages.currentRow()
        if row >= 0:
            del self.pages[row]
            self.list_pages.takeItem(row)
            if not self.pages:
                self.current_page_idx = -1
                self.editor.set_text("", "")
                self.viewer.scene.clear()
                self.lbl_status.setText(t("status_ready"))

    def clear_all_pages(self):
        if not self.pages:
            return
        res = QMessageBox.question(
            self, "Clear All Pages", "Are you sure you want to remove all attached pages from this session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if res == QMessageBox.StandardButton.Yes:
            self.pages.clear()
            self.list_pages.clear()
            self.current_page_idx = -1
            self.viewer.scene.clear()
            self.editor.set_text("", "")
            self.lbl_status.setText(t("status_ready"))

    def on_page_selected(self, row: int):
        if row < 0 or row >= len(self.pages):
            return

        # Save previous edits before switching
        if self.current_page_idx >= 0 and self.current_page_idx < len(self.pages):
            self.pages[self.current_page_idx]["edited_text"] = self.editor.get_text()

        self.current_page_idx = row
        pdata = self.pages[row]

        # Load image into viewer
        try:
            pil_img = Image.open(pdata["path"])
            self.viewer.load_image(pil_img, rotation=pdata["rotation"])
        except Exception as e:
            self.lbl_status.setText(f"Error loading image: {e}")

        # Load text into editor
        self.editor.set_text(pdata["edited_text"], pdata["raw_text"])

    def on_text_edited(self):
        if self.current_page_idx >= 0 and self.current_page_idx < len(self.pages):
            self.pages[self.current_page_idx]["edited_text"] = self.editor.get_text()

    def rotate_image_cw(self):
        if self.current_page_idx >= 0 and self.current_page_idx < len(self.pages):
            p = self.pages[self.current_page_idx]
            p["rotation"] = (p["rotation"] + 90) % 360
            self.viewer.rotate_cw()

    def rotate_image_ccw(self):
        if self.current_page_idx >= 0 and self.current_page_idx < len(self.pages):
            p = self.pages[self.current_page_idx]
            p["rotation"] = (p["rotation"] - 90) % 360
            self.viewer.rotate_ccw()

    def toggle_image_contrast(self):
        self.viewer.toggle_contrast()

    # --- OCR Execution ---
    def scan_current_page(self):
        if self.current_page_idx < 0 or self.current_page_idx >= len(self.pages):
            QMessageBox.information(self, "Notice", "Please attach and select an image to scan first.")
            return

        pdata = self.pages[self.current_page_idx]
        self.btn_scan.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(f"Scanning page {self.current_page_idx + 1}...")

        self.active_worker = OCRWorker(
            self.ocr_engine, self.learning_engine, pdata["path"], pdata["rotation"]
        )
        self.active_worker.progress.connect(self._on_ocr_progress)
        self.active_worker.finished.connect(lambda res: self._on_ocr_finished(self.current_page_idx, res))
        self.active_worker.error.connect(self._on_ocr_error)
        self.active_worker.start()

    def _on_ocr_progress(self, cur, tot, msg):
        pct = int((cur / max(1, tot)) * 100)
        self.progress_bar.setValue(pct)
        self.lbl_status.setText(f"{msg} ({cur}/{tot})")

    def _on_ocr_finished(self, page_idx: int, res: dict):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)

        if 0 <= page_idx < len(self.pages):
            p = self.pages[page_idx]
            p["raw_text"] = res["raw_text"]
            p["edited_text"] = res["text"]
            p["status"] = t("page_status_scanned")
            p["lines_boxes"] = res["lines"]

            item = self.list_pages.item(page_idx)
            if item:
                item.setText(f"{p['filename']}\n{t('page_status_scanned')}")

            if page_idx == self.current_page_idx:
                self.editor.set_text(res["text"], res["raw_text"])
                if res["corrections_applied"] > 0:
                    self.lbl_learned_badge.setText(f"Applied {res['corrections_applied']} automatic learned corrections ✓")

            self.lbl_status.setText(f"Page {page_idx + 1} scanned successfully ({len(res['lines'])} lines, applied {res['corrections_applied']} learned rules)!")

    def _on_ocr_error(self, err_msg: str):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        QMessageBox.critical(self, "OCR Error", f"An error occurred during OCR recognition:\n{err_msg}")
        self.lbl_status.setText("Scan failed.")

    def scan_all_pages(self):
        if not self.pages:
            QMessageBox.information(self, "Notice", "Please attach images to scan first.")
            return

        for i, p in enumerate(self.pages):
            if p["status"] != t("page_status_scanned"):
                self.list_pages.setCurrentRow(i)
                self.scan_current_page()
                return
        QMessageBox.information(self, "Complete", "All pages in notebook have already been scanned!")

    def learn_current_corrections(self):
        if self.current_page_idx < 0 or self.current_page_idx >= len(self.pages):
            return

        pdata = self.pages[self.current_page_idx]
        cur_text = self.editor.get_text()
        raw_text = pdata.get("raw_text", "")

        if not raw_text:
            QMessageBox.information(self, "Notice", "This page has not been scanned yet, or no edits were made.")
            return

        learned = self.learning_engine.learn_from_corrections(raw_text, cur_text, pdata["filename"])
        self.update_learned_count_badge()

        if learned:
            ex_str = ""
            for raw, corr in learned[:5]:
                ex_str += f" • '{raw}' ➔ '{corr}'\n"
            if len(learned) > 5:
                ex_str += f"... and {len(learned) - 5} more corrections.\n"

            msg = t(
                "learn_success_msg",
                count=len(learned),
                profile=self.learning_engine.get_active_profile_name(),
                examples=ex_str
            )
            QMessageBox.information(self, t("learn_success_title"), msg)
        else:
            QMessageBox.information(self, t("learn_none_title"), t("learn_none_msg"))

    def _refresh_profiles_ui(self):
        profiles = self.learning_engine.list_profiles()
        active_pid = self.learning_engine.get_active_profile_id()
        active_pname = self.learning_engine.get_active_profile_name()
        active_count = 0

        self.profile_menu.clear()

        for p in profiles:
            is_active = (p["id"] == active_pid)
            if is_active:
                active_count = p["rule_count"]
            prefix = "✓ " if is_active else "   "
            act = self.profile_menu.addAction(f"{prefix}{p['name']} ({p['rule_count']} rules)")
            act.triggered.connect(lambda checked, pid=p["id"]: self._switch_profile(pid))

        self.profile_menu.addSeparator()

        act_new = self.profile_menu.addAction("➕ " + t("dict_btn_new_prof"))
        act_new.triggered.connect(self._quick_new_profile)

        act_studio = self.profile_menu.addAction("🧠 " + t("btn_memory_tooltip"))
        act_studio.triggered.connect(self.open_dictionary_manager)

        display_name = active_pname
        if len(display_name) > 16:
            display_name = display_name[:14] + "…"
        self.btn_profile.setText(f"👤 {display_name} ({active_count}) ▾")
        self.btn_profile.setToolTip(f"Active Handwriting Profile: {active_pname}\nClick to switch writer or manage rules.")

    def _switch_profile(self, pid: str):
        if pid != self.learning_engine.get_active_profile_id():
            self.learning_engine.set_active_profile(pid)
            self._refresh_profiles_ui()
            self.update_learned_count_badge()
            self.lbl_status.setText(t("status_switched_profile", name=self.learning_engine.get_active_profile_name()))

    def _quick_new_profile(self):
        name, ok = QInputDialog.getText(self, t("btn_new_profile_tooltip"), "Enter new profile name:")
        if ok and name.strip():
            try:
                pid = self.learning_engine.create_profile(name.strip())
                self.learning_engine.set_active_profile(pid)
                self._refresh_profiles_ui()
                self.update_learned_count_badge()
                self.lbl_status.setText(t("status_created_profile", name=name.strip()))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create profile: {str(e)}")

    def update_learned_count_badge(self):
        rules = self.learning_engine.get_all_replacements(active_only=True)
        enabled_count = len(self.learning_engine.get_enabled_profile_ids())
        stack_info = t("status_stack_info", count=enabled_count) if enabled_count > 1 else ""
        self.lbl_learned_counter.setText(
            t("status_active_rules", count=len(rules), profile=self.learning_engine.get_active_profile_name(), stack_info=stack_info)
        )

    def export_to_docx_dialog(self):
        if not self.pages:
            QMessageBox.information(self, "Notice", "Please attach and edit pages before exporting.")
            return

        title, ok1 = QInputDialog.getText(self, t("export_dialog_title"), t("export_title_prompt"), text=t("export_default_title"))
        if not ok1:
            return
        subtitle, ok2 = QInputDialog.getText(self, t("export_dialog_title"), t("export_subtitle_prompt"), text="")
        if not ok2:
            return
        author, ok3 = QInputDialog.getText(self, t("export_dialog_title"), t("export_author_prompt"), text="")
        if not ok3:
            return

        # Choose destination file
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).strip() or "Notes"
        docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
        default_file = os.path.join(docs_dir, f"{safe_title}.docx")
        out_path, _ = QFileDialog.getSaveFileName(self, t("export_dialog_title"), default_file, t("export_filter"))
        if not out_path:
            return

        pages_to_export = []
        for i, p in enumerate(self.pages):
            text = p["edited_text"].strip() if p["edited_text"] else p["raw_text"].strip()
            if text:
                pages_to_export.append({
                    "page_num": i + 1,
                    "title": f"עמוד {i + 1} ({p['filename']})",
                    "text": text
                })

        if not pages_to_export:
            QMessageBox.warning(self, "Notice", "No text has been recognized or transcribed yet.")
            return

        try:
            author_formatted = f"הערות וחידושים מאת {author}" if author else ""
            export_notes_to_docx(
                pages_to_export,
                out_path,
                document_title=title,
                document_subtitle=subtitle,
                author_name=author_formatted,
                font_name="David"
            )
            resp = QMessageBox.question(
                self, t("export_success_title"),
                t("export_success_msg", path=out_path),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if resp == QMessageBox.StandardButton.Yes:
                os.startfile(out_path)
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error saving document:\n{str(e)}")

    def export_to_txt_dialog(self):
        if not self.pages:
            QMessageBox.information(self, "Notice", "Please attach and edit pages before exporting.")
            return

        docs_dir = os.path.join(os.path.expanduser("~"), "Documents")
        default_file = os.path.join(docs_dir, "TorahNotes_Export.txt")
        out_path, _ = QFileDialog.getSaveFileName(self, t("btn_export_txt_opt"), default_file, "Text Files (*.txt);;All Files (*)")
        if not out_path:
            return

        pages_to_export = []
        for i, p in enumerate(self.pages):
            text = p["edited_text"].strip() if p["edited_text"] else p["raw_text"].strip()
            if text:
                pages_to_export.append(f"--- Page {i + 1}: {p['filename']} ---\n{text}\n")

        if not pages_to_export:
            QMessageBox.warning(self, "Notice", "No text has been recognized or transcribed yet.")
            return

        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("\n".join(pages_to_export))
            QMessageBox.information(self, "Export Successful!", f"Document saved successfully to:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Error saving text document:\n{str(e)}")

    def open_dictionary_manager(self):
        dlg = DictionaryManagerDialog(self.learning_engine, self)
        dlg.exec()
        self._refresh_profiles_ui()
        self.update_learned_count_badge()

    def open_about_dialog(self):
        dlg = AboutDialog(self)
        dlg.exec()

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_theme:
            self.setStyleSheet(DARK_THEME)
            self.btn_theme.setText("☀")
        else:
            self.setStyleSheet(LIGHT_THEME)
            self.btn_theme.setText("🌙")
