# 🚀 NAVE VARADA - Juego Educativo sobre Gestión Financiera

## 📖 Descripción

**Nave Varada** es un juego educativo que enseña conceptos de gestión financiera, préstamos y priorización de recursos a través de mecánicas gamificadas. El jugador debe reparar su nave espacial varada mientras gestiona préstamos de oxígeno y recursos.

### Concepto Educativo Central
- **Oxígeno = Dinero** (moneda del juego)
- **Materiales = Trabajo** (lo que produces con esfuerzo)
- **Préstamos se piden en oxígeno, se pagan en materiales**

## 🎮 Cómo Jugar

### Objetivo
Reparar tu nave al 100% antes de quedarte sin oxígeno.

### Controles
- **[M]** - Minar materiales (costo: 2 oxígeno)
- **[R]** - Reparar nave (costo: 3 oxígeno + 5-10 materiales)
- **[I]** - Ver inventario
- **[D]** - Ver deudas
- **[P]** - Ver progreso de reparación
- **[ESPACIO]** - Avanzar diálogos
- **[A]/[R]** - Aceptar/Rechazar préstamos
- **[ESC]** - Cerrar paneles / Saltar diálogos

### Mecánicas Principales

#### 1. Sistema de Recursos
- **Oxígeno**: Tu "dinero" - se consume con cada acción
- **Materiales**: Recursos obtenidos minando, usados para reparar y pagar préstamos

#### 2. Sistema de Préstamos
Los prestamistas aparecen según tu nivel de oxígeno:
- **< 20% oxígeno**: Aparición obligatoria
- **20-50% oxígeno**: 50% probabilidad
- **> 50% oxígeno**: 20% probabilidad

#### 3. Prestamistas Disponibles

| Prestamista | Interés | Conversión | Penalización por impago |
|------------|---------|------------|------------------------|
| **Zorvax** | 50% | 1 oxígeno → 1.5 materiales | Roba materiales adicionales |
| **K'tarr** | 20% | 1 oxígeno → 1.2 materiales | Reduce oxígeno máximo |

#### 4. Estrategia
- Balancea entre minar materiales y reparar la nave
- Los préstamos dan oxígeno inmediato pero requieren más trabajo (materiales) para pagar
- Prioriza pagar deudas antes de que venzan

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.7+
- Pygame

### Instalación
```bash
# Clonar o descargar el proyecto
cd nave_varada

# Instalar dependencias
pip install pygame
```

### Ejecutar el Juego
```bash
python main.py
# o
python test_game.py
```

## 📁 Estructura del Proyecto

```
nave_varada/
├── main.py                 # Punto de entrada principal
├── engine/                 # Motor del juego
│   ├── state.py           # Estado del juego (GameState)
│   ├── events.py          # Sistema de eventos
│   └── loop.py            # Bucle principal
├── gameplay/              # Mecánicas de juego
│   ├── resources.py       # Gestión de materiales
│   ├── repair.py          # Sistema de reparación
│   └── minigames/         # Minijuegos (pendiente)
├── finance/               # Sistema financiero
│   ├── debt.py            # Clases de deuda
│   └── loan_manager.py    # Gestión de préstamos
├── ui/                    # Interfaz de usuario
│   ├── hud.py            # HUD principal
│   ├── renderer.py       # Renderizado
│   └── narrator.py       # Sistema de diálogos
└── data/                  # Datos y assets
    ├── config.json        # Configuración
    └── assets/           # Imágenes del juego
```

## 🎯 Estado de Implementación

### ✅ Completado
- Sistema de estado del juego (GameState)
- Sistema de eventos (EventManager)
- Bucle principal con fases
- Gestión simplificada de recursos (un tipo de material)
- HUD con barras de oxígeno, materiales y reparación
- Renderer con assets visuales
- Sistema de préstamos con Zorvax y K'tarr
- Sistema de reparación simplificado
- Narrator para diálogos educativos

### 🚧 Pendiente (Próximas mejoras)
- Minijuegos interactivos (Mining, Timing, Wiring)
- Más prestamistas (Consorcio Nebulosa, Aliado)
- Sistema de sonido
- Guardado/Carga de partidas
- Pantalla de estadísticas finales
- Tutorial interactivo

## 🎓 Valor Educativo

El juego enseña:
1. **Gestión de recursos**: Priorizar entre necesidades inmediatas y objetivos a largo plazo
2. **Concepto de préstamos**: El dinero prestado debe devolverse con "trabajo" extra
3. **Intereses**: Diferentes prestamistas tienen diferentes costos
4. **Consecuencias**: No pagar a tiempo tiene penalizaciones
5. **Planificación**: Necesidad de estrategia para ganar

## 🐛 Solución de Problemas

### El juego no inicia
- Verifica que Python 3.7+ esté instalado
- Instala pygame: `pip install pygame`
- Verifica que los archivos de assets estén en `data/assets/`

### La ventana se cierra inmediatamente
- Ejecuta desde terminal para ver mensajes de error
- Verifica que `config.json` esté presente y válido

### Los assets no se cargan
- El juego funciona sin assets pero se ve mejor con ellos
- Verifica que los archivos .png estén en `data/assets/`

## 📝 Notas de Desarrollo

### Simplificaciones MVP
- Un solo tipo de material genérico (en lugar de múltiples)
- Sistema de turnos basado en acciones (sin timers)
- Préstamos en oxígeno, pagos en materiales
- Progreso de reparación único (sin componentes individuales)

### Arquitectura
- Patrón Observer para eventos
- Referencias cruzadas entre managers
- Estado centralizado en GameState
- Renderizado por capas

## 🤝 Créditos

Desarrollado como juego educativo para enseñar conceptos financieros básicos a través de mecánicas de juego intuitivas.

---

**¡Disfruta el juego y aprende sobre gestión financiera!** 🚀💰
