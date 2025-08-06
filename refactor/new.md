# **《芯片战争》终极开发文档**

## **序章：创世史诗 (Prologue: The Genesis Epic)**

### **核心世界观**

玩家并非凡人，而是一位在未来“芯片战争”的终极对决中失败，却意外重生回到战争黎明期的“先知”。凭借对未来几十年的重大科技突破、市场脉络、关键人才的记忆，玩家拥有了改写历史、铸造传奇的唯一机会。

**最终目标**: 玩家的使命并非简单地积累财富，而是要亲手建立一个横跨全球的商业帝国，整合支离破碎的全球经济，最终废除所有主权货币，铸造统一的“星际联邦信用点 (FED$)”，为人类文明迈向星辰大海的未来铺平最后的道路。这既是游戏的终极胜利条件，也是“先知”的天命所在。

### **架构核心原则**

*   **命令驱动 (Command-Driven)**: 核心交互将围绕一个强大的命令行界面(CLI)展开，提供最高效、专业的沉浸式体验。
*   **模块化设计 (Modular Design)**: 系统的每一个核心功能（如银行、公司、新闻）都将是独立的、高内聚的模块。尤其体现在 `models` 目录结构上，严格遵循 `models/模块名/模型名.py` 的组织方式，确保命名空间的绝对清晰与未来的高扩展性。
*   **数据访问层 (Data Access Layer)**: 业务逻辑与数据库操作将通过严格的DAL和工作单元(Unit of Work)模式进行解耦，确保代码的可维护性和可测试性。
*   **事件驱动 (Event-Driven)**: 系统内部的关键活动（如时间流逝、交易完成、新闻发布）将通过一个全局的事件总线进行广播和监听，实现模块间的低耦合通信。


游戏主流程：
进入游戏，进行剧情，获得JC中央银行贷款（可选1000，10000，100000组合包含不同利率还款期等）
注册JC-Market股市账户（拟真抽成与交易税等预留），然后赢得第一桶金。
购买第一次电脑升级ROM，允许安装App应用商城，解锁限价单做多做空等交易。
然后达到1000000流动资产，购买地一套房子解锁家庭系统，在此可以进行第一次初创公司，作为企业家解锁JCSDAQ（JC联邦股票市场，更大）
然后进行企业经营，商业计划，做好资产分配，进军房地产等。
---

## **第一部：世界基石 (The Foundation)**

### **第一章：创世与货币 (Genesis & Currency)**

**目标**: 搭建项目的骨架，建立最底层的配置、数据库访问和多货币体系，为整个虚拟世界的运转提供动力。

**核心理念**: 一个稳定、可靠、可扩展的底层是上层建筑一切辉煌的保障。多货币体系的设计灵感来源于 `refactor/core/currency_system.py`，但将以更模块化、服务化的方式重构。

**技术实现要点**:

1.  **项目结构初始化**:
    *   创建核心目录：`/config`, `/core`, `/models`, `/services`, `/commands`, `/data/definitions`, `/dal`。

2.  **配置中心 (`/config/settings.py`)**:
    *   定义 `Settings` 类，用于管理游戏的所有静态配置，如数据库连接信息、初始资金、游戏版本号等。
    *   配置应可从环境变量或配置文件加载，便于开发和部署分离。

3.  **数据访问层 (DAL)**:
    *   **数据库引擎 (`/dal/database.py`)**: 初始化SQLAlchemy的engine和sessionmaker，提供全局唯一的数据库会话来源。
    *   **工作单元 (`/dal/unit_of_work.py`)**: 实现一个抽象的 `UnitOfWork` 协议和具体的 `SqlAlchemyUnitOfWork` 类。它将封装数据库会话的生命周期（提交、回滚），并作为所有服务操作数据库的唯一入口。

4.  **多货币系统**:
    *   **模型 (`/models/economy/currency.py`)**:
        *   定义 `Currency` ORM模型，包含字段：`code` (e.g., "USD", "JCD"), `name` (e.g., "US Dollar"), `rate_to_jcd` (相对JCD的汇率), `volatility` (波动率)。
        *   JCD (JackyCoin Dollar) 将作为游戏世界的基准货币，`rate_to_jcd` 恒定为1.0。
    *   **数据 (`/data/definitions/currencies.json`)**:
        *   存储所有货币的初始定义，包括美元、欧元、人民币等，便于游戏启动时初始化。
    *   **服务 (`/services/currency_service.py`)**:
        *   定义 `CurrencyService`，负责货币的加载、查询和汇率更新。
        *   实现 `update_exchange_rates()` 方法，该方法将被时间引擎每隔一段时间调用，根据各自的 `volatility` 模拟汇率波动。

