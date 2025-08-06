# **《芯片战争》终极开发文档 (v5.0)**

## **序章：创世史诗 (Prologue: The Genesis Epic)**

### **核心世界观**

玩家并非凡人，而是一位在未来“芯片战争”的终极对决中失败，却意外重生回到战争黎明期的“先知”。凭借对未来几十年的重大科技突破、市场脉络、关键人才的记忆，玩家拥有了改写历史、铸造传奇的唯一机会。

**最终目标**: 玩家的使命并非简单地积累财富，而是要亲手建立一个横跨全球的商业帝国，整合支离破碎的全球经济，最终废除所有主权货币，铸造统一的“星际联邦信用点 (FED$)”，为人类文明迈向星辰大海的未来铺平最后的道路。这既是游戏的终极胜利条件，也是“先知”的天命所在。

### **架构核心原则**

*   **命令驱动 (Command-Driven)**: 核心交互将围绕一个强大的命令行界面(CLI)展开，提供最高效、专业的沉浸式体验。
*   **模块化设计 (Modular Design)**: 系统的每一个核心功能都将是独立的、高内聚的模块，严格遵循 `models/模块名/模型名.py` 的组织方式。
*   **数据访问层 (Data Access Layer)**: 业务逻辑与数据库操作将通过严格的DAL和工作单元(Unit of Work)模式进行解耦。
*   **事件驱动 (Event-Driven)**: 系统内部的关键活动将通过一个全局的事件总线进行广播和监听，实现模块间的低耦合通信。

---

## **第一部：世界基石 (The Foundation)**

*   **游戏流程阶段**: 游戏启动前的核心架构搭建。此阶段为所有后续功能提供稳固的技术地基，创造一个“活”的世界框架。

### **第一章：创世与核心系统 (Genesis & Core Systems)**

**目标**: 搭建项目的骨架，建立驱动时间流逝的引擎、模块间通信的总线，以及最底层的配置和数据库访问机制。

**技术实现要点**:

1.  **项目结构初始化**:
    *   创建核心目录：`/config`, `/core`, `/models`, `/services`, `/commands`, `/data/definitions`, `/dal`。
2.  **配置中心 (`/config/settings.py`)**:
    *   定义 `Settings` 类，管理所有静态配置，并支持从环境变量或文件加载。
3.  **数据访问层 (DAL)**:
    *   **数据库引擎 (`/dal/database.py`)**: 初始化SQLAlchemy的engine和sessionmaker。
    *   **工作单元 (`/dal/unit_of_work.py`)**: 实现 `SqlAlchemyUnitOfWork`，封装数据库会话的生命周期，作为所有服务操作数据库的唯一入口。
4.  **时间引擎 (`/services/time_service.py`)**:
    *   创建 `TimeService` 作为游戏世界的主时钟，以固定的“tick”推进游戏时间（例如，每tick=1小时），并广播 `TimeTickEvent`。
5.  **事件总线 (`/core/event_bus.py`)**:
    *   实现一个全局的 `EventBus`，允许系统任何部分 `publish(event)` 一个事件，也允许任何服务 `subscribe(event_type, handler)` 来监听和处理，实现模块解耦。

### **第二章：神谕与身份 (The Oracle & Identity)**

**目标**: 构建玩家与游戏世界交互的桥梁——命令系统，并建立一个健壮、可扩展的权限与角色系统，为游戏管理和未来扩展奠定基础。

**技术实现要点**:

1.  **命令处理系统**:
    *   **命令抽象 (`/commands/base.py`)**: 定义抽象基类 `Command`，包含 `name`, `aliases`, `description` 和 `execute()` 方法。
    *   **注册与分发 (`/commands/registry.py`, `/services/command_dispatcher.py`)**: 创建 `CommandRegistry` 自动发现并注册所有命令，`CommandDispatcher` 负责解析用户输入并分发给相应的命令对象执行。
2.  **基础元命令**:
    *   实现 `help`, `alias`, `quit` 等基础命令，为玩家提供基本的交互能力。
3.  **权限与角色 (Auth System)**:
    *   **核心模型 (`/models/auth/`)**:
        *   `User`: 基础用户模型，增加 `role_id` 外键。
        *   `Role`: 定义角色 (e.g., "player", "admin")。
        *   `Permission`: 定义细粒度的权限 (e.g., "command.admin.set_role")。
        *   使用多对多关联表将 `Role` 与 `Permission` 关联。
    *   **认证服务 (`/services/auth_service.py`)**:
        *   创建 `AuthService`，负责用户登录、密码验证，并提供核心的授权检查装饰器 `permission_required(permission_name)`。
