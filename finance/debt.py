"""
Debt - Sistema de Deudas y Préstamos
Simplificado para MVP: Préstamos en oxígeno, pagos en materiales
Concepto educativo: Oxígeno = Dinero, Materiales = Trabajo
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class Debt(ABC):
    """
    Clase base abstracta para todos los tipos de deuda
    
    Simplificación MVP:
    - Préstamos se dan en OXÍGENO (moneda)
    - Pagos se hacen en MATERIALES (trabajo)
    - Conversión basada en interés del prestamista
    
    Atributos:
        principal: Cantidad de OXÍGENO prestado
        interest_rate: Tasa de interés (multiplicador para conversión)
        materials_owed: MATERIALES que se deben pagar
        turns_until_due: Turnos restantes para pagar
        is_defaulted: True si se ha incumplido el pago
        creditor_name: Nombre del acreedor
    """
    
    principal: float  # Oxígeno prestado
    interest_rate: float  # Multiplicador de conversión
    current_balance: float  # Balance en oxígeno (para tracking)
    turns_until_due: int  # Turnos para pagar
    is_defaulted: bool = False
    creditor_name: str = "Unknown"
    materials_owed: int = 0  # Materiales a pagar
    
    def __post_init__(self):
        """Inicializa el balance y calcula materiales a pagar"""
        if self.current_balance == 0:
            self.current_balance = self.principal
        
        # Calcular materiales a pagar según interés
        # Fórmula: materiales = oxígeno * (1 + interest_rate)
        self.materials_owed = int(self.principal * (1 + self.interest_rate))
        
        logger.info(f"Préstamo creado: {self.principal} oxígeno de {self.creditor_name}, "
                   f"debe pagar {self.materials_owed} materiales")
    
    @abstractmethod
    def calculate_interest(self) -> float:
        """
        Calcula el interés para el turno actual
        
        Returns:
            Cantidad de interés generado
        """
        pass
    
    @abstractmethod
    def apply_penalty(self) -> dict:
        """
        Aplica penalizaciones por impago o retraso
        
        Returns:
            Diccionario con los efectos de la penalización
        """
        pass
    
    def make_payment(self, materials_paid: int) -> bool:
        """
        Realiza un pago hacia la deuda EN MATERIALES
        
        Args:
            materials_paid: Cantidad de MATERIALES a pagar
            
        Returns:
            True si la deuda fue pagada completamente
        """
        if materials_paid <= 0:
            return False
        
        # Reducir materiales adeudados
        self.materials_owed = max(0, self.materials_owed - materials_paid)
        
        # Actualizar balance en oxígeno (para tracking)
        payment_ratio = materials_paid / (self.principal * (1 + self.interest_rate))
        self.current_balance = max(0, self.current_balance - (self.principal * payment_ratio))
        
        logger.info(f"Pago de {materials_paid} materiales a {self.creditor_name}. "
                   f"Restante: {self.materials_owed} materiales")
        
        # Verificar si está completamente pagado
        if self.materials_owed <= 0:
            logger.info(f"Préstamo de {self.creditor_name} pagado completamente")
            return True
        
        return False
    
    def advance_turn(self) -> None:
        """Avanza un turno, verificando vencimiento"""
        self.turns_until_due -= 1
        
        # En MVP, el interés ya está calculado en materials_owed
        # No se aplica interés compuesto adicional
        
        if self.turns_until_due <= 0 and self.materials_owed > 0:
            self.is_defaulted = True
            logger.warning(f"Préstamo de {self.creditor_name} en DEFAULT")
    
    def get_minimum_payment(self) -> int:
        """
        Calcula el pago mínimo requerido EN MATERIALES
        
        Returns:
            Cantidad mínima de materiales a pagar
        """
        if self.turns_until_due <= 0:
            # Si está vencido, debe pagar todo
            return self.materials_owed
        elif self.turns_until_due <= 2:
            # Si quedan pocos turnos, pagar al menos la mitad
            return max(1, self.materials_owed // 2)
        else:
            # Pago mínimo proporcional
            return max(1, self.materials_owed // self.turns_until_due)


class ZorvaxDebt(Debt):
    """
    Deuda con el Banco Zorvax (MVP)
    
    Características:
        - Interés del 50% (1.5x conversión oxígeno->materiales)
        - Penalización: Roba materiales adicionales si no pagas
        - Plazo: 10 turnos
    
    Ejemplo:
        - Pides 50 oxígeno
        - Debes pagar 75 materiales
        - Si no pagas, te quita materiales extras
    """
    
    def __init__(self, principal: float, turns: int = 10):
        super().__init__(
            principal=principal,
            interest_rate=0.5,  # 50% interés
            current_balance=principal,
            turns_until_due=turns,
            creditor_name="Banco Zorvax"
        )
    
    def calculate_interest(self) -> float:
        """Interés ya calculado en materials_owed"""
        return 0  # En MVP no hay interés compuesto adicional
    
    def apply_penalty(self) -> Dict[str, Any]:
        """Aplica penalización: robo de materiales"""
        if not self.is_defaulted:
            return {}
        
        # Penalización: pierde materiales adicionales
        penalty_materials = max(3, self.materials_owed // 10)
        
        return {
            "type": "material_theft",
            "materials_lost": penalty_materials,
            "message": f"Zorvax se lleva {penalty_materials} materiales como penalización"
        }


class KtarDebt(Debt):
    """
    Deuda con los Prestamistas K'tar (MVP)
    
    Características:
        - Interés del 20% (1.2x conversión oxígeno->materiales)
        - Penalización: Reduce oxígeno máximo temporalmente
        - Plazo: 5 turnos (más urgente)
    
    Ejemplo:
        - Pides 50 oxígeno
        - Debes pagar 60 materiales
        - Si no pagas, reduce tu oxígeno máximo
    """
    
    def __init__(self, principal: float, turns: int = 5):
        super().__init__(
            principal=principal,
            interest_rate=0.2,  # 20% interés
            current_balance=principal,
            turns_until_due=turns,
            creditor_name="Prestamistas K'tar"
        )
    
    def calculate_interest(self) -> float:
        """Interés ya calculado en materials_owed"""
        return 0
    
    def apply_penalty(self) -> Dict[str, Any]:
        """Aplica penalización: reduce oxígeno máximo"""
        if not self.is_defaulted:
            return {}
        
        # Penalización: reduce capacidad de oxígeno
        oxygen_reduction = min(10, self.principal * 0.2)
        
        return {
            "type": "oxygen_capacity_reduction",
            "oxygen_lost": oxygen_reduction,
            "message": f"K'tar reduce tu oxígeno máximo en {oxygen_reduction:.0f}"
        }


class NebulaConsortiumDebt(Debt):
    """
    Deuda con el Consorcio Nebulosa (MVP)
    
    Características:
        - Interés del 10% (1.1x conversión oxígeno->materiales)
        - Penalización: Reduce progreso de reparación
        - Plazo: 15 turnos (más flexible)
    
    Ejemplo:
        - Pides 50 oxígeno
        - Debes pagar 55 materiales
        - Si no pagas, pierdes progreso de reparación
    """
    
    def __init__(self, principal: float, turns: int = 15):
        super().__init__(
            principal=principal,
            interest_rate=0.1,  # 10% interés
            current_balance=principal,
            turns_until_due=turns,
            creditor_name="Consorcio Nebulosa"
        )
    
    def calculate_interest(self) -> float:
        """Interés ya calculado en materials_owed"""
        return 0
    
    def apply_penalty(self) -> Dict[str, Any]:
        """Aplica penalización: reduce progreso de reparación"""
        if not self.is_defaulted:
            return {}
        
        # Penalización: pierde progreso de reparación
        repair_loss = min(10, self.principal * 0.1)
        
        return {
            "type": "repair_sabotage",
            "repair_lost": repair_loss,
            "message": f"El Consorcio sabotea tu nave, pierdes {repair_loss:.0f}% de reparación"
        }


class FriendlyDebt(Debt):
    """
    Préstamo de un amigo/aliado (MVP)
    
    Características:
        - Interés del 5% (1.05x conversión oxígeno->materiales)
        - Sin penalizaciones directas
        - Máximo 30 oxígeno
        - Solo disponible una vez
    """
    
    def __init__(self, principal: float, turns: int = 20):
        # Limitar cantidad máxima
        principal = min(principal, 30)
        super().__init__(
            principal=principal,
            interest_rate=0.05,  # 5% interés (casi sin interés)
            current_balance=principal,
            turns_until_due=turns,
            creditor_name="Aliado"
        )
    
    def calculate_interest(self) -> float:
        """Interés mínimo ya calculado"""
        return 0
    
    def apply_penalty(self) -> Dict[str, Any]:
        """Sin penalizaciones directas, solo narrativas"""
        if not self.is_defaulted:
            return {}
        
        return {
            "type": "narrative_only",
            "message": "Tu aliado está decepcionado. No volverá a ayudarte."
        }

