import threading
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

import downloader as core

app = Flask(__name__)
app.secret_key = "crm-downloader-web-ui"

_STATUS_LABELS = {
    "queued":    "В очереди",
    "running":   "Выполняется",
    "completed": "Завершено",
    "failed":    "Ошибка",
}

@app.template_filter("job_status_label")
def job_status_label(status: str) -> str:
    """Переводит статус задачи на русский язык для отображения в шаблонах."""
    return _STATUS_LABELS.get(status, status)


_jobs_lock = threading.Lock()
_jobs: Dict[str, Dict[str, Any]] = {}

# Хранилище событий для отмены задач
_aborts_lock = threading.Lock()
_aborts: Dict[str, threading.Event] = {}


def _init_downloader() -> None:
    config_path = Path(__file__).parent / "config.json"
    core.CONFIG = core.load_config(config_path)

    core.BASE_DIR = Path(core.CONFIG.get("base_dir", r"D:\\00_WORK_RETOUCH\\3_ZLATO.UA\\Download_Work"))
    core.MY_COOKIE = core.CONFIG.get("my_cookie", "")
    core.MAX_WORKERS = core.CONFIG.get("max_workers", 5)
    core.REQUEST_TIMEOUT = core.CONFIG.get("request_timeout", 30)
    core.RETRY_ATTEMPTS = core.CONFIG.get("retry_attempts", 3)
    core.RETRY_DELAY = core.CONFIG.get("retry_delay", 1.0)
    core.LOG_TO_FILE = core.CONFIG.get("log_to_file", True)
    core.MIME_MAPPER = core.CONFIG.get("mime_types", {})
    core.download_counter_lock = threading.Lock()

    core.logger = core.setup_logging(
        log_to_file=core.LOG_TO_FILE,
        log_dir=core.BASE_DIR / "logs" if core.LOG_TO_FILE else None,
    )

    if not core.BASE_DIR.exists():
        core.BASE_DIR.mkdir(parents=True, exist_ok=True)


_init_downloader()


def _create_job(urls: List[str]) -> str:
    job_id = uuid.uuid4().hex[:12]
    with _jobs_lock:
        _jobs[job_id] = {
            "id": job_id,
            "status": "queued",
            "urls": urls,
            "completed": 0,
            "files_total": 0,
            "files_completed": 0,
            "bytes_completed": 0,
            "errors": [],
            "created_at": datetime.now(),
            "started_at": None,
            "finished_at": None,
        }
    
    # Создаем событие отмены
    with _aborts_lock:
        _aborts[job_id] = threading.Event()
        
    return job_id


def _run_job(job_id: str) -> None:
    """Запускает задачу в отдельном потоке. Несколько задач могут выполняться одновременно."""
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job["status"] = "running"
        job["started_at"] = datetime.now()

    # Получаем событие отмены
    with _aborts_lock:
        abort_event = _aborts.get(job_id)

    def stats_callback(event_type, data):
        """Callback для обновления детальной статистики из downloader.py"""
        with _jobs_lock:
            if event_type == 'init':
                job['files_total'] += data.get('total', 0)
            elif event_type == 'file_done':
                job['files_completed'] += 1
                job['bytes_completed'] += data.get('size', 0)

    errors = []
    completed = 0
    for url in job["urls"]:
        if abort_event and abort_event.is_set():
            break
            
        try:
            core.process_url(url, stats_callback=stats_callback, abort_event=abort_event)
            completed += 1
            with _jobs_lock:
                job["completed"] = completed
        except Exception as exc:  # pragma: no cover - best effort
            errors.append(str(exc))
            with _jobs_lock:
                job["errors"].append(str(exc))

    with _jobs_lock:
        job["finished_at"] = datetime.now()
        job["completed"] = completed
        job["errors"] = errors
        
        if abort_event and abort_event.is_set():
            job["status"] = "cancelled"
        else:
            job["status"] = "failed" if errors else "completed"
    
    # Очищаем событие отмены после завершения
    with _aborts_lock:
        if job_id in _aborts:
            del _aborts[job_id]


