@echo off
chcp 65001 > nul
title TECSUP - Laboratorio 07: Servidor Django
cls

echo ===============================================================================
echo   TECSUP - PROGRAMA DE DISENO Y DESARROLLO DE SOFTWARE
echo   CURSO: Desarrollo de Aplicaciones Empresariales
echo   LABORATORIO 07: ORM en Django
echo   ESTUDIANTE: Omar Steve Campos Noriega
echo ===============================================================================
echo.

set "BASE_DIR=%~dp0"
if exist "%BASE_DIR%venv\Scripts\python.exe" (
    set "VENV_DIR=%BASE_DIR%venv"
    set "LAB_DIR=%BASE_DIR%lab07"
) else if exist "%BASE_DIR%..\venv\Scripts\python.exe" (
    set "VENV_DIR=%BASE_DIR%..\venv"
    set "LAB_DIR=%BASE_DIR%"
) else (
    echo [INFO] Entorno virtual no detectado. Creando venv...
    python -m venv "%BASE_DIR%venv"
    set "VENV_DIR=%BASE_DIR%venv"
    set "LAB_DIR=%BASE_DIR%lab07"
    "%VENV_DIR%\Scripts\pip" install -r "%BASE_DIR%requirements.txt"
)

echo [1/3] Entorno virtual: %VENV_DIR%
cd /d "%LAB_DIR%"

echo [2/3] Aplicando migraciones...
"%VENV_DIR%\Scripts\python.exe" manage.py migrate --no-input

echo [3/3] Inicializando datos de prueba...
"%VENV_DIR%\Scripts\python.exe" poblar_datos.py

echo.
echo ===============================================================================
echo   SERVIDOR DISPONIBLE EN http://127.0.0.1:8000/
echo.
echo   Portal principal:      http://127.0.0.1:8000/
echo   Consultas ORM:         http://127.0.0.1:8000/consultas-avanzadas/
echo   Catalogo de eventos:   http://127.0.0.1:8000/eventos/
echo   Directorio usuarios:   http://127.0.0.1:8000/usuarios/
echo   Actividad 2 (Recetas): http://127.0.0.1:8000/recetas/
echo   Django Admin:          http://127.0.0.1:8000/admin/
echo   Admin credentials:     admin / Tecsup2019
echo ===============================================================================
echo.

timeout /t 2 /nobreak > nul
start "" "http://127.0.0.1:8000/"

"%VENV_DIR%\Scripts\python.exe" manage.py runserver 127.0.0.1:8000
pause
