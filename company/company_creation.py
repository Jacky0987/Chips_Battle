"""
JC公司创建向导系统
提供step-by-step的公司创建流程，包括详细的引导和验证
"""

import random
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from .company_types import IndustryCategory, CompanyType, CompanyStage, BusinessMetrics, CompanyFinancials, JCCompany


@dataclass
class CreationStep:
    """创建步骤数据类"""
    step_id: str
    title: str
    description: str
    options: List[str] = None
    validation_func: callable = None
    next_step: str = None


class CompanyCreationWizard:
    """公司创建向导"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.current_session = {}  # 当前创建会话数据
        self.creation_steps = self._init_creation_steps()
        self.current_step = "welcome"
        
    def _init_creation_steps(self) -> Dict[str, CreationStep]:
        """初始化创建步骤"""
        return {
            "welcome": CreationStep(
                step_id="welcome",
                title="🏢 欢迎来到JC企业孵化器",
                description="""
════════════════════════════════════════════════════════════════════════════════════════
                               🚀 JC企业孵化器 🚀                                    
════════════════════════════════════════════════════════════════════════════════════════

欢迎创业者！您正要踏上企业家之路，建立属于自己的商业帝国。

本向导将引导您逐步完成公司注册流程：
  📝 第1步: 公司基本信息设定
  🏭 第2步: 行业领域选择 
  💰 第3步: 初始资金规划
  👥 第4步: 团队组建方案
  📊 第5步: 商业模式设计
  🎯 第6步: 发展战略制定
  ✅ 第7步: 最终确认注册

💡 温馨提示: 
  • 每个选择都会影响公司的初始属性和发展潜力
  • 您可以随时输入 'back' 返回上一步
  • 输入 'cancel' 取消创建流程

准备好开始创业之旅了吗？ [输入 'start' 开始 / 'help' 查看帮助]
""",
                options=["start", "help", "cancel"],
                next_step="basic_info"
            ),
            
            "basic_info": CreationStep(
                step_id="basic_info",
                title="📝 第1步: 公司基本信息",
                description=f"""
────────────────────────────────────────────────────────────────────────────────────────
                                📝 公司基本信息设定                                   
────────────────────────────────────────────────────────────────────────────────────────

一个响亮的公司名称是成功的第一步！

🏷️  公司命名要求:
  • 长度: 2-30个字符
  • 格式: 支持中英文、数字、常见符号
  • 建议: 简洁易记，体现行业特色
  
📍 注册地址: JC经济特区（系统自动设定）
📅 成立日期: {datetime.now().strftime('%Y年%m月%d日')}（系统自动设定）

💡 命名建议:
  • 科技类: XX科技、XX智能、XX创新
  • 金融类: XX投资、XX资本、XX金融
  • 制造类: XX制造、XX工业、XX集团
  • 服务类: XX服务、XX咨询、XX传媒

请输入您的公司名称:
""",
                validation_func=lambda x: self._validate_company_name(x),
                next_step="industry_selection"
            ),
            
            "industry_selection": CreationStep(
                step_id="industry_selection",
                title="🏭 第2步: 行业领域选择",
                description="""
────────────────────────────────────────────────────────────────────────────────────────
                               🏭 选择您的行业领域                                  
────────────────────────────────────────────────────────────────────────────────────────

选择合适的行业是创业成功的关键。不同行业有不同的特点和发展前景：

🚀 高增长潜力行业:
  [1] 🔬 technology     - 科技行业 (AI、软件、硬件)     │ 高风险高回报
  [2] 🏥 healthcare     - 医疗健康 (制药、医疗设备)     │ 稳定需求
  [3] 💚 energy         - 新能源 (太阳能、风能)       │ 政策支持

🏭 传统稳健行业:
  [4] 🏭 manufacturing  - 制造业 (机械、电子制造)     │ 稳定增长
  [5] 🛒 retail         - 零售业 (商超、电商)         │ 市场庞大
  [6] 🏗️ real_estate    - 房地产 (开发、物业)        │ 资金密集

💼 服务专业行业:
  [7] 💰 finance        - 金融服务 (银行、保险)       │ 监管严格
  [8] 📞 telecom        - 电信通讯 (运营商、设备)     │ 技术门槛
  [9] 🚛 transportation - 交通运输 (物流、出行)       │ 基础设施

