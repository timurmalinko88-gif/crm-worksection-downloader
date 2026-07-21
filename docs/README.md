# CRM Downloader v3.0

Автоматический загрузчик файлов из CRM Worksection с полной поддержкой конфигурации, CLI, логирования, фильтрации и интерактивного меню.

## 🚀 Новые функции (v3.0)

### ✅ Реализовано (ПРИОРИТЕТ 3 - Удобство)

- **🎯 Фильтрация файлов** - фильтруйте по расширению, размеру и типу
- **🔔 Уведомления** - звук и Windows Toast при завершении
- **📋 Интерактивное меню** - красивый интерфейс вместо простого ввода
- **⚡ Параллельная обработка URL** - загружайте несколько URL одновременно
- **📊 Расширенная статистика** - таблицы с историей загрузок

### ✅ Реализовано (ПРИОРИТЕТ 2 - Надежность)

- **📊 Статистика загрузок** - время, скорость, процент успеха, ETA
- **💾 Проверка диска** - предупреждение если < 500MB свободно
- **📋 История загрузок** - JSON файл со всеми загруженными файлами
- **🔐 Дубликат-детекция** - пропуск файлов с одинаковым MD5

### ✅ Реализовано (ПРИОРИТЕТ 1 - Базовое)

- **Конфиг-файл (config.json)** - все параметры вынесены в конфигурацию
- **CLI аргументы** - запуск из командной строки с параметрами
- **Логирование в файл** - все события сохраняются в `logs/downloader_*.log`
- **Retry логика** - автоматические повторные попытки при ошибках (экспоненциальная задержка)
- **Прогресс-бары** - красивые полоски загрузки для файлов и данных

---

## 📋 Требования

```bash
pip install requests beautifulsoup4 tqdm tabulate colorama win10toast pytest pytest-mock
```

**Минимально:**
```bash
pip install requests beautifulsoup4 tqdm tabulate colorama
```

**Для уведомлений:**
```bash
pip install win10toast
```

**Для тестирования:**
```bash
pip install pytest pytest-mock
```

**Для улучшенного интерфейса (Фаза 1):**
```bash
pip install colorama
```

---

## ⚙️ Конфигурация

### Файл `config.json`

```json
{
  "base_dir": "D:\\путь\\к\\папке",
  "my_cookie": "your_cookie_here",
  "max_workers": 5,
  "request_timeout": 30,
  "retry_attempts": 3,
  "retry_delay": 1.0,
  "log_to_file": true,
  "log_level": "INFO",
  "mime_types": {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "application/pdf": ".pdf"
  },
  "enable_file_filtering": false,
  "allowed_extensions": [],
  "min_file_size_kb": 0,
  "max_file_size_mb": 0,
  "enable_notifications": true,
  "notification_sound": true,
  "notification_toast": true,
  "enable_batch_parallel": false,
  "parallel_urls": 2
}
```

**Параметры PRIORITY 3:**

| Параметр | Описание | По умолчанию |
|----------|---------|-------------|
| `enable_file_filtering` | Включить фильтрацию файлов | false |
| `allowed_extensions` | Разрешенные расширения (пусто = все) | [] |
| `min_file_size_kb` | Минимальный размер в KB (0 = без лимита) | 0 |
| `max_file_size_mb` | Максимальный размер в MB (0 = без лимита) | 0 |
| `enable_notifications` | Включить уведомления | true |
| `notification_sound` | Звуковые уведомления | true |
| `notification_toast` | Windows Toast уведомления | true |
| `enable_batch_parallel` | Параллельная обработка URL | false |
| `parallel_urls` | Кол-во параллельных URL | 2 |

**Параметры PRIORITY 1-2:**

| Параметр | Описание | По умолчанию |
|----------|---------|-------------|
| `base_dir` | Базовая папка для загрузок | `D:\...\Download_Work` |
| `my_cookie` | Cookie сессии для CRM | - |
| `max_workers` | Кол-во параллельных потоков файлов | 5 |
| `request_timeout` | Timeout запроса (сек) | 30 |
| `retry_attempts` | Попыток при ошибке | 3 |
| `retry_delay` | Задержка между попытками (сек) | 1.0 |
| `log_to_file` | Сохранять логи в файл | true |
| `log_level` | Уровень логирования | INFO |
| `mime_types` | Маппинг MIME-типов | 6 основных |

---

## 💻 Использование

### 1️⃣ Интерактивное меню (НОВОЕ в v3.0)

```bash
python downloader.py
```

Открывает красивое меню с опциями:

