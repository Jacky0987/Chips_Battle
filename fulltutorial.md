核心世界观
玩家并非凡人，而是一位在未来“芯片战争”的终极对决中失败，却意外重生回到战争黎明期的“先知”。凭借对未来几十年的重大科技突破、市场脉络、关键人才的记忆，玩家拥有了改写历史、铸造传奇的唯一机会。
主要货币为J$
所有文件夹与文件名不允许带复数s。
架构核心原则
- 命令驱动 (Command-Driven): 核心交互将围绕一个强大的命令行界面(CLI)展开，提供最高效、专业的沉浸式体验。
- 模块化设计 (Modular Design): 系统的每一个核心功能都将是独立的、高内聚的模块，严格遵循 models/模块名/模型名.py 的组织方式。
- 数据访问层 (Data Access Layer): 业务逻辑与数据库操作将通过严格的DAL和工作单元(Unit of Work)模式进行解耦。
- 事件驱动 (Event-Driven): 系统内部的关键活动将通过一个全局的事件总线进行广播和监听，实现模块间的低耦合通信。

---
第一部：世界基石 (The Foundation)
- 游戏流程阶段: 游戏启动前的核心架构搭建。此阶段为所有后续功能提供稳固的技术地基，创造一个“活”的世界框架。
第一章：创世与核心系统 (Genesis & Core Systems)
目标: 搭建项目的骨架，建立驱动时间流逝的引擎、模块间通信的总线，以及最底层的配置和数据库访问机制。
技术实现要点:
1. 项目结构初始化:
  - 创建核心目录：/config, /core, /models, /services, /commands, /data/definitions, /dal。
2. 配置中心 (/config/settings.py):
  - 定义 Settings 类，管理所有静态配置，并支持从环境变量或文件加载。
3. 数据访问层 (DAL):
  - 数据库引擎 (/dal/database.py): 初始化SQLAlchemy的engine和sessionmaker。
  - 工作单元 (/dal/unit_of_work.py): 实现 SqlAlchemyUnitOfWork，封装数据库会话的生命周期，作为所有服务操作数据库的唯一入口。
4. 时间引擎 (/services/time_service.py):
  - 创建 TimeService 作为游戏世界的主时钟，以固定的“tick”推进游戏时间（每tick=1小时），并广播 TimeTickEvent。
5. 事件总线 (/core/event_bus.py):
  - 实现一个全局的 EventBus，允许系统任何部分 publish(event) 一个事件，也允许任何服务 subscribe(event_type, handler) 来监听和处理，实现模块解耦。
第二章：神谕与身份 (The Oracle & Identity)
目标: 构建玩家与游戏世界交互的桥梁——命令系统，并建立一个健壮、可扩展的权限与角色系统，为游戏管理和未来扩展奠定基础。
技术实现要点:
1. 命令处理系统:
  - 命令抽象 (/commands/base.py): 定义抽象基类 Command，包含 name, aliases, description 和 execute() 方法。
  - 注册与分发 (/commands/registry.py, /services/command_dispatcher.py): 创建 CommandRegistry 自动发现并注册所有命令，CommandDispatcher 负责解析用户输入并分发给相应的命令对象执行。
2. 基础元命令:
  - 实现 help, alias, quit 等基础命令，为玩家提供基本的交互能力。
  - helpsystem是动态更新的。
3. 权限与角色 (Auth System):
  - 核心模型 (/models/auth/):
    - User: 基础用户模型，增加 role_id 外键。
    - Role: 定义角色 (e.g., "player", "admin")。
    - Permission: 定义细粒度的权限 (e.g., "command.admin.set_role")。
    - 使用多对多关联表将 Role 与 Permission 关联。
  - 认证服务 (/services/auth_service.py):
    - 创建 AuthService，负责用户登录、密码验证，并提供核心的授权检查装饰器 permission_required(permission_name)。
4. 管理员模块 (Pluggable DLC):
  - 命令 (/commands/admin/): 实现 role list, user list, user set_role 等强大的管理命令。
  - DLC 设计: 此模块必须设计为可独立增删。所有命令必须通过 sudo 提权执行，sudo 在执行时会调用 AuthService 进行严格的管理员角色和权限验证。
执行方式类似 sudo role list，sudo开头的指令就进行验证（一次性 验证通过可以执行 sudo exit退出管理员模式）
5. User Manager
  - 贯穿整个游戏的用户管理系统，通过调用dal层等实现用户登录，记录等实现隔离
  - 实现独立的UUID记录，通过uuid进行索引名字密码等关键参数。
  - 用户的信息？包含什么方面？
6. Achievement Manager
成就管理系统，预留接口。
第2章 Extra ：应用市场 (App Market)
目标: 引入一个基础的应用市场，作为玩家早期获取信息、提升效率的核心渠道。
核心理念: 借鉴 refactor/apps/ 和 refactor/features/app_market.py 的成功实践。应用市场是玩家增强自身能力的第一个窗口。它不直接创造财富，但能极大地放大玩家决策的准确性和效率。用命令行的方式展现一个类图形的展示方式，类似于早期Mac OS。
技术实现要点:
1. 模型 (/models/apps/):
  - App (app.py): 定义 App ORM模型，包含 id, name, description, price。
  - UserAppOwnership (ownership.py): 一个简单的关联模型，用于记录哪个用户拥有哪个App。
