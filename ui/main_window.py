# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Main Application Window
Modern, sleek, side-by-side OCR & handwriting transcription studio.
Supports English (default) and Hebrew UI localization with dynamic runtime switching.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from PIL import Image

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QListWidget, QListWidgetItem, QPushButton, 
    QLabel, QProgressBar, QFileDialog, QMessageBox, 
    QToolBar, QStatusBar, QFrame, QInputDialog, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction

from ui.image_viewer import DocumentViewer
from ui.text_editor import HebrewTextEditor
from ui.dictionary_dialog import DictionaryManagerDialog
from ui.about_dialog import AboutDialog
from ui.theme import DARK_THEME, LIGHT_THEME
from ui.i18n import t, I18nManager
from core.ocr_engine import OCREngine
from core.learning_engine import LearningEngine
from core.docx_exporter import export_notes_to_docx


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
        self.resize(1280, 820)
        self.setMinimumSize(960, 640)

        # Set Window Icon
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, "assets", "ksav_kooker.png")
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
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        # 1. Top Header Toolbar
        self._create_top_toolbar(main_layout)

        # 2. Main Content Splitter (Thumbnails | Image Viewer | Text Editor)
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        content_splitter.setChildrenCollapsible(False)

        # Left / Sidebar: Page Thumbnails List
        sidebar_frame = self._create_sidebar()
        content_splitter.addWidget(sidebar_frame)

        # Center: Document Image Viewer + controls
        viewer_frame = self._create_viewer_panel()
        content_splitter.addWidget(viewer_frame)

        # Right: Hebrew RTL Text Editor
        editor_frame = self._create_editor_panel()
        content_splitter.addWidget(editor_frame)

        # Set default split sizes (220px sidebar, 560px viewer, 570px editor)
        content_splitter.setSizes([220, 560, 570])
        main_layout.addWidget(content_splitter, 1)

        # 3. Bottom Progress & Status Bar
        self._create_status_bar(main_layout)

    def _create_top_toolbar(self, parent_layout):
        bar = QHBoxLayout()
        bar.setSpacing(8)

        # App Brand
        self.lbl_brand = QLabel(t("brand_name"))
        self.lbl_brand.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa; padding-right: 8px;")
        bar.addWidget(self.lbl_brand)

        # Attach Images Button
        self.btn_attach = QPushButton(t("btn_attach"))
        self.btn_attach.setObjectName("btn_primary")
        self.btn_attach.setToolTip(t("btn_attach_tooltip"))
        self.btn_attach.clicked.connect(self.attach_images_dialog)
        bar.addWidget(self.btn_attach)

        # Scan Current Page Button
        self.btn_scan = QPushButton(t("btn_scan"))
        self.btn_scan.setObjectName("btn_success")
        self.btn_scan.setToolTip(t("btn_scan_tooltip"))
        self.btn_scan.clicked.connect(self.scan_current_page)
        bar.addWidget(self.btn_scan)

        # Scan All Pages Button
        self.btn_scan_all = QPushButton(t("btn_scan_all"))
        self.btn_scan_all.setToolTip(t("btn_scan_all_tooltip"))
        self.btn_scan_all.clicked.connect(self.scan_all_pages)
        bar.addWidget(self.btn_scan_all)

        # Save & Learn Corrections
        self.btn_learn = QPushButton(t("btn_learn"))
        self.btn_learn.setToolTip(t("btn_learn_tooltip"))
        self.btn_learn.clicked.connect(self.learn_current_corrections)
        bar.addWidget(self.btn_learn)

        # Export to Word (.docx)
        self.btn_export = QPushButton(t("btn_export"))
        self.btn_export.setToolTip(t("btn_export_tooltip"))
        self.btn_export.clicked.connect(self.export_to_docx_dialog)
        bar.addWidget(self.btn_export)

        bar.addStretch()

        # Profile Selector
        self.lbl_prof = QLabel(t("lbl_profile"))
        self.lbl_prof.setStyleSheet("color: #a6adc8; font-weight: bold;")
        bar.addWidget(self.lbl_prof)

        self.combo_profile = QComboBox()
        self.combo_profile.setToolTip(t("profile_tooltip"))
        self.combo_profile.setMinimumWidth(160)
        self.combo_profile.currentIndexChanged.connect(self._on_profile_combo_changed)
        bar.addWidget(self.combo_profile)

        self.btn_new_prof_quick = QPushButton("+")
        self.btn_new_prof_quick.setToolTip(t("btn_new_profile_tooltip"))
        self.btn_new_prof_quick.setMaximumWidth(28)
        self.btn_new_prof_quick.clicked.connect(self._quick_new_profile)
        bar.addWidget(self.btn_new_prof_quick)

        # Learned Rules & Profile Manager
        self.btn_dict = QPushButton(t("btn_memory"))
        self.btn_dict.setToolTip(t("btn_memory_tooltip"))
        self.btn_dict.clicked.connect(self.open_dictionary_manager)
        bar.addWidget(self.btn_dict)

        # Theme toggle
        self.btn_theme = QPushButton("🌓")
        self.btn_theme.setToolTip(t("btn_theme_tooltip"))
        self.btn_theme.clicked.connect(self.toggle_theme)
        bar.addWidget(self.btn_theme)

        # Language toggle
        self.btn_lang = QPushButton(t("btn_lang"))
        self.btn_lang.setToolTip(t("btn_lang_tooltip"))
        self.btn_lang.clicked.connect(self.toggle_language)
        bar.addWidget(self.btn_lang)

        # About
        self.btn_about = QPushButton(t("btn_about"))
        self.btn_about.setToolTip(t("btn_about_tooltip"))
        self.btn_about.clicked.connect(self.open_about_dialog)
        bar.addWidget(self.btn_about)

        parent_layout.addLayout(bar)

    def _create_sidebar(self) -> QWidget:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        hdr = QHBoxLayout()
        self.lbl_pages = QLabel(t("sidebar_title"))
        self.lbl_pages.setStyleSheet("font-weight: bold; color: #89b4fa;")
        hdr.addWidget(self.lbl_pages)
        hdr.addStretch()

        self.btn_add_page = QPushButton("+")
        self.btn_add_page.setFixedSize(26, 26)
        self.btn_add_page.setToolTip(t("sidebar_add_tooltip"))
        self.btn_add_page.clicked.connect(self.attach_images_dialog)
        hdr.addWidget(self.btn_add_page)

        self.btn_remove_page = QPushButton("−")
        self.btn_remove_page.setFixedSize(26, 26)
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

        # Viewer mini-toolbar
        v_bar = QHBoxLayout()
        v_bar.setSpacing(4)

        self.lbl_viewer = QLabel(t("viewer_title"))
        self.lbl_viewer.setStyleSheet("font-weight: bold; color: #a6adc8; font-size: 11px;")
        v_bar.addWidget(self.lbl_viewer)

        self.btn_cw = QPushButton("↻ 90°")
        self.btn_cw.setToolTip(t("btn_cw_tooltip"))
        self.btn_cw.clicked.connect(self.rotate_image_cw)
        v_bar.addWidget(self.btn_cw)

        self.btn_ccw = QPushButton("↺ 90°")
        self.btn_ccw.setToolTip(t("btn_ccw_tooltip"))
        self.btn_ccw.clicked.connect(self.rotate_image_ccw)
        v_bar.addWidget(self.btn_ccw)

        self.btn_contrast = QPushButton(t("btn_contrast"))
        self.btn_contrast.setToolTip(t("btn_contrast_tooltip"))
        self.btn_contrast.clicked.connect(self.toggle_image_contrast)
        v_bar.addWidget(self.btn_contrast)

        self.btn_fit = QPushButton(t("btn_fit"))
        self.btn_fit.setToolTip(t("btn_fit_tooltip"))
        self.btn_fit.clicked.connect(lambda: self.viewer.fit_to_window())
        v_bar.addWidget(self.btn_fit)

        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setToolTip(t("btn_zoom_in_tooltip"))
        self.btn_zoom_in.setFixedSize(26, 24)
        self.btn_zoom_in.clicked.connect(lambda: self.viewer.zoom_in())
        v_bar.addWidget(self.btn_zoom_in)

        self.btn_zoom_out = QPushButton("−")
        self.btn_zoom_out.setToolTip(t("btn_zoom_out_tooltip"))
        self.btn_zoom_out.setFixedSize(26, 24)
        self.btn_zoom_out.clicked.connect(lambda: self.viewer.zoom_out())
        v_bar.addWidget(self.btn_zoom_out)

        v_bar.addStretch()
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
        self.lbl_editor.setStyleSheet("font-weight: bold; color: #89b4fa;")
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
        self.lbl_brand.setText(t("brand_name"))
        self.btn_attach.setText(t("btn_attach"))
        self.btn_attach.setToolTip(t("btn_attach_tooltip"))
        self.btn_scan.setText(t("btn_scan"))
        self.btn_scan.setToolTip(t("btn_scan_tooltip"))
        self.btn_scan_all.setText(t("btn_scan_all"))
        self.btn_scan_all.setToolTip(t("btn_scan_all_tooltip"))
        self.btn_learn.setText(t("btn_learn"))
        self.btn_learn.setToolTip(t("btn_learn_tooltip"))
        self.btn_export.setText(t("btn_export"))
        self.btn_export.setToolTip(t("btn_export_tooltip"))
        self.lbl_prof.setText(t("lbl_profile"))
        self.combo_profile.setToolTip(t("profile_tooltip"))
        self.btn_new_prof_quick.setToolTip(t("btn_new_profile_tooltip"))
        self.btn_dict.setText(t("btn_memory"))
        self.btn_dict.setToolTip(t("btn_memory_tooltip"))
        self.btn_theme.setToolTip(t("btn_theme_tooltip"))
        self.btn_lang.setText(t("btn_lang"))
        self.btn_lang.setToolTip(t("btn_lang_tooltip"))
        self.btn_about.setText(t("btn_about"))
        self.btn_about.setToolTip(t("btn_about_tooltip"))

        # Sidebar
        self.lbl_pages.setText(t("sidebar_title"))
        self.btn_add_page.setToolTip(t("sidebar_add_tooltip"))
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
        self.btn_scan_all.setEnabled(False)
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
        self.btn_scan_all.setEnabled(True)

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
        self.btn_scan_all.setEnabled(True)
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
        self.combo_profile.blockSignals(True)
        self.combo_profile.clear()
        profiles = self.learning_engine.list_profiles()
        active_pid = self.learning_engine.get_active_profile_id()
        selected_idx = 0
        for idx, p in enumerate(profiles):
            self.combo_profile.addItem(f"{p['name']} ({p['rule_count']})", p["id"])
            if p["id"] == active_pid:
                selected_idx = idx
        self.combo_profile.setCurrentIndex(selected_idx)
        self.combo_profile.blockSignals(False)

    def _on_profile_combo_changed(self, index):
        if index < 0:
            return
        pid = self.combo_profile.currentData()
        if pid and pid != self.learning_engine.get_active_profile_id():
            self.learning_engine.set_active_profile(pid)
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
