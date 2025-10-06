# 🔧 Guía de Desarrollo - AstroDebt

Esta guía documenta la estructura actual del proyecto y proporciona orientación para desarrolladores que se unan al equipo o necesiten extender funcionalidades existentes.

> **Nota**: Este proyecto está **completamente implementado y funcional**. Esta guía sirve como referencia para entender la arquitectura y añadir nuevas características.

## 📁 Estructura del Proyecto

### Carpetas Principales

```
nave_varada/
├── engine/              # Motor del juego (core)
├── finance/             # Sistema financiero y préstamos
├── gameplay/            # Mecánicas de juego y minijuegos
├── ui/                  # Interfaz de usuario
├── data/                # Configuración y assets
├── tests/               # Pruebas unitarias
└── main.py              # Punto de entrada
```

### 🎮 engine/ - Motor del Juego

**Propósito**: Núcleo del juego, gestiona el estado global, eventos y el bucle principal.

#### **engine/state.py** - Estado Global
- **Qué hace**: Mantiene todo el estado del juego (oxígeno, materiales, progreso, fase actual)
- **Responsabilidades**:
  - Gestión de recursos (oxígeno, materiales)
  - Progreso de reparación (0-100%)
  - Fases del juego (intro, main_game, minigame, end)
  - Condiciones de victoria/derrota
  - Referencias a managers (loan_manager, resource_manager, repair_system)
- **Estado**: ✅ **Completamente implementado**
- **Métodos clave**:
  - `update_oxygen(amount)`: Modifica oxígeno con límite de 100
  - `add_materials(amount)`: Añade materiales con límite de 999
  - `consume_materials(amount)`: Consume materiales con validación
  - `update_repair_progress(amount)`: Actualiza progreso de reparación
  - `advance_turn()`: Avanza el turno del juego
  - `check_game_over()`: Verifica condiciones de derrota
  - `save_state()` / `load_state()`: Serialización del estado

#### **engine/events.py** - Sistema de Eventos
- **Qué hace**: Implementa patrón Observer/PubSub para comunicación entre módulos
- **Responsabilidades**:
  - Suscripción y desuscripción de callbacks
  - Emisión de eventos (inmediata y en cola)
  - Historial de eventos para debugging
- **Estado**: ✅ **Completamente implementado**
- **Tipos de eventos**: 20+ eventos definidos en `EventType` enum
  - Estado: OXYGEN_CHANGED, MATERIALS_GAINED, REPAIR_PROGRESS_CHANGED
  - Minijuegos: MINIGAME_STARTED, MINIGAME_COMPLETED
  - Préstamos: LOAN_APPEARED, LOAN_ACCEPTED, PENALTY_APPLIED
  - Juego: PHASE_CHANGED, GAME_OVER, VICTORY
- **Métodos clave**:
  - `subscribe(event_type, callback)`: Suscribir a eventos
  - `emit(event)`: Emitir evento inmediatamente
  - `emit_quick(event_type, data)`: Atajo para emisión rápida
  - `process_queue()`: Procesar eventos en cola

#### **engine/loop.py** - Bucle Principal
- **Qué hace**: Coordina el flujo del juego, maneja input, actualiza lógica y renderiza
- **Responsabilidades**:
  - Gestión de fases (intro → main_game → minigame → end)
  - Procesamiento de input según fase y prioridades
  - Actualización de lógica del juego
  - Coordinación de renderizado
  - Inicio de minijuegos (minería, reparación, rescate de oxígeno)
  - Verificación de eventos especiales (prestamista, rescate marciano)
- **Estado**: ✅ **Completamente implementado**
- **Métodos clave**:
  - `start()`: Inicia el bucle principal
  - `handle_events()`: Procesa eventos de Pygame
  - `update(delta_time)`: Actualiza lógica según fase
  - `render()`: Coordina renderizado de todos los componentes
  - `change_phase(new_phase)`: Cambia fase del juego
  - `start_mining_minigame()`: Inicia minijuego de minería
  - `start_repair_minigame()`: Inicia minijuego de reparación
  - `start_oxygen_rescue_minigame()`: Inicia evento especial de rescate

### 💰 finance/ - Sistema Financiero

**Propósito**: Gestiona préstamos, deudas, intereses y penalizaciones.

#### **finance/debt.py** - Clases de Deuda
- **Qué hace**: Define diferentes tipos de acreedores con sus reglas de interés
- **Responsabilidades**:
  - Cálculo de intereses (compuesto, simple, exponencial)
  - Aplicación de penalizaciones por impago
  - Gestión de pagos y amortización
