from controllers.game_controller import GameController
from views.main_window import StockMarketGameApp
import tkinter as tk
import sys
import os
import json

def load_config(config_file="data/config.json"):
    """加载配置文件"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as file:
                return json.load(file)
        else:
            # 如果配置文件不存在，返回默认配置
            return {
                "game": {"starting_cash": 10000, "max_days": 300},
                "files": {"stocks_file": "data/stocks.json", "news_file": "data/news.json"},
                "ui": {"window_width": 1600, "window_height": 800},
                "simulation": {"news_event_chance": 0.3, "stock_news_chance": 0.2}
            }
    except Exception as e:
        print(f"Error loading config: {e}")
        return {
            "game": {"starting_cash": 10000, "max_days": 300},
            "ui": {"window_width": 1600, "window_height": 800}
        }

def main():
    # 设置控制台输出编码为UTF-8
    if sys.platform.startswith('win'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    # 确保data目录存在
    os.makedirs("data", exist_ok=True)
    
    # 加载配置
    config = load_config()
    
    # Create the root window
    print("[DEBUG] 启动股票模拟器应用")
    root = tk.Tk()
    
    # 设置窗口大小
    if "ui" in config and "window_width" in config["ui"] and "window_height" in config["ui"]:
        window_size = f"{config['ui']['window_width']}x{config['ui']['window_height']}"
        root.geometry(window_size)
    
    # Create the game controller
    print("[DEBUG] 创建游戏控制器")
    controller = GameController("data/config.json")
    
    # Create the main application window
    print("[DEBUG] 创建主应用窗口")
    app = StockMarketGameApp(root)
    
    # Connect the controller to the view
    print("[DEBUG] 连接控制器到视图")
    app.set_controller(controller)
    
    # Update the UI to show initial state
    print("[DEBUG] 更新UI显示初始状态")
    app.update_ui()
    
    # Start the main event loop
    print("[DEBUG] 启动主事件循环")
    root.mainloop()

if __name__ == "__main__":
    main()
