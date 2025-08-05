# Full main.py with all initializations and a simple CLI loop

import sys
import tkinter as tk
from gui.terminal import ProfessionalTerminal
from user_manager import UserManager
from core.event_bus import EventBus
from services.time_service import TimeService
from services.currency_service import CurrencyService
from services.command_dispatcher import CommandDispatcher
from services.news_service import NewsService
from services.auth_service import AuthService
from services.app_service import AppService
from services.home_service import HomeService
from services.bank_service import BankService
from services.credit_service import CreditService
from services.mission_service import MissionService
from services.company_service import CompanyService
from services.commodity_service import CommodityService
from services.corporate_warfare_service import CorporateWarfareService
from services.stock_service import StockService
from services.federation_service import FederationService
from services.crypto_service import CryptoService
from commands.crypto_commands import CryptoTradeCommand
from services.alliance_service import AllianceService
from commands.alliance_commands import AllianceCreateCommand
from services.politics_service import PoliticsService
from commands.nation_commands import NationStatusCommand
from services.media_service import MediaService
from commands.media_commands import MediaListCommand
from commands.world.news import NewsCommand
from commands.apps.market import AppMarketCommand
from commands.apps.buy import AppBuyCommand
from commands.home.market import HomeMarketCommand
from commands.bank.status import BankStatusCommand
from commands.corp.create import CorpCreateCommand
from commands.commodity_commands import CommodityTradeCommand
from commands.federation_commands import FederationStatusCommand
# Add other command imports as needed...

class MainApp:
    def __init__(self, root):
        self.root = root
        self.user_manager = UserManager()
        self.dispatcher = CommandDispatcher()
        self.command_processor = self.dispatcher
        
        # Initialize services
        self.event_bus = EventBus()
        self.time_service = TimeService(self.event_bus)
        self.currency_service = CurrencyService()
        self.news_service = NewsService(self.event_bus)
        self.auth_service = AuthService()
        self.app_service = AppService(self.user_manager)
        self.home_service = HomeService(self.event_bus)
        self.bank_service = BankService()
        self.credit_service = CreditService(self.event_bus)
        self.mission_service = MissionService()
        self.company_service = CompanyService()
        self.commodity_service = CommodityService(self.event_bus)
        self.corporate_service = CorporateWarfareService()
        self.stock_service = StockService()
        self.federation_service = FederationService()
        
        # DLC services
        self.crypto_service = CryptoService()
        self.alliance_service = AllianceService()
        self.politics_service = PoliticsService()
        self.media_service = MediaService()
        
        # Register commands
        self.dispatcher.registry.register(NewsCommand())
        self.dispatcher.registry.register(AppMarketCommand())
        self.dispatcher.registry.register(AppBuyCommand())
        self.dispatcher.registry.register(HomeMarketCommand())
        self.dispatcher.registry.register(BankStatusCommand())
        self.dispatcher.registry.register(CorpCreateCommand())
        self.dispatcher.registry.register(CommodityTradeCommand())
        self.dispatcher.registry.register(FederationStatusCommand())
        self.dispatcher.registry.register(CryptoTradeCommand())
        self.dispatcher.registry.register(AllianceCreateCommand())
        self.dispatcher.registry.register(NationStatusCommand())
        self.dispatcher.registry.register(MediaListCommand())
        # Add more registrations...

        self.time_service.start()

if __name__ == "__main__":
    root = tk.Tk()
    main_app = MainApp(root)
    terminal = ProfessionalTerminal(main_app)
    root.mainloop()