2. 数据 (/data/definitions/apps.json):
  - 定义一个JSON文件，存储所有基础应用的元数据。例如：
    - advanced_calculator: 用于复杂金融计算。
    - news_terminal_pro: 提供更强大的新闻搜索和过滤功能。
    - market_analyzer_v1: 提供基础的市场情绪分析。
3. 服务 (/services/app_service.py):
  - 创建 AppService，负责从JSON加载应用信息、处理玩家的购买请求、以及查询玩家是否拥有特定应用。
4. 命令 (/commands/apps/):
  1. 执行market.app之后出现 (market.app)@{user_name}$> -------
  - List用于展示所有app，buy <app_id> 购买
  
  - 主界面点击进入我拥有的app界面，或用app list进入
  - app list: 显示玩家已经拥有的应用。
  - app <app_name.app>: 应用名统一为xxx.app 执行此命令如app chart.app可以启动它。
第二部：第一桶金 (Part II: The First Pot of Gold)
- 游戏流程阶段: 玩家完成身份创建后，进入游戏世界，首要目标是积累原始资本。此阶段的核心是围绕银行系统和初级股票市场 (JCMarket) 进行的金融活动。
第三章：金融中枢 (The Financial Hub)
目标 : 建立一个强大、真实的金融系统，作为整个游戏经济的基石。这包括多币种支持和功能完备的银行服务，为玩家提供管理资金、获取杠杆的核心工具。
技术实现要点 :
1. 核心货币体系，三种名称：简称：J$/全称：Jacky Yuan/统一标识符：JCY
2. 多币种体系 :
  - 核心模型 ( /models/finance/currency.py ) : 定义 Currency 模型，包含 name , code (e.g., "USD", "CNY"), symbol , 和对标 J$ 的 exchange_rate 。
  - 数据定义 ( /data/definitions/currencies.json ) : 初始化多种世界主要货币及其初始汇率。
  - 核心服务 ( /services/currency_service.py ) : 创建 CurrencyService ，负责处理所有货币兑换计算，并响应 TimeTickEvent 来模拟汇率的随机波动。
