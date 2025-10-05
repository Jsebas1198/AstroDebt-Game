"""
LoanManager - Gestión Centralizada de Préstamos
Simplificado para MVP: Préstamos en oxígeno, pagos en materiales
"""

from typing import List, Dict, Type, Optional, Any
import random
import logging
from .debt import Debt, ZorvaxDebt, KtarDebt, NebulaConsortiumDebt, FriendlyDebt

logger = logging.getLogger(__name__)


class LoanManager:
    """
    Gestor centralizado de todos los préstamos del juego
    
    Responsabilidades:
        - Mantener lista de préstamos activos
        - Procesar pagos
        - Calcular deuda total
        - Aplicar intereses cada turno
        - Gestionar defaults y penalizaciones
        - Ofrecer nuevos préstamos
    
    Dependencias:
        - finance.debt: Clases de deuda
        - engine.events.EventManager: Para emitir eventos de préstamos
        - engine.state.GameState: Para acceder a recursos del jugador
    """
    
    def __init__(self):
        """Inicializa el gestor de préstamos"""
        self.active_loans: List[Debt] = []
        self.loan_history: List[Debt] = []
        
        # Catálogo de acreedores disponibles
        self.available_creditors: Dict[str, Type[Debt]] = {
            'zorvax': ZorvaxDebt,
            'ktar': KtarDebt,
            'nebula': NebulaConsortiumDebt,
            'friendly': FriendlyDebt
        }
        
        # Límites y restricciones
        self.max_loans = 3  # MVP: máximo 3 préstamos activos
        self.friendly_loan_used = False
        
        # Ofertas pendientes
        self.pending_offer: Optional[Dict[str, Any]] = None
        
        # Referencias a otros componentes (se asignan después)
        self.event_manager = None
        self.game_state = None
        
        logger.info("LoanManager inicializado")
    
    def check_loan_appearance(self) -> Optional[Dict[str, Any]]:
        """
        Verifica si debe aparecer un prestamista según el estado del juego
        
        Returns:
            Diccionario con información de la oferta o None
        """
        if not self.game_state or len(self.active_loans) >= self.max_loans:
            return None
        
        oxygen_level = self.game_state.oxygen
        
        # Probabilidad de aparición según oxígeno
        if oxygen_level < 20:
            # Oxígeno crítico: prestamista obligatorio
            appearance_chance = 1.0
        elif oxygen_level < 50:
            # Oxígeno bajo: 50% de chance
            appearance_chance = 0.5
        else:
            # Oxígeno aceptable: 20% de chance
            appearance_chance = 0.2
        
        if random.random() > appearance_chance:
            return None
        
        # Seleccionar prestamista (MVP: solo Zorvax y K'tar inicialmente)
        if oxygen_level < 20:
            # Situación crítica: Zorvax siempre aparece
            creditor_type = 'zorvax'
        else:
            # Alternar entre Zorvax y K'tar
            creditor_type = random.choice(['zorvax', 'ktar'])
        
        # Calcular cantidad de préstamo ofrecido
        if oxygen_level < 20:
            loan_amount = random.randint(30, 50)  # Préstamo grande en emergencia
        else:
            loan_amount = random.randint(20, 40)  # Préstamo moderado
        
        # Crear oferta
        offer = {
            'creditor_type': creditor_type,
            'amount': loan_amount,
            'creditor_name': self._get_creditor_name(creditor_type),
            'interest_rate': self._get_interest_rate(creditor_type),
            'materials_to_pay': self._calculate_materials_owed(loan_amount, creditor_type),
            'turns_to_pay': self._get_payment_terms(creditor_type)
        }
        
        self.pending_offer = offer
        
        # Emitir evento de aparición de préstamo
        if self.event_manager:
            from engine.events import EventType
            self.event_manager.emit_quick(EventType.LOAN_APPEARED, offer)
        
        logger.info(f"Prestamista aparece: {offer['creditor_name']} ofrece {loan_amount} oxígeno")
        
        return offer
    
    def accept_pending_offer(self) -> bool:
        """
        Acepta la oferta de préstamo pendiente
        
        Returns:
            True si el préstamo fue aceptado exitosamente
        """
        if not self.pending_offer or not self.game_state:
            return False
        
        offer = self.pending_offer
        
        # Crear instancia de deuda según el tipo
        creditor_class = self.available_creditors.get(offer['creditor_type'])
        if not creditor_class:
            logger.error(f"Tipo de acreedor desconocido: {offer['creditor_type']}")
            return False
        
        # Crear el préstamo
        loan = creditor_class(offer['amount'], offer['turns_to_pay'])
        
        # Añadir a préstamos activos
        self.active_loans.append(loan)
        
        # Dar oxígeno al jugador
        self.game_state.update_oxygen(offer['amount'])
        
        # Marcar préstamo amigo como usado si aplica
        if offer['creditor_type'] == 'friendly':
            self.friendly_loan_used = True
        
        # Emitir evento
        if self.event_manager:
            from engine.events import EventType
            self.event_manager.emit_quick(
                EventType.LOAN_ACCEPTED,
                {
                    'creditor': loan.creditor_name,
                    'amount': offer['amount'],
                    'materials_to_pay': loan.materials_owed
                }
            )
        
        logger.info(f"Préstamo aceptado: {offer['amount']} oxígeno de {loan.creditor_name}")
        
        # Limpiar oferta pendiente
        self.pending_offer = None
        
        return True
    
    def reject_pending_offer(self) -> None:
        """Rechaza la oferta de préstamo pendiente"""
        if self.pending_offer:
            logger.info(f"Préstamo rechazado de {self.pending_offer['creditor_name']}")
            
            if self.event_manager:
                from engine.events import EventType
                self.event_manager.emit_quick(
                    EventType.LOAN_REJECTED,
                    {'creditor': self.pending_offer['creditor_name']}
                )
            
            self.pending_offer = None
    
    def make_payment(self, loan: Debt, materials: int) -> bool:
        """
        Realiza un pago hacia un préstamo específico EN MATERIALES
        
        Args:
            loan: Préstamo a pagar
            materials: Cantidad de MATERIALES a pagar
            
        Returns:
            True si el pago fue exitoso
        """
        if not self.game_state or materials <= 0:
            return False
        
        # Verificar que el jugador tiene los materiales
        if self.game_state.materials < materials:
            logger.warning(f"Materiales insuficientes para pago: {materials} requeridos, {self.game_state.materials} disponibles")
            return False
        
        # Consumir materiales
        self.game_state.consume_materials(materials)
        
        # Procesar el pago
        is_paid_off = loan.make_payment(materials)
        
        # Emitir evento
        if self.event_manager:
            from engine.events import EventType
            self.event_manager.emit_quick(
                EventType.LOAN_PAYMENT,
                {
                    'creditor': loan.creditor_name,
                    'materials_paid': materials,
                    'remaining': loan.materials_owed,
                    'paid_off': is_paid_off
                }
            )
        
        # Si está completamente pagado, mover a historial
        if is_paid_off:
            self.active_loans.remove(loan)
            self.loan_history.append(loan)
            logger.info(f"Préstamo de {loan.creditor_name} pagado completamente")
        
        return True
    
    def get_total_debt_in_materials(self) -> int:
        """
        Calcula la deuda total EN MATERIALES de todos los préstamos activos
        
        Returns:
            Suma de todos los materiales adeudados
        """
        return sum(loan.materials_owed for loan in self.active_loans)
    
    def get_minimum_payment_due(self) -> int:
        """
        Calcula el pago mínimo total EN MATERIALES requerido este turno
        
        Returns:
            Suma de todos los pagos mínimos en materiales
        """
        return sum(loan.get_minimum_payment() for loan in self.active_loans)
    
    def process_turn(self) -> None:
        """Procesa el final del turno para todos los préstamos"""
        for loan in self.active_loans:
            loan.advance_turn()
            
            # Verificar si está en default
            if loan.is_defaulted:
                self._apply_loan_penalty(loan)
        
        # Verificar préstamos vencidos
        overdue_loans = [loan for loan in self.active_loans if loan.turns_until_due <= 0 and loan.materials_owed > 0]
        
        for loan in overdue_loans:
            if self.event_manager:
                from engine.events import EventType
                self.event_manager.emit_quick(
                    EventType.LOAN_OVERDUE,
                    {
                        'creditor': loan.creditor_name,
                        'materials_owed': loan.materials_owed
                    }
                )
            logger.warning(f"Préstamo vencido: {loan.creditor_name} espera {loan.materials_owed} materiales")
    
    def _apply_loan_penalty(self, loan: Debt) -> None:
        """
        Aplica la penalización de un préstamo en default
        
        Args:
            loan: Préstamo en default
        """
        if not self.game_state:
            return
        
        penalty = loan.apply_penalty()
        
        if penalty.get('type') == 'material_theft':
            # Zorvax roba materiales
            materials_lost = min(penalty['materials_lost'], self.game_state.materials)
            self.game_state.consume_materials(materials_lost)
            logger.info(f"Penalización aplicada: {penalty['message']}")
            
        elif penalty.get('type') == 'oxygen_capacity_reduction':
            # K'tar reduce oxígeno máximo
            self.game_state.max_oxygen -= penalty['oxygen_lost']
            self.game_state.oxygen = min(self.game_state.oxygen, self.game_state.max_oxygen)
            logger.info(f"Penalización aplicada: {penalty['message']}")
            
        elif penalty.get('type') == 'repair_sabotage':
            # Consorcio reduce progreso de reparación
            self.game_state.update_repair_progress(-penalty['repair_lost'])
            logger.info(f"Penalización aplicada: {penalty['message']}")
        
        # Emitir evento de penalización
        if self.event_manager:
            from engine.events import EventType
            self.event_manager.emit_quick(
                EventType.PENALTY_APPLIED,
                {'creditor': loan.creditor_name, 'penalty': penalty}
            )
    
    def _get_creditor_name(self, creditor_type: str) -> str:
        """Obtiene el nombre del acreedor"""
        names = {
            'zorvax': 'Banco Zorvax',
            'ktar': 'Prestamistas K\'tar',
            'nebula': 'Consorcio Nebulosa',
            'friendly': 'Aliado'
        }
        return names.get(creditor_type, 'Desconocido')
    
    def _get_interest_rate(self, creditor_type: str) -> float:
        """Obtiene la tasa de interés del acreedor"""
        rates = {
            'zorvax': 0.5,  # 50%
            'ktar': 0.2,    # 20%
            'nebula': 0.1,  # 10%
            'friendly': 0.05 # 5%
        }
        return rates.get(creditor_type, 0.5)
    
    def _calculate_materials_owed(self, oxygen_amount: float, creditor_type: str) -> int:
        """Calcula materiales a pagar según oxígeno prestado"""
        rate = self._get_interest_rate(creditor_type)
        return int(oxygen_amount * (1 + rate))
    
    def _get_payment_terms(self, creditor_type: str) -> int:
        """Obtiene el plazo de pago en turnos"""
        terms = {
            'zorvax': 10,
            'ktar': 5,
            'nebula': 15,
            'friendly': 20
        }
        return terms.get(creditor_type, 10)
    
    def can_take_loan(self) -> bool:
        """
        Verifica si el jugador puede tomar más préstamos
        
        Returns:
            True si puede tomar más préstamos
        """
        # Verificar límite de préstamos
        if len(self.active_loans) >= self.max_loans:
            return False
        
        # Verificar si hay demasiados defaults
        defaulted_loans = [loan for loan in self.active_loans if loan.is_defaulted]
        if len(defaulted_loans) >= 2:
            return False
        
        return True
    
    def get_loan_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de todos los préstamos
        
        Returns:
            Diccionario con información resumida de préstamos
        """
        summary = {
            'active_loans': len(self.active_loans),
            'total_debt_materials': self.get_total_debt_in_materials(),
            'minimum_payment': self.get_minimum_payment_due(),
            'defaulted_loans': sum(1 for loan in self.active_loans if loan.is_defaulted),
            'loans': []
        }
        
        for loan in self.active_loans:
            summary['loans'].append({
                'creditor': loan.creditor_name,
                'materials_owed': loan.materials_owed,
                'turns_until_due': loan.turns_until_due,
                'is_defaulted': loan.is_defaulted
            })
        
        return summary

