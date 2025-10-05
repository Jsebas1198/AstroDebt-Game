"""
Nave Varada - Juego Educativo sobre Finanzas
Punto de entrada principal del juego

El jugador debe reparar su nave espacial varada mientras gestiona
préstamos de oxígeno y recursos. Enseña conceptos de deuda, intereses
y priorización de recursos a través de mecánicas gamificadas.
"""

import pygame
import sys
import json
import logging
import os
from engine.state import GameState
from engine.loop import GameLoop
from engine.events import EventManager
from ui.renderer import Renderer
from ui.hud import HUD
from ui.narrator import Narrator
from finance.loan_manager import LoanManager
from gameplay.resources import ResourceManager
from gameplay.repair import RepairSystem

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Carga la configuración del juego desde config.json"""
    config_path = os.path.join('data', 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            logger.info("Configuración cargada exitosamente")
            return config
    except Exception as e:
        logger.error(f"Error cargando configuración: {e}")
        # Configuración por defecto si falla la carga
        return {
            "game": {
                "title": "Nave Varada",
                "screen_width": 1280,
                "screen_height": 720,
                "fps": 60
            },
            "gameplay": {
                "initial_oxygen": 100.0,
                "oxygen_consumption_per_turn": 2.0,
                "victory_repair_threshold": 100.0,
                "max_active_loans": 3
            }
        }


def main():
    """
    Función principal del juego
    Inicializa Pygame, crea las instancias necesarias y ejecuta el bucle principal
    """
    logger.info("Iniciando Nave Varada...")
    
    # Cargar configuración
    config = load_config()
    
    # Inicializar Pygame
    pygame.init()
    pygame.mixer.init()
    
    # Configurar ventana
    screen_width = config['game']['screen_width']
    screen_height = config['game']['screen_height']
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption(config['game']['title'])
    
    # Crear icono de ventana (si existe)
    try:
        icon_path = os.path.join('data', 'assets', 'blue_spaceship.png')
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
    except Exception as e:
        logger.warning(f"No se pudo cargar el icono: {e}")
    
    # Crear instancias principales
    event_manager = EventManager()
    game_state = GameState(config)
    
    # Crear sistemas del juego
    resource_manager = ResourceManager()
    loan_manager = LoanManager()
    repair_system = RepairSystem()
    
    # Crear componentes de UI
    renderer = Renderer(screen_width, screen_height)
    hud = HUD(screen)
    narrator = Narrator(screen)
    
    # Conectar referencias cruzadas
    game_state.loan_manager = loan_manager
    game_state.resource_manager = resource_manager
    game_state.repair_system = repair_system
    
    loan_manager.event_manager = event_manager
    loan_manager.game_state = game_state
    
    resource_manager.event_manager = event_manager
    resource_manager.game_state = game_state
    
    repair_system.resource_manager = resource_manager
    repair_system.event_manager = event_manager
    repair_system.game_state = game_state
    
    hud.game_state = game_state
    hud.loan_manager = loan_manager
    hud.resource_manager = resource_manager
    
    narrator.event_manager = event_manager
    
    # Inicializar componentes
    renderer.initialize(screen)
    hud.initialize()
    narrator.initialize()
    
    # Crear y configurar el game loop
    game_loop = GameLoop(game_state, event_manager)
    game_loop.renderer = renderer
    game_loop.hud = hud
    game_loop.narrator = narrator
    game_loop.config = config
    game_loop.screen = screen
    
    try:
        # Iniciar el juego
        logger.info("Iniciando bucle principal del juego")
        game_loop.start()
    except KeyboardInterrupt:
        logger.info("Juego interrumpido por el usuario")
    except Exception as e:
        logger.error(f"Error en el juego: {e}", exc_info=True)
    finally:
        # Cleanup
        logger.info("Cerrando el juego...")
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    main()

