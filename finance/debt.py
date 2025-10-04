"""
Debt - Sistema de Deudas y Préstamos
Define las clases de deuda y los diferentes tipos de acreedores alienígenas
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class Debt(ABC):
    """
    Clase base abstracta para todos los tipos de deuda
    
    Cada acreedor alienígena tiene sus propias reglas, tasas de interés
    y consecuencias por impago
    
    Atributos:
        principal: Cantidad principal del préstamo
        interest_rate: Tasa de interés (porcentaje por turno)
        current_balance: Balance actual de la deuda
        turns_remaining: Turnos restantes para pagar
        is_defaulted: True si se ha incumplido el pago
    """
    
    principal: float
    interest_rate: float
    current_balance: float
    turns_remaining: int
    is_defaulted: bool = False
    creditor_name: str = "Unknown"
    
    def __post_init__(self):
        """Inicializa el balance actual con el principal"""
        if self.current_balance == 0:
            self.current_balance = self.principal
    
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
    
    def make_payment(self, amount: float) -> bool:
        """
        Realiza un pago hacia la deuda
        
        Args:
            amount: Cantidad a pagar
            
        Returns:
            True si la deuda fue pagada completamente
        """
        # TODO: Reducir current_balance
        # TODO: Verificar si la deuda está saldada
        pass
    
    def advance_turn(self) -> None:
        """Avanza un turno, aplicando intereses"""
        # TODO: Calcular y aplicar intereses
        # TODO: Decrementar turns_remaining
        # TODO: Verificar si se ha incumplido
        pass
    
    def get_minimum_payment(self) -> float:
        """
        Calcula el pago mínimo requerido para este turno
        
        Returns:
            Cantidad mínima a pagar
        """
        # TODO: Implementar cálculo según tipo de acreedor
        pass


class ZorvaxDebt(Debt):
    """
    Deuda con el Banco Zorvax
    
    Características:
        - Interés compuesto estándar
        - Penalizaciones moderadas
        - Aceptan pagos parciales
        - Tasa base: 5% por turno
    
    Penalizaciones:
        - Incremento de tasa de interés
        - Embargo de materiales
    """
    
    creditor_name: str = "Banco Zorvax"
    
    def calculate_interest(self) -> float:
        """Calcula interés compuesto estándar"""
        # TODO: Implementar fórmula de interés compuesto
        pass
    
    def apply_penalty(self) -> dict:
        """Aplica penalizaciones moderadas de Zorvax"""
        # TODO: Incrementar tasa de interés
        # TODO: Posible embargo de materiales
        pass


class KtarDebt(Debt):
    """
    Deuda con los Prestamistas K'tar
    
    Características:
        - Interés simple pero alto
        - Penalizaciones severas e inmediatas
        - No aceptan excusas ni demoras
        - Tasa base: 10% por turno
    
    Penalizaciones:
        - Reducción drástica de oxígeno
        - Sabotaje de reparaciones
        - Pérdida permanente de materiales
    """
    
    creditor_name: str = "Prestamistas K'tar"
    
    def calculate_interest(self) -> float:
        """Calcula interés simple con tasa alta"""
        # TODO: Implementar fórmula de interés simple
        pass
    
    def apply_penalty(self) -> dict:
        """Aplica penalizaciones severas de K'tar"""
        # TODO: Reducir oxígeno significativamente
        # TODO: Reducir progreso de reparación
        # TODO: Confiscar materiales
        pass


class NebulaConsortiumDebt(Debt):
    """
    Deuda con el Consorcio Nebulosa
    
    Características:
        - Interés bajo al principio, crece exponencialmente
        - Muy flexible inicialmente
        - Penalizaciones catastróficas si se incumple
        - Tasa base: 2% por turno (se duplica cada 3 turnos de retraso)
    
    Penalizaciones:
        - Tasa de interés se dispara
        - Bloqueo total de recursos
        - Posible game over inmediato
    """
    
    creditor_name: str = "Consorcio Nebulosa"
    late_payment_turns: int = 0
    
    def calculate_interest(self) -> float:
        """Calcula interés que crece exponencialmente con retrasos"""
        # TODO: Implementar fórmula con crecimiento exponencial
        # TODO: Considerar late_payment_turns
        pass
    
    def apply_penalty(self) -> dict:
        """Aplica penalizaciones catastróficas del Consorcio"""
        # TODO: Duplicar o triplicar tasa de interés
        # TODO: Bloquear recursos
        # TODO: Verificar condición de game over
        pass


class FriendlyDebt(Debt):
    """
    Préstamo de un amigo/aliado
    
    Características:
        - Sin interés o interés muy bajo
        - Sin penalizaciones por retraso
        - Cantidad limitada
        - Solo disponible una vez
    
    Consecuencias:
        - No pagar daña la relación (narrativa)
        - Pérdida de oportunidades futuras
    """
    
    creditor_name: str = "Aliado"
    
    def calculate_interest(self) -> float:
        """Sin interés o muy bajo (0.5%)"""
        # TODO: Implementar interés mínimo o cero
        pass
    
    def apply_penalty(self) -> dict:
        """Sin penalizaciones directas, solo narrativas"""
        # TODO: Marcar evento narrativo
        # TODO: No penalizaciones de recursos
        pass

