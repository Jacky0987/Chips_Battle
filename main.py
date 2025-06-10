from app import StockTradingApp

if __name__ == "__main__":
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("请安装加密库: pip install cryptography")
        exit(1)

    app = StockTradingApp()
    app.run()
