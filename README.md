# 🚀 AstroDebt - Nave Varada

Un juego educativo sobre finanzas personales ambientado en el espacio. Tu nave espacial está varada y debes repararla mientras gestionas préstamos de diferentes acreedores alienígenas, cada uno con sus propias condiciones y consecuencias.

## 📖 Concepto del Juego

Estás varado en un cinturón de asteroides con tu nave dañada. Necesitas recursos para repararla antes de que se agote el oxígeno. Los acreedores galácticos están dispuestos a prestarte, pero cada uno tiene sus propias reglas:

- **Banco Zorvax**: Interés compuesto razonable, penalizaciones moderadas
- **Prestamistas K'tar**: Interés alto, penalizaciones severas e inmediatas
- **Consorcio Nebulosa**: Interés inicial bajo que crece exponencialmente con retrasos
- **Aliado**: Préstamo sin interés (solo disponible una vez)

### 🎯 Objetivos Educativos

- Comprender diferentes tipos de interés (simple, compuesto, exponencial)
- Aprender sobre consecuencias de deudas impagadas
- Desarrollar habilidades de gestión de recursos
- Practicar toma de decisiones financieras bajo presión

## 🏗️ Estructura del Proyecto

```
nave_varada/
├── engine/          # Motor del juego (estado, bucle, eventos)
├── finance/         # Sistema financiero (deudas, préstamos)
├── gameplay/        # Lógica de juego (recursos, reparación, minijuegos)
├── ui/              # Interfaz de usuario
├── data/            # Configuración y assets
├── tests/           # Pruebas unitarias
└── main.py          # Punto de entrada
```

## 🛠️ Requisitos

- Python 3.13.7
- Pygame 2.6.1
- Docker (opcional para desarrollo)

## 🚀 Instalación y Ejecución

### Sin Docker

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el juego
python main.py
```

### Con Docker

```bash
# Construir imagen
docker build -t astrodebt .

# Ejecutar contenedor
docker run -it --rm astrodebt
```

## 🎮 Mecánicas de Juego

### Recursos
- **Metal**: Material básico de construcción
- **Circuitos**: Componentes electrónicos
- **Combustible**: Necesario para el motor
- **Minerales Raros**: Materiales avanzados
- **Oxígeno**: Recurso vital (se consume cada turno)
- **Chatarra**: Material reciclable

### Minijuegos

1. **Minería**: Extrae recursos de asteroides con timing correcto
2. **Esquivar**: Navega entre escombros recolectando items
3. **Cableado**: Puzzle de conectar circuitos correctamente
4. **Timing**: Calibra sistemas con precisión rítmica

### Sistema de Reparación

La nave tiene varios componentes, algunos críticos para el despegue:
- Motor Principal (crítico)
- Sistema de Navegación (crítico)
- Soporte Vital (crítico)
- Escudo Deflector (opcional)
- Sistema de Comunicaciones (opcional)

## 🧪 Pruebas

```bash
# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=. --cov-report=html

# Ejecutar pruebas específicas
pytest tests/test_finance.py
```

## 📝 Estado del Desarrollo

Este proyecto está en **fase de esqueleto**. Todos los archivos base están creados con:
- ✅ Estructura de clases definida
- ✅ Comentarios sobre funcionalidad
- ✅ Importaciones necesarias
- ✅ Documentación de dependencias
- ⏳ Lógica pendiente de implementación

## 🔄 Próximos Pasos

1. Implementar lógica del sistema de eventos (`engine/events.py`)
2. Implementar sistema de estado del juego (`engine/state.py`)
3. Desarrollar clases de deuda y cálculos de interés (`finance/debt.py`)
4. Implementar gestión de recursos (`gameplay/resources.py`)
5. Crear minijuegos básicos
6. Desarrollar interfaz de usuario
7. Integrar todos los sistemas en el bucle principal
8. Pruebas y balanceo

## 📚 Dependencias entre Módulos

```
main.py
  ├── engine.loop (GameLoop)
  │     ├── engine.state (GameState)
  │     ├── engine.events (EventManager)
  │     ├── ui.renderer (Renderer)
  │     └── ui.hud (HUD)
  │
  ├── finance.loan_manager (LoanManager)
  │     └── finance.debt (Debt classes)
  │
  ├── gameplay.resources (ResourceManager)
  ├── gameplay.repair (RepairSystem)
  │     └── gameplay.minigames
  │
  └── ui.narrator (Narrator)
```

## 🤝 Contribución

Este es un proyecto educativo. Si deseas contribuir:
1. Lee la estructura de módulos
2. Elige un módulo para implementar
3. Sigue los TODOs en los comentarios
4. Escribe pruebas para tu código
5. Mantén el código simple y bien comentado

## 📄 Licencia

Proyecto educativo - Uso libre para fines de aprendizaje

## ✨ Créditos

Desarrollado como herramienta educativa para enseñar conceptos de finanzas personales de manera interactiva y divertida.

