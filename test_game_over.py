"""
Script de prueba para verificar la pantalla de Game Over por falta de oxígeno
"""

import pygame
import sys
from engine.state import GameState
from engine.loop import GameLoop
from engine.events import EventManager
from ui.renderer import Renderer
from ui.hud import HUD
from ui.narrator import Narrator
from ui.audio import AudioManager

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Crear pantalla
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Test Game Over - AstroDebt")

# Crear componentes
config = {
    "game": {
        "title": "AstroDebt - Test Game Over",
        "screen_width": 1280,
        "screen_height": 720,
        "fps": 60
    },
    "gameplay": {
        "initial_oxygen": 100.0,  # Oxígeno normal
        "oxygen_consumption_per_turn": 1.0,
        "victory_repair_threshold": 100.0,
        "max_active_loans": 3
    }
}

event_manager = EventManager()
game_state = GameState(config)
renderer = Renderer(1280, 720)
hud = HUD(screen)
narrator = Narrator(screen)
audio_manager = AudioManager()

# Conectar referencias
renderer.game_state = game_state
hud.game_state = game_state
narrator.event_manager = event_manager

# Inicializar
renderer.initialize(screen)
hud.initialize()
narrator.initialize()

# Cargar música
if audio_manager.load_music('399325__komitwav__chiptune-loop-100-bpm.wav'):
    audio_manager.play_music(loops=-1)

# Crear game loop
game_loop = GameLoop(game_state, event_manager)
game_loop.renderer = renderer
game_loop.hud = hud
game_loop.narrator = narrator
game_loop.audio_manager = audio_manager
game_loop.screen = screen
game_loop.config = config

print("\n" + "="*60)
print("TEST DE GAME OVER POR FALTA DE OXÍGENO")
print("="*60)
print(f"Oxígeno inicial: {game_state.oxygen}")
print("\nInstrucciones:")
print("1. Presiona ESPACIO o CLICK para saltar la intro")
print("2. El oxígeno está muy bajo (5)")
print("3. Presiona M para minar y consumir oxígeno")
print("4. El juego terminará automáticamente cuando llegue a 0")
print("5. En la pantalla de Game Over:")
print("   · Presiona ESPACIO para reiniciar")
print("   · Presiona ESC para salir")
print("="*60 + "\n")

# Forzar game over inmediato para prueba rápida
print("MODO DE PRUEBA: Forzando game over inmediato...")
game_state.oxygen = 0
game_state.trigger_game_over("oxygen_depleted")
print(f"Estado: oxygen={game_state.oxygen}, game_over={game_state.game_over}, phase={game_state.current_phase}")

# Iniciar juego
try:
    game_loop.start()
except KeyboardInterrupt:
    print("\nJuego interrumpido por el usuario")
finally:
    pygame.quit()
    sys.exit()

