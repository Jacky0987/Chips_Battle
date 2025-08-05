# Integrate from refactor/features/app_market.py

import json
import os
import importlib.util
from dal.unit_of_work import SqlAlchemyUnitOfWork
from models.apps.app import App
from models.apps.ownership import UserAppOwnership
from datetime import datetime

class AppService:
    def __init__(self, user_manager=None):
        self.user_manager = user_manager or object()  # Mock if None
        self.available_apps = self._initialize_apps()
        self.user_apps = {}  # To be loaded per user

    def _initialize_apps(self):
        apps = {}
        config_path = "data/definitions/apps.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for app_config in config.get('apps', []):
                # Load dynamically as in original
                module_name = app_config['module_name']
                class_name = app_config['class_name']
                spec = importlib.util.spec_from_file_location(
                    f"{app_config['app_id']}_app", 
                    os.path.join('apps', f"{module_name}.py")
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                app_class = getattr(module, class_name)
                app_instance = app_class()
                # Update from config
                app_instance.app_id = app_config['app_id']
                app_instance.name = app_config['name']
                app_instance.description = app_config['description']
                app_instance.price = app_config['price']
                app_instance.category = app_config['category']
                apps[app_config['app_id']] = app_instance
        return apps

    def load_user_apps(self, user_id):
        with SqlAlchemyUnitOfWork() as uow:
            ownerships = uow.session.query(UserAppOwnership).filter_by(user_id=user_id).all()
            self.user_apps = {own.app_id: {'install_date': own.install_date} for own in ownerships}

    def install_app(self, user_id, app_id):
        if app_id not in self.available_apps:
            return "App not found"
        app = self.available_apps[app_id]
        # Check cash, deduct, add ownership
        # Simplified
        with SqlAlchemyUnitOfWork() as uow:
            ownership = UserAppOwnership(user_id=user_id, app_id=app_id, install_date=datetime.now())
            uow.session.add(ownership)
            uow.commit()
        return "Installed successfully"

    # Other methods: show_market, run_app, etc. integrated from original 