4.  **管理员模块 (Pluggable DLC)**:
    *   **命令 (`/commands/admin/`)**: 实现 `role list`, `user list`, `user set_role` 等强大的管理命令。
    *   **DLC 设计**: 此模块必须设计为可独立增删。所有命令必须通过 `sudo` 提权执行，`sudo` 在执行时会调用 `AuthService` 进行严格的管理员角色和权限验证。
5. **User Manager**
    *   贯穿整个游戏的用户管理系统，通过调用dal层等实现用户登录，记录等实现隔离
    *   实现独立的UUID记录，通过uuid进行索引名字密码等关键参数。
    *   用户的信息？包含什么方面？


### **第2章 Extra ：应用市场 (App Market)**

**目标**: 引入一个基础的应用市场，作为玩家早期获取信息、提升效率的核心渠道。

**核心理念**: 借鉴 `refactor/apps/` 和 `refactor/features/app_market.py` 的成功实践。应用市场是玩家增强自身能力的第一个窗口。它不直接创造财富，但能极大地放大玩家决策的准确性和效率。用命令行的方式展现一个类图形的展示方式，类似于早起Mac OS。

**技术实现要点**:

1.  **模型 (`/models/apps/`)**:
    *   **`App` (`app.py`)**: 定义 `App` ORM模型，包含 `id`, `name`, `description`, `price`。
    *   **`UserAppOwnership` (`ownership.py`)**: 一个简单的关联模型，用于记录哪个用户拥有哪个App。

2.  **数据 (`/data/definitions/apps.json`)**:
    *   定义一个JSON文件，存储所有基础应用的元数据。例如：
        *   `advanced_calculator`: 用于复杂金融计算。
        *   `news_terminal_pro`: 提供更强大的新闻搜索和过滤功能。
        *   `market_analyzer_v1`: 提供基础的市场情绪分析。

3.  **服务 (`/services/app_service.py`)**:
    *   创建 `AppService`，负责从JSON加载应用信息、处理玩家的购买请求、以及查询玩家是否拥有特定应用。

4.  **命令 (`/commands/apps/`)**:
    *   **`app market`**: 显示应用市场中所有可供购买的应用列表。
    *   **`app buy <app_id>`**: 购买一个应用。
    *   **`app list`**: 显示玩家已经拥有的应用。
    *   **`app run <app_id>`**: (可选) 对于有独立界面的应用，执行此命令可以启动它。

## **第二部：第一桶金 (Part II: The First Pot of Gold)**

*   **游戏流程阶段**: 玩家完成身份创建后，进入游戏世界，首要目标是积累原始资本。此阶段的核心是围绕银行系统和初级股票市场 (JCMarket) 进行的金融活动。

### **第三章：金融中枢 (The Financial Hub)**

**目标**: 建立一个强大、真实的金融系统，作为整个游戏经济的基石。这包括多币种支持和功能完备的银行服务，为玩家提供管理资金、获取杠杆的核心工具。

**技术实现要点**:

1.  **多币种体系**:
    *   **核心模型 (`/models/finance/currency.py`)**: 定义 `Currency` 模型，包含 `name`, `code` (e.g., "USD", "CNY"), `symbol`, 和对标 FED$ 的 `exchange_rate`。
    *   **数据定义 (`/data/definitions/currencies.json`)**: 初始化多种世界主要货币及其初始汇率。
    *   **核心服务 (`/services/currency_service.py`)**: 创建 `CurrencyService`，负责处理所有货币兑换计算，并响应 `TimeTickEvent` 来模拟汇率的随机波动。
2.  **银行系统**:
    *   **核心模型 (`/models/finance/`)**:
        *   `BankAccount`: 存储玩家在不同银行、不同币种的存款。
        *   `Loan`: 记录玩家的贷款信息，包括金额、利率、期限、已还款等。
        *   `CreditProfile`: 玩家的信用档案，记录信用评分，影响贷款额度和利率。
    *   **核心服务**:
        *   **`BankService` (`/services/bank_service.py`)**: 提供 `deposit`, `withdraw`, `transfer`, `take_loan`, `repay_loan` 等核心银行操作。
        *   **`CreditService` (`/services/credit_service.py`)**: 根据玩家的资产、还款历史等，动态计算和更新其信用分。
    *   **银行命令 (`/commands/bank.py`)**:
        *   `bank`: 显示所有银行账户的概览。
        *   `bank deposit <currency> <amount>`: 存款。
        *   `bank withdraw <currency> <amount>`: 取款。
        *   `bank loan <amount>`: 申请贷款。
        *   `bank repay <loan_id>`: 偿还贷款。

