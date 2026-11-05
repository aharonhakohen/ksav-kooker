# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Hebrew RTL Text Editor
Full Right-to-Left (RTL) editing with Torah abbreviations toolbar,
line/word statistics, and mistake tracking.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLabel, QPushButton, QMenu, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QTextOption, QAction
import difflib
import re

COMMON_ABBREVIATIONS = [
    ("בס\"ד", "בס\"ד"),
    ("רש\"י", "רש\"י"),
    ("תוס'", "תוס'"),
    ("רמב\"ם", "רמב\"ם"),
    ("ראב\"ד", "ראב\"ד"),
    ("רי\"ף", "רי\"ף"),
    ("רא\"ש", "רא\"ש"),
    ("גמ'", "גמ'"),
    ("משנה", "משנה"),
    ("ברייתא", "ברייתא"),
    ("נפק\"מ", "נפקא מינה"),
    ("קמ\"ל", "קא משמע לן"),
    ("סד\"א", "סלקא דעתך אמינא"),
    ("ח\"נ", "חצי נזק"),
    ("נ\"ש", "נזק שלם"),
    ("ברה\"ר", "רשות הרבים"),
    ("ברה\"י", "רשות היחיד"),
    ("עיי\"ש", "עיין שם"),
    ("עכ\"ד", "עד כאן דבריו"),
    ("וכו'", "וכולי"),
    ("וגו'", "וגומר"),
]

class HebrewTextEditor(QWidget):
    text_changed = pyqtSignal()
    line_focused = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_raw_text = ""
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Quick Abbreviation Bar
        self.abbrev_bar = QHBoxLayout()
        self.abbrev_bar.setSpacing(4)
        
        lbl_quick = QLabel("קיצורים מהירים:")
        lbl_quick.setStyleSheet("font-weight: bold; color: #89b4fa; font-size: 11px;")
        self.abbrev_bar.addWidget(lbl_quick)

        for abbr, full in COMMON_ABBREVIATIONS[:8]:
            btn = QPushButton(abbr)
            btn.setToolTip(full)
            btn.setFixedHeight(24)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 2px 6px; 
                    font-size: 11px; 
                    font-weight: bold;
                    border-radius: 4px;
                }
            """)
            btn.clicked.connect(lambda checked, text=abbr: self.insert_text(text))
            self.abbrev_bar.addWidget(btn)

        # More abbreviations menu
        self.btn_more_abbr = QPushButton("עוד ▾")
        self.btn_more_abbr.setFixedHeight(24)
        more_menu = QMenu(self)
        for abbr, full in COMMON_ABBREVIATIONS[8:]:
            act = QAction(f"{abbr}  ({full})", self)
            act.triggered.connect(lambda checked, text=abbr: self.insert_text(text))
            more_menu.addAction(act)
        self.btn_more_abbr.setMenu(more_menu)
        self.abbrev_bar.addWidget(self.btn_more_abbr)

        self.abbrev_bar.addStretch()
        layout.addLayout(self.abbrev_bar)

        # Text Edit Area
        self.text_edit = QTextEdit()
        self.text_edit.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Typography: David / Segoe UI / Arial
        font = QFont("David", 15)
        font.setStyleHint(QFont.StyleHint.Serif)
        self.text_edit.setFont(font)
        
        # Word wrap & RTL alignment
        opt = self.text_edit.document().defaultTextOption()
        opt.setTextDirection(Qt.LayoutDirection.RightToLeft)
        opt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.text_edit.document().setDefaultTextOption(opt)

        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.cursorPositionChanged.connect(self._on_cursor_changed)
        layout.addWidget(self.text_edit)

        # Stats bar
        self.stats_bar = QHBoxLayout()
        self.lbl_stats = QLabel("מילים: 0 | תווים: 0 | שורות: 0")
        self.lbl_stats.setStyleSheet("color: #a6adc8; font-size: 11px;")
        
        self.lbl_corrections = QLabel("תיקונים שבוצעו: 0")
        self.lbl_corrections.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")

        self.stats_bar.addWidget(self.lbl_stats)
        self.stats_bar.addStretch()
        self.stats_bar.addWidget(self.lbl_corrections)
        layout.addLayout(self.stats_bar)

    def insert_text(self, text: str):
        cursor = self.text_edit.textCursor()
        cursor.insertText(text + " ")
        self.text_edit.setFocus()

    def set_text(self, text: str, raw_text: str = None):
        self.text_edit.blockSignals(True)
        self.text_edit.setPlainText(text)
        self.original_raw_text = raw_text if raw_text is not None else text
        self.text_edit.blockSignals(False)
        self._update_stats()

    def get_text(self) -> str:
        return self.text_edit.toPlainText()

    def _on_text_changed(self):
        self._update_stats()
        self.text_changed.emit()

    def _on_cursor_changed(self):
        cursor = self.text_edit.textCursor()
        line_num = cursor.blockNumber()
        self.line_focused.emit(line_num)

    def _update_stats(self):
        text = self.text_edit.toPlainText()
        words = len(re.findall(r'\S+', text))
        chars = len(text)
        lines = len(text.splitlines()) if text else 0
        self.lbl_stats.setText(f"מילים: {words:,} | תווים: {chars:,} | שורות: {lines:,}")

        # Compute corrections count vs raw OCR
        if self.original_raw_text and self.original_raw_text != text:
            raw_words = re.findall(r'\S+', self.original_raw_text)
            cur_words = re.findall(r'\S+', text)
            sm = difflib.SequenceMatcher(None, raw_words, cur_words)
            diff_count = sum(1 for tag, _, _, _, _ in sm.get_opcodes() if tag in ('replace', 'delete', 'insert'))
            self.lbl_corrections.setText(f"תיקונים שזוהו: {diff_count} (מוכן ללמידה ✓)")
            self.lbl_corrections.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")
        else:
            self.lbl_corrections.setText("טרם בוצעו תיקונים")
            self.lbl_corrections.setStyleSheet("color: #a6adc8; font-size: 11px;")
