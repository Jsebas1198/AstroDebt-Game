"""
Minigames Module
Módulo que contiene los minijuegos de AstroDebt
"""

from .base import BaseMinigame
from .mining import MiningMinigame
from .asteroid_shooter import AsteroidShooterMinigame
from .timing import TimingMinigame
from .wiring import WiringMinigame
from .dodge import DodgeMinigame

__all__ = [
    'BaseMinigame',
    'MiningMinigame', 
    'AsteroidShooterMinigame',
    'TimingMinigame',
    'WiringMinigame',
    'DodgeMinigame'
]

