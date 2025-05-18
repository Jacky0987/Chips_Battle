stock_market_simulator/
│
├── main.py                    # 主入口点
├── full.py                    # 完整版本的代码
│
├── models/                    # 数据模型
│   ├── __init__.py
│   ├── stock.py               # 股票类
│   ├── market.py              # 市场模拟器
│   ├── portfolio.py           # 投资组合管理
│   └── news.py                # 新闻生成
│
├── views/                     # UI组件
│   ├── __init__.py
│   ├── main_window.py         # 主应用窗口
│   ├── charts/                # 图表相关视图
│   │   ├── __init__.py
│   │   ├── price_chart.py     # 股票价格图表
│   │   ├── portfolio_chart.py # 投资组合价值图表
│   │   ├── comparison_chart.py # 性能比较
│   │   └── sector_chart.py    # 行业表现
│   │
│   ├── widgets/               # 自定义小部件
│       ├── __init__.py
│       ├── stock_list.py      # 股票列表表格
│       ├── portfolio_view.py  # 投资组合摘要
│       ├── trading_panel.py   # 交易界面
│       └── news_feed.py       # 新闻提要小部件
│
├── controllers/               # 业务逻辑
│   ├── __init__.py
│   └── game_controller.py     # 主游戏逻辑
│
├── data/                      # 数据文件
│   ├── config.json            # 配置文件
│   ├── stocks.json            # 股票数据
│   └── news.json              # 新闻数据
│
└── utils/                     # 实用函数
    ├── __init__.py
    ├── config.py              # 游戏配置
    └── constants.py           # 游戏常量