```
╔═══════════════════════════════════════════════════════════════╗
║ 🎯 CRM DOWNLOADER - PRIORITY 3 INTERACTIVE MENU              ║
╚═══════════════════════════════════════════════════════════════╝

ГЛАВНОЕ МЕНЮ:
│ 1. 📥 Загрузить по URL
│ 2. 📂 Загрузить из файла (batch)
│ 3. 📊 Просмотр статистики
│ 4. 📋 История загрузок
│ 5. 🧹 Очистить логи
│ 6. ⚙️  Параметры
│ 7. 🚪 Выход

> Выберите пункт (1-7):
```

### 2️⃣ Одиночная загрузка

```bash
python downloader.py https://example.com/task/123
```

### 3️⃣ Несколько URL

```bash
python downloader.py https://url1.com https://url2.com https://url3.com
```

### 4️⃣ Загрузка из файла (batch mode)

Создайте файл `urls.txt`:
```
https://example.com/task/1
https://example.com/task/2
https://example.com/task/3
```

**Последовательная загрузка:**
```bash
python downloader.py --batch urls.txt
```

**Параллельная загрузка (установите в config.json `enable_batch_parallel: true`):**
```bash
python downloader.py --batch urls.txt
# Загрузит все 3 URL одновременно (если parallel_urls >= 3)
```

### 5️⃣ Пользовательская конфигурация

```bash
python downloader.py --config custom_config.json https://url1.com
```

### 6️⃣ Изменение уровня логирования

```bash
python downloader.py --log-level DEBUG
python downloader.py --log-level WARNING
```

### 7️⃣ Справка

```bash
python downloader.py --help
```

---

## 🎯 Примеры (PRIORITY 3)

### Пример 1: Загрузка только PDF файлов

**config.json:**
```json
{
  "enable_file_filtering": true,
  "allowed_extensions": ["pdf"],
  "min_file_size_kb": 100,
  "max_file_size_mb": 50
}
```

**Результат:**
```
⊘ Пропускаю 'document.mp4': расширение .mp4 не разрешено
⊘ Пропускаю 'small.pdf': размер 50KB меньше минимума 100KB
✅ OK: Сохранен 'report.pdf' (2.5 MB)
```

### Пример 2: Быстрая параллельная загрузка

**urls.txt:**
```
https://example.com/task/1
https://example.com/task/2
https://example.com/task/3
```

**config.json:**
```json
{
  "enable_batch_parallel": true,
  "parallel_urls": 3
}
```

**Команда:**
```bash
python downloader.py --batch urls.txt
```

**Вывод:**
```
🚀 Параллельная обработка 3 URL (3 одновременно)...
--- Обрабатываю: https://example.com/task/1
--- Обрабатываю: https://example.com/task/2
--- Обрабатываю: https://example.com/task/3
✅ Завершено 1/3 URL
✅ Завершено 2/3 URL
✅ Завершено 3/3 URL
```

### Пример 3: С уведомлениями

**config.json:**
```json
{
  "enable_notifications": true,
  "notification_sound": true,
  "notification_toast": true
}
```

**При завершении загрузки:**
- 🔊 Проигрывается звуковой сигнал
- 🍞 Появляется Windows Toast с информацией:
  ```
  ✅ Загрузка завершена: TaskName
  15 файлов | 2.35GB | 45сек | 100%
  ```

---

## 📊 Пример вывода

```
============================================================
║ CRM DOWNLOADER - Автоматический загрузчик файлов
║ Версия 3.0 (PRIORITY 3 Complete)
============================================================
📁 Базовая папка: D:\...\Download_Work
⚡ Рабочих потоков: 5
🔄 Попыток при ошибке: 3

--- Обрабатываю: https://example.com/task/286860
Нашел задачу: [P-1774-R_01 (Важная)]. Сокращенное имя: [P-1774-R_01]
Создана папка: D:\...\P-1774-R_01
Ищу ссылки на скачивание...
🚀 Запускаю загрузку 15 файлов (5 потоков одновременно)...

📁 Файлы |████████░░░░░░░░| 67% [8/12 08:32<04:16]
📊 Данные |████████████░░░░| 245MB [1.2MB/s]

✅ === Готово. Скачано файлов: 12/12 ===

╔════════════════════════════════════════════════════════╗
║ 📊 СТАТИСТИКА ЗАГРУЗКИ
╠════════════════════════════════════════════════════════╣
║ ✅ Скачано файлов: 12/12
║ 📈 Процент успеха: 100.0%
║ 📦 Общий объем: 2.350 GB (2350 MB)
║ ⏱️  Время загрузки: 45.3 сек
║ 🚀 Средняя скорость: 52.12 MB/s
╚════════════════════════════════════════════════════════╝

🔔 Звуковое уведомление!
🍞 Toast: ✅ Загрузка завершена: P-1774-R_01
```

