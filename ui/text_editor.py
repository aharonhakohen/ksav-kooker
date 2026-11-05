# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Hebrew RTL Text Editor
Full Right-to-Left (RTL) editing with Torah abbreviations toolbar,
line/word statistics, and mistake tracking.
Supports internationalized English and Hebrew labels.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QLabel, QPushButton, QMenu, QToolButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor, QTextOption, QAction
import difflib
import re

from ui.i18n import t

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
        
        self.lbl_quick = QLabel(t("editor_quick_abbr"))
        self.lbl_quick.setStyleSheet("font-weight: bold; color: #89b4fa; font-size: 11px;")
        self.abbrev_bar.addWidget(self.lbl_quick)

        for abbr, full in [('בס"ד', 'בס"ד'), ('רש"י', 'רש"י'), ('תוס\'', 'תוספות')]:
            btn = QPushButton(abbr)
            btn.setToolTip(full)
            btn.setFixedHeight(24)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 2px 8px; 
                    font-size: 11px; 
                    font-weight: bold;
                    border-radius: 4px;
                }
            """)
            btn.clicked.connect(lambda checked, text=abbr: self.insert_text(text))
            self.abbrev_bar.addWidget(btn)

        # Categorized Torah Abbreviations Menu
        self.btn_more_abbr = QToolButton()
        self.btn_more_abbr.setText(t("abbr_menu_title"))
        self.btn_more_abbr.setFixedHeight(24)
        self.btn_more_abbr.setStyleSheet("""
            QToolButton {
                padding: 2px 8px; 
                font-size: 11px; 
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        self.btn_more_abbr.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        self.ab_menu = QMenu(self.btn_more_abbr)
        
        # Submenu 1: Seforim & Commentators
        menu_seforim = self.ab_menu.addMenu(t("abbr_group_seforim"))
        seforim_abbrs = [
            ('רש"י', 'רש"י'),
            ('תוס\'', 'תוספות'),
            ('רמב"ם', 'רמב"ם'),
            ('ראב"ד', 'ראב"ד'),
            ('רי"ף', 'רי"ף'),
            ('רא"ש', 'רא"ש'),
            ('משנה', 'משנה'),
            ('ברייתא', 'ברייתא'),
            ('גמ\'', 'גמרא'),
            ('שו"ע', 'שולחן ערוך'),
            ('טו"ר', 'טור')
        ]
        for a, full in seforim_abbrs:
            act = QAction(f"{a}  ({full})", self)
            act.triggered.connect(lambda checked, text=a: self.insert_text(text))
            menu_seforim.addAction(act)

        menu_terms = self.ab_menu.addMenu(t("abbr_group_talmud"))
        term_abbrs = [
            ('בס"ד', 'בס"ד'),
            ('נפק"מ', 'נפקא מינה'),
            ('קמ"ל', 'קא משמע לן'),
            ('סד"א', 'סלקא דעתך אמינא'),
            ('ח"נ', 'חצי נזק'),
            ('נ"ש', 'נזק שלם'),
            ('ברה"ר', 'רשות הרבים'),
            ('ברה"י', 'רשות היחיד'),
            ('עיי"ש', 'עיין שם'),
            ('עכ"ד', 'עד כאן דבריו'),
            ('וכו\'', 'וכולי'),
            ('וגו\'', 'וגומר')
        ]
        for a, full in term_abbrs:
            act = QAction(f"{a}  ({full})", self)
            act.triggered.connect(lambda checked, text=a: self.insert_text(text))
            menu_terms.addAction(act)

        self.btn_more_abbr.setMenu(self.ab_menu)
        self.abbrev_bar.addWidget(self.btn_more_abbr)

        self.abbrev_bar.addStretch()
        layout.addLayout(self.abbrev_bar)

        # Text Edit Area (Hebrew RTL)
        self.text_edit = QTextEdit()
        self.text_edit.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        font = QFont("David", 15)
        font.setStyleHint(QFont.StyleHint.Serif)
        self.text_edit.setFont(font)

        opt = self.text_edit.document().defaultTextOption()
        opt.setTextDirection(Qt.LayoutDirection.RightToLeft)
        opt.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.text_edit.document().setDefaultTextOption(opt)

        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.cursorPositionChanged.connect(self._on_cursor_changed)
        layout.addWidget(self.text_edit)

        # Stats bar
        self.stats_bar = QHBoxLayout()
        self.lbl_stats = QLabel("")
        self.lbl_stats.setStyleSheet("color: #a6adc8; font-size: 11px;")
        
        self.lbl_corrections = QLabel("")
        self.lbl_corrections.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")

        self.stats_bar.addWidget(self.lbl_stats)
        self.stats_bar.addStretch()
        self.stats_bar.addWidget(self.lbl_corrections)
        layout.addLayout(self.stats_bar)
        
        self._update_stats()

    def retranslate_ui(self):
        self.lbl_quick.setText(t("editor_quick_abbr"))
        self.btn_more_abbr.setText(t("abbr_menu_title"))
        self._update_stats()

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
        self.lbl_stats.setText(t("editor_stats", words=words, chars=chars, lines=lines))

        # Compute corrections count vs raw OCR
        if self.original_raw_text and self.original_raw_text != text:
            raw_words = re.findall(r'\S+', self.original_raw_text)
            cur_words = re.findall(r'\S+', text)
            sm = difflib.SequenceMatcher(None, raw_words, cur_words)
            diff_count = sum(1 for tag, _, _, _, _ in sm.get_opcodes() if tag in ('replace', 'delete', 'insert'))
            self.lbl_corrections.setText(t("editor_diff_ready", count=diff_count))
            self.lbl_corrections.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 11px;")
        else:
            self.lbl_corrections.setText(t("editor_diff_none"))
            self.lbl_corrections.setStyleSheet("color: #a6adc8; font-size: 11px;")
