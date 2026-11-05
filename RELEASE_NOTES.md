# Release Notes — Ksav Kooker (כתב קוקער)

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
   - One-click export into formatted Word documents with 1-inch margins, centered title/author headers, bold shiur markers, and page breaks.
7. **3D Logo & Emblem Branding**:
   - High-resolution 3D icon, heraldic shield, and banner featuring gold trim, an open sefer, holographic cyan OCR scanning beam, and dual-language Hebrew/English typography ("כתב קוקער / KSAV KOOKER").
   - Integrated into startup splash screen, taskbar icon, about dialog, and the Windows installer wizard.
8. **Self-Contained Windows Setup Wizard & Portable Packages**:
   - Packaged as an offline setup wizard (`KsavKooker_Setup.exe`) and portable zip archive (`KsavKooker-v1.0.0-Windows.zip`) containing Python runtime, PyTorch CPU, PyQt6, and neural weights.

### How to Install and Use It:
1. Double-click **`KsavKooker_Setup.exe`** to install into your user profile (no administrator privileges or internet required), or simply unzip **`KsavKooker-v1.0.0-Windows.zip`**.
2. Launch **Ksav Kooker** from your Desktop or Start Menu.
3. Click **"📁 צרף תמונות"** to attach your note pages.
4. Click **"⚡ סרוק עמוד נוכחי"** to transcribe the page.
5. Review the text in the right pane, fix any spelling, and click **"💾 שמור ולמד תיקונים"**.
6. When done, click **"📝 ייצוא לוורד (.docx)"** to create your Word document.