@app.get("/")
def index():
    with _jobs_lock:
        jobs = list(_jobs.values())
        active_jobs = [j for j in jobs if j['status'] in ['running', 'queued']]

    # Собираем общую статистику из истории
    history_data = {}
    total_files = 0
    total_bytes = 0
    
    if core.BASE_DIR and core.BASE_DIR.exists():
        history_data = core.load_download_history(core.BASE_DIR)
        for task in history_data.values():
            files = task.get('files', [])
            total_files += len(files)
            total_bytes += sum(f.get('size', 0) for f in files)

    # Свободное место
    try:
        usage = shutil.disk_usage(core.BASE_DIR or ".")
        free_gb = usage.free / (1024**3)
    except:
        free_gb = 0

    stats = {
        "active_jobs_count": len(active_jobs),
        "total_files": total_files,
        "total_gb": total_bytes / (1024**3),
        "free_gb": free_gb
    }

    cookie_ok = bool(core.CONFIG.get("my_cookie")) if core.CONFIG else False
    return render_template("index.html", jobs=jobs, cookie_ok=cookie_ok, stats=stats)


@app.post("/download")
def download():
    url = (request.form.get("url") or "").strip()
    batch_text = (request.form.get("batch_text") or "").strip()
    uploaded_file = request.files.get("file")

    urls: List[str] = []
    if url:
        urls = [url]
    elif batch_text:
        urls = [line.strip() for line in batch_text.splitlines() if line.strip()]
    elif uploaded_file and uploaded_file.filename:
        try:
            content = uploaded_file.read().decode('utf-8')
            urls = [line.strip() for line in content.splitlines() if line.strip()]
        except Exception as e:
            flash(f"Ошибка чтения файла: {e}", "error")
            return redirect(url_for("index"))

    if not urls:
        flash("Введите URL, список или загрузите файл.", "error")
        return redirect(url_for("index"))

    invalid_urls = [u for u in urls if not u.startswith(("http://", "https://"))]
    if invalid_urls:
        flash(f"Некорректные URL: {len(invalid_urls)}. Исправьте и повторите.", "error")
        return redirect(url_for("index"))

    if not core.CONFIG.get("my_cookie"):
        flash("MY_COOKIE не задан в config.json. Загрузка не запущена.", "error")
        return redirect(url_for("index"))

    job_id = _create_job(urls)
    worker = threading.Thread(target=_run_job, args=(job_id,), daemon=True)
    worker.start()

    return redirect(url_for("job_status", job_id=job_id))


@app.get("/jobs/<job_id>")
def job_status(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)

    if not job:
        flash("Задача не найдена.", "error")
        return redirect(url_for("index"))

    return render_template("job.html", job=job)


@app.get("/api/jobs/<job_id>")
def api_job_status(job_id: str):
    """JSON endpoint для live-обновления статуса задачи без перезагрузки страницы."""
    with _jobs_lock:
        job = _jobs.get(job_id)

    if not job:
        return jsonify({"error": "not found"}), 404

    def fmt(dt):
        return dt.isoformat() if dt else None

    return jsonify({
        "id": job["id"],
        "status": job["status"],
        "urls_total": len(job["urls"]),
        "completed": job["completed"],
        "files_total": job.get('files_total', 0),
        "files_completed": job.get('files_completed', 0),
        "bytes_completed": job.get('bytes_completed', 0),
        "errors": job["errors"],
        "created_at": fmt(job["created_at"]),
        "started_at": fmt(job["started_at"]),
        "finished_at": fmt(job["finished_at"]),
    })


@app.post("/jobs/<job_id>/cancel")
def cancel_job(job_id: str):
    """Эндпоинт для отмены активной задачи."""
    with _aborts_lock:
        event = _aborts.get(job_id)
        if event:
            event.set()
            flash(f"Запрос на отмену задачи {job_id} отправлен.", "info")
        else:
            flash("Задача не активна или уже завершена.", "warning")
            
    return redirect(url_for("job_status", job_id=job_id))


@app.get("/logs")
def logs():
    """Просмотр списка файлов логов."""
    logs_dir = core.BASE_DIR / "logs" if core.BASE_DIR else None
    log_files = []
    if logs_dir and logs_dir.exists():
        for f in logs_dir.glob("*.log"):
            stat = f.stat()
            log_files.append({
                "name": f.name,
                "size": stat.st_size,
                "mtime": datetime.fromtimestamp(stat.st_mtime)
            })
    
    # Сортировка: новые сверху
    log_files.sort(key=lambda x: x['mtime'], reverse=True)
    return render_template("logs.html", logs=log_files)