---

## 📝 Логирование

Логи сохраняются в папку `logs/` с форматом:
```
logs/
  downloader_2026-01-27_14-30-45.log
  downloader_2026-01-27_15-15-22.log
  downloader_2026-01-28_10-20-33.log
```

**Содержимое логa:**
```
2026-01-27 14:30:45 - INFO - Конфиг загружен: config.json
2026-01-27 14:30:45 - INFO - 📁 Базовая папка: D:\...\Download_Work
2026-01-27 14:30:47 - INFO - Нашел задачу: [P-1774-R_01]
2026-01-27 14:30:48 - WARNING - Попытка 1/3 не удалась: Connection timeout. Жду 1.0s...
2026-01-27 14:30:49 - INFO - ✅ OK: Сохранен 'P-1774-R_01_123.pdf'
```

---

## 🎯 План развития

**ПРИОРИТЕТ 1** (базовая функциональность): ✅ Завершено
- Config файлы, CLI, логирование, retry логика, прогресс-бары

**ПРИОРИТЕТ 2** (надежность): ✅ Завершено
- Статистика, проверка диска, история, дубликат-детекция (MD5)

**ПРИОРИТЕТ 3** (удобство): ✅ Завершено
- Фильтрация файлов, уведомления, интерактивное меню, параллельная обработка

**ПРИОРИТЕТ 4+** (будущее):
- Advanced фильтры (regex, MIME типы)
- Download resume (возобновление)
- CSV export истории
- Web интерфейс
- Cloud синхронизация

---

## 📚 Документация

Полная документация PRIORITY 3:
- [PRIORITY3_QUICKSTART.md](PRIORITY3_QUICKSTART.md) - Краткое руководство
- [PRIORITY3_IMPLEMENTATION.md](PRIORITY3_IMPLEMENTATION.md) - Полная техническая документация
- [PRIORITY3_COMPLETION_REPORT.md](PRIORITY3_COMPLETION_REPORT.md) - Отчет о завершении

---

## 🧪 Тестирование

Запуск всех тестов:

```bash
pytest tests/ -v
```

Только PRIORITY 3 тесты:

```bash
pytest tests/test_priority3.py -v
```

**Результат:** 29/29 тестов ✅

---

## 📁 Структура папок

```
c:\Download_Work\
├── downloader.py          # Основной скрипт (v3.0)
├── menu.py               # Интерактивное меню (НОВОЕ)
├── config.json           # Конфигурация (обновлено)
├── start.bat             # Батник для быстрого запуска
├── README.md             # Этот файл (обновлено)
├── PRIORITY3_QUICKSTART.md        # Краткое руководство
├── PRIORITY3_IMPLEMENTATION.md    # Полная документация
├── PRIORITY3_COMPLETION_REPORT.md # Отчет
├── PLAN.md               # План развития
├── tests/
│   ├── test_priority3.py # Тесты PRIORITY 3 (НОВОЕ)
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_download.py
│   ├── test_file_ops.py
│   ├── conftest.py
│   └── __init__.py
├── logs/                 # Папка с логами (создается автоматически)
└── [task_folders]/       # Загруженные файлы
    ├── TaskName_001/
    ├── TaskName_002/
    └── ...
```

---

## 🎓 Версии

| Версия | Дата | Функциональность |
|--------|------|------------------|
| **v1.0** | 2025 | Базовая: многопоточность, прогресс-бары |
| **v2.0** | 2026-01-25 | PRIORITY 1-2: конфиг, CLI, логи, retry, статистика, история |
| **v3.0** | 2026-01-27 | PRIORITY 3: фильтрация, уведомления, меню, параллельность |

**Текущая версия:** v3.0 (PRIORITY 3 Complete) ✅

---

## 📞 Поддержка

Для решения проблем см. разделы:
- [PRIORITY3_QUICKSTART.md - Решение проблем](PRIORITY3_QUICKSTART.md#-решение-проблем)
- [Логирование](#-логирование)

---

## 📄 Лицензия

Используйте свободно в личных целях.

---

**Последнее обновление:** 27 января 2026 г.  
**Версия:** 3.0 (PRIORITY 3 Complete)  
**Статус:** Production Ready ✅
