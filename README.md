# 🚀 JackyCoin股票交易模拟器

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个功能完整的股票交易模拟器，采用专业金融终端界面，提供全方位的投资体验。使用JackyCoin (JCK) 作为游戏内货币，让您在无风险环境中学习投资和交易。

## 📋 目录

- [项目概述](#项目概述)
- [核心特性](#核心特性)
- [系统要求](#系统要求)
- [安装指南](#安装指南)
- [快速开始](#快速开始)
- [功能详解](#功能详解)
- [系统架构](#系统架构)
- [开发指引](#开发指引)
- [贡献指南](#贡献指南)
- [版本历史](#版本历史)

## 🎯 项目概述

这是一个全面的股票交易模拟器，不仅提供基础的股票买卖功能，还包含了银行系统、应用商店、家庭投资理财、成就系统等丰富的模块。用户可以在安全的模拟环境中学习股票交易，体验各种投资策略，并通过多样化的小游戏和分析工具增强学习乐趣。

### 🌟 主要亮点

- **真实交易体验**: 模拟真实股票市场的价格波动和交易机制
- **🌍 大宗商品交易**: ⭐ **全新外汇、期货、现货交易系统，支持51个交易品种**
  - 15个外汇货币对，支持最高100倍杠杆
  - 21个期货合约，涵盖能源、贵金属、农产品、股指
  - 16种现货商品，支持实物交割
- **多元化投资**: 除股票外，还支持ETF基金、豪华车收藏等投资品种
- **银行金融服务**: 完整的银行系统，支持贷款、存款、信用评级等
- **应用生态**: 内置应用商店，提供各种小游戏和分析工具
- **成就系统**: 丰富的成就奖励机制，激励用户深度参与
- **智能分析**: AI辅助的技术分析和投资建议
- **现代界面**: 同时支持命令行和图形界面

## 🚀 核心特性

### 📈 交易系统
- **多种订单类型**: 市价单、限价单、止损单、止盈单
- **做空交易**: 支持做空和平仓操作
- **实时价格**: 动态价格更新和市场事件模拟
- **交易历史**: 完整的交易记录和统计分析

### 🏦 银行系统
- **信贷服务**: 多样化贷款产品，灵活的还款方式
- **存款理财**: 活期、定期存款，不同收益率
- **信用评级**: 动态信用评分系统
- **紧急救助**: 特殊情况下的资金援助
- **银行合约**: 任务系统，完成可获得奖励

### 🏪 应用商店
- **小游戏**: 老虎机、21点、德州扑克、骰子游戏等
- **分析工具**: AI智能分析师、新闻分析器、高级图表分析
- **付费模式**: 一次购买，永久使用
- **使用统计**: 详细的应用使用数据追踪

### 🏠 家庭投资系统
- **ETF基金**: 多种主题基金，专业投资组合
- **豪华车收藏**: 经典跑车投资，独特的另类投资
- **价格波动**: 基于真实市场逻辑的价格变化
- **投资建议**: 智能化的买卖时机提示

### 🏆 成就系统
- **多类别成就**: 交易、盈利、风险管理、银行业务等
- **等级系统**: 经验值和等级提升机制
- **奖励机制**: 丰富的现金和经验奖励
- **隐藏成就**: 特殊条件触发的稀有成就

### 📊 分析功能
- **技术分析**: RSI、MACD、布林带等技术指标
- **市场分析**: 行业分析、市场情绪、经济日历
- **图表工具**: 多种图表类型，可视化数据展示
- **风险评估**: 投资组合风险分析和建议

## 💻 系统要求

### 基础要求
- Python 3.8+
- Windows 10/11, macOS 10.14+, 或 Linux

### 依赖库
```
tkinter (内置)
cryptography>=3.0.0
```

### 可选依赖
```
matplotlib>=3.3.0  # 用于高级图表功能
numpy>=1.19.0      # 用于数据分析
```

## 🔧 安装指南

### 1. 克隆项目
```bash
git clone https://github.com/your-username/stock-trading-simulator.git
cd stock-trading-simulator
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 运行程序
```bash
python main.py
```

## 🎮 快速开始

### 首次运行
1. 启动程序后会出现登录界面
2. 新用户点击"注册"创建账户
3. 登录成功后进入主界面

### 基础操作
```bash
# 查看帮助
help

# 查看账户余额
balance

# 查看股票列表
list

# 买入股票
buy AAPL 10

# 卖出股票  
sell AAPL 5

# 查看投资组合
portfolio

# 查看交易历史
history
```

### 高级功能
```bash
# 限价买入
limit_buy MSFT 10 300

# 做空操作
short TSLA 5

# 设置止损
stop_loss AAPL 10 140

# 🌍 大宗商品交易 (新功能)
commodity                    # 查看市场概览
forex buy EURUSD 0.1 leverage=100   # 外汇交易
futures buy CL2501 1         # 期货交易
spot buy XAUUSD_SPOT 10     # 现货交易

# 银行服务
bank
bank loan 10000 30
bank deposit 5000 short

# 应用商店
appmarket

# 家庭投资
home
```

## 📖 功能详解

### 交易系统详解

#### 订单类型
1. **市价单**: 立即按当前市价执行
2. **限价单**: 指定价格，达到时自动执行
3. **止损单**: 价格跌破指定点位时卖出
4. **止盈单**: 价格达到目标价位时卖出

#### 做空机制
- 借入股票卖出，期待价格下跌
- 需要支付借股费用
- 平仓时买回股票归还

### 银行系统详解

#### 贷款产品
- **短期贷款**: 7-30天，利率较高
- **中期贷款**: 1-6个月，利率适中  
- **长期贷款**: 6个月以上，利率较低

#### 存款产品
- **活期存款**: 随时支取，利率最低
- **短期定存**: 1个月，利率较低
- **中期定存**: 3个月，利率适中
- **长期定存**: 6个月，利率最高

### 应用商店详解

#### 游戏应用
- **老虎机**: 经典的运气游戏，多种奖金组合
- **21点**: 与AI对战的纸牌游戏
- **德州扑克**: 策略性较强的扑克游戏
- **骰子游戏**: 简单的猜大小游戏

#### 分析工具
- **AI智能分析师**: 综合技术指标分析
- **新闻分析器**: 市场新闻和事件分析
- **高级图表分析**: 专业级GUI图表工具，支持K线图、技术指标、实时更新等

### 管理员功能详解

系统内置强大的管理员功能，支持全方位的系统管理：

#### 用户管理
```bash
sudo user list                    # 查看所有用户
sudo user info john               # 查看用户详细信息
sudo user cash john 50000         # 修改用户资金
sudo user level john 10           # 修改用户等级
sudo user exp john 5000           # 修改用户经验值
sudo user credit john AAA         # 修改银行信用等级
sudo user ban john                # 封禁用户
sudo user unban john              # 解封用户
```

#### 股票管理
```bash
sudo stock add TSLA Tesla 250.00 Technology    # 添加新股票
sudo stock remove AAPL                         # 删除股票
sudo stock price MSFT 300.00                   # 修改股票价格
sudo stock info AAPL                           # 查看股票详细信息
sudo stock list                                # 列出所有股票
sudo stock volatility TSLA 0.05                # 修改股票波动率
```

#### 银行管理
```bash
sudo bank rates loan 0.08          # 修改贷款基础利率
sudo bank rates deposit 0.03       # 修改存款基础利率
sudo bank credit john AAA          # 修改用户信用等级
sudo bank loan john 50000 30       # 强制发放贷款
sudo bank forgive john LOAN_001    # 免除贷款
```

#### 系统管理
```bash
sudo system event "央行降息，市场大涨"    # 创建市场事件
sudo system reset market                   # 重置市场价格
sudo system backup                         # 备份系统数据
sudo system maintenance on                 # 开启维护模式
```

#### 权限说明
- **用户等级修改**: 可设置1-100级，影响经验值和成就进度
- **信用等级**: AAA、AA、A、BBB、BB、B、CCC、CC、C、D十个等级
- **强制贷款**: 无视信用限制和还款能力强制发放
- **系统备份**: 自动备份用户数据和系统配置

## 🏗️ 系统架构

```
CLI/
├── main.py                 # 程序入口
├── app.py                  # 主应用类
├── login_window.py         # 登录界面
├── user_manager.py         # 用户管理
├── core/                   # 核心系统
│   ├── trading_engine.py   # 交易引擎
│   ├── market_data.py      # 市场数据管理
│   ├── achievement_system.py # 成就系统
│   └── multi_asset_engine.py # 多资产引擎
├── features/               # 功能模块
│   ├── app_market.py       # 应用商店
│   └── analysis.py         # 分析功能
├── home/                   # 家庭投资系统
│   ├── base_asset.py       # 资产基类
│   ├── etf_funds.py        # ETF基金
│   └── luxury_cars.py      # 豪华车收藏
├── apps/                   # 应用生态
│   ├── base_app.py         # 应用基类
│   ├── slot_machine.app.py # 老虎机应用
│   ├── blackjack.app.py    # 21点应用
│   ├── texas_holdem.app.py # 德州扑克应用
│   ├── dice.app.py         # 骰子游戏应用
│   ├── poker_game.app.py   # 扑克游戏应用
│   ├── ai_analysis.app.py  # AI分析应用
│   ├── news_analyzer.app.py # 新闻分析应用
│   └── advanced_chart.app.py # 高级图表应用
├── gui/                    # 图形界面
│   └── main_window.py      # 主窗口
├── bank/                   # 银行系统
│   ├── bank_manager.py     # 银行管理器
│   ├── bank_types.py       # 银行类型定义
│   ├── credit_system.py    # 信用评级系统
│   └── task_system.py      # 银行任务系统
├── company/                # 公司系统
│   ├── company_manager.py  # 公司管理器
│   └── company_types.py    # 公司类型定义
├── commands/               # 命令系统
│   ├── command_processor.py # 命令处理器
│   └── help_system.py      # 帮助系统
├── utils/                  # 工具模块
│   └── chart_tools.py      # 图表工具
├── data/                   # 数据文件
│   ├── stocks.json         # 股票数据
│   ├── achievements.json   # 成就定义
│   └── market_events.json  # 市场事件
└── admin/                  # 管理员模块
    └── admin_manager.py    # 管理员功能
```

### 核心设计模式

1. **MVC架构**: 模型-视图-控制器分离
2. **策略模式**: 不同交易策略的实现
3. **观察者模式**: 市场事件和价格更新
4. **工厂模式**: 应用和资产的创建
5. **命令模式**: 用户操作的命令化处理

## 🚀 开发指引

### 短期开发方向 (1-3个月)

#### 1. 市场机制优化
- **期权交易**: 添加期权买卖功能
- **期货交易**: 商品期货和股指期货
- **外汇交易**: 主要货币对交易
- **数字货币**: 比特币等加密货币模拟

#### 2. 数据分析增强
- **机器学习**: 股价预测模型
- **情绪分析**: 新闻和社交媒体情绪指标
- **量化策略**: 内置量化交易策略
- **回测系统**: 策略历史表现回测

#### 3. 社交功能
- **好友系统**: 添加好友，查看朋友投资组合
- **聊天室**: 实时交流和讨论
- **投资比赛**: 定期举办投资竞赛
- **策略分享**: 分享和订阅投资策略

### 中期开发方向 (3-6个月)

#### 1. 高级交易工具
- **算法交易**: 自定义交易算法
- **套利工具**: 跨市场套利机会识别
- **风险管理**: 高级风险控制工具
- **组合优化**: 马科维茨投资组合理论应用

#### 2. 教育系统
- **交易课程**: 结构化的交易教育内容
- **模拟考试**: 投资知识测试
- **导师系统**: AI或人工导师指导
- **学习路径**: 个性化学习建议

#### 3. 移动端支持
- **Web版本**: 基于Web的交易界面
- **移动应用**: 原生移动应用开发
- **云同步**: 跨设备数据同步
- **推送通知**: 重要市场事件通知

### 长期开发方向 (6个月+)

#### 1. 人工智能集成
- **智能顾问**: AI投资顾问服务
- **个性化推荐**: 基于用户行为的投资建议
- **自动化交易**: 完全自动化的交易机器人
- **自然语言处理**: 语音和文字交易指令

#### 2. 区块链集成
- **NFT交易**: 数字艺术品投资
- **DeFi模拟**: 去中心化金融产品
- **智能合约**: 自动化投资合约
- **代币经济**: 平台内代币激励机制

#### 3. 大数据分析
- **实时数据**: 真实市场数据接入
- **大数据处理**: 处理海量市场数据
- **云计算**: 利用云服务提升性能
- **API服务**: 对外提供数据和服务API

### 技术栈升级建议

#### 前端技术
```
React/Vue.js    # 现代化Web前端
React Native    # 跨平台移动应用
Electron        # 桌面应用
WebGL          # 3D图表和可视化
```

#### 后端技术
```
FastAPI/Django  # 高性能Web框架
Redis          # 缓存和会话管理
PostgreSQL     # 关系型数据库
MongoDB        # 文档数据库
Kafka          # 消息队列
```

#### 数据科学
```
pandas         # 数据处理
scikit-learn   # 机器学习
TensorFlow     # 深度学习
Apache Spark   # 大数据处理
Jupyter        # 数据分析环境
```

#### 部署和运维
```
Docker         # 容器化部署
Kubernetes     # 容器编排
AWS/Azure      # 云服务
Prometheus     # 监控和告警
ELK Stack      # 日志分析
```

### 代码质量提升

#### 1. 测试覆盖
- **单元测试**: 核心功能单元测试
- **集成测试**: 模块间集成测试
- **性能测试**: 压力和性能测试
- **UI测试**: 用户界面自动化测试

#### 2. 代码规范
- **类型提示**: 完整的Python类型注解
- **文档字符串**: 详细的API文档
- **代码格式化**: Black、isort等工具
- **静态分析**: pylint、mypy等工具

#### 3. 架构优化
- **微服务**: 拆分为独立的微服务
- **异步处理**: 使用asyncio提升性能
- **缓存策略**: 多级缓存优化
- **数据库优化**: 查询优化和索引设计

## 🤝 贡献指南

### 开发环境设置
```bash
# 1. Fork项目
# 2. 克隆你的fork
git clone https://github.com/your-username/stock-trading-simulator.git

# 3. 创建开发分支
git checkout -b feature/your-feature-name

# 4. 安装开发依赖
pip install -r requirements-dev.txt

# 5. 运行测试
python -m pytest tests/

# 6. 提交变更
git commit -m "Add: your feature description"

# 7. 推送到你的fork
git push origin feature/your-feature-name

# 8. 创建Pull Request
```

### 代码贡献指南
1. **功能开发**: 新功能需要有对应的测试
2. **Bug修复**: 修复需要包含重现步骤
3. **文档更新**: 代码变更需要更新相关文档
4. **代码风格**: 遵循项目的代码规范

### 提交消息规范
```
类型(作用域): 简短描述

详细描述(可选)

closes #issue_number
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

## 📚 文档和资源

### 用户文档
- [用户手册](docs/user-guide.md)
- [交易指南](docs/trading-guide.md)
- [API参考](docs/api-reference.md)

### 开发文档
- [架构设计](docs/architecture.md)
- [开发指南](docs/development.md)
- [API文档](docs/api-docs.md)

### 教程和示例
- [快速入门教程](tutorials/quickstart.md)
- [高级交易策略](tutorials/advanced-strategies.md)
- [应用开发指南](tutorials/app-development.md)

## 📈 版本历史

### v2.0.0 (当前版本)
- ✨ 新增应用商店系统
- ✨ 新增家庭投资理财模块
- ✨ 完善银行金融服务
- ✨ 增强成就和等级系统
- 🔧 优化用户界面和交互体验
- 🐛 修复多个已知问题

### v1.5.0
- ✨ 新增银行系统
- ✨ 新增高级交易功能
- 🔧 改进市场数据管理
- 🔧 优化性能和稳定性

### v1.0.0
- 🎉 初始版本发布
- ✨ 基础交易功能
- ✨ 用户管理系统
- ✨ 简单的成就系统

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙋‍♂️ 支持和反馈

### 获取帮助
- 📧 邮箱: support@trading-simulator.com
- 💬 讨论: [GitHub Discussions](https://github.com/your-username/stock-trading-simulator/discussions)
- 🐛 Bug报告: [GitHub Issues](https://github.com/your-username/stock-trading-simulator/issues)

### 社区
- 🌟 给项目点Star支持我们
- 🔗 分享给朋友和同事
- 💡 提出新功能建议
- 🤝 参与代码贡献

---

**感谢您使用股票交易模拟器！** 🚀

如果这个项目对您有帮助，请考虑给我们一个 ⭐️ Star！ 

### 应用商店系统

模拟器内置应用商店，提供各种小游戏和分析工具：

```bash
# 查看应用商店
appmarket

# 安装应用 (使用应用ID)
install slot_machine      # 安装老虎机游戏 ($5,000)
install blackjack         # 安装21点游戏 ($8,000)  
install ai_analysis       # 安装AI分析工具 ($15,000)

# 运行已安装的应用
appmarket.app slot_machine 100        # 玩老虎机，投注$100
appmarket.app blackjack 500           # 玩21点，投注$500
appmarket.app ai_analysis AAPL        # AI分析苹果股票

# 管理应用
appmarket my               # 查看已安装应用
appmarket usage            # 查看使用统计
uninstall dice_game        # 卸载应用
```

**可用应用ID：**
- 游戏娱乐: `slot_machine`, `blackjack`, `texas_holdem`, `dice_game`, `poker_game`
- 分析工具: `ai_analysis`, `news_analyzer`, `advanced_chart`

#### 🆕 高级图表分析工具 (advanced_chart)

**特色功能：**
- 📊 **独立GUI窗口**: 专业的图表显示界面
- 📈 **多种图表类型**: K线图、线型图、成交量图、技术指标图
- 🔧 **技术指标**: MA移动平均线、BOLL布林带、MACD、RSI、KDJ等
- ⏰ **实时更新**: 30秒自动刷新数据
- 💾 **图表导出**: 保存为高清PNG图片
- 🖱️ **交互操作**: 缩放、平移、数据点查看
- 📊 **多时间框架**: 1天到1年的历史数据

**使用示例：**
```bash
# 启动苹果公司的K线图
appmarket.app advanced_chart AAPL

# 查看特斯拉的技术指标图
appmarket.app advanced_chart TSLA indicators

# 分析微软的成交量
appmarket.app advanced_chart MSFT volume

# 线型图查看谷歌股价
appmarket.app advanced_chart GOOGL line
```

**图表窗口快捷键：**
- `F5` - 刷新数据
- `Ctrl+S` - 保存图表
- `ESC` - 关闭窗口

**💰 应用价格：** $20,000 (一次购买，永久使用) 