# 🚀 AstroDebt - Manual del Jugador

## 📖 Historia
Tu nave espacial se ha estrellado en un planeta desconocido. Para volver a la Tierra deberás:
- 🔧 Reparar tu nave hasta el 100%
- 🫧 Gestionar tu oxígeno (tu moneda)
- ⛏️ Recolectar materiales para las reparaciones
- 💰 Decidir sabiamente si tomas préstamos de alienígenas

## 🎮 Controles Principales

### En el Menú Principal
- **ESPACIO** o **CLICK** → Comenzar el juego
- **ESC** → Salir

### En el Juego Principal
- **M** → Iniciar minijuego de minería (consume 2 de oxígeno)
- **R** → Iniciar minijuego de reparación (consume 3 de oxígeno + 5-10 materiales)
- **I** → Ver inventario detallado
- **D** → Ver panel de deudas
- **P** → Ver panel de reparación
- **ESC** → Cerrar paneles / Pausar

## 🎯 Minijuegos

### 🪨 Minería (Tecla M)
Al presionar M, el juego selecciona aleatoriamente uno de estos minijuegos:

#### 1. Mining Clicker
- **Objetivo**: Destruir rocas haciendo clic repetidamente
- **Controles**: 
  - Click izquierdo o ESPACIO en la roca
  - Mantén el combo para más puntos
- **Recompensa**: 3-8 materiales (éxito) / 1 material (fallo)

#### 2. Asteroid Shooter
- **Objetivo**: Destruir 5 asteroides antes de que se acabe el tiempo
- **Controles**:
  - Mueve el mouse para apuntar
  - Click izquierdo o ESPACIO para disparar
  - Flechas izquierda/derecha para rotar el cañón
- **Recompensa**: 5-10 materiales (éxito) / 1-2 materiales (fallo)

### 🔧 Reparación (Tecla R)
Al presionar R, el juego selecciona aleatoriamente uno de estos minijuegos:

#### 3. Timing Precision
- **Objetivo**: Presionar ESPACIO cuando el indicador esté en la zona verde
- **Controles**:
  - ESPACIO o Click cuando el indicador esté en la zona correcta
  - Zona dorada = puntos extra
- **Recompensa**: +5-15% reparación (éxito) / 0% o -2% (fallo)

#### 4. Wiring Puzzle
- **Objetivo**: Conectar cables del mismo color entre paneles
- **Controles**:
  - Arrastra los cables con el mouse
  - R para reiniciar el puzzle
- **Recompensa**: +10-20% reparación (éxito) / 0% o -2% (fallo)

## 📊 Recursos y Economía

### 🫧 Oxígeno (Moneda)
- **Inicial**: 100 unidades
- **Consumo por turno**: 2 unidades
- **Consumo por minería**: 2 unidades
- **Consumo por reparación**: 3 unidades
- ⚠️ Si llega a 0, pierdes el juego

### ⛏️ Materiales
- **Inicial**: 10 unidades
- **Uso**: Reparar la nave y pagar préstamos
- **Obtención**: Minijuegos de minería
- **Costo de reparación**: 5-10 por intento

### 🔧 Progreso de Reparación
- **Objetivo**: Alcanzar 100%
- **Incremento**: Mediante minijuegos de reparación
- 🏆 Al llegar al 100%, ¡ganas el juego!

## 💡 Consejos Estratégicos

1. **Gestión de Recursos**
   - No gastes todo tu oxígeno en minería
   - Mantén un balance entre materiales y oxígeno
   - Considera los préstamos solo en emergencias

2. **Minijuegos**
   - En Mining Clicker, mantén el combo alto para más recompensas
   - En Asteroid Shooter, apunta a los asteroides más grandes primero
   - En Timing Precision, apunta a la zona dorada para bonus
   - En Wiring Puzzle, tómate tu tiempo para identificar los colores

3. **Préstamos** (próximamente)
   - Los préstamos te dan oxígeno inmediato
   - Pero deberás pagar con materiales (más intereses)
   - Cada prestamista tiene diferentes tasas de interés

## 🏆 Condiciones de Victoria/Derrota

### Victoria ✅
- Reparar la nave al 100%

### Derrota ❌
- Oxígeno llega a 0
- Deudas impagables (cuando se implementen los préstamos)

## 🐛 Solución de Problemas

### El juego no inicia
1. Asegúrate de tener Python 3.7+ instalado
2. Instala Pygame: `pip install pygame`
3. Ejecuta desde la carpeta del juego: `python main.py`

### Los minijuegos no aparecen
- Verifica que tengas al menos 2 de oxígeno para minería
- Para reparación necesitas 3 de oxígeno Y 5+ materiales

### Pantalla negra
- Presiona ESC para cerrar paneles abiertos
- Reinicia el juego si persiste

## 🎯 Objetivo Educativo

AstroDebt enseña conceptos financieros importantes:
- **Gestión de recursos**: Equilibrar ingresos y gastos
- **Costo de oportunidad**: Cada acción tiene un precio
- **Inversión**: Gastar recursos ahora para obtener más después
- **Deuda responsable**: Los préstamos pueden ayudar, pero tienen un costo

¡Buena suerte, astronauta! 🚀
