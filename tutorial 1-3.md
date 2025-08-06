Game：Chips Battle Remake ver：3.0 alpha
核心世界观
玩家并非凡人，而是一位在未来“芯片战争”的终极对决中失败，却意外重生回到战争黎明期的“先知”。凭借对未来几十年的重大科技突破、市场脉络、关键人才的记忆，玩家拥有了改写历史、铸造传奇的唯一机会。
主要货币为J$
所有文件夹与文件名不允许带复数s。
架构核心原则
命令驱动 (Command-Driven): 核心交互将围绕一个强大的命令行界面(CLI)展开，提供最高效、专业的沉浸式体验。
模块化设计 (Modular Design): 系统的每一个核心功能都将是独立的、高内聚的模块，严格遵循 models/模块名/模型名.py 的组织方式。
数据访问层 (Data Access Layer): 业务逻辑与数据库操作将通过严格的DAL和工作单元(Unit of Work)模式进行解耦。
事件驱动 (Event-Driven): 系统内部的关键活动将通过一个全局的事件总线进行广播和监听，实现模块间的低耦合通信。
第一部：世界基石 (The Foundation)
游戏流程阶段: 游戏启动前的核心架构搭建。此阶段为所有后续功能提供稳固的技术地基，创造一个“活”的世界框架。
第一章：创世与核心系统 (Genesis & Core Systems)
目标: 搭建项目的骨架，建立驱动时间流逝的引擎、模块间通信的总线，以及最底层的配置和数据库访问机制。
技术实现要点:
项目结构初始化:
创建核心目录：/config, /core, /models, /services, /commands, /data/definitions, /dal。
配置中心 (/config/settings.py):
定义 Settings 类，管理所有静态配置，并支持从环境变量或文件加载。
数据访问层 (DAL):
数据库引擎 (/dal/database.py): 初始化SQLAlchemy的engine和sessionmaker。
工作单元 (/dal/unit_of_work.py): 实现 SqlAlchemyUnitOfWork，封装数据库会话的生命周期，作为所有服务操作数据库的唯一入口。
时间引擎 (/services/time_service.py):
创建 TimeService 作为游戏世界的主时钟，以固定的“tick”推进游戏时间（每tick=1小时），并广播 TimeTickEvent。
事件总线 (/core/event_bus.py):
实现一个全局的 EventBus，允许系统任何部分 publish(event) 一个事件，也允许任何服务 subscribe(event_type, handler) 来监听和处理，实现模块解耦。
第二章：神谕与身份 (The Oracle & Identity)
目标: 构建玩家与游戏世界交互的桥梁——命令系统，并建立一个健壮、可扩展的权限与角色系统，为游戏管理和未来扩展奠定基础。
技术实现要点:
命令处理系统:
命令抽象 (/commands/base.py): 定义抽象基类 Command，包含 name, aliases, description 和 execute() 方法。
注册与分发 (/commands/registry.py, /services/command_dispatcher.py): 创建 CommandRegistry 自动发现并注册所有命令，CommandDispatcher 负责解析用户输入并分发给相应的命令对象执行。
基础元命令:
实现 help, alias, quit 等基础命令，为玩家提供基本的交互能力。
helpsystem是动态更新的。
权限与角色 (Auth System):
核心模型 (/models/auth/):
User: 基础用户模型，增加 role_id 外键。
Role: 定义角色 (e.g., "player", "admin")。
Permission: 定义细粒度的权限 (e.g., "command.admin.set_role")。
使用多对多关联表将 Role 与 Permission 关联。
认证服务 (/services/auth_service.py):
创建 AuthService，负责用户登录、密码验证，并提供核心的授权检查装饰器 permission_required(permission_name)。
管理员模块 (Pluggable DLC):
命令 (/commands/admin/): 实现 role list, user list, user set_role 等强大的管理命令。
DLC 设计: 此模块必须设计为可独立增删。所有命令必须通过 sudo 提权执行，sudo 在执行时会调用 AuthService 进行严格的管理员角色和权限验证。
执行方式类似 sudo role list，sudo开头的指令就进行验证（一次性 验证通过可以执行 sudo exit退出管理员模式）
User Manager
贯穿整个游戏的用户管理系统，通过调用dal层等实现用户登录，记录等实现隔离
实现独立的UUID记录，通过uuid进行索引名字密码等关键参数。
用户的信息？包含什么方面？
Achievement Manager
成就管理系统，预留接口。
第2章 Extra ：应用市场 (App Market)
目标: 引入一个基础的应用市场，作为玩家早期获取信息、提升效率的核心渠道。
核心理念: 借鉴 refactor/apps/ 和 refactor/features/app_market.py 的成功实践。应用市场是玩家增强自身能力的第一个窗口。它不直接创造财富，但能极大地放大玩家决策的准确性和效率。用命令行的方式展现一个类图形的展示方式，类似于早期Mac OS。
技术实现要点:
模型 (/models/apps/):
App (app.py): 定义 App ORM模型，包含 id, name, description, price。
UserAppOwnership (ownership.py): 一个简单的关联模型，用于记录哪个用户拥有哪个App。
数据 (/data/definitions/apps.json):
定义一个JSON文件，存储所有基础应用的元数据。例如：
advanced_calculator: 用于复杂金融计算。
news_terminal_pro: 提供更强大的新闻搜索和过滤功能。
market_analyzer_v1: 提供基础的市场情绪分析。
服务 (/services/app_service.py):
创建 AppService，负责从JSON加载应用信息、处理玩家的购买请求、以及查询玩家是否拥有特定应用。
命令 (/commands/apps/):
执行market.app之后出现 (market.app)@{user_name}$> -------
List用于展示所有app，buy <app_id> 购买
主界面点击进入我拥有的app界面，或用app list进入
app list: 显示玩家已经拥有的应用。
app <app_name.app>: 应用名统一为xxx.app 执行此命令如app chart.app可以启动它。
第二部：第一桶金 (Part II: The First Pot of Gold)
游戏流程阶段: 玩家完成身份创建后，进入游戏世界，首要目标是积累原始资本。此阶段的核心是围绕银行系统和初级股票市场 (JCMarket) 进行的金融活动。
第三章：金融中枢 (The Financial Hub)
目标 : 建立一个强大、真实的金融系统，作为整个游戏经济的基石。这包括多币种支持和功能完备的银行服务，为玩家提供管理资金、获取杠杆的核心工具。
技术实现要点 :
核心货币体系，三种名称：简称：J$/全称：Jacky Yuan/统一标识符：JCY
多币种体系 :
核心模型 ( /models/finance/currency.py ) : 定义 Currency 模型，包含 name , code (e.g., "USD", "CNY"), symbol , 和对标 J$ 的 exchange_rate 。
数据定义 ( /data/definitions/currencies.json ) : 初始化多种世界主要货币及其初始汇率。
核心服务 ( /services/currency_service.py ) : 创建 CurrencyService ，负责处理所有货币兑换计算，并响应 TimeTickEvent 来模拟汇率的随机波动。
银行系统 :
  金融体系：银行机构
  中央银行
