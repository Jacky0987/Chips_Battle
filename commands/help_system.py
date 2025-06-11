class HelpSystem:
    """
    股票交易模拟器帮助系统
    提供分类的帮助信息和导航功能
    """
    
    def __init__(self, app):
        self.app = app
        self.help_categories = {
            'basic': '基础功能',
            'trading': '高级交易',
            'commodities': '大宗商品交易',
            'analysis': '市场分析', 
            'banking': '银行服务',
            'company': '公司系统',
            'apps': '应用商店',
            'home': '家庭投资',
            'admin': '管理员功能',
            'quickstart': '快速入门'
        }
        
        # 别名映射，支持更多的输入方式
        self.help_aliases = {
            # 基础功能别名
            'base': 'basic',
            'basics': 'basic',
            'beginner': 'basic',
            '基础': 'basic',
            '基本': 'basic',
            
            # 交易功能别名  
            'trade': 'trading',
            'trades': 'trading',
            'advanced': 'trading',
            '交易': 'trading',
            '高级': 'trading',
            
            # 大宗商品别名
            'commodity': 'commodities',
            'forex': 'commodities',
            'futures': 'commodities',
            'spot': 'commodities',
            '商品': 'commodities',
            '大宗': 'commodities',
            '外汇': 'commodities',
            '期货': 'commodities',
            '现货': 'commodities',
            
            # 分析功能别名
            'analyze': 'analysis',
            'chart': 'analysis',
            'technical': 'analysis',
            '分析': 'analysis',
            '图表': 'analysis',
            
            # 银行服务别名
            'bank': 'banking',
            'finance': 'banking',
            'loan': 'banking',
            '银行': 'banking',
            '金融': 'banking',
            
            # 公司系统别名
            'corp': 'company',
            'business': 'company',
            'ipo': 'company',
            '公司': 'company',
            '企业': 'company',
            
            # 应用商店别名
            'app': 'apps',
            'market': 'apps',
            'games': 'apps',
            '应用': 'apps',
            '商店': 'apps',
            '游戏': 'apps',
            
            # 家庭投资别名
            'investment': 'home',
            'assets': 'home',
            'etf': 'home',
            'cars': 'home',
            '投资': 'home',
            '家庭': 'home',
            
            # 管理员别名
            'administrator': 'admin',
            'manage': 'admin',
            'sudo': 'admin',
            '管理': 'admin',
            '管理员': 'admin',
            
            # 快速入门别名
            'start': 'quickstart',
            'begin': 'quickstart',
            'tutorial': 'quickstart',
            'guide': 'quickstart',
            '入门': 'quickstart',
            '教程': 'quickstart',
            '开始': 'quickstart'
        }
    
    def show_help(self, category=None):
        """显示帮助信息"""
        if category is None:
            self._show_main_help()
        else:
            # 处理别名
            category = category.lower()
            if category in self.help_aliases:
                category = self.help_aliases[category]
            
            if category in self.help_categories:
                self._show_category_help(category)
            else:
                # 尝试模糊匹配
                suggestions = self._find_similar_categories(category)
                if suggestions:
                    self.app.print_to_output(f"❌ 未知的帮助分类: {category}", '#FF0000')
                    self.app.print_to_output(f"💡 您是否想查看: {', '.join(suggestions)}", '#FFAA00')
                    self.app.print_to_output("💡 输入 'help' 查看所有可用分类", '#FFAA00')
                else:
                    self.app.print_to_output(f"❌ 未知的帮助分类: {category}", '#FF0000')
                    self._show_main_help()
    
    def _find_similar_categories(self, input_category):
        """查找相似的帮助分类"""
        suggestions = []
        input_lower = input_category.lower()
        
        # 检查是否是分类名的一部分
        for category, name in self.help_categories.items():
            if input_lower in category or input_lower in name.lower():
                suggestions.append(category)
        
        # 检查别名中是否有相似的
        for alias, real_category in self.help_aliases.items():
            if input_lower in alias and real_category not in suggestions:
                suggestions.append(real_category)
        
        return suggestions[:3]  # 最多返回3个建议
    
    def _show_main_help(self):
        """显示主帮助页面"""
        help_text = """
═══════════════════════════════════════════════════════════════
                    📚 股票交易模拟器 v2.0 帮助中心                    
═══════════════════════════════════════════════════════════════

🎯 欢迎使用股票交易模拟器！以下是帮助分类导航：

📌 基础功能导航:
  help basic          - 🔰 基础交易命令 (买卖、查询、账户管理)
  help quickstart     - 🚀 新手快速入门指南
  
📈 交易相关:
  help trading        - ⚡ 高级交易功能 (限价单、做空、止损等)
  help commodities    - 🌍 大宗商品交易 (外汇、期货、现货) - 新功能!
  help analysis       - 📊 市场分析工具 (技术分析、图表、风险评估)
  
🏦 金融服务:
  help banking        - 🏦 银行金融服务 (贷款、存款、信用等)
  help company        - 🏢 公司管理系统 (创建公司、IPO、发展等)
  help home          - 🏠 家庭投资理财 (ETF、豪车收藏等)
  
🎮 扩展功能:
  help apps          - 🛒 应用商店系统 (小游戏、分析工具等)
  
👑 管理功能:
  help admin         - 🔧 管理员功能 (仅管理员可用)

 💡 使用技巧:
   • 使用 'help <分类>' 查看详细帮助，如: help basic, help 交易
   • 支持中英文别名: help basic = help 基础 = help beginner
   • 大部分命令支持缩写: bal=balance, port=portfolio, hist=history
   • 输入命令时支持自动补全 (按Tab键)
   • 管理员命令需要在命令前加 'sudo'

🆘 需要帮助？
  • 遇到问题请查看对应分类的详细帮助
  • 管理员可使用 'sudo admin_help' 查看管理员专用命令
  • 使用 'appmarket' 浏览可用应用和工具

═══════════════════════════════════════════════════════════════
💫 提示: 输入 'help quickstart' 开始您的交易之旅！
"""
        self.app.print_to_output(help_text)
    
    def _show_category_help(self, category):
        """显示特定分类的帮助"""
        help_methods = {
            'basic': self._show_basic_help,
            'trading': self._show_trading_help,
            'commodities': self._show_commodities_help,
            'analysis': self._show_analysis_help,
            'banking': self._show_banking_help,
            'company': self._show_company_help,
            'apps': self._show_apps_help,
            'home': self._show_home_help,
            'admin': self._show_admin_help,
            'quickstart': self._show_quickstart_help
        }
        
        if category in help_methods:
            help_methods[category]()
        
    def _show_basic_help(self):
        """基础功能帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        🔰 基础功能帮助                           
═══════════════════════════════════════════════════════════════

📋 账户管理:
  help                - 显示帮助信息
  balance (bal)       - 显示账户余额和总资产
  profile            - 查看个人资料和统计数据
  settings           - 调整模拟器设置
  save               - 手动保存游戏数据

📊 股票查询:
  list               - 显示所有股票及当前价格  
  quote <代码>        - 显示特定股票的详细信息
  portfolio (port)   - 查看当前持仓情况
  history (hist)     - 查看交易历史记录

💰 基础交易:
  buy <代码> <数量>    - 市价买入指定数量的股票
  sell <代码> <数量>   - 市价卖出指定数量的股票

📈 基础分析:
  market             - 查看市场概况和趋势
  news               - 查看最新市场动态

🎯 成就系统:
  achievements       - 查看成就系统总览
  leaderboard        - 查看排行榜

🛠️ 系统操作:
  clear (cls)        - 清屏
  logout             - 退出当前用户
  exit               - 退出程序

💡 实用示例:
  buy AAPL 10        - 买入10股苹果公司股票
  sell MSFT 5        - 卖出5股微软股票
  quote TSLA         - 查看特斯拉股票详情
  bal                - 快速查看余额

═══════════════════════════════════════════════════════════════
💫 下一步: 输入 'help trading' 学习高级交易功能
"""
        self.app.print_to_output(help_text)
    
    def _show_trading_help(self):
        """高级交易帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        ⚡ 高级交易帮助                           
═══════════════════════════════════════════════════════════════

📋 限价交易:
  limit_buy <代码> <数量> <限价>    - 限价买入订单
  limit_sell <代码> <数量> <限价>   - 限价卖出订单

📉 做空交易:
  short <代码> <数量>              - 做空股票 (借股卖出)
  limit_short <代码> <数量> <限价>  - 限价做空订单
  cover <代码> <数量>              - 平仓做空 (买回股票)

🛡️ 风险管理:
  stop_loss <代码> <数量> <止损价>     - 设置止损单
  take_profit <代码> <数量> <目标价>   - 设置止盈单

📋 订单管理:
  orders             - 查看所有挂单状态
  cancel <订单号>     - 取消指定订单

💡 交易示例:
  limit_buy AAPL 10 150        - 苹果股价跌到$150时买入10股
  short TSLA 5                 - 做空5股特斯拉
  stop_loss MSFT 10 290        - 微软跌破$290时自动卖出10股
  take_profit GOOGL 2 2800     - 谷歌涨到$2800时自动卖出2股

🔍 订单类型说明:
  • 市价单: 立即按当前市价执行
  • 限价单: 指定价格，达到时自动执行  
  • 止损单: 价格跌破指定点位时卖出
  • 止盈单: 价格达到目标价位时卖出

⚠️ 做空风险提示:
  • 做空需要支付借股费用
  • 潜在亏损可能无限大
  • 及时平仓控制风险

═══════════════════════════════════════════════════════════════
💫 下一步: 输入 'help analysis' 学习市场分析工具
"""
        self.app.print_to_output(help_text)
    
    def _show_commodities_help(self):
        """大宗商品交易帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        🌍 大宗商品交易帮助                        
═══════════════════════════════════════════════════════════════

🌍 外汇交易 (Forex):
  forex                         - 外汇市场概览
  forex list                   - 所有货币对列表
  forex info <货币对>          - 货币对详细信息
  forex buy <货币对> <手数> [leverage=杠杆]   - 买入货币对
  forex sell <货币对> <手数> [leverage=杠杆]  - 卖出货币对
  forex sessions               - 全球交易时段

📈 期货交易 (Futures):
  futures                      - 期货市场概览
  futures list                - 所有期货合约
  futures info <合约代码>      - 合约详细信息
  futures buy <合约> <数量>    - 买入期货合约
  futures sell <合约> <数量>   - 卖出期货合约
  futures contracts           - 活跃合约信息

🏪 现货交易 (Spot):
  spot                        - 现货市场概览
  spot list                   - 所有现货商品
  spot info <商品代码>        - 商品详细信息
  spot buy <商品> <数量>       - 买入现货商品
  spot sell <商品> <数量>      - 卖出现货商品
  spot delivery               - 交割信息

💼 通用商品命令:
  commodity                   - 商品市场概览
  commodity search <关键词>   - 搜索商品
  commodity positions         - 当前持仓
  commodity history           - 交易历史
  commodity close <商品>      - 平仓
  commodity movers            - 涨跌榜
  commodity calendar          - 市场时间

💰 外汇交易示例:
  forex buy JCKUSD 0.1        - 买入0.1手JCK/USD
  forex buy JCKEUR 0.2 leverage=50  - 50倍杠杆买入JCK/EUR
  forex sell JCKGBP 0.1       - 卖出0.1手JCK/GBP

📊 期货交易示例:
  futures buy CL2501 1        - 买入1手原油期货
  futures sell GC2502 2       - 卖出2手黄金期货
  futures info ES2501         - 查看标普500期货信息

🏪 现货交易示例:
  spot buy XAUUSD_SPOT 10     - 买入10盎司现货黄金
  spot sell COFFEE_SPOT 100   - 卖出100磅咖啡现货

🎯 JCK货币对 (核心特色):
  JCKUSD - JackyCoin对美元 (1 JCK ≈ 1.25 USD)
  JCKEUR - JackyCoin对欧元 (1 JCK ≈ 1.15 EUR)
  JCKGBP - JackyCoin对英镑 (1 JCK ≈ 0.98 GBP)
  JCKJPY - JackyCoin对日元 (1 JCK ≈ 187.5 JPY)

💡 交易提示:
  • 外汇支持最高100倍杠杆，风险较高
  • 期货有到期日，需要注意合约期限
  • 现货支持实物交割，储存成本需考虑
  • JCK货币对是本系统特色，汇率相对稳定

⚠️ 风险警告:
  • 杠杆交易风险极高，可能损失全部资金
  • 期货价格波动剧烈，请谨慎操作
  • 现货交易需要考虑储存和运输成本

═══════════════════════════════════════════════════════════════
🌟 特色: 全球首个以JCK为核心的外汇交易系统!
💫 下一步: 输入 'help analysis' 学习市场分析工具"""
        self.app.print_to_output(help_text)
    
    def _show_analysis_help(self):
        """市场分析帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        📊 市场分析帮助                           
═══════════════════════════════════════════════════════════════

📈 技术分析:
  analysis <代码>              - 股票技术分析 (RSI、MACD等)
  chart <代码> [时间范围]       - 显示股价历史图表
  compare <代码1> <代码2>      - 对比两支股票表现

🏭 行业分析:
  sector                      - 查看行业分析总览
  sector_chart [行业名]        - 查看行业图表分析

📊 市场情绪:
  market_sentiment            - 查看市场情绪分析
  economic_calendar           - 查看经济日历

🔍 风险评估:
  risk                       - 进行投资风险评估
  performance               - 查看投资组合绩效

📊 指数系统:
  index (indices)           - 查看所有指数概况
  index <指数代码>           - 查看特定指数详情
  index list               - 列出所有可用指数
  index category <类别>     - 查看特定类别指数
  index compare <指数1> <指数2> - 对比两个指数

💡 分析示例:
  analysis AAPL             - 苹果股票技术分析
  chart TSLA 1m             - 特斯拉1个月价格图表
  compare AAPL MSFT         - 对比苹果和微软
  sector_chart Technology   - 科技行业图表分析
  index SP500              - 查看标普500指数详情

📚 指标说明:
  • RSI: 相对强弱指数 (14天)
  • MACD: 指数平滑移动平均线
  • 布林带: 价格波动区间
  • 成交量: 交易活跃度指标

🎯 可用指数:
  • SP500: 标普500指数
  • NASDAQ: 纳斯达克综合指数
  • DOW: 道琼斯工业指数
  • TECH_INDEX: 科技股指数
  • FINANCE_INDEX: 金融股指数

═══════════════════════════════════════════════════════════════
💫 下一步: 输入 'help banking' 了解银行金融服务
"""
        self.app.print_to_output(help_text)
    
    def _show_banking_help(self):
        """银行服务帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        🏦 银行服务帮助                           
═══════════════════════════════════════════════════════════════

🏦 银行系统主菜单:
  bank                        - 进入多银行管理系统主菜单
  bank list                   - 查看所有可用银行列表
  bank status [银行ID]         - 查看银行账户状态

💳 贷款服务:
  bank loan <金额> [天数] [银行ID]  - 在指定银行申请贷款
  bank repay <贷款ID>              - 偿还银行贷款

💰 存款服务:  
  bank deposit <金额> [类型] [银行ID] - 在指定银行存款
  bank withdraw <存款ID>             - 提取银行存款

🎯 银行任务系统:
  bank tasks [银行ID]               - 查看银行任务列表
  bank tasks accept <任务ID>        - 接受银行任务
  bank tasks progress               - 查看任务进度

🏦 六大银行体系:

🏪 JC商业银行 (JC_COMMERCIAL):
  • 基础银行服务，适合新手
  • 贷款利率: 8.5%, 存款利率: 2.0%
  • 解锁条件: 默认可用

💼 JC投资银行 (JC_INVESTMENT):  
  • 高端投资理财服务
  • 贷款利率: 7.5%, 存款利率: 2.8%
  • 解锁条件: 等级5，资产≥50万

📈 JC交易银行 (JC_TRADING):
  • 专业交易员服务
  • 贷款利率: 7.0%, 存款利率: 2.5%
  • 解锁条件: 等级8，交易次数≥100

₿ JC数字银行 (JC_CRYPTO):
  • 数字货币相关服务
  • 贷款利率: 9.0%, 存款利率: 3.5%
  • 解锁条件: 等级10，持有数字货币

💎 JC财富银行 (JC_WEALTH):
  • 超高净值客户专属
  • 贷款利率: 6.0%, 存款利率: 3.8%
  • 解锁条件: 等级15，资产≥200万

🏛️ JC央行 (JC_CENTRAL):
  • 央行直接服务
  • 特殊利率和政策工具
  • 解锁条件: 等级20，特殊成就

📊 银行关系等级:
  1-2级: 新客户 (基础利率)
  3-4级: 认识客户 (95%利率)
  5-6级: 合作伙伴 (90%利率)
  7-8级: 优质客户 (85%利率)
  9-10级: VIP客户 (80%利率)

🏆 信用评级系统:
  AAA > AA > A > BBB > BB > B > CCC > CC > C > D
  • 影响贷款额度: AAA(5倍) → D(0.5倍)
  • 影响贷款利率: AAA(-30%) → D(+50%)
  • 通过及时还款、完成任务提升

💡 存款类型:
  • demand: 活期存款 (随时支取，基础利率)
  • short: 短期定存 (1个月，+0.5%利率)
  • medium: 中期定存 (3个月，+1.0%利率)  
  • long: 长期定存 (6个月，+1.5%利率)

🎯 银行任务类型:
  • 交易任务: 完成指定交易量/次数
  • 存款任务: 维持一定存款余额
  • 投资任务: 投资组合达到目标
  • 挑战任务: 完成复合条件目标

💰 使用示例:
  bank loan 100000 30 JC_INVESTMENT    - 在投资银行申请10万元贷款
  bank deposit 50000 medium JC_WEALTH  - 在财富银行存入5万元中期定存
  bank tasks JC_COMMERCIAL              - 查看商业银行的任务
  bank status JC_TRADING                - 查看在交易银行的账户状态

⚠️ 重要提示:
  • 每家银行独立计算关系等级和信用评级
  • 不同银行有不同的利率和服务特色
  • 建议根据需求选择最适合的银行
  • 完成银行任务可获得关系点数和奖励

═══════════════════════════════════════════════════════════════
💫 下一步: 输入 'help company' 了解公司系统
"""
        self.app.print_to_output(help_text)
    
    def _show_company_help(self):
        """公司系统帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                    🏢 公司系统帮助 (模块化重设计版)                
═══════════════════════════════════════════════════════════════

🚀 创建公司 - 全新体验:
  company create             - 启动交互式公司创建向导 (推荐)
  company wizard             - 启动公司创建向导
  company gui                - 启动公司管理GUI界面
  
🏢 传统创建方式:
  company create <名称> <行业> [描述]  - 快速创建公司

👨‍💼 公司管理:
  company                    - 公司市场概览
  company my                 - 查看我的公司
  company info <ID/代码>     - 公司详细信息
  company market             - 公司市场总览

📈 公司运营与发展:
  company develop <ID> <类型>  - 公司发展投资
  company news <ID>           - 公司新闻事件

🔥 高级功能:
  company acquire <收购方> <目标> <价格>     - 公司收购
  company jv <公司1> <公司2> <投资额>       - 合资企业
  company competition <ID>                 - 竞争分析

💹 IPO上市:
  company ipo <ID> <发行价> <股数>         - 申请IPO上市

🏭 行业分析:
  company industry <行业名>               - 行业分析报告

🎯 创建向导特色功能:
  
🌟 7个详细阶段:
  1️⃣ 欢迎介绍 - 流程概览和准备
  2️⃣ 基本信息 - 公司名称、总部选择
  3️⃣ 行业选择 - 12大行业详细介绍
  4️⃣ 资金规划 - 启动资金和风险评估
  5️⃣ 团队建设 - 4种团队配置方案
  6️⃣ 商业模式 - B2B/B2C/制造/平台/混合
  7️⃣ 发展策略 - 扩张/稳定/技术/市场/多元化

🖥️ CLI风格GUI界面:
  • ASCII艺术场景渲染
  • 办公大楼、工厂、会议室等场景
  • 动态场景切换和动画效果
  • 专业命令行风格界面

📊 公司发展阶段系统:
  🌱 初创期 (Startup) - 基础运营能力
  📈 成长期 (Growth) - 扩展业务范围
  🏢 成熟期 (Mature) - 稳定盈利能力
  🌍 扩张期 (Expansion) - 多元化发展
  🏛️ 企业级 (Corporate) - 行业领导地位

🛠️ 10种运营管理:
  1️⃣ 市场营销 - 提升品牌影响力
  2️⃣ 产品研发 - 创新技术突破
  3️⃣ 人才招聘 - 扩充团队实力
  4️⃣ 设备升级 - 提升生产效率
  5️⃣ 客户服务 - 改善服务质量
  6️⃣ 供应链优化 - 降低运营成本
  7️⃣ 数字化转型 - 技术升级改造
  8️⃣ 品质管理 - 提升产品质量
  9️⃣ 国际化扩张 - 开拓海外市场
  🔟 战略合作 - 建立合作关系

🎯 12大行业完整体系:
  
🖥️ 科技 (technology) - 创新驱动，高风险高回报
📊 金融 (finance) - 稳定收益，政策敏感
🏥 医疗 (healthcare) - 长期稳定，抗周期
⚡ 能源 (energy) - 资本密集，周期性强
🏭 制造 (manufacturing) - 传统稳健，转型升级
🛒 零售 (retail) - 消费驱动，竞争激烈
🏠 房地产 (real_estate) - 资本密集，政策敏感
🚛 运输 (transportation) - 基础服务，稳定需求
📡 电信 (telecom) - 基础设施，技术迭代
🔌 公用事业 (utilities) - 稳定收益，监管严格
🍔 消费品 (consumer_goods) - 日常需求，品牌重要
🌾 农业 (agriculture) - 基础产业，季节性强

💡 发展投资类型 (8种):
  research     - 🔬 研发投资 (创新技术)
  marketing    - 📢 营销投资 (品牌推广)  
  expansion    - 🏗️ 扩张投资 (规模扩大)
  efficiency   - ⚙️ 效率投资 (流程优化)
  technology   - 💻 技术投资 (数字化升级)
  talent       - 👥 人才投资 (团队建设)
  brand        - 🏆 品牌投资 (品牌价值)
  innovation   - 💡 创新投资 (突破性发展)

🎮 使用示例:
  
🌟 推荐方式:
  company create                      - 启动创建向导
  company gui                         - 打开管理界面
  
📝 传统方式:
  company create "AI科技" technology  - 快速创建科技公司
  company develop TECH01 research     - 研发投资
  company ipo TECH01 50 1000000      - IPO上市
  
🏢 高级功能:
  company acquire TECH01 MSFT 300    - 收购微软
  company jv TECH01 AAPL 5000000     - 与苹果合资
  company competition TECH01          - 竞争分析

📊 公司评级系统:
  S+: 95-100分 🏆 (完美表现)
  S:  90-94分  ⭐ (优秀表现)
  A+: 85-89分  🎯 (强烈买入)
  A:  80-84分  📈 (买入)
  B+: 75-79分  📊 (持有)
  B:  70-74分  ⚖️ (中性)
  B-: 65-69分  ⚠️ (谨慎)
  C:  50-64分  📉 (减持)
  D:  0-49分   ⛔ (卖出)

⚠️ 重要特性:
  • 🎯 分阶段指导的创建向导
  • 🖥️ 专业CLI风格GUI界面
  • 📊 动态公司发展阶段系统
  • 🛠️ 10种详细运营管理选项
  • 🏢 公司收购与合资功能
  • 📈 智能竞争分析系统
  • 🎨 ASCII艺术场景渲染
  • 💼 完整的公司生命周期管理

═══════════════════════════════════════════════════════════════
🚀 新特色: 全面重设计的模块化公司管理系统!
💫 下一步: 输入 'help apps' 了解应用商店系统
"""
        self.app.print_to_output(help_text)
    
    def _show_apps_help(self):
        """应用商店帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        🛒 应用商店帮助                           
═══════════════════════════════════════════════════════════════

🛒 应用商店导航:
  appmarket                     - 查看应用商店
  appmarket <类别>              - 查看特定类别应用
  appmarket my                  - 查看我的应用
  appmarket usage               - 查看使用统计

📦 应用管理:
  install <应用ID>              - 购买并安装应用
  uninstall <应用ID>            - 卸载应用
  appmarket.app <应用ID> [参数] - 运行已安装的应用

🎮 游戏娱乐类应用:
  slot_machine     - 🎰 老虎机游戏 ($5,000)
  blackjack        - 🃏 21点纸牌游戏 ($8,000)
  texas_holdem     - ♠️ 德州扑克 ($12,000)
  dice_game        - 🎲 骰子猜大小 ($3,000)
  poker_game       - 🃏 扑克游戏 ($6,000)

🔧 分析工具类应用:
  ai_analysis      - 🤖 AI智能分析师 ($15,000)
  news_analyzer    - 📰 新闻分析器 ($10,000)
  advanced_chart   - 📊 高级图表分析工具 ($20,000)

💡 应用使用示例:
  install slot_machine                    - 安装老虎机游戏
  appmarket.app slot_machine 100          - 玩老虎机，投注$100
  appmarket.app blackjack 500             - 玩21点，投注$500
  appmarket.app ai_analysis AAPL          - AI分析苹果股票
  appmarket.app advanced_chart TSLA       - 启动特斯拉专业图表窗口

🌟 推荐应用:
  • 📊 advanced_chart: 专业级GUI图表工具
    - 独立窗口显示K线图、技术指标
    - 支持实时更新和图表导出
    - 多种图表类型和时间框架
  
  • 🤖 ai_analysis: AI智能分析师
    - 综合技术、基本面、情绪分析
    - 智能投资建议和风险评估
    - 个性化推荐投资策略

💰 应用定价:
  • 一次购买，永久使用
  • 价格根据应用复杂度和功能定价
  • 支持试用和退款(部分应用)

📊 应用分类:
  • entertainment: 游戏娱乐
  • analysis: 分析工具  
  • utility: 实用工具
  • education: 教育培训

═══════════════════════════════════════════════════════════════
💫 下一步: 输入 'help home' 了解家庭投资理财
"""
        self.app.print_to_output(help_text)
    
    def _show_home_help(self):
        """家庭投资帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        🏠 家庭投资帮助                           
═══════════════════════════════════════════════════════════════

🏠 家庭投资中心:
  home                   - 进入家庭投资理财中心
  home portfolio         - 查看我的投资组合

🎯 投资市场:
  home etf               - 浏览ETF基金投资市场
  home cars              - 浏览豪华车收藏市场
  home market            - 查看综合投资市场

🏠 家居展示:
  home interior          - 查看我的家居和藏品展示

💰 交易操作:
  home buy <类型> <ID> <数量>   - 购买投资品
  home sell <类型> <ID> <数量>  - 出售投资品
  home info <类型> <ID>         - 查看投资品详细信息

📈 ETF基金 (etf):
  • TECH_GROWTH: 科技成长基金 (高风险高收益)
  • STABLE_INCOME: 稳健收益基金 (低风险稳定收益)
  • GLOBAL_MARKETS: 全球市场基金 (分散投资)
  • GREEN_ENERGY: 绿色能源基金 (环保主题)
  • HEALTHCARE_PLUS: 医疗健康基金 (医疗行业)

🚗 豪华车收藏 (car):
  • FERRARI_F8: 法拉利F8 Tributo (经典超跑)
  • LAMBORGHINI_HURACAN: 兰博基尼Huracán (奢华性能)
  • PORSCHE_911: 保时捷911 Turbo S (经典跑车)
  • MCLAREN_720S: 迈凯伦720S (英伦超跑)
  • BUGATTI_CHIRON: 布加迪Chiron (极致奢华)

💡 投资示例:
  home buy etf TECH_GROWTH 1000        - 购买1000份科技成长基金
  home sell car FERRARI_F8 1          - 出售1辆法拉利F8
  home info etf STABLE_INCOME          - 查看稳健收益基金详情
  home info car PORSCHE_911            - 查看保时捷911详情

📊 投资特点:
  • ETF基金: 基于股票市场表现，费用比率影响收益
  • 豪华车: 独特的价格波动模式，稀有度影响升值
  • 价格实时更新: 所有投资品价格动态变化
  • 投资建议: 系统提供智能买卖建议

🏆 稀有度等级:
  • common: 普通 (基础收益)
  • rare: 稀有 (中等收益) 
  • epic: 史诗 (高收益)
  • legendary: 传奇 (极高收益)

💎 投资策略:
  • 分散投资: 不要把所有资金投入单一资产
  • 长期持有: 部分资产适合长期投资
  • 定期关注: 及时调整投资组合
  • 风险控制: 高收益伴随高风险

═══════════════════════════════════════════════════════════════
💫 下一步: 输入 'help admin' 了解管理员功能
"""
        self.app.print_to_output(help_text)
    
    def _show_admin_help(self):
        """管理员功能帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        🔧 管理员功能帮助                          
═══════════════════════════════════════════════════════════════

⚠️  管理员专用功能 - 需要管理员权限

🔐 进入管理员模式:
  sudo <命令>             - 执行管理员命令 (首次需验证密码)
  exit_admin             - 退出管理员模式

👥 用户管理 (sudo user):
  sudo user list                      - 查看所有用户
  sudo user info <用户名>               - 查看用户详细信息
  sudo user cash <用户名> <金额>        - 修改用户资金
  sudo user level <用户名> <等级>       - 修改用户等级 (1-100)
  sudo user exp <用户名> <经验值>       - 修改用户经验值
  sudo user credit <用户名> <信用等级>  - 修改银行信用等级
  sudo user reset <用户名>             - 重置用户数据
  sudo user ban <用户名>               - 封禁用户
  sudo user unban <用户名>             - 解封用户

📈 股票管理 (sudo stock):
  sudo stock add <代码> <名称> <价格> <行业> [波动率] - 添加新股票
  sudo stock remove <代码>                          - 删除股票
  sudo stock price <代码> <价格>                     - 修改股票价格
  sudo stock info <代码>                            - 查看股票详细信息
  sudo stock list                                   - 查看所有股票
  sudo stock volatility <代码> <波动率>              - 修改股票波动率

🏦 银行管理 (sudo bank):
  sudo bank rates loan <利率>          - 修改贷款基础利率
  sudo bank rates deposit <利率>       - 修改存款基础利率
  sudo bank credit <用户名> <等级>      - 修改用户信用等级
  sudo bank loan <用户名> <金额> [天数] - 强制发放贷款
  sudo bank forgive <用户名> <贷款ID>   - 免除贷款

⚙️ 系统管理 (sudo system):
  sudo system event <事件内容>         - 创建市场事件
  sudo system reset market            - 重置市场价格
  sudo system backup                  - 备份系统数据
  sudo system maintenance <on/off>    - 维护模式开关

💡 管理员示例:
  sudo user cash john 50000           - 给用户john增加50000资金
  sudo user level alice 15            - 将用户alice等级设为15
  sudo stock add NTES 网易 180.50 Technology - 添加网易股票
  sudo bank rates loan 0.08           - 设置贷款利率为8%
  sudo system event "央行降息，市场大涨" - 创建市场事件

🔧 权限说明:
  • 用户管理: 可以修改任意用户的所有数据
  • 股票管理: 可以添加/删除股票，修改价格和波动率
  • 银行管理: 可以强制发放贷款，免除债务
  • 系统管理: 可以创建市场事件，备份系统

⚠️ 安全提示:
  • 管理员权限很强大，请谨慎使用
  • 修改用户数据会影响游戏平衡性
  • 建议定期备份系统数据
  • 管理员密码默认为 "admin"

📋 信用等级列表:
  AAA, AA, A, BBB, BB, B, CCC, CC, C, D
  (从高到低，影响贷款额度和利率)

═══════════════════════════════════════════════════════════════
💫 提示: 使用管理员功能请务必小心，避免破坏游戏平衡
"""
        self.app.print_to_output(help_text)
    
    def _show_quickstart_help(self):
        """快速入门帮助"""
        help_text = """
═══════════════════════════════════════════════════════════════
                        🚀 新手快速入门                           
═══════════════════════════════════════════════════════════════

👋 欢迎来到股票交易模拟器！跟着这个指南开始您的投资之旅：

📊 第一步: 了解您的账户
  balance                - 查看您的初始资金 ($100,000)
  profile               - 查看个人资料和等级

📈 第二步: 浏览股票市场
  list                  - 查看所有可交易股票
  quote AAPL            - 查看苹果公司股票详情
  market                - 了解当前市场概况

💰 第三步: 进行第一笔交易
  buy AAPL 10           - 买入10股苹果股票
  portfolio             - 查看您的持仓
  sell AAPL 5           - 卖出5股苹果股票

📊 第四步: 学习分析工具
  analysis AAPL         - 查看苹果股票技术分析
  chart AAPL            - 查看价格图表
  risk                  - 评估投资风险

🏆 第五步: 探索成就系统
  achievements          - 查看可获得的成就
  leaderboard           - 查看排行榜

🎮 第六步: 体验更多功能
  appmarket             - 浏览应用商店
  bank                  - 了解银行服务
  home                  - 探索家庭投资

💡 新手建议:

📚 学习基础:
  • 先用小金额练习交易
  • 了解股票价格波动原理
  • 学习基本的技术分析指标

🎯 设定目标:
  • 完成第一笔盈利交易
  • 达到账户10万以上资产
  • 解锁基础交易成就

⚠️ 风险管理:
  • 不要把所有资金投入一只股票
  • 学会使用止损单控制损失
  • 保持冷静，避免情绪化交易

🚀 进阶功能:
  • 尝试限价单交易
  • 学习做空操作
  • 使用银行贷款杠杆交易

🎲 娱乐功能:
  • 安装小游戏放松心情
  • 尝试AI分析工具
  • 投资ETF基金分散风险

📞 获得帮助:
  help basic            - 基础功能详细说明
  help trading          - 高级交易功能
  help analysis         - 市场分析工具

🏅 第一个目标：尝试完成以下操作
  1. 查看账户余额
  2. 买入任意股票
  3. 查看持仓情况
  4. 完成一笔盈利交易
  5. 解锁第一个成就

═══════════════════════════════════════════════════════════════
💫 准备好了吗？输入 'balance' 开始您的投资之旅！
"""
        self.app.print_to_output(help_text)