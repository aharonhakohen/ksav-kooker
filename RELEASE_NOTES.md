# Release Notes — Ksav Kooker (כתב קוקער)

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
   - Excluded unused sub-packages (`transformers`, `scipy`, `matplotlib`, `pandas`, `onnxruntime`, `av`), significantly trimming the standalone installer and download size.

---

## [v1.0.1] — 2026-11-04

### Explanatory Title:
**Brand Visual Upgrade: Integrating Option 2 (Dual-Page Transformation Stream) Across Application, Icons, and Setup Wizard**

### Summary in Plain English:
In response to user feedback, version `v1.0.1` transitions the visual identity of **Ksav Kooker** to the **"Dual-Page Digital Transformation Stream"** 3D design (Option 2). The new emblem represents the core mission of the software: taking personal handwritten yeshiva notes and watching them dynamically transform into clean, structured, printed pages.

### What Changed & What Is Included:
1. **Application Icon & Windows Shortcut Icon**:
   - Replaced `assets/ksav_kooker.ico` with high-resolution multi-size Windows icon slices (256x256 down to 16x16) generated from the Option 2 design.
   - All desktop and start menu shortcuts now display the new dual-page transformation icon.
2. **Startup Splash Screen**:
   - Integrated the new 3D emblem into the frameless splash screen, smoothly scaled with drop-shadow effects during neural engine warmup.
3. **Windows Setup Wizard GUI**:
   - Updated the installer welcome banner and completion screen in `installer/setup_gui.py` to showcase the new branding.
4. **About Dialog & Documentation**:
   - Updated the About dialog in `ui/about_dialog.py` and project README to showcase the new artwork.
5. **Standalone Installer & Packages Rebuilt**:
   - Re-compiled `KsavKooker_Setup.exe` (single-file offline setup wizard) and portable package `KsavKooker-v1.0.1-Windows.zip`.

---

## [v1.0.0] — 2026-11-04 (Initial Release)

### Explanatory Title:
**Initial Release of Ksav Kooker: Offline Hebrew Handwriting & Torah Notes OCR Desktop Studio with Continuous Self-Learning Memory, 3D Emblem Branding, and Word Export**

### Summary in Plain English:
This is the inaugural release of **Ksav Kooker** (`v1.0.0`), a specialized, 100% offline desktop application built for yeshiva students, rebbeim, and scholars to transcribe handwritten Hebrew notes (both Ashkenazi/Sefardi cursive and print), proofread them side-by-side with original photos, and export clean, formatted Microsoft Word documents (`.docx`).

### What Changed & What Is Included:
1. **100% Offline Neural Handwriting Recognition**:
   - Integrated the Mishkefet-v1 handwriting OCR model running completely offline on standard CPUs with zero internet required.
   - Built-in line segmentation and Hebrew language model word priors for deciphering cursive script and handwriting.
2. **Self-Learning Memory Engine**:
   - Created a persistent SQLite database that automatically compares your proofreading edits with the raw OCR output.
   - Extracts word and abbreviation substitutions (e.g. `קוס` -> `תוס'`, `רשל` -> `רגל`, `בסייד` -> `בס"ד`).
   - Automatically applies learned corrections to all subsequent scans so the app becomes smarter with each page scanned.
3. **Pre-Loaded Yeshiva / Rabbinic Lexicon**:
   - Seeded with over 50 of the most common Talmudic abbreviations (Roshei Teivot) and terms (רש"י, תוס', רמב"ם, ראב"ד, רי"ף, רא"ש, גמ', נפק"מ, קמ"ל, ח"נ, נ"ש, סד"א, ברה"ר, ברה"י, etc.).
4. **Interactive Document Viewer**:
   - High-resolution pan, smooth mouse-wheel zoom, and 90-degree clockwise / counter-clockwise rotation buttons to quickly orient phone photos.
   - High-contrast ink-enhancement filter to make faint pencil or faded ink legible.
5. **Hebrew Right-to-Left (RTL) Editor**:
   - Styled with Hebrew typography (David/Arial fonts), bidirectional cursor support, and a quick-insertion toolbar for common Yeshiva terms.
   - Live mistake tracking counter comparing current edits to raw scan.
6. **Microsoft Word (.docx) Exporter**:
   - Generates professionally styled Right-To-Left (RTL) `.docx` files with 1-inch margins, centered title headings, bold shiur markers, and notebook page breaks.
7. **Packaging & Distribution**:
   - Packaged offline self-extracting installer (`KsavKooker_Setup.exe`) and portable zip archive (`KsavKooker-v1.0.0-Windows.zip`).