🔧 基础支撑行业:
  [10] ⚡ utilities      - 公用事业 (电力、水务)       │ 垄断特征
  [11] 🛍️ consumer_goods - 消费品 (食品、日用品)      │ 刚性需求
  [12] 🌾 agriculture    - 农业 (种植、畜牧)          │ 周期性强

请输入您选择的行业编号或名称 [1-12]:
""",
                validation_func=lambda x: self._validate_industry(x),
                next_step="funding_plan"
            ),
            
            "funding_plan": CreationStep(
                step_id="funding_plan",
                title="💰 第3步: 初始资金规划",
                description=f"""
────────────────────────────────────────────────────────────────────────────────────────
                               💰 初始资金投入规划                                 
────────────────────────────────────────────────────────────────────────────────────────

确定您的初始投资金额。投资越多，公司起点越高，但风险也更大。

当前您的可用资金: J${self.main_app.cash:,.0f}

💼 推荐投资方案:

🟢 保守型 (100万 - 500万):
  • 适合: 服务业、咨询业
  • 特点: 风险低、增长稳定
  • 优势: 压力小、容易管理
  • 劣势: 增长缓慢、竞争激烈

🟡 平衡型 (500万 - 2000万):
  • 适合: 制造业、零售业
  • 特点: 风险适中、增长潜力好
  • 优势: 发展空间大、抗风险能力强
  • 劣势: 需要一定管理经验

🔴 激进型 (2000万以上):
  • 适合: 科技业、能源业
  • 特点: 高风险高回报
  • 优势: 快速扩张、市场领先
  • 劣势: 风险极高、资金压力大

💡 投资建议:
  • 不建议投入超过总资产的70%
  • 保留足够的流动资金应对市场变化
  • 初创企业建议保守起步

请输入您的投资金额 (最低100万，最高5000万):
""",
                validation_func=lambda x: self._validate_funding(x),
                next_step="team_building"
            ),
            
            "team_building": CreationStep(
                step_id="team_building",
                title="👥 第4步: 核心团队组建",
                description="""
────────────────────────────────────────────────────────────────────────────────────────
                               👥 组建您的核心团队                                 
────────────────────────────────────────────────────────────────────────────────────────

优秀的团队是企业成功的基石。根据您的行业和资金情况选择合适的团队配置：

👔 团队配置方案:

🎯 精英小队 (5-15人):
  • 成本: 投资额的15-20%
  • 构成: 核心技术专家 + 销售精英 + 管理骨干
  • 适合: 科技、咨询、金融行业
  • 优势: 效率高、执行力强、沟通顺畅
  • 风险: 人员依赖性强

⚖️ 均衡团队 (15-50人):
  • 成本: 投资额的20-25%
  • 构成: 技术团队 + 销售团队 + 运营团队 + 管理层
  • 适合: 制造、零售、服务行业
  • 优势: 功能完整、风险分散
  • 风险: 管理复杂度增加

🏭 规模团队 (50人以上):
  • 成本: 投资额的25-30%
  • 构成: 完整部门架构 + 专业分工
  • 适合: 制造、运输、农业行业
  • 优势: 执行力强、规模效应
  • 风险: 管理成本高、反应慢

🤖 自动化优先 (3-10人):
  • 成本: 投资额的10-15% (人力) + 20% (设备)
  • 构成: 技术专家 + 少量运营人员
  • 适合: 高科技、制造业
  • 优势: 成本可控、扩展性强
  • 风险: 技术依赖性高

请选择团队配置方案 [精英小队/均衡团队/规模团队/自动化优先]:
""",
                validation_func=lambda x: self._validate_team_config(x),
                next_step="business_model"
            ),
            
            "business_model": CreationStep(
                step_id="business_model",
                title="📊 第5步: 商业模式设计",
                description="""
────────────────────────────────────────────────────────────────────────────────────────
                               📊 设计您的商业模式                                 
────────────────────────────────────────────────────────────────────────────────────────

商业模式决定了公司如何创造和获取价值。选择适合您行业的盈利模式：

💰 收入模式选择:

