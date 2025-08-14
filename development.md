# Chips Battle 开发文档

## 1. 项目架构

### 1.1 架构核心原则
- **命令驱动 (Command-Driven)**: 核心交互将围绕一个强大的命令行界面(CLI)展开，提供最高效、专业的沉浸式体验。
- **模块化设计 (Modular Design)**: 系统的每一个核心功能都将是独立的、高内聚的模块，严格遵循 models/模块名/模型名.py 的组织方式。
- **数据访问层 (Data Access Layer)**: 业务逻辑与数据库操作将通过严格的DAL和工作单元(Unit of Work)模式进行解耦。
- **事件驱动 (Event-Driven)**: 系统内部的关键活动将通过一个全局的事件总线进行广播和监听，实现模块间的低耦合通信。

### 1.2 技术栈
- **编程语言**: Python 3.8+
- **Web框架**: FastAPI
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **容器化**: Docker
- **测试框架**: pytest

### 1.3 项目结构
```
Chips_Battle/
├── config/                 # 配置文件
├── core/                   # 核心模块
├── models/                 # 数据模型
│   ├── auth/               # 权限认证模型
│   ├── finance/            # 金融系统模型
│   ├── apps/               # 应用市场模型
│   ├── home/               # 家园系统模型
│   └── company/            # 企业经营模型
├── services/               # 业务服务层
├── commands/               # 命令处理模块
├── dal/                    # 数据访问层
├── data/                   # 数据定义文件
│   └── definitions/        # JSON数据定义
├── tests/                  # 测试代码
└── utils/                  # 工具函数
```

## 2. 核心模块设计

### 2.1 时间引擎
```python
# /services/time_service.py

class TimeService:
    """游戏世界的时间引擎"""
    
    def __init__(self, unit_of_work):
        self.unit_of_work = unit_of_work
        self.current_tick = 0
        self.tick_interval = 3600  # 每tick代表1小时
        
    def start(self):
        """启动时间引擎"""
        # 启动定时器，定期推进时间
        pass
        
    def advance_tick(self):
        """推进一个时间tick"""
        self.current_tick += 1
        # 广播时间推进事件
        event_bus.publish(TimeTickEvent(self.current_tick))
        
    def get_game_time(self):
        """获取游戏时间"""
        # 将tick转换为游戏时间
        pass
```

### 2.2 事件总线
```python
# /core/event_bus.py

class EventBus:
    """全局事件总线"""
    
    def __init__(self):
        self._handlers = {}
        
    def subscribe(self, event_type, handler):
        """订阅事件"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    def publish(self, event):
        """发布事件"""
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)
```

### 2.3 数据访问层
```python
# /dal/unit_of_work.py

class UnitOfWork:
    """工作单元模式"""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None
        
    def __enter__(self):
        self.session = self.session_factory()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
        
    def commit(self):
        """提交事务"""
        self.session.commit()
        
    def rollback(self):
        """回滚事务"""
        self.session.rollback()
```

## 3. 金融系统实现

### 3.1 货币系统
```python
# /models/finance/currency.py

class Currency(Base):
    """货币模型"""
    __tablename__ = 'currencies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    code = Column(String(3), unique=True, nullable=False)  # ISO货币代码
    symbol = Column(String(5), nullable=False)
    exchange_rate_to_jcy = Column(Float, nullable=False)   # 对J$的汇率
    
    def convert_to(self, amount, target_currency):
        """货币转换"""
        # 实现货币转换逻辑
        pass
```

### 3.2 银行系统
```python
# /models/finance/bank.py

class BankCard(Base):
    """银行卡模型"""
    __tablename__ = 'bank_cards'
    
    id = Column(Integer, primary_key=True)
    card_number = Column(String(20), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bank_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class BankAccount(Base):
    """银行账户模型"""
    __tablename__ = 'bank_accounts'
    
    id = Column(Integer, primary_key=True)
    card_id = Column(Integer, ForeignKey('bank_cards.id'), nullable=False)
    currency_code = Column(String(3), nullable=False)
    balance = Column(Float, default=0.0)
    account_type = Column(String(20), default='checking')  # savings, checking
```

### 3.3 证券市场
```python
# /models/finance/stock.py

class Stock(Base):
    """股票模型"""
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, nullable=False)
    company_name = Column(String(100), nullable=False)
    current_price = Column(Float, nullable=False)
    pe_ratio = Column(Float)      # 市盈率
    beta = Column(Float)          # 贝塔系数
    dividend_yield = Column(Float) # 股息率
    eps = Column(Float)           # 每股收益
    
    def update_price(self, market_conditions):
        """根据市场条件更新股价"""
        # 实现股价更新逻辑
        pass
```

## 4. 命令系统实现

### 4.1 命令基类
```python
# /commands/base.py

class Command(ABC):
    """命令抽象基类"""
    
    def __init__(self, name, aliases=None, description=""):
        self.name = name
        self.aliases = aliases or []
        self.description = description
        
    @abstractmethod
    def execute(self, args, context):
        """执行命令"""
        pass
        
    def get_help(self):
        """获取命令帮助信息"""
        return f"{self.name}: {self.description}"
```

### 4.2 命令注册与分发
```python
# /services/command_dispatcher.py

class CommandDispatcher:
    """命令分发器"""
    
    def __init__(self, command_registry):
        self.command_registry = command_registry
        
    def dispatch(self, input_text, context):
        """分发命令"""
        parts = input_text.strip().split()
        if not parts:
            return
            
        command_name = parts[0]
        args = parts[1:]
        
        command = self.command_registry.get_command(command_name)
        if command:
            try:
                return command.execute(args, context)
            except Exception as e:
                return f"执行命令时出错: {str(e)}"
        else:
            return f"未知命令: {command_name}"