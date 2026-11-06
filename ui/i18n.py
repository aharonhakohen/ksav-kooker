# -*- coding: utf-8 -*-
"""
Ohr HaKsav - Internationalization & UI Localization (i18n)
Default language: English ("en").
Supported languages: English ("en"), Hebrew ("he").
"""

import os
import json

def get_app_data_dir() -> str:
    if os.environ.get("OHR_HAKSAV_DATA_DIR"):
        return os.environ["OHR_HAKSAV_DATA_DIR"]
    if os.environ.get("KSAV_KOOKER_DATA_DIR"):
        return os.environ["KSAV_KOOKER_DATA_DIR"]
    base = os.environ.get("APPDATA", os.path.expanduser("~"))
    new_dir = os.path.join(base, "OhrHaKsav")
    old_dir = os.path.join(base, "KsavKooker")
    if os.path.exists(old_dir) and not os.path.exists(new_dir):
        try:
            import shutil
            shutil.copytree(old_dir, new_dir)
        except Exception:
            pass
    return new_dir

SETTINGS_PATH = os.path.join(get_app_data_dir(), "ui_settings.json")

STRINGS = {
    "en": {
        # App brand
        "app_title": "Ohr HaKsav  •  Offline Torah Notes & Hebrew Handwriting OCR Studio",
        "brand_name": "Ohr HaKsav",
        "brand_subtitle": "אור הכתב",

        # Main Menu Bar
        "menu_file": "File",
        "menu_file_add": "Add Notebook Pages... (Ctrl+O)",
        "menu_file_remove": "Remove Selected Page (Del)",
        "menu_file_clear": "Clear All Pages",
        "menu_file_export_word": "Export to Microsoft Word (.docx)... (Ctrl+E)",
        "menu_file_export_txt": "Export to Plain Text (.txt)...",
        "menu_file_exit": "Exit (Alt+F4)",

        "menu_scan": "Scan && OCR",
        "menu_scan_current": "Scan Current Page (F5)",
        "menu_scan_all": "Scan All Pages (Shift+F5)",
        "menu_scan_enhance": "Enhance Ink / High Contrast",

        "menu_learning": "Learning && Profiles",
        "menu_learning_save": "Save Current Corrections (Ctrl+L)",
        "menu_learning_studio": "Memory Studio (Rules & Backups)... (Ctrl+M)",
        "menu_learning_new_profile": "Create New Profile...",

        "menu_view": "View",
        "menu_view_rotate_cw": "Rotate 90° Clockwise (Ctrl+])",
        "menu_view_rotate_ccw": "Rotate 90° Counter-Clockwise (Ctrl+[)",
        "menu_view_zoom_in": "Zoom In (Ctrl++)",
        "menu_view_zoom_out": "Zoom Out (Ctrl+-)",
        "menu_view_fit": "Fit Window (Ctrl+0)",
        "menu_view_theme": "Toggle Dark / Light Theme (Ctrl+T)",
        "menu_view_stats": "Show Statistics & Details (Ctrl+Shift+S)",

        "menu_language": "Language",
        "menu_lang_en": "English",
        "menu_lang_he": "עברית (Hebrew)",

        "menu_help": "Help",
        "menu_help_guide": "User Guide & Tips (F1)",
        "menu_help_about": "About Ohr HaKsav...",
        "menu_help_check_updates": "Check for Updates... (Ctrl+U)",

        # Update Dialog
        "update_dialog_title": "Check for Updates",
        "update_tab_status": "Update Status",
        "update_tab_settings": "Update Source & Settings",
        "update_curr_version": "Installed Version: v{version}",
        "update_checking_msg": "Checking for updates from {source}...",
        "update_up_to_date_hdr": "You're Running the Latest Version!",
        "update_up_to_date_sub": "Ohr HaKsav v{version} is up to date. No updates are currently needed.",
        "update_available_hdr": "⚡ New Version Available: v{version}",
        "update_release_date": "Released: {date}",
        "update_whats_new": "What's New in This Release:",
        "update_btn_check_again": "Check Again",
        "update_btn_run_installer": "🚀 Launch Installer Now",
        "update_btn_open_folder": "📁 Open Staging Folder",
        "update_btn_open_web": "🌐 Open Release on GitHub",
        "update_btn_close": "Close",
        "update_err_hdr": "Unable to Check for Updates",
        "update_err_folder_not_found": "Update directory not found: {folder}",
        "update_err_no_version_json": "version.json was not found in directory: {folder}",
        "update_err_invalid_data": "Received invalid update information from server.",
        "update_err_network": "Network connection error: {err}",
        "update_source_group": "Select Where to Look for Updates:",
        "update_source_web": "Official GitHub Cloud (Online)",
        "update_source_web_desc": "Checks GitHub for the latest official public releases (requires internet connection).",
        "update_source_local": "Local Network Share / Folder / USB (Offline & Domain)",
        "update_source_local_desc": "Checks a local folder or UNC server share (e.g. \\\\newltcserver\\share or M:\\...) containing version.json and OhrHaKsav_Setup.exe.",
        "update_folder_path_lbl": "Network / Local Staging Folder Path:",
        "update_folder_browse_btn": "Browse...",
        "update_auto_check": "Automatically check for updates on startup",
        "update_save_settings_btn": "Save Settings & Check Now",
        "update_prompt_close_title": "Launch Installer",
        "update_prompt_close_msg": "The installer is about to launch. Would you like to close Ohr HaKsav now so the upgrade can proceed smoothly?",
        
        # Top toolbar
        "btn_attach": "📁 Attach Pages",
        "btn_add_pages_short": "Add Pages",
        "btn_scan": "⚡ Scan Current Page",
        "btn_scan_menu": "Scan ▾",
        "btn_scan_current_opt": "⚡ Scan Current Page (F5)",
        "btn_scan_all_opt": "⚡⚡ Scan All Pages (Shift+F5)",
        "btn_scan_tooltip": "Run offline neural OCR recognition on the active page",
        "btn_scan_all": "⚡⚡ Scan All Pages",
        "btn_scan_all_tooltip": "Batch-scan all attached notebook pages sequentially",
        "btn_learn": "💾 Save & Learn",
        "btn_learn_short": "Save && Learn Mistakes",
        "btn_learn_tooltip": "Save your proofreading edits and absorb corrections into the mistake memory bank",
        "btn_export": "📝 Export to Word (.docx)",
        "btn_export_menu": "Export ▾",
        "btn_export_word_opt": "📝 Microsoft Word (.docx)...",
        "btn_export_txt_opt": "📄 Plain Text (.txt)...",
        "btn_export_tooltip": "Export transcribed pages to Word (.docx) or Text (.txt)",
        "lbl_profile": "Profile:",
        "profile_tooltip": "Active handwriting profile (click to switch writer or manage rules)",
        "btn_new_profile_tooltip": "Create a new handwriting profile",
        "btn_memory": "🧠 Memory",
        "btn_memory_short": "Memory",
        "btn_memory_tooltip": "Manage learned rules, handwriting profiles, backups, and restores",
        "btn_theme": "🌓 Theme",
        "btn_theme_tooltip": "Toggle between dark and light themes",
        "btn_lang": "🌐 עברית",
        "btn_lang_tooltip": "Switch UI language to Hebrew / החלף ממשק לעברית",
        "btn_about": "ℹ",
        "btn_about_tooltip": "About Ohr HaKsav and version information",

        # Sidebar
        "sidebar_title": "Notebook Pages",
        "sidebar_add_tooltip": "Attach new photos",
        "sidebar_remove_tooltip": "Remove selected page",
        "btn_add_short": "+ Add",
        "btn_del_short": "Delete",
        "page_status_ready": "Ready to scan",
        "page_status_processing": "Processing OCR...",
        "page_status_scanned": "Scanned successfully ✓",
        "page_status_error": "Scan error",

        # Viewer panel
        "viewer_title": "Page Image",
        "btn_cw": "↻ 90°",
        "btn_cw_tooltip": "Rotate clockwise",
        "btn_ccw": "↺ 90°",
        "btn_ccw_tooltip": "Rotate counter-clockwise",
        "btn_contrast": "✨ Ink Enhancer",
        "btn_contrast_tooltip": "Enhance contrast for faint pencil or light pen ink",
        "btn_fit": "⛶ Fit",
        "btn_fit_tooltip": "Fit image to window",
        "btn_zoom_in_tooltip": "Zoom in",
        "btn_zoom_out_tooltip": "Zoom out",

        # Editor panel
        "editor_title": "Transcribed Notes & Proofreader (RTL)",
        "editor_quick_abbr": "Top:",
        "editor_workflow_hint": "💡 Proofreading Workflow: Correct any misread words in the editor, then click '🎓 Save & Learn Mistakes' to train future scans.",
        "editor_more_abbr": "More ▾",
        "abbr_menu_title": "⚡ Torah Abbreviations ▾",
        "abbr_group_seforim": "Seforim & Rishonim (ספרים וראשונים)",
        "abbr_group_talmud": "Talmudic Terms (לשונות הש\"ס)",
        "editor_stats": "Words: {words:,} | Characters: {chars:,} | Lines: {lines:,}",
        "editor_diff_ready": "Corrections detected: {count} (Ready to learn ✓)",
        "editor_diff_none": "No edits made yet",

        # Status bar
        "status_ready": "Ready. Drag or attach photos of handwritten notes.",
        "status_switched_profile": "Switched handwriting profile to: {name}",
        "status_created_profile": "Created new active profile: {name}",
        "status_active_rules": "Active Rules: {count:,} [{profile}]{stack_info}",
        "status_stack_info": " (Stacked {count} profiles)",

        # Dialogs - Word Export
        "export_dialog_title": "Export to Word (.docx)",
        "export_title_prompt": "Main document title:",
        "export_default_title": "Shiur Notes",
        "export_subtitle_prompt": "Topic / Tractate / Date (optional):",
        "export_author_prompt": "Lecturer or author name (optional):",
        "export_filter": "Word Documents (*.docx)",
        "export_success_title": "Export Successful!",
        "export_success_msg": "Document saved successfully to:\n{path}\n\nWould you like to open the document now?",

        # Dialogs - Memory & Profiles Studio
        "dict_window_title": "Memory Studio, Profiles & Backup — Ohr HaKsav",
        "dict_header_title": "Handwriting Memory & Profile Studio",
        "dict_active_prof_lbl": "Active Profile for editing and learning: {name}",
        "dict_quick_backup_btn": "⚡ Quick Backup",
        "dict_quick_backup_tooltip": "Instant timestamped backup of the active profile",
        "dict_tab_rules": "📚 Learned Rules in Profile",
        "dict_tab_profiles": "👥 Profiles & Scribes",
        "dict_tab_backup": "💾 Backup & Restore",
        "dict_search_placeholder": "🔍 Search rules or words...",
        "dict_btn_add_rule": "+ Add New Rule",
        "dict_rules_header_id": "ID",
        "dict_rules_header_raw": "Original OCR Text (Error)",
        "dict_rules_header_corr": "Learned Correction",
        "dict_rules_header_count": "Times Seen",
        "dict_rules_header_active": "Active",
        "dict_rules_total": "Total rules in current profile: {count:,}",
        "dict_btn_delete_rule": "Delete Selected Rule",
        "dict_profiles_desc": "💡 Manage isolated learning profiles for different scribes, students, or notebooks.\nCheck 'Stack in OCR' to apply rules from multiple profiles simultaneously during scans.",
        "dict_profiles_header_enabled": "Stack in OCR",
        "dict_profiles_header_name": "Profile Name",
        "dict_profiles_header_desc": "Description",
        "dict_profiles_header_count": "Rule Count",
        "dict_profiles_header_status": "Status",
        "dict_profiles_status_primary": "🟢 Primary Active",
        "dict_profiles_status_secondary": "Secondary",
        "dict_btn_new_prof": "+ New Profile",
        "dict_btn_set_active": "🎯 Set as Active",
        "dict_btn_dup_prof": "📋 Duplicate",
        "dict_btn_edit_prof": "✏️ Rename",
        "dict_btn_merge_prof": "🔗 Merge into Active",
        "dict_btn_merge_prof_tooltip": "Merge all learned rules from this profile into the active profile",
        "dict_btn_del_prof": "🗑️ Delete",
        "dict_grp_backup": "Profile Data Backup",
        "dict_lbl_backup_desc": "A complete backup preserves all learned rules, abbreviations, and scribe preferences in a portable file.",
        "dict_btn_quick_backup": "⚡ Quick Backup Now",
        "dict_btn_save_as": "💾 Save Backup to File...",
        "dict_btn_open_folder": "📂 Open Backups Folder",
        "dict_grp_restore": "Restore & Merge from Backup",
        "dict_lbl_restore_desc": "Restore from a backup archive (.ksavbackup / .db / .json). A safety snapshot is automatically created before any restoration.",
        "dict_btn_restore_new": "➕ Restore as New Profile...",
        "dict_btn_restore_new_tooltip": "Restores the backup file as a new independent profile without touching existing profiles",
        "dict_btn_restore_overwrite": "🔄 Overwrite Active Profile...",
        "dict_btn_restore_overwrite_tooltip": "Replaces the current active profile's rules with the backup file data",
        "dict_btn_merge_file": "🧩 Merge Rules from File...",
        "dict_btn_merge_file_tooltip": "Imports and combines rules from another profile without deleting your existing rules",
        "dict_grp_share": "Export & Share Rules (JSON)",
        "dict_lbl_share_desc": "Export rules to a readable JSON file for easy sharing with colleagues or students.",
        "dict_btn_export_json": "📤 Export Rules to JSON...",
        "dict_btn_import_json": "📥 Import Rules from JSON...",
        "dict_btn_close": "Close",

        # Learning feedback
        "learn_success_title": "Learning Complete ✓",
        "learn_success_msg": "Successfully learned and recorded {count} new correction rules in memory profile '{profile}'!\n\nExamples learned:\n{examples}\nThese corrections will now be applied automatically to all future scans!",
        "learn_none_title": "Memory",
        "learn_none_msg": "No new corrections detected on this page (everything is already recorded in memory).",

        # About Dialog
        "about_title": "About Ohr HaKsav",
        "about_version": "Version {version} (Offline Edition)",
        "about_desc": "Ohr HaKsav (אור הכתב) is an intelligent, 100% offline desktop application built for yeshiva students, rebbeim, and scholars to transcribe handwritten Hebrew notes, proofread side-by-side, and export clean formatted Word documents.",
        "about_features": "• 100% Offline PyTorch Neural OCR (Mishkefet-v1)\n• Multi-User Handwriting Profiles & Stacking\n• Self-Learning Mistake Memory Engine\n• Instant One-Click Backup, Restore & Knowledge Merging\n• High-DPI Document Viewer with Ink Enhancer\n• Formatted Right-to-Left Word (.docx) Export"
    },

    "he": {
        # App brand
        "app_title": "אור הכתב  •  אולפן זיהוי ועריכת כתב יד ושיעורי תורה אופליין",
        "brand_name": "אור הכתב",
        "brand_subtitle": "Ohr HaKsav",

        # Main Menu Bar
        "menu_file": "קובץ",
        "menu_file_add": "הוסף עמודי מחברת... (Ctrl+O)",
        "menu_file_remove": "הסר עמוד נבחר (Del)",
        "menu_file_clear": "נקה את כל העמודים",
        "menu_file_export_word": "ייצא למסמך וורד (.docx)... (Ctrl+E)",
        "menu_file_export_txt": "ייצא לקובץ טקסט (.txt)...",
        "menu_file_exit": "יציאה (Alt+F4)",

        "menu_scan": "סריקה ופענוח",
        "menu_scan_current": "סרוק עמוד נוכחי (F5)",
        "menu_scan_all": "סרוק את כל העמודים (Shift+F5)",
        "menu_scan_enhance": "הדגשת דיו / ניגודיות גבוהה",

        "menu_learning": "פרופילים וזיכרון",
        "menu_learning_save": "שמור תיקונים לזיכרון (Ctrl+L)",
        "menu_learning_studio": "מרכז הזיכרון והפרופילים... (Ctrl+M)",
        "menu_learning_new_profile": "צור פרופיל כתב יד חדש...",

        "menu_view": "תצוגה",
        "menu_view_rotate_cw": "סובב 90° עם כיוון השעון (Ctrl+])",
        "menu_view_rotate_ccw": "סובב 90° נגד כיוון השעון (Ctrl+[)",
        "menu_view_zoom_in": "הגדל תצוגה (Ctrl++)",
        "menu_view_zoom_out": "הקטן תצוגה (Ctrl+-)",
        "menu_view_fit": "התאם לחלון (Ctrl+0)",
        "menu_view_theme": "החלף ערכת נושא (Ctrl+T)",
        "menu_view_stats": "הצג סטטיסטיקות ופרטי מסמך (Ctrl+Shift+S)",

        "menu_language": "שפה",
        "menu_lang_en": "English (אנגלית)",
        "menu_lang_he": "עברית (ברירת מחדל בעברית)",

        "menu_help": "עזרה",
        "menu_help_guide": "מדריך למשתמש וקיצורים (F1)",
        "menu_help_about": "אודות אור הכתב...",
        "menu_help_check_updates": "בדוק עדכונים... (Ctrl+U)",

        # Update Dialog
        "update_dialog_title": "בדיקת עדכונים",
        "update_tab_status": "סטטוס עדכון",
        "update_tab_settings": "הגדרות ומקור עדכון",
        "update_curr_version": "גרסה מותקנת: v{version}",
        "update_checking_msg": "בודק עדכונים מתוך {source}...",
        "update_up_to_date_hdr": "התוכנה מעודכנת לחלוטין!",
        "update_up_to_date_sub": "אור הכתב גרסה {version} היא הגרסה העדכנית ביותר. אין צורך בעדכון.",
        "update_available_hdr": "⚡ גרסה חדשה זמינה: v{version}",
        "update_release_date": "תאריך שחרור: {date}",
        "update_whats_new": "מה חדש בגרסה זו:",
        "update_btn_check_again": "בדוק שוב",
        "update_btn_run_installer": "🚀 הפעל התקנת עדכון כעת",
        "update_btn_open_folder": "📁 פתח תיקיית עדכון",
        "update_btn_open_web": "🌐 פתח דף שחרור ב-GitHub",
        "update_btn_close": "סגור",
        "update_err_hdr": "לא ניתן לבדוק עדכונים",
        "update_err_folder_not_found": "תיקיית העדכון לא נמצאה: {folder}",
        "update_err_no_version_json": "קובץ version.json לא נמצא בתיקייה: {folder}",
        "update_err_invalid_data": "התקבלו נתוני עדכון לא תקינים.",
        "update_err_network": "שגיאת חיבור רשת: {err}",
        "update_source_group": "בחר היכן לחפש עדכונים:",
        "update_source_web": "ענן GitHub הרשמי (אונליין)",
        "update_source_web_desc": "בודק ב-GitHub עדכונים רשמיים חדשים (דורש חיבור אינטרנט).",
        "update_source_local": "שיתוף רשת מקומי / שרת / USB (אופליין ודומיין)",
        "update_source_local_desc": "בודק תיקייה מקומית או שיתוף שרת UNC (כגון \\\\newltcserver\\share או M:\\...) המכיל version.json ואת קובץ ההתקנה.",
        "update_folder_path_lbl": "נתיב תיקיית רשת או שיתוף שרת:",
        "update_folder_browse_btn": "עיון...",
        "update_auto_check": "בדוק עדכונים אוטומטית בהפעלת התוכנה",
        "update_save_settings_btn": "שמור הגדרות ובדוק כעת",
        "update_prompt_close_title": "הפעלת התקנה",
        "update_prompt_close_msg": "אשף ההתקנה עומד לפעול. האם לסגור את אור הכתב כעת כדי שהעדכון יוכל להתבצע באופן תקין?",

        # Top toolbar
        "btn_attach": "📁 צרף תמונות",
        "btn_add_pages_short": "הוסף עמודים",
        "btn_scan": "⚡ סרוק עמוד נוכחי",
        "btn_scan_menu": "סריקה ▾",
        "btn_scan_current_opt": "⚡ סרוק עמוד נוכחי (F5)",
        "btn_scan_all_opt": "⚡⚡ סרוק את כל העמודים (Shift+F5)",
        "btn_scan_tooltip": "הפעל זיהוי כתב יד OCR אופליין עבור העמוד הנוכחי",
        "btn_scan_all": "⚡⚡ סרוק הכל",
        "btn_scan_all_tooltip": "סרוק ברצף את כל העמודים שצורפו",
        "btn_learn": "💾 שמור שינויים",
        "btn_learn_short": "שמור ולמד שגיאות",
        "btn_learn_tooltip": "שומר את העריכה ורושם בזיכרון את כל המילים שתוקנו כדי לתקן אותן אוטומטית בעתיד",
        "btn_export": "📝 ייצוא לוורד (.docx)",
        "btn_export_menu": "ייצוא ▾",
        "btn_export_word_opt": "📝 מסמך וורד (.docx)...",
        "btn_export_txt_opt": "📄 קובץ טקסט (.txt)...",
        "btn_export_tooltip": "ייצא את כל העמודים למסמך Word או לקובץ טקסט",
        "lbl_profile": "פרופיל:",
        "profile_tooltip": "פרופיל כתב היד הפעיל (לחץ להחלפת פרופיל או ניהול כללים)",
        "btn_new_profile_tooltip": "צור פרופיל כתב יד חדש",
        "btn_memory": "🧠 מרכז זיכרון",
        "btn_memory_short": "מרכז זיכרון",
        "btn_memory_tooltip": "פתח את מנהל הזיכרון, הפרופילים, הגיבוי והשחזור",
        "btn_theme": "🌓 ערכת נושא",
        "btn_theme_tooltip": "החלף בין ערכת נושא כהה לבהירה",
        "btn_lang": "🌐 English",
        "btn_lang_tooltip": "Switch UI language to English / החלף ממשק לאנגלית",
        "btn_about": "ℹ",
        "btn_about_tooltip": "אודות אור הכתב ומידע על הגרסה",

        # Sidebar
        "sidebar_title": "עמודי המחברת",
        "sidebar_add_tooltip": "הוסף עמודים",
        "sidebar_remove_tooltip": "הסר עמוד נבחר",
        "btn_add_short": "+ הוסף",
        "btn_del_short": "מחק",
        "page_status_ready": "מוכן לסריקה",
        "page_status_processing": "סורק ב-OCR...",
        "page_status_scanned": "נסרק בהצלחה ✓",
        "page_status_error": "שגיאה בסריקה",

        # Viewer panel
        "viewer_title": "תצלום הדף",
        "btn_cw": "↻ 90°",
        "btn_cw_tooltip": "סובב ימינה עם כיוון השעון",
        "btn_ccw": "↺ 90°",
        "btn_ccw_tooltip": "סובב שמאלה נגד כיוון השעון",
        "btn_contrast": "✨ הדגש דיו",
        "btn_contrast_tooltip": "הגבר ניגודיות עבור עפרון או עט בהיר",
        "btn_fit": "⛶ התאם",
        "btn_fit_tooltip": "התאם גודל לחלון",
        "btn_zoom_in_tooltip": "הגדל",
        "btn_zoom_out_tooltip": "הקטן",

        # Editor panel
        "editor_title": "תמליל ועריכה (מימין לשמאל)",
        "editor_quick_abbr": "ראשי תיבות:",
        "editor_more_abbr": "עוד ▾",
        "abbr_menu_title": "⚡ קיצורים תורניים ▾",
        "abbr_group_seforim": "ספרים וראשונים",
        "abbr_group_talmud": "לשונות הש\"ס",
        "editor_stats": "מילים: {words:,} | תווים: {chars:,} | שורות: {lines:,}",
        "editor_diff_ready": "תיקונים שזוהו: {count} (מוכן ללמידה ✓)",
        "editor_diff_none": "טרם בוצעו תיקונים",

        # Status bar
        "status_ready": "מוכן לפעולה. גרור או צרף תמונות של מחברת השיעורים.",
        "status_switched_profile": "הוחלף לפרופיל כתב יד: {name}",
        "status_created_profile": "נוצר פרופיל פעיל חדש: {name}",
        "status_active_rules": "כללים פעילים: {count:,} [{profile}]{stack_info}",
        "status_stack_info": " (משולב {count} פרופילים)",

        # Dialogs - Word Export
        "export_dialog_title": "ייצוא לוורד (.docx)",
        "export_title_prompt": "כותרת ראשית למסמך:",
        "export_default_title": "שיעורים וחידושי תורה",
        "export_subtitle_prompt": "נושא / מסכת / תאריך (אופציונלי):",
        "export_author_prompt": "שם בעל השיעור או המחבר (אופציונלי):",
        "export_filter": "מסמכי וורד (*.docx)",
        "export_success_title": "הייצוא הושלם בהצלחה!",
        "export_success_msg": "המסמך נשמר בהצלחה בנתיב:\n{path}\n\nהאם ברצונך לפתוח את המסמך כעת?",

        # Dialogs - Memory & Profiles Studio
        "dict_window_title": "מנהל הזיכרון, הפרופילים והגיבוי — Ohr HaKsav",
        "dict_header_title": "מנהל זיכרון ופרופילי כתב יד",
        "dict_active_prof_lbl": "פרופיל פעיל לעריכה ושמירה: {name}",
        "dict_quick_backup_btn": "⚡ גבה עכשיו",
        "dict_quick_backup_tooltip": "יצירת גיבוי מהיר של הפרופיל הפעיל",
        "dict_tab_rules": "📚 כללים נלמדים בפרופיל",
        "dict_tab_profiles": "👥 פרופילים ומשתמשים",
        "dict_tab_backup": "💾 גיבוי ושחזור",
        "dict_search_placeholder": "🔍 חיפוש כלל או מילה...",
        "dict_btn_add_rule": "+ הוסף כלל חדש",
        "dict_rules_header_id": "מזהה",
        "dict_rules_header_raw": "טקסט מקורי (שגיאת OCR)",
        "dict_rules_header_corr": "תיקון נלמד",
        "dict_rules_header_count": "פעמים שנצפה",
        "dict_rules_header_active": "פעיל",
        "dict_rules_total": "סה\"כ כללים בפרופיל הנוכחי: {count:,}",
        "dict_btn_delete_rule": "מחק כלל נבחר",
        "dict_profiles_desc": "💡 ניתן לנהל פרופילי לימוד נפרדים עבור כל כותב, תלמיד או מחברת.\nסמן בתיבת הסימון 'משולב בסריקה' כדי להחיל כללים ממספר פרופילים בו-זמנית בעת סריקת דפים.",
        "dict_profiles_header_enabled": "משולב בסריקה",
        "dict_profiles_header_name": "שם הפרופיל",
        "dict_profiles_header_desc": "תיאור",
        "dict_profiles_header_count": "כמות כללים",
        "dict_profiles_header_status": "סטטוס",
        "dict_profiles_status_primary": "🟢 פעיל ראשי",
        "dict_profiles_status_secondary": "משני",
        "dict_btn_new_prof": "+ פרופיל חדש",
        "dict_btn_set_active": "🎯 קבע כפרופיל פעיל",
        "dict_btn_dup_prof": "📋 שכפל",
        "dict_btn_edit_prof": "✏️ ערוך שם",
        "dict_btn_merge_prof": "🔗 מזג לפרופיל הפעיל",
        "dict_btn_merge_prof_tooltip": "מיזוג כל הכללים מהפרופיל הנבחר אל תוך הפרופיל הפעיל",
        "dict_btn_del_prof": "🗑️ מחק",
        "dict_grp_backup": "גיבוי ושמירת נתונים",
        "dict_lbl_backup_desc": "גיבוי מלא שומר את כל הכללים הנלמדים, ראשי התיבות, והעדפות הכתיב בקובץ עצמאי.",
        "dict_btn_quick_backup": "⚡ גיבוי מהיר עכשיו",
        "dict_btn_save_as": "💾 שמור גיבוי לקובץ...",
        "dict_btn_open_folder": "📂 פתח תיקיית גיבויים",
        "dict_grp_restore": "שחזור ומיזוג מגיבוי",
        "dict_lbl_restore_desc": "שחזור מקובץ גיבוי קיים (.ksavbackup / .db / .json). המערכת תבצע אוטומטית גיבוי בטיחותי לפני השחזור.",
        "dict_btn_restore_new": "➕ שחזר כפרופיל חדש...",
        "dict_btn_restore_new_tooltip": "פותח את קובץ הגיבוי כפרופיל עצמאי חדש מבלי לגעת בפרופילים הקיימים",
        "dict_btn_restore_overwrite": "🔄 שחזר לתוך הפרופיל הפעיל...",
        "dict_btn_restore_overwrite_tooltip": "מחליף את נתוני הפרופיל הפעיל בנתוני הגיבוי",
        "dict_btn_merge_file": "🧩 מזג כללים מקובץ חיצוני...",
        "dict_btn_merge_file_tooltip": "מוסיף את הכללים מקובץ חיצוני אל הפרופיל הפעיל מבלי למחוק כללים קיימים",
        "dict_grp_share": "ייצוא ושיתוף כללים (JSON)",
        "dict_lbl_share_desc": "ייצוא הכללים לקובץ JSON קריא לשיתוף קל עם חברים, תלמידים, או מחשבים אחרים.",
        "dict_btn_export_json": "📤 ייצוא כללים לקובץ JSON...",
        "dict_btn_import_json": "📥 ייבוא כללים מקובץ JSON...",
        "dict_btn_close": "סגור",

        # Learning feedback
        "learn_success_title": "הלמידה הושלמה בהצלחה ✓",
        "learn_success_msg": "נלמדו ונרשמו בהצלחה {count} כללי תיקון חדשים בזיכרון המערכת בפרופיל '{profile}'!\n\nדוגמאות שנלמדו:\n{examples}\nתיקונים אלו יחולו אוטומטית בכל הסריקות הבאות!",
        "learn_none_title": "זיכרון",
        "learn_none_msg": "לא זוהו מילים חדשות ללמידה בעמוד זה (הכל כבר מעודכן בזיכרון).",

        # About Dialog
        "about_title": "אודות אור הכתב",
        "about_version": "גרסה {version} (מהדורה אופליין)",
        "about_desc": "אור הכתב היא תוכנה חכמה הפועלת 100% אופליין ללא אינטרנט, המיועדת לתלמידי ישיבות, רבנים וחוקרים לפענוח תצלומי מחברות כתב יד עברי, הגהה ועריכה זה לצד זה, וייצוא למסמכי Word מעוצבים.",
        "about_features": "• מנוע זיהוי עצבי PyTorch אופליין (Mishkefet-v1)\n• ניהול ושילוב פרופילי כתב יד למספר כותבים\n• מנוע זיכרון ולמידה עצמית משגיאות והגהות\n• מרכז גיבוי, שחזור ומיזוג כללים מהיר בלחיצה אחת\n• תצוגת מסמכים חדה ברזולוציה גבוהה עם מחדד דיו\n• ייצוא ישיר למסמכי Microsoft Word (.docx) מעוצבים"
    }
}


class I18nManager:
    _instance = None

    def __init__(self):
        self.current_lang = "en"  # English by default
        self._load_settings()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = I18nManager()
        return cls._instance

    def _load_settings(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    self.current_lang = cfg.get("language", "en")
        except Exception:
            self.current_lang = "en"

    def save_settings(self):
        try:
            os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump({"language": self.current_lang}, f, indent=2)
        except Exception:
            pass

    def t(self, key: str, **kwargs) -> str:
        lang_dict = STRINGS.get(self.current_lang, STRINGS["en"])
        val = lang_dict.get(key, STRINGS["en"].get(key, key))
        if kwargs:
            try:
                return val.format(**kwargs)
            except Exception:
                return val
        return val

    def toggle_language(self) -> str:
        self.current_lang = "he" if self.current_lang == "en" else "en"
        self.save_settings()
        return self.current_lang

    def set_language(self, lang: str):
        if lang in ("en", "he"):
            self.current_lang = lang
            self.save_settings()


def t(key: str, **kwargs) -> str:
    """Convenience shortcut to translate a key."""
    return I18nManager.instance().t(key, **kwargs)


def get_current_language() -> str:
    """Get currently active language code ('en' or 'he')."""
    return I18nManager.instance().current_lang