🔄 B2B服务模式:
  • 特点: 面向企业客户，长期合同
  • 优势: 客户稳定、收入可预测、利润率高
  • 适合: 软件服务、咨询、金融服务
  • 发展: 重点关系维护、专业度提升

🛒 B2C销售模式:
  • 特点: 面向消费者，快速周转
  • 优势: 市场规模大、增长潜力高
  • 适合: 零售、消费品、娱乐
  • 发展: 品牌建设、渠道扩张

🏭 制造供应模式:
  • 特点: 生产制造，供应链管理
  • 优势: 规模效应、技术壁垒
  • 适合: 制造业、农业、能源
  • 发展: 产能扩张、成本控制

📱 平台连接模式:
  • 特点: 连接供需双方，收取佣金
  • 优势: 轻资产、网络效应强
  • 适合: 科技、金融、服务
  • 发展: 用户增长、生态建设

💡 创新混合模式:
  • 特点: 多种模式组合，风险分散
  • 优势: 收入来源多样化
  • 适合: 成熟企业、大型集团
  • 发展: 协同效应、资源整合

请选择您的商业模式 [B2B服务/B2C销售/制造供应/平台连接/创新混合]:
""",
                validation_func=lambda x: self._validate_business_model(x),
                next_step="development_strategy"
            ),
            
            "development_strategy": CreationStep(
                step_id="development_strategy",
                title="🎯 第6步: 发展战略制定",
                description="""
────────────────────────────────────────────────────────────────────────────────────────
                               🎯 制定发展战略目标                                 
────────────────────────────────────────────────────────────────────────────────────────

制定未来3年的发展战略，明确公司的发展方向和重点：

🚀 发展战略选择:

⚡ 快速扩张策略:
  • 目标: 3年内成为行业领导者
  • 重点: 市场份额、品牌知名度
  • 投入: 研发30% + 营销40% + 人才20% + 运营10%
  • 适合: 科技、零售、服务行业
  • 风险: 资金压力大、管理挑战

🛡️ 稳健发展策略:
  • 目标: 稳步提升盈利能力
  • 重点: 运营效率、客户满意度
  • 投入: 运营40% + 研发25% + 营销20% + 人才15%
  • 适合: 制造、金融、公用事业
  • 风险: 增长缓慢、竞争劣势

🔬 技术领先策略:
  • 目标: 成为技术创新引领者
  • 重点: 技术研发、专利积累
  • 投入: 研发50% + 人才30% + 营销10% + 运营10%
  • 适合: 科技、医疗、新能源
  • 风险: 研发风险、商业化挑战

🌐 市场渗透策略:
  • 目标: 深度开发现有市场
  • 重点: 客户关系、服务质量
  • 投入: 营销35% + 服务30% + 运营25% + 研发10%
  • 适合: 传统行业、本地服务
  • 风险: 市场天花板、竞争加剧

🔄 多元化发展策略:
  • 目标: 业务多元化降低风险
  • 重点: 新业务拓展、协同效应
  • 投入: 新业务40% + 现有业务35% + 整合25%
  • 适合: 成熟企业、资金充足
  • 风险: 管理复杂、资源分散

