"""
GameLoop - Bucle Principal del Juego
Gestiona el flujo del juego, turnos, tiempo y fases
"""

import pygame
from typing import Optional, Dict, Any
import logging
from .state import GameState
from .events import EventManager, EventType, Event

logger = logging.getLogger(__name__)


class GameLoop:
    """
    Clase que gestiona el bucle principal del juego
    
    Responsabilidades:
        - Procesar eventos de entrada
        - Actualizar estado del juego
        - Controlar fases del juego (exploración, combate, gestión)
        - Gestionar el tiempo y los turnos
    
    Dependencias:
        - engine.state.GameState: Estado del juego
        - engine.events.EventManager: Sistema de eventos
        - ui.renderer.Renderer: Para renderizar el juego
        - ui.hud.HUD: Para mostrar la interfaz
    """
    
    def __init__(self, game_state: GameState, event_manager: EventManager):
        """
        Inicializa el bucle del juego
        
        Args:
            game_state: Instancia del estado del juego
            event_manager: Gestor de eventos
        """
        self.game_state = game_state
        self.event_manager = event_manager
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Referencias a componentes (se asignan después)
        self.renderer = None
        self.hud = None
        self.narrator = None
        self.config = None
        self.screen = None
        
        # Estado del minijuego actual
        self.current_minigame = None
        
        # Control de input
        self.input_enabled = True
        
        # Suscribir a eventos importantes
        self._setup_event_subscriptions()
    
    def start(self) -> None:
        """Inicia el bucle principal del juego"""
        logger.info("Iniciando bucle del juego...")
        
        # Establecer fase inicial
        self.game_state.current_phase = "intro"
        
        # Mostrar narrativa inicial
        if self.narrator:
            intro_text = (
                "Tu nave se estrelló en un planeta desconocido. "
                "Para volver a la Tierra deberás reparar tu nave, "
                "gestionar tu oxígeno y tus materiales, "
                "y decidir sabiamente si tomas préstamos de oxígeno... o no."
            )
            self.narrator.show_narrative(intro_text)
        
        # Emitir evento de inicio
        self.event_manager.emit_quick(EventType.PHASE_CHANGED, {"phase": "intro"})
        
        self.running = True
        self.run()
    
    def run(self) -> None:
        """Ejecuta el bucle principal del juego"""
        while self.running:
            # Calcular delta time
            delta_time = self.clock.tick(self.fps) / 1000.0
            
            # Procesar eventos
            self.handle_events()
            
            # Actualizar lógica del juego
            self.update(delta_time)
            
            # Renderizar
            self.render()
            
            # Procesar cola de eventos
            self.event_manager.process_queue()
        
        logger.info("Bucle del juego terminado")
    
    def handle_events(self) -> None:
        """Procesa todos los eventos de entrada"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop()
                return
            
            # Delegar eventos según la fase actual
            if self.game_state.current_phase == "intro":
                self._handle_intro_events(event)
            elif self.game_state.current_phase == "main_game":
                self._handle_main_game_events(event)
            elif self.game_state.current_phase == "minigame":
                self._handle_minigame_events(event)
            elif self.game_state.current_phase == "end":
                self._handle_end_events(event)
            
            # Delegar a componentes UI
            if self.narrator and self.narrator.is_active:
                self.narrator.handle_input(event)
            elif self.hud and self.input_enabled:
                self.hud.handle_input(event)
    
    def update(self, delta_time: float) -> None:
        """
        Actualiza el estado del juego
        
        Args:
            delta_time: Tiempo transcurrido desde el último frame (en segundos)
        """
        # Actualizar renderer (para efectos como shake)
        if self.renderer and hasattr(self.renderer, 'update'):
            self.renderer.update(delta_time)
        
        # Actualizar componentes UI
        if self.hud:
            self.hud.update(delta_time)
        if self.narrator:
            self.narrator.update(delta_time)
        
        # Actualizar según la fase
        if self.game_state.current_phase == "minigame" and self.current_minigame:
            self.current_minigame.update(delta_time)
            
            # Verificar si el minijuego terminó
            if self.current_minigame.is_complete:
                self._complete_minigame()
        
        # Verificar condiciones del juego
        if self.game_state.current_phase == "main_game":
            self.game_state.check_game_over_conditions()
    
    def render(self) -> None:
        """Renderiza el frame actual"""
        if not self.screen:
            return
        
        # Limpiar pantalla
        self.screen.fill((0, 0, 0))
        
        # Renderizar según la fase
        if self.renderer:
            if self.game_state.current_phase == "intro":
                self.renderer.render_intro()
            elif self.game_state.current_phase == "main_game":
                self.renderer.render_frame()
            elif self.game_state.current_phase == "minigame" and self.current_minigame:
                self.current_minigame.render(self.screen)
            elif self.game_state.current_phase == "end":
                self.renderer.render_end_screen()
        
        # Renderizar HUD (siempre encima)
        if self.hud and self.game_state.current_phase in ["main_game", "minigame"]:
            self.hud.render()
        
        # Renderizar narrador (más encima)
        if self.narrator:
            self.narrator.render()
        
        # Actualizar pantalla
        pygame.display.flip()
    
    def change_phase(self, new_phase: str) -> None:
        """
        Cambia la fase actual del juego
        
        Args:
            new_phase: Nueva fase (intro, main_game, minigame, end)
        """
        valid_phases = ["intro", "main_game", "minigame", "end"]
        if new_phase not in valid_phases:
            logger.warning(f"Fase inválida: {new_phase}")
            return
        
        old_phase = self.game_state.current_phase
        self.game_state.current_phase = new_phase
        
        logger.info(f"Cambio de fase: {old_phase} -> {new_phase}")
        
        # Emitir evento de cambio de fase
        self.event_manager.emit_quick(
            EventType.PHASE_CHANGED,
            {"old_phase": old_phase, "new_phase": new_phase}
        )
        
        # Acciones específicas por fase
        if new_phase == "main_game":
            # Avanzar turno al entrar en fase principal
            self.game_state.advance_turn()
            
            # Resetear completamente el shake de la intro
            if self.renderer and hasattr(self.renderer, 'reset_shake'):
                self.renderer.reset_shake()
                logger.info("Shake de intro reseteado")
    
    def _setup_event_subscriptions(self) -> None:
        """Configura las suscripciones a eventos"""
        # Suscribir a eventos de game over y victoria
        self.event_manager.subscribe(EventType.GAME_OVER, self._on_game_over)
        self.event_manager.subscribe(EventType.VICTORY, self._on_victory)
    
    def _on_game_over(self, event: Event) -> None:
        """Maneja el evento de game over"""
        self.change_phase("end")
        if self.narrator:
            reason = event.data.get("reason", "unknown")
            if reason == "oxygen_depleted":
                self.narrator.show_narrative("El oxígeno se ha agotado. Tu aventura termina aquí.")
            elif reason == "debt_overwhelming":
                self.narrator.show_narrative("Tus acreedores han perdido la paciencia. No hay escapatoria de tus deudas.")
    
    def _on_victory(self, event: Event) -> None:
        """Maneja el evento de victoria"""
        self.change_phase("end")
        if self.narrator:
            self.narrator.show_narrative(
                "¡Lo lograste! La nave está reparada y lista para despegar. "
                "Ahora solo espero que puedas pagar tus deudas..."
            )
    
    def stop(self) -> None:
        """Detiene el bucle del juego"""
        logger.info("Deteniendo el bucle del juego...")
        self.running = False
    
    def _handle_intro_events(self, event: pygame.event.Event) -> None:
        """Maneja eventos durante la fase de intro"""
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                # Saltar intro y empezar el juego
                self.change_phase("main_game")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Click para continuar
            self.change_phase("main_game")
    
    def _handle_main_game_events(self, event: pygame.event.Event) -> None:
        """Maneja eventos durante la fase principal del juego"""
        if event.type == pygame.KEYDOWN:
            # Atajos de teclado para acciones
            if event.key == pygame.K_m:
                # Minar materiales
                self.start_mining_minigame()
            elif event.key == pygame.K_r:
                # Reparar nave
                self.start_repair_minigame()
            elif event.key == pygame.K_ESCAPE:
                # Menú de pausa
                pass
    
    def _handle_minigame_events(self, event: pygame.event.Event) -> None:
        """Maneja eventos durante los minijuegos"""
        if self.current_minigame:
            self.current_minigame.handle_input(event)
    
    def _handle_end_events(self, event: pygame.event.Event) -> None:
        """Maneja eventos durante la pantalla final"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Reiniciar juego
                self._restart_game()
            elif event.key == pygame.K_ESCAPE:
                # Salir del juego
                self.stop()
    
    def start_mining_minigame(self) -> None:
        """Inicia el minijuego de minería"""
        if not self.game_state.can_afford_action("mining"):
            if self.hud:
                self.hud.add_notification("Oxígeno insuficiente para minar", "warning")
            return
        
        # Consumir oxígeno
        self.game_state.update_oxygen(-self.game_state.oxygen_cost_mining)
        
        # Cambiar a fase de minijuego
        self.change_phase("minigame")
        
        # Crear minijuego (se implementará más adelante)
        # self.current_minigame = MiningMinigame()
        logger.info("Minijuego de minería iniciado (pendiente de implementación)")
    
    def start_repair_minigame(self) -> None:
        """Inicia el minijuego de reparación"""
        if not self.game_state.can_afford_action("repair"):
            if self.hud:
                self.hud.add_notification("Oxígeno insuficiente para reparar", "warning")
            return
        
        if self.game_state.materials < 5:
            if self.hud:
                self.hud.add_notification("Materiales insuficientes para reparar", "warning")
            return
        
        # Consumir oxígeno
        self.game_state.update_oxygen(-self.game_state.oxygen_cost_repair)
        
        # Cambiar a fase de minijuego
        self.change_phase("minigame")
        
        # Crear minijuego (se implementará más adelante)
        # self.current_minigame = TimingMinigame()
        logger.info("Minijuego de reparación iniciado (pendiente de implementación)")
    
    def _complete_minigame(self) -> None:
        """Completa el minijuego actual y vuelve al juego principal"""
        if self.current_minigame:
            # Procesar resultados del minijuego
            # (se implementará con los minijuegos)
            pass
        
        self.current_minigame = None
        self.change_phase("main_game")
    
    def _restart_game(self) -> None:
        """Reinicia el juego"""
        logger.info("Reiniciando juego...")
        # Reiniciar estado
        self.game_state.__init__(self.game_state.config)
        # Volver a intro
        self.change_phase("intro")

