"""
AudioManager - Sistema de Gestión de Audio
Maneja música de fondo y efectos de sonido del juego
"""

import pygame
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AudioManager:
    """
    Gestor de audio del juego
    
    Responsabilidades:
        - Cargar y reproducir música de fondo
        - Cargar y reproducir efectos de sonido
        - Controlar volumen de música y efectos
        - Gestionar estados de audio (habilitado/deshabilitado)
    """
    
    def __init__(self):
        """Inicializa el gestor de audio"""
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music: Optional[str] = None
        
        # Volúmenes (0.0 - 1.0)
        self.music_volume = 0.5  # 50% para música de fondo
        self.sfx_volume = 0.7    # 70% para efectos de sonido
        
        # Estados
        self.music_enabled = True
        self.sfx_enabled = True
        
        logger.info("AudioManager inicializado")
    
    def load_sound(self, name: str, filename: str) -> bool:
        """
        Carga un efecto de sonido
        
        Args:
            name: Nombre identificador del sonido
            filename: Nombre del archivo en data/sounds/
            
        Returns:
            True si se cargó correctamente, False en caso contrario
        """
        try:
            path = os.path.join('data', 'sounds', filename)
            if not os.path.exists(path):
                logger.warning(f"Archivo de sonido no encontrado: {path}")
                return False
            
            self.sounds[name] = pygame.mixer.Sound(path)
            self.sounds[name].set_volume(self.sfx_volume)
            logger.info(f"Sonido cargado: {name} ({filename})")
            return True
        except Exception as e:
            logger.error(f"Error al cargar sonido {name}: {e}")
            return False
    
    def play_sound(self, name: str, loops: int = 0) -> None:
        """
        Reproduce un efecto de sonido
        
        Args:
            name: Nombre del sonido a reproducir
            loops: Número de repeticiones (0 = una vez)
        """
        if self.sfx_enabled and name in self.sounds:
            self.sounds[name].play(loops=loops)
        elif name not in self.sounds:
            logger.warning(f"Sonido no cargado: {name}")
    
    def stop_sound(self, name: str) -> None:
        """Detiene un efecto de sonido específico"""
        if name in self.sounds:
            self.sounds[name].stop()
    
    def load_music(self, filename: str) -> bool:
        """
        Carga música de fondo
        
        Args:
            filename: Nombre del archivo en data/music/
            
        Returns:
            True si se cargó correctamente, False en caso contrario
        """
        try:
            path = os.path.join('data', 'music', filename)
            if not os.path.exists(path):
                logger.warning(f"Archivo de música no encontrado: {path}")
                return False
            
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            self.current_music = filename
            logger.info(f"Música cargada: {filename}")
            return True
        except Exception as e:
            logger.error(f"Error al cargar música: {e}")
            return False
    
    def play_music(self, loops: int = -1, fade_ms: int = 0) -> None:
        """
        Reproduce música de fondo
        
        Args:
            loops: Número de repeticiones (-1 = loop infinito)
            fade_ms: Tiempo de fade in en milisegundos (0 = sin fade)
        """
        if self.music_enabled:
            try:
                if fade_ms > 0:
                    pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
                else:
                    pygame.mixer.music.play(loops=loops)
                logger.info(f"Música reproduciendo: {self.current_music}")
            except Exception as e:
                logger.error(f"Error al reproducir música: {e}")
    
    def stop_music(self, fade_ms: int = 0) -> None:
        """
        Detiene la música de fondo
        
        Args:
            fade_ms: Tiempo de fade out en milisegundos (0 = detener inmediatamente)
        """
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        logger.info("Música detenida")
    
    def pause_music(self) -> None:
        """Pausa la música de fondo"""
        pygame.mixer.music.pause()
    
    def unpause_music(self) -> None:
        """Resume la música de fondo pausada"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float) -> None:
        """
        Establece el volumen de la música
        
        Args:
            volume: Volumen (0.0 - 1.0)
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        logger.info(f"Volumen de música: {self.music_volume:.1%}")
    
    def set_sfx_volume(self, volume: float) -> None:
        """
        Establece el volumen de los efectos de sonido
        
        Args:
            volume: Volumen (0.0 - 1.0)
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        # Actualizar volumen de todos los sonidos cargados
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)
        logger.info(f"Volumen de efectos: {self.sfx_volume:.1%}")
    
    def toggle_music(self) -> bool:
        """
        Activa/desactiva la música
        
        Returns:
            Estado actual de la música (True = habilitada)
        """
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.unpause_music()
        else:
            self.pause_music()
        logger.info(f"Música {'habilitada' if self.music_enabled else 'deshabilitada'}")
        return self.music_enabled
    
    def toggle_sfx(self) -> bool:
        """
        Activa/desactiva los efectos de sonido
        
        Returns:
            Estado actual de los efectos (True = habilitados)
        """
        self.sfx_enabled = not self.sfx_enabled
        logger.info(f"Efectos de sonido {'habilitados' if self.sfx_enabled else 'deshabilitados'}")
        return self.sfx_enabled
    
    def is_music_playing(self) -> bool:
        """Verifica si la música está reproduciéndose"""
        return pygame.mixer.music.get_busy()