5. **User Manager**
    *   贯穿整个游戏的用户管理系统，通过调用dal层等实现用户登录，记录等实现隔离
    *   实现独立的UUID记录，通过uuid进行索引名字密码等关键参数。
    *   用户的信息？包含什么方面？

### **第二章：神谕与交互 (Oracle & Interaction)**

**目标**: 构建一个健壮、可扩展的命令处理系统，它是玩家与游戏世界交互的唯一桥梁。

**核心理念**: 借鉴 `refactor/commands/command_processor.py` 的经验，我们将设计一个更优雅、更面向对象的命令注册与分发系统。所有功能最终都将体现为一条条精准的命令。

**技术实现要点**:

1.  **命令抽象 (`/commands/base.py`)**:
    *   定义一个抽象基类 `Command`，所有具体的命令都将继承自它。包含 `name`, `aliases`, `description` 属性和一个 `execute()` 方法。

2.  **命令注册与分发**:
    *   **注册表 (`/commands/registry.py`)**: 创建 `CommandRegistry` 类，一个单例或全局可访问的对象，负责在系统启动时自动发现并注册所有 `Command` 的子类。
    *   **分发器 (`/services/command_dispatcher.py`)**: 创建 `CommandDispatcher` 服务。它接收原始的用户输入字符串，解析出命令名称和参数，从 `CommandRegistry` 中查找对应的命令对象，并调用其 `execute()` 方法。

3.  **基础元命令**:
    *   **帮助 (`/commands/meta/help.py`)**: 实现 `HelpCommand`。当执行 `help` 时，它能遍历 `CommandRegistry`，格式化输出所有已注册命令的名称和描述。执行 `help <command_name>` 时，能显示该命令更详细的用法。
    *   **别名 (`/commands/meta/alias.py`)**: 实现 `AliasCommand`，允许玩家为现有命令创建自定义的别名，提升操作效率。
    *   **退出 (`/commands/meta/quit.py`)**: 实现 `QuitCommand`，用于安全退出游戏。

4.  **未来展望（无需实现）- 自然语言接口**:
    *   在 `CommandDispatcher` 的设计中，为未来集成自然语言处理(NLP)引擎预留一个 `parse_natural_language()` 的接口。当前可以是一个空实现，但它标志着我们对 `WIKI.md` 中提到的“自然语言交易”的长期承诺。

### **第三章：世界脉搏与新闻 (World Pulse & News)**

**目标**: 创造一个“活”的世界。建立驱动时间流逝的引擎、模块间通信的总线，以及作为核心事件源的动态新闻系统。

**核心理念**: 游戏世界不应是静止的，而应是一个随时间动态演化的有机体。新闻是驱动这种演化的主要外部变量，它将深刻影响后续所有经济活动。

**技术实现要点**:

1.  **时间引擎 (`/services/time_service.py`)**:
    *   创建 `TimeService`，它将作为游戏世界的主时钟。
    *   内部维护一个独立的线程，以固定的间隔（“tick”）推进游戏内的时间（天、小时）。每天包含24个tick，每个tick代表1小时。
    *   每个tick，`TimeService` 都会通过事件总线广播一个 `TimeTickEvent` 事件。
    *   允许通过命令和手动执行快进，下一日等操作。

2.  **事件总线 (`/core/event_bus.py`)**:
    *   实现一个全局的 `EventBus`。它允许系统任何部分 `publish(event)` 一个事件，也允许任何服务 `subscribe(event_type, handler)` 来监听并处理特定类型的事件。
    *   这是实现模块解耦的关键。例如，`CurrencyService` 可以订阅 `TimeTickEvent` 来触发汇率更新，而无需与 `TimeService` 直接耦合。

