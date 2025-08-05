from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///game.db"  # 默认使用 SQLite
    GAME_VERSION: str = "1.0.0"
    INITIAL_FUNDS: float = 10000.0  # 初始资金
    TICK_INTERVAL: int = 60  # 时间引擎 tick 间隔（秒）

    class Config:
        env_file = ".env"

settings = Settings() 