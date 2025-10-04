"""
Minigames Module
Módulo que contiene los minijuegos de AstroDebt
"""

from .mining import MiningMinigame
from .dodge import DodgeMinigame
from .wiring import WiringMinigame
from .timing import TimingMinigame

__all__ = ['MiningMinigame', 'DodgeMinigame', 'WiringMinigame', 'TimingMinigame']

