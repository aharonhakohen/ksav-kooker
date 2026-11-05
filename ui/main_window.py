# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Main Application Window
Modern, sleek, side-by-side OCR & handwriting transcription studio.
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
            img = Image.open(self.image_path)
            if self.rotation % 360 != 0:
                img = img.rotate(-self.rotation, expand=True)

            res = self.ocr_engine.recognize_page(
                img,
                learning_engine=self.learning_engine,
                progress_callback=lambda cur, tot, msg: self.progress.emit(cur, tot, msg)
            )
            self.finished.emit(res)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("כתב קוקער | Ksav Kooker — Offline Torah Notes OCR Studio (v1.0.0)")
        self.resize(1350, 850)
        self.setAcceptDrops(True)

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

        # Set default split sizes (220px sidebar, 550px viewer, 580px editor)
        content_splitter.setSizes([220, 560, 570])
        main_layout.addWidget(content_splitter, 1)

        # 3. Bottom Progress & Status Bar
        self._create_status_bar(main_layout)

    def _create_top_toolbar(self, parent_layout):
        bar = QHBoxLayout()
        bar.setSpacing(8)

        # App Brand
        lbl_brand = QLabel("כתב קוקער 📖")
        lbl_brand.setStyleSheet("font-size: 18px; font-weight: bold; color: #89b4fa; padding-right: 8px;")
        bar.addWidget(lbl_brand)

        # Attach Images Button
        self.btn_attach = QPushButton("📁 צרף תמונות")
        self.btn_attach.setObjectName("btn_primary")
        self.btn_attach.setToolTip("צרף תמונה אחת או מספר תמונות של מחברת השיעורים (ניתן גם לגרור לכאן)")
        self.btn_attach.clicked.connect(self.attach_images_dialog)
        bar.addWidget(self.btn_attach)

        # Scan Current Page Button
        self.btn_scan = QPushButton("⚡ סרוק עמוד נוכחי")
        self.btn_scan.setObjectName("btn_success")
        self.btn_scan.setToolTip("הפעל זיהוי כתב יד OCR אופליין עבור העמוד הנוכחי")
        self.btn_scan.clicked.connect(self.scan_current_page)
        bar.addWidget(self.btn_scan)

        # Scan All Pages Button
        self.btn_scan_all = QPushButton("⚡⚡ סרוק הכל")
        self.btn_scan_all.setToolTip("סרוק ברצף את כל העמודים שצורפו")
        self.btn_scan_all.clicked.connect(self.scan_all_pages)
        bar.addWidget(self.btn_scan_all)

        # Save & Learn Corrections
        self.btn_learn = QPushButton("💾 שמור ולמד תיקונים")
        self.btn_learn.setToolTip("שומר את העריכה ורושם בזיכרון את כל המילים שתוקנו כדי לתקן אותן אוטומטית בעתיד")
        self.btn_learn.clicked.connect(self.learn_current_corrections)
        bar.addWidget(self.btn_learn)

        # Export to Word (.docx)
        self.btn_export = QPushButton("📝 ייצוא לוורד (.docx)")
        self.btn_export.setToolTip("ייצא את כל העמודים למסמך Word מעוצב מימין לשמאל בגופן דוד")
        self.btn_export.clicked.connect(self.export_to_docx_dialog)
        bar.addWidget(self.btn_export)

        bar.addStretch()

        # Profile Selector
        lbl_prof = QLabel("👤 כתב יד:")
        lbl_prof.setStyleSheet("color: #a6adc8; font-weight: bold;")
        bar.addWidget(lbl_prof)

        self.combo_profile = QComboBox()
        self.combo_profile.setToolTip("פרופיל כתב היד הפעיל (בחר להחלפה בין כותבים/תלמידים שונים)")
        self.combo_profile.setMinimumWidth(160)
        self.combo_profile.currentIndexChanged.connect(self._on_profile_combo_changed)
        bar.addWidget(self.combo_profile)

        btn_new_prof_quick = QPushButton("+")
        btn_new_prof_quick.setToolTip("יצירת פרופיל כתב יד חדש")
        btn_new_prof_quick.setMaximumWidth(28)
        btn_new_prof_quick.clicked.connect(self._quick_new_profile)
        bar.addWidget(btn_new_prof_quick)

        # Learned Rules & Profile Manager
        btn_dict = QPushButton("🧠 מנהל הזיכרון")
        btn_dict.setToolTip("פתח את מנהל הזיכרון, הפרופילים, הגיבוי והשחזור")
        btn_dict.clicked.connect(self.open_dictionary_manager)
        bar.addWidget(btn_dict)

        # Theme toggle
        self.btn_theme = QPushButton("🌓")
        self.btn_theme.setToolTip("החלף בין ערכת נושא כהה לבהירה")
        self.btn_theme.clicked.connect(self.toggle_theme)
        bar.addWidget(self.btn_theme)

        # About
        btn_about = QPushButton("ℹ אודות")
        btn_about.clicked.connect(self.open_about_dialog)
        bar.addWidget(btn_about)

        parent_layout.addLayout(bar)

    def _create_sidebar(self) -> QWidget:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        hdr = QHBoxLayout()
        lbl_pages = QLabel("עמודי המחברת")
        lbl_pages.setStyleSheet("font-weight: bold; color: #89b4fa;")
        hdr.addWidget(lbl_pages)
        hdr.addStretch()

        btn_add = QPushButton("+")
        btn_add.setFixedSize(26, 26)
        btn_add.setToolTip("הוסף עמודים")
        btn_add.clicked.connect(self.attach_images_dialog)
        hdr.addWidget(btn_add)

        btn_remove = QPushButton("−")
        btn_remove.setFixedSize(26, 26)
        btn_remove.setToolTip("הסר עמוד נבחר")
        btn_remove.clicked.connect(self.remove_selected_page)
        hdr.addWidget(btn_remove)
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

        lbl_v = QLabel("תצלום הדף")
        lbl_v.setStyleSheet("font-weight: bold; color: #a6adc8; font-size: 11px;")
        v_bar.addWidget(lbl_v)

        btn_cw = QPushButton("↻ 90°")
        btn_cw.setToolTip("סובב ימינה עם כיוון השעון")
        btn_cw.clicked.connect(self.rotate_image_cw)
        v_bar.addWidget(btn_cw)

        btn_ccw = QPushButton("↺ 90°")
        btn_ccw.setToolTip("סובב שמאלה נגד כיוון השעון")
        btn_ccw.clicked.connect(self.rotate_image_ccw)
        v_bar.addWidget(btn_ccw)

        btn_contrast = QPushButton("◐ הדגש דיו")
        btn_contrast.setToolTip("הגבר ניגודיות עבור עפרון או עט בהיר")
        btn_contrast.clicked.connect(self.toggle_image_contrast)
        v_bar.addWidget(btn_contrast)

        btn_fit = QPushButton("⛶ התאם")
        btn_fit.setToolTip("התאם גודל לחלון")
        btn_fit.clicked.connect(lambda: self.viewer.fit_to_window())
        v_bar.addWidget(btn_fit)

        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setFixedSize(26, 24)
        btn_zoom_in.clicked.connect(lambda: self.viewer.zoom_in())
        v_bar.addWidget(btn_zoom_in)

        btn_zoom_out = QPushButton("−")
        btn_zoom_out.setFixedSize(26, 24)
        btn_zoom_out.clicked.connect(lambda: self.viewer.zoom_out())
        v_bar.addWidget(btn_zoom_out)

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
        lbl_e = QLabel("תמליל ועריכה (מימין לשמאל)")
        lbl_e.setStyleSheet("font-weight: bold; color: #89b4fa;")
        hdr.addWidget(lbl_e)
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

        self.lbl_status = QLabel("מוכן לפעולה. גרור או צרף תמונות של מחברת השיעורים.")
        self.lbl_status.setStyleSheet("color: #a6adc8; font-size: 12px;")
        bar.addWidget(self.lbl_status)

        bar.addStretch()

        self.lbl_learned_counter = QLabel("כללים נלמדים פעילים: 0")
        self.lbl_learned_counter.setStyleSheet("color: #89b4fa; font-weight: bold; font-size: 11px;")
        bar.addWidget(self.lbl_learned_counter)
        self.update_learned_count_badge()

        parent_layout.addLayout(bar)

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

    # --- Actions ---
    def attach_images_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "בחירת תמונות שיעורים", "",
            "Images (*.jpg *.jpeg *.png *.webp *.tiff *.bmp)"
        )
        if files:
            self.add_images(files)

    def add_images(self, file_paths: List[str]):
        start_idx = len(self.pages)
        for p in file_paths:
            fname = os.path.basename(p)
            page_data = {
                "path": p,
                "filename": fname,
                "rotation": 0,
                "raw_text": "",
                "text": "",
                "boxes": [],
                "status": "טרם נסרק",
                "corrections_applied": 0
            }
            self.pages.append(page_data)

            item = QListWidgetItem(f"עמוד {len(self.pages)}: {fname}\n[טרם נסרק]")
            self.list_pages.addItem(item)

        if self.current_page_idx == -1 and self.pages:
            self.list_pages.setCurrentRow(0)

        self.lbl_status.setText(f"נוספו {len(file_paths)} עמודים למחברת.")

    def remove_selected_page(self):
        row = self.list_pages.currentRow()
        if 0 <= row < len(self.pages):
            self.pages.pop(row)
            self.list_pages.takeItem(row)
            # Re-label items
            for i in range(self.list_pages.count()):
                self.list_pages.item(i).setText(f"עמוד {i+1}: {self.pages[i]['filename']}\n[{self.pages[i]['status']}]")
            if not self.pages:
                self.current_page_idx = -1
                self.editor.set_text("", "")
                self.viewer.scene.clear()

    def on_page_selected(self, row: int):
        if row < 0 or row >= len(self.pages):
            return

        # Save previous page text if changed
        if 0 <= self.current_page_idx < len(self.pages):
            self.pages[self.current_page_idx]["text"] = self.editor.get_text()

        self.current_page_idx = row
        pdata = self.pages[row]

        # Load image into viewer
        try:
            pil_img = Image.open(pdata["path"])
            self.viewer.load_image(pil_img, rotation=pdata["rotation"])
            if pdata.get("boxes"):
                self.viewer.set_bounding_boxes(pdata["boxes"])
        except Exception as e:
            QMessageBox.warning(self, "שגיאה בטעינת תמונה", str(e))

        # Load text into editor
        self.editor.set_text(pdata["text"], pdata["raw_text"])
        if pdata.get("corrections_applied", 0) > 0:
            self.lbl_learned_badge.setText(f"הוחלו {pdata['corrections_applied']} כללי תיקון אוטומטיים ✓")
        else:
            self.lbl_learned_badge.setText("")

    def on_text_edited(self):
        if 0 <= self.current_page_idx < len(self.pages):
            self.pages[self.current_page_idx]["text"] = self.editor.get_text()

    def rotate_image_cw(self):
        if 0 <= self.current_page_idx < len(self.pages):
            self.pages[self.current_page_idx]["rotation"] = (self.pages[self.current_page_idx]["rotation"] + 90) % 360
            self.viewer.rotate_cw()

    def rotate_image_ccw(self):
        if 0 <= self.current_page_idx < len(self.pages):
            self.pages[self.current_page_idx]["rotation"] = (self.pages[self.current_page_idx]["rotation"] - 90) % 360
            self.viewer.rotate_ccw()

    def toggle_image_contrast(self):
        active = self.viewer.toggle_contrast()
        self.lbl_status.setText("מצב הדגשת דיו / עפרון: " + ("מופעל ✓" if active else "כבוי"))

    def scan_current_page(self):
        if self.current_page_idx < 0 or self.current_page_idx >= len(self.pages):
            QMessageBox.information(self, "אין עמוד נבחר", "אנא צרף ובחר עמוד לסריקה.")
            return

        pdata = self.pages[self.current_page_idx]
        self._start_ocr_worker(pdata, self.current_page_idx)

    def _start_ocr_worker(self, pdata, page_idx):
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(5)
        self.lbl_status.setText(f"מפעיל מנוע זיהוי כתב יד אופליין עבור עמוד {page_idx + 1}...")
        self.btn_scan.setEnabled(False)
        self.btn_scan_all.setEnabled(False)

        self.active_worker = OCRWorker(
            self.ocr_engine,
            self.learning_engine,
            pdata["path"],
            rotation=pdata["rotation"]
        )
        self.active_worker.progress.connect(self._on_ocr_progress)
        self.active_worker.finished.connect(lambda res, idx=page_idx: self._on_ocr_finished(res, idx))
        self.active_worker.error.connect(self._on_ocr_error)
        self.active_worker.start()

    def _on_ocr_progress(self, cur, tot, msg):
        self.progress_bar.setValue(cur)
        self.lbl_status.setText(msg)

    def _on_ocr_finished(self, res: dict, page_idx: int):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.btn_scan_all.setEnabled(True)

        if 0 <= page_idx < len(self.pages):
            pdata = self.pages[page_idx]
            pdata["raw_text"] = "\n".join(l["raw_text"] for l in res["lines"])
            pdata["text"] = res["full_text"]
            pdata["boxes"] = [l["box"] for l in res["lines"] if l.get("box")]
            pdata["status"] = "נסרק בהצלחה ✓"
            pdata["corrections_applied"] = res["corrections_applied"]

            # Update list item text
            self.list_pages.item(page_idx).setText(f"עמוד {page_idx + 1}: {pdata['filename']}\n[הושלם ✓]")

            # If current view is this page, refresh editor & bounding boxes
            if self.current_page_idx == page_idx:
                self.editor.set_text(pdata["text"], pdata["raw_text"])
                self.viewer.set_bounding_boxes(pdata["boxes"])
                if res["corrections_applied"] > 0:
                    self.lbl_learned_badge.setText(f"הוחלו {res['corrections_applied']} כללי תיקון אוטומטיים ✓")

            self.lbl_status.setText(f"עמוד {page_idx + 1} נסרק בהצלחה ({len(res['lines'])} שורות, הוחלו {res['corrections_applied']} כללים נלמדים)!")

    def _on_ocr_error(self, err_msg: str):
        self.progress_bar.setVisible(False)
        self.btn_scan.setEnabled(True)
        self.btn_scan_all.setEnabled(True)
        QMessageBox.critical(self, "שגיאה בסריקה", f"אירעה שגיאה במהלך הסריקה:\n{err_msg}")
        self.lbl_status.setText("הסריקה נכשלה.")

    def scan_all_pages(self):
        if not self.pages:
            QMessageBox.information(self, "אין עמודים", "אנא צרף תמונות לסריקה תחילה.")
            return

        # Start scanning from first un-scanned page
        for i, p in enumerate(self.pages):
            if p["status"] != "נסרק בהצלחה ✓":
                self.list_pages.setCurrentRow(i)
                self.scan_current_page()
                return
        QMessageBox.information(self, "הסריקה הושלמה", "כל העמודים במחברת כבר נסרקו!")

    def learn_current_corrections(self):
        """Extracts user edits, updates SQLite knowledge base, and shows feedback."""
        if self.current_page_idx < 0 or self.current_page_idx >= len(self.pages):
            return

        pdata = self.pages[self.current_page_idx]
        cur_text = self.editor.get_text()
        raw_text = pdata.get("raw_text", "")

        if not raw_text:
            QMessageBox.information(self, "מידע", "טרם נסרק עמוד זה, או שלא בוצעו בו שינויים מול ה-OCR המקורי.")
            return

        learned = self.learning_engine.learn_from_corrections(raw_text, cur_text, pdata["filename"])
        self.update_learned_count_badge()

        if learned:
            msg = f"נלמדו ונרשמו בהצלחה {len(learned)} כללי תיקון חדשים בזיכרון המערכת!\n\nדוגמאות שנלמדו:\n"
            for raw, corr in learned[:5]:
                msg += f" • '{raw}' ➔ '{corr}'\n"
            if len(learned) > 5:
                msg += f"... ועוד {len(learned) - 5} תיקונים נוספים.\n"
            msg += "\nתיקונים אלו יחולו אוטומטית בכל הסריקות הבאות!"
            QMessageBox.information(self, "הלמידה הושלמה בהצלחה ✓", msg)
        else:
            QMessageBox.information(self, "זיכרון", "לא זוהו מילים חדשות ללמידה בעמוד זה (הכל כבר מעודכן בזיכרון).")

    def _refresh_profiles_ui(self):
        self.combo_profile.blockSignals(True)
        self.combo_profile.clear()
        profiles = self.learning_engine.list_profiles()
        active_pid = self.learning_engine.get_active_profile_id()
        selected_idx = 0
        for idx, p in enumerate(profiles):
            self.combo_profile.addItem(f"{p['name']} ({p['rule_count']} כללים)", p["id"])
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
            self.lbl_status.setText(f"הוחלף לפרופיל כתב יד: {self.learning_engine.get_active_profile_name()}")

    def _quick_new_profile(self):
        name, ok = QInputDialog.getText(self, "פרופיל כתב יד חדש", "שם הפרופיל החדש (למשל: שם התלמיד/מחברת):")
        if ok and name.strip():
            try:
                pid = self.learning_engine.create_profile(name.strip())
                self.learning_engine.set_active_profile(pid)
                self._refresh_profiles_ui()
                self.update_learned_count_badge()
                self.lbl_status.setText(f"נוצר פרופיל פעיל חדש: {name.strip()}")
            except Exception as e:
                QMessageBox.critical(self, "שגיאה", f"נכשל ביצירת פרופיל: {str(e)}")

    def update_learned_count_badge(self):
        rules = self.learning_engine.get_all_replacements(active_only=True)
        enabled_count = len(self.learning_engine.get_enabled_profile_ids())
        stack_info = f" (משולב {enabled_count} פרופילים)" if enabled_count > 1 else ""
        self.lbl_learned_counter.setText(
            f"כללים פעילים: {len(rules):,} [{self.learning_engine.get_active_profile_name()}]{stack_info}"
        )

    def export_to_docx_dialog(self):
        if not self.pages:
            QMessageBox.information(self, "אין נתונים", "אנא צרף וערוך עמודים לפני הייצוא.")
            return

        # Prompt for doc title
        title, ok1 = QInputDialog.getText(self, "ייצוא לוורד", "כותרת ראשית למסמך:", text="שיעורים במסכת בבא קמא")
        if not ok1:
            return
        subtitle, ok2 = QInputDialog.getText(self, "ייצוא לוורד", "תת-כותרת (פרק / זמן):", text="פרק כיצד הרגל | זמן חורף")
        if not ok2:
            return
        author, ok3 = QInputDialog.getText(self, "ייצוא לוורד", "שם הכותב / הערות מאת:", text="")
        if not ok3:
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self, "שמירת מסמך וורד", "מחברת שיעורים - כיצד הרגל.docx",
            "Word Documents (*.docx)"
        )
        if not out_path:
            return

        # Prepare pages
        pages_to_export = []
        for i, p in enumerate(self.pages):
            pages_to_export.append({
                "page_num": i + 1,
                "title": f"עמוד {i + 1} — {p['filename']}",
                "date": "",
                "text": p["text"]
            })

        try:
            export_notes_to_docx(
                pages_to_export,
                out_path,
                document_title=title,
                document_subtitle=subtitle,
                author_name=f"הערות וחידושים מאת {author}" if author else "",
                font_name="David"
            )
            resp = QMessageBox.question(
                self, "הייצוא הושלם בהצלחה!",
                f"המסמך נשמר בהצלחה בנתיב:\n{out_path}\n\nהאם ברצונך לפתוח את המסמך כעת?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if resp == QMessageBox.StandardButton.Yes:
                os.startfile(out_path)
        except Exception as e:
            QMessageBox.critical(self, "שגיאה בייצוא", f"אירעה שגיאה בעת שמירת הקובץ:\n{str(e)}")

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
            self.btn_theme.setText("☀ מצב יום")
        else:
            self.setStyleSheet(LIGHT_THEME)
            self.btn_theme.setText("🌙 מצב לילה")