### **第四章：JCMarket 初体验 (First Steps in JCMarket)**

**目标**: 引入一个动态的、由新闻驱动的初级股票市场 (JCMarket)，让玩家熟悉基本的市场交易，并作为早期资金增值的主要途径。

**技术实现要点**:

1.  **动态新闻系统**:
    *   **核心模型 (`/models/news.py`)**: 定义 `News` 模型，包含 `headline`, `body`, `timestamp`, 以及最重要的 `impact_tags` (e.g., `["tech+", "finance-"]`)。
    *   **新闻模板 (`/data/definitions/news_templates.json`)**: 创建大量新闻模板，包含可变占位符 (e.g., "【公司】的【产品】发布会取得巨大成功")，用于动态生成新闻。
    *   **核心服务 (`/services/news_service.py`)**: `NewsService` 监听 `TimeTickEvent`，有一定几率根据模板生成新的新闻条目，并广播 `NewsPublishedEvent`。
2.  **JCMarket 实现**:
    *   **核心模型 (`/models/stock.py`)**:
        *   `Stock`: 定义股票基本信息，如 `ticker`, `company_name`, `industry`。
        *   `StockPrice`: 记录某支股票在特定时间点的价格。
    *   **数据定义 (`/data/definitions/jc_stocks.json`)**: 初始化 JCMarket 的上市公司列表。
    *   **核心服务 (`/services/stock_service.py`)**:
        *   `StockService` 是市场的核心驱动。它监听 `TimeTickEvent` 来引入微小的随机价格波动。
        *   同时，它监听 `NewsPublishedEvent`，检查新闻的 `impact_tags`，并对相关行业或公司的股票价格产生显著影响，实现“新闻驱动市场”。
    *   **股票命令 (`/commands/stock.py`)**:
        *   `news`: 查看最新的财经新闻。
        *   `stock list`: 列出 JCMarket 的所有股票。
        *   `stock view <ticker>`: 查看特定股票的详细信息和历史价格图表。
        *   `stock buy <ticker> <shares>`: 购买股票。
        *   `stock sell <ticker> <shares>`: 出售股票。
        *   `portfolio`: 查看当前持仓。

## **第三部：财富扩张 (Part III: Wealth Expansion)**

*   **游戏流程阶段**: 当玩家通过初级市场和银行系统积累了第一笔可观的财富后（例如，流动资产达到 1,000,000 J$），游戏将引导其进入更广阔的投资领域。此阶段的核心是“消费升级”和“资产配置”，解锁应用市场和家园体系。

### **第五章：应用市场与高级交易 (App Market & Advanced Trading)**

**目标**: 引入一个可扩展的应用生态系统，玩家可以通过购买和使用各种软件工具来增强其信息获取和交易执行能力，从而深化游戏策略。

**技术实现要点**:

1.  **解锁机制**:
    *   当玩家的 `BankAccount` 总余额首次超过设定的阈值（e.g., 1,000,000），系统会触发一个一次性事件，提示玩家可以“升级计算机硬件”，从而解锁“应用市场”功能。
2.  **应用市场实现**:
    *   **核心模型 (`/models/app/`)**:
        *   `App`: 定义应用的基本信息，如 `name`, `description`, `price`, `category` (e.g., "Trading", "Data Analysis")。
        *   `UserAppOwnership`: 记录玩家拥有的应用。
    *   **数据定义 (`/data/definitions/apps.json`)**:
        *   定义所有可用的应用程序。例如：
            *   `高级图表分析工具`: 解锁更详细的股票技术指标。
            *   `新闻情感分析器`: 自动分析新闻的潜在市场影响。
            *   `限价单机器人`: 解锁 `stock` 命令的限价单功能。
    *   **核心服务 (`/services/app_service.py`)**:
        *   `AppService` 负责处理应用的购买逻辑，并提供查询玩家是否拥有特定应用的功能。
    *   **相关命令 (`/commands/app.py`, `/commands/stock.py`)**:
        *   `computer upgrade`: 执行一次性的升级操作，解锁应用市场。
        *   `app market`: 查看所有可购买的应用。
        *   `app buy <app_name>`: 购买应用。
        *   `app list`: 查看已拥有的应用。
        *   `stock` 命令扩展：`buy` 和 `sell` 子命令将增加 `--limit <price>` 和 `--stop-loss <price>` 等参数。在执行时，命令会先通过 `AppService` 检查玩家是否已购买相应功能的应用，否则操作失败。