3.  **动态新闻系统**:
    *   **模型 (`/models/world/news.py`)**:
        *   定义 `News` ORM模型，包含字段：`headline` (标题), `content` (内容), `timestamp` (发布时间), `source` (来源，如路透社、彭博社), `impact_tags` (影响标签，如 `["tech", "semiconductor", "positive"]`)。
    *   **数据 (`/data/definitions/news_templates.json`)**:
        *   创建一个包含大量新闻模板的JSON文件。每个模板可以包含占位符，如 `{company_name}`, `{region_name}`，并预设了 `impact_tags`。
    *   **服务 (`/services/news_service.py`)**:
        *   创建 `NewsService`。它将订阅 `TimeTickEvent`。
        *   在每个tick，它有一定概率根据世界当前状况（如某个行业发展迅速），从 `news_templates.json` 中选择一个模板，填充占位符，生成一条新的新闻并存入数据库。
        *   新闻生成后，`NewsService` 会发布一个 `NewsPublishedEvent`，其中包含新闻的详细信息和 `impact_tags`。其他系统（如股票市场、商品市场）将监听此事件，并根据标签来调整自身行为。
    *   **命令 (`/commands/world/news.py`)**:
        *   实现 `NewsCommand`，允许玩家查看最近发生的新闻列表，或根据关键词搜索历史新闻。


## **第二部：帝国序曲 (The Overture of an Empire)**

### **第四章：权限与角色 (Permission & Roles)**

**目标**: 建立一个健壮、可扩展的权限系统，为游戏管理和未来的多人模式（如热座、联盟）提供不可或缺的基础。

**核心理念**: 并非所有与世界交互的实体都拥有相同的能力。通过定义清晰的“角色”与“权限”，我们可以保护核心游戏逻辑，并为不同类型的玩家（或管理员）提供不同的工具集。此设计吸收了 `refactor/admin/admin_manager.py` 和 `refactor/user_manager.py` 的管理思想。

**技术实现要点**:

1.  **核心模型 (`/models/auth/`)**:
    *   **`User` (`user.py`)**: 扩展基础的用户模型，增加一个 `role_id` 外键。
    *   **`Role` (`role.py`)**: 定义 `Role` ORM模型，包含 `id`, `name` (e.g., "player", "admin", "moderator")。
    *   **`Permission` (`permission.py`)**: 定义 `Permission` ORM模型，包含 `id`, `name` (e.g., "command.admin.set_role", "service.bank.create_loan")。
    *   **关联表**: 使用多对多关联表将 `Role` 与 `Permission` 关联起来，从而赋予角色一组权限。

2.  **认证与授权服务 (`/services/auth_service.py`)**:
    *   创建 `AuthService`，负责处理用户登录、密码验证，并提供核心的授权检查功能。
    *   实现一个关键的装饰器或函数 `permission_required(permission_name)`。这个装饰器可以被应用到任何一个 `Command` 的 `execute` 方法或任何一个 `Service` 的方法上。在执行前，它会检查当前用户的角色是否拥有所需的权限，如果没有，则直接拒绝操作。

3.  **命令 (`/commands/admin/`) 必须用sudo进行提权 sudo执行时进行管理员权限验证 该模块必须可以独立增删作为DLC**:
    *   **`role list`**: 列出系统中所有可用的角色。
    *   **`user list`**: 列出所有用户及其当前角色。
    *   **`user set_role <username> <role_name>`**: (仅限管理员) 改变一个用户的角色。
    *   **`role grant <role_name> <permission_name>`**: (仅限管理员) 为一个角色授予新的权限。

### **第五章：应用市场 (App Market)**

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

增加：5.5章 股票默认市场 JCMarket

#### **第5.5章：资本启动 (Capital Endgame)**

**核心目标**: 在完成基本盈利要求后，玩家可以进入JCMarket进行带限制的股票交易。
实现从初级“JCMarket”到高级“全球资本市场”的演进。玩家必须通过解锁特定的高阶科技，才能获得进入这个顶级赌局的门票，与全球最顶尖的AI科技巨头同台竞技。

**技术实现**:

*   **模型层 (`models/stock_market/`)**:
    *   `global_stock.py`: 为全球AI巨头（如 `QuantumLeap Inc.`, `NeuroNet Corp.`）定义的股票模型。这些股票价值高、流动性强，其价格波动与全球宏观经济、重大科技突破和地缘政治事件紧密挂钩。
    *   `market_index.py`: 定义全球市场指数，如“全球科技100指数”，为玩家提供宏观市场表现的参照。
        *   **参考**: `refactor/core/index_manager.py`

*   **服务层 (`services/stock_service.py`)**:
    *   **市场分层**: 服务内部将明确区分 `JCMarket` 和 `GlobalMarket` 等多个市场。
    *   **准入机制**: 玩家的交易请求会经过一个前置检查，`player.tech_tree.is_unlocked("Global Finance")` 将是访问 `GlobalMarket` 的先决条件。
    *   **定价模型**: `GlobalMarket` 的股票价格更新将引入更多维度的变量，包括但不限于：全球经济指数、行业整体表现、`corporate_warfare_service` 中发生的重大事件（如AI巨头间的合作或竞争）。

