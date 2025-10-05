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
                  │ Asteroid     │
                  │ Wiring       │
                  │ Timing       │
                  │ OxygenRescue │
                  └──────────────┘
```

## 🎮 Controles del Juego

### Juego Principal (main_game)
```
[M] - Minar materiales (Costo: 12-15 oxígeno)
[R] - Reparar nave (Costo: 12-15 oxígeno + 5-10 materiales)
[O] - Conseguir oxígeno (Abrir modal de intercambio)
[I] - Ver inventario y recursos
[D] - Ver deudas activas
[P] - Ver progreso de reparación
[ESC] - Cerrar paneles abiertos
[SPACE] - Continuar diálogos / Aceptar prestamista
[Y] - Aceptar evento de oxígeno
[N] - Rechazar evento de oxígeno
```

### Modal de Intercambio
```
[←] / [→] - Ajustar cantidad de materiales
[ENTER] - Confirmar intercambio
[ESC] - Cancelar y cerrar modal
Mouse - Arrastrar slider para seleccionar cantidad
```

### Minijuego: Mineral Rush
```
Mouse Click - Hacer clic en minerales
```

### Minijuego: Asteroid Shooter
```
[W][A][S][D] - Mover nave
Mouse - Apuntar
Click - Disparar
```

### Minijuego: Timing Precision
```
[SPACE] - Presionar en zona verde
```

### Minijuego: Wiring Puzzle
```
Mouse Click - Seleccionar y conectar cables
```

### Minijuego: Rescate del Marciano
```
[W][A][S][D] - Mover jugador
Mouse - Apuntar dirección
Click Izquierdo - Disparar
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
  │     ├─> Delegar según fase actual:
  │     │   ├─> "intro": Narrador (historia inicial)
  │     │   ├─> "main_game": HUD y acciones principales
  │     │   ├─> "minigame": Minijuego activo
  │     │   └─> "end": Pantalla final
  │     └─> Gestionar prioridades de input
  │
  ├─> update(delta_time)
  │     ├─> Actualizar según fase:
  │     │   ├─> "intro": Esperar continuación
  │     │   ├─> "main_game": 
  │     │   │   ├─> Actualizar GameState
  │     │   │   ├─> Verificar evento oxígeno (< 80%)
  │     │   │   ├─> Verificar prestamista (< 90%)
  │     │   │   └─> Verificar game over
  │     │   ├─> "minigame": Actualizar minijuego activo
  │     │   └─> "end": Mostrar resultado final
  │     ├─> Actualizar HUD (notificaciones, animaciones)
  │     └─> Procesar cola de eventos
  │
  └─> render()
        ├─> Renderer.render_frame() (fondo, nave, efectos)
        ├─> Minigame.render() (si fase == "minigame")
        ├─> HUD.render() (barras, paneles, modal)
        ├─> Narrator.render() (si hay diálogo activo)
        └─> Renderer.render_lender() (si prestamista visible)
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
  - **base.py**: Clase base abstracta para todos los minijuegos
  - **mining.py**: Mineral Rush - Whack-a-Mole con minerales (Cobre, Plata, Oro)
  - **asteroid_shooter.py**: Shooter espacial - Destruir asteroides
  - **timing.py**: Timing Precision - Calibración rítmica con barras
  - **wiring.py**: Wiring Puzzle - Conectar cables correctamente
  - **oxygen_rescue.py**: Rescate del Marciano - Combate top-down para obtener oxígeno
  - **dodge.py**: Placeholder (no implementado aún)

### UI (Interfaz de Usuario)
- **renderer.py**: Renderizado visual
  - Fondo y ambiente espacial
  - Nave y efectos
  - Gestión de capas

- **hud.py**: Heads-Up Display
  - Barras de recursos (oxígeno, materiales, reparación)
  - Inventario y paneles informativos
  - Información de deudas activas
  - Notificaciones flotantes
  - **Sistema de intercambio**: Modal para vender materiales por oxígeno (2 materiales = 1 oxígeno)
  - Botón visual de "Conseguir Oxígeno" con validaciones inteligentes

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
Eventos de Estado:
  GameState ──OXYGEN_CHANGED──────────> EventManager ──> HUD
  GameState ──MATERIALS_GAINED────────> EventManager ──> HUD
  GameState ──MATERIALS_CONSUMED──────> EventManager ──> HUD
  GameState ──REPAIR_PROGRESS_CHANGED─> EventManager ──> HUD

