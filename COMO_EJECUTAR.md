# 🚀 Cómo Ejecutar AstroDebt

## ⚡ Inicio Rápido (Windows)

### Opción 1: Script Automático (RECOMENDADO)

```cmd
cd "C:\Projects\Hackaton Python\nave_varada"
run.bat
```

Este script:
- ✅ Verifica Python
- ✅ Crea entorno virtual si no existe
- ✅ Instala dependencias automáticamente
- ✅ Ejecuta el juego

### Opción 2: Manual Paso a Paso

```cmd
cd "C:\Projects\Hackaton Python\nave_varada"

# Crear entorno virtual (solo primera vez)
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias (solo primera vez)
pip install -r requirements.txt

# Ejecutar el juego
python main.py
```

### Opción 3: Python Directo (Sin Venv)

```cmd
cd "C:\Projects\Hackaton Python\nave_varada"

# Instalar dependencias globalmente (no recomendado)
pip install -r requirements.txt

# Ejecutar
python main.py
```

---

## 🐳 Docker - Limitaciones en Windows

### ⚠️ IMPORTANTE: Docker + GUI en Windows

**Docker NO funciona bien con Pygame en Windows** porque:
- ❌ No hay acceso directo a la GUI de Windows
- ❌ Pygame requiere una ventana gráfica
- ❌ `docker-compose up -d` ejecutará el contenedor pero no verás nada

### ✅ Cuándo SÍ usar Docker

Docker es útil para:
- ✅ **Tests sin GUI**: `docker-compose run dev pytest`
- ✅ **Verificar imports**: `docker-compose run dev python -c "import pygame"`
- ✅ **CI/CD**: Integración continua
- ✅ **Verificar dependencias**: Asegurar que todo funciona en contenedor

### 🔧 Usar Docker para Desarrollo (Sin GUI)

```bash
# Construir imagen
docker-compose build dev

# Ejecutar shell interactivo
docker-compose run dev

# Dentro del contenedor puedes:
# - Ejecutar tests: pytest
# - Verificar imports: python -c "import pygame; print('OK')"
# - Ejecutar scripts: python -m some_module
```

### 📋 Comandos Docker Útiles

```bash
# Construir imagen
docker-compose build

# Shell interactivo para desarrollo
docker-compose run dev bash

# Ejecutar tests en Docker
docker-compose run dev pytest tests/ -v

# Verificar que las dependencias están OK
docker-compose run dev pip list

# Limpiar contenedores
docker-compose down

# Reconstruir desde cero
docker-compose build --no-cache
```

---

## 🖥️ Solución para Docker + GUI (Avanzado)

### En Linux (Funciona)

Si estuvieras en Linux, podrías descomentar en `docker-compose.yml`:

```yaml
environment:
  - DISPLAY=${DISPLAY}
volumes:
  - /tmp/.X11-unix:/tmp/.X11-unix:rw
network_mode: host
```

Y ejecutar:
```bash
xhost +local:docker
docker-compose up astrodebt
```

### En Windows (Complejo)

Para que funcione en Windows necesitarías:
1. **VcXsrv** o **Xming** (servidor X11 para Windows)
2. Configurar DISPLAY variable
3. Modificar docker-compose.yml

**No lo recomiendo** - es muy complejo y propenso a errores.

---

## 🎯 Resumen de Recomendaciones

| Escenario | Solución | Comando |
|-----------|----------|---------|
| **Desarrollo del juego** | Local + venv | `run.bat` |
| **Probar el juego** | Local + venv | `python main.py` |
| **Ejecutar tests** | Local o Docker | `pytest` o `docker-compose run dev pytest` |
| **Verificar dependencias** | Docker | `docker-compose run dev pip list` |
| **CI/CD** | Docker | En pipeline |

---

## 📝 Problemas Comunes

### "docker-compose up -d no muestra nada"
**Causa**: Pygame necesita GUI, Docker en Windows no la tiene.  
**Solución**: Usa `run.bat` para ejecutar localmente.

### "ModuleNotFoundError: No module named 'pygame'"
**Causa**: Dependencias no instaladas.  
**Solución**: `pip install -r requirements.txt`

### "python: command not found"
**Causa**: Python no está en PATH.  
**Solución**: Reinstala Python marcando "Add to PATH" o usa `py` en lugar de `python`.

### "Cannot find path 'venv'"
**Causa**: Entorno virtual no creado.  
**Solución**: `python -m venv venv`

---

## ✅ Flujo de Trabajo Recomendado

### Para Desarrollo:

```bash
# 1. Primera vez - Setup
cd "C:\Projects\Hackaton Python\nave_varada"
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Cada día - Activar y trabajar
venv\Scripts\activate
python main.py

# 3. Antes de commit - Tests
pytest

# 4. (Opcional) Verificar en Docker
docker-compose run dev pytest
```

### Para Implementar:

```bash
# 1. Activar venv
venv\Scripts\activate

# 2. Editar código
# ... trabajar en tu editor ...

# 3. Probar cambios
python main.py

# 4. Ejecutar tests
pytest tests/test_finance.py -v

# 5. Repetir
```

---

## 🆘 ¿Necesitas Ayuda?

### Verificar que todo funciona:

```bash
cd "C:\Projects\Hackaton Python\nave_varada"
python run.py
```

Este script verifica:
- ✅ Versión de Python
- ✅ Dependencias instaladas
- ✅ Archivos presentes
- ✅ Módulos correctos

### Reinstalar desde cero:

```bash
# Borrar entorno virtual
rmdir /s /q venv

# Crear nuevo
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

# Probar
python main.py
```

---

## 📚 Recursos Adicionales

- **QUICKSTART.md** - Inicio rápido en 5 minutos
- **DEVELOPMENT.md** - Guía de desarrollo completa
- **README.md** - Documentación principal

---

**Resumen**: Para desarrollar este juego en Windows, usa **`run.bat`** o ejecuta Python localmente. Docker es útil para tests y CI/CD, pero no para la GUI del juego.

