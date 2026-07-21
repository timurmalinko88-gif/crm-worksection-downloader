@echo off
REM Скрипт запуска CRM Downloader v3.0 с Фазой 1

chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo   CRM DOWNLOADER v3.0 - Фаза 1 (Красивое меню)
echo ========================================================================
echo.

REM Проверка и активация виртуального окружения
if exist ".venv\Scripts\activate.bat" (
    echo ℹ️  Активация виртуального окружения...
    call .venv\Scripts\activate.bat
    echo ✅ Виртуальное окружение активировано
    echo.
) else (
    echo ⚠️  Виртуальное окружение не найдено, используется системный Python
    echo.
)

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не установлен!
    echo    Пожалуйста установите Python 3.8+
    pause
    exit /b 1
)

REM Проверка зависимостей
echo ℹ️  Проверка зависимостей...
pip show requests beautifulsoup4 tqdm tabulate colorama >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Некоторые зависимости не установлены, устанавливаю...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей!
        pause
        exit /b 1
    )
    echo ✅ Зависимости установлены успешно!
)

REM Проверка config.json
if not exist config.json (
    echo ❌ Файл config.json не найден!
    echo    Пожалуйста создайте config.json по образцу из docs\README.md
    pause
    exit /b 1
)

REM Создание необходимых папок
if not exist "logs" mkdir logs >nul 2>&1
if not exist "downloads" mkdir downloads >nul 2>&1

echo ✅ Все проверки пройдены!
echo.

REM Меню запуска
echo Выберите режим:
echo   1. Запустить главную программу
echo   2. Запустить тесты Фазы 1
echo   3. Запустить все тесты
echo   4. Выход
echo.

set /p choice="Ваш выбор (1-4): "

if "%choice%"=="1" (
    echo.
    echo Запуск CRM Downloader...
    echo.
    python downloader.py
) else if "%choice%"=="2" (
    echo.
    echo Запуск тестов Фазы 1...
    echo.
    python test_phase1.py
) else if "%choice%"=="3" (
    echo.
    echo Запуск всех тестов...
    echo.
    python -m pytest tests/ -v
) else if "%choice%"=="4" (
    echo.
    echo До встречи! 👋
    echo.
) else (
    echo.
    echo ❌ Неверный выбор!
    echo.
    pause
    goto :eof
)

pause
