# PRIORITY 3 - Быстрая Справка

## 📋 Команды

```bash
# Интерактивное меню (рекомендуется)
python downloader.py

# Один URL
python downloader.py https://example.com/task

# Несколько URL
python downloader.py url1 url2 url3

# Batch файл
python downloader.py --batch urls.txt

# С конфигом
python downloader.py --config my_config.json url

# Debug логирование
python downloader.py --log-level DEBUG url

# Справка
python downloader.py --help
```

---

## ⚙️ Config Параметры PRIORITY 3

### Фильтрация
```json
"enable_file_filtering": false,
"allowed_extensions": ["pdf", "jpg"],
"min_file_size_kb": 0,
"max_file_size_mb": 100
```

### Уведомления
```json
"enable_notifications": true,
"notification_sound": true,
"notification_toast": true
```

### Параллельность
```json
"enable_batch_parallel": false,
"parallel_urls": 2
```

---

## 🎯 Примеры

### Загружать только PDF < 50MB
```json
{
  "enable_file_filtering": true,
  "allowed_extensions": ["pdf"],
  "max_file_size_mb": 50
}
```

### Быстрая загрузка 3 URL одновременно
```json
{
  "enable_batch_parallel": true,
  "parallel_urls": 3
}
```

### Без уведомлений
```json
{
  "enable_notifications": false
}
```

---

## 📊 Статистика Версии

- **Тестов:** 29/29 ✅
- **Компонентов:** 4
- **Документации:** 5 файлов
- **Строк кода:** 1000+
- **Качество:** 100%

---

## 📚 Документация

| Файл | Для кого | Размер |
|------|----------|--------|
| PRIORITY3_QUICKSTART.md | Пользователей | 250+ строк |
| PRIORITY3_IMPLEMENTATION.md | Разработчиков | 400+ строк |
| PRIORITY3_COMPLETION_REPORT.md | Менеджеров | 300+ строк |
| PRIORITY3_EXECUTIVE_SUMMARY.md | Всех | 150+ строк |
| README.md | Всех | обновлен |

---

## ✅ Что включено

- ✅ Фильтрация файлов (расширение, размер)
- ✅ Уведомления (звук, Toast)
- ✅ Интерактивное меню (7 опций)
- ✅ Параллельная загрузка URL
- ✅ 29 тестов
- ✅ Полная документация
- ✅ 100% обратная совместимость

---

## 🚀 Быстрый Старт

1. **Активируйте окружение:**
   ```bash
   .\venv\Scripts\Activate.ps1
   ```

2. **Запустите программу:**
   ```bash
   python downloader.py
   ```

3. **Выберите опцию из меню**

4. **Следуйте инструкциям**

---

## 🔧 Частые Операции

### Загрузить по URL
```bash
python downloader.py https://example.com/task
```

### Просмотреть историю
```bash
python downloader.py
# Выберите опцию 4
```

### Очистить логи
```bash
python downloader.py
# Выберите опцию 5
```

### Использовать фильтры
Отредактируйте config.json, затем запустите

---

## 📱 Опции Меню

```
1 📥 Загрузить по URL         Ввести URL вручную
2 📂 Загрузить из файла       Batch режим
3 📊 Просмотр статистики      Таблица результатов
4 📋 История загрузок        Все загруженные файлы
5 🧹 Очистить логи           Удалить старые логи
6 ⚙️  Параметры              Текущие настройки
7 🚪 Выход                    Завершить программу
```

---

## 🆘 Проблемы?

1. **Нет звука/Toast?**
   → Проверьте `enable_notifications: true`

2. **Файлы не загружаются?**
   → Проверьте `enable_file_filtering` и расширения

3. **Медленно?**
   → Увеличьте `parallel_urls` (если `enable_batch_parallel: true`)

4. **Нужна помощь?**
   → Откройте PRIORITY3_QUICKSTART.md

---

## 📊 Версия

**v3.0 - PRIORITY 3 Complete**
- Дата: 27 января 2026
- Статус: Production Ready ✅
- Тесты: 29/29 ✅
- Документация: Complete ✅

---

**Последнее обновление:** 27 января 2026