### **第六章：家园体系与实物资产 (The Home System & Physical Assets)**

**目标**: 引入房地产和奢侈品等实物资产，作为玩家财富的重要组成部分和价值储存手段，完美契合 `new.md` 中“做好资产分配，进军房地产”的核心理念。

**技术实现要点**:

1.  **解锁机制**:
    *   当玩家购买第一处房产后，“家园”标签页将在主界面解锁。
2.  **家园系统实现**:
    *   **核心模型 (`/models/home/personal_asset.py`)**:
        *   `PersonalAsset`: 一个通用的实物资产模型，包含 `name`, `type` ("Real Estate", "Luxury Car", "Art"), `purchase_price`, `current_value`, 以及一个 `value_update_rule` 字段（e.g., a small formula or set of tags indicating how its value changes）。
    *   **数据定义 (`/data/definitions/personal_assets.json`)**:
        *   定义一个包含全球主要城市地标房产、限量版跑车、传世艺术品等的市场。
    *   **核心服务 (`/services/home_service.py`)**:
        *   `HomeService` 监听 `TimeTickEvent`，根据每个资产的 `value_update_rule` 和全局经济事件（e.g., 房地产市场繁荣/萧条）来定期更新其 `current_value`。
    *   **相关命令 (`/commands/home.py`)**:
        *   `home market`: 查看当前可购买的房产和奢侈品。
        *   `home buy <asset_id>`: 购买一项资产。
        *   `home assets`: 显示玩家当前拥有的所有实物资产及其总价值。
        *   `home sell <asset_id>`: 出售已拥有的资产。

## **第四部：企业帝国 (Part IV: The Corporate Empire)**

*   **游戏流程阶段**: 当玩家的财富和影响力达到一个新的高度后（例如，总资产超过 10,000,000 J$），游戏将引导其创立自己的第一家公司，从资本的投机者转变为价值的创造者。这是游戏的中后期核心玩法。

### **第七章：公司与价值链 (Company & Value Chain)**

**目标**: 构建一个深度、复杂的公司经营模拟系统。玩家需要选择行业、研发科技、设计产品、建立生产线，并最终将产品推向市场，形成完整的商业闭环。

**技术实现要点**:

1.  **解锁与创立**:
    *   达到资产阈值后，玩家将解锁 `company create` 命令，允许其投入一笔启动资金，在特定行业（如半导体、软件、生物科技）创立第一家公司。
2.  **核心模型 (`/models/company/`)**:
    *   `Company`: 公司的核心实体，包含财务报表（现金、资产、负债、收入、利润）、员工、科技水平等。
    *   `Industry`: 定义行业及其特定的科技树和市场需求。
    *   `Technology`: 可被公司研发的具体技术，是解锁更高级产品的前提。
    *   `ProductBlueprint`: 玩家设计的产品蓝图，结合了已研发的技术，决定了产品的性能和成本。
    *   `ProductionLine`: 公司建造的生产线，用于将产品蓝图转化为实际的库存。
    *   `InventoryItem`: 库存中的待售商品。
3.  **数据定义 (`/data/definitions/`)**:
    *   `industries.json`: 定义所有可选行业及其特性。
    *   `technologies.json`: 定义完整的、跨行业的科技树。
4.  **核心服务**:
    *   `CompanyService` (`/services/company_service.py`): 管理公司的财务、招聘和日常运营。
    *   `TechnologyService` (`/services/technology_service.py`): 处理科技研发的逻辑和进度。
    *   `ProductionService` (`/services/production_service.py`): 管理生产线的建造和产品生产。
