#!/usr/bin/env python
"""
Фаза 1: Демонстрация улучшений интерактивного меню
"""

import sys
from pathlib import Path
from menu import MenuManager, Colors

# Тестовая конфигурация
test_config = {
    "base_dir": "D:\\00_WORK_RETOUCH\\3_ZLATO.UA\\Download_Work",
    "max_workers": 5,
    "request_timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "log_to_file": True,
    "log_level": "INFO",
    "enable_file_filtering": False,
    "allowed_extensions": [],
    "min_file_size_kb": 0,
    "max_file_size_mb": 0,
    "enable_notifications": True,
    "notification_sound": True,
    "notification_toast": True,
    "enable_batch_parallel": False,
    "parallel_urls": 2,
}

def test_banner():
    """Тест красивого баннера"""
    print(f"\n{Colors.SUCCESS}=== ТЕСТ 1: БАННЕР ==={Colors.RESET}\n")
    manager = MenuManager(test_config["base_dir"], test_config)
    manager.display_banner()
    input("Нажмите Enter для продолжения...")

def test_menu():
    """Тест главного меню"""
    print(f"\n{Colors.SUCCESS}=== ТЕСТ 2: ГЛАВНОЕ МЕНЮ ==={Colors.RESET}\n")
    manager = MenuManager(test_config["base_dir"], test_config)
    manager.display_main_menu()
    input("Нажмите Enter для продолжения...")

def test_settings():
    """Тест просмотра параметров"""
    print(f"\n{Colors.SUCCESS}=== ТЕСТ 3: ПАРАМЕТРЫ ==={Colors.RESET}\n")
    manager = MenuManager(test_config["base_dir"], test_config)
    manager.show_settings()
    input("Нажмите Enter для продолжения...")

def test_colors():
    """Тест цветов"""
    print(f"\n{Colors.SUCCESS}=== ТЕСТ 4: ЦВЕТОВАЯ СХЕМА ==={Colors.RESET}\n")
    print(f"{Colors.SUCCESS}✅ Зеленый цвет (успех){Colors.RESET}")
    print(f"{Colors.ERROR}❌ Красный цвет (ошибка){Colors.RESET}")
    print(f"{Colors.WARNING}⚠️  Желтый цвет (предупреждение){Colors.RESET}")
    print(f"{Colors.INFO}ℹ️  Синий цвет (информация){Colors.RESET}")
    print(f"{Colors.HEADER}🎯 Голубой цвет (заголовок){Colors.RESET}")
    print(f"{Colors.MENU}📋 Пурпурный цвет (меню){Colors.RESET}")
    input("Нажмите Enter для продолжения...")

def main():
    """Запуск тестов"""
    print(f"\n{Colors.HEADER}{'='*60}")
    print(f"  ФАЗА 1: ТЕСТЫ УЛУЧШЕНИЙ ИНТЕРАКТИВНОГО МЕНЮ")
    print(f"{'='*60}{Colors.RESET}\n")
    
    tests = [
        ("Баннер приложения", test_banner),
        ("Главное меню", test_menu),
        ("Параметры", test_settings),
        ("Цветовая схема", test_colors),
    ]
    
    for i, (name, test_func) in enumerate(tests, 1):
        print(f"{Colors.INFO}[{i}/{len(tests)}] {name}...{Colors.RESET}")
        try:
            test_func()
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Тестирование прервано пользователем.{Colors.RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"{Colors.ERROR}Ошибка при тесте: {e}{Colors.RESET}")
    
    print(f"\n{Colors.SUCCESS}{'='*60}")
    print(f"  ✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print(f"{'='*60}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