- **Estado**: ✅ **Completamente implementado**
- **Tipos de acreedores**:
  - `ZorvaxDebt`: Interés compuesto estándar (5% por turno)
  - `KtarrDebt`: Interés simple alto (10% por turno) + penalizaciones severas
  - `NebulaDebt`: Interés exponencial creciente (comienza bajo, crece rápido)
  - `FriendlyDebt`: Sin interés, sin penalizaciones (tutorial/ayuda)
- **Métodos clave**:
  - `calculate_interest()`: Calcula interés según tipo
  - `apply_penalty()`: Aplica penalización por impago
  - `make_payment(amount)`: Procesa pago parcial o total

#### **finance/loan_manager.py** - Gestor de Préstamos
- **Qué hace**: Administra ofertas de préstamos y préstamos activos
- **Responsabilidades**:
  - Generar ofertas de préstamos aleatorias
  - Aceptar/rechazar préstamos
  - Procesar turnos (aplicar intereses)
  - Gestionar múltiples préstamos activos
  - Emitir eventos de préstamos
- **Estado**: ✅ **Completamente implementado**
- **Métodos clave**:
  - `offer_loan()`: Genera oferta aleatoria de préstamo
  - `accept_loan(loan)`: Acepta préstamo y añade oxígeno
  - `process_turn()`: Actualiza todos los préstamos activos
  - `get_total_debt()`: Calcula deuda total

### 🎯 gameplay/ - Mecánicas de Juego

**Propósito**: Implementa las mecánicas core del juego (recursos, reparación, minijuegos).

#### **gameplay/resources.py** - Gestión de Recursos
- **Qué hace**: Administra el inventario de materiales del jugador
- **Responsabilidades**:
  - Recolección de materiales
  - Consumo de materiales
  - Verificación de disponibilidad
  - Límites de almacenamiento
- **Estado**: ✅ **Completamente implementado**
- **Métodos clave**:
  - `collect_resource(amount)`: Añade materiales con límite
  - `consume_resource(amount)`: Consume materiales con validación
  - `has_resources(amount)`: Verifica disponibilidad

#### **gameplay/repair.py** - Sistema de Reparación
- **Qué hace**: Gestiona el progreso de reparación de la nave
- **Responsabilidades**:
  - Iniciar proceso de reparación
  - Actualizar progreso
  - Verificar condición de victoria (100% reparado)
  - Consumir recursos para reparación
- **Estado**: ✅ **Completamente implementado**
- **Métodos clave**:
  - `start_repair()`: Inicia reparación (consume recursos)
  - `complete_repair_step(progress)`: Añade progreso de reparación
  - `can_launch_ship()`: Verifica si nave está lista (100%)

#### **gameplay/minigames/** - Minijuegos Interactivos

**Propósito**: Minijuegos que el jugador completa para obtener recursos o progreso.

##### **gameplay/minigames/base.py** - Clase Base
- **Qué hace**: Clase abstracta que define la estructura común de todos los minijuegos
- **Responsabilidades**:
  - Definir interfaz común (load_assets, handle_input, update, render)
  - Gestionar estado del minijuego (is_complete, success, score)
  - Inicializar fuentes y superficie de renderizado
- **Estado**: ✅ **Completamente implementado**

##### **gameplay/minigames/mining.py** - Mineral Rush
- **Tipo**: Whack-a-Mole con minerales
- **Objetivo**: Hacer clic en minerales antes de que desaparezcan
- **Duración**: 10 segundos
- **Recompensa**: Hasta 7 materiales
- **Mecánicas**:
  - 9 minas en grid 3x3
  - 3 tipos de minerales (Cobre 0.05, Plata 0.1, Oro 0.2)
  - Sistema de combos (×2, ×3, ×5)
  - Partículas y efectos visuales
- **Estado**: ✅ **Completamente implementado**

##### **gameplay/minigames/asteroid_shooter.py** - Shooter Espacial
- **Tipo**: Shooter espacial top-down
- **Objetivo**: Destruir asteroides
- **Duración**: 30 segundos
- **Recompensa**: Materiales según asteroides destruidos
- **Mecánicas**:
  - Control WASD + disparo con mouse
  - Asteroides de diferentes tamaños
  - Sistema de puntuación
- **Estado**: ✅ **Completamente implementado**

##### **gameplay/minigames/timing.py** - Timing Precision
- **Tipo**: Calibración rítmica
- **Objetivo**: Presionar ESPACIO en zona verde
- **Mecánicas**:
  - 3 barras consecutivas para ganar
  - Velocidad aumenta progresivamente
  - Zona verde se reduce con cada éxito
- **Recompensa**: Progreso de reparación
- **Estado**: ✅ **Completamente implementado**

##### **gameplay/minigames/wiring.py** - Wiring Puzzle
- **Tipo**: Puzzle de conexiones
- **Objetivo**: Conectar cables correctamente
- **Mecánicas**:
  - Arrastrar y soltar cables
  - Validación de conexiones correctas
  - Límite de tiempo