5.  **公司命令 (`/commands/company.py`)**:
    *   `company create <name> --industry <industry_name>`: 创建新公司。
    *   `company status`: 查看公司财务、运营和库存的详细报告。
    *   `company research <tech_name>`: 投入资金研发新技术。
    *   `company design <product_name> --tech <tech1,tech2...>`: 设计新产品蓝图。
    *   `company build <production_line_name> --blueprint <product_name>`: 建造生产线。
    *   `company produce <amount> --line <line_name>`: 开始生产。
    *   `company sell <item_id> <price>`: 在市场上销售库存商品。

### **第八章：进军JCSDAQ与企业地产 (Entering JCSDAQ & Corporate Real Estate)**

**目标**: 将玩家亲手创立的公司推向资本市场，并引入企业级资产配置，特别是商业地产投资，实现虚拟经济与实体经济的深度融合。

**技术实现要点**:

1.  **市场分层 (JCSDAQ)**:
    *   当玩家的公司达到一定规模和盈利能力后，将解锁 `company ipo` 命令，允许公司在高级证券交易所 **JCSDAQ** 上市。
    *   JCSDAQ 是一个独立的市场，其上市公司均为玩家或其他高级AI所拥有的企业。
2.  **高级市场特性**:
    *   **股价联动**: JCSDAQ 上市公司的股价将不再仅仅由新闻驱动，而是与 `CompanyService` 中的财务数据（收入、利润、增长率）强相关。`StockService` 将扩展其定价模型，把公司基本面作为核心影响因子。
    *   **企业地产投资**: 公司可以将其利润投资于大型商业地产（办公楼、工厂、数据中心），这些地产作为公司的核心资产，不仅能产生租金收入，还能提升公司的整体估值和抗风险能力，并对股价产生正面影响。这部分将扩展 `HomeService` 或创建一个新的 `CorporateAssetService` 来管理。
3.  **命令扩展与新增**:
    *   `company ipo`: 公司进行首次公开募股。
    *   `company asset buy <property_id>`: 为公司购置商业地产。
    *   `stock` 命令增加 `--market <JCMarket|JCSDAQ>` 参数，允许玩家在两个市场间切换交易。
    *   `analyse <ticker> --market JCSDAQ`: 对玩家自己的公司进行深度财务和市场分析。


## **第九章：更远的金融征程 (Chapter 9: The Further Financial Journey)**

*   **游戏流程阶段**: 在玩家成功创建并运营了自己的公司，甚至可能已将其推向JCSDAQ之后，他们将接触到更广阔、更复杂的全球金融生态系统。这一阶段标志着玩家从成熟的企业家转变为金融巨头，可以利用各种前沿的金融工具进行资本运作。

### **第一节：商品与金融衍生品 (Commodities & Financial Derivatives)**

**目标**: 引入一个与股票和公司经营相关但独立的商品市场，以及基于此的期货交易系统，为玩家提供对冲风险和进行高杠杆投机的工具。

**技术实现要点**:

1.  **商品市场 (Spot Commodities Market)**:
    *   **核心模型 (`/models/commodity/`)**:
        *   `Commodity`: 定义基础商品，如原油、黄金、稀有金属、农产品等。属性包括 `name`, `symbol`, `unit` (e.g., "桶", "盎司")。
        *   `CommodityPrice`: 记录商品在特定时间点的价格。
    *   **数据定义 (`/data/definitions/commodities.json`)**: 初始化全球主要商品及其初始价格。
    *   **核心服务 (`/services/commodity_service.py`)**:
        *   `CommodityService` 监听 `TimeTickEvent`，模拟商品价格的自然波动，并响应全球经济事件（如地缘政治冲突、自然灾害）带来的剧烈价格冲击。
    *   **命令 (`/commands/commodity.py`)**:
        *   `commodity list`: 列出所有可交易商品。
        *   `commodity view <symbol>`: 查看特定商品的实时价格和历史图表。
        *   `commodity buy/sell <symbol> <quantity>`: 进行现货交易。
