# 🐳 Ejecutar AstroDebt con Docker en Windows (Con GUI)

## 🎯 Objetivo
Ejecutar el juego en Docker **SIN instalar Python** en tu máquina Windows, pero poder ver la ventana del juego.

---

## 📋 Solución: VcXsrv (Servidor X11)

Para que Docker pueda mostrar ventanas en Windows, necesitas un "puente" entre Docker y Windows. Ese puente es **VcXsrv**.

### Paso 1: Instalar VcXsrv

1. **Descarga VcXsrv**:
   - Sitio oficial: https://sourceforge.net/projects/vcxsrv/
   - Descarga el instalador `.exe`

2. **Instala VcXsrv**:
   - Ejecuta el instalador
   - Sigue el asistente (Next, Next, Install)
   - Ubicación por defecto: `C:\Program Files\VcXsrv`

### Paso 2: Configurar VcXsrv

1. **Ejecuta XLaunch** (viene con VcXsrv)
2. Configuración recomendada:
   
   **Pantalla 1 - Display settings:**
   - ✅ Selecciona: **Multiple windows**
   - Display number: **0**
   - → Next

   **Pantalla 2 - Client startup:**
   - ✅ Selecciona: **Start no client**
   - → Next

   **Pantalla 3 - Extra settings:**
   - ✅ Marca: **Disable access control** ⚠️ (importante!)
   - ✅ Marca: **Native opengl**
   - → Next

   **Pantalla 4:**
   - → Finish

3. **Verifica que VcXsrv está corriendo**:
   - Debe aparecer un icono en la bandeja del sistema (X negra)

### Paso 3: Obtener tu IP de Windows

Abre PowerShell o CMD:

```cmd
ipconfig
```

Busca tu IP (ejemplo: `192.168.1.100`). Generalmente está en:
- **Adaptador Ethernet** (cable)
- **Adaptador Wi-Fi** (inalámbrico)

Anota esta IP, la necesitarás en el siguiente paso.

### Paso 4: Configurar Docker Compose

Edita `docker-compose.yml` y modifica el servicio `astrodebt`:

```yaml
  astrodebt:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: astrodebt-game
    image: astrodebt:latest
    
    # Configuración para GUI en Windows
    environment:
      - DISPLAY=TU_IP:0.0  # ← Cambia TU_IP por tu IP (ej: 192.168.1.100:0.0)
      - LIBGL_ALWAYS_INDIRECT=1
    
    volumes:
      - .:/app:rw
    
    stdin_open: true
    tty: true
    
    command: python main.py
    
    restart: "no"
```

**Ejemplo con IP real:**
```yaml
    environment:
      - DISPLAY=192.168.1.100:0.0
      - LIBGL_ALWAYS_INDIRECT=1
```

### Paso 5: Ejecutar Docker

```bash
# Construir imagen (primera vez)
docker-compose build astrodebt

# Ejecutar el juego
docker-compose up astrodebt
```

¡Deberías ver la ventana de Pygame abrirse! 🎉

---

## 🚀 Uso Diario

### Cada vez que quieras trabajar:

```bash
# 1. Inicia VcXsrv (si no está corriendo)
#    Busca "XLaunch" en el menú de Windows

# 2. Ejecuta Docker
docker-compose up astrodebt
```

### Para apagar:
```bash
# Ctrl+C en la terminal, o en otra terminal:
docker-compose down
```

---

## 🛠️ Configuración Automática (Opcional)

Puedes hacer que VcXsrv se inicie automáticamente:

### Opción A: Atajo en Inicio

1. Abre: `C:\Program Files\VcXsrv`
2. Busca `vcxsrv.exe`
3. Clic derecho → Crear acceso directo
4. Agrega parámetros al acceso directo:
   ```
   "C:\Program Files\VcXsrv\vcxsrv.exe" :0 -multiwindow -clipboard -wgl -ac
   ```
5. Copia el acceso directo a:
   ```
   C:\Users\TU_USUARIO\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
   ```

### Opción B: Script PowerShell

Crea `start-vcxsrv.ps1`:

```powershell
# Verificar si VcXsrv ya está corriendo
$vcxsrv = Get-Process vcxsrv -ErrorAction SilentlyContinue

if ($null -eq $vcxsrv) {
    Write-Host "Iniciando VcXsrv..."
    Start-Process "C:\Program Files\VcXsrv\vcxsrv.exe" -ArgumentList ":0 -multiwindow -clipboard -wgl -ac"
    Start-Sleep -Seconds 2
    Write-Host "VcXsrv iniciado correctamente"
} else {
    Write-Host "VcXsrv ya está corriendo"
}

# Ejecutar docker-compose
Write-Host "Iniciando AstroDebt en Docker..."
docker-compose up astrodebt
```