请选择发展战略 [快速扩张/稳健发展/技术领先/市场渗透/多元化发展]:
""",
                validation_func=lambda x: self._validate_strategy(x),
                next_step="final_confirmation"
            ),
            
            "final_confirmation": CreationStep(
                step_id="final_confirmation",
                title="✅ 第7步: 最终确认",
                description="""""",  # 动态生成
                next_step="complete"
            )
        }
    
    def start_creation(self) -> str:
        """开始创建流程"""
        self.current_session = {
            'user_id': self.main_app.user_manager.current_user,
            'created_at': datetime.now().isoformat(),
            'step_history': []
        }
        self.current_step = "welcome"
        return self._get_current_step_display()
    
    def process_input(self, user_input: str) -> Tuple[bool, str]:
        """处理用户输入"""
        user_input = user_input.strip()
        
        # 处理特殊命令
        if user_input.lower() == 'cancel':
            return False, "❌ 公司创建已取消"
        
        if user_input.lower() == 'back' and len(self.current_session.get('step_history', [])) > 0:
            return self._go_back()
        
        if user_input.lower() == 'help':
            return True, self._get_help_text()
        
        # 处理当前步骤
        step = self.creation_steps[self.current_step]
        
        if step.validation_func:
            is_valid, message = step.validation_func(user_input)
            if not is_valid:
                return True, f"❌ {message}\n\n{self._get_current_step_display()}"
        
        # 保存用户输入并前进到下一步
        return self._advance_step(user_input)
    
    def _get_current_step_display(self) -> str:
        """获取当前步骤显示"""
        step = self.creation_steps[self.current_step]
        
        if self.current_step == "final_confirmation":
            return self._generate_confirmation_display()
        
        progress = f"[步骤 {list(self.creation_steps.keys()).index(self.current_step)}/7]"
        
        return f"""
{progress}
{step.title}
{step.description}
"""
    
    def _advance_step(self, user_input: str) -> Tuple[bool, str]:
        """前进到下一步"""
        current_step_obj = self.creation_steps[self.current_step]
        
        # 保存当前步骤信息到历史
        self.current_session['step_history'].append({
            'step': self.current_step,
            'input': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保存特定步骤的数据
        if self.current_step == "basic_info":
            self.current_session['company_name'] = user_input
        elif self.current_step == "industry_selection":
            self.current_session['industry'] = self._parse_industry_input(user_input)
        elif self.current_step == "funding_plan":
            self.current_session['initial_funding'] = float(user_input.replace(',', ''))
        elif self.current_step == "team_building":
            self.current_session['team_config'] = user_input
        elif self.current_step == "business_model":
            self.current_session['business_model'] = user_input
        elif self.current_step == "development_strategy":
            self.current_session['strategy'] = user_input
        
        # 前进到下一步
        if current_step_obj.next_step == "complete":
            return self._complete_creation()
        
        self.current_step = current_step_obj.next_step
        return True, self._get_current_step_display()
    
    def _complete_creation(self) -> Tuple[bool, str]:
        """完成公司创建"""
        try:
            # 保存会话数据以供后续使用
            business_model = self.current_session['business_model']
            strategy = self.current_session['strategy']
            funding = self.current_session['initial_funding']
            
            # 创建公司对象
            company = self._build_company()
            
            # 保存到公司管理器
            manager = self.main_app.company_manager
            manager.companies[company.company_id] = company
            
            # 记录用户公司
            user_id = self.current_session['user_id']
            if user_id not in manager.user_companies:
                manager.user_companies[user_id] = []
            manager.user_companies[user_id].append(company.company_id)
            
            # 扣除资金
            self.main_app.cash -= funding
            
            # 保存数据
            manager.save_companies()
            
            # 清理会话
            self.current_session = {}
            
            success_msg = f"""
🎉 恭喜！公司创建成功！

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                            🏢 {company.name} 🏢                            
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 公司标识:
  ⭐ 公司ID:   【{company.company_id}】       👈 重要！请记住此ID
  📊 股票代码: 【{company.symbol}】
  🏭 行业:     {company.industry.value.title()}
  
💰 财务状况:
  💵 初始投资: J${funding:,.0f}
  🏦 注册资本: J${company.metrics.assets:,.0f}
  👥 员工数量: {company.metrics.employees}人
  
