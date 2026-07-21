import os
import requests
import re
import time
import logging
import json
import argparse
import sys
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from tqdm import tqdm

# Import PRIORITY 3 menu
try:
    from menu import show_menu_loop
    MENU_AVAILABLE = True
except ImportError:
    MENU_AVAILABLE = False

# ==========================================
# ⚙️ ЗОНА НАСТРОЕК И КОНФИГУРАЦИИ
# ==========================================

def load_config(config_path=None):
    """Загружает конфигурацию из JSON файла или создаёт шаблон."""
    if config_path is None:
        config_path = Path(__file__).parent / 'config.json'
    
    if not config_path.exists():
        if logger:
            logger.warning(f"Конфиг-файл не найден: {config_path}")
            logger.info("Используются значения по умолчанию")
        print(f"⚠️  Конфиг-файл не найден: {config_path}. Используются значения по умолчанию.")
        return get_default_config()
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if logger:
            logger.info(f"Конфиг загружен: {config_path}")
        return config
    except json.JSONDecodeError as e:
        if logger:
            logger.error(f"Ошибка парсинга JSON: {e}")
        print(f"❌ Ошибка парсинга JSON: {e}")
        return get_default_config()
    except Exception as e:
        if logger:
            logger.error(f"Ошибка загрузки конфига: {e}")
        print(f"❌ Ошибка загрузки конфига: {e}")
        return get_default_config()

def get_default_config():
    """Возвращает конфигурацию по умолчанию."""
    return {
        'base_dir': r'D:\00_WORK_RETOUCH\3_ZLATO.UA\Download_Work',
        'my_cookie': '',
        'max_workers': 5,
        'request_timeout': 30,
        'retry_attempts': 3,
        'retry_delay': 1.0,
        'log_to_file': True,
        'log_level': 'INFO',
        'mime_types': {
            'image/jpeg': '.jpg',
            'image/tiff': '.tif',
            'image/png': '.png',
            'application/pdf': '.pdf',
            'application/zip': '.zip',
            'application/x-zip-compressed': '.zip',
        },
        # PRIORITY 3: Convenience features
        'enable_file_filtering': False,
        'allowed_extensions': [],  # Пусто = все расширения
        'min_file_size_kb': 0,
        'max_file_size_mb': 0,  # 0 = без ограничений
        'enable_notifications': True,
        'notification_sound': True,
        'notification_toast': True,
        'enable_batch_parallel': False,
        'parallel_urls': 2,
    }

# Загружаем конфиг ДО инициализации логирования
CONFIG = None
BASE_DIR = None
MY_COOKIE = None
MAX_WORKERS = None
REQUEST_TIMEOUT = None
RETRY_ATTEMPTS = None
RETRY_DELAY = None
LOG_TO_FILE = None
MIME_MAPPER = None

# Будет инициализировано после парсинга аргументов
logger = None

# ==========================================
# 📊 СТАТИСТИКА И ИСТОРИЯ
# ==========================================
class DownloadStats:
    """Класс для отслеживания статистики загрузок."""
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.total_bytes = 0
        self.files_success = 0
        self.files_total = 0
        self.bytes_lock = Lock()
        
    def start(self):
        self.start_time = time.time()
    
    def finish(self):
        self.end_time = time.time()
    
    def add_bytes(self, size):
        with self.bytes_lock:
            self.total_bytes += size
    
    def get_duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def get_speed_mbps(self):
        duration = self.get_duration()
        if duration > 0:
            mb = self.total_bytes / (1024 * 1024)
            return mb / duration
        return 0
    
    def get_success_rate(self):
        if self.files_total > 0:
            return (self.files_success / self.files_total) * 100
        return 0
    
    def get_eta(self, current_file, total_files):
        """Вычисляет примерное время до завершения."""
        if self.start_time is None:
            return 0
        
        elapsed = time.time() - self.start_time
        if current_file <= 0:
            return 0
        
        avg_time_per_file = elapsed / current_file
        remaining_files = total_files - current_file
        return avg_time_per_file * remaining_files

current_stats = DownloadStats()

# ==========================================
# 🧱 ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==========================================

