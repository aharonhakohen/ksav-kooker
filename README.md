# IbberKuck (איבערקוק) — v1.0.0
### Offline Torah Notes & Handwriting OCR Studio
*דער קלוגער כתב-איבערקוקער פאר שיעורים און חידושי תורה*

---

## Overview
**IbberKuck** (from the Yiddish *איבערקוקן* — "to inspect, look over, review, and proofread") is a standalone, 100% offline desktop application built specifically for yeshiva students, rebbeim, and scholars to transcribe handwritten Hebrew notes (both Ashkenazi/Sefardi cursive and print), proofread them side-by-side with original photos, and export clean, formatted Microsoft Word (`.docx`) documents.

## Key Features

1. **100% Offline Neural OCR Engine**
   - Uses a compact CTC neural model (Mishkefet-v1 architecture) optimized to recognize cursive and handwritten Hebrew on standard CPU laptops without requiring any internet connection.
   - Built-in word prior and character n-gram language models to decipher ambiguous letterforms.

2. **Self-Learning Memory & Mistake Correction Engine**
   - **Continuous Learning**: When you edit or correct mistakes in the editor, clicking **"שמור ולמד תיקונים"** extracts the corrections using word alignment diffing.
   - **Persistent Knowledge Base**: Saves rules in a local SQLite database (`learned_corrections.db`), remembering how you prefer specific words or abbreviations spelled.
   - **Automatic Future Application**: Every subsequent scan automatically applies all learned corrections.
   - **Preloaded Yeshiva Lexicon**: Comes pre-populated with standard Talmudic abbreviations (ראשי תיבות) such as:
     - רש"י, תוס', רמב"ם, ראב"ד, רי"ף, רא"ש, גמ', משנה, ברייתא
     - נפק"מ, קמ"ל, סד"א, ח"נ, נ"ש, ברה"ר, ברה"י, עיי"ש, עכ"ד, וכו'

3. **Modern, Clean, High-DPI GUI**
   - **Side-by-Side Review**: Document photo on one side, rich Hebrew editor on the other.
   - **Multi-Image Support**: Attach single or multiple pages (drag-and-drop supported), with thumbnail navigation.
   - **Interactive Document Viewer**: Smooth mouse-wheel zooming, panning, 90° clockwise/counter-clockwise rotation (ideal for phone photos), and high-contrast ink-enhancer filter.
   - **Hebrew RTL Editor**: Right-to-Left bidirectional typing, classic David/Arial typography, live word/character counters, and one-click quick Roshei Teivot toolbar.

4. **Microsoft Word (.docx) Export**
   - Generates professionally styled Right-To-Left (RTL) `.docx` files.
   - Configured with 1-inch margins, centered title headings, bold shiur markers, and page breaks between notebook pages.

---

## Quick Start Guide

### Launching the Application
Run **`IbberKuck.exe`** inside the application folder:
- **Local build**: `C:\Users\afink\TorahNotesOCR\dist\IbberKuck\IbberKuck.exe`
- **Google Drive deployment**: `M:\My Drive\Personal\Dovid Shmaryahu\Notes App\IbberKuck\IbberKuck.exe`

### Step-by-Step Workflow
1. **Attach Photos**: Click **"📁 צרף תמונות"** or simply drag & drop image files into the window.
2. **Rotate if needed**: If a photo was taken in landscape mode, click **"↻ 90°"** in the viewer to orient it right side up.
3. **Scan (OCR)**: Click **"⚡ סרוק עמוד נוכחי"** (or **"⚡⚡ סרוק הכל"** for batch processing).
4. **Proofread & Correct**: Read through the transcription in the right panel side-by-side with your handwritten page, correcting any typos or adding missing words.
5. **Learn**: Click **"💾 שמור ולמד תיקונים"**. The system immediately absorbs your corrections into its memory bank.
6. **Export**: Click **"📝 ייצוא לוורד (.docx)"** to create a formatted Word document.

---

## Managing Learned Rules
Click **"🧠 מנהל הזיכרון"** in the top bar to:
- View all active learned replacement rules and frequency counts.
- Search, add manual rules, or remove rules.
- Export or import the dictionary as a `.json` backup file.

---

## Technical Specifications
- **Framework**: Python 3.12, PyQt6 (Modern Qt GUI)
- **Deep Learning / OCR**: PyTorch CPU, TorchVision, Pillow, Mishkefet-v1 CTC Model
- **Storage**: SQLite 3 (Persistent local learning database)
- **Document Output**: `python-docx` with XML RTL bidirectional tags (`w:bidi`, `w:rtl`)
- **Packaging**: PyInstaller onedir standalone bundle
