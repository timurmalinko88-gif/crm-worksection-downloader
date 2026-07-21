@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM CRM Downloader v3.0 - Web UI launcher

title CRM Downloader Web

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=%SCRIPT_DIR%.venv\Scripts\python.exe"
set "WEB_APP_PY=%SCRIPT_DIR%web_app.py"

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

if not exist "%WEB_APP_PY%" (
    echo.
    echo ❌ Файл web_app.py не найден:
    echo    %WEB_APP_PY%
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%config.json" (
    echo.
    echo ❌ Файл config.json не найден!
    echo    Пожалуйста создайте config.json по образцу из docs\README.md
    echo.
    pause
    exit /b 1
)

echo ℹ️  Проверка зависимостей...
"%PYTHON_EXE%" -c "import flask" 2>nul
if errorlevel 1 (
    echo ⚠️  Flask не установлен, устанавливаю зависимости...
    "%SCRIPT_DIR%.venv\Scripts\pip.exe" install -r "%SCRIPT_DIR%requirements.txt"
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей!
        pause
        exit /b 1
    )
    echo ✅ Зависимости установлены успешно!
)

if not exist "%SCRIPT_DIR%logs" mkdir "%SCRIPT_DIR%logs" >nul 2>&1
if not exist "%SCRIPT_DIR%downloads" mkdir "%SCRIPT_DIR%downloads" >nul 2>&1

echo ✅ Все проверки пройдены!
echo.
echo 🚀 Запуск Web интерфейса...
echo.
echo 🌐 Откройте в браузере: http://localhost:5000
start "" "http://localhost:5000"

"%PYTHON_EXE%" "%WEB_APP_PY%"

set "ERRORLEVEL_VAR=%ERRORLEVEL%"

echo.
if %ERRORLEVEL_VAR% equ 0 (
    echo ✅ Web интерфейс завершен успешно!
) else (
    echo ❌ Ошибка выполнения (код %ERRORLEVEL_VAR%)
)

echo.
pause
endlocal
exit /b %ERRORLEVEL_VAR%
