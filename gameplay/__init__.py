"""
Gameplay Module
Módulo que contiene la lógica principal del juego: recursos, reparación y minijuegos
"""

from .resources import ResourceManager, ResourceType
from .repair import RepairSystem, ShipComponent

__all__ = ['ResourceManager', 'ResourceType', 'RepairSystem', 'ShipComponent']

