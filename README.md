# pdf-booklet-maker 🚀

A high-performance, local-first command-line tool and local web application designed to convert standard Portrait A4 PDFs into booklet imposition sheets (separate front and back printable PDFs) for manual double-sided printing.

This project is built purely using deterministic page imposition algorithms and high-performance libraries (PyMuPDF). It contains **no external AI dependencies or web service connections**, ensuring 100% privacy and security for corporate or sensitive documents.

---

## ✨ Features

- **Local-First & Offline:** Absolute privacy. Files never leave your local workspace.
- **Dynamic Blank Page Padding:** Automatically pads files ($N \pmod 4 \neq 0$) to align pages to a multiple of 4 by injecting blank pages at the end of the document.
- **Parametric Creep & Gutter Controls:** Precise physical formatting to account for fold offsets and binding spacing.
- **Corrupted & DRM PDF Validation:** Scans for encryption, security constraints, and corrupted elements before processing.
- **Structured JSON Logging:** Outputs standard logging outputs in JSON format to stdout for easy parsing and orchestration.
- **Glassmorphic Local Web UI:** Modern, lightweight FastAPI Single Page Application (SPA) utilizing drag-and-drop actions, parameters configuration, real-time log streaming, and downloadable packages.

---

## 📂 Project Directory Structure

```text
pdf-booklet-maker/
├── pdf_booklet/                # Core Python package
│   ├── engine.py               # Imposition mapping, padding & translation matrices
│   ├── validator.py            # Pre-checks (DRM/encryption, corruption, page counts)
│   ├── exceptions.py           # Structured package errors
│   ├── logger.py               # JSON structured logging configuration
│   ├── cli.py                  # CLI argument parsing
│   └── web/                    # FastAPI local web server and assets
│       └── static/             # Single Page Application (HTML/CSS/JS)
├── tests/                      # Unit test suite
├── Dockerfile                  # Container instructions
├── docker-compose.yml          # Container configuration orchestrator
├── .dockerignore               # Patterns to ignore during container builds
├── requirements.txt            # Package dependencies
├── make_booklet.py             # Main CLI executable
├── run_web_ui.py               # Main Web UI launcher script
└── build_executable.py         # Automates PyInstaller compilation
```

---

## 🚀 Quick Start

### 1. Installation
Create and activate your virtual environment, then install dependencies:
```bash
# Set up virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Or .venv/bin/activate.fish if using fish shell

# Install requirements
pip install -r requirements.txt
```

### 2. Running via Command Line
Generate front/back PDFs directly from your terminal:
```bash
# Basic run (outputs [input]_front.pdf and [input]_back.pdf in same directory)
python3 make_booklet.py input.pdf

# Custom run with 10 pt gutter margin and 0.5 pt creep compensation
python3 make_booklet.py input.pdf --output-dir ./output --gutter 10 --creep 0.5
```

### 3. Running the Local Web UI
You can start the local FastAPI web server to upload and process files in your browser:
```bash
# Start server
python3 make_booklet.py --web
# (Alternatively, run: python3 run_web_ui.py)
```
Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 📦 Distribution & Packaging

### Containerization (Docker)
Build and run the application as an isolated container service:
```bash
# Start container
docker compose up --build -d

# Stop container
docker compose down
```

### Standalone Executable (PyInstaller)
Compile the entire project into a single, dependency-free binary file (so you don't even need Python installed to run it):
```bash
# Build standalone binary
python3 build_executable.py
```
Your compiled binary will be placed at **`dist/pdf-booklet-maker`** (or `.exe` on Windows).
Run it directly:
```bash
# Start Web UI
./dist/pdf-booklet-maker --web

# Process PDF via CLI
./dist/pdf-booklet-maker input.pdf --output-dir ./out
```

---

## 🧪 Testing

Execute the programmatically generated unit test suite:
```bash
python3 -m unittest discover -s tests
```
All tests automatically generate mock PDFs in temporary directories and perform assertions against them, leaving no clutter.