- **Recompensa**: Progreso de reparación
- **Estado**: ✅ **Completamente implementado**

##### **gameplay/minigames/oxygen_rescue.py** - Rescate del Marciano
- **Tipo**: Shooter top-down con combate
- **Objetivo**: Derrotar 5 enemigos para rescatar al marciano
- **Trigger**: Oxígeno < 80% (evento único)
- **Mecánicas**:
  - Control WASD + disparo con mouse
  - 5 enemigos (2 izquierda, 2 derecha, 1 arriba)
  - Sistema de vida para jugador y enemigos
  - Proyectiles (naranja jugador, azul enemigos)
  - Flecha indicadora de dirección
- **Recompensa**: +10 oxígeno si gana
- **Estado**: ✅ **Completamente implementado**

##### **gameplay/minigames/dodge.py** - Placeholder
- **Estado**: ⚠️ **No implementado** (placeholder para futuro)

### 🖥️ ui/ - Interfaz de Usuario

**Propósito**: Renderizado visual y presentación de información al jugador.

#### **ui/renderer.py** - Renderizado Visual
- **Qué hace**: Renderiza el fondo, nave, efectos visuales y prestamista
- **Responsabilidades**:
  - Renderizar fondo espacial con parallax
  - Renderizar nave con animaciones
  - Efectos visuales (shake, partículas)
  - Renderizar prestamista (NPC) con diálogos
  - Gestión de capas de renderizado
- **Estado**: ✅ **Completamente implementado**
- **Métodos clave**:
  - `render_frame(screen)`: Renderiza frame completo
  - `render_background()`: Fondo espacial animado
  - `render_ship()`: Nave con efectos
  - `render_lender()`: Prestamista con diálogo
  - `show_lender()` / `dismiss_lender()`: Control de prestamista

#### **ui/hud.py** - Heads-Up Display
- **Qué hace**: Muestra información del juego (barras, paneles, notificaciones, modal de intercambio)
- **Responsabilidades**:
  - Barras de recursos (oxígeno, materiales, reparación)
  - Paneles informativos (inventario, deudas, reparación)
  - Notificaciones flotantes
  - Menú de acciones ([M] Minar, [R] Reparar, [O] Conseguir Oxígeno)
  - **Modal de intercambio**: Vender materiales por oxígeno (1 material = 5 oxígeno)
  - Botón visual "Conseguir Oxígeno" con estados
- **Estado**: ✅ **Completamente implementado**
- **Características especiales**:
  - Sistema de intercambio con slider interactivo
  - Validaciones inteligentes (no exceder 100 oxígeno, máximo vendible)
  - Bloqueo de input durante minijuegos
  - Cierre automático de paneles al entrar a minijuegos
- **Métodos clave**:
  - `render()`: Renderiza todo el HUD
  - `render_oxygen_bar()` / `render_materials_bar()` / `render_repair_progress()`
  - `render_inventory_panel()` / `render_debt_panel()` / `render_repair_panel()`
  - `open_exchange_modal()` / `confirm_exchange()`: Sistema de intercambio
  - `add_notification(message, type)`: Notificaciones flotantes

#### **ui/narrator.py** - Sistema Narrativo
- **Qué hace**: Muestra diálogos, narrativa y opciones de decisión
- **Responsabilidades**:
  - Diálogos con NPCs
  - Narrativa de eventos
  - Opciones de diálogo (Y/N)
  - Efecto de escritura (typewriter)
  - Tutorial y explicaciones
- **Estado**: ✅ **Completamente implementado**
- **Métodos clave**:
  - `show_narrative(text)`: Muestra texto narrativo
  - `show_dialogue(character, text, options)`: Diálogo con opciones
  - `handle_input(event)`: Procesa input del jugador

### 📦 data/ - Datos y Assets

**Propósito**: Almacena configuración, localización y recursos visuales.

#### **data/config.json** - Configuración del Juego
- **Qué contiene**: Parámetros de juego, balanceo, configuración de ventana
- **Secciones**:
  - `game`: Título, resolución, FPS
  - `gameplay`: Oxígeno inicial, consumo, umbrales
  - `creditors`: Configuración de prestamistas
  - `components`: Componentes de la nave a reparar

#### **data/localization.json** - Textos del Juego
- **Qué contiene**: Todos los textos en español
- **Secciones**:
  - `ui`: Textos de interfaz
  - `dialogues`: Diálogos de NPCs
  - `creditors`: Nombres y descripciones de prestamistas
  - `notifications`: Mensajes de notificaciones

