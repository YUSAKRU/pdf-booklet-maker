# pdf-booklet-maker

**Language / Dil:**
- [English](#-english)
- [Türkçe](#-türkçe)

---

<a name="-english"></a>
## English

A high-performance, local-first command-line tool and web application that converts standard Portrait A4 PDFs into booklet imposition sheets — separate front and back printable PDFs — for manual double-sided printing.

Built entirely on deterministic page imposition algorithms and PyMuPDF. **No external AI dependencies, no network calls, no telemetry.** 100% private: your files never leave your machine.

---

### Features

- **Local-First & Offline:** Files are processed entirely on your machine and never transmitted anywhere.
- **Dynamic Blank Page Padding:** Automatically pads documents to a multiple of 4 pages by injecting blank pages at the end ($N \pmod 4 \neq 0$).
- **Parametric Creep & Gutter Controls:** Fine-tune fold offset compensation and binding margin in points.
- **Custom Output Page Size:** Override the default A4 Landscape output dimensions with `--width` / `--height`.
- **Upload Size Limit:** Web UI enforces a 200 MB per-file limit to protect local resources.
- **DRM & Corruption Validation:** Detects encryption, security restrictions, and corrupted content before processing starts.
- **Structured JSON Logging:** All log output is JSON-formatted on stdout for easy parsing and pipeline integration.
- **Local Web UI:** Modern FastAPI single-page application with drag-and-drop upload, real-time log streaming, parameter controls, and one-click ZIP download.

---

### Project Structure

```text
pdf-booklet-maker/
├── pdf_booklet/                # Core Python package
│   ├── engine.py               # Imposition mapping, blank-page padding & transform matrices
│   ├── validator.py            # Pre-flight checks (DRM/encryption, corruption, page count)
│   ├── exceptions.py           # Typed package exceptions
│   ├── logger.py               # JSON structured logging
│   ├── cli.py                  # CLI argument parsing and dispatch
│   └── web/
│       ├── server.py           # FastAPI application, upload handling & session management
│       └── static/             # Single-page application (HTML / CSS / JS)
├── tests/                      # Unit test suite
├── Dockerfile                  # Container image definition
├── docker-compose.yml          # Container orchestration
├── .dockerignore               # Docker build exclusions
├── requirements.txt            # Python dependencies
├── make_booklet.py             # Main entry point (CLI and --web launcher)
├── run_web_ui.py               # Alternative Web UI launcher script
└── build_executable.py         # Automates PyInstaller compilation
```

---

### Quick Start

#### 1. Requirements

- Python **3.8** or later
- pip

#### 2. Installation

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # bash / zsh
# source .venv/bin/activate.fish  # fish shell

# Install dependencies
pip install -r requirements.txt
```

#### 3. CLI Usage

```bash
# Basic: outputs input_front.pdf and input_back.pdf next to the input file
python3 make_booklet.py input.pdf

# Custom output directory, 10 pt gutter, 0.5 pt creep compensation
python3 make_booklet.py input.pdf --output-dir ./output --gutter 10 --creep 0.5

# Custom output sheet size (e.g. US Letter landscape: 792 x 612 pt)
python3 make_booklet.py input.pdf --width 792 --height 612
```

**All CLI options:**

| Option | Default | Description |
|---|---|---|
| `input_file` | — | Path to the input Portrait PDF |
| `-o`, `--output-dir` | Same as input | Directory for output files |
| `-g`, `--gutter` | `0.0` | Base gutter margin between pages (points) |
| `-c`, `--creep` | `0.0` | Creep compensation per sheet (points) |
| `--width` | `842.0` | Output sheet width in points (A4 landscape default) |
| `--height` | `595.0` | Output sheet height in points (A4 landscape default) |
| `--web` | — | Launch the local Web UI server |
| `-v`, `--verbose` | — | Enable DEBUG-level logging |

#### 4. Web UI

```bash
python3 make_booklet.py --web
# Alternative: python3 run_web_ui.py
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

The server only binds to `127.0.0.1` — it is not exposed to the network.

---

### Docker

```bash
# Build and start
docker compose up --build -d

# Stop
docker compose down
```

The container exposes port **8000** and mounts `.sessions/` as a volume for session persistence across restarts.

---

### Standalone Executable (PyInstaller)

Compile everything into a single binary that requires no Python installation:

```bash
python3 build_executable.py
```

The binary is placed at `dist/pdf-booklet-maker` (or `dist/pdf-booklet-maker.exe` on Windows).

```bash
# Web UI
./dist/pdf-booklet-maker --web

# CLI
./dist/pdf-booklet-maker input.pdf --output-dir ./out
```

---

### Testing

```bash
python3 -m unittest discover -s tests
```

Tests generate synthetic PDFs in temporary directories and clean up after themselves.

---

---

<a name="-türkçe"></a>
## Türkçe

Manuel çift taraflı yazdırma için standart Dikey A4 PDF'leri kitapçık düzenine — ayrı ön ve arka yazdırılabilir PDF'ler — dönüştüren yüksek performanslı, yerel öncelikli bir komut satırı aracı ve web uygulamasıdır.

Tamamen deterministik sayfa düzeni algoritmaları ve PyMuPDF üzerine inşa edilmiştir. **Harici yapay zeka bağımlılığı, ağ çağrısı veya telemetri içermez.** %100 gizlilik: dosyalarınız asla makinenizden ayrılmaz.

---

### Özellikler

- **Yerel Öncelikli ve Çevrimdışı:** Dosyalar tamamen yerel makinenizde işlenir, hiçbir yere aktarılmaz.
- **Dinamik Boş Sayfa Doldurma:** Belge sonuna boş sayfa ekleyerek sayfa sayısını otomatik olarak 4'ün katına tamamlar ($N \pmod 4 \neq 0$).
- **Parametrik Katlama Payı (Creep) ve Cilt Payı (Gutter):** Katlama kayması ve cilt boşluğunu nokta cinsinden ince ayarla.
- **Özel Çıktı Sayfa Boyutu:** `--width` / `--height` ile varsayılan A4 Yatay boyutunu değiştir.
- **Yükleme Boyutu Limiti:** Web arayüzü yerel kaynakları korumak için dosya başına 200 MB sınırı uygular.
- **DRM ve Bozulma Doğrulaması:** İşleme başlamadan önce şifreleme, güvenlik kısıtlamaları ve bozuk içeriği tespit eder.
- **Yapılandırılmış JSON Günlükleme:** Tüm log çıktısı kolay ayrıştırma ve pipeline entegrasyonu için stdout'a JSON formatında yazılır.
- **Yerel Web Arayüzü:** Sürükle-bırak yükleme, gerçek zamanlı log akışı, parametre kontrolleri ve tek tıkla ZIP indirme sunan modern FastAPI tek sayfa uygulaması.

---

### Proje Yapısı

```text
pdf-booklet-maker/
├── pdf_booklet/                # Çekirdek Python paketi
│   ├── engine.py               # Kitapçık düzeni eşleme, boş sayfa ekleme ve dönüşüm matrisleri
│   ├── validator.py            # Ön kontroller (DRM/şifreleme, bozulma, sayfa sayısı)
│   ├── exceptions.py           # Tipli paket hataları
│   ├── logger.py               # JSON yapılandırılmış loglama
│   ├── cli.py                  # CLI argüman ayrıştırma ve yönlendirme
│   └── web/
│       ├── server.py           # FastAPI uygulaması, yükleme yönetimi ve oturum yönetimi
│       └── static/             # Tek sayfa uygulaması (HTML / CSS / JS)
├── tests/                      # Birim test paketi
├── Dockerfile                  # Konteyner imaj tanımı
├── docker-compose.yml          # Konteyner orkestrasyonu
├── .dockerignore               # Docker derleme dışlamaları
├── requirements.txt            # Python bağımlılıkları
├── make_booklet.py             # Ana giriş noktası (CLI ve --web başlatıcı)
├── run_web_ui.py               # Alternatif Web UI başlatıcı betiği
└── build_executable.py         # PyInstaller derlemesini otomatikleştiren betik
```

---

### Hızlı Başlangıç

#### 1. Gereksinimler

- Python **3.8** veya üzeri
- pip

#### 2. Kurulum

```bash
# Sanal ortam oluştur ve aktifleştir
python3 -m venv .venv
source .venv/bin/activate        # bash / zsh
# source .venv/bin/activate.fish  # fish kabuğu

# Bağımlılıkları yükle
pip install -r requirements.txt
```

#### 3. Komut Satırı Kullanımı

```bash
# Temel: girdi dosyasının yanına input_front.pdf ve input_back.pdf üretir
python3 make_booklet.py girdi.pdf

# Özel çıktı dizini, 10 pt cilt payı, 0.5 pt katlama payı telafisi
python3 make_booklet.py girdi.pdf --output-dir ./output --gutter 10 --creep 0.5

# Özel çıktı boyutu (örn. US Letter Yatay: 792 x 612 pt)
python3 make_booklet.py girdi.pdf --width 792 --height 612
```

**Tüm CLI seçenekleri:**

| Seçenek | Varsayılan | Açıklama |
|---|---|---|
| `input_file` | — | Girdi Dikey PDF dosyasının yolu |
| `-o`, `--output-dir` | Girdiyle aynı dizin | Çıktı dosyaları için dizin |
| `-g`, `--gutter` | `0.0` | Sayfalar arası temel cilt payı (nokta) |
| `-c`, `--creep` | `0.0` | Sayfa başına katlama payı telafisi (nokta) |
| `--width` | `842.0` | Çıktı yaprağı genişliği (nokta, A4 Yatay varsayılan) |
| `--height` | `595.0` | Çıktı yaprağı yüksekliği (nokta, A4 Yatay varsayılan) |
| `--web` | — | Yerel Web UI sunucusunu başlat |
| `-v`, `--verbose` | — | DEBUG seviyesi loglamayı etkinleştir |

#### 4. Web Arayüzü

```bash
python3 make_booklet.py --web
# Alternatif: python3 run_web_ui.py
```

Tarayıcınızda **[http://127.0.0.1:8000](http://127.0.0.1:8000)** adresini açın.

Sunucu yalnızca `127.0.0.1`'e bağlanır — ağa açık değildir.

---

### Docker

```bash
# Derle ve başlat
docker compose up --build -d

# Durdur
docker compose down
```

Konteyner **8000** portunu açığa çıkarır ve yeniden başlatmalar arasında oturum kalıcılığı için `.sessions/` dizinini volume olarak bağlar.

---

### Taşınabilir Çalıştırılabilir Dosya (PyInstaller)

Python kurulumu gerektirmeyen tek bir binary'e derle:

```bash
python3 build_executable.py
```

Binary `dist/pdf-booklet-maker` konumuna yerleştirilir (Windows'ta `dist/pdf-booklet-maker.exe`).

```bash
# Web UI
./dist/pdf-booklet-maker --web

# CLI
./dist/pdf-booklet-maker girdi.pdf --output-dir ./out
```

---

### Test Etme

```bash
python3 -m unittest discover -s tests
```

Testler geçici dizinlerde yapay PDF'ler oluşturur ve tamamlandığında temizler.
