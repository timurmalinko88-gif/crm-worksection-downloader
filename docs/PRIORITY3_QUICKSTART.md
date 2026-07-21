# PRIORITY 3 - Удобство (Convenience) - КРАТКОЕ РУКОВОДСТВО

## 🚀 Быстрый Старт

```bash
# 1. Активируйте virtual environment
.\venv\Scripts\Activate.ps1

# 2. Запустите программу с интерактивным меню
python downloader.py

# 3. Выберите опцию из меню и следуйте инструкциям
```

---

## 📝 PRIORITY 3 Функции

### 1️⃣ **Фильтрация Файлов** 🎯

**Что это:** Загружайте только нужные вам файлы по типу, размеру и имени.

**Включить:**
```json
config.json:
{
  "enable_file_filtering": true,
  "allowed_extensions": ["pdf", "jpg", "png"],
  "min_file_size_kb": 100,
  "max_file_size_mb": 50
}
```

**Результат:**
```
⊘ Пропускаю 'document.mp4': расширение .mp4 не разрешено
✅ OK: Сохранен 'photo.jpg' (2.5 MB)
```

---

### 2️⃣ **Уведомления** 🔔

**Что это:** Получайте уведомления о завершении загрузки (звук + всплывающее окно).

**Включить:**
```json
config.json:
{
  "enable_notifications": true,
  "notification_sound": true,        // 🔊 Звуковой сигнал
  "notification_toast": true         // 🍞 Windows Toast
}
```

**Видно:**
- 🔊 Звук (1000Hz, 0.5s)
- 🍞 Всплывающее окно с информацией о загрузке

---

### 3️⃣ **Интерактивное Меню** 📋

**Что это:** Красивое меню вместо простого ввода URL.

**Автоматически** запускается при запуске без аргументов:
```bash
python downloader.py
```

**Опции:**
```
1. 📥 Загрузить по URL         → Вводите URL и загружаете
2. 📂 Загрузить из файла       → Batch загрузка из файла
3. 📊 Просмотр статистики      → Таблица с результатами
4. 📋 История загрузок         → Все загруженные файлы
5. 🧹 Очистить логи           → Удалить старые логи
6. ⚙️  Параметры              → Показать текущие настройки
7. 🚪 Выход                    → Завершить программу
```

---

### 4️⃣ **Параллельная Загрузка** ⚡

**Что это:** Загружайте несколько URL одновременно из batch файла.

**Включить:**
```json
config.json:
{
  "enable_batch_parallel": true,
  "parallel_urls": 2              // одновременно 2 URL
}
```

**Использование:**
```bash
python downloader.py --batch urls.txt
```

**Результат:**
```
🚀 Параллельная обработка 5 URL (2 одновременно)...
✅ Завершено 1/5
✅ Завершено 2/5
✅ Завершено 3/5
✅ Завершено 4/5
✅ Завершено 5/5
```

---

## 📊 Сравнение Режимов

| Режим | Команда | Использование |
|-------|---------|---------------|
| **Меню** | `python downloader.py` | Удобство, новичкам |
| **Один URL** | `python downloader.py URL` | Быстрая загрузка |
| **Batch** | `python downloader.py --batch urls.txt` | Несколько URL |
| **Batch параллельно** | То же + `enable_batch_parallel: true` | Быстро загрузить много |

---

## ⚙️ Конфигурация PRIORITY 3

**Полный пример config.json:**

```json
{
  "base_dir": "D:\\Downloads",
  "my_cookie": "...",
  "max_workers": 5,
  "request_timeout": 30,
  "retry_attempts": 3,
  "retry_delay": 1.0,
  "log_to_file": true,
  "log_level": "INFO",
  
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

---

## 🧪 Тестирование

```bash
# Все PRIORITY 3 тесты
pytest tests/test_priority3.py -v

# Результат: 29 тестов ✅ passed
```

**Включает тесты:**
- ✅ Фильтрации файлов (6 тестов)
- ✅ Уведомлений (4 теста)
- ✅ Интерактивного меню (15 тестов)
- ✅ Параллельной обработки (2 теста)
- ✅ Интеграции (2 теста)

---

## 📚 Примеры Использования

### Пример 1: Использование Меню
```bash
$ python downloader.py

> Выберите пункт (1-7): 3
📊 СТАТИСТИКА ЗАГРУЗОК

Задача          Файлов  Размер      Дата
─────────────────────────────────────────
Task1           15      2.3 GB      2026-01-27
Task2           8       1.2 GB      2026-01-26
```

### Пример 2: Фильтрация PDF только
```json
{
  "enable_file_filtering": true,
  "allowed_extensions": ["pdf"],
  "min_file_size_kb": 50,
  "max_file_size_mb": 100
}
```
✅ Скачаны только PDF файлы от 50KB до 100MB

### Пример 3: Batch с параллельностью
**urls.txt:**
```
https://example.com/task1
https://example.com/task2
https://example.com/task3
```

**config.json:**
```json
{"enable_batch_parallel": true, "parallel_urls": 3}
```

**Запуск:**
```bash
python downloader.py --batch urls.txt
```
⚡ Все 3 URL загружаются одновременно!

---

## 🆘 Решение Проблем

### Проблема: Меню не показывается
**Решение:** Убедитесь что установлен `menu.py` в том же каталоге

### Проблема: Нет звука/Toast
**Решение:** Проверьте конфиг:
```json
{
  "enable_notifications": true,
  "notification_sound": true,
  "notification_toast": true
}
```

### Проблема: Файлы не загружаются (фильтры)
**Решение:** Проверьте расширения в конфиге:
```json
{
  "allowed_extensions": ["pdf", "jpg"]  // Например, это не включает .png
}
```

### Проблема: Параллельная загрузка медленная
**Решение:** Увеличьте `parallel_urls`, но не более чем `max_workers`:
```json
{
  "max_workers": 5,
  "parallel_urls": 3
}
```

---

## 📂 Файлы PRIORITY 3

| Файл | Описание |
|------|---------|
| `downloader.py` | ✏️ Расширен фильтрацией, уведомлениями, меню |
| `menu.py` | ✨ НОВЫЙ: Интерактивное меню |
| `config.json` | ✏️ Добавлены PRIORITY 3 параметры |
| `tests/test_priority3.py` | ✨ НОВЫЙ: 29 тестов |
| `PRIORITY3_IMPLEMENTATION.md` | 📖 Полная документация |

---

## 🎯 Что Дальше?

После PRIORITY 3 можно добавить:
- **PRIORITY 4:** Расширенные фильтры (regex, MIME типы)
- **PRIORITY 5:** Планирование загрузок (off-peak times)
- **PRIORITY 6:** Облачная синхронизация
- **PRIORITY 7:** Web интерфейс

---

## ✅ Проверка Статуса

Проверить что всё работает:

```bash
# 1. Запустить тесты
pytest tests/test_priority3.py -v

# 2. Запустить меню
python downloader.py

# 3. Проверить одиночную загрузку
python downloader.py https://example.com/task

# 4. Проверить batch с параллельностью
python downloader.py --batch urls.txt
```

**Если всё зелено** ✅ - PRIORITY 3 готов к использованию!

---

**Версия:** 3.0  
**Статус:** ✅ Production Ready  
**Дата:** 27 января 2026
