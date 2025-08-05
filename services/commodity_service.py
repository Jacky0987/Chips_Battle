import json
from core.event_bus import EventBus
from dal.unit_of_work import SqlAlchemyUnitOfWork
from models.commodities.base_commodity import BaseCommodity

class CommodityService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.commodities = self.load_commodities()
        event_bus.subscribe("TimeTickEvent", self.update_prices)

    def load_commodities(self):
        with open('data/definitions/commodities.json', 'r') as f:
            data = json.load(f)
        commodities = {}
        for item in data:
            comm = BaseCommodity(**item)
            commodities[item['symbol']] = comm
        return commodities

    def update_prices(self, data):
        for comm in self.commodities.values():
            # Update price logic
            pass

    def trade(self, user_id, symbol, action, quantity):
        # Trade logic
        pass 