#### **data/assets/** - Recursos Visuales
- **Imágenes del juego**: PNG con transparencia
- **Categorías**:
  - Nave y jugador: `blue_spaceship.png`, `player.png`, `player_weapon.png`
  - NPCs: `npc_helper.png`, `alien.png`, `ktarr_alien.png`, `zorvax_alien.png`
  - Enemigos: `seal_left.png`, `seal_right.png`
  - Minerales: `copper_mineral.png`, `silver_mineral.png`, `gold_mineral.png`
  - UI: Barras, botones, alertas
  - Fondos de minijuegos: `minigame_*.png`
  - Fondos: `space_background.png`, `landing_moon.png`

### 🧪 tests/ - Pruebas Unitarias

**Propósito**: Validar funcionalidad de módulos críticos.

- **tests/test_finance.py**: Pruebas del sistema financiero
- **tests/test_repair.py**: Pruebas del sistema de reparación
- **tests/test_resources.py**: Pruebas de gestión de recursos
- **Estado**: ✅ Pruebas implementadas para módulos core

### 📄 Archivos Raíz

- **main.py**: Punto de entrada, inicializa todos los sistemas
- **test_game.py**: Script de prueba rápida del juego
- **test_minigames.py**: Script para probar minijuegos individualmente
- **requirements.txt**: Dependencias de Python (pygame)
- **run.py** / **run.sh** / **run.bat**: Scripts de ejecución multiplataforma
- **Dockerfile** / **docker-compose.yml**: Configuración de Docker
- **README.md**: Documentación principal del proyecto
- **ARCHITECTURE.md**: Documentación de arquitectura detallada
- **GAME_README.md**: Guía del jugador
- **QUICKSTART.md**: Guía de inicio rápido

## 🔄 Flujo de Inicialización

El juego se inicializa en el siguiente orden (ver `main.py`):

```python
1. Cargar config.json
2. Inicializar Pygame
3. Crear instancias principales:
   - EventManager (sistema de eventos)
   - GameState (estado global)
   - ResourceManager, LoanManager, RepairSystem (managers)
   - Renderer, HUD, Narrator (UI)
4. Conectar referencias cruzadas (inyección de dependencias):
   - game_state ↔ loan_manager, resource_manager, repair_system
   - managers → event_manager
   - hud → game_state, loan_manager, resource_manager
   - narrator → event_manager
5. Inicializar componentes (cargar assets, configurar UI)
6. Crear GameLoop y asignar componentes
7. Iniciar bucle principal (game_loop.start())
```

## 🎮 Flujo del Juego

### Fases del Juego

El juego tiene 4 fases principales gestionadas por `GameState.current_phase`:

1. **"intro"**: Historia inicial, tutorial
   - Narrador muestra contexto del juego
   - Jugador presiona SPACE para continuar
   - Transición automática a "main_game"

2. **"main_game"**: Juego principal
   - Jugador puede:
     - [M] Minar materiales (minijuego)
     - [R] Reparar nave (minijuego)
     - [O] Conseguir oxígeno (modal de intercambio)
     - [I] Ver inventario
     - [D] Ver deudas
     - [P] Ver progreso de reparación
   - Eventos especiales:
     - Prestamista (oxígeno < 90%, una vez)
     - Rescate del Marciano (oxígeno < 80%, una vez)
   - Verificación continua de game over

3. **"minigame"**: Minijuego activo
   - Input delegado completamente al minijuego
   - HUD bloqueado (no se pueden abrir paneles)
   - Al completar, vuelve a "main_game" con recompensas

4. **"end"**: Victoria o derrota
   - Muestra pantalla final con estadísticas
   - Opciones: Reiniciar o Salir

### Eventos Especiales

#### Prestamista Educativo
- **Trigger**: `oxygen < 90 AND !prestamista_shown`
- **Propósito**: Enseñar al jugador sobre préstamos
- **Flujo**:
  1. Aparece NPC helper
  2. Jugador presiona SPACE para ver prestamista
  3. Prestamista ofrece préstamo
  4. Jugador puede aceptar o rechazar
  5. Flag `prestamista_shown = True`

#### Rescate del Marciano
- **Trigger**: `oxygen < 80 AND !oxygen_event_shown`
- **Propósito**: Dar al jugador oportunidad de recuperar oxígeno
- **Flujo**:
  1. Narrador muestra historia del marciano
  2. Opciones: [Y] Ayudar / [N] Rechazar
  3. Si acepta: Inicia minijuego `OxygenRescueMinigame`
  4. Victoria: +10 oxígeno
  5. Derrota: Sin recompensa
  6. Flag `oxygen_event_shown = True`
  7. **No aparece prestamista después** de este evento

## 🎯 Checklist para Añadir Nuevas Características

### Añadir Nuevo Minijuego

1. **Crear archivo** en `gameplay/minigames/nuevo_minijuego.py`
2. **Heredar de `BaseMinigame`**:
   ```python
   from .base import BaseMinigame
   
   class NuevoMinigame(BaseMinigame):
       def __init__(self, screen_width, screen_height):
           super().__init__(screen_width, screen_height)
           # Inicialización específica
   ```
