# 🏛️ Arquitectura de AstroDebt

Este documento describe la arquitectura del juego y cómo interactúan los diferentes módulos.

## 📊 Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                           main.py                                │
│                    (Punto de Entrada)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      engine/loop.py                              │
│                    (Bucle Principal)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ handle_input │→ │    update    │→ │    render    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└───────┬──────────────────┬───────────────────┬──────────────────┘
        │                  │                   │
        ▼                  ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ engine/      │   │ engine/      │   │ ui/          │
│ events.py    │   │ state.py     │   │ renderer.py  │
│              │   │              │   │              │
│ EventManager │   │  GameState   │   │  Renderer    │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                   │
       │                  │                   │
       └──────────┬───────┴───────┬───────────┘
                  │               │
      ┌───────────┴───────┐  ┌────┴────────────┐
      ▼                   ▼  ▼                 ▼
┌─────────────┐   ┌─────────────┐   ┌──────────────┐
│ finance/    │   │ gameplay/   │   │ ui/          │
│             │   │             │   │              │
│ LoanManager │   │ ResourceMgr │   │ HUD          │
│ Debt        │   │ RepairSys   │   │ Narrator     │
└─────────────┘   └──────┬──────┘   └──────────────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ gameplay/    │
                  │ minigames/   │
                  │              │
                  │ Mining       │
                  │ Dodge        │
                  │ Wiring       │
                  │ Timing       │
                  └──────────────┘
```

## 🔄 Flujo de Datos

### 1. Inicialización
```
main.py
  ├─> Cargar config.json
  ├─> Crear EventManager
  ├─> Crear GameState
  ├─> Crear Managers (Loan, Resource, Repair)
  ├─> Inyectar dependencias
  ├─> Crear GameLoop
  └─> Iniciar juego
```

### 2. Bucle Principal
```
GameLoop.run()
  ├─> handle_events()
  │     ├─> Procesar input de Pygame
  │     └─> Emitir eventos personalizados
  │
  ├─> update(delta_time)
  │     ├─> Actualizar GameState
  │     ├─> Procesar cola de eventos
  │     ├─> Actualizar managers
  │     └─> Verificar condiciones de victoria/derrota
  │
  └─> render()
        ├─> Renderer.render_frame()
        ├─> HUD.render()
        └─> Narrator.render() (si hay diálogo activo)
```

### 3. Sistema de Eventos
```
Módulo A                EventManager              Módulo B
    │                        │                        │
    │ subscribe(evento, fn)  │                        │
    ├───────────────────────>│                        │
    │                        │                        │
    │                        │      emit(evento)      │
    │                        │<───────────────────────┤
    │                        │                        │
    │   callback(evento)     │                        │
    │<───────────────────────┤                        │
    │                        │                        │
```

## 🧩 Módulos y Responsabilidades

### Engine (Motor del Juego)
- **state.py**: Estado global del juego
  - Recursos vitales (oxígeno)
  - Inventario de materiales
  - Progreso de reparación
  - Estado de victoria/derrota

- **loop.py**: Bucle principal
  - Gestión de fases del juego
  - Procesamiento de input
  - Actualización de lógica
  - Coordinación de renderizado

- **events.py**: Sistema de eventos
  - Pub/Sub pattern
  - Desacoplamiento entre módulos
  - Historial de eventos (debugging)

### Finance (Sistema Financiero)
- **debt.py**: Clases de deuda
  - Zorvax: Interés compuesto estándar
  - K'tar: Interés simple alto, penalizaciones severas
  - Nebulosa: Interés creciente exponencial
  - Amigable: Sin interés, sin penalizaciones

- **loan_manager.py**: Gestor de préstamos
  - Ofertas de préstamos
  - Aceptación y gestión de préstamos activos
  - Procesamiento de pagos
  - Aplicación de penalizaciones

### Gameplay (Mecánicas de Juego)
- **resources.py**: Gestión de recursos
  - Inventario de materiales
  - Límites de almacenamiento
  - Recolección y consumo
  - Comercio/intercambio

- **repair.py**: Sistema de reparación
  - Componentes de la nave
  - Progreso de reparación
  - Requisitos de recursos
  - Condiciones de victoria

- **minigames/**: Minijuegos
  - Mining: Recolección con timing
  - Dodge: Esquivar obstáculos
  - Wiring: Puzzle de circuitos
  - Timing: Calibración rítmica

### UI (Interfaz de Usuario)
- **renderer.py**: Renderizado visual
  - Fondo y ambiente espacial
  - Nave y efectos
  - Gestión de capas

- **hud.py**: Heads-Up Display
  - Barras de recursos
  - Inventario
  - Información de deudas
  - Notificaciones

- **narrator.py**: Sistema narrativo
  - Diálogos con personajes
  - Texto narrativo
  - Opciones de diálogo
  - Tutoriales

## 🔗 Patrones de Diseño Utilizados

### 1. Observer Pattern (EventManager)
Permite comunicación desacoplada entre módulos mediante eventos.

```python
# Módulo se suscribe a eventos
event_manager.subscribe(EventType.LOAN_TAKEN, self.on_loan_taken)

# Otro módulo emite el evento
event_manager.emit(Event(EventType.LOAN_TAKEN, data={...}))
```

### 2. State Pattern (GameState)
Centraliza el estado del juego para facilitar save/load y debugging.

```python
# Guardar estado
state_dict = game_state.save_state()

# Cargar estado
game_state = GameState.load_state(state_dict)
```

### 3. Strategy Pattern (Debt classes)
Diferentes estrategias de cálculo de interés y penalizaciones.

```python
class Debt(ABC):
    @abstractmethod
    def calculate_interest(self) -> float:
        pass

