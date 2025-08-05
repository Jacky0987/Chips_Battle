from core.event_bus import EventBus
from dal.unit_of_work import SqlAlchemyUnitOfWork
from models.bank.credit import CreditProfile

class CreditService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        event_bus.subscribe("LoanRepaidEvent", self.handle_loan_repaid)
        event_bus.subscribe("LoanDefaultedEvent", self.handle_loan_defaulted)

    def handle_loan_repaid(self, data):
        # Increase credit score
        pass

    def handle_loan_defaulted(self, data):
        # Decrease credit score
        pass 