#!/bin/bash
# Script de inicio rápido para Linux/Mac
# AstroDebt - Nave Varada

echo ""
echo "========================================"
echo " AstroDebt - Nave Varada"
echo " Juego Educativo sobre Finanzas"
echo "========================================"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no encontrado"
    echo "Por favor, instala Python 3.13.7 o superior"
    exit 1
fi

# Verificar versión de Python
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python versión: $python_version"

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "No se encontró entorno virtual. Creando..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudo crear el entorno virtual"
        exit 1
    fi
fi

# Activar entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "[ERROR] No se pudo activar el entorno virtual"
    exit 1
fi

# Instalar dependencias si es necesario
echo "Verificando dependencias..."
if ! python -c "import pygame" &> /dev/null; then
    echo "Instalando dependencias..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] No se pudieron instalar las dependencias"
        exit 1
    fi
fi

# Ejecutar el script de inicio
echo ""
python run.py

# Desactivar entorno virtual
deactivate

echo ""

