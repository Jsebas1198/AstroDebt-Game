@echo off
REM Script de inicio rápido para Windows
REM AstroDebt - Nave Varada

echo.
echo ========================================
echo  AstroDebt - Nave Varada
echo  Juego Educativo sobre Finanzas
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado en el PATH
    echo Por favor, instala Python 3.13.7 o superior
    pause
    exit /b 1
)

REM Verificar si existe el entorno virtual
if not exist "venv\" (
    echo No se encontro entorno virtual. Creando...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM Instalar dependencias si es necesario
echo Verificando dependencias...
pip show pygame >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

REM Ejecutar el script de inicio
echo.
python run.py

REM Desactivar entorno virtual
deactivate

echo.
pause

