# Release Notes — IbberKuck (איבערקוק)

## [v1.0.0] — 2026-11-04 (Initial Release)

### Explanatory Title:
**Initial Release of IbberKuck: Offline Hebrew Handwriting OCR Desktop Studio with Continuous Self-Learning Memory and Word Export**

### Summary in Plain English:
This is the debut release of **IbberKuck** (`v1.0.0`), a specialized, offline Windows application created to digitize handwritten yeshiva shiur notes and Torah notebooks. It allows you to attach photos of handwritten notebook pages, run neural OCR offline, proofread the extracted text alongside the photo, and export clean Microsoft Word documents.

### What Changed & What Is Included:
1. **Offline Neural Handwriting Recognition**:
   - Integrated the Mishkefet-v1 handwriting OCR model running completely offline on standard CPUs.
   - Built-in line segmentation and Hebrew language model word priors for deciphering cursive script.
2. **Self-Learning Memory Engine**:
   - Created a persistent SQLite database that automatically compares your proofreading edits with the raw OCR output.
   - Extracts word and abbreviation substitutions (e.g. `קוס` -> `תוס'`, `רשל` -> `רגל`, `בסייד` -> `בס"ד`).
   - Automatically applies learned corrections to all subsequent scans so the app becomes smarter with each page scanned.
3. **Pre-Loaded Yeshiva / Rabbinic Lexicon**:
   - Seeded with over 50 of the most common Talmudic abbreviations (Roshei Teivot) and terms (רש"י, תוס', רמב"ם, ראב"ד, רי"ף, רא"ש, גמ', נפק"מ, קמ"ל, ח"נ, נ"ש, סד"א, ברה"ר, ברה"י, etc.).
4. **Interactive Document Viewer**:
   - High-resolution pan, smooth mouse-wheel zoom, and 90-degree clockwise / counter-clockwise rotation buttons to quickly orient phone photos.
   - Optional high-contrast ink-enhancement filter to make faint pencil or faded ink legible.
5. **Hebrew Right-to-Left (RTL) Editor**:
   - Styled with Hebrew typography (David/Arial fonts), bidirectional cursor support, and a quick-insertion toolbar for common Yeshiva terms.
   - Live mistake tracking counter comparing current edits to raw scan.
6. **Microsoft Word (.docx) Exporter**:
   - One-click export into formatted Word documents with 1-inch margins, centered title/author headers, bold shiur markers, and page breaks.
7. **Standalone Windows Executable**:
   - Compiled with PyInstaller into a standalone package that runs offline on any 64-bit Windows laptop without needing Python or an internet connection.

### How to Use It:
1. Open the folder `M:\My Drive\Personal\Dovid Shmaryahu\Notes App\IbberKuck` (or copy it to a USB drive / his laptop).
2. Double-click **`IbberKuck.exe`**.
3. Click **"📁 צרף תמונות"** to attach your note pages.
4. Click **"⚡ סרוק עמוד נוכחי"** to transcribe the page.
5. Review the text in the right pane, fix any spelling, and click **"💾 שמור ולמד תיקונים"**.
6. When done, click **"📝 ייצוא לוורד (.docx)"** to create your Word document.
