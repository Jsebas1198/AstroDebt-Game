# ⚡ Inicio Rápido - AstroDebt

Guía express para comenzar a trabajar en el proyecto en 5 minutos.

## 🎯 Para Empezar YA

### Opción 1: Scripts Automáticos (Recomendado)

#### Windows
```cmd
run.bat
```

#### Linux/Mac
```bash
chmod +x run.sh
./run.sh
```

### Opción 2: Manual

```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python main.py
```

### Opción 3: Docker

```bash
# Construir y ejecutar
docker-compose up astrodebt

# O con Docker directo
docker build -t astrodebt .
docker run -it --rm astrodebt
```

## 📚 Documentación Esencial

| Archivo | Para qué sirve |
|---------|----------------|
| `README.md` | Visión general del proyecto |
| `DEVELOPMENT.md` | **EMPIEZA AQUÍ** para implementar |
| `ARCHITECTURE.md` | Cómo funciona todo junto |
| `FILELIST.md` | Lista de todos los archivos |

## 🛠️ Primeros Pasos de Desarrollo

### 1️⃣ Lee el Orden de Implementación
Abre `DEVELOPMENT.md` y sigue el orden sugerido.

### 2️⃣ Comienza con el Sistema de Eventos
```bash
# Abre en tu editor
code engine/events.py
```

Implementa:
- `subscribe()` y `unsubscribe()`
- `emit()` y `queue_event()`
- `process_queue()`

### 3️⃣ Ejecuta Tests
```bash
# Mientras desarrollas, ejecuta tests
pytest tests/test_finance.py -v
```

### 4️⃣ Verifica con Linter
```bash
# Opcional: verifica tu código
pylint engine/events.py
mypy engine/events.py
```

## 📋 Checklist Rápido

Antes de empezar a programar:

- [ ] Python 3.13.7 instalado (o 3.9+)
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] `DEVELOPMENT.md` leído
- [ ] Editor de código abierto
- [ ] Git configurado (opcional)

## 🎮 Estructura del Juego

```
Usuario juega
    ↓
Recolecta recursos (minijuegos)
    ↓
Repara la nave
    ↓
¡Pero necesita más recursos!
    ↓
Pide préstamos a alienígenas
    ↓
Cada turno: paga intereses, consume oxígeno
    ↓
Victoria: Nave reparada
Derrota: Sin oxígeno o deuda impagable
```

## 🔑 Conceptos Clave

### Sistema de Eventos (Pub/Sub)
```python
# Módulo A se suscribe
event_manager.subscribe(EventType.LOAN_TAKEN, callback)

# Módulo B emite evento
event_manager.emit(Event(EventType.LOAN_TAKEN, data={...}))

# Módulo A recibe automáticamente
```

### Flujo de un Turno
```python
1. Jugador realiza acciones
2. Fin de turno
   → Consumir oxígeno
   → Aplicar intereses de préstamos
   → Verificar game over
3. Nuevo turno
```

### Acreedores
```python
Zorvax:    5% interés compuesto,  penalizaciones moderadas
K'tar:     10% interés simple,    penalizaciones SEVERAS
Nebulosa:  2% → exponencial,      penalizaciones catastróficas
Amigo:     0.5% o 0%,             sin penalizaciones reales
```

## 💡 Tips Rápidos

### Encuentra TODOs
```bash
# Busca todos los TODOs en el proyecto
grep -r "TODO" --include="*.py" .
```

### Ejecuta un Solo Test
```bash
pytest tests/test_finance.py::TestDebtClasses::test_zorvax_debt_creation -v
```

### Debug con el Historial de Eventos
```python
# En tu código
events = event_manager.get_history()
for event in events:
    print(f"{event.event_type}: {event.data}")
```

### Ajusta el Balanceo
Edita `data/config.json` para cambiar:
- Tasas de interés
- Consumo de oxígeno
- Recursos requeridos
- Dificultad de minijuegos

## 🚫 Errores Comunes

### "ModuleNotFoundError: No module named 'pygame'"
**Solución**: `pip install -r requirements.txt`

### "Import error" entre módulos
**Solución**: Usa imports absolutos desde la raíz del proyecto
```python
# Bien ✅
from engine.state import GameState

# Mal ❌
from ..engine.state import GameState
```

### Pygame no funciona en Docker
**Nota**: Pygame con GUI requiere configuración especial de X11 en Docker.
Para desarrollo, usa el entorno local en lugar de Docker.

## 📖 Ejemplo: Implementar una Función

Antes (esqueleto):
```python
def calculate_interest(self) -> float:
    """Calcula el interés para el turno actual"""
    # TODO: Implementar fórmula de interés compuesto
    pass
```

Después (implementado):
```python
def calculate_interest(self) -> float:
    """Calcula el interés para el turno actual"""
    # Interés compuesto: P * (1 + r)^t - P
    interest = self.current_balance * self.interest_rate
    return interest
```

## 🎯 Meta del Proyecto

**Crear un juego funcional y educativo que enseñe:**
- Tipos de interés (simple, compuesto, exponencial)
- Consecuencias de endeudarse
- Gestión de recursos bajo presión
- Toma de decisiones financieras

## 📞 Recursos Útiles

- [Pygame Docs](https://www.pygame.org/docs/)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Docs](https://docs.pytest.org/)

## 🚀 Comandos Más Usados

```bash
# Ejecutar juego
python main.py

# Tests
pytest
pytest -v
pytest --cov=.

# Linting
pylint engine/
mypy engine/

# Ver estructura
tree nave_varada/    # Linux/Mac
dir /s /b           # Windows
```

## ✅ ¡Listo!

Ahora tienes todo lo necesario para empezar. Recuerda:

1. **Lee** `DEVELOPMENT.md` primero
2. **Implementa** en el orden sugerido
3. **Testea** constantemente con pytest
4. **Balancea** editando config.json
5. **Diviértete** programando 🎮

---

**¿Dudas?** Revisa la documentación en:
- `README.md` - Visión general
- `DEVELOPMENT.md` - Guía de desarrollo
- `ARCHITECTURE.md` - Arquitectura técnica
- `FILELIST.md` - Lista de archivos

¡Buena suerte! 🚀