3. **Implementar métodos abstractos**:
   - `load_assets()`: Cargar imágenes, sonidos
   - `handle_input(event)`: Procesar input del jugador
   - `update(delta_time)`: Actualizar lógica del minijuego
   - `render(screen)`: Dibujar en pantalla
   - `get_results()`: Retornar recompensas
4. **Exportar en `__init__.py`**:
   ```python
   from .nuevo_minigame import NuevoMinigame
   __all__ = [..., 'NuevoMinigame']
   ```
5. **Registrar en `engine/loop.py`**:
   - Importar el minijuego
   - Añadir a rotación en `start_mining_minigame()` o `start_repair_minigame()`
6. **Añadir assets** en `data/assets/`
7. **Probar** con `test_minigames.py`

### Añadir Nuevo Tipo de Acreedor

1. **Crear clase** en `finance/debt.py`:
   ```python
   class NuevoAcreedor(Debt):
       def calculate_interest(self) -> float:
           # Implementar lógica de interés
           pass
       
       def apply_penalty(self) -> float:
           # Implementar penalización
           pass
   ```
2. **Añadir a `LoanManager.available_creditors`** en `finance/loan_manager.py`
3. **Configurar** en `data/config.json`:
   ```json
   "creditors": {
       "nuevo_acreedor": {
           "name": "Nombre del Acreedor",
           "interest_rate": 0.05,
           ...
       }
   }
   ```
4. **Añadir textos** en `data/localization.json`
5. **Añadir imagen** del acreedor en `data/assets/`
6. **Probar** con `tests/test_finance.py`

### Añadir Nueva Mecánica de UI

1. **Decidir ubicación**: ¿HUD, Renderer o Narrator?
2. **Implementar en módulo correspondiente**:
   - HUD: Información interactiva, paneles, modales
   - Renderer: Efectos visuales, animaciones
   - Narrator: Diálogos, narrativa
3. **Añadir manejo de input** si es necesario
4. **Emitir eventos** para comunicación con otros módulos
5. **Actualizar `render()` o `update()`** del módulo
6. **Añadir assets visuales** si se requieren

### Añadir Nuevo Evento Especial

1. **Definir trigger** (condición para activar)
2. **Añadir flag** en `GameState` (ej: `evento_shown = False`)
3. **Implementar verificación** en `engine/loop.py` → `update()`
4. **Crear narrativa** para el evento
5. **Implementar consecuencias** (minijuego, recompensa, etc.)
6. **Marcar flag** como `True` después de mostrar
7. **Probar** diferentes escenarios

## 🧪 Ejecutar Pruebas Durante Desarrollo

```bash
# Prueba un módulo específico mientras lo desarrollas
pytest tests/test_finance.py -v

# Prueba con cobertura
pytest tests/test_finance.py --cov=finance --cov-report=term-missing

# Modo watch (requiere pytest-watch)
# pip install pytest-watch
ptw tests/test_finance.py
```

## 🎨 Convenciones de Código

### Naming
- Clases: `PascalCase`
- Funciones/métodos: `snake_case`
- Constantes: `UPPER_SNAKE_CASE`
- Privados: `_leading_underscore`

### Type Hints
Usa type hints siempre que sea posible:
```python
def collect_resource(self, resource_type: ResourceType, amount: int) -> int:
    ...
```

### Docstrings
Usa formato Google/NumPy:
```python
def example_function(param1: str, param2: int) -> bool:
    """
    Descripción breve de la función.
    
    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2
        
    Returns:
        Descripción del valor de retorno
        
    Raises:
        ValueError: Cuando y por qué se lanza
    """
```

## 🔌 Conexión entre Módulos

### Patrón de Inyección de Dependencias

Los módulos se conectan mediante referencias asignadas después de la creación:

```python
# En main.py o donde inicialices
game_state = GameState()
event_manager = EventManager()
loan_manager = LoanManager()

# Inyectar dependencias
loan_manager.event_manager = event_manager
loan_manager.game_state = game_state
game_state.loan_manager = loan_manager
```

### Sistema de Eventos

Usa el EventManager para comunicación desacoplada:

```python
# En un módulo, suscribirse a eventos
event_manager.subscribe(EventType.MATERIAL_COLLECTED, self.on_material_collected)

# En otro módulo, emitir eventos
event = Event(
    event_type=EventType.MATERIAL_COLLECTED,
    data={'resource_type': ResourceType.METAL, 'amount': 10}
)
event_manager.emit(event)
```

## 🐛 Debugging

### Historial de Eventos
El EventManager mantiene un historial:
```python
# Ver todos los eventos recientes
history = event_manager.get_history()

# Filtrar por tipo
debt_events = event_manager.get_history(EventType.LOAN_TAKEN)
```

