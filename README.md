# Chips Battle Remake v3.0 Alpha

一个现代化的命令行游戏，基于经典的 Chips Battle 重制而成。采用 Python 异步架构，提供丰富的游戏体验和扩展性。

## 🎮 游戏特色

- **命令驱动**: 通过输入命令与游戏世界互动
- **多货币系统**: 支持 JCC、CNY、USD、EUR 等多种货币
- **股票市场**: 模拟真实的股票交易系统
- **应用市场**: 创建和发布自己的应用程序
- **新闻系统**: 实时的游戏世界新闻和事件
- **用户系统**: 完整的用户注册、认证和权限管理
- **事件驱动**: 基于事件总线的松耦合架构

## 🏗️ 技术架构

### 核心技术栈
- **Python 3.8+**: 主要开发语言
- **SQLAlchemy**: ORM 和数据库抽象层
- **Rich**: 终端 UI 和文本渲染
- **Pydantic**: 数据验证和设置管理
- **Asyncio**: 异步编程支持

### 架构设计
```
├── config/          # 配置管理
├── core/            # 核心系统（事件总线等）
├── dal/             # 数据访问层
├── models/          # 数据模型
├── services/        # 业务逻辑服务
├── commands/        # 命令系统
├── migrations/      # 数据库迁移
└── main.py          # 应用入口
```

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- pip 包管理器

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd Chips_Battle
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **初始化数据库**
   ```bash
   python migrations/init_db.py
   ```

4. **启动游戏**
   ```bash
   python main.py
   ```

### 首次登录

数据库初始化后会自动创建管理员账户：
- **用户名**: `admin`
- **密码**: `admin123`

⚠️ **重要**: 请在首次登录后立即更改密码！

## 🎯 游戏指南

### 基础命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `help` | 显示帮助信息 | `help`, `help wallet` |
| `status` | 查看当前状态 | `status` |
| `profile` | 管理个人资料 | `profile`, `profile edit` |
| `quit` | 退出游戏 | `quit`, `quit --force` |

### 财务命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `wallet` | 查看钱包余额 | `wallet`, `wallet CNY` |
| `transfer` | 转账给其他用户 | `transfer user123 1000 CNY` |
| `exchange` | 货币兑换 | `exchange CNY USD 1000` |

### 股票命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `market` | 查看股票市场 | `market`, `market AAPL` |
| `buy` | 购买股票 | `buy AAPL 100` |
| `sell` | 出售股票 | `sell AAPL 50` |
| `portfolio` | 查看投资组合 | `portfolio` |

### 应用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `apps` | 浏览应用市场 | `apps`, `apps search game` |
| `install` | 安装应用 | `install app123` |
| `create` | 创建新应用 | `create "My App"` |

## 🔧 开发指南

### 项目结构详解

#### 配置系统 (`config/`)
- `settings.py`: 全局配置管理，支持环境变量和文件配置

#### 核心系统 (`core/`)
- `event_bus.py`: 事件总线，支持发布-订阅模式

#### 数据访问层 (`dal/`)
- `database.py`: 数据库引擎和连接管理
- `unit_of_work.py`: 工作单元模式实现

#### 数据模型 (`models/`)
- `base.py`: 基础模型类和混入
- `auth/`: 认证相关模型（用户、角色、权限）

#### 服务层 (`services/`)
- `auth_service.py`: 认证和授权服务
- `command_dispatcher.py`: 命令分发器
- `time_service.py`: 游戏时间管理

#### 命令系统 (`commands/`)
- `base.py`: 命令基类和解析器
- `registry.py`: 命令注册器
- `basic/`: 基础命令实现

### 添加新命令

1. **创建命令类**
   ```python
   from commands.base import BasicCommand, CommandResult, CommandContext
   
   class MyCommand(BasicCommand):
       def __init__(self):
           super().__init__()
           self.name = "mycommand"
           self.description = "我的自定义命令"
       
       async def execute(self, args, context):
           return self.success("命令执行成功！")
   ```

2. **注册命令**
   ```python
   # 在适当的模块中注册命令
   from commands.registry import CommandRegistry
   
   registry = CommandRegistry()
   registry.register(MyCommand())
   ```

### 添加新服务

1. **创建服务类**
   ```python
   class MyService:
       def __init__(self, uow, event_bus):
           self.uow = uow
           self.event_bus = event_bus
       
       async def do_something(self):
           # 业务逻辑
           pass
   ```

2. **在主应用中注册**
   ```python
   # 在 main.py 中添加服务初始化
   self.my_service = MyService(self.uow, self.event_bus)
   ```

## 🗄️ 数据库管理

### 初始化数据库
```bash
python migrations/init_db.py
```

### 重置数据库
```bash
python migrations/init_db.py --reset
```

### 数据库配置

默认使用 SQLite 数据库，配置文件位于 `config/settings.py`：

```python
class DatabaseConfig:
    driver: str = "sqlite+aiosqlite"
    name: str = "chips_battle.db"
    # 其他配置...
```

## 🔐 权限系统

### 角色层级
1. **admin**: 系统管理员，拥有所有权限
2. **moderator**: 版主，拥有内容管理权限
3. **user**: 普通用户，基础功能权限
4. **guest**: 访客，只读权限

### 权限类型
- **system.***: 系统管理权限
- **content.***: 内容管理权限
- **finance.***: 财务操作权限
- **user.***: 用户操作权限

## 🎨 自定义配置

### 环境变量
```bash
# 数据库配置
DB_NAME=my_game.db
DB_ECHO=true

# 游戏配置
GAME_INITIAL_MONEY=10000
GAME_MAX_LEVEL=100

# 安全配置
SECURITY_PASSWORD_MIN_LENGTH=8
SECURITY_SESSION_TIMEOUT=3600
```

### 配置文件
创建 `.env` 文件来覆盖默认配置：
```env
DB_NAME=production.db
GAME_INITIAL_MONEY=5000
LOG_LEVEL=INFO
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试
python -m pytest tests/test_auth.py

# 生成覆盖率报告
python -m pytest --cov=. --cov-report=html
```

## 📝 日志

日志文件位于 `logs/` 目录：
- `app.log`: 应用日志
- `error.log`: 错误日志
- `debug.log`: 调试日志（开发模式）

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- 使用 Black 进行代码格式化
- 遵循 PEP 8 编码规范
- 添加适当的类型注解
- 编写单元测试

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果你遇到问题或有建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索现有的 [Issues](../../issues)
3. 创建新的 Issue
4. 加入我们的讨论群

## 🗺️ 路线图

### v3.0 Alpha (当前版本)
- [x] 基础架构搭建
- [x] 用户认证系统
- [x] 命令系统框架
- [x] 数据库设计
- [ ] 基础命令实现
- [ ] 财务系统

### v3.0 Beta
- [ ] 股票市场系统
- [ ] 应用市场
- [ ] 新闻系统
- [ ] Web 界面

### v3.0 正式版
- [ ] 多人在线功能
- [ ] 实时通信
- [ ] 移动端支持
- [ ] 插件系统

---

**Chips Battle Remake** - 重新定义命令行游戏体验 🎮