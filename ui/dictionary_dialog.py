# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Dictionary & Learned Rules Manager Dialog
Allows viewing, searching, adding, editing, and deleting learned OCR rules and abbreviations.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, 
    QHeaderView, QMessageBox, QFileDialog, QCheckBox
)
from PyQt6.QtCore import Qt
import json

class DictionaryManagerDialog(QDialog):
    def __init__(self, learning_engine, parent=None):
        super().__init__(parent)
        self.learning_engine = learning_engine
        self.setWindowTitle("מנהל הזיכרון והכללים הנלמדים (IbberKuck Memory)")
        self.resize(700, 500)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._init_ui()
        self.load_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Header Title & Description
        lbl_title = QLabel("כללי תיקון וזיכרון נלמד")
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa;")
        lbl_desc = QLabel("המערכת לומדת באופן אוטומטי מכל תיקון שתבצע בעורך, ומחילה את הכללים בסריקות הבאות.")
        lbl_desc.setStyleSheet("color: #a6adc8; font-size: 12px;")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)

        # Search Bar + Action Buttons
        search_bar = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("חיפוש כלל או מילה...")
        self.txt_search.textChanged.connect(self.filter_data)
        search_bar.addWidget(self.txt_search)

        btn_add = QPushButton("+ הוסף כלל חדש")
        btn_add.setObjectName("btn_primary")
        btn_add.clicked.connect(self.add_rule_dialog)
        search_bar.addWidget(btn_add)

        btn_export = QPushButton("ייצוא...")
        btn_export.clicked.connect(self.export_rules)
        search_bar.addWidget(btn_export)

        btn_import = QPushButton("ייבוא...")
        btn_import.clicked.connect(self.import_rules)
        search_bar.addWidget(btn_import)

        layout.addLayout(search_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["מזהה", "טקסט מקורי (שגיאת OCR)", "תיקון נלמד", "פעמים שנצפה", "פעיל"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Bottom Bar
        bottom_bar = QHBoxLayout()
        self.lbl_stats = QLabel("סה\"כ כללים: 0")
        self.lbl_stats.setStyleSheet("font-weight: bold; color: #a6adc8;")
        bottom_bar.addWidget(self.lbl_stats)

        bottom_bar.addStretch()

        btn_delete = QPushButton("מחק כלל נבחר")
        btn_delete.setStyleSheet("background-color: #dc2626; color: white;")
        btn_delete.clicked.connect(self.delete_selected)
        bottom_bar.addWidget(btn_delete)

        btn_close = QPushButton("סגור")
        btn_close.clicked.connect(self.accept)
        bottom_bar.addWidget(btn_close)

        layout.addLayout(bottom_bar)

    def load_data(self):
        self.table.setRowCount(0)
        rules = self.learning_engine.get_all_replacements(active_only=False)
        self.all_rules = rules
        self.lbl_stats.setText(f"סה\"כ כללים פעילים במערכת: {len(rules):,}")

        for r in rules:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # ID
            item_id = QTableWidgetItem(str(r["id"]))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, item_id)

            # Raw
            item_raw = QTableWidgetItem(r["raw_text"])
            self.table.setItem(row, 1, item_raw)

            # Corrected
            item_corr = QTableWidgetItem(r["corrected_text"])
            self.table.setItem(row, 2, item_corr)

            # Count
            item_cnt = QTableWidgetItem(str(r["count"]))
            item_cnt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, item_cnt)

            # Active checkbox
            chk = QCheckBox()
            chk.setChecked(r["is_active"])
            chk.stateChanged.connect(lambda state, rid=r["id"]: self.learning_engine.toggle_replacement(rid, state == 2))
            chk_widget = QDialog()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 4, chk_widget)

    def filter_data(self, query: str):
        query = query.strip().lower()
        for row in range(self.table.rowCount()):
            raw = self.table.item(row, 1).text().lower()
            corr = self.table.item(row, 2).text().lower()
            match = not query or query in raw or query in corr
            self.table.setRowHidden(row, not match)

    def add_rule_dialog(self):
        from PyQt6.QtWidgets import QInputDialog
        raw, ok1 = QInputDialog.getText(self, "הוספת כלל חדש", "טקסט מקורי (כפי שנקרא ב-OCR לפעמים):")
        if not ok1 or not raw.strip():
            return
        corr, ok2 = QInputDialog.getText(self, "הוספת כלל חדש", f"התיקון הנכון עבור '{raw.strip()}':")
        if not ok2 or not corr.strip():
            return

        self.learning_engine.add_or_update_replacement(raw.strip(), corr.strip(), increment=5)
        self.load_data()
        QMessageBox.information(self, "נוסף בהצלחה", f"הכלל '{raw.strip()}' -> '{corr.strip()}' נשמר במערכת.")

    def delete_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "לא נבחר", "אנא בחר שורה למחיקה.")
            return

        row = selected_rows[0].row()
        rule_id = int(self.table.item(row, 0).text())
        raw = self.table.item(row, 1).text()
        corr = self.table.item(row, 2).text()

        confirm = QMessageBox.question(
            self, "אישור מחיקה",
            f"האם אתה בטוח שברצונך למחוק את הכלל '{raw}' -> '{corr}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.learning_engine.delete_replacement(rule_id)
            self.load_data()

    def export_rules(self):
        path, _ = QFileDialog.getSaveFileName(self, "ייצוא כללים לקובץ JSON", "learned_rules.json", "JSON Files (*.json)")
        if not path:
            return
        rules = self.learning_engine.get_all_replacements(active_only=False)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "ייצוא הושלם", f"נשמרו {len(rules)} כללים לקובץ.")

    def import_rules(self):
        path, _ = QFileDialog.getOpenFileName(self, "ייבוא כללים מקובץ JSON", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                rules = json.load(f)
            count = 0
            for r in rules:
                if "raw_text" in r and "corrected_text" in r:
                    self.learning_engine.add_or_update_replacement(r["raw_text"], r["corrected_text"], increment=r.get("count", 1))
                    count += 1
            self.load_data()
            QMessageBox.information(self, "ייבוא הושלם", f"יובאו {count} כללים בהצלחה.")
        except Exception as e:
            QMessageBox.critical(self, "שגיאה בייבוא", f"אירעה שגיאה בקריאת הקובץ:\n{str(e)}")