*   **科技树扩展 (`models/company/tech_tree.py`)**:
    *   **新增节点**: 在科技树的后期阶段，加入 `"金融工程 (Financial Engineering)"`, `"全球合规 (Global Compliance)"`, `"量子交易 (Quantum Trading)"` 等关键科技。
    *   **解锁效果**: 解锁这些科技不仅是进入全球市场的门槛，还可能为玩家提供新的交易指令或分析工具。

*   **命令层 (`commands/stock_commands.py`)**:
    *   **扩展现有命令**: `trade`, `market`, `portfolio` 等命令将增加一个可选参数 `--market [jc|global]`，用于在不同层级的市场间切换。默认值为 `jc`。
----------------------------------------------------------------------------------------------------
### **第六章：家园体系 (Home System)**

**目标**: 为玩家的财富提供一个非生产性的出口，引入个人资产管理和生活方式的维度。

**核心理念**: 财富的意义不仅在于再投资。参考 `refactor/home/` 的设计，家园系统允许玩家将商业成功的果实转化为可见的、可炫耀的个人资产，提供一个重要的“金钱熔炉”和满足感来源。

**技术实现要点**:

1.  **模型 (`/models/home/`)**:
    *   **`PersonalAsset` (`asset.py`)**: 定义 `PersonalAsset` ORM模型，包含 `id`, `name`, `category` (e.g., "房产", "载具", "艺术品"), `purchase_price`, `current_market_value`, `owner_id`。

2.  **数据 (`/data/definitions/personal_assets.json`)**:
    *   定义一个JSON文件，列出所有可供购买的奢侈品，及其初始价格和价值波动特性。

3.  **服务 (`/services/home_service.py`)**:
    *   创建 `HomeService`，处理个人资产的买卖。
    *   该服务将订阅 `TimeTickEvent`，并根据预设的波动率，周期性地更新玩家名下资产的 `current_market_value`，模拟折旧或升值。

4.  **命令 (`/commands/home/`)**:
    *   **`home market`**: 查看当前奢侈品市场上有什么可买。
    *   **`home buy <asset_id>`**: 购买一项个人资产。
    *   **`home assets`**: 展示“我的豪宅/车库/收藏室”，列出已拥有的所有个人资产及其当前总价值。
    *   **`home sell <asset_id>`**: 卖掉一项个人资产。

### **第七章：金融中枢 (Financial Hub)**

**目标**: 深度融合 `refactor/bank` 和 `WIKI.md` 的设计，构建一个包含存款、贷款、信用评级和银行任务的完整银行系统。

**核心理念**: 银行是帝国的血液泵。它不仅是资金的存取处，更是信用和机遇的放大器。一个强大的银行系统是撬动更大资本的唯一杠杆。

**技术实现要点**:

1.  **模型 (`/models/bank/`)**:
    *   **`BankAccount` (`account.py`)**: 存储用户的存款信息。
    *   **`Loan` (`loan.py`)**: 记录每一笔贷款的详情，包括本金、利率、期限、还款状态。
    *   **`CreditProfile` (`credit.py`)**: 存储每个用户的信用分数和历史评级记录。
    *   **`BankMission` (`mission.py`)**: 存储银行发布的任务，包括目标（如“连续一个月保持存款高于10万”）和奖励。

2.  **服务 (`/services/`)**:
    *   **`BankService` (`bank_service.py`)**: 提供存、取款，以及贷款申请和审批的核心逻辑。审批贷款时，会向 `CreditService` 查询申请人的信用分来决定利率。
    *   **`CreditService` (`credit_service.py`)**: 这是一个事件驱动的服务。它会监听 `LoanRepaidEvent`, `LoanDefaultedEvent` 等事件，并根据这些事件动态调整用户的信用分数。
    *   **`MissionService` (`mission_service.py`)**: 负责向玩家发布银行任务，并检查任务完成情况以发放奖励。

3.  **命令 (`/commands/bank/`)**:
    *   **`bank status`**: 查看银行账户余额和存款详情。
    *   **`bank deposit|withdraw <amount>`**: 存取款。
    *   **`bank credit`**: 查看自己详细的信用报告。
    *   **`bank loans`**: 查看可申请的贷款产品或已有的贷款状态。
    *   **`bank missions`**: 查看当前可接受的银行任务。

