# Release Notes — Ksav Kooker (כתב קוקער)

## [v1.2.1] — 2026-11-05

### Explanatory Title:
**Light Mode Default UX, Domain Roaming Desktop/Start Menu Shortcuts, and Reliable Process Launching**

### Summary in Plain English:
Version `v1.2.1` addresses workstation installation issues in Windows Server domain environments (such as Torah U'Mesorah) and switches the default application theme to **Light Mode**. When installing on domain workstations with Folder Redirection or Roaming Profiles, the user's Desktop and Start Menu are often hosted on a network share (e.g. `\\newltcserver\userdata$\<user>\Desktop`). Previous versions attempted to write shortcuts to the local `C:\Users\<user>\Desktop` path, which is hidden by Windows Explorer. Version `v1.2.1` queries the Windows Shell APIs and Registry to resolve redirected network folders, OneDrive, and local paths, installing shortcuts in all active locations using native Windows Script Host (avoiding domain PowerShell restrictions). Furthermore, the installer now launches Ksav Kooker as an independent, detached process with the correct application working directory upon clicking **Finish**.

### What Changed & What Is Included:
1. **Light Mode Default Interface (`ui/main_window.py`)**:
   - The application now defaults to crisp, high-contrast Light Mode upon fresh launch.
   - Theme toggle button prominently displays a moon icon (`🌙`) in Light Mode and a sun icon (`☀`) in Dark Mode.
   - User theme preferences are automatically saved in `%APPDATA%\KsavKooker\ui_settings.json` and preserved across sessions.
2. **Windows Server Domain & Folder Redirection Support (`installer/setup_gui.py`)**:
   - Implemented `get_windows_desktop_dirs()` and `get_windows_start_menu_dirs()` querying `SHGetFolderPathW` (`CSIDL_DESKTOPDIRECTORY`, `CSIDL_PROGRAMS`) and Windows Explorer User Shell Folders.
   - Accurately detects and installs shortcuts to redirected domain server shares (e.g. `\\newltcserver\userdata$\...\Desktop`), OneDrive, and local directories simultaneously.
3. **Zero-Dependency Native Shortcut Creation**:
   - Replaced PowerShell with native Windows Script Host (`cscript //nologo`), ensuring shortcuts are created reliably even on domain workstations with restricted PowerShell execution policies or AppLocker rules.
4. **Reliable Post-Install App Launching**:
   - Placed an explicit **"Launch Ksav Kooker now"** checkbox directly on the final wizard page.
   - Application launch now uses `subprocess.Popen` with `DETACHED_PROCESS` and `CREATE_NEW_PROCESS_GROUP`, explicitly setting `cwd` to the application directory so `KsavKooker.exe` loads its dependencies and stays running when the installer exits.

---

## [v1.2.0] — 2026-11-05

### Explanatory Title:
**In-App Update Checker (GitHub Cloud & Local Network Share Channels) with Clean Upgrade Process**

### Summary in Plain English:
Version `v1.2.0` introduces a dedicated **"Check for Updates..."** tool inside the **Help** menu (<kbd>Ctrl+U</kbd>), paired with an intelligent upgrade engine that resolves file-locking conflicts and purges obsolete application binaries. Users and network administrators can configure where Ksav Kooker looks for updates: either from the official **GitHub Cloud** (for internet-connected systems) or from a **Local Network Share / Windows Server Domain Share / USB Drive** (such as `\\newltcserver\Installs\KsavKooker` or a mapped drive) for offline institutional environments. When upgrading via the setup executable, the installer automatically detects any active instance of Ksav Kooker and closes it, removes old binary files from the program directory, and ensures that personal handwriting profiles, mistake memories, custom dictionaries, and backups in `%APPDATA%` are completely preserved and untouched.

### What Changed & What Is Included:
1. **In-App Update Checker (`ui/update_dialog.py`)**:
   - Added **Help > Check for Updates...** (<kbd>Ctrl+U</kbd>) to the main menu bar.
   - Dual-channel update architecture:
     - **Official GitHub Cloud**: Fetches `version.json` over HTTPS and displays release notes and download links.
     - **Local Network Share / USB / Server Folder**: Scans a UNC path (e.g. `\\newltcserver\Installs\KsavKooker`) or local drive containing `version.json` and `KsavKooker_Setup.exe`.
   - Rich update card displaying the new version number, release date, plain-English summary, and bulleted features list.
   - One-click action buttons: Launch local installer directly or open the web release page.
   - User configuration saved to `%APPDATA%\KsavKooker\ui_settings.json`.
2. **Clean Upgrade Process & Process-Lock Protection (`installer/setup_gui.py`)**:
   - **Active Process Detection**: Setup checks if `KsavKooker.exe` is currently running and terminates it before extracting files, completely avoiding Windows `PermissionError` file-locking failures.
   - **Obsolete Binary Purge**: When upgrading over an existing installation, setup purges old application binaries (`_internal/`, old `.dll`, `.pyd`, and `.exe` files) before extracting the new release, preventing orphaned file bloat and library mismatch errors.
   - **Guaranteed User Data Isolation**: Explicitly isolates application program files from user data; all personal handwriting profiles, mistake memory rules, and backups stored in `%APPDATA%\KsavKooker` remain 100% untouched.
   - **Upgrade Mode Indicator**: The setup wizard displays a clear green confirmation banner when an existing installation is detected, assuring the user that their data is safe.
3. **Automated Deployment with `version.json` (`build_exe.py`)**:
   - Deploy script now copies `version.json` alongside `KsavKooker_Setup.exe` into destination staging folders (e.g. `M:\My Drive\Personal\Dovid Shmaryahu\Notes App`), enabling instant offline update checking across network workstations.

---

## [v1.1.2] — 2026-11-05

### Explanatory Title:
**High-Contrast Installer & Streamlined Studio UX Overhaul (Native Menu Bar, Stacked Dropdowns, Fixed Font Clipping)**

### Summary in Plain English:
Version `v1.1.2` delivers a comprehensive visual and user experience overhaul for **Ksav Kooker**. It resolves the "washed out" low-contrast text reported in the Windows Setup Wizard, ensures the custom 3D dual-page emblem is always displayed, and reorganizes the main studio interface to eliminate button squishing, font truncation, and empty square character boxes. Actions have been grouped into intuitive stacked dropdowns (`⚡ Scan ▾`, `📄 Export ▾`, and a unified Profile Hub), complemented by a native Windows Menu Bar (`File`, `Scan & OCR`, `Learning & Profiles`, `View`, `Language`, `Help`) with industry-standard keyboard shortcuts.

### What Changed & What Is Included:
1. **High-Contrast Windows Setup Wizard (`installer/setup_gui.py`)**:
   - **Fixed Washed-Out Text**: Replaced pale colors on white wizard pages with deep slate WCAG AAA typography (`#0f172a` headings, `#1e293b` body text, `#047857` version badge).
   - **Guaranteed 3D Logo Rendering**: Implemented PyInstaller `sys._MEIPASS` dynamic resource locator so the brand emblem always loads correctly inside the compiled single-file installer.
   - **Standard Windows Controls**: Form directory inputs now display crisp white backgrounds with slate borders, blue focus outlines, and standard checkbox indicators.
   - **High-Visibility Navigation**: Primary `Next >` / `Finish` buttons styled in bold blue (`#2563eb`) and emerald green (`#16a34a`) with white text.
2. **Native Windows Menu Bar (`ui/main_window.py`)**:
   - Added a full top menu bar (`QMenuBar`) providing structured access to every feature:
     - **File**: Add Pages (`Ctrl+O`), Remove Page (`Del`), Clear All, Export to Word (`Ctrl+E`), Export to Text, Exit (`Alt+F4`).
     - **Scan & OCR**: Scan Current Page (`F5`), Scan All Pages (`Shift+F5`), Enhance Ink Contrast.
     - **Learning & Profiles**: Save Corrections (`Ctrl+L`), Memory Studio (`Ctrl+M`), Create New Profile.
     - **View**: Rotate Clockwise (`Ctrl+]`), Rotate Counter-Clockwise (`Ctrl+[`), Zoom In (`Ctrl++`), Zoom Out (`Ctrl+-`), Fit Window (`Ctrl+0`), Dark/Light Theme (`Ctrl+T`).
     - **Language**: English (`Ctrl+Shift+E`), עברית (`Ctrl+Shift+H`).
     - **Help**: User Guide & Documentation (`F1`), About Ksav Kooker.
3. **Streamlined Top Action Toolbar**:
   - Replaced overcrowded 13-button toolbar with an ergonomic, uncluttered layout:
     - **Brand Hub**: 3D emblem and non-collapsible `Ksav Kooker` title.
     - **`📁 Add Pages`**: Primary entry point.
     - **`⚡ Scan ▾` (Stacked Dropdown)**: Click directly to scan the current page (`F5`), or click the arrow for `Scan All Pages (Shift+F5)`.
     - **`💾 Save`**: Instantly records proofreading edits into the self-learning memory engine (`Ctrl+L`).
     - **`📄 Export ▾` (Stacked Dropdown)**: Clean menu to export to Microsoft Word (`.docx`) or Plain Text (`.txt`).
     - **Unified Profile Hub**: Shows active profile name and learned rule count (e.g., `👤 ברירת מחדל (כללי) (66) ▾`). Clicking lets the user switch profiles, add a new profile, or open the Memory Studio.
     - **Direct Shortcuts**: Quick access to `🧠 Memory`, `🌓` theme switch, `🌐 Language` pill, and `ℹ` About.
4. **Sidebar & Viewer Font / Icon Clipping Fix (`ui/theme.py`, `ui/main_window.py`)**:
   - Reduced button horizontal padding and refined CSS so small buttons (`+ Add`, `Delete`, `↻ 90°`, `↺ 90°`, `✨ Ink Enhancer`, `⛶ Fit`, `+`, `−`) render with full text and proper glyphs without clipping into empty squares.
5. **Categorized Torah Abbreviations Menu (`ui/text_editor.py`)**:
   - Sprawling inline buttons replaced with top 3 favorites (`[בס"ד] [רש"י] [תוס']`) and a stacked `[⚡ Torah Abbreviations ▾]` menu categorized into *Seforim & Rishonim* (רמב"ם, ראב"ד, רי"ף, רא"ש, etc.) and *Talmudic Terms* (נפק"מ, קמ"ל, סד"א, ח"נ, etc.).
6. **English Default Localization (`ui/i18n.py`)**:
   - Default interface launches in English with full bilingual parity.

---

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
