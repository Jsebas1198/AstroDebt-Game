# 🔧 Guía de Desarrollo - AstroDebt

Esta guía te ayudará a comenzar a implementar la lógica del juego siguiendo la estructura de esqueleto.

## 📋 Orden Sugerido de Implementación

### Fase 1: Fundamentos (Engine)
1. **engine/events.py** - Sistema de eventos
   - Implementar subscribe/unsubscribe
   - Implementar emit y queue_event
   - Probar con eventos simples

2. **engine/state.py** - Estado del juego
   - Implementar update_oxygen
   - Implementar add_material/consume_material
   - Implementar save/load state

3. **engine/loop.py** - Bucle principal
   - Implementar handle_events
   - Implementar update
   - Implementar render

### Fase 2: Finanzas
4. **finance/debt.py** - Sistema de deudas
   - Implementar calculate_interest para cada tipo
   - Implementar apply_penalty
   - Implementar make_payment
   - **Probar con tests/test_finance.py**

5. **finance/loan_manager.py** - Gestor de préstamos
   - Implementar offer_loan
   - Implementar accept_loan
   - Implementar process_turn
   - **Probar con tests/test_finance.py**

### Fase 3: Gameplay
6. **gameplay/resources.py** - Gestión de recursos
   - Implementar collect_resource
   - Implementar consume_resource
   - Implementar has_resources
   - **Probar con tests/test_resources.py**

7. **gameplay/repair.py** - Sistema de reparación
   - Implementar start_repair
   - Implementar complete_repair_step
   - Implementar can_launch_ship
   - **Probar con tests/test_repair.py**

8. **gameplay/minigames/** - Minijuegos
   - Empezar con mining.py (el más simple)
   - Luego timing.py
   - Después dodge.py
   - Finalmente wiring.py (el más complejo)

### Fase 4: Interfaz
9. **ui/renderer.py** - Renderizado
   - Implementar render_background
   - Implementar render_ship
   - Implementar render_effects

10. **ui/hud.py** - HUD
    - Implementar render_oxygen_bar
    - Implementar render_resource_summary
    - Implementar render_debt_summary

11. **ui/narrator.py** - Narrativa
    - Implementar show_dialogue
    - Implementar efecto de escritura
    - Implementar opciones de diálogo

### Fase 5: Integración
12. **main.py** - Punto de entrada
    - Conectar todos los sistemas
    - Implementar bucle principal
    - Cargar configuración

## 🎯 Checklist de Cada Módulo

Al implementar cada módulo, asegúrate de:

- [ ] Eliminar todos los `pass` e implementar lógica
- [ ] Añadir docstrings completos si faltan
- [ ] Implementar manejo de errores
- [ ] Escribir/actualizar pruebas unitarias
- [ ] Probar con pytest
- [ ] Documentar decisiones de diseño complejas
- [ ] Verificar integración con otros módulos

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

## 🎮 Minijuegos - Estructura Común

Todos los minijuegos siguen este patrón:

```python
class MinigameTemplate:
    def __init__(self, difficulty: int):
        self.difficulty = difficulty
        self.is_active = False
        self.is_complete = False
        
    def start(self):
        # Inicializar estado
        self.is_active = True
        
    def update(self, delta_time: float):
        # Actualizar lógica del juego
        pass
        
    def handle_input(self, event: pygame.event.Event):
        # Procesar input del jugador
        pass
        
    def render(self, screen: pygame.Surface):
        # Dibujar el minijuego
        pass
        
    def complete(self) -> RewardType:
        # Finalizar y retornar recompensas
        self.is_complete = True
        return rewards
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

## ✅ Definición de "Completo"

Un módulo está completo cuando:
1. ✅ Toda la lógica está implementada (no hay `pass`)
2. ✅ Las pruebas unitarias pasan
3. ✅ La cobertura de tests es > 80%
4. ✅ No hay errores de linter (pylint, mypy)
5. ✅ Está integrado y funciona con otros módulos
6. ✅ Está documentado

## 🎉 ¡Empecemos!

Comienza con `engine/events.py` - es el fundamento sobre el que todo lo demás se construye. ¡Buena suerte!