### **第八章：公司与价值链 (Company & Value Chain)**

**目标**: 将公司、行业、科技、生产四个核心概念融为一体，打造游戏最核心的价值创造循环。

**核心理念**: 公司是玩家征服世界的唯一工具。公司的创立、成长、扩张是游戏的主线。行业决定了公司的赛道，科技是其引擎，产品是其炮弹。

**技术实现要点**:

1.  **模型 (`/models/company/`)**:
    *   **`Company` (`company.py`)**: 核心模型，包含 `name`, `ceo_id`, `cash`, `industry_code`，以及 `is_on_jcmarket` 等状态字段。
    *   **`Industry` (`industry.py`)**: 定义行业，从数据文件加载。
    *   **`Technology` (`tech.py`)**: 定义科技树节点，包含研发成本、前置条件等，与行业挂钩。
    *   **`ProductBlueprint` (`blueprint.py`)**: 定义产品蓝图，是科技研发的直接产物。
    *   **`ProductionLine` (`production.py`)**: 公司的生产线资产，用于将蓝图转化为产品。
    *   **`InventoryItem` (`inventory.py`)**: 库存中的具体产品。

2.  **数据 (`/data/definitions/`)**:
    *   **`industries.json`**: 定义所有行业及其特性。
    *   **`technologies.json`**: 定义与各行业绑定的完整科技树。

3.  **服务 (`/services/`)**:
    *   **`CompanyService` (`company_service.py`)**: 负责公司的创建、财务管理和在“JCMarket”的IPO流程。
    *   **`TalentService` (`talent_service.py`)**: 维护一个全局的人才库，供所有玩家公司招聘。人才拥有技能、期望薪资等属性。
    *   **`ResearchService` (`research_service.py`)**: 管理公司的研发活动，解锁科技树。
    *   **`ProductionService` (`production_service.py`)**: 管理生产线的建造和产品的生产。

4.  **命令 (`/commands/corp/`)**:
    *   **`corp create <name> --industry <id>`**: 创建一家公司。
    *   **`corp status`**: 查看公司财报、员工、资产等全方位信息。
    *   **`corp hire <talent_id>`**: 雇佣一名员工。
    *   **`corp fire <employee_id>`**: 解雇一名员工。
    *   **`corp tech tree`**: 查看公司的科技树。
    *   **`corp research <tech_id>`**: 开始一项新的研发。
    *   **`corp build <blueprint_id>`**: 建造一条新的生产线。
    *   **`corp produce <line_id> <quantity>`**: 在指定生产线上生产产品。
    *   **`corp ipo`**: 启动在JCMarket的上市流程。

***

### **第三部：全球博弈 (Part III: Global Game)**

当玩家的公司在本土市场（JCMarket）站稳脚跟后，游戏的重心将转移到全球舞台。本部分将引入全球商品贸易、与跨国AI公司的直接对抗，以及通往顶级资本市场的终极路径。

---

#### **第九章：商品帝国 (Commoditу Empire)**

**核心目标**: 建立一个动态的、全球化的商品交易系统。玩家不再仅仅是生产和销售最终产品，更能通过交易原材料、工业品和农产品等大宗商品来影响全球经济，并从中牟利。

**技术实现**:

*   **模型层 (`models/commodities/`)**:
    *   `base_commodity.py`: 定义所有商品的抽象基类。
        *   **参考**: `refactor/commodities/base_commodity.py`
        *   **属性**: `name` (名称), `base_price` (基础价格), `volatility` (波动率), `supply` (供给), `demand` (需求), `tags` (标签，如 `energy`, `metal`, `agriculture`)。
    *   `physical_commodity.py`: 定义具体的物理商品，如原油、黄金、铁矿石、大豆等。
    *   `commodity_lot.py`: 定义玩家持有的商品仓位，包含数量、平均成本等信息。

*   **服务层 (`services/commodity_service.py`)**:
    *   **职责**: 管理商品生命周期，处理交易。
    *   **价格更新**: 价格将由一个复杂的算法驱动，该算法综合考虑基础供需、`news_service` 发布的全球事件（如：某产油国战争导致油价上涨）、玩家的交易行为（大宗买入推高价格）以及与 `company_service` 的联动（如：大量生产汽车导致钢铁需求增加）。
    *   **交易引擎**: 与 `refactor/core/trading_engine.py` 的概念整合，提供一个专门处理大宗商品交易的核心。
    *   **数据源**: `data/commodities.json` 文件将用于初始化游戏世界中的所有商品及其基础参数。