3. 银行系统 :
  金融体系：银行机构
  中央银行
  - 完整名: 杰克币人民银行 (People's Bank of JackyCoin)
  - 缩写: PBJC
  核心职能 (Core Function) :
  - 利率调控 (Interest Rate Control) : JC-FED是唯一的货币政策制定者。它通过设定“联邦基准利率 (Federal Funds Rate)”，直接影响整个金融市场的借贷成本。当JC-FED宣布加息或降息时，会成为头条新闻事件，所有商业银行的贷款和存款利率都会随之浮动。
  - 市场稳定器 (Market Stabilizer) : 在金融危机期间，JC-FED会扮演“最后贷款人”的角色，向陷入困境的系统重要性银行注入流动性，以防止金融崩溃。
  - 监管机构 (Regulator) : 负责监管其他商业银行的合规性，确保金融系统的健康运行。

---
  六大银行
  - 完整名: 杰克币工商银行 (Industrial and Commercial Bank of JC)
  - 缩写: ICBJC
  - 业务侧重: 企业金融 - 为大型企业和工业项目提供贷款。
  
  - 完整名: 杰克币建设银行 (JC Construction Bank)
  - 缩写: JCCB
  - 业务侧重: 基础设施与房地产 - 建筑和地产开发贷款的首选。
  
  - 完整名: 杰克币农业银行 (Agricultural Bank of JC)
  - 缩写: ABJC
  - 业务侧重: 农业与商品 - 在农产品、矿产等大宗商品领域有优势。
  
  - 完整名: 杰克币银行 (Bank of JackyCoin)
  - 缩写: BJC
  - 业务侧重: 国际业务与外汇 - 处理全球贸易和货币兑换的最佳选择。
  
  - 完整名: 杰克币交通银行 (Bank of Communications JC)
  - 缩写: BCOJC
  - 业务侧重: 交通物流与贸易 - 专注于运输、物流和供应链融资。
  
  - 完整名: 杰克币邮政储蓄银行 (Postal Savings Bank of JC)
  - 缩写: PSBJC
  - 业务侧重: 零售与个人业务 - 网点最广，面向个人和小微企业，是初期的主要银行。
  
  - 核心模型 ( /models/finance/ ) :
    - BankCard ：银行卡是银行系统的核心，玩家需要先申请银行卡才能进行各类银行操作。每张卡都与特定银行关联，并记录卡号、持卡人、银行等信息。
    - BankAccount ：存储玩家在不同银行、不同币种的存款，与银行卡关联。
    - Loan ：记录玩家的贷款信息，包括金额、利率、期限、已还款等。
    - CreditProfile ：玩家的信用档案，记录信用评分，影响贷款额度和利率。
    - BankTask ：银行发布的任务，玩家可以通过完成任务获得奖励或提升信用评分。
  - 核心服务 :
    - BankService ( /services/bank_service.py ) : 提供 deposit ， withdraw ， transfer ， take_loan ， repay_loan 等核心银行操作，并支持银行任务的发布和管理。
    - CreditService ( /services/credit_service.py ) : 根据玩家的资产、还款历史等，动态计算和更新其信用分。
    - BankTaskService ( /services/bank_task_service.py ) : 负责生成、分发和验证银行任务的完成情况。
  - 银行命令 ( /commands/bank.py ) :
    - bank ：显示所有银行账户的概览。
    - bank apply_card <bank_name> ：申请指定银行的银行卡。
    - bank deposit ：存款。
    - bank withdraw ：取款。
    - bank loan ：申请贷款。
    - bank repay <loan_id> ：偿还贷款。
    - bank task list ：查看当前可接取的银行任务。
    - bank task accept <task_id> ：接受指定的银行任务。
    - bank task submit <task_id> ：提交已完成的银行任务。
第四章：JCMarket 初体验 (First Steps in JCMarket)
目标: 引入一个动态的、由新闻驱动的初级股票市场 (JCMarket)，让玩家熟悉基本的市场交易，并作为早期资金增值的主要途径。
技术实现要点:
1. 动态新闻系统:
  - 核心模型 (/models/news.py): 定义 News 模型，包含 headline, body, timestamp, 以及最重要的 impact_tags (e.g., ["tech+", "finance-"])。
  - 新闻模板 (/data/definitions/news_templates.json): 创建大量新闻模板，包含可变占位符 (e.g., "【公司】的【产品】发布会取得巨大成功")，用于动态生成新闻。
  - 核心服务 (/services/news_service.py): NewsService 监听 TimeTickEvent，有一定几率根据模板生成新的新闻条目，并广播 NewsPublishedEvent。
2. JCMarket 实现:
  - 核心模型 (/models/stock.py):
    - Stock: 定义股票基本信息，如 ticker, company_name, industry。

    "name": "Adobe Inc.",
    "price": 494.63,
    "change": -9.75,
    "sector": "Technology",
    "volatility": 0.025,
    "market_cap": 220000000000,
    "pe_ratio": 43.58,
    "volume": 2958616,
    "beta": 1.2,
    "dividend_yield": 0.0,
    "price_history": [
      534.73
    ],
    "eps": 11.35,
    "last_updated": "2025-06-10T09:22:19.666014+00:00" 帮我增加特征，使其更贴近现实。
    - StockPrice: 记录某支股票在特定时间点的价格。
  - 数据定义 (/data/definitions/jc_stocks.json): 初始化 JCMarket 的上市公司列表。
  - 核心服务 (/services/stock_service.py):
    - StockService 是市场的核心驱动。它监听 TimeTickEvent 来引入微小的随机价格波动。
    - 同时，它监听 NewsPublishedEvent，检查新闻的 impact_tags，并对相关行业或公司的股票价格产生显著影响，实现“新闻驱动市场”。
  - 股票命令 (/commands/stock.py):
    - news: 查看最新的财经新闻。
    - stock list: 列出 JCMarket 的所有股票。
    - stock view <ticker>: 查看特定股票的详细信息和历史价格图表。
    - stock buy <ticker> <shares>: 购买股票。
    - stock sell <ticker> <shares>: 出售股票。
    - portfolio: 查看当前持仓。

    
第三部：财富扩张 (Part III: Wealth Expansion)
- 游戏流程阶段: 当玩家通过初级市场和银行系统积累了第一笔可观的财富后（例如，流动资产达到 1,000,000 J$），游戏将引导其进入更广阔的投资领域。此阶段的核心是“消费升级”和“资产配置”，解锁应用市场和家园体系。
第五章：应用市场与高级交易 (App Market & Advanced Trading)
目标: 引入一个可扩展的应用生态系统，玩家可以通过购买和使用各种软件工具来增强其信息获取和交易执行能力，从而深化游戏策略。
技术实现要点:
1. 解锁机制:
  - 当玩家的 BankAccount 总余额首次超过设定的阈值（e.g., 1,000,000），系统会触发一个一次性事件，提示玩家可以“升级计算机硬件”，从而解锁“应用市场”功能。
2. 应用市场实现:
  - 核心模型 (/models/app/):
    - App: 定义应用的基本信息，如 name, description, price, category (e.g., "Trading", "Data Analysis")。
    - UserAppOwnership: 记录玩家拥有的应用。
  - 数据定义 (/data/definitions/apps.json):
    - 定义所有可用的应用程序。例如：
      - 高级图表分析工具: 解锁更详细的股票技术指标。
      - 新闻情感分析器: 自动分析新闻的潜在市场影响。
      - 限价单机器人: 解锁 stock 命令的限价单功能。
  - 核心服务 (/services/app_service.py):
    - AppService 负责处理应用的购买逻辑，并提供查询玩家是否拥有特定应用的功能。
  - 相关命令 (/commands/app.py, /commands/stock.py):
    - computer upgrade: 执行一次性的升级操作，解锁应用市场。
    - app market: 查看所有可购买的应用。
    - app buy <app_name>: 购买应用。
    - app list: 查看已拥有的应用。
    - stock 命令扩展：buy 和 sell 子命令将增加 --limit <price> 和 --stop-loss <price> 等参数。在执行时，命令会先通过 AppService 检查玩家是否已购买相应功能的应用，否则操作失败。
第六章：家园体系与实物资产 (The Home System & Physical Assets)
目标: 引入房地产和奢侈品等实物资产，作为玩家财富的重要组成部分和价值储存手段，完美契合 new.md 中“做好资产分配，进军房地产”的核心理念。
技术实现要点:
1. 解锁机制:
  - 当玩家购买第一处房产后，“家园”标签页将在主界面解锁。
2. 家园系统实现:
  - 核心模型 (/models/home/personal_asset.py):
    - PersonalAsset: 一个通用的实物资产模型，包含 name, type ("Real Estate", "Luxury Car", "Art"), purchase_price, current_value, 以及一个 value_update_rule 字段（e.g., a small formula or set of tags indicating how its value changes）。
  - 数据定义 (/data/definitions/personal_assets.json):
    - 定义一个包含全球主要城市地标房产、限量版跑车、传世艺术品等的市场。
  - 核心服务 (/services/home_service.py):
    - HomeService 监听 TimeTickEvent，根据每个资产的 value_update_rule 和全局经济事件（e.g., 房地产市场繁荣/萧条）来定期更新其 current_value。
  - 相关命令 (/commands/home.py):
    - home market: 查看当前可购买的房产和奢侈品。
    - home buy <asset_id>: 购买一项资产。
    - home assets: 显示玩家当前拥有的所有实物资产及其总价值。
    - home sell <asset_id>: 出售已拥有的资产。
第四部：企业帝国 (Part IV: The Corporate Empire)
- 游戏流程阶段 : 当玩家的财富和影响力达到一个新的高度后（例如，总资产超过 10,000,000 J$），游戏将引导其创立自己的第一家公司。这标志着玩家身份的根本转变——从资本的投机者，到价值的创造者和产业的塑造者。这不再仅仅是中后期玩法，而是游戏真正的核心，一个深度、复杂且充满挑战的经营模拟篇章。
第七章：从车库到巨头 (From Garage to Goliath)
目标 : 构建一个贯穿企业完整生命周期的模拟系统，从最初的创意火花到全球性的商业帝国，并引入真实的经营困境与挑战。
技术实现要点 :
阶段一：初创期 (The Startup Phase)
1. 
解锁与创立 :
  - 达到资产阈值后，玩家将解锁 company create 命令。
  - company create <公司名> --industry <行业代码> --capital <启动资金> : 投入一笔启动资金，在特定行业（如半导体、软件、生物科技）创立第一家公司。选择的行业将决定初始的科技树和市场环境。
2. 2.
核心模型 ( /models/company/ ) :
  
  - Company : 公司的核心实体，包含财务报表（现金、资产、负债、收入、利润）、员工、科技水平、市场声誉、总部等级等。
  - Industry : 定义行业及其特定的科技树、市场需求和监管环境。
  - Technology : 可被公司研发的具体技术，是解锁更高级产品的前提。
  - ProductBlueprint : 玩家设计的产品蓝图，结合了已研发的技术，决定了产品的性能、成本和市场吸引力。
  - ProductionLine : 公司建造的生产线，用于将产品蓝图转化为实际的库存。
  - InventoryItem : 库存中的待售商品。
3. 3.
数据定义 ( /data/definitions/ ) :
  
  - industries.json : 定义所有可选行业及其特性。
  - technologies.json : 定义完整的、跨行业的科技树。
4. 4.
核心服务 :
  
  - CompanyService ( /services/company_service.py ): 管理公司的财务、招聘、日常运营和扩张。
  - TechnologyService ( /services/technology_service.py ): 处理科技研发的逻辑和进度。
  - ProductionService ( /services/production_service.py ): 管理生产线的建造和产品生产。
5. 5.
初创期核心命令 ( /commands/company.py ) :
  
  - company status : 查看公司财务、运营和库存的详细报告。
  - company research <技术名> : 投入资金研发新技术。
  - company design <产品名> --tech <tech1,tech2...> : 设计新产品蓝图。
  - company build <生产线名> --blueprint <产品名> : 建造生产线。
  - company produce <数量> --line <生产线名> : 开始生产。
  - company sell <商品ID> <价格> : 在市场上销售库存商品。
阶段二：成长期 (The Growth Phase)
1. 1.
扩张与升级 :
  - 当公司实现持续盈利后，可以进行扩张。
  - company establish_branch <城市名> : 在全球不同城市建立分公司。分公司可以扩大市场覆盖范围，但也增加了管理成本和物流复杂度。
  - company upgrade_hq : 当公司规模达到一定程度，可以升级总部。每次升级都会解锁新的管理模块（如并购部、法务部）和全局增益效果。
阶段三：成熟与上市 (Maturity & IPO)
1. 1.
进军JCSDAQ :
  - 当公司达到严苛的财务标准（如连续三季度盈利、市值超过特定门槛）后，将解锁 company ipo 命令，允许公司在高级证券交易所 JCSDAQ 上市。
  - IPO过程将是一个复杂的多阶段任务，需要聘请投行、路演、定价，并面临被监管机构质询的风险。
2. 2.
上市后的世界 :
  - 股价联动 : JCSDAQ 上市公司的股价将与 CompanyService 中的财务数据（收入、利润、增长率、市场占有率）强相关。 StockService 将扩展其定价模型，把公司基本面作为核心影响因子。
  - 股东压力 : 上市后，玩家需要对股东负责，定期发布财报。不及预期的财报将导致股价暴跌和信任危机。
  
目标: 构建一个深度、复杂的公司经营模拟系统。玩家需要选择行业、研发科技、设计产品、建立生产线，并最终将产品推向市场，形成完整的商业闭环。
技术实现要点:
1. 解锁与创立:
  - 达到资产阈值后，玩家将解锁 company create 命令，允许其投入一笔启动资金，在特定行业（如半导体、软件、生物科技）创立第一家公司。
2. 核心模型 (/models/company/):
  - Company: 公司的核心实体，包含财务报表（现金、资产、负债、收入、利润）、员工、科技水平等。
  - Industry: 定义行业及其特定的科技树和市场需求。
  - Technology: 可被公司研发的具体技术，是解锁更高级产品的前提。
  - ProductBlueprint: 玩家设计的产品蓝图，结合了已研发的技术，决定了产品的性能和成本。
  - ProductionLine: 公司建造的生产线，用于将产品蓝图转化为实际的库存。
  - InventoryItem: 库存中的待售商品。
3. 数据定义 (/data/definitions/):
  - industries.json: 定义所有可选行业及其特性。
  - technologies.json: 定义完整的、跨行业的科技树。
4. 核心服务:
  - CompanyService (/services/company_service.py): 管理公司的财务、招聘和日常运营。
  - TechnologyService (/services/technology_service.py): 处理科技研发的逻辑和进度。
  - ProductionService (/services/production_service.py): 管理生产线的建造和产品生产。
5. 公司命令 (/commands/company.py):
  - company create <name> --industry <industry_name>: 创建新公司。
  - company status: 查看公司财务、运营和库存的详细报告。
  - company research <tech_name>: 投入资金研发新技术。
  - company design <product_name> --tech <tech1,tech2...>: 设计新产品蓝图。
  - company build <production_line_name> --blueprint <product_name>: 建造生产线。
  - company produce <amount> --line <line_name>: 开始生产。
  - company sell <item_id> <price>: 在市场上销售库存商品。
第八章：跨界征服 (Cross-Industry Conquest) - 详细扩展
目标: 在主营业务（如科技、制造）获得市场领导地位后，玩家将解锁将公司资本部署到全新领域的能力。这不仅仅是多元化投资，而是创建新的、专业的子公司，深度参与到金融、地产等行业的运作中，构建一个真正无法被撼动的、跨领域协同的商业帝国。
核心机制: 玩家需要通过 company establish_subsidiary <子公司名> --industry <新行业代码> 命令来创建专营特定业务的子公司。每个子公司都拥有独立的财务报表，但其利润和亏损最终会合并到母公司的财报中。

---
8.1 进军房地产 (Entering Real Estate)
业务模式: 从被动的商业地产持有者，转变为主动的房地产开发商。
- 目标: 模拟完整的房地产开发价值链，从土地竞拍、规划设计、建筑施工到最终的营销和销售，体验高杠杆、长周期、高风险和高回报的地产游戏。
- 核心模型 (/models/real_estate/):
  - LandPlot: 代表一块可供开发的土地。属性包括：location (地理位置，影响最终售价), zoning_type (区域规划，如住宅、商业、工业), plot_size (地块面积), acquisition_cost (购置成本)。
  - BuildingBlueprint: 建筑蓝图。属性包括：type (如经济公寓、豪华别墅、写字楼、购物中心), construction_cost_per_sqm (单位面积建造成本), construction_time (建造周期), capacity (可容纳户数或商铺数)。
  - RealEstateProject: 一个具体的开发项目。它将一块 LandPlot 和一个 BuildingBlueprint 结合起来，并跟踪 status (规划中、建设中、预售中、已竣工), construction_progress (建设进度), budget (预算), units_sold (已售单位) 等。
- 核心服务 (/services/real_estate_service.py):
  - RealEstateService 负责管理土地市场。它会定期（如每季度）向市场投放新的 LandPlot，并以拍卖形式出售。
  - 服务将模拟政府审批流程。玩家提交开发申请后，需要经过一个有概率失败的审批周期。审批结果可能受城市发展规划、环境评估等随机事件影响。
  - 服务将与 NewsService 深度联动。例如，“央行加息”新闻会直接增加项目的融资成本并压低市场需求；“新经济区规划出台”新闻则会使特定区域的 LandPlot 价值飙升。
- 命令 (/commands/real_estate.py):
  - realty market plots: 查看当前土地市场所有可供竞拍的地块。
  - realty bid <plot_id> <amount>: 对指定地块进行竞价。
  - realty develop <plot_id> --blueprint <blueprint_id>: 获得土地后，选择一个建筑蓝图开始开发项目。
  - realty project status <project_id>: 查看开发项目的详细进度、预算使用情况和销售情况。
  - realty presale <project_id> --price <price_per_unit>: 在项目建设到一定阶段后（如30%），开启预售回笼资金。
  - realty sell <unit_id>: 在竣工后，向市场销售单个单位（公寓、商铺等）。

---
8.2 & 8.3 驾驭商品与期货 (Mastering Commodities & Futures)
业务模式: 成立企业级的交易部门，利用信息优势和资本规模进行套期保值和战略投机。
- 目标: 将公司的交易行为与其实体业务相结合。如果公司是半导体制造商，其交易部就应该能通过交易铜、稀土等期货来对冲原材料成本上涨的风险。
- 核心模型 (/models/corporate_trading/):
  - CorporatePortfolio: 一个独立于玩家个人账户的企业投资组合，能够持有更大规模的现货和期货头寸。
  - HedgingStrategy: 一个由AI驱动的分析模型。当公司建立生产线时，该模型会自动分析其上游原材料，并向玩家提出对冲建议。例如：“为对冲未来6个月的芯片生产成本，建议买入X手铜期货合约”。
- 核心服务 (/services/corporate_trading_service.py):
  - 该服务为企业账户提供更低的交易费用、更高的交易限额和更快的执行速度。
  - 它会生成专业的风险报告，分析公司在商品市场的风险敞口，并根据VaR（风险价值）模型给出警告。
  - 与 CompanyService 集成，交易部门的巨额盈利或亏损将直接影响公司季度财报，并最终反映在股价上。
- 命令 (/commands/corporate_trading.py):
  - ctrade buy/sell <symbol> <quantity> --market [spot|futures]: 以公司名义执行大宗交易。
  - ctrade portfolio: 查看公司的持仓详情和盈亏状况。
  - ctrade hedge-analysis: 运行套期保值分析，获取针对公司业务的对冲策略建议。

---
8.4 创立资产管理 (Launching Asset Management)
业务模式: 从自己赚钱，到帮别人管钱。
- 目标: 模拟成立和运营一家基金公司的全过程。这是一种轻资产、高利润的业务，但极度依赖市场声誉和基金经理（即玩家）的投资能力。
- 核心模型 (/models/asset_management/):
  - ManagedFund: 定义一只由玩家公司管理的基金。属性包括：name, strategy_desc (投资策略描述，如“专注于AI和生物科技的成长型基金”), AUM (资产管理规模), NAV (单位净值), management_fee (管理费率), performance_fee (业绩提成费率)。
  - FundInvestor: 记录了所有投资该基金的外部投资者（其他玩家或AI）及其份额。
- 核心服务 (/services/asset_management_service.py):
  - AssetManagementService 负责每日计算和更新基金的 NAV。
  - 它处理外部投资者的申购 (subscription) 和赎回 (redemption) 请求。
  - 定期（如每季度）自动从基金资产中扣除管理费，并在基金表现超过基准时（如JCSDAQ指数）提取业绩提成，这些都将成为母公司的收入。
  - 监管机制: 如果基金出现持续亏损或违背其宣称的投资策略，将触发“监管调查”事件，可能导致罚款甚至吊销牌照。
- 命令 (/commands/asset_management.py)`):
  - assetmgr create-fund --name <name> --strategy "<description>": 设立一只新基金。
  - assetmgr status <fund_id>: 查看基金的详细信息，包括AUM、NAV历史走势、持仓等。
  - assetmgr report <fund_id>: 生成一份专业的基金季报，用于吸引新的投资者。
  - （其他玩家或AI将使用 invest <fund_id> <amount> 命令来投资你的基金）

---
8.5 & 8.6 探索前沿金融 (Exploring Financial Frontiers: Insurance & DeFi)
业务模式: 进入最高风险、最复杂的金融领域。
- e. 保险业务 (Insurance Business):
  - 目标: 模拟保险公司的核心商业模式——收取保费，承担风险，并投资“浮存金”来盈利。
  - 玩法: 玩家可以成立保险子公司，设计保险产品（如“生产线停工险”、“IPO失败险”）。你需要建立精算模型来为风险定价（即设定保费）。当其他玩家或AI购买你的保险后，如果发生合同约定的负面事件，你就必须进行赔付。这是一场对概率和风险管理的终极考验。
- f. 去中心化金融 (DeFi):
  - 目标: 将公司的部分金库投入到高收益但也高风险的DeFi世界。
  - 玩法: 成立一个专门的加密资产投资部门。你可以将公司的现金兑换成稳定币，然后投入到各种DeFi协议中：
    - 流动性挖矿: 在去中心化交易所（DEX）为交易对（如 FED$/JCoin）提供流动性，赚取交易费和协议代币奖励。
    - 借贷: 在去中心化借贷平台存入资产以赚取利息，或抵押资产借出其他代币进行更复杂的操作。
    - 风险: 必须时刻警惕智能合约漏洞（可能导致资金被盗的随机事件）和无常损失（在提供流动性时，代币价格剧烈波动造成的损失）。

  - commodity list: 列出所有可交易商品。
  - commodity view <symbol>: 查看特定商品的实时价格和历史图表。
  - commodity buy/sell <symbol> <quantity>: 进行现货交易。
1. 期货市场 (Futures Market):
  - 核心模型 (/models/futures/):
    - FuturesContract: 定义一份期货合约。属性包括 underlying_commodity (标的商品), contract_size, expiration_date, strike_price, current_price, long_position_holder, short_position_holder。
  - 核心服务 (/services/futures_service.py):
    - FuturesService 负责创建新的期货合约（通常是每月或每季度到期），管理合约的交易和持仓，并在到期日进行结算。结算时，会根据到期日的现货价格与合约价格的差额，从赢家的账户向输家的账户转移资金。
    - 价格驱动：期货价格紧密跟踪其标的商品的现货价格，并加上持有成本（如仓储费、利息）和市场情绪溢价。
  - 命令 (/commands/futures.py):
    - futures list: 列出当前所有有效的期货合约。
    - futures view <contract_id>: 查看特定合约的详细信息。
    - futures buy/sell <contract_id> <quantity>: 开立多头或空头仓位。
    - futures position: 查看玩家当前持有的所有期货仓位。

第九章：帝国的黄昏 (The Twilight of an Empire)
目标 : 引入真实的企业经营困境、衰退与终结机制，让游戏充满不确定性，增加经营层面的细节与难度。

技术实现要点 :
1. 1.
   经营危机 (Operational Crisis) :
   - 负面事件 : 随机或由玩家决策不当触发的负面事件（如供应链中断、关键技术人员离职、产品重大缺陷、法律诉讼）将持续考验公司的应变能力。
   - 现金流断裂 : 如果公司现金流为负，将无法支付员工工资、供应商货款和银行利息，导致员工忠诚度下降、生产停滞，信用评级被下调。
2. 2.
   倒闭流程 (Bankruptcy) :
   - 当公司资不抵债时，将被强制触发破产清算程序。
   - company declare_bankruptcy : 玩家也可以主动申请破产。
   - 后果 : 所有公司资产将被冻结并由系统接管进行拍卖，以偿还债务。玩家作为创始人，其个人声誉、银行信用将遭受毁灭性打击，并可能在一段时间内被禁止再次创建公司。
3. 3.
   注销流程 (Voluntary Deregistration) :
   - 如果一个公司虽然没有破产，但已失去发展前景或玩家希望战略收缩，可以选择主动注销。
   - company liquidate : 这是一个有序的清盘过程。玩家需要自行出售所有资产、解雇员工、偿还债务。
   - 后果 : 相比破产，主动注销对玩家的负面影响较小，允许玩家回收部分剩余价值，为东山再起保留火种。
第五部：全球统治 (Part V: Global Dominion)
- 游戏流程阶段: 玩家的公司已成为行业巨头，并主宰了JCSDAQ。此时，游戏进入终局阶段，玩家的目标将从建立企业扩展到重塑全球经济格局，与其他超级企业和国家力量进行直接对抗。
第X章：全球棋局与资本战争 (The Global Chessboard & Capital Wars)
目标: 引入宏观经济和跨国公司间的终极对抗。玩家将参与并购、恶意收购，并在全球范围内配置资源，与其他巨头争夺产业链的控制权。
技术实现要点:
1. 跨国并购 (M&A):
  - 核心服务 (/services/merger_service.py):
    - MergerService 负责处理复杂的并购逻辑，包括估值、谈判（一个基于成功率和多轮出价的迷你游戏）、以及股东投票。
    - 玩家可以对 JCMarket 或 JCSDAQ 上的任何非玩家控股公司发起收购要约。
  - 恶意收购:
    - 玩家可以在二级市场上秘密吸筹，当持股比例超过特定阈值（e.g., 5%）时，可以发起代理权战争或直接的恶意收购，这将引发目标公司管理层的激烈反抗。
2. 全球化运营:
  - 模型扩展: Company 模型增加 global_operations 字段，记录在不同国家/地区的子公司和资产。
  - 地缘政治事件: NewsService 将生成影响特定国家或地区经济的宏观事件（如贸易战、经济制裁、技术封锁），直接影响玩家跨国公司的运营效率和盈利能力。
3. 相关命令 (/commands/corpwar.py):
  - corp offer buy <ticker> --price <price_per_share>: 发起一个友好的收购要约。
  - corp hostile takeover <ticker>: 发动一场恶意的收购战争。
  - corp expand <country_code>: 在新的国家建立分公司，开拓海外市场。
第XI章：人才战争与第四次工业革命 (The War for Talent & The Fourth Industrial Revolution)
目标: 引入“人”作为核心战略资源，并设计能够颠覆游戏规则的终极科技，让玩家为最终目标做准备。
技术实现要点:
1. 关键人才系统 (Key Personnel):
  - 核心模型 (/models/hr/):
    - Talent: 定义游戏中的关键人才（如明星CEO、顶尖科学家），他们拥有独特的技能和属性，能极大地增幅公司特定领域的表现。
  - 核心服务 (/services/hr_service.py):
    - HRService 管理一个全局的人才市场，玩家可以通过 headhunt 命令高薪挖角。
    - 将人才分配到公司后，其技能会自动生效（e.g., 一个“供应链大师”CEO可以降低所有生产成本）。
2. 终局科技 (Endgame Technologies):
  - TechnologyService 将包含一个特殊的“第四次工业革命”科技树，其中包含如“强人工智能”、“可控核聚变”、“量子计算”等颠覆性技术。
  - 研发这些技术需要巨量的资本和前置科技，但一旦完成，将给予玩家不对称的巨大优势，例如解锁全新的、利润极高的产业。
3. 相关命令 (/commands/hr.py, /commands/company.py):
  - hr market: 查看当前可供招聘的人才。
  - hr headhunt <talent_id> --offer <salary>: 尝试挖角一名人才。
  - company assign <talent_id> --position <CEO|CTO...>: 任命人才。

第六部：DLC
DLC1：影子战争 (The Shadow War)
目标: 作为一个完全独立、可插拔的DLC模块，为游戏增加一层信息战、商业间谍和暗中破坏的玩法，满足喜爱高风险、高回报策略的玩家。
技术实现要点:
1. 情报机构:
  - 玩家可以创建自己的“情报部门”，这是一个特殊的公司类型。
  - 核心模型 (/models/intelligence/): Spy, Intel, CovertOp。
  - 核心服务 (/services/intelligence_service.py): 管理间谍的招募、培训和任务派遣。
2. 谍报活动:
  - 窃取技术: 派遣间谍窃取竞争对手正在研发的技术。
  - 市场操纵: 散播关于竞争对手的虚假负面消息，以打压其股价。
  - 破坏活动: 对竞争对手的生产线进行物理或网络破坏。
  - 反间谍: 部署自己的安保力量，抓捕对方的间谍。
3. 相关命令 (/commands/intel.py):
  - intel recruit: 招募新的间谍。
  - intel dispatch <spy_id> --op <StealTech|Sabotage> --target <company_id>: 派遣间谍执行任务。
  - intel report: 查看所有情报任务的报告。
DLC 2: 企业同盟 (Corporate Alliance)
核心目标: 引入“远程联机，本地存档”的轻度多人协作模式。玩家可以与其他玩家组成同盟，共同应对更强大的AI派系或完成宏伟的合作项目。
技术实现:
- 网络层 (services/network_service.py):
  - 职责: 处理玩家间的非实时数据同步。采用一个轻量级的API服务器来交换同盟状态、共享资金、项目进度等信息。
  - 数据同步: 玩家上线时，客户端会向服务器请求同盟的最新数据并更新本地存档。玩家的本地操作（如向同盟金库注资）会异步推送到服务器。这种设计避免了对强实时同步的需求。
- 模型层 (models/alliance/):
  - alliance.py: 定义一个企业同盟。
    - 属性: name, members (成员列表), shared_treasury (共享金库), alliance_tech_tree (同盟独有的科技树), joint_ventures (合作项目列表)。
  - joint_venture.py: 定义一个合作项目，如“建造全球超高速铁路网”。需要多个成员共同投资和贡献资源才能完成。
- 服务层 (services/alliance_service.py):
  - 同盟管理: 处理创建、邀请、加入、退出同盟的逻辑。
  - 金库与治理: 管理共享金库的资金流动，并可实现一套简单的投票系统来决定重大事项。
  - 项目驱动: 驱动合作项目的进展，根据成员的贡献更新项目状态，并在项目完成时给予所有参与者丰厚的回报。
- 命令层 (commands/alliance_commands.py):
  - alliance [create|invite|join|status]: 管理同盟。
  - alliance deposit [amount]: 向同盟金库注资。
  - alliance venture [start|contribute|status]: 管理合作项目。

---
DLC 3: 地缘棋局 (Geopolitical Chess)
核心目标: 将基础游戏中的“国家”概念深化，允许玩家通过经济和科技实力深度干预国际政治，从而为自己的商业帝国谋求战略优势。
技术实现:
- 模型层 (models/nation/):
  - nation.py: 扩展国家模型，加入更多政治属性。
    - 新增属性: government_type (政体), policies (政策字典，如税率、关税、环保法规), stability (稳定度), relations (与其他国家的关系), player_influence (玩家对该国的影响力)。
  - policy.py: 定义具体的国家政策及其对经济和游戏世界的影响。
- 服务层 (services/politics_service.py):
  - 政治模拟: 模拟各国的内部政治动态。例如，在民主国家，选举会定期举行，玩家可以通过政治献金支持符合自己利益的候选人。
  - 游说系统: 玩家可以花费资金和影响力，对特定国家的特定政策进行游说，以期推动有利于自己的法规出台（如降低奢侈品消费税）。
  - 国际关系: 国家间的关系会动态变化，可能爆发贸易战、组建贸易同盟等。这些事件将作为高级新闻由 news_service 发布，并对全球市场产生深远影响。
- 命令层 (commands/nation_commands.py):
  - nation status [nation_name]: 查看一个国家的详细状态。
  - nation lobby [nation_name] --policy [policy_name] --action [support|oppose]: 对某项政策进行游说。

---
DLC 4: 传媒帝国 (Media Empire)
核心目标: 允许玩家收购、建立和运营媒体集团，将“信息”本身作为一种强大的武器，用于引导舆论、影响市场、甚至对竞争对手发起舆论攻击。
技术实现:
- 模型层 (models/media/):
  - media_outlet.py: 定义一个媒体实体，如电视台、报社、社交媒体平台。
    - 属性: name, reach (受众规模), credibility (公信力), bias (立场倾向), owner (所有者)。
- 服务层 (services/media_service.py):
  - 内容生产: 与 news_service 深度绑定。当玩家控制一个媒体后，可以下令“制造”新闻。
  - 舆论引擎: 玩家可以发起一场“公关活动”或“舆论攻击”。例如，发布一篇吹捧自己公司新技术的文章，或是一篇揭露对手公司财务问题的深度报道。
  - 效果模拟: 发布的新闻会通过 news_service 传播。其影响力取决于媒体的公信力和受众规模。一条成功的正面报道可以显著提升公司股价和产品销量；而一条成功的负面报道则可能引发对手的公关危机，导致其股价暴跌。
- 命令层 (commands/media_commands.py):
  - media list: 查看全球可收购的媒体列表。
  - media acquire [outlet_name]: 发起对一个媒体的收购。
  - media campaign [outlet_name] --target [company_name] --type [positive|negative] --topic "[topic]": 发起一场舆论活动。