class ZorvaxDebt(Debt):
    def calculate_interest(self) -> float:
        # Implementación de interés compuesto
        ...
```

### 4. Facade Pattern (Managers)
Managers proveen una interfaz simplificada a subsistemas complejos.

```python
# LoanManager oculta la complejidad de múltiples préstamos
loan_manager.process_turn()  # Actualiza todos los préstamos
```

### 5. Game Loop Pattern
Estructura estándar de juegos: input → update → render.

```python
while running:
    handle_events()    # Procesar input
    update(dt)         # Actualizar lógica
    render()           # Dibujar frame
```

## 📦 Dependencias entre Módulos

### Dependencias Directas
```
GameLoop ─depends on─> GameState
GameLoop ─depends on─> EventManager
LoanManager ─depends on─> GameState
LoanManager ─depends on─> EventManager
ResourceManager ─depends on─> GameState
ResourceManager ─depends on─> EventManager
RepairSystem ─depends on─> ResourceManager
Minigames ─depends on─> ResourceManager
```

### Comunicación via Eventos
```
LoanManager ──LOAN_TAKEN──> EventManager ──> HUD
ResourceManager ──MATERIAL_COLLECTED──> EventManager ──> HUD
RepairSystem ──REPAIR_PROGRESS──> EventManager ──> GameState
```

## 🚦 Fases del Juego

```
INICIO
  │
  ▼
EXPLORACIÓN ◄─┐
  │           │
  ├─> Recolectar recursos (minijuego)
  │           │
  ├─> Reparar componente (minijuego)
  │           │
  ├─> Gestionar préstamos (menú)
  │           │
  ├─> Ver inventario/deudas (menú)
  │           │
  └─> Fin de turno
      │
      ├─> Consumir oxígeno
      ├─> Aplicar intereses
      ├─> Verificar game over
      │
      └───────┘

VICTORIA: Nave reparada
DERROTA: Oxígeno agotado o deuda impagable
```

## 🎯 Flujos Críticos

### Flujo de Préstamo
```
1. Jugador solicita préstamo
   └─> LoanManager.offer_loan()

2. Jugador acepta oferta
   └─> LoanManager.accept_loan()
       ├─> Añadir a active_loans
       ├─> Actualizar recursos del jugador
       └─> Emitir evento LOAN_TAKEN

3. Fin de turno
   └─> LoanManager.process_turn()
       ├─> Calcular intereses
       ├─> Aplicar penalizaciones si hay default
       └─> Emitir eventos correspondientes
```

### Flujo de Reparación
```
1. Jugador selecciona componente
   └─> RepairSystem.start_repair()
       ├─> Verificar recursos
       ├─> Consumir recursos
       └─> Iniciar minijuego

2. Jugador completa minijuego
   └─> Minigame.complete()
       └─> Retorna progreso obtenido

3. Actualizar componente
   └─> RepairSystem.complete_repair_step()
       ├─> Añadir progreso al componente
       ├─> Actualizar GameState
       ├─> Emitir evento REPAIR_PROGRESS_CHANGED
       └─> Verificar condición de victoria
```

### Flujo de Minijuego
```
1. Iniciar minijuego
   └─> Minigame.start()
       └─> Inicializar estado del minijuego

2. Bucle del minijuego
   ├─> handle_input()
   ├─> update(dt)
   └─> render()

3. Finalizar
   └─> Minigame.complete()
       ├─> Calcular recompensas
       ├─> Emitir evento MINIGAME_COMPLETED
       └─> Retornar recompensas
```

## 🔒 Condiciones de Victoria y Derrota

### Victoria
```python
def check_victory():
    # Todos los componentes críticos reparados
    return repair_system.can_launch_ship()
```

### Derrota
```python
def check_defeat():
    # Oxígeno agotado
    if game_state.oxygen <= 0:
        return True
    
    # Deuda impagable (todos los acreedores en default severo)
    if loan_manager.is_debt_unmanageable():
        return True
    
    return False
```

## 📈 Escalabilidad

### Añadir Nuevo Tipo de Acreedor
1. Crear clase en `finance/debt.py` heredando de `Debt`
2. Implementar `calculate_interest()` y `apply_penalty()`
3. Añadir a `loan_manager.available_creditors`
4. Configurar en `data/config.json`
5. Añadir textos en `data/localization.json`

### Añadir Nuevo Minijuego
1. Crear archivo en `gameplay/minigames/`
2. Heredar estructura común de minijuegos
3. Implementar métodos requeridos
4. Registrar en `RepairSystem` o donde sea necesario
5. Configurar en `data/config.json`

### Añadir Nuevo Recurso
1. Añadir a enum `ResourceType` en `resources.py`
2. Configurar en `data/config.json`
3. Añadir nombre traducido en `localization.json`
4. Añadir icono en `data/assets/`

## 🐛 Testing Strategy

```
Unit Tests
  ├─> finance/       (test_finance.py)
  ├─> gameplay/      (test_resources.py, test_repair.py)
  └─> engine/        (test_state.py, test_events.py)

Integration Tests
  └─> Test interacción entre módulos

System Tests
  └─> Test flujos completos de juego
```

## 📊 Métricas y Balanceo

Variables clave para balanceo del juego:
- Consumo de oxígeno por turno
- Tasas de interés de cada acreedor
- Recursos requeridos por componente
- Dificultad y recompensas de minijuegos
- Límites de almacenamiento de recursos

Todas ajustables en `data/config.json` sin cambiar código.

---

**Nota**: Esta arquitectura prioriza:
- ✅ Desacoplamiento (via EventManager)
- ✅ Mantenibilidad (código organizado en módulos claros)
- ✅ Testabilidad (lógica separada de presentación)
- ✅ Escalabilidad (fácil añadir nuevos contenidos)