*   **命令层 (`commands/commodity_commands.py`)**:
    *   `trade [buy|sell] [commodity_name] [quantity]`: 执行商品买卖。
    *   `portfolio commodity`: 查看当前持有的所有商品仓位。
    *   `market commodity`: 查看商品市场的实时行情。

---

#### **第十章：全球商战 (Global Business War)**

**核心目标**: 引入强大的AI跨国公司作为玩家的直接竞争对手。这不仅仅是市场份额的争夺，更包括恶意收购、供应链战争、技术封锁等高级商业对抗形式。

**技术实现**:

*   **模型层 (`models/corporations/`)**:
    *   `ai_corporation.py`: 定义AI控制的跨国公司。
        *   **属性**: 拥有独立的公司实体（与玩家公司结构类似）、战略倾向（如 `Aggressive`, `Defensive`, `Innovative`）、资本、技术储备。
        *   **行为**: AI公司将根据其战略，自主进行研发、生产、扩张、并购，甚至对玩家公司发起价格战或收购要约。
    *   `market_share.py`: 用于追踪和记录不同行业/产品在各个市场的份额。

*   **服务层 (`services/corporate_warfare_service.py`)**:
    *   **AI战略引擎**: 驱动AI公司的宏观决策。例如，一个 `Aggressive` 的AI对手可能会在玩家进入新市场时，立即发动价格战。
    *   **并购模拟**: 管理恶意收购流程。当任一公司（包括玩家）在公开市场持有对手公司超过特定比例（如20%）的股份时，可以触发收购事件。被收购方可以选择接受、拒绝或寻求“白衣骑士”的帮助。
    *   **事件联动**:
        *   与 `company_service` 深度集成，处理公司间的互动。
        *   与 `news_service` 联动，播报重大的商业新闻，如“XX集团宣布对YY公司发起敌意收购”。
        *   与 `stock_service` 联动，所有收购行为最终都通过股票市场的交易来体现。

---


***

***

### **第四部：迈向未来 (Part IV: Towards the Future)**

这是基础游戏的最终章。玩家在建立了全球商业帝国后，将揭示并执行作为“先知”的最终使命：终结全球货币壁垒，建立一个统一、稳定、高效的全新金融秩序，为人类文明的下一阶段铺平道路。

---

#### **第十二章：星辰联邦 (The Star Federation)**

**核心目标**: 铸造终极统一货币——“星际联邦信用点 (Federal Credit, FED$)”，实现游戏的最终胜利。

**世界观整合**:
在这一阶段，游戏的世界观将完全展开。玩家通过解锁一项名为“未来视解读 (Future-Sight Decryption)”的终极科技，会从“神谕系统”中获得最终启示：当前的全球经济体系因主权货币之间的摩擦、汇率波动和政治博弈而内耗严重，阻碍了文明的进一步发展。玩家的使命，就是利用自己建立的庞大经济帝国作为杠杆，整合全球所有主要经济体，用一个统一的货币取而代之。

**技术实现**:

*   **模型层 (`models/federation/`)**:
    *   `federation.py`: 定义“星辰联邦”这个核心实体。
        *   **属性**: `member_nations` (成员国列表), `total_gdp` (总GDP), `integration_progress` (整合进度), `federation_status` (联邦状态，如 `Forming`, `Active`)。
    *   `sovereign_currency.py`: 定义需要被整合的主权货币。
        *   **属性**: `name` (如 `USD`, `EUR`, `CNY`), `issuing_nation` (发行国), `exchange_rate_to_fed` (与FED的固定汇率), `integration_status` (整合状态)。

*   **服务层 (`services/federation_service.py`)**:
    *   **职责**: 这是游戏终局的核心逻辑控制器。
    *   **整合流程**: 玩家需要通过一系列复杂的“联邦任务”来逐个整合主权经济体。这些任务可能包括：
        1.  **经济主导**: 玩家公司的市值和影响力必须在该国达到绝对主导地位。
        2.  **金融渗透**: 玩家控制的银行系统需要接管该国的主要银行业务。
        3.  **科技注入**: 向该国注入高级科技，提升其生产力，使其达到“联邦准入标准”。
        4.  **外交谈判**: 通过一个简化的谈判界面，说服该国领导层加入联邦。谈判的成功率与玩家的全球声望、经济实力和完成的前置任务相关。
    *   **货币铸造**: 当足够多的经济体（例如，占全球GDP 80%以上）被整合后，`federation_service` 将触发“统一货币铸造”事件。此时，所有被整合的主权货币将按固定汇率兑换为 FED$，全球市场将开始使用 FED$ 进行计价和交易。
    *   **胜利条件检测**: 服务会持续监控 `federation.integration_progress`。一旦达到100%，游戏将触发最终的胜利结局动画和通关画面。