🎯 发展规划:
  📈 商业模式: {business_model}
  🚀 发展战略: {strategy}
  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 快速入门指令:

  📊 查看公司详情:
    company info {company.company_id}
    
  🎯 开始经营管理:
    company manage {company.company_id}
    
  🌟 申请IPO上市:
    company ipo {company.company_id} <价格> <股数>
    
  📈 投资发展:
    company develop {company.company_id} <类型>
    
  📰 查看公司新闻:
    company news {company.company_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 创业提示:
  • 公司ID【{company.company_id}】是您管理公司的唯一标识
  • 通过持续的经营管理来提升公司价值
  • 达到条件后可申请IPO上市，实现财富增长目标！
  • 使用 'company my' 随时查看您的所有公司

🎊 祝您创业成功！
"""
            
            return False, success_msg
            
        except Exception as e:
            return False, f"❌ 公司创建失败: {str(e)}"
    
    def _build_company(self) -> JCCompany:
        """构建公司对象"""
        session = self.current_session
        
        # 基本信息
        company_name = session['company_name']
        industry = IndustryCategory(session['industry'])
        initial_funding = session['initial_funding']
        
        # 生成公司ID和股票代码
        company_id = f"JC_{industry.name[:3].upper()}_{random.randint(1000, 9999)}"
        symbol = self._generate_stock_symbol(company_name)
        
        # 根据团队配置和资金计算初始指标
        team_config = session['team_config']
        business_model = session['business_model']
        strategy = session['strategy']
        
        # 计算初始员工数
        team_configs = {
            '精英小队': (5, 15, 0.18),
            '均衡团队': (15, 50, 0.23),
            '规模团队': (50, 150, 0.28),
            '自动化优先': (3, 10, 0.13)
        }
        
        min_emp, max_emp, cost_ratio = team_configs.get(team_config, (10, 30, 0.20))
        employees = random.randint(min_emp, max_emp)
        hr_cost = initial_funding * cost_ratio
        
        # 计算其他初始指标
        assets = initial_funding * 0.8  # 80%转为资产
        liabilities = initial_funding * 0.3  # 30%负债
        
        # 基础营收 (基于行业和规模)
        industry_multipliers = {
            'technology': 1.5,
            'finance': 2.0,
            'healthcare': 1.3,
            'energy': 1.8,
            'manufacturing': 1.0,
            'retail': 0.8,
            'real_estate': 2.2,
            'transportation': 1.1,
            'telecom': 1.4,
            'utilities': 1.6,
            'consumer_goods': 0.9,
            'agriculture': 0.7
        }
        
        base_revenue = employees * 200000 * industry_multipliers.get(industry.value, 1.0)
        revenue = base_revenue * random.uniform(0.8, 1.2)
        
        # 利润 (基于商业模式)
        profit_margins = {
            'B2B服务': 0.25,
            'B2C销售': 0.15,
            '制造供应': 0.12,
            '平台连接': 0.35,
            '创新混合': 0.20
        }
        
        profit_margin = profit_margins.get(business_model, 0.18)
        profit = revenue * profit_margin * random.uniform(0.5, 1.5)
        
        # 其他指标
        market_share = random.uniform(0.001, 0.01)
        growth_rate = random.uniform(0.05, 0.25)
        debt_ratio = liabilities / assets if assets > 0 else 0.3
        
        # 创建业务指标
        metrics = BusinessMetrics(
            revenue=revenue,
            profit=profit,
            assets=assets,
            liabilities=liabilities,
            employees=employees,
            market_share=market_share,
            growth_rate=growth_rate,
            debt_ratio=debt_ratio
        )
        
        # 创建公司
        company = JCCompany(
            company_id=company_id,
            name=company_name,
            symbol=symbol,
            industry=industry,
            company_type=CompanyType.STARTUP,
            stage=CompanyStage.STARTUP,
            founded_date=datetime.now().strftime("%Y-%m-%d"),
            description=self._generate_company_description(company_name, industry, business_model),
            headquarters="JC经济特区",
            website=f"www.{symbol.lower()}.jc",
            ceo_name=session['user_id'],  # 创始人为CEO
            metrics=metrics,
            financials=CompanyFinancials(),
            created_by_user=session['user_id'],
            performance_score=random.uniform(45, 65),  # 初创公司表现一般
            risk_level=self._calculate_initial_risk_level(strategy, industry)
        )
        
        return company
    
    def _generate_stock_symbol(self, company_name: str) -> str:
        """生成股票代码"""
        # 提取中文拼音首字母或英文首字母
        clean_name = re.sub(r'[^\w\u4e00-\u9fff]', '', company_name)
        
        if len(clean_name) >= 4:
            symbol = clean_name[:4].upper()
        elif len(clean_name) >= 2:
            symbol = clean_name[:2].upper() + str(random.randint(10, 99))
        else:
            symbol = f"JC{random.randint(100, 999)}"
        
        # 确保唯一性
        existing_symbols = set()
        if hasattr(self.main_app, 'company_manager'):
            existing_symbols = set(self.main_app.company_manager.stock_symbols.keys())
        if hasattr(self.main_app, 'market_data'):
            existing_symbols.update(self.main_app.market_data.stocks.keys())
        
        base_symbol = symbol
        counter = 1
        while symbol in existing_symbols:
            symbol = f"{base_symbol[:2]}{counter:02d}"
            counter += 1
            
        return symbol
    
    def _generate_company_description(self, name: str, industry: IndustryCategory, model: str) -> str:
        """生成公司描述"""
        industry_descriptions = {
            'technology': "致力于技术创新和数字化解决方案",
            'finance': "提供专业的金融服务和投资管理",
            'healthcare': "专注于医疗健康和生物技术领域",
            'energy': "推动清洁能源和可持续发展",
            'manufacturing': "专业制造和工业解决方案提供商",
            'retail': "创新零售体验和消费者服务",
            'real_estate': "房地产开发和资产管理服务",
            'transportation': "智能交通和物流解决方案",
            'telecom': "通信技术和网络基础设施",
            'utilities': "公用事业和基础设施运营",
            'consumer_goods': "优质消费品制造和销售",
            'agriculture': "现代农业和食品安全解决方案"
        }
        
        base_desc = industry_descriptions.get(industry.value, "多元化业务发展")
        return f"{name}是一家{base_desc}的创新型企业，采用{model}的商业模式，致力于成为行业领先者。"
    
    def _calculate_initial_risk_level(self, strategy: str, industry: IndustryCategory) -> int:
        """计算初始风险等级"""
        base_risk = 3  # 初创公司基础风险
        
        # 战略风险调整
        strategy_risks = {
            '快速扩张': 2,
            '稳健发展': -1,
            '技术领先': 1,
            '市场渗透': 0,
            '多元化发展': 1
        }
        
        # 行业风险调整
        industry_risks = {
            'technology': 1,
            'finance': 0,
            'healthcare': -1,
            'energy': 1,
            'manufacturing': 0,
            'retail': 0,
            'real_estate': 1,
            'transportation': 0,
            'telecom': 0,
            'utilities': -1,
            'consumer_goods': -1,
            'agriculture': 0
        }
        
        risk = base_risk + strategy_risks.get(strategy, 0) + industry_risks.get(industry.value, 0)
        return max(1, min(5, risk))
    
    def _go_back(self) -> Tuple[bool, str]:
        """返回上一步"""
        if not self.current_session.get('step_history'):
            return True, "已经是第一步，无法返回"
        
        # 移除最后一步
        self.current_session['step_history'].pop()
        
        # 确定要返回的步骤
        if not self.current_session['step_history']:
            self.current_step = "welcome"
        else:
            last_step = self.current_session['step_history'][-1]['step']
            steps_list = list(self.creation_steps.keys())
            current_index = steps_list.index(last_step)
            self.current_step = steps_list[current_index + 1]
        
        return True, f"↩️ 已返回上一步\n\n{self._get_current_step_display()}"
    
    def _get_help_text(self) -> str:
        """获取帮助文本"""
        return """
📖 公司创建向导帮助

🎮 可用命令:
  • 按照提示输入相应内容
  • 'back' - 返回上一步
  • 'cancel' - 取消创建流程
  • 'help' - 显示此帮助

💡 创建提示:
  • 每个选择都会影响公司初始属性
  • 建议根据自己的资金情况选择合适的投资规模
  • 不同行业有不同的特点和发展前景
  • 可以随时返回修改之前的选择
"""
    
    def _generate_confirmation_display(self) -> str:
        """生成最终确认显示"""
        session = self.current_session
        
        # 预估初始数据
        funding = session['initial_funding']
        team_cost_ratios = {
            '精英小队': 0.18, '均衡团队': 0.23, 
            '规模团队': 0.28, '自动化优先': 0.13
        }
        team_cost = funding * team_cost_ratios.get(session['team_config'], 0.20)
        
        return f"""
────────────────────────────────────────────────────────────────────────────────────────
                               ✅ 公司创建信息确认                                 
────────────────────────────────────────────────────────────────────────────────────────

请仔细核对以下信息，确认无误后即可完成公司注册：

🏢 基本信息:
  公司名称: {session['company_name']}
  行业领域: {session['industry'].title()}
  注册地址: JC经济特区
  创立日期: {datetime.now().strftime('%Y年%m月%d日')}
  
💰 投资规划:
  初始投资: J${session['initial_funding']:,.0f}
  人力成本: J${team_cost:,.0f} ({team_cost/funding*100:.1f}%)
  运营资金: J${funding-team_cost:,.0f} ({(1-team_cost/funding)*100:.1f}%)
  
👥 团队配置: {session['team_config']}
📊 商业模式: {session['business_model']}  
🎯 发展战略: {session['strategy']}

💸 资金扣除: 将从您的账户扣除 J${session['initial_funding']:,.0f}
💼 当前余额: J${self.main_app.cash:,.0f}
💵 操作后余额: J${self.main_app.cash - session['initial_funding']:,.0f}

⚠️  重要提醒:
• 公司一旦创建将无法撤销
• 资金将立即从您的账户扣除
• 您将成为该公司的创始人和CEO
• 可通过经营管理提升公司价值并申请IPO

确认创建公司吗？ [输入 'confirm' 确认 / 'back' 返回修改]
"""

    # 验证函数
    def _validate_company_name(self, name: str) -> Tuple[bool, str]:
        """验证公司名称"""
        if not name:
            return False, "公司名称不能为空"
        if len(name) < 2:
            return False, "公司名称至少需要2个字符"
        if len(name) > 30:
            return False, "公司名称不能超过30个字符"
        return True, ""
    
    def _validate_industry(self, input_str: str) -> Tuple[bool, str]:
        """验证行业选择"""
        industry_map = {
            '1': 'technology', '2': 'healthcare', '3': 'energy',
            '4': 'manufacturing', '5': 'retail', '6': 'real_estate',
            '7': 'finance', '8': 'telecom', '9': 'transportation',
            '10': 'utilities', '11': 'consumer_goods', '12': 'agriculture'
        }
        
        if input_str in industry_map or input_str.lower() in industry_map.values():
            return True, ""
        
        return False, "无效的行业选择。请输入1-12的数字或有效的行业名称"
    
    def _parse_industry_input(self, input_str: str) -> str:
        """解析行业输入"""
        industry_map = {
            '1': 'technology', '2': 'healthcare', '3': 'energy',
            '4': 'manufacturing', '5': 'retail', '6': 'real_estate',
            '7': 'finance', '8': 'telecom', '9': 'transportation',
            '10': 'utilities', '11': 'consumer_goods', '12': 'agriculture'
        }
        
        if input_str in industry_map:
            return industry_map[input_str]
        
        return input_str.lower().strip()
    
    def _validate_funding(self, input_str: str) -> Tuple[bool, str]:
        """验证资金投入"""
        try:
            # 移除逗号和空格
            clean_input = input_str.replace(',', '').replace(' ', '')
            funding = float(clean_input)
            
            if funding < 1000000:  # 最低100万
                return False, "投资金额不能少于100万"
            
            if funding > 50000000:  # 最高5000万
                return False, "投资金额不能超过5000万"
            
            if funding > self.main_app.cash:
                return False, f"资金不足，您当前只有 J${self.main_app.cash:,.0f}"
            
            # 建议不超过总资产的70%
            if funding > self.main_app.cash * 0.7:
                return False, f"建议投资金额不超过总资产的70% (J${self.main_app.cash * 0.7:,.0f})"
            
            return True, ""
            
        except ValueError:
            return False, "请输入有效的数字金额"
    
    def _validate_team_config(self, input_str: str) -> Tuple[bool, str]:
        """验证团队配置"""
        valid_configs = ['精英小队', '均衡团队', '规模团队', '自动化优先']
        if input_str in valid_configs:
            return True, ""
        return False, f"请选择有效的团队配置: {', '.join(valid_configs)}"
    
    def _validate_business_model(self, input_str: str) -> Tuple[bool, str]:
        """验证商业模式"""
        valid_models = ['B2B服务', 'B2C销售', '制造供应', '平台连接', '创新混合']
        if input_str in valid_models:
            return True, ""
        return False, f"请选择有效的商业模式: {', '.join(valid_models)}"
    
    def _validate_strategy(self, input_str: str) -> Tuple[bool, str]:
        """验证发展战略"""
        valid_strategies = ['快速扩张', '稳健发展', '技术领先', '市场渗透', '多元化发展']
        if input_str in valid_strategies:
            return True, ""
        return False, f"请选择有效的发展战略: {', '.join(valid_strategies)}" 