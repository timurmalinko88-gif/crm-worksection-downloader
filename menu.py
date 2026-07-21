"""
PRIORITY 3: Interactive Menu Module
Предоставляет интерактивный интерфейс для управления загрузчиком.
Фаза 1 улучшения: цветной вывод, лучшие ошибки, горячие клавиши.
"""

import os
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

# Цветной вывод
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False
    # Fallback если colorama не установлена
    class FakeColor:
        def __getattr__(self, name):
            return ""
    Fore = FakeColor()
    Back = FakeColor()
    Style = FakeColor()

logger = logging.getLogger(__name__)

# ==========================================
# 🎨 ЦВЕТОВАЯ СХЕМА
# ==========================================
class Colors:
    """Цвета для красивого вывода."""
    HEADER = f"{Fore.CYAN}{Style.BRIGHT}"
    SUCCESS = f"{Fore.GREEN}{Style.BRIGHT}"
    WARNING = f"{Fore.YELLOW}{Style.BRIGHT}"
    ERROR = f"{Fore.RED}{Style.BRIGHT}"
    INFO = f"{Fore.BLUE}"
    MENU = f"{Fore.MAGENTA}{Style.BRIGHT}"
    RESET = Style.RESET_ALL
    
    # Для таблиц
    TABLE_HEADER = f"{Fore.WHITE}{Back.BLUE}{Style.BRIGHT}"
    TABLE_SUCCESS = f"{Fore.GREEN}"
    TABLE_ERROR = f"{Fore.RED}"


