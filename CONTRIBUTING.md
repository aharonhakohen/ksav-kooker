# Contributing to Ksav Kooker (כתב קוקער)

Thank you for your interest in contributing to **Ksav Kooker**! We welcome contributions to improve handwriting OCR accuracy, enhance the user interface, optimize memory storage, or expand language modeling for Torah and Yeshiva manuscripts.

---

## 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/aharonhakohen/ksav-kooker.git
   cd ksav-kooker
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify model weights:**
   Ensure `model_assets/mishkefet-v1.pt`, `model_assets/charset.json`, and `model_assets/hebrew_words.pkl` are present. If `mishkefet-v1.pt` was not pulled via Git LFS, download it from the latest GitHub Release and place it inside `model_assets/`.

5. **Run the application:**
   ```bash
   python main.py
   ```

---

## 🌿 Git & Workflow Standards

- **Branch Naming**: Always create a descriptive branch for your work:
  - `feature/description` for new capabilities.
  - `fix/description` for bug repairs.
  - `docs/description` for documentation improvements.
- **Commits**: Write clear, explanatory commit messages:
  - Format: `type(scope): Subject in plain English` (e.g., `feat(ocr): Add binarization threshold slider`).
- **Pull Requests**:
  - Open a PR against `main`.
  - Include an explanatory title and a plain-English summary of what changed and how it was tested.
  - Ensure all offline guarantees are preserved: the app must **never require internet connectivity** at runtime.

---

## 📦 Building Standalone Executables

To build the standalone Windows `.exe` and setup installer:
```bash
python build_exe.py
```
This will compile:
1. `dist/KsavKooker/KsavKooker.exe` (Portable distribution folder)
2. `dist/KsavKooker_Setup.exe` (Self-contained Windows Setup Wizard)

---

## ⚖️ License
By contributing to Ksav Kooker, you agree that your contributions will be licensed under its [MIT License](LICENSE).