*   **命令层 (`commands/federation_commands.py`)**:
    *   `federation status`: 显示当前星辰联邦的组建进度、成员国和各项关键指标。
    *   `federation integrate [nation_name]`: 启动对某个主权经济体的整合任务。
    *   `federation proposal`: 查看可用的联邦任务和整合提案。

---

至此，基础游戏的核心内容已经全部规划完毕。玩家从零开始，通过建立公司、征战商场、主导全球经济，最终完成了统一货币、建立星辰联邦的宏伟目标。

接下来是同样重要的 **DLC (可下载内容)** 规划部分，将为游戏提供长期的可玩性和新的挑战。

***

### **第五部：DLCs (Downloadable Contents)**

在主线游戏通关后，DLC将为玩家提供全新的系统、挑战和游戏维度，极大地扩展《芯片战争》的世界。每个DLC都设计为一个独立的模块，可以被无缝集成到现有游戏中。

---

#### **DLC 1: 加密货币狂潮 (Cryptocurrency Frenzy)**

**核心目标**: 引入一个与传统金融市场平行、高波动性、高风险高回报的加密货币生态系统。

**技术实现**:

*   **模型层 (`models/crypto/`)**:
    *   `crypto_currency.py`: 定义加密货币的基础模型。
        *   **属性**: `name` (如 "BitCoin"), `symbol` (如 "BTC"), `current_price`, `total_supply`, `circulating_supply`, `hash_rate` (全网算力), `algorithm` (挖矿算法)。
    *   `crypto_wallet.py`: 玩家的加密货币钱包，用于存储和管理不同种类的加密资产。
    *   `mining_farm.py`: 玩家可投资的“矿场”资产，用于挖矿。属性包括 `hash_power` (算力), `energy_consumption` (能耗), `operational_cost` (运营成本)。

*   **服务层 (`services/crypto_service.py`)**:
    *   **市场模拟**: 驱动加密货币价格的波动。其价格模型将比股票更不稳定，受“炒作”、“社区情绪”、“技术突破”和“监管新闻”（由 `news_service` 发布）等因素剧烈影响。
    *   **挖矿逻辑**: 模拟挖矿过程。玩家投资矿场后，`crypto_service` 会根据玩家矿场的算力占全网算力的比例来分配新挖出的币。挖矿难度会根据全网算力的变化动态调整。
    *   **交易所**: 提供一个24/7的加密货币交易平台。

*   **命令层 (`commands/crypto_commands.py`)**:
    *   `crypto trade [buy|sell] [symbol] [quantity]`: 交易加密货币。
    *   `crypto market`: 查看加密货币行情。
    *   `crypto wallet`: 显示玩家的加密资产。
    *   `crypto farm [invest|status|upgrade]`: 投资、查看或升级矿场。

---

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

***

***

## **附录：项目技术与结构总览 (Appendix: Technical & Structural Overview)**

本附录旨在为《芯片战争》的实际开发工作提供清晰、统一的技术规范和结构指导。

---

### **一、技术选型 (Technology Stack)**

为确保项目的健壮性、可维护性和高性能，我们选用以下经过业界验证的成熟技术栈：

*   **编程语言**: Python 3.10+
*   **核心框架**: 无特定Web框架，纯粹的面向对象业务逻辑。
*   **数据库ORM**: SQLAlchemy 2.0 (用于与数据库的交互，提供强大的异步支持和类型提示)
*   **数据库**:
    *   **开发/测试**: SQLite (轻量、零配置，便于快速启动和测试)
    *   **生产**: PostgreSQL (功能强大、稳定可靠，足以支撑复杂的金融模拟和未来扩展)
*   **命令行接口 (CLI)**: Typer / Click (构建现代化、用户友好的命令行应用)
*   **依赖管理**: Pip + `requirements.txt`
*   **代码格式化与检查**: Black, Ruff, mypy (确保代码风格统一和类型安全)
*   **测试框架**: Pytest (提供灵活、强大的测试能力，拥有丰富的插件生态)

