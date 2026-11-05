# Release Notes — Ksav Kooker (כתב קוקער)

## [v1.1.1] — 2026-11-04

### Explanatory Title:
**English Default UI Localization with Dynamic Language Toggle (🌐 עברית / English)**

### Summary in Plain English:
Version `v1.1.1` sets English as the default interface language across all application menus, buttons, toolbars, tooltips, dialogs, and the Windows Setup Wizard, in accordance with standard Windows productivity software conventions. For users who prefer a Hebrew interface, a prominent **"🌐 עברית / English"** language toggle has been added to the top toolbar, enabling seamless, instant runtime switching between English and Hebrew without restarting the app.

### What Changed & What Is Included:
1. **English Default User Interface (`ui/i18n.py`)**:
   - Built a comprehensive internationalization engine defaulting to clean, modern English.
   - All top-toolbar action buttons, sidebar headers, viewer controls, status messages, and proofreader tools display in English by default.
2. **Dynamic Language Switcher**:
   - Added a **"🌐 עברית / English"** button in the main top bar.
   - Clicking the toggle immediately retranslates all menus, toolbars, buttons, tooltips, and dialogs on-the-fly and remembers the user's preference in `%APPDATA%\KsavKooker\ui_settings.json`.
3. **English Windows Setup Wizard (`installer/setup_gui.py`)**:
   - Updated the setup wizard to present in clear, professional English by default with standard navigation controls (`Next >`, `< Back`, `Finish`, `Cancel`).
4. **Preserved Hebrew RTL Proofreader & Export**:
   - The document editor remains optimized for Right-to-Left Hebrew typing and Talmudic abbreviation expansion, while its surrounding statistical indicators and controls are in English.
   - Word (`.docx`) export remains formatted Right-to-Left with traditional David Hebrew typography.

---

## [v1.1.0] — 2026-11-04

### Explanatory Title:
**Multi-User Handwriting Profiles, Multi-Profile Stacking During OCR, and One-Click Backup/Restore Studio**

### Summary in Plain English:
Version `v1.1.0` introduces comprehensive multi-user handwriting profile management, multi-profile stacking during OCR, and automated backup/restore tools for Ksav Kooker. Different students, scribes, or family members often have distinct handwriting quirks and preferred abbreviations; users can now create isolated profiles for each person, switch profiles on-the-fly, or even stack multiple profiles together so the OCR engine checks rules from multiple people simultaneously during a scan. Furthermore, users can now create instant timestamped backups, save backups to USB or network storage, restore profiles with safety pre-backups, and merge colleagues' learned rules directly into their active profile.

### What Changed & What Is Included:
1. **Multi-User Handwriting Profiles (`core/learning_engine.py`)**:
   - Store learned corrections in isolated databases per scribe/student/book inside `%APPDATA%\KsavKooker\profiles\`.
   - Seamlessly creates, renames, duplicates, and deletes profiles.
   - Backward-compatible: Automatically migrates existing single-database corrections to the default profile without data loss.
2. **Top Toolbar Quick Profile Selector (`ui/main_window.py`)**:
   - Added a profile dropdown and quick "+" button right in the main window header.
   - Switch active profiles instantly while transcribing without needing to restart the app.
3. **Multi-Profile Stacking (Simultaneous Multi-Person Rules)**:
   - When transcribing notes, users can check multiple profiles in the Profile Manager.
   - Ksav Kooker dynamically stacks rules from all checked profiles during OCR, allowing a student to benefit from both a shared Yeshiva profile and their personal handwriting profile simultaneously.
4. **Backup & Restore Center (`ui/dictionary_dialog.py`)**:
   - **Quick Backup**: One-click instant timestamped backup saved to `%APPDATA%\KsavKooker\backups`.
   - **Save Backup As**: Export `.ksavbackup` files directly to a USB flash drive, external drive, or cloud folder.
   - **Safe Restore**: Restore any `.ksavbackup`, `.db`, or `.json` file as a new profile or over the active profile (with automatic safety pre-backup).
   - **Rule Merging**: Import and combine a colleague's or teacher's rules into your active profile without overwriting existing rules.
5. **Modern Tabbed Memory Studio**:
   - Redesigned the Memory Manager dialog into three organized tabs:
     - **Tab 1: 📚 כללים נלמדים בפרופיל (Active Profile Rules)**
     - **Tab 2: 👥 פרופילים ומשתמשים (Profile Manager & Stacking Checkboxes)**
     - **Tab 3: 💾 גיבוי ושחזור (Backup, Restore & JSON Sharing)**
6. **Installer Package Optimization (`build_exe.py`)**:
   - Excluded unused sub-packages (`transformers`, `scipy`, `matplotlib`, `pandas`, `onnxruntime`, `av`), significantly trimming the standalone installer and download size from 568 MB to 409 MB.

---

## [v1.0.1] — 2026-11-04

### Explanatory Title:
**Brand Visual Upgrade: Integrating Option 2 (Dual-Page Transformation Stream) Across Application, Icons, and Setup Wizard**

### Summary in Plain English:
In response to user feedback, version `v1.0.1` transitions the visual identity of **Ksav Kooker** to the **"Dual-Page Digital Transformation Stream"** 3D design (Option 2). The new emblem represents the core mission of the software: taking personal handwritten yeshiva notes and watching them dynamically transform into clean, structured, printed pages.

---

## [v1.0.0] — 2026-11-04 (Initial Release)

### Explanatory Title:
**Initial Release of Ksav Kooker: Offline Hebrew Handwriting & Torah Notes OCR Desktop Studio with Continuous Self-Learning Memory, 3D Emblem Branding, and Word Export**