2.  **期货市场 (Futures Market)**:
    *   **核心模型 (`/models/futures/`)**:
        *   `FuturesContract`: 定义一份期货合约。属性包括 `underlying_commodity` (标的商品), `contract_size`, `expiration_date`, `strike_price`, `current_price`, `long_position_holder`, `short_position_holder`。
    *   **核心服务 (`/services/futures_service.py`)**:
        *   `FuturesService` 负责创建新的期货合约（通常是每月或每季度到期），管理合约的交易和持仓，并在到期日进行结算。结算时，会根据到期日的现货价格与合约价格的差额，从赢家的账户向输家的账户转移资金。
        *   价格驱动：期货价格紧密跟踪其标的商品的现货价格，并加上持有成本（如仓储费、利息）和市场情绪溢价。
    *   **命令 (`/commands/futures.py`)**:
        *   `futures list`: 列出当前所有有效的期货合约。
        *   `futures view <contract_id>`: 查看特定合约的详细信息。
        *   `futures buy/sell <contract_id> <quantity>`: 开立多头或空头仓位。
        *   `futures position`: 查看玩家当前持有的所有期货仓位。

### **第二节：去中心化金融 (DeFi) 与 NFT**

**目标**: 引入一个基于区块链的、去中心化的金融实验场。玩家可以参与流动性挖矿、赚取协议收入，并通过NFT拥有独一无二的数字资产。

**技术实现要点**:

1.  **DeFi 生态系统**:
    *   **核心模型 (`/models/defi/`)**:
        *   `DeFiProtocol`: 代表一个DeFi协议，如去中心化交易所(DEX)、借贷协议、流动性挖矿池。属性包括 `name`, `total_value_locked (TVL)`, `yield_rate` (APY)。
        *   `LP_Token`: 玩家在提供流动性后获得的凭证。
    *   **核心服务 (`/services/defi_service.py`)**:
        *   `DeFiService` 模拟协议的运行。例如，借贷协议会根据供需动态调整利率；流动性挖矿池会根据TVL和预设规则定期向LP代币持有者发放奖励代币。
        *   与主币种系统集成：玩家可以将持有的FED$等法币存入DeFi协议，兑换成生息代币（如xFED$）。
    *   **命令 (`/commands/defi.py`)**:
        *   `defi protocols`: 列出所有可用的DeFi协议。
        *   `defi deposit <protocol_name> <amount>`: 将资金存入协议。
        *   `defi withdraw <protocol_name> <amount>`: 从协议中提取资金和收益。
        *   `defi farm`: 参与流动性挖矿，提供流动性并获得LP代币。
2.  **NFT (非同质化代币)**:
    *   **核心模型 (`/models/nft/`)**:
        *   `NFT`: 代表一个独一无二的数字资产。属性包括 `token_id`, `name`, `description`, `metadata` (存储图片、属性等信息的URI), `owner`。
        *   `NFTCollection`: 代表一个NFT系列，如“传奇芯片设计图”或“历史CEO签名”。
    *   **数据定义 (`/data/definitions/nft_collections.json`)**: 定义各种独特的NFT系列及其稀有度。
    *   **核心服务 (`/services/nft_service.py`)**:
        *   `NFTService` 管理NFT的铸造、转移和市场交易。
        *   **NFT市场**: 一个玩家可以买卖NFT的二级市场。NFT的价格由其稀有度和市场需求决定。
    *   **命令 (`/commands/nft.py`)**:
        *   `nft collection <collection_name>`: 查看特定系列的NFT。
        *   `nft view <token_id>`: 查看特定NFT的详细信息。
        *   `nft mint <collection_name>`: （在特定条件下）铸造一个新的NFT。
        *   `nft trade [buy|sell] <token_id> <price>`: 在NFT市场上进行交易。
        *   `nft inventory`: 查看玩家拥有的所有NFT。


## **第五部：全球统治 (Part V: Global Dominion)**

*   **游戏流程阶段**: 玩家的公司已成为行业巨头，并主宰了JCSDAQ。此时，游戏进入终局阶段，玩家的目标将从建立企业扩展到重塑全球经济格局，与其他超级企业和国家力量进行直接对抗。

### **第X章：全球棋局与资本战争 (The Global Chessboard & Capital Wars)**

**目标**: 引入宏观经济和跨国公司间的终极对抗。玩家将参与并购、恶意收购，并在全球范围内配置资源，与其他巨头争夺产业链的控制权。

**技术实现要点**:

1.  **跨国并购 (M&A)**:
    *   **核心服务 (`/services/merger_service.py`)**:
        *   `MergerService` 负责处理复杂的并购逻辑，包括估值、谈判（一个基于成功率和多轮出价的迷你游戏）、以及股东投票。
        *   玩家可以对 JCMarket 或 JCSDAQ 上的任何非玩家控股公司发起收购要约。
    *   **恶意收购**:
        *   玩家可以在二级市场上秘密吸筹，当持股比例超过特定阈值（e.g., 5%）时，可以发起代理权战争或直接的恶意收购，这将引发目标公司管理层的激烈反抗。