完整名: 杰克币人民银行 (People's Bank of JackyCoin)
缩写: PBJC
  核心职能 (Core Function) :
利率调控 (Interest Rate Control) : JC-FED是唯一的货币政策制定者。它通过设定“联邦基准利率 (Federal Funds Rate)”，直接影响整个金融市场的借贷成本。当JC-FED宣布加息或降息时，会成为头条新闻事件，所有商业银行的贷款和存款利率都会随之浮动。
市场稳定器 (Market Stabilizer) : 在金融危机期间，JC-FED会扮演“最后贷款人”的角色，向陷入困境的系统重要性银行注入流动性，以防止金融崩溃。
监管机构 (Regulator) : 负责监管其他商业银行的合规性，确保金融系统的健康运行。
  六大银行
完整名: 杰克币工商银行 (Industrial and Commercial Bank of JC)
缩写: ICBJC
业务侧重: 企业金融 - 为大型企业和工业项目提供贷款。
完整名: 杰克币建设银行 (JC Construction Bank)
缩写: JCCB
业务侧重: 基础设施与房地产 - 建筑和地产开发贷款的首选。
完整名: 杰克币农业银行 (Agricultural Bank of JC)
缩写: ABJC
业务侧重: 农业与商品 - 在农产品、矿产等大宗商品领域有优势。
完整名: 杰克币银行 (Bank of JackyCoin)
缩写: BJC
业务侧重: 国际业务与外汇 - 处理全球贸易和货币兑换的最佳选择。
完整名: 杰克币交通银行 (Bank of Communications JC)
缩写: BCOJC
业务侧重: 交通物流与贸易 - 专注于运输、物流和供应链融资。
完整名: 杰克币邮政储蓄银行 (Postal Savings Bank of JC)
缩写: PSBJC
业务侧重: 零售与个人业务 - 网点最广，面向个人和小微企业，是初期的主要银行。
核心模型 ( /models/finance/ ) :
BankCard ：银行卡是银行系统的核心，玩家需要先申请银行卡才能进行各类银行操作。每张卡都与特定银行关联，并记录卡号、持卡人、银行等信息。
BankAccount ：存储玩家在不同银行、不同币种的存款，与银行卡关联。
Loan ：记录玩家的贷款信息，包括金额、利率、期限、已还款等。
CreditProfile ：玩家的信用档案，记录信用评分，影响贷款额度和利率。
BankTask ：银行发布的任务，玩家可以通过完成任务获得奖励或提升信用评分。
核心服务 :
BankService ( /services/bank_service.py ) : 提供 deposit ， withdraw ， transfer ， take_loan ， repay_loan 等核心银行操作，并支持银行任务的发布和管理。
CreditService ( /services/credit_service.py ) : 根据玩家的资产、还款历史等，动态计算和更新其信用分。
BankTaskService ( /services/bank_task_service.py ) : 负责生成、分发和验证银行任务的完成情况。
银行命令 ( /commands/bank.py ) :
bank ：显示所有银行账户的概览。
bank apply_card <bank_name> ：申请指定银行的银行卡。
bank deposit ：存款。
bank withdraw ：取款。
bank loan ：申请贷款。
bank repay <loan_id> ：偿还贷款。
bank task list ：查看当前可接取的银行任务。
bank task accept <task_id> ：接受指定的银行任务。
bank task submit <task_id> ：提交已完成的银行任务。
第四章：JCMarket 初体验 (First Steps in JCMarket)
目标: 引入一个动态的、由新闻驱动的初级股票市场 (JCMarket)，让玩家熟悉基本的市场交易，并作为早期资金增值的主要途径。
技术实现要点:
动态新闻系统:
核心模型 (/models/news.py): 定义 News 模型，包含 headline, body, timestamp, 以及最重要的 impact_tags (e.g., ["tech+", "finance-"])。
新闻模板 (/data/definitions/news_templates.json): 创建大量新闻模板，包含可变占位符 (e.g., "【公司】的【产品】发布会取得巨大成功")，用于动态生成新闻。
核心服务 (/services/news_service.py): NewsService 监听 TimeTickEvent，有一定几率根据模板生成新的新闻条目，并广播 NewsPublishedEvent。
JCMarket 实现:
核心模型 (/models/stock.py):
Stock: 定义股票基本信息，如 