def get_extension_from_mime(content_type):
    """Определяет расширение файла на основе заголовка Content-Type."""
    if not content_type:
        return None
    clean_type = content_type.split(';')[0].strip().lower() 
    
    for mime_pattern, ext in MIME_MAPPER.items():
        if mime_pattern == clean_type:
            return ext
    
    # Попытка определить через стандартную библиотеку, если нет в нашем маппере
    try:
        import mimetypes
        guessed = mimetypes.guess_extension(clean_type)
        return guessed
    except:
        return None

def check_disk_space(target_dir):
    """Проверяет свободное место на диске. Возвращает True, если можно продолжать."""
    try:
        target_path = Path(target_dir)
        if not target_path.exists():
            target_path.mkdir(parents=True, exist_ok=True)
        
        # Получаем свободное место
        stat = shutil.disk_usage(target_path)
        free_mb = stat.free / (1024 * 1024)
        free_gb = free_mb / 1024
        
        logger.info(f"💾 Свободное место на диске: {free_gb:.2f} GB ({free_mb:.0f} MB)")
        
        # Критическое предупреждение
        if free_mb < 100:
            logger.critical(f"❌ КРИТИЧНО: < 100 MB свободно! Загрузка остановлена!")
            return False
        
        # Важное предупреждение
        if free_mb < 500:
            logger.warning(f"⚠️  ВНИМАНИЕ: < 500 MB свободно! Рекомендуется освободить место.")
        
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка проверки диска: {e}")
        return True  # Продолжаем в любом случае

def get_file_md5(file_path):
    """Вычисляет MD5 хеш файла."""
    try:
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    except Exception as e:
        logger.error(f"❌ Ошибка вычисления MD5: {e}")
        return None

def load_download_history(base_dir):
    """Загружает историю загрузок из JSON файла."""
    history_file = Path(base_dir) / 'download_history.json'
    
    if history_file.exists():
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️  Ошибка загрузки истории: {e}. Создаю новую.")
            return {}
    return {}

def save_download_history(base_dir, history):
    """Сохраняет историю загрузок в JSON файл."""
    history_file = Path(base_dir) / 'download_history.json'
    
    try:
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения истории: {e}")

def check_duplicate_by_md5(file_path, base_dir, history):
    """Проверяет, не скачан ли уже файл с таким же MD5."""
    file_md5 = get_file_md5(file_path)
    if not file_md5:
        return False
    
    # Ищем файл с таким же MD5 в истории
    for task_name, task_data in history.items():
        for file_info in task_data.get('files', []):
            if file_info.get('md5') == file_md5:
                logger.info(f"    📋 Дубликат найден (по MD5): {file_info.get('filename')} в {task_name}")
                return True
    
    return False

def clean_filename(name):
    """Очищает строку от символов, запрещенных в именах файлов Windows."""
    if not name:
        return ""
    cleaned = re.sub(r'[<>:"/\\|?*]', '', name)
    cleaned = re.sub(r'[^\w\s\-\._()]', '', cleaned).strip()
    return cleaned

def setup_logging(log_to_file=False, log_dir=None):
    """Настраивает логирование в консоль и опционально в файл."""
    global logger
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Очищаем старые обработчики
    logger.handlers.clear()
    
    # Формат логирования
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Логирование в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Логирование в файл (если включено)
    if log_to_file and log_dir:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file = log_dir / f'downloader_{timestamp}.log'
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Логирование в файл: {log_file}")
    
    return logger
    

def rename_existing_files(folder_path, safe_title):
    """
    Переименовывает старые файлы (file_ID.ext) в новый формат (safe_title_ID.ext).
    """
    logger.info(f"--- Запускаю проверку и переименование в папке: {folder_path} ---")
    
    for filename in os.listdir(folder_path):
        name_part, ext = os.path.splitext(filename)
        
        # Ищем ID в конце имени
        match = re.search(r'(\d+)$', name_part)
        
        if match:
            file_id_part = match.group(1)
            
            # 1. Формируем НОВОЕ имя по строгому правилу
            new_filename = f"{safe_title}_{file_id_part}{ext.lower()}"
            
            # 2. Если имя не совпадает (т.е. это старый формат 'file_ID.ext')
            if filename != new_filename:
                old_path = os.path.join(folder_path, filename)
                new_path = os.path.join(folder_path, new_filename)
                
                # Защита от конфликта
                if os.path.exists(new_path):
                    logger.warning(f"    Пропускаю: {new_filename} уже существует.")
                    continue

                try:
                    os.rename(old_path, new_path)
                    logger.info(f"    Переименовано: {filename} -> {new_filename}")
                except Exception as e:
                    logger.error(f"    Ошибка переименования {filename}: {e}")
        
    logger.info("--- Автоматическое переименование завершено ---")