2.  **全球化运营**:
    *   **模型扩展**: `Company` 模型增加 `global_operations` 字段，记录在不同国家/地区的子公司和资产。
    *   **地缘政治事件**: `NewsService` 将生成影响特定国家或地区经济的宏观事件（如贸易战、经济制裁、技术封锁），直接影响玩家跨国公司的运营效率和盈利能力。
3.  **相关命令 (`/commands/corpwar.py`)**:
    *   `corp offer buy <ticker> --price <price_per_share>`: 发起一个友好的收购要约。
    *   `corp hostile takeover <ticker>`: 发动一场恶意的收购战争。
    *   `corp expand <country_code>`: 在新的国家建立分公司，开拓海外市场。

### **第XI章：人才战争与第四次工业革命 (The War for Talent & The Fourth Industrial Revolution)**

**目标**: 引入“人”作为核心战略资源，并设计能够颠覆游戏规则的终极科技，让玩家为最终目标做准备。

**技术实现要点**:

1.  **关键人才系统 (Key Personnel)**:
    *   **核心模型 (`/models/hr/`)**:
        *   `Talent`: 定义游戏中的关键人才（如明星CEO、顶尖科学家），他们拥有独特的技能和属性，能极大地增幅公司特定领域的表现。
    *   **核心服务 (`/services/hr_service.py`)**:
        *   `HRService` 管理一个全局的人才市场，玩家可以通过 `headhunt` 命令高薪挖角。
        *   将人才分配到公司后，其技能会自动生效（e.g., 一个“供应链大师”CEO可以降低所有生产成本）。
2.  **终局科技 (Endgame Technologies)**:
    *   `TechnologyService` 将包含一个特殊的“第四次工业革命”科技树，其中包含如“强人工智能”、“可控核聚变”、“量子计算”等颠覆性技术。
    *   研发这些技术需要巨量的资本和前置科技，但一旦完成，将给予玩家不对称的巨大优势，例如解锁全新的、利润极高的产业。
3.  **相关命令 (`/commands/hr.py`, `/commands/company.py`)**:
    *   `hr market`: 查看当前可供招聘的人才。
    *   `hr headhunt <talent_id> --offer <salary>`: 尝试挖角一名人才。
    *   `company assign <talent_id> --position <CEO|CTO...>`: 任命人才。

### **DLC1模块：影子战争 (The Shadow War)**

**目标**: 作为一个完全独立、可插拔的DLC模块，为游戏增加一层信息战、商业间谍和暗中破坏的玩法，满足喜爱高风险、高回报策略的玩家。

**技术实现要点**:

1.  **情报机构**:
    *   玩家可以创建自己的“情报部门”，这是一个特殊的公司类型。
    *   **核心模型 (`/models/intelligence/`)**: `Spy`, `Intel`, `CovertOp`。
    *   **核心服务 (`/services/intelligence_service.py`)**: 管理间谍的招募、培训和任务派遣。
2.  **谍报活动**:
    *   **窃取技术**: 派遣间谍窃取竞争对手正在研发的技术。
    *   **市场操纵**: 散播关于竞争对手的虚假负面消息，以打压其股价。
    *   **破坏活动**: 对竞争对手的生产线进行物理或网络破坏。
    *   **反间谍**: 部署自己的安保力量，抓捕对方的间谍。
3.  **相关命令 (`/commands/intel.py`)**:
    *   `intel recruit`: 招募新的间谍。
    *   `intel dispatch <spy_id> --op <StealTech|Sabotage> --target <company_id>`: 派遣间谍执行任务。
    *   `intel report`: 查看所有情报任务的报告。

#### **DLC 2: 企业同盟 (Corporate Alliance)**

**核心目标**: 引入“远程联机，本地存档”的轻度多人协作模式。玩家可以与其他玩家组成同盟，共同应对更强大的AI派系或完成宏伟的合作项目。

**技术实现**:

*   **网络层 (`services/network_service.py`)**:
    *   **职责**: 处理玩家间的非实时数据同步。采用一个轻量级的API服务器来交换同盟状态、共享资金、项目进度等信息。
    *   **数据同步**: 玩家上线时，客户端会向服务器请求同盟的最新数据并更新本地存档。玩家的本地操作（如向同盟金库注资）会异步推送到服务器。这种设计避免了对强实时同步的需求。