Eventos de Minijuegos:
  GameLoop ──MINIGAME_STARTED─────────> EventManager ──> HUD
  GameLoop ──MINIGAME_COMPLETED───────> EventManager ──> HUD
  Minigame ──MATERIALS_GAINED_SUCCESS─> EventManager ──> GameState

Eventos de Préstamos:
  LoanManager ──LOAN_APPEARED─────────> EventManager ──> Renderer
  LoanManager ──LOAN_ACCEPTED─────────> EventManager ──> GameState
  LoanManager ──PENALTY_APPLIED───────> EventManager ──> HUD

Eventos de Juego:
  GameLoop ──PHASE_CHANGED────────────> EventManager ──> Todos
  GameLoop ──GAME_OVER────────────────> EventManager ──> Renderer
  GameLoop ──VICTORY──────────────────> EventManager ──> Renderer

Eventos de UI:
  Narrator ──DIALOGUE_STARTED─────────> EventManager ──> GameLoop
  HUD ──NOTIFICATION_SHOWN────────────> EventManager ──> (log)
  HUD ──ALERT_OXYGEN──────────────────> EventManager ──> Renderer
```

## 🚦 Fases del Juego

```
INICIO (intro)
  │
  ▼
JUEGO PRINCIPAL (main_game) ◄─┐
  │                            │
  ├─> [M] Minar materiales ────┼─> MINIJUEGO (minigame)
  │   (Costo: 12-15 oxígeno)   │   - Mineral Rush
  │                            │   - Asteroid Shooter
  │                            │
  ├─> [R] Reparar nave ────────┼─> MINIJUEGO (minigame)
  │   (Costo: 12-15 ox + 5-10 mat) - Timing Precision
  │                            │   - Wiring Puzzle
  │                            │
  ├─> [O] Conseguir oxígeno ───┼─> MODAL INTERCAMBIO
  │   (2 materiales = 1 oxígeno)   (No consume turno)
  │                            │
  ├─> Ver inventario [I]       │
  ├─> Ver deudas [D]           │
  ├─> Ver reparación [P]       │
  │                            │
  └─> Fin de minijuego ────────┘
      │
      ├─> Aplicar recompensas
      ├─> Verificar evento oxígeno (< 80%)
      ├─> Verificar prestamista (< 90%, solo una vez)
      ├─> Verificar game over
      │
      └───────┘

EVENTO ESPECIAL (oxygen < 80%):
  └─> Rescate del Marciano (combate)
      - Victoria: +10 oxígeno
      - Derrota: Sin recompensa

VICTORIA (end): Reparación al 100%
DERROTA (end): Oxígeno agotado
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
   └─> GameLoop.start_mining_minigame() o start_repair_minigame()
       ├─> Verificar recursos suficientes
       ├─> Consumir oxígeno (12-15 aleatorio)
       ├─> Consumir materiales si es reparación (5-10 aleatorio)
       ├─> Cerrar paneles del HUD
       ├─> Cambiar fase a "minigame"
       └─> Crear instancia del minijuego (aleatorio o tutorial)

2. Bucle del minijuego (fase "minigame")
   ├─> handle_input() - Solo procesa eventos del minijuego
   ├─> update(dt) - Actualiza lógica del minijuego
   └─> render() - Dibuja el minijuego

3. Finalizar minijuego
   └─> GameLoop._complete_minigame()
       ├─> Obtener resultados (reward_materials, reward_repair, reward_oxygen)
       ├─> Aplicar recompensas al GameState
       ├─> Mostrar notificaciones en HUD
       ├─> Emitir eventos correspondientes
       ├─> Cambiar fase a "main_game"
       └─> Verificar aparición de prestamista (excepto Oxygen Rescue)
```

### Flujo de Evento Especial: Rescate del Marciano
```
1. Trigger automático
   └─> GameLoop.update()
       ├─> Verificar: oxygen < 80 AND !oxygen_event_shown
       ├─> Marcar oxygen_event_shown = True
       ├─> Ocultar prestamista si está visible
       └─> Mostrar narrativa con opciones [Y/N]