# ==========================================
# 🎁 PRIORITY 3: ФИЛЬТРАЦИЯ ФАЙЛОВ
# ==========================================

def should_download_file(filename, file_size_kb):
    """Проверяет, должен ли файл быть загружен на основе фильтров."""
    if not CONFIG.get('enable_file_filtering', False):
        return True, "фильтрация отключена"
    
    # Проверка расширения файла
    allowed_exts = CONFIG.get('allowed_extensions', [])
    if allowed_exts:
        _, ext = os.path.splitext(filename)
        ext = ext.lower().lstrip('.')
        if ext not in [e.lower().lstrip('.') for e in allowed_exts]:
            return False, f"расширение .{ext} не в разрешённых: {allowed_exts}"
    
    # Проверка минимального размера
    min_size_kb = CONFIG.get('min_file_size_kb', 0)
    if min_size_kb > 0 and file_size_kb < min_size_kb:
        return False, f"размер {file_size_kb}KB меньше минимума {min_size_kb}KB"
    
    # Проверка максимального размера
    max_size_mb = CONFIG.get('max_file_size_mb', 0)
    if max_size_mb > 0:
        max_size_kb = max_size_mb * 1024
        if file_size_kb > max_size_kb:
            return False, f"размер {file_size_kb}KB больше максимума {max_size_mb}MB"
    
    return True, "passed filters"


# ==========================================
# 🔔 PRIORITY 3: УВЕДОМЛЕНИЯ
# ==========================================

def play_notification_sound():
    """Проигрывает звуковое уведомление (Windows)."""
    try:
        import winsound
        frequency = 1000  # Hz
        duration = 500    # milliseconds
        winsound.Beep(frequency, duration)
        if logger:
            logger.debug("🔔 Звуковое уведомление воспроизведено")
    except ImportError:
        if logger:
            logger.warning("⚠️  winsound недоступен (не Windows)")
    except Exception as e:
        if logger:
            logger.warning(f"⚠️  Ошибка воспроизведения звука: {e}")