Ejecuta:
```powershell
.\start-vcxsrv.ps1
```

---

## 🔧 Problemas Comunes

### Problema 1: "Cannot connect to display"

**Solución:**
1. Verifica que VcXsrv está corriendo (icono X en bandeja)
2. Verifica que usaste tu IP correcta en DISPLAY
3. Verifica que marcaste "Disable access control" en VcXsrv
4. Reinicia VcXsrv

### Problema 2: "Connection refused"

**Solución:**
```powershell
# En PowerShell como Administrador:
New-NetFirewallRule -DisplayName "VcXsrv" -Direction Inbound -Program "C:\Program Files\VcXsrv\vcxsrv.exe" -Action Allow
```

### Problema 3: La ventana se abre pero está en negro

**Solución:**
1. En VcXsrv config, asegúrate de marcar "Native opengl"
2. Agrega la variable de entorno en docker-compose:
   ```yaml
   - LIBGL_ALWAYS_INDIRECT=1
   ```

### Problema 4: "Error: Unable to initialize SDL"

**Solución:**
Agrega estas variables de entorno en docker-compose:
```yaml
environment:
  - DISPLAY=TU_IP:0.0
  - SDL_VIDEODRIVER=x11
  - LIBGL_ALWAYS_INDIRECT=1
```

### Problema 5: No sé cuál es mi IP

```cmd
# CMD o PowerShell:
ipconfig | findstr IPv4

# O más simple:
ipconfig
```

Busca la línea que dice "Dirección IPv4" o "IPv4 Address".

---

## 📋 Checklist Completo

- [ ] VcXsrv instalado
- [ ] VcXsrv corriendo (XLaunch ejecutado)
- [ ] "Disable access control" marcado en VcXsrv
- [ ] IP de Windows identificada (ipconfig)
- [ ] docker-compose.yml editado con tu IP
- [ ] Docker Desktop instalado y corriendo
- [ ] Firewall permite VcXsrv (si es necesario)

---

## 🎮 Comandos Útiles

```bash
# Ver si el contenedor está corriendo
docker ps

# Ver logs del contenedor
docker-compose logs astrodebt

# Entrar al contenedor (shell)
docker-compose exec astrodebt bash

# Reconstruir si cambias Dockerfile
docker-compose build --no-cache astrodebt

# Limpiar todo y empezar de cero
docker-compose down
docker system prune -a
docker-compose build astrodebt
docker-compose up astrodebt
```

---

## 🔒 Consideraciones de Seguridad

⚠️ **Importante**: "Disable access control" en VcXsrv permite que cualquier aplicación se conecte al servidor X11. 

**Para mayor seguridad:**
- Solo inicia VcXsrv cuando vayas a usar Docker
- Cierra VcXsrv cuando termines de desarrollar
- No uses esta configuración en redes públicas

**Alternativa más segura** (requiere más configuración):
- Usa autenticación Xauth
- Configura un archivo `.Xauthority`
- Monta el archivo en Docker

---

## 📊 Comparación de Opciones

| Método | Pros | Contras |
|--------|------|---------|
| **Python local** | ✅ Más simple<br>✅ Mejor rendimiento | ❌ Instalar Python<br>❌ Dependencias en Windows |
| **Docker + VcXsrv** | ✅ No instalar Python<br>✅ Ambiente aislado | ❌ Configuración inicial<br>❌ Overhead de Docker |
| **WSL2 + Docker** | ✅ Más nativo<br>✅ Mejor integración | ❌ Requiere WSL2<br>❌ Más complejo |

---

## 🚀 Alternativa: WSL2 (Avanzado)

Si tienes WSL2 habilitado:

1. Instala Docker Desktop con integración WSL2
2. Dentro de WSL2:
   ```bash
   cd /mnt/c/Projects/Hackaton\ Python/nave_varada
   docker-compose up astrodebt
   ```
3. La ventana debería aparecer automáticamente

Esto funciona mejor que VcXsrv pero requiere WSL2.

---

## ✅ Resumen Rápido

Para ejecutar el juego en Docker sin instalar Python:

1. **Instala VcXsrv** (solo una vez)
2. **Ejecuta XLaunch** con "Disable access control"
3. **Obtén tu IP** con `ipconfig`
4. **Edita docker-compose.yml** con tu IP
5. **Ejecuta**: `docker-compose up astrodebt`

¡Y listo! Pygame debería abrirse en una ventana.

---

## 📞 ¿Necesitas Ayuda?

Si tienes problemas:
1. Verifica el checklist completo
2. Revisa la sección "Problemas Comunes"
3. Verifica los logs: `docker-compose logs astrodebt`

---

**Nota**: Esta configuración es para desarrollo. Para producción, considera otras opciones como ejecutables compilados.