class MenuManager:
    """Управляет интерактивным меню приложения."""
    
    def __init__(self, base_dir, config):
        self.base_dir = Path(base_dir)
        self.config = config
        self.history_file = self.base_dir / 'download_history.json'
        self.logs_dir = self.base_dir / 'logs'
    
    def display_banner(self):
        """Выводит красивый заголовок приложения."""
        print(f"\n{Colors.HEADER}{'='*72}")
        print(f"║ {'🎯 CRM DOWNLOADER v3.0 - ИНТЕРАКТИВНОЕ МЕНЮ'.center(70)} ║")
        print(f"║ {'Фаза 1: Улучшенный интерфейс'.center(70)} ║")
        print(f"{'='*72}{Colors.RESET}\n")
    
    def display_main_menu(self):
        """Выводит красивое главное меню."""
        print(f"\n{Colors.MENU}{'─'*72}")
        print(f"║ {'ГЛАВНОЕ МЕНЮ'.ljust(70)} ║")
        print(f"{'├'+'─'*70+'┤'}")
        print(f"║ {Colors.SUCCESS}1.{Colors.RESET} 📥 Загрузить по URL                                          ║")
        print(f"║ {Colors.SUCCESS}2.{Colors.RESET} 📂 Загрузить из файла (batch-режим)                          ║")
        print(f"║ {Colors.SUCCESS}3.{Colors.RESET} 📊 Просмотр статистики                                       ║")
        print(f"║ {Colors.SUCCESS}4.{Colors.RESET} 📋 История загрузок                                          ║")
        print(f"║ {Colors.SUCCESS}5.{Colors.RESET} 🧹 Очистить логи                                            ║")
        print(f"║ {Colors.SUCCESS}6.{Colors.RESET} ⚙️  Параметры                                               ║")
        print(f"║ {Colors.WARNING}7.{Colors.RESET} 🚪 Выход                                                     ║")
        print(f"{'└'+'─'*70+'┘'}")
        print(f"{Colors.INFO}Подсказка:{Colors.RESET} Нажмите Ctrl+C чтобы выйти в любой момент\n")
    
    def get_menu_choice(self):
        """Запрашивает выбор у пользователя с лучшей обработкой ошибок."""
        while True:
            try:
                choice = input(f"{Colors.INFO}> Выберите пункт (1-7): {Colors.RESET}").strip()
                
                if choice in ['1', '2', '3', '4', '5', '6', '7']:
                    return choice
                
                if choice.lower() in ['help', 'h', '?']:
                    print(f"{Colors.INFO}Команды:{Colors.RESET}")
                    print("  1-7    - Выберите пункт меню")
                    print("  back   - Вернуться в меню")
                    print("  exit   - Выход")
                    continue
                
                if choice.lower() in ['exit', 'quit', 'q']:
                    return '7'
                
                print(f"{Colors.WARNING}⚠️  Неверный выбор.{Colors.RESET} Введите число от 1 до 7.")
                
            except KeyboardInterrupt:
                print(f"\n{Colors.WARNING}⚠️  Прервано пользователем.{Colors.RESET}")
                return '7'
            except EOFError:
                return '7'
            except Exception as e:
                logger.error(f"Ошибка ввода: {e}")
                print(f"{Colors.ERROR}❌ Ошибка ввода: {e}{Colors.RESET} Попробуйте снова.")
    
    def get_url_input(self):
        """Запрашивает URL у пользователя с валидацией."""
        print(f"\n{Colors.HEADER}{'─'*72}")
        print(f"║ {'ЗАГРУЗКА ПО URL'.ljust(70)} ║")
        print(f"{'└'+'─'*70+'┘'}{Colors.RESET}")
        
        try:
            url = input(f"\n{Colors.INFO}> Введите URL (или 'back' для возврата): {Colors.RESET}").strip()
            
            if url.lower() == 'back':
                return None
            
            if not url:
                print(f"{Colors.ERROR}❌ URL не может быть пустым.{Colors.RESET}")
                return None
            
            if not url.startswith(('http://', 'https://')):
                print(f"{Colors.ERROR}❌ URL должен начинаться с 'http://' или 'https://'{Colors.RESET}")
                return None
            
            if len(url) > 2048:
                print(f"{Colors.ERROR}❌ URL слишком длинный (макс 2048 символов){Colors.RESET}")
                return None
            
            print(f"{Colors.SUCCESS}✅ URL принят.{Colors.RESET}")
            return url
            
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Операция отменена.{Colors.RESET}")
            return None
        except Exception as e:
            logger.error(f"Ошибка ввода URL: {e}")
            print(f"{Colors.ERROR}❌ Ошибка ввода: {e}{Colors.RESET}")
            return None
    
    def get_batch_file_input(self):
        """Запрашивает путь к файлу с URL с улучшенной валидацией."""
        print(f"\n{Colors.HEADER}{'─'*72}")
        print(f"║ {'ЗАГРУЗКА ИЗ ФАЙЛА (BATCH-РЕЖИМ)'.ljust(70)} ║")
        print(f"{'└'+'─'*70+'┘'}{Colors.RESET}")
        
        try:
            file_path = input(f"\n{Colors.INFO}> Путь к файлу (один URL на строку, или 'back'): {Colors.RESET}").strip()
            
            if file_path.lower() == 'back':
                return None
            
            if not file_path:
                print(f"{Colors.ERROR}❌ Путь не может быть пустым.{Colors.RESET}")
                return None
            
            batch_path = Path(file_path)
            
            if not batch_path.exists():
                print(f"{Colors.ERROR}❌ Файл не найден: {batch_path}{Colors.RESET}")
                return None
            
            if not batch_path.is_file():
                print(f"{Colors.ERROR}❌ Это не файл: {batch_path}{Colors.RESET}")
                return None
            
            file_size_mb = batch_path.stat().st_size / (1024 * 1024)
            if file_size_mb > 10:
                print(f"{Colors.WARNING}⚠️  Файл очень большой ({file_size_mb:.1f} MB){Colors.RESET}")
            
            try:
                with open(batch_path, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                
                if not urls:
                    print(f"{Colors.ERROR}❌ Файл не содержит URL.{Colors.RESET}")
                    return None
                
                # Валидация URL
                invalid_urls = []
                for url in urls:
                    if not url.startswith(('http://', 'https://')):
                        invalid_urls.append(url)
                
                if invalid_urls:
                    print(f"{Colors.WARNING}⚠️  Найдено {len(invalid_urls)} неверных URL:{Colors.RESET}")
                    for url in invalid_urls[:5]:
                        print(f"   - {url}")
                    if len(invalid_urls) > 5:
                        print(f"   ... и еще {len(invalid_urls) - 5}")
                    
                    proceed = input(f"{Colors.INFO}> Продолжить только с корректными URL? (да/нет): {Colors.RESET}").strip().lower()
                    if proceed in ['да', 'yes', 'y']:
                        urls = [url for url in urls if url.startswith(('http://', 'https://'))]
                    else:
                        return None
                
                print(f"{Colors.SUCCESS}✅ Загружено {len(urls)} URL из файла.{Colors.RESET}")
                return urls
            
            except UnicodeDecodeError:
                print(f"{Colors.ERROR}❌ Ошибка кодировки файла. Используйте UTF-8.{Colors.RESET}")
                return None
        
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Операция отменена.{Colors.RESET}")
            return None
        except Exception as e:
            logger.error(f"Ошибка чтения файла: {e}")
            print(f"{Colors.ERROR}❌ Ошибка чтения файла: {e}{Colors.RESET}")
            return None
    
    def show_statistics(self):
        """Выводит красивую статистику загрузок."""
        print(f"\n{Colors.HEADER}{'─'*72}")
        print(f"║ {'СТАТИСТИКА ЗАГРУЗОК'.ljust(70)} ║")
        print(f"{'└'+'─'*70+'┘'}{Colors.RESET}")
        
        if not self.history_file.exists():
            print(f"\n{Colors.INFO}📭 История пуста. Еще нет загруженных файлов.{Colors.RESET}")
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not history:
                print(f"\n{Colors.INFO}📭 История пуста.{Colors.RESET}")
                return
            
            # Подсчитаем статистику
            total_tasks = len(history)
            total_files = sum(len(task.get('files', [])) for task in history.values())
            total_size = sum(
                f.get('size', 0) 
                for task in history.values() 
                for f in task.get('files', [])
            )
            total_gb = total_size / (1024 * 1024 * 1024)
            total_mb = (total_size % (1024 * 1024 * 1024)) / (1024 * 1024)
            
            # Красивый вывод общей статистики
            print(f"\n{Colors.SUCCESS}📊 ОБЩАЯ СТАТИСТИКА:{Colors.RESET}")
            print(f"   {Colors.TABLE_HEADER}{'Метрика':<30} {'Значение':>15}{Colors.RESET}")
            print(f"   {Colors.TABLE_HEADER}{'─'*45}{Colors.RESET}")
            print(f"   Задач обработано         {total_tasks:>15}")
            print(f"   Файлов загружено         {total_files:>15}")
            if total_gb > 0:
                print(f"   Общий объем              {f'{total_gb:.2f} GB ({total_mb:.0f} MB)':>15}")
            else:
                print(f"   Общий объем              {f'{total_mb:.1f} MB':>15}")
            
            # Таблица по задачам
            print(f"\n{Colors.SUCCESS}📋 СТАТИСТИКА ПО ЗАДАЧАМ:{Colors.RESET}")
            table_data = []
            for task_name, task_data in history.items():
                files = task_data.get('files', [])
                files_count = len(files)
                size = sum(f.get('size', 0) for f in files)
                size_mb = size / (1024 * 1024)
                first_date = task_data.get('first_download', 'N/A')
                
                table_data.append([
                    task_name[:30],
                    files_count,
                    f"{size_mb:.1f} MB",
                    first_date[:10] if first_date != 'N/A' else 'N/A'
                ])
            
            headers = [f"{Colors.TABLE_HEADER}Задача{Colors.RESET}", 
                      f"{Colors.TABLE_HEADER}Файлов{Colors.RESET}", 
                      f"{Colors.TABLE_HEADER}Размер{Colors.RESET}", 
                      f"{Colors.TABLE_HEADER}Дата{Colors.RESET}"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        except json.JSONDecodeError:
            print(f"{Colors.ERROR}❌ Ошибка парсинга истории.{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Операция отменена.{Colors.RESET}")
        except Exception as e:
            logger.error(f"Ошибка вывода статистики: {e}")
            print(f"{Colors.ERROR}❌ Ошибка: {e}{Colors.RESET}")
    
    def show_download_history(self):
        """Выводит подробную историю загрузок с цветом."""
        print(f"\n{Colors.HEADER}{'─'*72}")
        print(f"║ {'ИСТОРИЯ ЗАГРУЗОК (ПОДРОБНАЯ)'.ljust(70)} ║")
        print(f"{'└'+'─'*70+'┘'}{Colors.RESET}")
        
        if not self.history_file.exists():
            print(f"\n{Colors.INFO}📭 История пуста.{Colors.RESET}")
            return
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            if not history:
                print(f"\n{Colors.INFO}📭 История пуста.{Colors.RESET}")
                return
            
            for task_name, task_data in history.items():
                files = task_data.get('files', [])
                first_date = task_data.get('first_download', 'N/A')
                
                print(f"\n{Colors.SUCCESS}📂 {task_name}{Colors.RESET}")
                print(f"   Первая загрузка: {first_date[:19] if first_date != 'N/A' else 'N/A'}")
                print(f"   Всего файлов: {Colors.SUCCESS}{len(files)}{Colors.RESET}")
                
                if files:
                    table_data = []
                    for f in files[:10]:  # Показываем первые 10
                        size_kb = f.get('size', 0) / 1024
                        md5 = f.get('md5', 'N/A')
                        date = f.get('download_date', 'N/A')
                        
                        table_data.append([
                            f.get('filename', 'N/A')[:30],
                            f"{size_kb:.1f} KB",
                            md5[:8] if md5 != 'N/A' else 'N/A',
                            date[:10] if date != 'N/A' else 'N/A'
                        ])
                    
                    headers = ["Файл", "Размер", "MD5", "Дата"]
                    print(tabulate(table_data, headers=headers, tablefmt="simple"))
                    
                    if len(files) > 10:
                        print(f"   {Colors.INFO}... и еще {len(files) - 10} файлов{Colors.RESET}")
        
        except json.JSONDecodeError:
            print(f"{Colors.ERROR}❌ Ошибка парсинга истории.{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Операция отменена.{Colors.RESET}")
        except Exception as e:
            logger.error(f"Ошибка вывода истории: {e}")
            print(f"{Colors.ERROR}❌ Ошибка: {e}{Colors.RESET}")
    
    def clear_logs(self):
        """Очищает старые логи с подтверждением."""
        print(f"\n{Colors.HEADER}{'─'*72}")
        print(f"║ {'ОЧИСТКА ЛОГОВ'.ljust(70)} ║")
        print(f"{'└'+'─'*70+'┘'}{Colors.RESET}")
        
        if not self.logs_dir.exists():
            print(f"\n{Colors.INFO}📭 Папка логов не найдена.{Colors.RESET}")
            return
        
        log_files = list(self.logs_dir.glob('*.log'))
        
        if not log_files:
            print(f"\n{Colors.INFO}📭 Нет файлов логов для удаления.{Colors.RESET}")
            return
        
        total_size = sum(f.stat().st_size for f in log_files)
        total_mb = total_size / (1024 * 1024)
        
        print(f"\n{Colors.WARNING}⚠️  Найдено {len(log_files)} файлов логов ({total_mb:.1f} MB):{Colors.RESET}")
        for i, log_file in enumerate(log_files[-10:], 1):
            size_kb = log_file.stat().st_size / 1024
            mod_time = datetime.fromtimestamp(log_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            print(f"   {i:2}. {log_file.name:<40} ({size_kb:>8.1f} KB) - {mod_time}")
        
        if len(log_files) > 10:
            print(f"   {Colors.INFO}... и еще {len(log_files) - 10} файлов{Colors.RESET}")
        
        try:
            confirm = input(f"\n{Colors.WARNING}> Удалить все логи? (да/нет): {Colors.RESET}").strip().lower()
            
            if confirm in ['да', 'yes', 'y']:
                deleted = 0
                failed = 0
                for log_file in log_files:
                    try:
                        log_file.unlink()
                        deleted += 1
                    except Exception as e:
                        logger.error(f"Не удалось удалить {log_file.name}: {e}")
                        failed += 1
                
                if deleted > 0:
                    print(f"{Colors.SUCCESS}✅ Удалено {deleted} файлов логов.{Colors.RESET}")
                if failed > 0:
                    print(f"{Colors.WARNING}⚠️  Ошибка при удалении {failed} файлов.{Colors.RESET}")
            else:
                print(f"{Colors.INFO}⊘ Отменено.{Colors.RESET}")
        
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Операция отменена.{Colors.RESET}")
        except Exception as e:
            logger.error(f"Ошибка удаления логов: {e}")
            print(f"{Colors.ERROR}❌ Ошибка при удалении логов: {e}{Colors.RESET}")
    
    def show_settings(self):
        """Выводит текущие параметры с цветной схемой."""
        print(f"\n{Colors.HEADER}{'─'*72}")
        print(f"║ {'ПАРАМЕТРЫ'.ljust(70)} ║")
        print(f"{'└'+'─'*70+'┘'}{Colors.RESET}")
        
        # Основные параметры
        print(f"\n{Colors.SUCCESS}📋 ОСНОВНЫЕ ПАРАМЕТРЫ:{Colors.RESET}")
        settings_table = [
            ["Базовая папка", str(self.base_dir)[:50]],
            ["Рабочих потоков", self.config.get('max_workers', 5)],
            ["Timeout запроса", f"{self.config.get('request_timeout', 30)}s"],
            ["Попыток при ошибке", self.config.get('retry_attempts', 3)],
            ["Задержка retry", f"{self.config.get('retry_delay', 1.0)}s"],
        ]
        for setting, value in settings_table:
            print(f"   {setting:<30} → {value}")
        
        # Логирование
        print(f"\n{Colors.SUCCESS}📝 ЛОГИРОВАНИЕ:{Colors.RESET}")
        log_settings = [
            ["Логирование в файл", f"{Colors.TABLE_SUCCESS}✅{Colors.RESET}" if self.config.get('log_to_file', True) else f"{Colors.ERROR}❌{Colors.RESET}"],
            ["Уровень логирования", self.config.get('log_level', 'INFO')],
        ]
        for setting, value in log_settings:
            print(f"   {setting:<30} → {value}")
        
        # PRIORITY 3 функции
        print(f"\n{Colors.SUCCESS}🎯 PRIORITY 3 (УДОБСТВО):{Colors.RESET}")
        priority3_settings = [
            ["Фильтрация файлов", f"{Colors.TABLE_SUCCESS}✅{Colors.RESET}" if self.config.get('enable_file_filtering', False) else f"{Colors.ERROR}❌{Colors.RESET}"],
            ["Уведомления", f"{Colors.TABLE_SUCCESS}✅{Colors.RESET}" if self.config.get('enable_notifications', True) else f"{Colors.ERROR}❌{Colors.RESET}"],
            ["Звуковые уведомления", f"{Colors.TABLE_SUCCESS}✅{Colors.RESET}" if self.config.get('notification_sound', True) else f"{Colors.ERROR}❌{Colors.RESET}"],
            ["Toast уведомления", f"{Colors.TABLE_SUCCESS}✅{Colors.RESET}" if self.config.get('notification_toast', True) else f"{Colors.ERROR}❌{Colors.RESET}"],
            ["Batch параллельно", f"{Colors.TABLE_SUCCESS}✅{Colors.RESET}" if self.config.get('enable_batch_parallel', False) else f"{Colors.ERROR}❌{Colors.RESET}"],
            ["Кол-во параллельных URL", self.config.get('parallel_urls', 2)],
        ]
        for setting, value in priority3_settings:
            print(f"   {setting:<30} → {value}")
        
        # Фильтрация (если включена)
        if self.config.get('enable_file_filtering', False):
            print(f"\n{Colors.SUCCESS}🔍 ФИЛЬТРАЦИЯ ФАЙЛОВ:{Colors.RESET}")
            filter_settings = [
                ["Мин размер", f"{self.config.get('min_file_size_kb', 0)} KB"],
                ["Макс размер", f"{self.config.get('max_file_size_mb', 0)} MB"],
                ["Расширения", ", ".join(self.config.get('allowed_extensions', [])) or "Все"],
            ]
            for setting, value in filter_settings:
                print(f"   {setting:<30} → {value}")
        
        print(f"\n{Colors.INFO}💡 Совет: Измените параметры в config.json{Colors.RESET}")


def show_menu_loop(base_dir, config):
    """Запускает цикл главного меню с обработкой исключений."""
    manager = MenuManager(base_dir, config)
    
    manager.display_banner()
    
    while True:
        try:
            manager.display_main_menu()
            choice = manager.get_menu_choice()
            
            if choice == '1':
                url = manager.get_url_input()
                if url:
                    return ('url', url)
            
            elif choice == '2':
                urls = manager.get_batch_file_input()
                if urls:
                    return ('batch', urls)
            
            elif choice == '3':
                manager.show_statistics()
            
            elif choice == '4':
                manager.show_download_history()
            
            elif choice == '5':
                manager.clear_logs()
            
            elif choice == '6':
                manager.show_settings()
            
            elif choice == '7':
                print(f"\n{Colors.SUCCESS}👋 До свидания!{Colors.RESET}\n")
                return ('exit', None)
        
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}⚠️  Прервано пользователем.{Colors.RESET}")
            confirm = input(f"{Colors.INFO}> Выйти из программы? (да/нет): {Colors.RESET}").strip().lower()
            if confirm in ['да', 'yes', 'y']:
                print(f"{Colors.SUCCESS}👋 До свидания!{Colors.RESET}\n")
                return ('exit', None)
        except EOFError:
            print(f"\n{Colors.SUCCESS}👋 До свидания!{Colors.RESET}\n")
            return ('exit', None)
        except Exception as e:
            logger.error(f"Критическая ошибка меню: {e}")
            print(f"{Colors.ERROR}❌ Критическая ошибка: {e}{Colors.RESET}")
            print(f"{Colors.INFO}Пожалуйста, сообщите об ошибке разработчику.{Colors.RESET}")