### Estado del Juego
Serializa el estado para debugging:
```python
state_dict = game_state.save_state()
print(json.dumps(state_dict, indent=2))
```

## 📊 Balanceo del Juego

Ajusta estos valores en `data/config.json`:

- **Oxígeno**: Consumo por turno vs capacidad
- **Recursos**: Valores, límites de almacenamiento
- **Préstamos**: Tasas de interés, términos
- **Componentes**: Dificultad de reparación, recursos requeridos
- **Minijuegos**: Tiempo límite, multiplicadores de dificultad

## 🎮 Sistema de Minijuegos

### Estructura Común (BaseMinigame)

Todos los minijuegos heredan de `BaseMinigame` y deben implementar:

```python
from gameplay.minigames.base import BaseMinigame

class NuevoMinigame(BaseMinigame):
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        super().__init__(screen_width, screen_height)
        # Inicialización específica del minijuego
        
    def load_assets(self) -> None:
        """Cargar imágenes, sonidos, etc."""
        # Implementar carga de assets
        
    def handle_input(self, event: pygame.event.Event) -> None:
        """Procesar input del jugador"""
        # Implementar manejo de input
        
    def update(self, delta_time: float) -> None:
        """Actualizar lógica del minijuego"""
        # Implementar lógica de actualización
        # Actualizar self.time_remaining
        # Verificar condiciones de victoria/derrota
        # Marcar self.is_complete = True cuando termine
        
    def render(self, screen: pygame.Surface) -> None:
        """Dibujar el minijuego"""
        # Implementar renderizado
        
    def get_results(self) -> Dict[str, Any]:
        """Retornar resultados y recompensas"""
        return {
            'success': self.success,
            'score': self.score,
            'reward_materials': self.reward_materials,  # Para minijuegos de minería
            'reward_repair': self.reward_repair,        # Para minijuegos de reparación
            'reward_oxygen': 0                          # Para eventos especiales
        }
```

### Propiedades Heredadas de BaseMinigame

```python
# Estado del minijuego
self.is_complete: bool      # True cuando el minijuego termina
self.success: bool          # True si el jugador ganó
self.score: int             # Puntuación obtenida
self.time_remaining: float  # Tiempo restante

# Recompensas
self.reward_materials: int  # Materiales a otorgar
self.reward_repair: int     # Progreso de reparación a otorgar

# Dimensiones
self.screen_width: int
self.screen_height: int

# Fuentes predefinidas
self.font_large: pygame.font.Font   # 48px
self.font_normal: pygame.font.Font  # 32px
self.font_small: pygame.font.Font   # 24px

# Superficie de renderizado
self.surface: pygame.Surface
```

### Sistema de Tutorial

Los primeros 2 intentos de cada acción muestran minijuegos específicos:

**Minería** (obtener materiales):
- Intento 1: `MiningMinigame` (Mineral Rush)
- Intento 2: `AsteroidShooterMinigame`
- Intento 3+: Aleatorio entre los dos

**Reparación** (progreso de reparación):
- Intento 1: `TimingMinigame` (Timing Precision)
- Intento 2: `WiringMinigame` (Wiring Puzzle)
- Intento 3+: Aleatorio entre los dos

**Implementación** (en `engine/loop.py`):
```python
# Contadores de intentos
self.mining_attempts = 0
self.repair_attempts = 0

# En start_mining_minigame():
if self.mining_attempts == 0:
    minigame = MiningMinigame(...)  # Primer intento
elif self.mining_attempts == 1:
    minigame = AsteroidShooterMinigame(...)  # Segundo intento
else:
    minigame = random.choice([MiningMinigame, AsteroidShooterMinigame])(...)
```

## 🚀 Optimización

### Antes de optimizar:
1. ¿El juego funciona correctamente?
2. ¿Hay problemas de rendimiento reales?
3. ¿Has perfilado el código? (`python -m cProfile`)

### Áreas comunes de optimización:
- Cache de superficies renderizadas en Pygame
- Limitar llamadas a `render()` solo cuando cambia el estado
- Usar dirty rect rendering
- Pool de objetos para partículas/efectos

## 📝 Documentación de Decisiones

Cuando tomes decisiones importantes de diseño, documéntalas:

```python
# DECISIÓN DE DISEÑO: Usamos interés compuesto para Zorvax porque...
# - Es más realista para bancos
# - Crea una curva de dificultad interesante
# - Enseña al jugador sobre interés compuesto
def calculate_interest(self) -> float:
    ...
```

## 🔄 Git Workflow

```bash
# Crear rama para feature
git checkout -b feature/implement-debt-system

# Commits atómicos
git add finance/debt.py
git commit -m "Implement interest calculation for Zorvax debt"

git add tests/test_finance.py
git commit -m "Add tests for Zorvax interest calculation"

# Merge a main cuando esté completo y probado
git checkout main
git merge feature/implement-debt-system
```

