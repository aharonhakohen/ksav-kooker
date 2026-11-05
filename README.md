# Ksav Kooker (כתב קוקער) — v1.1.0
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

2. **Multi-User Handwriting Profiles & Stacking (New in v1.1.0)**
   - **Isolated Profiles**: Create dedicated learning profiles for different people (individual students, scribes, rebbeim, or notebook styles) stored in `%APPDATA%\KsavKooker\profiles\`.
   - **Top-Bar Profile Switcher**: Instantly switch the active profile directly from the top toolbar without restarting.
   - **Multi-Profile Stacking**: Check multiple profiles simultaneously in the profile manager; Ksav Kooker combines rules from all enabled people during OCR scans.
   - **Preloaded Yeshiva / Rabbinic Lexicon**: Out of the box, recognizes over 50 common Talmudic abbreviations (*ראשי תיבות*) including רש"י, תוס', רמב"ם, ראב"ד, רי"ף, רא"ש, גמ', נפק"מ, קמ"ל, ח"נ, נ"ש, סד"א, ברה"ר, ברה"י, etc.

3. **Backup, Restore & Knowledge Merging Center (New in v1.1.0)**
   - **Instant Quick Backup**: One-click timestamped `.ksavbackup` saved directly to your local backups repository.
   - **Custom Save & Restore**: Save backups to USB drives or network storage, and restore safely with automatic pre-backup protection.
   - **Rule Merging**: Import and combine a colleague's or teacher's learned rules directly into your active profile without erasing your existing rules.
   - **JSON Sharing**: Export/import clean JSON files for easy sharing.

4. **Modern, Clean, High-DPI Desktop Interface**
   - **Side-by-Side Review**: Compare original handwritten notes on the left directly against transcribed text on the right.
   - **Multi-Image Navigation**: Attach one or multiple pages (via drag-and-drop or file dialog) with thumbnail selector.
   - **Document Viewer Tools**: Smooth mouse-wheel zoom, panning, 90° rotation, and an ink-enhancer filter to make faint pencil notes legible.
   - **Hebrew Right-To-Left (RTL) Editor**: Full bidirectional cursor support, David/Arial fonts, live character/word counters, and a quick-insertion Roshei Teivot toolbar.

5. **Professional Microsoft Word (.docx) Export**
   - Generates properly tagged Right-to-Left Word documents with 1-inch margins, centered title headers, bold shiur markers, and page breaks between notebook pages.

6. **Self-Contained Setup Wizard & Portable Distribution**
   - Available as a standalone Windows Setup Wizard (`KsavKooker_Setup.exe`) that installs to `%LocalAppData%\Programs\Ksav Kooker` without admin rights.
   - Also available as a zero-install portable zip package (`KsavKooker-v1.1.0-Windows.zip`).

---

## 🚀 Quick Start Guide

### Option 1: Windows Setup Wizard (Recommended)
1. Download **`KsavKooker_Setup.exe`** from the [Releases](https://github.com/aharonhakohen/ksav-kooker/releases) page.
2. Run the installer and click **התקן עכשיו (Install Now)**.
3. Launch **Ksav Kooker** from your Desktop or Start Menu.

### Option 2: Portable Zip
1. Download **`KsavKooker-v1.1.0-Windows.zip`**.
2. Unzip to any folder on your laptop or USB drive.
3. Double-click **`KsavKooker.exe`**.

---

## 📝 User Workflow

```
[ Attach Photos ] ──> [ Select Profile ] ──> [ Rotate / Orient ] ──> [ ⚡ Scan OCR ] 
                                                                           │
                                                                           ▼
[ 📝 Export .docx ] <── [ 💾 Save & Learn Corrections ] <── [ Side-by-Side Proofread ]
```

1. **Select Profile**: Select your active handwriting profile from the **👤 כתב יד** dropdown in the top bar.
2. **Attach Photos**: Click **"📁 צרף תמונות"** or drag-and-drop JPG/PNG/WEBP images into the window.
3. **Rotate if needed**: If a photo was taken sideways, click **"↻ 90°"** to orient it upright.
4. **Scan (OCR)**: Click **"⚡ סרוק עמוד נוכחי"** (or **"⚡⚡ סרוק הכל"** for batch scans).
5. **Proofread & Correct**: Read through the transcription side-by-side with the original photo, correcting typos.
6. **Learn**: Click **"💾 שמור ולמד תיקונים"**. The system immediately saves your corrections into the active profile.
7. **Export**: Click **"📝 ייצוא לוורד (.docx)"** to create your formatted Word document.

---

## 🧠 Memory, Profiles & Backup Studio
Click **"🧠 מנהל הזיכרון"** in the top bar to:
- **📚 כללים נלמדים**: View, search, edit, or delete active rules in the current profile.
- **👥 פרופילים ומשתמשים**: Manage separate profiles for different scribes or students, and check boxes to enable multi-profile stacking.
- **💾 גיבוי ושחזור**: Perform instant timestamped backups, restore from files, or merge external rules into your active profile.

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

### Building the Standalone Installer
```bash
python build_exe.py
```

---

## 📄 License & Attribution
- Licensed under the [MIT License](LICENSE).
- Powered by PyTorch, OpenCV, and the Mishkefet neural OCR architecture.
- Developed for Torah u'Mesorah Lakewood Teachers Center & the Yeshiva community.
