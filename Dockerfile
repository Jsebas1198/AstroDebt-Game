# Dockerfile para AstroDebt - Nave Varada
# Python 3.13.7 con Pygame

FROM python:3.13.7-slim

# Etiquetas de metadata
LABEL maintainer="AstroDebt Team"
LABEL description="Juego educativo sobre finanzas - AstroDebt"
LABEL version="0.1.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependencias del sistema necesarias para Pygame
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivo de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar el código del proyecto
COPY . .

# Exponer puerto si necesitamos debugging o telemetría (opcional)
# EXPOSE 8000

# Comando por defecto para ejecutar el juego
CMD ["python", "main.py"]

# Nota: Para ejecutar con interfaz gráfica en Docker, necesitarás:
# docker run -it --rm \
#   -e DISPLAY=$DISPLAY \
#   -v /tmp/.X11-unix:/tmp/.X11-unix \
#   astrodebt

