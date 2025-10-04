@echo off
REM ============================================
REM Script para iniciar AstroDebt en Docker
REM con GUI en Windows
REM ============================================

echo.
echo ========================================
echo  AstroDebt - Inicio con Docker
echo ========================================
echo.

REM Verificar Docker Desktop
docker version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Desktop no esta corriendo
    echo Por favor, inicia Docker Desktop primero
    pause
    exit /b 1
)

echo [OK] Docker Desktop detectado
echo.

REM Verificar VcXsrv
tasklist /FI "IMAGENAME eq vcxsrv.exe" 2>NUL | find /I /N "vcxsrv.exe">NUL
if errorlevel 1 (
    echo [ADVERTENCIA] VcXsrv no detectado
    echo.
    echo Necesitas iniciar VcXsrv primero. Opciones:
    echo.
    echo 1. Busca "XLaunch" en el menu de Windows
    echo 2. Configuralo con:
    echo    - Multiple windows
    echo    - Start no client
    echo    - [X] Disable access control ^(IMPORTANTE!^)
    echo    - [X] Native opengl
    echo.
    
    set /p continuar="Presiona Y si ya iniciaste VcXsrv, o N para salir [Y/N]: "
    if /i not "%continuar%"=="Y" (
        echo Cancelado. Inicia VcXsrv y vuelve a ejecutar este script.
        pause
        exit /b 1
    )
) else (
    echo [OK] VcXsrv detectado y corriendo
)

echo.
echo ========================================
echo  Configuracion de Red
echo ========================================
echo.
echo Detectando tu direccion IP...
echo.

REM Intentar obtener IP automáticamente
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :got_ip
)

:got_ip
REM Limpiar espacios
set IP=%IP: =%

if "%IP%"=="" (
    echo [ADVERTENCIA] No se pudo detectar tu IP automaticamente
    echo.
    echo Por favor, ejecuta este comando en otra ventana:
    echo   ipconfig
    echo.
    echo Y busca tu "Direccion IPv4" ^(ejemplo: 192.168.1.100^)
    echo.
    set /p IP="Ingresa tu IP manualmente: "
) else (
    echo [OK] IP detectada: %IP%
    echo.
    set /p usar_ip="Es correcta esta IP? [Y/N]: "
    if /i not "%usar_ip%"=="Y" (
        echo.
        set /p IP="Ingresa tu IP manualmente: "
    )
)

echo.
echo ========================================
echo  Configurando Docker Compose
echo ========================================
echo.

REM Crear archivo docker-compose temporal con la IP
echo Creando configuracion temporal con IP: %IP%

(
echo version: '3.8'
echo.
echo services:
echo   astrodebt:
echo     build:
echo       context: .
echo       dockerfile: Dockerfile
echo     container_name: astrodebt-game
echo     image: astrodebt:latest
echo     environment:
echo       - DISPLAY=%IP%:0.0
echo       - SDL_VIDEODRIVER=x11
echo       - LIBGL_ALWAYS_INDIRECT=1
echo       - PYGAME_HIDE_SUPPORT_PROMPT=1
echo     volumes:
echo       - .:/app:rw
echo     stdin_open: true
echo     tty: true
echo     command: python main.py
echo     restart: "no"
) > docker-compose.temp.yml

echo [OK] Configuracion creada
echo.

echo ========================================
echo  Verificando imagen Docker
echo ========================================
echo.

REM Verificar si la imagen existe
docker images astrodebt:latest -q >nul 2>&1
if errorlevel 1 (
    echo La imagen no existe. Construyendo...
    echo Esto puede tomar varios minutos la primera vez...
    echo.
    docker-compose -f docker-compose.temp.yml build astrodebt
    if errorlevel 1 (
        echo [ERROR] Fallo la construccion de la imagen
        del docker-compose.temp.yml
        pause
        exit /b 1
    )
) else (
    echo [OK] Imagen Docker encontrada
)

echo.
echo ========================================
echo  Iniciando AstroDebt
echo ========================================
echo.
echo Si todo esta bien, deberia abrirse una ventana con el juego.
echo.
echo Para detener el juego: Presiona Ctrl+C
echo.
echo Iniciando en 3 segundos...
timeout /t 3 /nobreak >nul

docker-compose -f docker-compose.temp.yml up astrodebt

REM Limpiar archivo temporal
del docker-compose.temp.yml

echo.
echo ========================================
echo  AstroDebt cerrado
echo ========================================
echo.
pause

