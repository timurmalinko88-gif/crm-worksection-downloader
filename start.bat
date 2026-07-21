@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM CRM Downloader v3.0 - Основной скрипт запуска
REM Автоматический запуск загрузчика файлов с проверкой ошибок

title CRM Downloader v3.0

REM Получаем путь к текущей папке
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
set "DOWNLOADER_PY=%SCRIPT_DIR%downloader.py"

REM Проверяем наличие Python
if not exist "%PYTHON_EXE%" (
    echo.
    echo ❌ Python не найден в виртуальном окружении:
    echo    %PYTHON_EXE%
    echo.
    echo 💡 Создайте виртуальное окружение:
    echo    python -m venv .venv
    echo    .venv\Scripts\pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Проверяем наличие скрипта
if not exist "%DOWNLOADER_PY%" (
    echo.
    echo ❌ Файл downloader.py не найден:
    echo    %DOWNLOADER_PY%
    echo.
    pause
    exit /b 1
)

REM Проверяем config.json
if not exist "%SCRIPT_DIR%config.json" (
    echo.
    echo ❌ Файл config.json не найден!
    echo    Пожалуйста создайте config.json по образцу из docs\README.md
    echo.
    pause
    exit /b 1
)

REM Проверяем зависимости
echo ℹ️  Проверка зависимостей...
"%PYTHON_EXE%" -c "import requests, bs4, tqdm, tabulate, colorama" 2>nul
if errorlevel 1 (
    echo ⚠️  Некоторые зависимости не установлены, устанавливаю...
    "%SCRIPT_DIR%.venv\Scripts\pip.exe" install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей!
        pause
        exit /b 1
    )
    echo ✅ Зависимости установлены успешно!
)

REM Создаём необходимые папки
if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs" >nul 2>&1
if not exist "%SCRIPT_DIR%downloads" mkdir "%SCRIPT_DIR%downloads" >nul 2>&1

REM Запускаем скрипт
echo ✅ Все проверки пройдены!
echo.
echo 🚀 Запуск CRM Downloader...
echo.

"%PYTHON_EXE%" "%DOWNLOADER_PY%"

REM Сохраняем код ошибки
set "ERRORLEVEL_VAR=%ERRORLEVEL%"

echo.
if %ERRORLEVEL_VAR% equ 0 (
    echo ✅ Программа завершена успешно!
) else (
    echo ❌ Ошибка выполнения (код %ERRORLEVEL_VAR%)
)

echo.
pause
endlocal
exit /b %ERRORLEVEL_VAR%