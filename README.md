# Ksav Kooker (כתב קוקער) — v1.0.1
### Offline Torah Notes & Hebrew Handwriting OCR Studio
*דער קלוגער כתב-קוקער פאר שיעורים און חידושי תורה*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Windows 64-bit](https://img.shields.io/badge/Platform-Windows%2064--bit-0078D6.svg?logo=windows)](https://github.com/aharonhakohen/ksav-kooker)
[![Offline: 100%](https://img.shields.io/badge/Offline-100%25%20No%20Internet-brightgreen.svg)](#key-features)
[![GUI: PyQt6](https://img.shields.io/badge/GUI-PyQt6-41CD52.svg?logo=qt)](https://www.riverbankcomputing.com/software/pyqt/)
[![OCR Engine: PyTorch CPU](https://img.shields.io/badge/AI-PyTorch%20CPU-EE4C2C.svg?logo=pytorch)](https://pytorch.org/)

---

<p align="center">
  <img src="assets/ksav_kooker.png" alt="Ksav Kooker 3D Logo" width="220" />
</p>

## 📖 Overview
**Ksav Kooker** (from the Yiddish *כתב קוקער* — "the intelligent handwriting reader/examiner") is a standalone, **100% offline** desktop application built for yeshiva students, rebbeim, and scholars. It allows users to transcribe photos of handwritten notebook pages (both Ashkenazi/Sefardi cursive script and print), proofread them side-by-side with the original image, and export polished Microsoft Word documents (`.docx`).

Ksav Kooker features a **continuous self-learning memory engine**: when you correct transcription errors in the editor, the app absorbs your corrections into its local knowledge base and automatically applies them to future scans, becoming smarter with every notebook digitized.

---

## ✨ Key Features

1. **100% Offline Neural OCR Engine**
   - Employs a CTC neural vision model (Mishkefet-v1 architecture) specifically tuned for handwritten Hebrew cursive on standard laptop CPUs.
   - Zero internet connectivity required: full privacy, zero cloud uploads, completely secure for personal notebooks.
   - Built-in character n-gram and word unigram language models for disambiguating visually similar Hebrew letters.

2. **Self-Learning Mistake Memory Engine**
   - **Continuous Learning**: Editing words and clicking **"שמור ולמד תיקונים"** triggers bidirectional sequence alignment to detect exact corrections.
   - **Persistent Local Database**: Stores user preferences and learned substitutions in a local SQLite database (`learned_corrections.db`).
   - **Automatic Future Correction**: Pre-processes raw OCR output through the learned rule registry before presenting the text.
   - **Preloaded Yeshiva / Rabbinic Lexicon**: Out of the box, recognizes over 50 common Talmudic abbreviations (*ראשי תיבות*) including:
     - רש"י, תוס', רמב"ם, ראב"ד, רי"ף, רא"ש, גמ', משנה, ברייתא
     - נפק"מ, קמ"ל, סד"א, ח"נ, נ"ש, ברה"ר, ברה"י, עיי"ש, עכ"ד, וכו'

3. **Modern, Clean, High-DPI Desktop Interface**
   - **Side-by-Side Review**: Compare original handwritten notes on the left directly against transcribed text on the right.
   - **Multi-Image Navigation**: Attach one or multiple pages (via drag-and-drop or file dialog) with thumbnail selector.
   - **Document Viewer Tools**: Smooth mouse-wheel zoom, panning, 90° clockwise/counter-clockwise rotation (ideal for phone photos), and an ink-enhancer filter to make faint pencil notes legible.
   - **Hebrew Right-To-Left (RTL) Editor**: Full bidirectional cursor support, David/Arial fonts, live character/word counters, and a quick-insertion Roshei Teivot toolbar.

4. **Professional Microsoft Word (.docx) Export**
   - Generates properly tagged Right-to-Left Word documents with 1-inch margins, centered title headers, bold shiur markers, and page breaks between notebook pages.

5. **Self-Contained Setup Wizard & Portable Distribution**
   - Available as a standalone Windows Setup Wizard (`KsavKooker_Setup.exe`) that installs to `%LocalAppData%\Programs\Ksav Kooker` without admin rights.
   - Also available as a zero-install portable zip package (`KsavKooker-v1.0.0-Windows.zip`).

---

## 🚀 Quick Start Guide

### Option 1: Windows Setup Wizard (Recommended)
1. Download **`KsavKooker_Setup.exe`** from the [Releases](https://github.com/aharonhakohen/ksav-kooker/releases) page.
2. Run the installer and click **התקן עכשיו (Install Now)**.
3. Launch **Ksav Kooker** from your Desktop or Start Menu.

### Option 2: Portable Zip
1. Download **`KsavKooker-v1.0.0-Windows.zip`**.
2. Unzip to any folder on your laptop or USB drive.
3. Double-click **`KsavKooker.exe`**.

---

## 📝 User Workflow

```
[ Attach Photos ] ──> [ Rotate / Orient ] ──> [ ⚡ Scan OCR ] 
        │
        ▼
[ Side-by-Side Proofread ] ──> [ 💾 Save & Learn Corrections ] ──> [ 📝 Export .docx ]
```

1. **Attach Photos**: Click **"📁 צרף תמונות"** or drag-and-drop JPG/PNG/WEBP images into the window.
2. **Rotate if needed**: If a photo was taken sideways, click **"↻ 90°"** to orient it upright.
3. **Scan (OCR)**: Click **"⚡ סרוק עמוד נוכחי"** (or **"⚡⚡ סרוק הכל"** for batch scans).
4. **Proofread & Correct**: Read through the transcription in the right panel side-by-side with your handwritten page, correcting any typos or adding missing words.
5. **Learn**: Click **"💾 שמור ולמד תיקונים"**. The system immediately absorbs your corrections into its memory bank.
6. **Export**: Click **"📝 ייצוא לוורד (.docx)"** to create your formatted Word document.

---

## 🧠 Memory & Rules Manager
Click **"🧠 מנהל הזיכרון"** in the top bar to:
- View all active learned replacement rules and frequency counts.
- Search, add manual rules, or remove rules.
- Export or import the dictionary as a `.json` backup file.

---

## 🛠️ Developer Setup & Building from Source

### Prerequisites
- Python 3.10+ (64-bit)
- Git (and Git LFS for model weights)

### Installation
```bash
git clone https://github.com/aharonhakohen/ksav-kooker.git
cd ksav-kooker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Running from Source
```bash
python main.py
```

### Building the Standalone Executable & Installer
```bash
python build_exe.py
```
Outputs:
- `dist/KsavKooker/KsavKooker.exe` (Standalone application directory)
- `dist/KsavKooker_Setup.exe` (Self-contained Windows Setup Wizard)
- `dist/KsavKooker-v1.0.0-Windows.zip` (Portable release archive)

---

## 📂 Project Architecture

```
TorahNotesOCR/
├── assets/                  # 3D branding icons and banners (PNG, ICO)
├── core/
│   ├── hebocr/             # Neural handwriting recognition & language models
│   ├── docx_exporter.py    # RTL Microsoft Word document generator
│   ├── learning_engine.py  # SQLite-backed self-learning correction engine
│   └── ocr_engine.py       # Pre-processing, segmentation & recognition pipeline
├── installer/
│   └── setup_gui.py        # Modern Windows installation wizard GUI
├── model_assets/           # Model weights (Mishkefet-v1), charset, and lexicon
├── public/                 # Version metadata
├── ui/                     # PyQt6 high-DPI modern graphical interface
│   ├── about_dialog.py     # About dialog with 3D logo
│   ├── dictionary_dialog.py# Memory and Roshei Teivot manager dialog
│   ├── image_viewer.py     # Interactive zoomable/rotatable image viewer
│   ├── main_window.py      # Dual-pane main application layout
│   ├── splash_screen.py    # Animated frameless startup splash screen
│   ├── text_editor.py      # RTL Hebrew text editor with mistake tracker
│   └── theme.py            # Modern dark/light styling system
├── build_exe.py            # Automated build script for PyInstaller
├── main.py                 # Application entry point
├── requirements.txt        # Python package dependencies
├── LICENSE                 # MIT License
├── README.md               # User & developer documentation
└── RELEASE_NOTES.md        # Plain English release changelog
```

---

## ⚖️ License
This project is licensed under the [MIT License](LICENSE).
Developed for Torah u'Mesorah Lakewood Teachers Center (TU / LTC).
