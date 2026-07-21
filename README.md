# CRM Worksection Downloader v3.0

An automated system for downloading and organizing files from Worksection CRM tasks, featuring a CLI, an interactive terminal menu, and a Web UI (Flask).

---

## 🌟 Key Features

- **🌐 Flask Web UI**: A fully-featured web interface to start downloads, view history, manage settings, and monitor logs in real-time.
- **💻 CLI & Interactive Menu**: Interactive console menu (`menu.py`) and command-line execution (`downloader.py`).
- **⚡ Multithreading & Parallelism**: High-speed file downloading via `ThreadPoolExecutor` and concurrent processing of multiple URLs.
- **🎯 Flexible File Filtering**: Filter attachments by extension (`.jpg`, `.png`, `.pdf`, `.tif`, etc.) and size.
- **🔐 Duplicate Detection & Retries**: Automatic MD5 hash verification to skip duplicates, and exponential backoff for download retries.
- **🔔 System Notifications**: Audio alerts and system toast notifications upon task completion.
- **📊 Logging & Statistics**: Detailed logging of all operations and persistent download history.

---

## 📁 Project Structure

```
Download_Work/
├── downloader.py          # Core file downloading engine
├── menu.py                # Interactive console menu
├── web_app.py             # Flask Web UI server
├── config.example.json    # Configuration file template
├── requirements.txt       # Python dependencies
├── pytest.ini             # Pytest configuration
├── templates/             # Web UI HTML templates
├── static/                # Web UI CSS and JS resources
├── tests/                 # 100+ unit and integration tests
├── docs/                  # Technical documentation
├── start.bat              # Script to launch the CLI menu
└── start_web.bat          # Script to launch the Web UI
```

---

## 🚀 Quick Start

### 1. Install Dependencies

Ensure Python 3.8+ is installed:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Create a `config.json` file based on `config.example.json`:

```bash
cp config.example.json config.json
```

Specify your Worksection authorization cookie in the `my_cookie` parameter:

```json
{
  "base_dir": "./downloads",
  "my_cookie": "YOUR_WORKSECTION_COOKIE_HERE",
  "max_workers": 5,
  "request_timeout": 30,
  "enable_file_filtering": true,
  "allowed_extensions": ["jpg", "jpeg", "tif", "tiff", "png", "pdf"]
}
```

---

## 💻 Usage

### 🌐 Option 1: Web UI

Start the web server:
```bash
python web_app.py
```
Or execute `start_web.bat`.

Open in your browser: `http://127.0.0.1:5000`

### 📋 Option 2: Interactive Console Menu

Start the menu:
```bash
python menu.py
```
Or execute `start.bat`.

### ⚡ Option 3: Command Line Interface (CLI)

Download files from a single URL:
```bash
python downloader.py --url "https://zolotoyvek.worksection.com/project/123/456/"
```

Batch download from a URL list file:
```bash
python downloader.py --batch-file urls.txt
```

---

## 🧪 Testing

The project is fully covered by automated tests (100+ tests).

To run the complete test suite, execute:

```bash
pytest
```

---

## 📄 License

MIT License
