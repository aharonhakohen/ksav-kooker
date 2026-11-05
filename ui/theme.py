# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Theme & Styling
Modern, clean, professional themes with dark and light modes.
"""

DARK_THEME = """
QWidget {
    background-color: #181825;
    color: #cdd6f4;
    font-family: 'Segoe UI', 'David', 'Arial', sans-serif;
    font-size: 13px;
}

/* ToolBar & Header */
QToolBar {
    background-color: #1e1e2e;
    border-bottom: 1px solid #313244;
    spacing: 8px;
    padding: 6px;
}

QToolButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
}

QToolButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
    color: #ffffff;
}

QToolButton:pressed {
    background-color: #585b70;
}

/* Primary Action Buttons */
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #45475a;
    border-color: #89b4fa;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #585b70;
}

QPushButton#btn_primary {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
}

QPushButton#btn_primary:hover {
    background-color: #1d4ed8;
    border-color: #60a5fa;
}

QPushButton#btn_success {
    background-color: #059669;
    color: #ffffff;
    border: 1px solid #10b981;
}

QPushButton#btn_success:hover {
    background-color: #047857;
    border-color: #34d399;
}

/* Splitter */
QSplitter::handle {
    background-color: #313244;
    width: 3px;
    height: 3px;
}

QSplitter::handle:hover {
    background-color: #89b4fa;
}

/* List & Thumbnails */
QListWidget {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    background-color: #262638;
    border: 1px solid #36364a;
    border-radius: 6px;
    padding: 8px;
    margin: 4px 2px;
}

QListWidget::item:hover {
    background-color: #313248;
    border-color: #89b4fa;
}

QListWidget::item:selected {
    background-color: #363854;
    border: 2px solid #89b4fa;
    color: #ffffff;
}

/* Text Editor */
QTextEdit, QPlainTextEdit {
    background-color: #1e1e2e;
    color: #f5f5f7;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 12px;
    font-family: 'David', 'Arial', sans-serif;
    font-size: 16px;
    line-height: 1.5;
    selection-background-color: #3b82f6;
    selection-color: #ffffff;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #89b4fa;
}

/* Graphics View / Canvas */
QGraphicsView {
    background-color: #11111b;
    border: 1px solid #313244;
    border-radius: 8px;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #45475a;
    border-radius: 6px;
    text-align: center;
    background-color: #1e1e2e;
    color: #ffffff;
    font-weight: bold;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 5px;
}

/* Status Bar */
QStatusBar {
    background-color: #1e1e2e;
    border-top: 1px solid #313244;
    color: #a6adc8;
    font-size: 12px;
    padding: 2px 8px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #181825;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #45475a;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Dialogs & Tables */
QDialog {
    background-color: #181825;
    color: #cdd6f4;
}

QTableWidget {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    gridline-color: #313244;
    color: #cdd6f4;
    border-radius: 6px;
}

QTableWidget::item {
    padding: 6px;
}

QHeaderView::section {
    background-color: #262638;
    color: #cdd6f4;
    padding: 6px;
    border: 1px solid #313244;
    font-weight: bold;
}

QLineEdit {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #ffffff;
}

QLineEdit:focus {
    border-color: #89b4fa;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f8fafc;
    color: #1e293b;
    font-family: 'Segoe UI', 'David', 'Arial', sans-serif;
    font-size: 13px;
}

/* ToolBar & Header */
QToolBar {
    background-color: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    spacing: 8px;
    padding: 6px;
}

QToolButton {
    background-color: #f1f5f9;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 600;
}

QToolButton:hover {
    background-color: #e2e8f0;
    border-color: #2563eb;
    color: #0f172a;
}

QPushButton {
    background-color: #f1f5f9;
    color: #1e293b;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #e2e8f0;
    border-color: #2563eb;
}

QPushButton#btn_primary {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #1d4ed8;
}

QPushButton#btn_primary:hover {
    background-color: #1d4ed8;
}

QPushButton#btn_success {
    background-color: #059669;
    color: #ffffff;
    border: 1px solid #047857;
}

QPushButton#btn_success:hover {
    background-color: #047857;
}

QSplitter::handle {
    background-color: #e2e8f0;
    width: 3px;
    height: 3px;
}

QListWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 4px;
}

QListWidget::item {
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 8px;
    margin: 4px 2px;
}

QListWidget::item:hover {
    background-color: #f1f5f9;
    border-color: #3b82f6;
}

QListWidget::item:selected {
    background-color: #eff6ff;
    border: 2px solid #2563eb;
    color: #1e3a8a;
}

QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 12px;
    font-family: 'David', 'Arial', sans-serif;
    font-size: 16px;
    line-height: 1.5;
    selection-background-color: #bfdbfe;
    selection-color: #1e3a8a;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #2563eb;
}

QGraphicsView {
    background-color: #f1f5f9;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}

QProgressBar {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    text-align: center;
    background-color: #f1f5f9;
    color: #1e293b;
    font-weight: bold;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #2563eb;
    border-radius: 5px;
}

QStatusBar {
    background-color: #ffffff;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    font-size: 12px;
    padding: 2px 8px;
}

QScrollBar:vertical {
    border: none;
    background: #f8fafc;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #94a3b8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QDialog {
    background-color: #f8fafc;
    color: #1e293b;
}

QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    gridline-color: #f1f5f9;
    color: #1e293b;
    border-radius: 6px;
}

QHeaderView::section {
    background-color: #f1f5f9;
    color: #334155;
    padding: 6px;
    border: 1px solid #e2e8f0;
    font-weight: bold;
}

QLineEdit {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 10px;
    color: #0f172a;
}

QLineEdit:focus {
    border-color: #2563eb;
}
"""