---

### **二、最终项目目录结构 (Final Project Directory Structure)**

基于前述所有设计，项目最终将采用以下高度模块化的目录结构：

```plaintext
/Chips_Battle/
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD 配置文件
├── .gitignore
├── README.md
├── requirements.txt
├── main.py                     # 应用程序主入口
├── config/
│   └── settings.py             # 全局配置管理
├── core/
│   ├── event_bus.py            # 全局事件总线
│   └── exceptions.py           # 自定义异常
├── dal/
│   ├── database.py             # SQLAlchemy引擎和会话设置
│   └── unit_of_work.py         # 工作单元模式实现
├── data/
│   └── definitions/            # 所有静态游戏数据定义
│       ├── apps.json
│       ├── commodities.json
│       ├── currencies.json
│       ├── industries.json
│       ├── news_templates.json
│       ├── personal_assets.json
│       └── technologies.json
├── models/                     # ORM模型 (按功能模块组织)
│   ├── alliance/
│   ├── apps/
│   ├── auth/
│   ├── bank/
│   ├── commodities/
│   ├── company/
│   ├── corporations/
│   ├── crypto/
│   ├── economy/
│   ├── federation/
│   ├── home/
│   ├── media/
│   ├── nation/
│   ├── stock_market/
│   └── world/
├── services/                   # 业务逻辑层 (按功能模块组织)
│   ├── alliance_service.py
│   ├── app_service.py
│   ├── auth_service.py
│   ├── bank_service.py
│   ├── command_dispatcher.py
│   ├── company_service.py
│   ├── ... (其他服务)
│   └── time_service.py
├── commands/                   # CLI命令 (按功能模块组织)
│   ├── base.py                 # 命令基类
│   ├── registry.py             # 命令注册表
│   ├── admin/
│   ├── alliance/
│   ├── apps/
│   ├── bank/
│   ├── ... (其他命令模块)
│   └── world/
└── tests/                      # 测试代码 (镜像项目结构)
    ├── conftest.py
    ├── commands/
    ├── models/
    └── services/
```

---

### **三、开发与部署 (Development & Deployment)**

*   **版本控制**: 采用 Git 进行版本控制，并遵循 **Git Flow** 分支模型（`main`, `develop`, `feature/`, `release/`, `hotfix/`）。
*   **持续集成 (CI)**: 在 `.github/workflows/ci.yml` 中配置 GitHub Actions。每当有代码推送到 `develop` 分支或创建 Pull Request 时，自动执行以下任务：
    1.  安装依赖。
    2.  运行代码格式化与静态分析检查 (Black, Ruff, mypy)。
    3.  运行所有单元测试和集成测试 (Pytest)。
*   **部署**: 游戏本体为本地客户端应用，通过打包工具（如 PyInstaller）生成可执行文件分发。对于需要服务器支持的DLC（如“企业同盟”），将另行部署一个轻量级的 FastAPI/Flask 应用来处理API请求。

---

### **四、测试策略 (Testing Strategy)**

*   **单元测试 (Unit Tests)**:
    *   **目标**: 针对 `services/` 中的每个服务和核心工具类。
    *   **方法**: 使用内存中的 SQLite 数据库和模拟数据，独立测试每个方法的逻辑正确性。确保业务逻辑在隔离环境中按预期工作。
*   **集成测试 (Integration Tests)**:
    *   **目标**: 针对 `commands/` 中的每个命令，测试从用户输入到完成一次完整操作的整个流程。
    *   **方法**: 模拟用户输入，调用 `CommandDispatcher`，验证数据库状态的改变、外部API的调用（使用mock）以及最终输出是否符合预期。
*   **端到端测试 (E2E Tests)**:
    *   **目标**: 模拟真实玩家的长时间游戏会话，执行一系列复杂的连续操作。
    *   **方法**: 编写测试脚本，模拟玩家从创建公司到IPO，再到参与全球贸易的完整路径，以发现模块间深层次的、非预期的交互问题。

***

**【开发文档终】**

至此，《芯片战争》的完整开发文档已全部完成。这份文档不仅包含了游戏的设计理念和宏大叙事，也提供了具体、可执行的技术蓝图。它将是我们从现在开始，将这个世界变为现实的共同基石。

我们随时可以启动第一行代码的编写。
        