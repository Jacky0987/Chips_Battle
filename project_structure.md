# Chips Battle Remake v3.0 Alpha - 项目结构设计

## 核心架构原则
- 命令驱动 (Command-Driven)
- 模块化设计 (Modular Design)
- 数据访问层 (Data Access Layer)
- 事件驱动 (Event-Driven)
- UUID用户系统

## 项目目录结构

```
Chips_Battle/
├── main.py                          # 主程序入口
├── requirements.txt                  # 依赖管理
├── README.md                        # 项目说明
│
├── config/                          # 配置中心
│   ├── __init__.py
│   └── settings.py                  # Settings类，管理所有静态配置
│
├── core/                           # 核心系统
│   ├── __init__.py
│   └── event_bus.py                # 全局事件总线
│
├── dal/                            # 数据访问层
│   ├── __init__.py
│   ├── database.py                 # SQLAlchemy引擎和sessionmaker
│   └── unit_of_work.py            # SqlAlchemyUnitOfWork工作单元
│
├── services/                       # 基础引擎服务
│   ├── __init__.py
│   ├── time_service.py             # 游戏时间引擎
│   ├── command_dispatcher.py       # 命令分发器
│   ├── auth_service.py             # 认证服务
│   ├── currency_service.py         # 货币服务
│   ├── app_service.py              # 应用市场服务
│   ├── news_service.py             # 新闻服务
│   └── stock_service.py            # 股票服务
│
├── commands/                       # 命令分发中央处理
│   ├── __init__.py
│   ├── base.py                     # 命令抽象基类
│   ├── registry.py                 # 命令注册器
│   ├── basic/                      # 基础命令
│   │   ├── __init__.py
│   │   ├── help.py
│   │   ├── alias.py
│   │   └── quit.py
│   ├── admin/                      # 管理员命令(DLC)
│   │   ├── __init__.py
│   │   ├── sudo.py
│   │   ├── role.py
│   │   └── user.py
│   ├── apps/                       # 应用市场命令
│   │   ├── __init__.py
│   │   ├── market.py
│   │   └── app.py
│   └── finance/                    # 金融命令
│       ├── __init__.py
│       ├── bank.py
│       └── stock.py
│
├── models/                         # 游戏模块
│   ├── __init__.py
│   ├── auth/                       # 权限与角色系统
│   │   ├── __init__.py
│   │   ├── user.py                 # User模型
│   │   ├── role.py                 # Role模型
│   │   ├── permission.py           # Permission模型
│   │   └── auth_command.py         # 认证相关命令
│   ├── apps/                       # 应用市场模块
│   │   ├── __init__.py
│   │   ├── app.py                  # App模型
│   │   ├── ownership.py            # UserAppOwnership模型
│   │   └── app_command.py          # 应用相关命令
│   ├── finance/                    # 金融模块
│   │   ├── __init__.py
│   │   ├── currency.py             # Currency模型
│   │   ├── account.py              # 银行账户模型
│   │   └── bank_command.py         # 银行相关命令
│   ├── stock/                      # 股票模块
│   │   ├── __init__.py
│   │   ├── stock.py                # Stock模型
│   │   ├── stock_price.py          # StockPrice模型
│   │   ├── portfolio.py            # Portfolio模型
│   │   └── stock_command.py        # 股票相关命令
│   ├── news/                       # 新闻模块
│   │   ├── __init__.py
│   │   ├── news.py                 # News模型
│   │   └── news_command.py         # 新闻相关命令
│   └── achievement/                # 成就系统(预留)
│       ├── __init__.py
│       ├── achievement.py
│       └── achievement_command.py
│
└── data/                           # 数据定义
    ├── definitions/
    │   ├── currencies.json          # 货币定义
    │   ├── apps.json               # 应用定义
    │   ├── jc_stocks.json          # JCMarket股票定义
    │   └── news_templates.json     # 新闻模板
    └── database/
        └── chips_battle.db         # SQLite数据库文件
```

## 核心模块说明

### 1. 配置中心 (config/)
- **settings.py**: 管理所有静态配置，支持环境变量和文件加载

### 2. 核心系统 (core/)
- **event_bus.py**: 全局事件总线，支持publish/subscribe模式

### 3. 数据访问层 (dal/)
- **database.py**: SQLAlchemy引擎初始化
- **unit_of_work.py**: 工作单元模式，封装数据库会话生命周期

### 4. 服务层 (services/)
- **time_service.py**: 游戏时间引擎，每tick=1小时
- **command_dispatcher.py**: 命令解析和分发
- **auth_service.py**: 用户认证和权限验证
- **currency_service.py**: 多币种管理和汇率计算
- **app_service.py**: 应用市场管理
- **news_service.py**: 动态新闻生成
- **stock_service.py**: 股票市场驱动

### 5. 命令系统 (commands/)
- **base.py**: 命令抽象基类
- **registry.py**: 自动发现和注册命令
- **basic/**: help, alias, quit等基础命令
- **admin/**: sudo权限管理命令(DLC设计)
- **apps/**: 应用市场相关命令
- **finance/**: 金融相关命令

### 6. 模型层 (models/)
按功能模块组织，每个模块包含:
- ORM模型定义
- 模块特定的命令处理

### 7. 数据定义 (data/)
- **definitions/**: JSON格式的静态数据定义
- **database/**: 数据库文件

## 技术栈
- **Python 3.8+**
- **SQLAlchemy**: ORM和数据库操作
- **Click**: 命令行界面框架
- **Rich**: 终端美化和表格显示
- **Pydantic**: 数据验证
- **UUID**: 用户标识系统

## 核心特性

### 货币系统
- 主要货币: J$ (Jacky Yuan, JCY)
- 多币种支持，动态汇率

### 命令系统
- 命令驱动交互
- 动态帮助系统
- 权限控制
- 别名支持

### 事件系统
- TimeTickEvent: 时间流逝事件
- NewsPublishedEvent: 新闻发布事件
- 模块间低耦合通信

### 应用市场
- 类Mac OS早期界面风格
- 命令行图形化展示
- 应用购买和管理

### JCMarket股票系统
- 新闻驱动的价格波动
- 真实股票特征模拟
- 投资组合管理

## 开发阶段

### 第一部: 世界基石
1. **第一章**: 核心系统搭建
2. **第二章**: 命令系统和权限管理
3. **第二章Extra**: 应用市场

### 第二部: 第一桶金
4. **第三章**: 金融中枢
5. **第四章**: JCMarket初体验

这个架构设计确保了系统的可扩展性、模块化和维护性，为后续功能开发奠定了坚实的基础。