@app.get("/logs/view/<filename>")
def view_log(filename: str):
    """Просмотр содержимого конкретного лога."""
    # Защита от выхода из директории
    if ".." in filename or "/" in filename or "\\" in filename:
        flash("Неверное имя файла.", "error")
        return redirect(url_for("logs"))
        
    logs_dir = core.BASE_DIR / "logs" if core.BASE_DIR else None
    log_file = logs_dir / filename
    
    if not log_file.exists():
        flash("Лог-файл не найден.", "error")
        return redirect(url_for("logs"))
        
    try:
        # Читаем последние 1000 строк
        with open(log_file, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            content = "".join(lines[-1000:])
            return render_template("log_view.html", filename=filename, content=content)
    except Exception as e:
        flash(f"Ошибка чтения лога: {e}", "error")
        return redirect(url_for("logs"))


@app.get("/history")
def history():
    history_file = (core.BASE_DIR / "download_history.json") if core.BASE_DIR else None
    history_data = {}

    if history_file and history_file.exists():
        try:
            history_data = core.load_download_history(core.BASE_DIR)
        except Exception:
            history_data = {}

    return render_template("history.html", history=history_data)


@app.get("/settings")
def settings():
    return render_template("settings.html", config=core.CONFIG)


@app.post("/settings")
def save_settings():
    try:
        # Получаем данные формы
        new_config = {
            "base_dir": request.form.get("base_dir", core.CONFIG.get("base_dir")),
            "my_cookie": request.form.get("my_cookie", core.CONFIG.get("my_cookie")),
            "max_workers": int(request.form.get("max_workers", 5)),
            "request_timeout": int(request.form.get("request_timeout", 30)),
            "retry_attempts": int(request.form.get("retry_attempts", 3)),
            "retry_delay": float(request.form.get("retry_delay", 1.0)),
            "log_to_file": request.form.get("log_to_file") == "on",
            "log_level": request.form.get("log_level", "INFO"),
            "mime_types": core.CONFIG.get("mime_types", {}),
            "enable_file_filtering": request.form.get("enable_file_filtering") == "on",
            "allowed_extensions": [ext.strip() for ext in request.form.get("allowed_extensions", "").split(",") if ext.strip()],
            "min_file_size_kb": int(request.form.get("min_file_size_kb", 0)),
            "max_file_size_mb": int(request.form.get("max_file_size_mb", 0)),
            "enable_notifications": request.form.get("enable_notifications") == "on",
            "notification_sound": request.form.get("notification_sound") == "on",
            "notification_toast": request.form.get("notification_toast") == "on",
            "enable_batch_parallel": request.form.get("enable_batch_parallel") == "on",
            "parallel_urls": int(request.form.get("parallel_urls", 2)),
        }

        # Сохраняем в файл
        config_path = Path(__file__).parent / "config.json"
        with open(config_path, "w", encoding="utf-8") as f:
            import json
            json.dump(new_config, f, indent=2, ensure_ascii=False)

        # Обновляем глобальный конфиг
        core.CONFIG.update(new_config)
        core.BASE_DIR = Path(new_config["base_dir"])
        core.MY_COOKIE = new_config["my_cookie"]
        core.MAX_WORKERS = new_config["max_workers"]
        core.REQUEST_TIMEOUT = new_config["request_timeout"]
        core.RETRY_ATTEMPTS = new_config["retry_attempts"]
        core.RETRY_DELAY = new_config["retry_delay"]
        core.LOG_TO_FILE = new_config["log_to_file"]
        core.MIME_MAPPER = new_config["mime_types"]

        flash("Настройки сохранены успешно!", "success")
    except ValueError as e:
        flash(f"Ошибка: неверный формат числа - {e}", "error")
    except Exception as e:
        flash(f"Ошибка сохранения настроек: {e}", "error")

    return redirect(url_for("settings"))


@app.post("/logs/clear")
def clear_logs():
    try:
        logs_dir = core.BASE_DIR / "logs" if core.BASE_DIR else None
        if not logs_dir or not logs_dir.exists():
            flash("Папка логов не найдена.", "info")
            return redirect(url_for("settings"))

        log_files = list(logs_dir.glob("*.log"))
        deleted = 0
        for log_file in log_files:
            try:
                log_file.unlink()
                deleted += 1
            except Exception:
                pass

        flash(f"Удалено {deleted} файлов логов.", "success")
    except Exception as e:
        flash(f"Ошибка удаления логов: {e}", "error")

    return redirect(url_for("settings"))


if __name__ == "__main__":
    _init_downloader()
    app.run(host="0.0.0.0", port=5000, debug=False)