def send_toast_notification(title, message, show_time_sec=5):
    """Отправляет системное уведомление через plyer (кроссплатформенно)."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            timeout=show_time_sec,
            app_name="CRM Downloader",
        )
        if logger:
            logger.debug(f"🍞 Уведомление отправлено: {title}")
    except ImportError:
        if logger:
            logger.debug("ℹ️  plyer не установлен. Пропускаю уведомление.")
    except Exception as e:
        if logger:
            logger.warning(f"⚠️  Ошибка отправки уведомления: {e}")


def notify_completion(task_name, files_count, total_gb, duration_sec, success_rate):
    """Отправляет уведомление о завершении загрузки."""
    if not CONFIG.get('enable_notifications', True):
        return
    
    # Звуковое уведомление
    if CONFIG.get('notification_sound', True):
        play_notification_sound()
    
    # Toast уведомление
    if CONFIG.get('notification_toast', True):
        title = f"✅ Загрузка завершена: {task_name}"
        message = f"{files_count} файлов | {total_gb:.2f}GB | {duration_sec:.0f}сек | {success_rate:.0f}%"
        send_toast_notification(title, message, show_time_sec=7)



# ==========================================
# ⚡ МНОГОПОТОЧНАЯ ЗАГРУЗКА
# ==========================================

def download_single_file(file_url, link_href, safe_title, folder_path, headers, pbar_files=None, pbar_bytes=None, base_dir=None, history=None, stats_callback=None, abort_event=None):
    """Загружает один файл в отдельном потоке с прогресс-барами и retry логикой."""
    try:
        file_id_part = link_href.strip('/').split('/')[-1]
        filename_base = f"{safe_title}_{file_id_part}"
        
        # Определяем расширение с помощью запроса HEAD
        for attempt in range(RETRY_ATTEMPTS):
            try:
                r_file = requests.get(file_url, headers=headers, stream=True, timeout=REQUEST_TIMEOUT)
                r_file.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                if attempt < RETRY_ATTEMPTS - 1:
                    wait_time = RETRY_DELAY * (2 ** attempt)  # Экспоненциальная задержка
                    logger.warning(f"    Попытка {attempt + 1}/{RETRY_ATTEMPTS} не удалась: {e}. Жду {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"    ❌ Ошибка скачивания (все {RETRY_ATTEMPTS} попытки): {e}")
                    if pbar_files:
                        pbar_files.update(1)
                    return False
        
        # 1. Получаем расширение
        content_type = r_file.headers.get('content-type', '')
        content_disposition = r_file.headers.get('content-disposition', '')

        determined_ext = None

        # Приоритет 1: имя из заголовка Content-Disposition
        if content_disposition:
            cd_match = re.search(
                r"filename\*?=['\"]?(?:UTF-8'')?([^'\";\r\n]+)",
                content_disposition,
                re.IGNORECASE
            )
            if cd_match:
                cd_filename = cd_match.group(1).strip().strip('"\'')
                try:
                    from urllib.parse import unquote
                    cd_filename = unquote(cd_filename)
                except Exception:
                    pass
                _, cd_ext = os.path.splitext(cd_filename)
                if cd_ext:
                    determined_ext = cd_ext.lower()
                    logger.debug(f"    📎 Расширение из Content-Disposition: {determined_ext} (файл: {cd_filename})")

        # Приоритет 2: MIME-тип из Content-Type
        if not determined_ext:
            determined_ext = get_extension_from_mime(content_type)
            if determined_ext:
                logger.debug(f"    📎 Расширение из MIME ({content_type}): {determined_ext}")

        # Приоритет 3: fallback
        if not determined_ext:
            determined_ext = '.dat'
            logger.warning(f"    ⚠️ Не удалось определить тип файла (Content-Type: '{content_type}', CD: '{content_disposition}'). Сохраняю как .dat")

        # 2. Формируем имя: Артикул_ID.ext
        filename = f"{filename_base}{determined_ext}"
        
        # 3. PRIORITY 3: Проверяем фильтры
        file_size_kb = int(r_file.headers.get('content-length', 0)) / 1024
        should_download, filter_reason = should_download_file(filename, file_size_kb)
        
        if not should_download:
            logger.info(f"    ⊘ Пропускаю '{filename}': {filter_reason}")
            if pbar_files:
                pbar_files.update(1)
            return False
        
        save_path = os.path.join(folder_path, filename)
        
        # Защита от повторного скачивания
        if os.path.exists(save_path):
            logger.warning(f"    ⊘ Пропускаю: '{filename}' уже существует.")
            if pbar_files:
                pbar_files.update(1)
            return False

        # Получаем общий размер файла
        total_size = int(r_file.headers.get('content-length', 0))
        
        # Обновляем размер общего прогресс-бара
        if pbar_bytes and total_size > 0:
            pbar_bytes.total += total_size
            pbar_bytes.refresh()

        # Сохраняем файл с отслеживанием прогресса
        downloaded_size = 0
        with open(save_path, 'wb') as f:
            for chunk in r_file.iter_content(chunk_size=8192):
                if abort_event and abort_event.is_set():
                    logger.warning(f"    ⏹️ Загрузка прервана пользователем: {filename}")
                    f.close()
                    if os.path.exists(save_path):
                        os.remove(save_path)
                    return False

                f.write(chunk)
                downloaded_size += len(chunk)
                if pbar_bytes:
                    pbar_bytes.update(len(chunk))
        
        # Обновляем статистику
        current_stats.add_bytes(downloaded_size)
        current_stats.files_success += 1

        if stats_callback:
            stats_callback('file_done', {'size': downloaded_size})
        
        # Вычисляем MD5 файла
        file_md5 = get_file_md5(save_path)
        
        # Сохраняем информацию в историю
        if history is not None and base_dir is not None:
            if safe_title not in history:
                history[safe_title] = {
                    'task_name': safe_title,
                    'first_download': datetime.now().isoformat(),
                    'files': []
                }
            
            file_info = {
                'filename': filename,
                'size': downloaded_size,
                'md5': file_md5,
                'download_date': datetime.now().isoformat(),
                'url': file_url
            }
            history[safe_title]['files'].append(file_info)
            save_download_history(base_dir, history)
        
        logger.info(f"    ✅ OK: Сохранен '{filename}' ({downloaded_size / 1024:.1f} KB, MD5: {file_md5[:8]}...)")
        if pbar_files:
            pbar_files.update(1)
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"    ❌ Ошибка скачивания: {e}")
        if pbar_files:
            pbar_files.update(1)
        return False
    except Exception as e:
        logger.error(f"    ❌ Неизвестная ошибка: {e}")
        if pbar_files:
            pbar_files.update(1)
        return False


# ==========================================
# 🎯 ОСНОВНАЯ ЛОГИКА
# ==========================================

def process_url(url, stats_callback=None, abort_event=None):
    logger.info(f"\n--- Обрабатываю: {url}")
    
    # Проверяем свободное место на диске
    if not check_disk_space(BASE_DIR):
        logger.critical("❌ Загрузка остановлена: недостаточно свободного места!")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Cookie': MY_COOKIE 
    }
    
    # Загружаем историю
    download_history = load_download_history(BASE_DIR)
    
    # 1. Заходим на страницу задачи
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        # Обработка ошибки куки
        if response.status_code in [401, 403]:
            logger.critical(f"!!! ОШИБКА: СТАТУС {response.status_code} !!!")
            logger.critical(f"!!! Куки устарела. Вручную обновите MY_COOKIE в ЗОНЕ НАСТРОЕК и перезапустите скрипт.")
            return
            
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"!!! Ошибка доступа к странице: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # 2. Ищем АРТИКУЛ и СОКРАЩАЕМ его
    try:
        title_tag = soup.find('span', class_='b')
        if title_tag:
            raw_title = title_tag.text.strip()
            
            # НОВОЕ: Извлекаем часть до первой скобки (
            short_part = raw_title.split('(')[0].strip()
            
            # Используем очищенную, короткую часть
            safe_title = clean_filename(short_part)
            
            if not safe_title:
                 safe_title = "Unknown_Task"
            logger.info(f"Нашел задачу: [{raw_title}]. Сокращенное имя: [{safe_title}]")
        else:
            safe_title = "Unknown_Task"
            logger.warning("!!! Не нашел название (span class='b'). Назовем папку 'Unknown_Task'.")

    except Exception as e:
        logger.error(f"Ошибка поиска имени: {e}")
        return

    # 3. Создаем папку (имя папки теперь будет P-1774-R_01_1)
    folder_path = os.path.join(BASE_DIR, safe_title)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logger.info(f"Создана папка: {folder_path}")

    # 4. Ищем файлы для скачивания (МНОГОПОТОЧНАЯ загрузка)
    logger.info("Ищу ссылки на скачивание...")
    
    links = soup.find_all('a', href=True)
    download_links = [link for link in links if '/download/' in link['href']]
    
    if not download_links:
        logger.warning("На странице не найдено ссылок на скачивание (/download/).")
        return

    if stats_callback:
        stats_callback('init', {'total': len(download_links)})

    # Инициализируем статистику
    current_stats.start()
    current_stats.files_total = len(download_links)
    current_stats.files_success = 0
    current_stats.total_bytes = 0

    # МНОГОПОТОЧНАЯ загрузка
    count = 0
    logger.info(f"🚀 Запускаю загрузку {len(download_links)} файлов ({MAX_WORKERS} потоков одновременно)...")
    
    # Создаём прогресс-бары
    pbar_files = tqdm(total=len(download_links), desc="📁 Файлы", unit="file", colour="green")
    pbar_bytes = tqdm(total=0, desc="📊 Данные", unit="B", unit_scale=True, colour="cyan")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        
        for link in download_links:
            file_url = urljoin(url, link['href'])
            file_id_part = link['href'].strip('/').split('/')[-1]
            
            future = executor.submit(
                download_single_file,
                file_url,
                link['href'],
                safe_title,
                folder_path,
                headers,
                pbar_files=pbar_files,
                pbar_bytes=pbar_bytes,
                base_dir=BASE_DIR,
                history=download_history,
                stats_callback=stats_callback,
                abort_event=abort_event
            )
            futures.append(future)
        
        # Ждём завершения всех загрузок
        for future in as_completed(futures):
            if abort_event and abort_event.is_set():
                logger.warning("⏹️ Прерывание очереди задач...")
                break
                
            try:
                if future.result():
                    with download_counter_lock:
                        count += 1
            except Exception as e:
                logger.error(f"Ошибка в потоке: {e}")
    
    # Закрываем прогресс-бары
    pbar_files.close()
    pbar_bytes.close()
    
    # Завершаем статистику
    current_stats.finish()
    
    # Выводим статистику
    duration = current_stats.get_duration()
    speed = current_stats.get_speed_mbps()
    success_rate = current_stats.get_success_rate()
    total_gb = current_stats.total_bytes / (1024 * 1024 * 1024)
    
    logger.info(f"")
    logger.info(f"╔{'='*60}╗")
    logger.info(f"║ 📊 СТАТИСТИКА ЗАГРУЗКИ")
    logger.info(f"╠{'='*60}╣")
    logger.info(f"║ ✅ Скачано файлов: {current_stats.files_success}/{current_stats.files_total}")
    logger.info(f"║ 📈 Процент успеха: {success_rate:.1f}%")
    logger.info(f"║ 📦 Общий объем: {total_gb:.3f} GB ({current_stats.total_bytes / 1024:.0f} MB)")
    logger.info(f"║ ⏱️  Время загрузки: {duration:.1f} сек")
    logger.info(f"║ 🚀 Средняя скорость: {speed:.2f} MB/s")
    logger.info(f"╚{'='*60}╝")
    logger.info(f"")
    
    logger.info(f"✅ === Готово. Скачано файлов: {count}/{len(download_links)} ===")
    
    # PRIORITY 3: Отправляем уведомление
    notify_completion(safe_title, current_stats.files_success, total_gb, duration, success_rate)
    
    # Запускаем переименование для унификации имен (имя папки короткое)
    rename_existing_files(folder_path, safe_title)


# --- ЗАПУСК ---
if __name__ == "__main__":
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(
        description='CRM Downloader - Автоматический загрузчик файлов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python downloader.py                          # Интерактивный режим
  python downloader.py https://url1 https://url2  # Загрузить несколько URL
  python downloader.py --batch urls.txt        # Загрузить URL из файла
  python downloader.py --config custom.json    # Использовать свой конфиг
        """
    )
    
    parser.add_argument('urls', nargs='*', help='URL для загрузки')
    parser.add_argument('--batch', '-b', help='Файл со списком URL (один на строку)')
    parser.add_argument('--config', '-c', help='Путь к файлу конфигурации (default: config.json)')
    parser.add_argument('--log-level', '-l', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Уровень логирования (default: INFO)')
    
    args = parser.parse_args()
    
    # Загружаем конфигурацию
    config_path = Path(args.config) if args.config else Path(__file__).parent / 'config.json'
    CONFIG = load_config(config_path)
    
    # Инициализируем переменные из конфига
    BASE_DIR = Path(CONFIG.get('base_dir', r'D:\00_WORK_RETOUCH\3_ZLATO.UA\Download_Work'))
    MY_COOKIE = CONFIG.get('my_cookie', '')
    MAX_WORKERS = CONFIG.get('max_workers', 5)
    REQUEST_TIMEOUT = CONFIG.get('request_timeout', 30)
    RETRY_ATTEMPTS = CONFIG.get('retry_attempts', 3)
    RETRY_DELAY = CONFIG.get('retry_delay', 1.0)
    LOG_TO_FILE = CONFIG.get('log_to_file', True)
    MIME_MAPPER = CONFIG.get('mime_types', {})
    download_counter_lock = Lock()
    
    # PRIORITY 3 инициализация (для фильтрации и уведомлений)
    # Значения уже в CONFIG.get() вызовах в функциях
    
    # Инициализируем логирование
    logger = setup_logging(
        log_to_file=LOG_TO_FILE,
        log_dir=BASE_DIR / 'logs' if LOG_TO_FILE else None
    )
    logger.setLevel(getattr(logging, args.log_level))
    
    # Проверяем наличие куки
    if not MY_COOKIE:
        logger.warning("⚠️  MY_COOKIE не установлена в конфиге!")
        logger.warning("   Обновите 'my_cookie' в config.json и повторите попытку")
        sys.exit(1)
    
    logger.info(f"╔{'='*60}╗")
    logger.info(f"║ CRM DOWNLOADER - Автоматический загрузчик файлов")
    logger.info(f"║ Версия 2.0 (с конфигурацией и CLI)")
    logger.info(f"╚{'='*60}╝")
    
    logger.info(f"📁 Базовая папка: {BASE_DIR}")
    logger.info(f"⚡ Рабочих потоков: {MAX_WORKERS}")
    logger.info(f"🔄 Попыток при ошибке: {RETRY_ATTEMPTS}")
    
    # Создаём базовую папку
    if not BASE_DIR.exists():
        try:
            BASE_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Создана базовая папка: {BASE_DIR}")
        except Exception as e:
            logger.critical(f"❌ Не удалось создать папку: {e}")
            sys.exit(1)
    
    urls_to_process = []
    
    # Обработка аргументов командной строки
    if args.urls:
        urls_to_process = args.urls
        logger.info(f"📥 Получено {len(args.urls)} URL из аргументов")
    elif args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            logger.error(f"❌ Файл не найден: {batch_path}")
            sys.exit(1)
        
        try:
            with open(batch_path, 'r', encoding='utf-8') as f:
                urls_to_process = [line.strip() for line in f if line.strip()]
            logger.info(f"📥 Загружено {len(urls_to_process)} URL из файла: {batch_path}")
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла: {e}")
            sys.exit(1)
    
    # PRIORITY 3: Interactive menu mode
    if not urls_to_process and MENU_AVAILABLE:
        try:
            logger.info("📍 Интерактивный режим (меню)")
            menu_result = show_menu_loop(BASE_DIR, CONFIG)
            
            if menu_result[0] == 'url':
                urls_to_process = [menu_result[1]]
            elif menu_result[0] == 'batch':
                urls_to_process = menu_result[1]
            elif menu_result[0] == 'exit':
                sys.exit(0)
        except Exception as e:
            logger.warning(f"⚠️  Ошибка меню: {e}. Используется простой интерактивный режим.")
            urls_to_process = []
    
    # Обработка URL
    if urls_to_process:
        # PRIORITY 3: Проверка параллельной обработки batch
        if len(urls_to_process) > 1 and CONFIG.get('enable_batch_parallel', False):
            parallel_urls = CONFIG.get('parallel_urls', 2)
            logger.info(f"🚀 Параллельная обработка {len(urls_to_process)} URL ({parallel_urls} одновременно)...")
            
            with ThreadPoolExecutor(max_workers=parallel_urls) as executor:
                futures = {executor.submit(process_url, url.strip()): url for url in urls_to_process}
                
                completed = 0
                for future in as_completed(futures):
                    try:
                        future.result()
                        completed += 1
                        logger.info(f"✅ Завершено {completed}/{len(urls_to_process)} URL")
                    except Exception as e:
                        logger.error(f"❌ Ошибка обработки URL: {e}")
            
            logger.info("✅ Параллельная обработка завершена!")
        else:
            # Последовательная обработка
            for url in urls_to_process:
                if url.strip():
                    process_url(url.strip())
            logger.info("✅ Обработка завершена!")
    else:
        # Простой интерактивный режим (без меню)
        logger.info("📍 Интерактивный режим (напишите 'exit' или 'quit' для выхода)")
        while True:
            try:
                user_input = input("\n> Ссылка: ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    logger.info("👋 До свидания!")
                    break
                if user_input:
                    process_url(user_input)
            except KeyboardInterrupt:
                logger.info("\n👋 Программа прервана пользователем")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка: {e}")