## 📚 Recursos Útiles

- [Pygame Documentation](https://www.pygame.org/docs/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Game Programming Patterns](https://gameprogrammingpatterns.com/)

## 🆘 Problemas Comunes

### Pygame no se instala
```bash
# Windows: Instalar Visual C++ Build Tools
# Linux: sudo apt-get install python3-dev
```

### Import errors entre módulos
```python
# Usa imports absolutos desde la raíz
from engine.state import GameState
# No uses imports relativos como: from ..engine.state import GameState
```

### EventManager no funciona
- Verifica que los callbacks están correctamente suscritos
- Asegúrate de llamar `process_queue()` si usas cola
- Revisa el historial de eventos para debugging

## 🔍 Debugging y Herramientas

### Logging

El proyecto usa el módulo `logging` de Python. Niveles configurados:

```python
import logging
logger = logging.getLogger(__name__)

# Niveles disponibles:
logger.debug("Información detallada para debugging")
logger.info("Información general del flujo")
logger.warning("Advertencias no críticas")
logger.error("Errores que no detienen el juego")
logger.critical("Errores críticos")
```

**Configuración** (en `main.py`):
```python
logging.basicConfig(
    level=logging.INFO,  # Cambiar a DEBUG para más detalle
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Historial de Eventos

El `EventManager` mantiene un historial de eventos para debugging:

```python
# Ver todos los eventos recientes
history = event_manager.get_history()
for event in history:
    print(f"{event.event_type.name}: {event.data}")

# Filtrar por tipo específico
oxygen_events = event_manager.get_history(EventType.OXYGEN_CHANGED)
```

### Estado del Juego

Serializar el estado para inspección:

```python
state_dict = game_state.save_state()
import json
print(json.dumps(state_dict, indent=2))
```

### Modo Testing

**Testing de Victoria** (en `main.py`):
```python
TEST_VICTORY_ANIMATION = True  # Activar para probar pantalla de victoria
```

**Testing de Minijuegos** (usar `test_minigames.py`):
```bash
python test_minigames.py
```

### Herramientas Útiles

- **Pygame Inspector**: Inspeccionar superficies y rects
- **cProfile**: Perfilar rendimiento
  ```bash
  python -m cProfile -o profile.stats main.py
  python -m pstats profile.stats
  ```
- **pytest**: Ejecutar pruebas unitarias
  ```bash
  pytest tests/ -v
  pytest tests/test_finance.py --cov=finance
  ```

## 📊 Balanceo del Juego

### Valores Clave (ajustables en `data/config.json`)

```json
{
  "gameplay": {
    "initial_oxygen": 100.0,
    "oxygen_consumption_per_turn": 1.0,
    "victory_repair_threshold": 100.0,
    "max_active_loans": 3
  }
}
```

### Costos Actuales (hardcoded en `engine/state.py` y `engine/loop.py`)

- **Minar materiales**: 12-15 oxígeno (aleatorio)
- **Reparar nave**: 12-15 oxígeno + 5-10 materiales (aleatorio)
- **Intercambio**: 1 material = 5 oxígeno (fijo)

### Recompensas de Minijuegos

- **Mineral Rush**: Hasta 7 materiales
- **Asteroid Shooter**: Variable según asteroides destruidos
- **Timing Precision**: 10-20 progreso de reparación
- **Wiring Puzzle**: 15-25 progreso de reparación
- **Oxygen Rescue**: +10 oxígeno (victoria)

### Ajustar Dificultad

**Hacer más fácil**:
- Reducir costos de oxígeno
- Aumentar recompensas de minijuegos
- Reducir tasas de interés
- Aumentar tiempo de minijuegos

**Hacer más difícil**:
- Aumentar costos de oxígeno
- Reducir recompensas de minijuegos
- Aumentar tasas de interés
- Reducir tiempo de minijuegos

## 🤝 Patrones de Diseño Utilizados

### Observer Pattern (EventManager)
Comunicación desacoplada entre módulos mediante eventos.

```python
# Suscribirse
event_manager.subscribe(EventType.OXYGEN_CHANGED, self.on_oxygen_changed)

# Emitir
event_manager.emit_quick(EventType.OXYGEN_CHANGED, {'amount': 10})
```

### Dependency Injection
Referencias asignadas después de la creación para evitar dependencias circulares.

```python
game_state.loan_manager = loan_manager
loan_manager.game_state = game_state
```

### State Pattern (GameState)
Estado centralizado para facilitar save/load y debugging.

### Strategy Pattern (Debt classes)
Diferentes estrategias de cálculo de interés según tipo de acreedor.

### Template Method (BaseMinigame)
Estructura común para todos los minijuegos con métodos abstractos.

## 📚 Recursos de Referencia

### Documentación del Proyecto
- **ARCHITECTURE.md**: Arquitectura detallada del sistema
- **GAME_README.md**: Guía del jugador
- **QUICKSTART.md**: Inicio rápido
- **COMO_EJECUTAR.md**: Instrucciones de ejecución
- **DOCKER_WINDOWS_GUI.md**: Configuración de Docker con GUI

### Documentación Externa
- [Pygame Documentation](https://www.pygame.org/docs/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [Game Programming Patterns](https://gameprogrammingpatterns.com/)

## 🆘 Problemas Comunes y Soluciones

### Pygame no se instala
```bash
# Windows: Instalar Visual C++ Build Tools
# Linux: sudo apt-get install python3-dev
# Mac: brew install sdl sdl_image sdl_mixer sdl_ttf portmidi
```

### Import errors entre módulos
```python
# ✅ Correcto: Imports absolutos desde la raíz
from engine.state import GameState
from gameplay.minigames.mining import MiningMinigame

# ❌ Incorrecto: Imports relativos
from ..engine.state import GameState
```

### EventManager no funciona
- Verifica que los callbacks están correctamente suscritos
- Asegúrate de llamar `process_queue()` si usas cola
- Revisa el historial de eventos para debugging
- Verifica que el `event_type` coincide exactamente

### Minijuego no aparece
- Verifica que está importado en `gameplay/minigames/__init__.py`
- Verifica que está registrado en `engine/loop.py`
- Revisa logs para errores de carga de assets
- Verifica que la fase cambió a "minigame"

### HUD no responde durante minijuego
- **Comportamiento esperado**: El HUD se bloquea durante minijuegos
- Verifica `game_state.current_phase == "minigame"`
- El input debe ser manejado por el minijuego, no el HUD

### Prestamista no aparece
- Verifica `game_state.oxygen < 90`
- Verifica `game_state.prestamista_shown == False`
- Revisa logs de `engine/loop.py` → `_check_lender_appearance()`

### Evento de oxígeno no se activa
- Verifica `game_state.oxygen < 80`
- Verifica `oxygen_event_shown == False` en `engine/loop.py`
- Asegúrate de que no hay prestamista visible (se oculta automáticamente)

## ✅ Estado Actual del Proyecto

### Módulos Completamente Implementados ✅

- ✅ **engine/**: events.py, state.py, loop.py
- ✅ **finance/**: debt.py, loan_manager.py
- ✅ **gameplay/**: resources.py, repair.py
- ✅ **gameplay/minigames/**: base.py, mining.py, asteroid_shooter.py, timing.py, wiring.py, oxygen_rescue.py
- ✅ **ui/**: renderer.py, hud.py, narrator.py
- ✅ **main.py**: Inicialización y bucle principal
- ✅ **data/**: config.json, localization.json, assets/

### Características Implementadas ✅

- ✅ Sistema de eventos (Observer pattern)
- ✅ Gestión de estado global
- ✅ Bucle principal con fases
- ✅ 5 minijuegos funcionales (+ 1 placeholder)
- ✅ Sistema de préstamos con 4 tipos de acreedores
- ✅ Sistema de reparación
- ✅ HUD completo con paneles informativos
- ✅ Sistema de intercambio de materiales por oxígeno
- ✅ Eventos especiales (prestamista, rescate del marciano)
- ✅ Sistema narrativo con diálogos
- ✅ Renderizado con efectos visuales
- ✅ Tutorial integrado (primeros 2 intentos guiados)
- ✅ Pantalla de victoria/derrota
- ✅ Pruebas unitarias para módulos core

### Pendientes / Mejoras Futuras ⚠️

- ⚠️ **dodge.py**: Minijuego no implementado (placeholder)
- 💡 Sistema de sonido y música
- 💡 Más tipos de acreedores (Consorcio Nebulosa completo)
- 💡 Animaciones adicionales
- 💡 Sistema de logros/achievements
- 💡 Guardar/cargar partidas
- 💡 Dificultad ajustable
- 💡 Más eventos especiales

## 🎉 Conclusión

Este proyecto está **completamente funcional** y listo para jugar. La arquitectura está diseñada para ser:

- **Modular**: Fácil añadir nuevos minijuegos, acreedores, eventos
- **Mantenible**: Código organizado, bien documentado, con pruebas
- **Extensible**: Patrones de diseño facilitan nuevas características
- **Educativo**: Enseña conceptos de finanzas de forma interactiva

Para añadir nuevas características, sigue los checklists y patrones establecidos en esta guía. ¡Buena suerte! 🚀

---

**Última actualización**: Octubre 2025 - Refleja el estado completo del proyecto AstroDebt.

