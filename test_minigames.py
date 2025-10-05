"""
Script de prueba para verificar que los minijuegos funcionan correctamente
"""

import pygame
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gameplay.minigames import (
    MiningMinigame,
    AsteroidShooterMinigame,
    TimingMinigame,
    WiringMinigame
)


def test_minigame(minigame_class, name):
    """Prueba un minijuego individual"""
    print(f"\nProbando {name}...")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption(f"Test: {name}")
    clock = pygame.time.Clock()
    
    # Crear instancia del minijuego
    minigame = minigame_class(1280, 720)
    
    # Loop de prueba
    running = True
    while running and not minigame.is_complete:
        delta_time = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            minigame.handle_input(event)
        
        # Actualizar minijuego
        minigame.update(delta_time)
        
        # Renderizar
        screen.fill((0, 0, 0))
        minigame.render(screen)
        pygame.display.flip()
    
    # Mostrar resultados
    if minigame.is_complete:
        results = minigame.get_results()
        print(f"Minijuego completado:")
        print(f"  - Éxito: {results['success']}")
        print(f"  - Puntuación: {results['score']}")
        print(f"  - Materiales ganados: {results['reward_materials']}")
        print(f"  - Progreso de reparación: {results['reward_repair']}")
    else:
        print("Minijuego cancelado")
    
    pygame.quit()


def main():
    """Función principal de prueba"""
    print("=== PRUEBA DE MINIJUEGOS DE ASTRODEBT ===")
    print("\nSelecciona un minijuego para probar:")
    print("1. Mining Clicker")
    print("2. Asteroid Shooter")
    print("3. Timing Precision")
    print("4. Wiring Puzzle")
    print("5. Probar todos en secuencia")
    print("0. Salir")
    
    while True:
        try:
            choice = input("\nOpción: ")
            
            if choice == "1":
                test_minigame(MiningMinigame, "Mining Clicker")
            elif choice == "2":
                test_minigame(AsteroidShooterMinigame, "Asteroid Shooter")
            elif choice == "3":
                test_minigame(TimingMinigame, "Timing Precision")
            elif choice == "4":
                test_minigame(WiringMinigame, "Wiring Puzzle")
            elif choice == "5":
                print("\nProbando todos los minijuegos...")
                test_minigame(MiningMinigame, "Mining Clicker")
                test_minigame(AsteroidShooterMinigame, "Asteroid Shooter")
                test_minigame(TimingMinigame, "Timing Precision")
                test_minigame(WiringMinigame, "Wiring Puzzle")
                print("\n¡Todas las pruebas completadas!")
            elif choice == "0":
                print("Saliendo...")
                break
            else:
                print("Opción no válida")
        except KeyboardInterrupt:
            print("\nPrueba interrumpida")
            break
        except Exception as e:
            print(f"Error durante la prueba: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
