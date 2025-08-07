# -*- coding: utf-8 -*-
"""
游戏配置中心

管理所有静态配置，支持从环境变量和文件加载。
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class Settings:
    """游戏配置类"""
    
    def __init__(self, env_file: Optional[str] = None):
        """初始化配置
        
        Args:
            env_file: 环境变量文件路径，默认为项目根目录的.env文件
        """
        # 加载环境变量
        if env_file:
            load_dotenv(env_file)
        else:
            # 尝试加载项目根目录的.env文件
            project_root = Path(__file__).parent.parent
            env_path = project_root / ".env"
            if env_path.exists():
                load_dotenv(env_path)
        
        # 项目信息
        self.PROJECT_NAME = "Chips Battle Remake"
        self.VERSION = "3.0.0-alpha"
        self.DESCRIPTION = "命令驱动的金融模拟游戏"
        
        # 路径配置
        self.PROJECT_ROOT = Path(__file__).parent.parent
        self.DATA_DIR = self.PROJECT_ROOT / "data"
        self.DATABASE_DIR = self.DATA_DIR / "database"
        self.DEFINITIONS_DIR = self.DATA_DIR / "definitions"
        
        # 确保目录存在
        self.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
        self.DEFINITIONS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 数据库配置
        self.DATABASE_URL = os.getenv(
            "DATABASE_URL", 
            f"sqlite:///{self.DATABASE_DIR / 'chips_battle.db'}"
        )
        self.DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"
        
        # 游戏配置
        self.GAME_TICK_INTERVAL = int(os.getenv("GAME_TICK_INTERVAL", "60"))  # 秒
        self.GAME_HOURS_PER_TICK = int(os.getenv("GAME_HOURS_PER_TICK", "1"))  # 游戏小时
        
        # 货币配置
        self.BASE_CURRENCY = os.getenv("BASE_CURRENCY", "JCY")  # Jacky Yuan
        self.BASE_CURRENCY_SYMBOL = os.getenv("BASE_CURRENCY_SYMBOL", "J$")
        self.BASE_CURRENCY_NAME = os.getenv("BASE_CURRENCY_NAME", "Jacky Yuan")
        
        # 初始资金配置
        self.INITIAL_BALANCE = float(os.getenv("INITIAL_BALANCE", "10000.0"))  # J$
        
        # 股票市场配置
        self.STOCK_MARKET_NAME = os.getenv("STOCK_MARKET_NAME", "JCMarket")
        self.STOCK_PRICE_UPDATE_INTERVAL = int(os.getenv("STOCK_PRICE_UPDATE_INTERVAL", "5"))  # 分钟
        self.STOCK_VOLATILITY_BASE = float(os.getenv("STOCK_VOLATILITY_BASE", "0.02"))  # 2%
        
        # 新闻系统配置
        self.NEWS_GENERATION_PROBABILITY = float(os.getenv("NEWS_GENERATION_PROBABILITY", "0.3"))  # 30%
        self.NEWS_IMPACT_MULTIPLIER = float(os.getenv("NEWS_IMPACT_MULTIPLIER", "1.5"))
        
        # 应用市场配置
        self.APP_MARKET_NAME = os.getenv("APP_MARKET_NAME", "ChipsApp Store")
        
        # 安全配置
        self.SECRET_KEY = os.getenv("SECRET_KEY", "chips-battle-secret-key-change-in-production")
        self.PASSWORD_HASH_ALGORITHM = os.getenv("PASSWORD_HASH_ALGORITHM", "bcrypt")
        
        # 日志配置
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv(
            "LOG_FORMAT", 
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # 开发配置
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.TESTING = os.getenv("TESTING", "false").lower() == "true"
        
        # 命令系统配置
        self.COMMAND_HISTORY_SIZE = int(os.getenv("COMMAND_HISTORY_SIZE", "100"))
        self.COMMAND_TIMEOUT = int(os.getenv("COMMAND_TIMEOUT", "30"))  # 秒
        
        # 权限配置
        self.DEFAULT_USER_ROLE = os.getenv("DEFAULT_USER_ROLE", "player")
        self.ADMIN_ROLE = os.getenv("ADMIN_ROLE", "admin")
        
        # 事件系统配置
        self.EVENT_QUEUE_SIZE = int(os.getenv("EVENT_QUEUE_SIZE", "1000"))
        
        # 汇率更新配置
        self.EXCHANGE_RATE_UPDATE_INTERVAL = int(os.getenv("EXCHANGE_RATE_UPDATE_INTERVAL", "60"))  # 分钟
        self.EXCHANGE_RATE_VOLATILITY = float(os.getenv("EXCHANGE_RATE_VOLATILITY", "0.01"))  # 1%
    
    def get_database_url(self) -> str:
        """获取数据库连接URL"""
        return self.DATABASE_URL
    
    def get_data_file_path(self, filename: str) -> Path:
        """获取数据文件路径
        
        Args:
            filename: 文件名
            
        Returns:
            完整的文件路径
        """
        return self.DEFINITIONS_DIR / filename
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.DEBUG or self.TESTING
    
    def __repr__(self) -> str:
        return f"<Settings(project={self.PROJECT_NAME}, version={self.VERSION})>"