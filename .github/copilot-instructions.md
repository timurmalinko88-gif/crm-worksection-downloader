# CRM Downloader - AI Coding Agent Instructions

## Project Overview
**CRM Downloader v3.0** is a Python-based file downloader for the Worksection CRM platform with prioritized feature tiers:
- **PRIORITY 1** ✅: Config files, logging, CLI args, retry logic, progress bars
- **PRIORITY 2** ✅: Download stats, disk checks, download history (MD5 deduplication), batch mode
- **PRIORITY 3** ✅: File filtering, notifications, interactive menu, parallel URL processing
- **PHASE 1** ✅: Beautiful colored UI with Colorama, hotkeys, improved error handling

### Recent Updates (27.01.2026)
- ✅ Added colorized menu with 6-color scheme
- ✅ Improved error handling (KeyboardInterrupt, validation)
- ✅ Added hotkeys: back, exit, help, Ctrl+C support
- ✅ Enhanced validation: URL length, file encoding, batch URL checking
- ✅ Beautiful formatted tables with proper size conversions (GB/MB/KB)
- ✅ See [PHASE1_IMPROVEMENTS.md](PHASE1_IMPROVEMENTS.md) for full details

## Architecture & Data Flow

### Core Components

#### 1. **downloader.py** (Primary Engine)
- **Global State**: `CONFIG`, `logger`, `current_stats` (thread-safe DownloadStats object)
- **Config Loading**: `load_config()` → `config.json` file or defaults via `get_default_config()`
- **Data Pipeline**: 
  ```
  URL → get_extension_from_mime() → clean_filename() → save_file()
                                           ↓
  check_duplicate_by_md5() → load_download_history() → save_download_history()
  ```
- **Thread-Safe Operations**: `DownloadStats` uses `Lock` for concurrent file size tracking
- **Retry Logic**: Exponential backoff (1s, 2s, 4s) wrapped in exception handlers—always log before retrying

#### 2. **menu.py** (Interactive UI - PRIORITY 3)
- `MenuManager` class wraps all menu operations
- Stateful: tracks `base_dir`, `config`, history file location
- Menu choices (1-7) route to different download modes: single URL, batch file, stats view, history view, log cleanup, settings, exit
- File input validation: checks path existence, reads URLs line-by-line

#### 3. **config.json** (Configuration)
- **Static Params**: `base_dir`, `my_cookie`, `max_workers`, `request_timeout`, `retry_attempts`, `retry_delay`
- **MIME Mapping**: Dict of content-type → file extension (e.g., `"image/jpeg": ".jpg"`)
- **PRIORITY 3 Toggles**: `enable_file_filtering`, `allowed_extensions`, `min_file_size_kb`, `max_file_size_mb`, `enable_notifications`, `enable_batch_parallel`
- **No Defaults in CLI Args**: Always load config first, then CLI args override config values

#### 4. **download_history.json** (Persistent State)
- Stored in `base_dir/download_history.json`
- Structure: `{task_name: {files: [{filename, url, md5, timestamp, size_bytes}]}}`
- Used for duplicate detection via MD5 matching—**check before download**

## Critical Workflows

### Adding New Features
1. Add config keys to `get_default_config()` dict first
2. Update schema comments in config section (e.g., "PRIORITY 3" tag)
3. Access via `CONFIG['key_name']` after initialization
4. Add tests in `tests/test_config.py` for config loading

### Handling Downloads
1. **Pre-download checks** (in order):
   - `check_disk_space()` → fails if < 100MB free
   - `check_duplicate_by_md5()` → skip if exists
   - File size filter check (if enabled)
2. **During download**: Feed `tqdm` progress bar from `response.iter_content(chunk_size)`
3. **Post-download**: Update stats, save history, calculate MD5
4. **Never catch and silently ignore errors**—log them and re-raise or return error code

### Logging & Monitoring
- Initialize early: `setup_logging(log_to_file=True, log_dir=Path(BASE_DIR)/'logs')`
- Log format: `'%(asctime)s - %(levelname)s - %(message)s'`
- Filenames: `downloader_YYYY-MM-DD_HH-MM-SS.log` (one per session)
- **Levels**: DEBUG (verbose steps), INFO (successful actions), WARNING (config issues), ERROR (failures), CRITICAL (stop execution)
- Thread safety: `logging` module is thread-safe by default

## Project-Specific Patterns

### Threading & Concurrency
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
with ThreadPoolExecutor(max_workers=CONFIG['max_workers']) as executor:
    futures = {executor.submit(download_file, url): url for url in urls}
    for future in as_completed(futures):
        try:
            result = future.result()
        except Exception as e:
            logger.error(f"...{e}")
```
- Always use `as_completed()` for non-blocking waits
- **DownloadStats.bytes_lock**: Use for thread-safe stat updates

### File Operations
- **Paths**: Always use `Path()` from `pathlib` (cross-platform, safer)
- **Filename Cleaning**: `clean_filename()` removes Windows-invalid chars: `< > : " / \ | ? *`
- **MD5 Hashing**: Chunk-based reading (4KB blocks) to handle large files
- **Disk Space**: Check before ANY file operations, warn at 500MB, fail at 100MB

### CLI Arguments
- Parser in `main()`: defines `--url`, `--batch`, `--config`, `--help`
- Order: parse args → load config → override config with args → initialize logger
- Example: `python downloader.py https://url.com --config custom.json`

### Testing Patterns (pytest)
- Fixtures in [conftest.py](tests/conftest.py): `temp_dir`, `sample_config`, `mock_session`, `sample_html_response`
- Mock external deps (requests, filesystem) → focus on logic
- Classes: `TestMimeTypeDetection`, `TestFileNameGeneration`, `TestDownloadLogic`
- Run: `pytest` (auto-discovers `test_*.py` per pytest.ini config)

## Common Gotchas

1. **Cookie Handling**: `my_cookie` must be set in config before making requests—it's session-specific to Worksection
2. **MIME Type Edge Cases**: Types include charset params (`"text/html; charset=utf-8"`) → strip before lookup
3. **History File Corruption**: Always check JSON validity before updating → use try/except in load/save
4. **Notification Module Optional**: `win10toast` only available on Windows; catch ImportError gracefully
5. **Concurrent History Writes**: If multiple workers write simultaneously, use file locking or queue writes to single thread
6. **Stats Object Lifecycle**: Shared `current_stats` across all threads—initialize once in `main()`, reset between batches

## Key Files to Reference
- [downloader.py](downloader.py#L1-L100) — Config, logging setup, retry logic
- [menu.py](menu.py#L1-L100) — Interactive menu structure
- [config.json](config.json) — All runtime parameters
- [tests/conftest.py](tests/conftest.py) — Fixture definitions for testing
- [PLAN.md](PLAN.md) — Feature priorities and roadmap

## Integration Points
- **External Deps**: `requests` (HTTP), `beautifulsoup4` (parsing), `tqdm` (progress), `tabulate` (stats tables), `win10toast` (notifications)
- **OS-Specific**: Disk space checks use `shutil.disk_usage()` (works on Windows/Linux)
- **Worksection CRM**: Cookie-based session; URLs are task-specific file download endpoints