2. Jugador decide
   ├─> [Y] Aceptar misión
   │   └─> GameLoop.start_oxygen_rescue_minigame()
   │       ├─> Cerrar paneles del HUD
   │       ├─> Cambiar fase a "minigame"
   │       └─> Crear OxygenRescueMinigame
   │
   └─> [N] Rechazar misión
       └─> Cerrar narrador y continuar

3. Minijuego de combate
   ├─> Jugador vs 5 enemigos
   ├─> Victoria: Todos los enemigos derrotados
   └─> Derrota: Vida del jugador llega a 0

4. Recompensa
   ├─> Victoria: +10 oxígeno
   ├─> Derrota: Sin recompensa
   └─> NO verifica prestamista después (is_oxygen_rescue = True)
```

### Flujo de Intercambio de Materiales
```
1. Abrir modal
   └─> Jugador presiona [O] o hace clic en botón
       ├─> Verificar: oxygen < 100 AND materials > 0
       ├─> Calcular max_materials_to_sell
       └─> Mostrar modal con slider

2. Seleccionar cantidad
   ├─> Slider (mouse drag)
   ├─> Flechas ←/→ (teclado)
   └─> Actualización en tiempo real del oxígeno a recibir

3. Confirmar intercambio
   └─> HUD.confirm_exchange()
       ├─> Validar: oxygen < 100
       ├─> Ajustar cantidad si es impar (redondear hacia abajo)
       ├─> Calcular: oxygen_gained = materials // 2
       ├─> Verificar límite de 100 (ajustar si excede)
       ├─> Consumir materiales
       ├─> Añadir oxígeno
       ├─> Mostrar notificación
       └─> Cerrar modal
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
1. Crear archivo en `gameplay/minigames/` (ej: `nuevo_minijuego.py`)
2. Heredar de `BaseMinigame` e implementar métodos abstractos:
   - `load_assets()`: Cargar imágenes y sonidos
   - `handle_input(event)`: Procesar input del jugador
   - `update(delta_time)`: Actualizar lógica del juego
   - `render(screen)`: Dibujar en pantalla
3. Exportar en `gameplay/minigames/__init__.py`
4. Registrar en `engine/loop.py` (métodos `start_mining_minigame` o `start_repair_minigame`)
5. Añadir assets necesarios en `data/assets/`
6. Configurar recompensas en método `get_results()`

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

## 💱 Sistema de Intercambio de Recursos

### Venta de Materiales por Oxígeno
El jugador puede intercambiar materiales por oxígeno directamente desde el HUD:

```
Tasa de cambio: 2 materiales = 1 oxígeno

Restricciones:
- Solo se puede vender en pares de materiales
- No se puede exceder 100 de oxígeno
- El slider se ajusta automáticamente al máximo vendible
- Botón visual con estados (habilitado/deshabilitado)
```

**Flujo de intercambio:**
1. Jugador presiona `[O]` o hace clic en botón "🪙 Conseguir Oxígeno"
2. Se abre modal con slider interactivo
3. Jugador selecciona cantidad (teclado ←/→ o mouse)
4. Sistema calcula oxígeno a recibir en tiempo real
5. Confirma con ENTER o botón verde
6. Materiales se consumen, oxígeno se añade

**Validaciones inteligentes:**
- Máximo vendible = `min(materiales_disponibles, (100 - oxígeno_actual) * 2)`
- Ajuste automático si la cantidad excedería 100
- Redondeo hacia abajo si se selecciona cantidad impar

## 🎮 Minijuegos Detallados

### Minijuegos de Minería (Obtener Materiales)
El sistema alterna entre dos minijuegos:

**1. Mineral Rush (mining.py)**
- Tipo: Whack-a-Mole con minerales
- Duración: 10 segundos
- Objetivo: Hacer clic en minerales antes de que desaparezcan
- Minerales: Cobre (0.05), Plata (0.1), Oro (0.2)
- Sistema de combos: ×2, ×3, ×5
- Máximo: 7 materiales por partida

**2. Asteroid Shooter (asteroid_shooter.py)**
- Tipo: Shooter espacial
- Duración: 30 segundos
- Objetivo: Destruir asteroides
- Recompensa: Materiales según asteroides destruidos

### Minijuegos de Reparación
El sistema alterna entre dos minijuegos:

**1. Timing Precision (timing.py)**
- Tipo: Calibración rítmica
- Objetivo: Presionar ESPACIO cuando el indicador esté en zona verde
- 3 barras consecutivas para ganar
- Velocidad aumenta con cada barra

**2. Wiring Puzzle (wiring.py)**
- Tipo: Puzzle de conexiones
- Objetivo: Conectar cables correctamente
- Requiere lógica y planificación

### Evento Especial: Rescate del Marciano (oxygen_rescue.py)
**Trigger:** Oxígeno < 80% (solo una vez por sesión)

**Mecánica:**
- Tipo: Shooter top-down con combate
- Jugador: Control WASD + disparo con mouse
- Enemigos: 5 enemigos (seal_left.png, seal_right.png)
  - 2 desde la izquierda
  - 2 desde la derecha
  - 1 desde arriba (aleatorio)
- Vida jugador: 5 impactos
- Vida enemigos: 3 impactos cada uno
- Disparos: Jugador (naranja), Enemigos (azul)

**Recompensa:**
- Victoria: +10 oxígeno
- Derrota: Sin recompensa

**Características:**
- Flecha indicadora de dirección de disparo
- Barras de vida visibles
- Sin límite de tiempo (termina al ganar o perder)
- No aparece prestamista después de este minijuego

## 📊 Métricas y Balanceo

Variables clave para balanceo del juego:
- **Consumo de oxígeno por acción**: 12-15 (aleatorio) para Minar y Reparar
- Tasas de interés de cada acreedor
- Recursos requeridos por componente: 5-10 materiales (aleatorio)
- Dificultad y recompensas de minijuegos
- Límites de almacenamiento de recursos
- **Tasa de intercambio**: 2 materiales = 1 oxígeno (fijo)

Todas ajustables en `data/config.json` sin cambiar código.

## 🆕 Mejoras y Características Recientes

### Sistema de Tutorial Integrado
Los primeros 2 intentos de cada tipo de acción muestran minijuegos específicos en orden:
- **Minería**: Intento 1 → Mineral Rush, Intento 2 → Asteroid Shooter, Intento 3+ → Aleatorio
- **Reparación**: Intento 1 → Timing Precision, Intento 2 → Wiring Puzzle, Intento 3+ → Aleatorio

### Gestión Inteligente de Input
- **Prioridades de eventos**: Evento oxígeno > Prestamista > Acciones normales
- **Bloqueo de HUD durante minijuegos**: Paneles no se pueden abrir, teclas deshabilitadas
- **Cierre automático de paneles**: Al entrar a minijuegos, todos los paneles se cierran
- **Narrador no interfiere**: Si hay prestamista o evento de oxígeno activo, el narrador no captura SPACE

### Validaciones y UX Mejorada
- **Intercambio de materiales**: Slider limitado al máximo vendible, ajuste automático de cantidades
- **Botón visual con estados**: Verde (habilitado), Gris (deshabilitado con razón)
- **Notificaciones contextuales**: Mensajes claros de éxito, error e información
- **Prevención de bugs**: No se puede exceder 100 de oxígeno, no se venden materiales de más

### Eventos Especiales
- **Prestamista educativo** (oxígeno < 90%): Aparece una vez para enseñar sobre préstamos
- **Rescate del Marciano** (oxígeno < 80%): Evento de combate único para obtener oxígeno extra
- **Ambos eventos son opcionales**: El jugador puede rechazarlos

### Optimizaciones de Rendimiento
- **Renderizado por capas**: Background, Game, Effects, UI separados
- **Actualización selectiva**: Solo se actualiza lo necesario según la fase
- **Gestión de memoria**: Assets cargados una vez, reutilizados

---

**Nota**: Esta arquitectura prioriza:
- ✅ Desacoplamiento (via EventManager)
- ✅ Mantenibilidad (código organizado en módulos claros)
- ✅ Testabilidad (lógica separada de presentación)
- ✅ Escalabilidad (fácil añadir nuevos contenidos)
- ✅ Experiencia de usuario (validaciones inteligentes, feedback claro)
- ✅ Balanceo dinámico (costos aleatorios, dificultad progresiva)

**Última actualización**: Octubre 2025 - Incluye sistema de intercambio, evento de rescate del marciano, y mejoras de UX.