*   **模型层 (`models/alliance/`)**:
    *   `alliance.py`: 定义一个企业同盟。
        *   **属性**: `name`, `members` (成员列表), `shared_treasury` (共享金库), `alliance_tech_tree` (同盟独有的科技树), `joint_ventures` (合作项目列表)。
    *   `joint_venture.py`: 定义一个合作项目，如“建造全球超高速铁路网”。需要多个成员共同投资和贡献资源才能完成。

*   **服务层 (`services/alliance_service.py`)**:
    *   **同盟管理**: 处理创建、邀请、加入、退出同盟的逻辑。
    *   **金库与治理**: 管理共享金库的资金流动，并可实现一套简单的投票系统来决定重大事项。
    *   **项目驱动**: 驱动合作项目的进展，根据成员的贡献更新项目状态，并在项目完成时给予所有参与者丰厚的回报。

*   **命令层 (`commands/alliance_commands.py`)**:
    *   `alliance [create|invite|join|status]`: 管理同盟。
    *   `alliance deposit [amount]`: 向同盟金库注资。
    *   `alliance venture [start|contribute|status]`: 管理合作项目。

---

#### **DLC 3: 地缘棋局 (Geopolitical Chess)**

**核心目标**: 将基础游戏中的“国家”概念深化，允许玩家通过经济和科技实力深度干预国际政治，从而为自己的商业帝国谋求战略优势。

**技术实现**:

*   **模型层 (`models/nation/`)**:
    *   `nation.py`: 扩展国家模型，加入更多政治属性。
        *   **新增属性**: `government_type` (政体), `policies` (政策字典，如税率、关税、环保法规), `stability` (稳定度), `relations` (与其他国家的关系), `player_influence` (玩家对该国的影响力)。
    *   `policy.py`: 定义具体的国家政策及其对经济和游戏世界的影响。

*   **服务层 (`services/politics_service.py`)**:
    *   **政治模拟**: 模拟各国的内部政治动态。例如，在民主国家，选举会定期举行，玩家可以通过政治献金支持符合自己利益的候选人。
    *   **游说系统**: 玩家可以花费资金和影响力，对特定国家的特定政策进行游说，以期推动有利于自己的法规出台（如降低奢侈品消费税）。
    *   **国际关系**: 国家间的关系会动态变化，可能爆发贸易战、组建贸易同盟等。这些事件将作为高级新闻由 `news_service` 发布，并对全球市场产生深远影响。

*   **命令层 (`commands/nation_commands.py`)**:
    *   `nation status [nation_name]`: 查看一个国家的详细状态。
    *   `nation lobby [nation_name] --policy [policy_name] --action [support|oppose]`: 对某项政策进行游说。

---

#### **DLC 4: 传媒帝国 (Media Empire)**

**核心目标**: 允许玩家收购、建立和运营媒体集团，将“信息”本身作为一种强大的武器，用于引导舆论、影响市场、甚至对竞争对手发起舆论攻击。

**技术实现**:

*   **模型层 (`models/media/`)**:
    *   `media_outlet.py`: 定义一个媒体实体，如电视台、报社、社交媒体平台。
        *   **属性**: `name`, `reach` (受众规模), `credibility` (公信力), `bias` (立场倾向), `owner` (所有者)。

*   **服务层 (`services/media_service.py`)**:
    *   **内容生产**: 与 `news_service` 深度绑定。当玩家控制一个媒体后，可以下令“制造”新闻。
    *   **舆论引擎**: 玩家可以发起一场“公关活动”或“舆论攻击”。例如，发布一篇吹捧自己公司新技术的文章，或是一篇揭露对手公司财务问题的深度报道。
    *   **效果模拟**: 发布的新闻会通过 `news_service` 传播。其影响力取决于媒体的公信力和受众规模。一条成功的正面报道可以显著提升公司股价和产品销量；而一条成功的负面报道则可能引发对手的公关危机，导致其股价暴跌。

*   **命令层 (`commands/media_commands.py`)**:
    *   `media list`: 查看全球可收购的媒体列表。
    *   `media acquire [outlet_name]`: 发起对一个媒体的收购。
    *   `media campaign [outlet_name] --target [company_name] --type [positive|negative] --topic "[topic]"`: 发起一场舆论活动。
