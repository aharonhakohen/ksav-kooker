# -*- coding: utf-8 -*-
"""
TorahNotesOCR - Dictionary, Profiles & Backup Manager Dialog (v1.1.0)
Supports English (default) and Hebrew localization via ui.i18n.
"""

import os
import json
import subprocess
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLineEdit, QLabel, 
    QHeaderView, QMessageBox, QFileDialog, QCheckBox,
    QTabWidget, QWidget, QGroupBox, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from ui.i18n import t, I18nManager


class DictionaryManagerDialog(QDialog):
    def __init__(self, learning_engine, parent=None):
        super().__init__(parent)
        self.learning_engine = learning_engine
        self.setWindowTitle(t("dict_window_title"))
        self.resize(840, 600)
        
        is_hebrew = (I18nManager.instance().current_lang == "he")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft if is_hebrew else Qt.LayoutDirection.LeftToRight)
        
        self._init_ui()
        self.load_all_data()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(16, 16, 16, 16)

        # Top Header Banner
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        self.lbl_title = QLabel(t("dict_header_title"))
        self.lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #89b4fa;")
        self.lbl_active_profile = QLabel(t("dict_active_prof_lbl", name="..."))
        self.lbl_active_profile.setStyleSheet("color: #a6e3a1; font-weight: bold; font-size: 13px;")
        title_box.addWidget(self.lbl_title)
        title_box.addWidget(self.lbl_active_profile)
        header_layout.addLayout(title_box)
        header_layout.addStretch()

        btn_quick_backup = QPushButton(t("dict_quick_backup_btn"))
        btn_quick_backup.setToolTip(t("dict_quick_backup_tooltip"))
        btn_quick_backup.clicked.connect(self.quick_backup_action)
        header_layout.addWidget(btn_quick_backup)

        main_layout.addLayout(header_layout)

        # Tab Widget
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)

        # Tab 1: Learned Rules
        self.tab_rules = QWidget()
        self._init_rules_tab()
        self.tabs.addTab(self.tab_rules, t("dict_tab_rules"))

        # Tab 2: Handwriting Profiles
        self.tab_profiles = QWidget()
        self._init_profiles_tab()
        self.tabs.addTab(self.tab_profiles, t("dict_tab_profiles"))

        # Tab 3: Backup & Restore
        self.tab_backup = QWidget()
        self._init_backup_tab()
        self.tabs.addTab(self.tab_backup, t("dict_tab_backup"))

        # Dialog Footer
        footer_layout = QHBoxLayout()
        footer_layout.addStretch()
        btn_close = QPushButton(t("dict_btn_close"))
        btn_close.clicked.connect(self.accept)
        footer_layout.addWidget(btn_close)
        main_layout.addLayout(footer_layout)

    # =========================================================================
    # Tab 1: Rules Table
    # =========================================================================

    def _init_rules_tab(self):
        layout = QVBoxLayout(self.tab_rules)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Search Bar + Actions
        search_bar = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText(t("dict_search_placeholder"))
        self.txt_search.textChanged.connect(self.filter_rules)
        search_bar.addWidget(self.txt_search)

        btn_add = QPushButton(t("dict_btn_add_rule"))
        btn_add.setObjectName("btn_primary")
        btn_add.clicked.connect(self.add_rule_dialog)
        search_bar.addWidget(btn_add)

        layout.addLayout(search_bar)

        # Table
        self.table_rules = QTableWidget()
        self.table_rules.setColumnCount(5)
        self.table_rules.setHorizontalHeaderLabels([
            t("dict_rules_header_id"),
            t("dict_rules_header_raw"),
            t("dict_rules_header_corr"),
            t("dict_rules_header_count"),
            t("dict_rules_header_active")
        ])
        self.table_rules.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_rules.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_rules.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_rules.setAlternatingRowColors(True)
        layout.addWidget(self.table_rules)

        # Bottom stats & delete
        bottom_bar = QHBoxLayout()
        self.lbl_rules_stats = QLabel(t("dict_rules_total", count=0))
        self.lbl_rules_stats.setStyleSheet("font-weight: bold; color: #a6adc8;")
        bottom_bar.addWidget(self.lbl_rules_stats)
        bottom_bar.addStretch()

        btn_delete = QPushButton(t("dict_btn_delete_rule"))
        btn_delete.setStyleSheet("background-color: #dc2626; color: white;")
        btn_delete.clicked.connect(self.delete_selected_rule)
        bottom_bar.addWidget(btn_delete)

        layout.addLayout(bottom_bar)

    def load_rules_data(self):
        self.table_rules.setRowCount(0)
        rules = self.learning_engine.get_all_replacements(active_only=False, include_all_enabled=False)
        self.lbl_rules_stats.setText(t("dict_rules_total", count=len(rules)))

        for r in rules:
            row = self.table_rules.rowCount()
            self.table_rules.insertRow(row)

            item_id = QTableWidgetItem(str(r["id"]))
            item_id.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_rules.setItem(row, 0, item_id)

            item_raw = QTableWidgetItem(r["raw_text"])
            self.table_rules.setItem(row, 1, item_raw)

            item_corr = QTableWidgetItem(r["corrected_text"])
            self.table_rules.setItem(row, 2, item_corr)

            item_cnt = QTableWidgetItem(str(r["count"]))
            item_cnt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_rules.setItem(row, 3, item_cnt)

            chk = QCheckBox()
            chk.setChecked(r["is_active"])
            chk.stateChanged.connect(lambda state, rid=r["id"]: self.learning_engine.toggle_replacement(rid, state == 2))
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table_rules.setCellWidget(row, 4, chk_widget)

    def filter_rules(self, query: str):
        query = query.strip().lower()
        for row in range(self.table_rules.rowCount()):
            raw = self.table_rules.item(row, 1).text().lower()
            corr = self.table_rules.item(row, 2).text().lower()
            match = not query or query in raw or query in corr
            self.table_rules.setRowHidden(row, not match)

    def add_rule_dialog(self):
        raw, ok1 = QInputDialog.getText(self, t("dict_btn_add_rule"), "Original text / OCR error:")
        if not ok1 or not raw.strip():
            return
        corr, ok2 = QInputDialog.getText(self, t("dict_btn_add_rule"), f"Corrected spelling for '{raw.strip()}':")
        if not ok2 or not corr.strip():
            return

        self.learning_engine.add_or_update_replacement(raw.strip(), corr.strip(), increment=5)
        self.load_rules_data()
        self.load_profiles_data()
        QMessageBox.information(self, "Success", f"Rule '{raw.strip()}' -> '{corr.strip()}' saved to profile.")

    def delete_selected_rule(self):
        selected_rows = self.table_rules.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Notice", "Please select a rule to delete.")
            return

        row = selected_rows[0].row()
        rule_id = int(self.table_rules.item(row, 0).text())
        raw = self.table_rules.item(row, 1).text()
        corr = self.table_rules.item(row, 2).text()

        confirm = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete rule '{raw}' -> '{corr}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.learning_engine.delete_replacement(rule_id)
            self.load_rules_data()
            self.load_profiles_data()

    # =========================================================================
    # Tab 2: Profiles Management
    # =========================================================================

    def _init_profiles_tab(self):
        layout = QVBoxLayout(self.tab_profiles)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        lbl_desc = QLabel(t("dict_profiles_desc"))
        lbl_desc.setStyleSheet("color: #a6adc8; font-size: 12px; line-height: 1.4;")
        layout.addWidget(lbl_desc)

        # Profiles Table
        self.table_profiles = QTableWidget()
        self.table_profiles.setColumnCount(5)
        self.table_profiles.setHorizontalHeaderLabels([
            t("dict_profiles_header_enabled"),
            t("dict_profiles_header_name"),
            t("dict_profiles_header_desc"),
            t("dict_profiles_header_count"),
            t("dict_profiles_header_status")
        ])
        self.table_profiles.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table_profiles.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_profiles.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_profiles.setAlternatingRowColors(True)
        layout.addWidget(self.table_profiles)

        # Profile Actions Toolbar
        actions_bar = QHBoxLayout()
        btn_new_prof = QPushButton(t("dict_btn_new_prof"))
        btn_new_prof.setObjectName("btn_primary")
        btn_new_prof.clicked.connect(self.new_profile_dialog)
        actions_bar.addWidget(btn_new_prof)

        btn_set_active = QPushButton(t("dict_btn_set_active"))
        btn_set_active.clicked.connect(self.set_active_profile_action)
        actions_bar.addWidget(btn_set_active)

        btn_dup_prof = QPushButton(t("dict_btn_dup_prof"))
        btn_dup_prof.clicked.connect(self.duplicate_profile_action)
        actions_bar.addWidget(btn_dup_prof)

        btn_edit_prof = QPushButton(t("dict_btn_edit_prof"))
        btn_edit_prof.clicked.connect(self.edit_profile_action)
        actions_bar.addWidget(btn_edit_prof)

        btn_merge_prof = QPushButton(t("dict_btn_merge_prof"))
        btn_merge_prof.setToolTip(t("dict_btn_merge_prof_tooltip"))
        btn_merge_prof.clicked.connect(self.merge_profile_action)
        actions_bar.addWidget(btn_merge_prof)

        btn_del_prof = QPushButton(t("dict_btn_del_prof"))
        btn_del_prof.setStyleSheet("background-color: #dc2626; color: white;")
        btn_del_prof.clicked.connect(self.delete_profile_action)
        actions_bar.addWidget(btn_del_prof)

        layout.addLayout(actions_bar)

    def load_profiles_data(self):
        self.table_profiles.setRowCount(0)
        profiles = self.learning_engine.list_profiles()
        active_pid = self.learning_engine.get_active_profile_id()
        enabled_pids = self.learning_engine.get_enabled_profile_ids()

        self.lbl_active_profile.setText(t("dict_active_prof_lbl", name=self.learning_engine.get_active_profile_name()))

        for p in profiles:
            row = self.table_profiles.rowCount()
            self.table_profiles.insertRow(row)

            chk = QCheckBox()
            chk.setChecked(p["id"] in enabled_pids)
            if p["id"] == active_pid:
                chk.setEnabled(False)
            chk.stateChanged.connect(lambda state, pid=p["id"]: self._toggle_profile_enabled(pid, state == 2))
            chk_widget = QWidget()
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chk_layout.setContentsMargins(0, 0, 0, 0)
            self.table_profiles.setCellWidget(row, 0, chk_widget)

            item_name = QTableWidgetItem(p["name"])
            item_name.setData(Qt.ItemDataRole.UserRole, p["id"])
            if p["is_active"]:
                font = item_name.font()
                font.setBold(True)
                item_name.setFont(font)
                item_name.setForeground(QColor("#a6e3a1"))
            self.table_profiles.setItem(row, 1, item_name)

            item_desc = QTableWidgetItem(p["description"])
            self.table_profiles.setItem(row, 2, item_desc)

            item_cnt = QTableWidgetItem(str(p["rule_count"]))
            item_cnt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_profiles.setItem(row, 3, item_cnt)

            status_text = t("dict_profiles_status_primary") if p["is_active"] else t("dict_profiles_status_secondary")
            item_status = QTableWidgetItem(status_text)
            item_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table_profiles.setItem(row, 4, item_status)

    def _toggle_profile_enabled(self, profile_id: str, is_enabled: bool):
        current_enabled = self.learning_engine.get_enabled_profile_ids()
        if is_enabled and profile_id not in current_enabled:
            current_enabled.append(profile_id)
        elif not is_enabled and profile_id in current_enabled:
            current_enabled.remove(profile_id)
        self.learning_engine.set_enabled_profiles(current_enabled)

    def new_profile_dialog(self):
        name, ok1 = QInputDialog.getText(self, t("dict_btn_new_prof"), "Profile Name (e.g. Student name or notebook topic):")
        if not ok1 or not name.strip():
            return
        desc, ok2 = QInputDialog.getText(self, "Profile Description", "Description (optional):")
        if not ok2:
            desc = ""

        try:
            pid = self.learning_engine.create_profile(name.strip(), desc.strip(), seed_defaults=True)
            self.learning_engine.set_active_profile(pid)
            self.load_all_data()
            QMessageBox.information(self, "Success", f"Profile '{name.strip()}' created and set as active.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create profile: {str(e)}")

    def set_active_profile_action(self):
        selected_rows = self.table_profiles.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Notice", "Please select a profile from the table.")
            return

        row = selected_rows[0].row()
        pid = self.table_profiles.item(row, 1).data(Qt.ItemDataRole.UserRole)
        self.learning_engine.set_active_profile(pid)
        self.load_all_data()

    def duplicate_profile_action(self):
        selected_rows = self.table_profiles.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Notice", "Please select a profile to duplicate.")
            return

        row = selected_rows[0].row()
        pid = self.table_profiles.item(row, 1).data(Qt.ItemDataRole.UserRole)
        old_name = self.table_profiles.item(row, 1).text()

        new_name, ok = QInputDialog.getText(self, t("dict_btn_dup_prof"), f"Name for clone of '{old_name}':", text=f"{old_name} (Copy)")
        if not ok or not new_name.strip():
            return

        try:
            self.learning_engine.duplicate_profile(pid, new_name.strip())
            self.load_profiles_data()
            QMessageBox.information(self, "Success", f"Profile '{new_name.strip()}' cloned successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clone profile: {str(e)}")

    def edit_profile_action(self):
        selected_rows = self.table_profiles.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Notice", "Please select a profile to edit.")
            return

        row = selected_rows[0].row()
        pid = self.table_profiles.item(row, 1).data(Qt.ItemDataRole.UserRole)
        current_name = self.table_profiles.item(row, 1).text()
        current_desc = self.table_profiles.item(row, 2).text()

        new_name, ok1 = QInputDialog.getText(self, t("dict_btn_edit_prof"), "Profile Name:", text=current_name)
        if not ok1 or not new_name.strip():
            return
        new_desc, ok2 = QInputDialog.getText(self, "Profile Description", "Description:", text=current_desc)
        if not ok2:
            new_desc = current_desc

        self.learning_engine.rename_profile(pid, new_name.strip(), new_desc.strip())
        self.load_all_data()

    def merge_profile_action(self):
        selected_rows = self.table_profiles.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Notice", "Please select a profile to merge.")
            return

        row = selected_rows[0].row()
        src_pid = self.table_profiles.item(row, 1).data(Qt.ItemDataRole.UserRole)
        src_name = self.table_profiles.item(row, 1).text()
        active_name = self.learning_engine.get_active_profile_name()

        if src_pid == self.learning_engine.get_active_profile_id():
            QMessageBox.information(self, "Notice", "This is already the active profile.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Rule Merge",
            f"Merge all rules from '{src_name}' into active profile '{active_name}'?\n\nAll rules will be added without deleting existing rules.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                count = self.learning_engine.merge_profiles(src_pid)
                self.load_all_data()
                QMessageBox.information(self, "Merge Complete", f"Successfully merged {count} rules into '{active_name}'.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to merge rules:\n{str(e)}")

    def delete_profile_action(self):
        selected_rows = self.table_profiles.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Notice", "Please select a profile to delete.")
            return

        if len(self.learning_engine.list_profiles()) <= 1:
            QMessageBox.warning(self, "Notice", "Cannot delete the only remaining profile.")
            return

        row = selected_rows[0].row()
        pid = self.table_profiles.item(row, 1).data(Qt.ItemDataRole.UserRole)
        name = self.table_profiles.item(row, 1).text()

        confirm = QMessageBox.question(
            self, "Confirm Profile Deletion",
            f"Are you sure you want to permanently delete profile '{name}' and all its learned rules?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.learning_engine.delete_profile(pid)
            self.load_all_data()

    # =========================================================================
    # Tab 3: Backup & Restore
    # =========================================================================

    def _init_backup_tab(self):
        layout = QVBoxLayout(self.tab_backup)
        layout.setSpacing(14)
        layout.setContentsMargins(14, 14, 14, 14)

        # Section 1: Backup
        grp_backup = QGroupBox(t("dict_grp_backup"))
        backup_layout = QVBoxLayout(grp_backup)
        backup_layout.setSpacing(8)

        lbl_b_desc = QLabel(t("dict_lbl_backup_desc"))
        lbl_b_desc.setStyleSheet("color: #a6adc8; font-size: 12px;")
        backup_layout.addWidget(lbl_b_desc)

        b_buttons = QHBoxLayout()
        btn_quick = QPushButton(t("dict_btn_quick_backup"))
        btn_quick.setObjectName("btn_primary")
        btn_quick.clicked.connect(self.quick_backup_action)
        b_buttons.addWidget(btn_quick)

        btn_save_as = QPushButton(t("dict_btn_save_as"))
        btn_save_as.clicked.connect(self.save_backup_as_action)
        b_buttons.addWidget(btn_save_as)

        btn_open_folder = QPushButton(t("dict_btn_open_folder"))
        btn_open_folder.clicked.connect(self.open_backups_folder_action)
        b_buttons.addWidget(btn_open_folder)
        backup_layout.addLayout(b_buttons)
        layout.addWidget(grp_backup)

        # Section 2: Restore & Import
        grp_restore = QGroupBox(t("dict_grp_restore"))
        restore_layout = QVBoxLayout(grp_restore)
        restore_layout.setSpacing(8)

        lbl_r_desc = QLabel(t("dict_lbl_restore_desc"))
        lbl_r_desc.setStyleSheet("color: #a6adc8; font-size: 12px;")
        restore_layout.addWidget(lbl_r_desc)

        r_buttons = QHBoxLayout()
        btn_restore_new = QPushButton(t("dict_btn_restore_new"))
        btn_restore_new.setToolTip(t("dict_btn_restore_new_tooltip"))
        btn_restore_new.clicked.connect(lambda: self.restore_action(as_new=True))
        r_buttons.addWidget(btn_restore_new)

        btn_restore_overwrite = QPushButton(t("dict_btn_restore_overwrite"))
        btn_restore_overwrite.setToolTip(t("dict_btn_restore_overwrite_tooltip"))
        btn_restore_overwrite.clicked.connect(lambda: self.restore_action(as_new=False))
        r_buttons.addWidget(btn_restore_overwrite)

        btn_merge_file = QPushButton(t("dict_btn_merge_file"))
        btn_merge_file.setToolTip(t("dict_btn_merge_file_tooltip"))
        btn_merge_file.clicked.connect(self.merge_from_file_action)
        r_buttons.addWidget(btn_merge_file)
        restore_layout.addLayout(r_buttons)
        layout.addWidget(grp_restore)

        # Section 3: JSON Export & Share
        grp_share = QGroupBox(t("dict_grp_share"))
        share_layout = QVBoxLayout(grp_share)
        share_layout.setSpacing(8)

        lbl_s_desc = QLabel(t("dict_lbl_share_desc"))
        lbl_s_desc.setStyleSheet("color: #a6adc8; font-size: 12px;")
        share_layout.addWidget(lbl_s_desc)

        s_buttons = QHBoxLayout()
        btn_export_json = QPushButton(t("dict_btn_export_json"))
        btn_export_json.clicked.connect(self.export_json_action)
        s_buttons.addWidget(btn_export_json)

        btn_import_json = QPushButton(t("dict_btn_import_json"))
        btn_import_json.clicked.connect(self.import_json_action)
        s_buttons.addWidget(btn_import_json)
        share_layout.addLayout(s_buttons)
        layout.addWidget(grp_share)

        layout.addStretch()

    def quick_backup_action(self):
        try:
            path = self.learning_engine.quick_backup()
            QMessageBox.information(
                self, "Backup Complete",
                f"Full backup of active profile created:\n\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Failed to create backup:\n{str(e)}")

    def save_backup_as_action(self):
        pname = self.learning_engine.get_active_profile_name()
        default_name = f"OhrHaKsav_{pname}.ohrhaksav"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Backup File", default_name, "Ohr HaKsav Backup (*.ohrhaksav *.ksavbackup);;SQLite Database (*.db)"
        )
        if not path:
            return
        try:
            self.learning_engine.backup_profile(self.learning_engine.get_active_profile_id(), path)
            QMessageBox.information(self, "Backup Saved", f"Backup saved successfully to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save backup:\n{str(e)}")

    def open_backups_folder_action(self):
        folder = self.learning_engine.backups_dir
        if os.path.exists(folder):
            try:
                os.startfile(folder)
            except Exception:
                subprocess.Popen(["explorer", folder])
        else:
            QMessageBox.information(self, "Notice", "Backups folder has not been created yet.")

    def restore_action(self, as_new: bool):
        title = "Select Backup File to Restore as New Profile" if as_new else "Select Backup File to Overwrite Active Profile"
        path, _ = QFileDialog.getOpenFileName(
            self, title, "", "Backup Files (*.ohrhaksav *.ksavbackup *.db *.json);;All Files (*.*)"
        )
        if not path:
            return

        prof_name = ""
        if as_new:
            base_suggest = os.path.splitext(os.path.basename(path))[0]
            name, ok = QInputDialog.getText(self, "Restored Profile Name", "New profile name:", text=base_suggest)
            if not ok or not name.strip():
                return
            prof_name = name.strip()
        else:
            active_name = self.learning_engine.get_active_profile_name()
            confirm = QMessageBox.question(
                self, "Confirm Restore",
                f"This will replace all rules in active profile '{active_name}' with the backup data.\n\nAn automatic safety pre-backup will be made.\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

        try:
            pid = self.learning_engine.restore_profile(path, profile_name=prof_name, as_new_profile=as_new)
            self.learning_engine.set_active_profile(pid)
            self.load_all_data()
            QMessageBox.information(self, "Restore Complete", f"Data restored successfully to profile '{self.learning_engine.get_active_profile_name()}'.")
        except Exception as e:
            QMessageBox.critical(self, "Restore Error", f"Error restoring backup:\n{str(e)}")

    def merge_from_file_action(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Rule File to Merge", "", "Rule Files (*.ohrhaksav *.ksavbackup *.db *.json);;All Files (*.*)"
        )
        if not path:
            return

        active_name = self.learning_engine.get_active_profile_name()
        try:
            count = self.learning_engine.merge_profiles(path)
            self.load_all_data()
            QMessageBox.information(
                self, "Merge Complete",
                f"Successfully added and merged {count} rules into active profile '{active_name}'."
            )
        except Exception as e:
            QMessageBox.critical(self, "Merge Error", f"Error merging file:\n{str(e)}")

    def export_json_action(self):
        pname = self.learning_engine.get_active_profile_name()
        default_file = f"ohr_haksav_rules_{pname}.json"
        path, _ = QFileDialog.getSaveFileName(self, "Export Rules to JSON", default_file, "JSON Files (*.json)")
        if not path:
            return
        rules = self.learning_engine.get_all_replacements(active_only=False, include_all_enabled=False)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        QMessageBox.information(self, "Export Complete", f"Saved {len(rules)} rules to file.")

    def import_json_action(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import Rules from JSON", "", "JSON Files (*.json)")
        if not path:
            return
        try:
            count = self.learning_engine.merge_profiles(path)
            self.load_all_data()
            QMessageBox.information(self, "Import Complete", f"Imported and merged {count} rules successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Error reading file:\n{str(e)}")

    # =========================================================================
    # Master Data Reload
    # =========================================================================

    def load_all_data(self):
        self.load_rules_data()
        self.load_profiles_data()
