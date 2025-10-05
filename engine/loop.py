"""
GameLoop - Bucle Principal del Juego
Gestiona el flujo del juego, turnos, tiempo y fases
"""

import pygame
import random
from typing import Optional, Dict, Any
import logging
from .state import GameState
from .events import EventManager, EventType, Event
from gameplay.minigames import (
    MiningMinigame,
    AsteroidShooterMinigame,
    TimingMinigame,
    WiringMinigame,
    OxygenRescueMinigame
)

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
        
        # Contadores para mostrar tutorial de minijuegos (primeros 2 intentos)
        self.mining_attempts = 0  # Contador de intentos de minería
        self.repair_attempts = 0  # Contador de intentos de reparación
        
        # Control del evento de oxígeno
        self.oxygen_event_shown = False  # Para mostrar solo una vez por sesión
        self.oxygen_event_pending = False  # Si hay un evento pendiente
        self.oxygen_event_accepted = False  # Si el jugador aceptó el evento
        
        # Suscribir a eventos importantes
        self._setup_event_subscriptions()
    
    def start(self) -> None:
        """Inicia el bucle principal del juego"""
        logger.info("Iniciando bucle del juego...")
        
        # Establecer fase inicial (solo si no está en modo testing)
        if self.game_state.current_phase != "end":
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
            # IMPORTANTE: Si el prestamista está esperando input o hay evento de oxígeno,
            # NO delegar al narrador para evitar conflictos con SPACE
            lender_blocking = self.renderer and self.renderer.lender_waiting_for_input
            oxygen_event_blocking = self.oxygen_event_pending
            
            if self.narrator and self.narrator.is_active and not lender_blocking and not oxygen_event_blocking:
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
        
        # Actualizar animación de prestamista
        if self.renderer:
            self.renderer.update_lender(delta_time)
        
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
            
            # Verificar evento de oxígeno (solo una vez cuando baja del 80%)
            if (self.game_state.oxygen < 80 and not self.oxygen_event_shown 
                and not self.oxygen_event_pending):
                self._trigger_oxygen_event()
    
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
            # PRIORIDAD 1: Verificar si hay evento de oxígeno pendiente (tiene máxima prioridad)
            if self.oxygen_event_pending:
                if event.key == pygame.K_y:  # Aceptar ayudar al marciano
                    self.oxygen_event_accepted = True
                    self.oxygen_event_pending = False
                    self.start_oxygen_rescue_minigame()
                    return
                elif event.key == pygame.K_n:  # Rechazar ayuda
                    self.oxygen_event_pending = False
                    if self.narrator:
                        self.narrator.is_active = False
                    if self.hud:
                        self.hud.add_notification("Has decidido no ayudar al marciano", "info")
                    return
                # Si hay evento de oxígeno pendiente, ignorar otras teclas
                return
            
            # PRIORIDAD 2: Si el prestamista está visible esperando input, solo permitir continuar
            if self.renderer and self.renderer.lender_waiting_for_input:
                if event.key == pygame.K_SPACE:
                    # Ocultar prestamista y cerrar narrador
                    self.renderer.dismiss_lender()
                    if self.narrator:
                        self.narrator.is_active = False
                        self.narrator.current_dialogue = None
                    logger.info("Jugador continuó después de ver prestamista")
                return  # No procesar otras teclas mientras el prestamista está visible
            
            # PRIORIDAD 3: Atajos de teclado para acciones normales
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
                # Si es victoria y no ha comenzado la animación, iniciarla
                if (self.game_state.victory and self.renderer and 
                    not self.renderer.victory_animation_active and 
                    not self.renderer.victory_animation_complete):
                    self.renderer.start_victory_animation()
                # Si la animación ya completó, reiniciar juego
                elif (self.game_state.victory and self.renderer and 
                      self.renderer.victory_animation_complete):
                    self._restart_game()
                # Si no es victoria (game over), reiniciar directamente
                else:
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
        
        # Consumir oxígeno (aleatorio entre 12-15)
        oxygen_consumed = random.randint(12, 15)
        self.game_state.update_oxygen(-oxygen_consumed)
        logger.info(f"Oxígeno consumido en minería: {oxygen_consumed}")
        
        # Cerrar paneles del HUD antes de entrar al minijuego
        if self.hud:
            self.hud.close_all_panels()
        
        # Cambiar a fase de minijuego
        self.change_phase("minigame")
        
        # Incrementar contador de intentos
        self.mining_attempts += 1
        
        # Primeros 2 intentos: mostrar ambos minijuegos en orden (tutorial)
        if self.mining_attempts == 1:
            # Primer intento: Mining Clicker
            selected_game = MiningMinigame
            logger.info("Tutorial: Mostrando Mineral Rush (primer intento de minería)")
        elif self.mining_attempts == 2:
            # Segundo intento: Asteroid Shooter
            selected_game = AsteroidShooterMinigame
            logger.info("Tutorial: Mostrando Asteroid Shooter (segundo intento de minería)")
        else:
            # A partir del tercer intento: aleatorio
            mining_games = [MiningMinigame, AsteroidShooterMinigame]
            selected_game = random.choice(mining_games)
        
        # Crear el minijuego seleccionado
        self.current_minigame = selected_game(self.screen.get_width(), self.screen.get_height())
        
        # Mostrar notificación del minijuego
        game_name = "Mineral Rush" if selected_game == MiningMinigame else "Asteroid Shooter"
        if self.hud:
            self.hud.add_notification(f"Iniciando: {game_name}", "info")
        
        logger.info(f"Minijuego de minería iniciado: {game_name} (Intento #{self.mining_attempts})")
    
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
        
        # Consumir oxígeno (aleatorio entre 12-15) y materiales
        oxygen_consumed = random.randint(12, 15)
        self.game_state.update_oxygen(-oxygen_consumed)
        logger.info(f"Oxígeno consumido en reparación: {oxygen_consumed}")
        
        materials_cost = random.randint(5, 10)
        self.game_state.consume_materials(materials_cost)
        
        # Cerrar paneles del HUD antes de entrar al minijuego
        if self.hud:
            self.hud.close_all_panels()
        
        # Cambiar a fase de minijuego
        self.change_phase("minigame")
        
        # Incrementar contador de intentos
        self.repair_attempts += 1
        
        # Primeros 2 intentos: mostrar ambos minijuegos en orden (tutorial)
        if self.repair_attempts == 1:
            # Primer intento: Timing Precision
            selected_game = TimingMinigame
            logger.info("Tutorial: Mostrando Timing Precision (primer intento de reparación)")
        elif self.repair_attempts == 2:
            # Segundo intento: Wiring Puzzle
            selected_game = WiringMinigame
            logger.info("Tutorial: Mostrando Wiring Puzzle (segundo intento de reparación)")
        else:
            # A partir del tercer intento: aleatorio
            repair_games = [TimingMinigame, WiringMinigame]
            selected_game = random.choice(repair_games)
        
        # Crear el minijuego seleccionado
        self.current_minigame = selected_game(self.screen.get_width(), self.screen.get_height())
        
        # Mostrar notificación del minijuego
        game_name = "Timing Precision" if selected_game == TimingMinigame else "Wiring Puzzle"
        if self.hud:
            self.hud.add_notification(f"Iniciando: {game_name}", "info")
        
        logger.info(f"Minijuego de reparación iniciado: {game_name} (Intento #{self.repair_attempts})")
    
    def _complete_minigame(self) -> None:
        """Completa el minijuego actual y vuelve al juego principal"""
        if self.current_minigame:
            # Obtener resultados del minijuego
            results = self.current_minigame.get_results()
            
            # Verificar si es el minijuego de rescate de oxígeno
            is_oxygen_rescue = isinstance(self.current_minigame, OxygenRescueMinigame)
            
            if is_oxygen_rescue:
                # Procesar recompensa de oxígeno
                oxygen_reward = results.get('reward_oxygen', 0)
                if oxygen_reward > 0:
                    self.game_state.update_oxygen(oxygen_reward)
                    self.event_manager.emit_quick(
                        EventType.OXYGEN_CHANGED,
                        {'amount': oxygen_reward, 'current': self.game_state.oxygen}
                    )
                    if self.hud:
                        self.hud.add_notification(
                            f"¡Has rescatado al marciano y obtenido +{oxygen_reward} de oxígeno!",
                            "success"
                        )
                else:
                    if self.hud:
                        self.hud.add_notification(
                            "El marciano no pudo ser rescatado",
                            "error"
                        )
            else:
                # Procesar recompensas de materiales (minijuegos normales)
                materials_gained = results['reward_materials']
                
                if materials_gained > 0:
                    self.game_state.add_materials(materials_gained)
                
                # Emitir evento y notificación según el éxito
                if results['success']:
                    self.event_manager.emit_quick(
                        EventType.MATERIALS_GAINED_SUCCESS,
                        {'amount': materials_gained}
                    )
                    if self.hud:
                        self.hud.add_notification(
                            f"¡Éxito! Obtuviste {materials_gained} materiales",
                            "success"
                        )
                else:
                    self.event_manager.emit_quick(
                        EventType.MATERIALS_GAINED_FAIL,
                        {'amount': materials_gained}
                    )
                    if self.hud:
                        if materials_gained > 0:
                            self.hud.add_notification(
                                f"Recolectaste {materials_gained} materiales (objetivo no alcanzado)",
                                "warning"
                            )
                        else:
                            self.hud.add_notification(
                                "No recolectaste materiales",
                                "error"
                            )
            
            # Procesar recompensas de reparación
            if results['reward_repair'] != 0:
                self.game_state.update_repair_progress(results['reward_repair'])
                
                # Emitir evento de progreso de reparación
                self.event_manager.emit_quick(
                    EventType.REPAIR_PROGRESS_CHANGED,
                    {'progress': self.game_state.repair_progress}
                )
                
                if results['reward_repair'] > 0:
                    if self.hud:
                        self.hud.add_notification(
                            f"Reparación: +{results['reward_repair']}%",
                            "success"
                        )
                else:
                    if self.hud:
                        self.hud.add_notification(
                            f"¡La nave sufrió daños! {results['reward_repair']}%",
                            "error"
                        )
            
            # Verificar alertas de recursos
            if self.game_state.oxygen <= 20:
                self.event_manager.emit_quick(EventType.ALERT_OXYGEN, {})
            
            if self.game_state.materials == 0:
                self.event_manager.emit_quick(EventType.ALERT_MATERIALS, {})
        
        self.current_minigame = None
        self.change_phase("main_game")
        
        # Verificar si mostrar prestamista (educativo)
        # PERO NO después del minijuego de rescate de oxígeno
        if not is_oxygen_rescue:
            self._check_lender_appearance()
    
    def _check_lender_appearance(self) -> None:
        """
        Verifica si debe aparecer el prestamista aleatorio (educativo)
        Solo aparece una vez cuando el oxígeno < 90
        """
        if self.game_state.oxygen < 90 and not self.game_state.prestamista_shown:
            self.game_state.prestamista_shown = True
            
            # Elegir prestamista aleatorio
            lenders = ['zorvax', 'ktarr', 'consorcio']
            selected_lender = random.choice(lenders)
            
            # Mensajes educativos según prestamista
            messages = {
                'zorvax': "Un prestamista Zorvax se aproxima... Todavía tienes suficiente oxígeno, no hace falta un crédito ahora, pero cuidado de no agotarlo.",
                'ktarr': "Un comerciante Ktarr observa desde lejos... Todavía tienes suficiente oxígeno, no hace falta un crédito ahora, pero cuidado de no agotarlo.",
                'consorcio': "El Consorcio Galáctico te está monitoreando... Todavía tienes suficiente oxígeno, no hace falta un crédito ahora, pero cuidado de no agotarlo."
            }
            
            # Mostrar prestamista visualmente en la escena
            if self.renderer:
                self.renderer.show_lender(selected_lender)
            
            # Mostrar mensaje del narrador
            if self.narrator:
                self.narrator.show_narrative(messages.get(selected_lender, messages['consorcio']))
            
            # Notificación en HUD
            if self.hud:
                self.hud.add_notification(
                    f"⚠️ Prestamista {selected_lender.upper()} detectado",
                    "warning"
                )
            
            logger.info(f"Prestamista aleatorio aparecido: {selected_lender} (Oxígeno: {self.game_state.oxygen:.1f})")
    
    def _trigger_oxygen_event(self) -> None:
        """Dispara el evento de oxígeno cuando está por debajo del 80%"""
        self.oxygen_event_shown = True
        self.oxygen_event_pending = True
        
        # Ocultar prestamista si está visible (para evitar conflictos)
        if self.renderer and self.renderer.lender_visible:
            self.renderer.dismiss_lender()
            logger.info("Prestamista ocultado para mostrar evento de oxígeno")
        
        # Mostrar narrativa del evento
        if self.narrator:
            narrative_text = (
                "¡Un marciano necesita tu ayuda! "
                "Está siendo atacado por criaturas hostiles. "
                "Si lo rescatas, te recompensará con oxígeno valioso. "
                "¿Quieres ayudarlo? (Presiona Y para aceptar, N para rechazar)"
            )
            self.narrator.show_narrative(narrative_text)
        
        # Notificación en HUD
        if self.hud:
            self.hud.add_notification("⚠️ Evento de Oxígeno: ¡Un marciano necesita ayuda!", "warning")
        
        logger.info(f"Evento de oxígeno disparado (Oxígeno actual: {self.game_state.oxygen:.1f})")
    
    def start_oxygen_rescue_minigame(self) -> None:
        """Inicia el minijuego de rescate del marciano"""
        logger.info("Iniciando minijuego de rescate del marciano")
        
        # Cerrar paneles del HUD antes de entrar al minijuego
        if self.hud:
            self.hud.close_all_panels()
        
        # Cambiar a fase de minijuego
        self.change_phase("minigame")
        
        # Crear el minijuego
        self.current_minigame = OxygenRescueMinigame(self.screen.get_width(), self.screen.get_height())
        
        # Notificación
        if self.hud:
            self.hud.add_notification("¡Rescata al marciano de los enemigos!", "info")
    
    def _restart_game(self) -> None:
        """Reinicia el juego"""
        logger.info("Reiniciando juego...")
        
        # Reiniciar estado del juego
        self.game_state.__init__(self.game_state.config)
        
        # Resetear contadores de minijuegos (para volver a mostrar tutorial)
        self.mining_attempts = 0
        self.repair_attempts = 0
        
        # Resetear control del evento de oxígeno
        self.oxygen_event_shown = False
        self.oxygen_event_pending = False
        self.oxygen_event_accepted = False
        
        # Resetear animaciones del renderer
        if self.renderer:
            self.renderer.reset_animations()
        
        # Resetear narrador
        if self.narrator:
            self.narrator.is_active = False
            self.narrator.current_dialogue = None
            self.narrator.dialogue_queue.clear()
        
        # Volver a intro
        self.change_phase("intro")
        
        # Mostrar narrativa inicial de nuevo
        if self.narrator:
            intro_text = (
                "Tu nave se estrelló en un planeta desconocido. "
                "Para volver a la Tierra deberás reparar tu nave, "
                "gestionar tu oxígeno y tus materiales, "
                "y decidir sabiamente si tomas préstamos de oxígeno... o no."
            )
            self.narrator.show_narrative(intro_text)
        
        logger.info("Juego reiniciado completamente")

