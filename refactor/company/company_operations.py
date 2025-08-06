"""
JC公司运营管理系统
包含公司日常运营、投资决策、战略管理等功能
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from enum import Enum

from .company_types import JCCompany, CompanyStage, BusinessMetrics


class OperationType(Enum):
    """运营类型"""
    RESEARCH = "research"           # 研发投入
    MARKETING = "marketing"         # 市场营销
    EXPANSION = "expansion"         # 业务扩张
    EFFICIENCY = "efficiency"       # 效率提升
    TECHNOLOGY = "technology"       # 技术升级
    TALENT = "talent"              # 人才培养
    BRAND = "brand"                # 品牌建设
    INNOVATION = "innovation"       # 创新研发
    ACQUISITION = "acquisition"     # 收购并购
    PARTNERSHIP = "partnership"     # 战略合作


class CompanyOperations:
    """公司运营管理器"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.operation_cooldowns = {}  # {company_id: {operation: last_time}}
        
    def show_operations_menu(self, company_id: str) -> str:
        """显示运营管理菜单"""
        company = self.main_app.company_manager.companies.get(company_id)
        if not company:
            return "❌ 公司不存在"
            
        if company.created_by_user != self.main_app.user_manager.current_user:
            return "❌ 您不是该公司的创始人"
            
        menu_text = f"""
🏢 {company.name} - 运营管理中心

════════════════════════════════════════════════════════════════════════════════════════
                                   📊 公司状态概览                                    
════════════════════════════════════════════════════════════════════════════════════════

🏢 基本信息:
  公司名称: {company.name} ({company.symbol})
  发展阶段: {company.stage.value.title()}
  行业领域: {company.industry.value.title()}
  成立时间: {company.founded_date}
  
💰 财务状况:
  营业收入: J${company.metrics.revenue:,.0f}
  净利润: J${company.metrics.profit:,.0f}
  总资产: J${company.metrics.assets:,.0f}
  负债: J${company.metrics.liabilities:,.0f}
  净资产: J${company.metrics.calculate_equity():,.0f}
  
👥 人力资源:
  员工总数: {company.metrics.employees}人
  人均产值: J${company.metrics.revenue/company.metrics.employees:,.0f}/人
  
📈 经营指标:
  市场份额: {company.metrics.market_share*100:.3f}%
  增长率: {company.metrics.growth_rate*100:.1f}%
  债务率: {company.metrics.debt_ratio*100:.1f}%
  表现评分: {company.performance_score:.1f}/100
  风险等级: {company.risk_level}/5 ⭐
  
════════════════════════════════════════════════════════════════════════════════════════
                                   🎮 运营管理选项                                   
════════════════════════════════════════════════════════════════════════════════════════

📊 基础运营:
  [1] research     - 🔬 研发投入     │ 提升技术实力和创新能力
  [2] marketing    - 📢 市场营销     │ 扩大市场份额和品牌影响
  [3] expansion    - 🏗️ 业务扩张     │ 增加产能和市场覆盖
  [4] efficiency   - ⚡ 效率优化     │ 降低成本提升运营效率
  
🚀 高级运营:
  [5] technology   - 💻 技术升级     │ 投资先进技术和设备
  [6] talent       - 👥 人才培养     │ 招聘培训优秀人才
  [7] brand        - 🏆 品牌建设     │ 提升品牌价值和声誉
  [8] innovation   - 💡 创新研发     │ 突破性产品和服务
  
💼 战略运营:
  [9] acquisition  - 🤝 收购并购     │ 收购其他公司快速扩张
  [10] partnership - 🔗 战略合作     │ 与其他公司建立合作关系

📋 管理功能:
  status          - 📊 详细状态     │ 查看公司详细经营状况
  forecast        - 📈 业绩预测     │ 预测未来发展趋势
  reports         - 📄 财务报告     │ 生成财务和运营报告
  history         - 📚 运营历史     │ 查看历史运营记录
  ipo             - 📈 IPO准备      │ 申请公开上市
  
💡 使用方法: company operate <公司ID> <操作类型> [参数]
例如: company operate {company_id} research
"""
        
        # 显示冷却时间
        cooldowns = self._get_operation_cooldowns(company_id)
        if cooldowns:
            menu_text += "\n⏰ 操作冷却中:\n"
            for operation, remaining in cooldowns.items():
                menu_text += f"  {operation}: {remaining}小时后可用\n"
        
        return menu_text
    
    def execute_operation(self, company_id: str, operation_type: str, amount: Optional[float] = None) -> Tuple[bool, str]:
        """执行运营操作"""
        company = self.main_app.company_manager.companies.get(company_id)
        if not company:
            return False, "❌ 公司不存在"
            
        if company.created_by_user != self.main_app.user_manager.current_user:
            return False, "❌ 您不是该公司的创始人"
            
        # 检查冷却时间
        if self._is_operation_on_cooldown(company_id, operation_type):
            remaining = self._get_remaining_cooldown(company_id, operation_type)
            return False, f"❌ 操作冷却中，{remaining}小时后可用"
        
        # 执行对应操作
        operations_map = {
            'research': self._execute_research,
            'marketing': self._execute_marketing,
            'expansion': self._execute_expansion,
            'efficiency': self._execute_efficiency,
            'technology': self._execute_technology,
            'talent': self._execute_talent,
            'brand': self._execute_brand,
            'innovation': self._execute_innovation,
            'acquisition': self._execute_acquisition,
            'partnership': self._execute_partnership
        }
        
        operation_func = operations_map.get(operation_type)
        if not operation_func:
            return False, f"❌ 无效的操作类型: {operation_type}"
        
        try:
            success, result = operation_func(company, amount)
            
            if success:
                # 设置冷却时间
                self._set_operation_cooldown(company_id, operation_type)
                
                # 保存公司数据
                company.last_updated = datetime.now().isoformat()
                self.main_app.company_manager.save_companies()
                
                # 同步更新股价(如果已上市)
                if company.is_public:
                    self._update_stock_price_after_operation(company, operation_type)
            
            return success, result
            
        except Exception as e:
            return False, f"❌ 操作执行失败: {str(e)}"
    
    def _execute_research(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行研发投入"""
        # 计算投入成本
        if amount:
            cost = min(amount, self.main_app.cash)
        else:
            cost = max(company.metrics.revenue * 0.1, 1000000)  # 10%营收或100万最低
        
        if cost > self.main_app.cash:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
        
        # 扣除资金
        self.main_app.cash -= cost
        
        # 执行效果
        success_rate = 0.75 + (company.performance_score / 100) * 0.2  # 75-95%成功率
        
        if random.random() < success_rate:
            # 成功
            tech_boost = random.uniform(0.05, 0.15)
            growth_boost = random.uniform(0.02, 0.08)
            
            company.metrics.revenue *= (1 + tech_boost * 0.5)
            company.metrics.growth_rate += growth_boost
            company.performance_score += random.uniform(3, 8)
            
            # 降低风险
            company.risk_level = max(1, company.risk_level - random.randint(0, 1))
            
            # 生成新闻
            company.generate_news_event('product')
            
            result = f"""
✅ 研发投入成功！

💰 投入资金: J${cost:,.0f}
📊 效果评估:
  • 技术实力提升 {tech_boost*100:.1f}%
  • 增长率提升 +{growth_boost*100:.1f}%
  • 表现评分: {company.performance_score:.1f}/100
  • 风险等级: {company.risk_level}/5 ⭐

🔬 研发成果:
  • 推出了新的技术解决方案
  • 提高了产品竞争力
  • 为未来发展奠定技术基础
  
💡 建议: 继续加大研发投入，保持技术领先优势
"""
        else:
            # 失败
            minor_boost = random.uniform(0.01, 0.03)
            company.metrics.revenue *= (1 + minor_boost)
            
            result = f"""
⚠️ 研发项目效果不佳

💰 投入资金: J${cost:,.0f}
📊 效果评估:
  • 技术提升有限 {minor_boost*100:.1f}%
  • 虽未达预期，但积累了宝贵经验
  
🔍 问题分析:
  • 技术路线选择可能有误
  • 研发团队能力需要提升
  • 市场需求判断不够准确
  
💡 建议: 总结经验教训，调整研发方向
"""
        
        return True, result
    
    def _execute_marketing(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行市场营销"""
        if amount:
            cost = min(amount, self.main_app.cash)
        else:
            cost = max(company.metrics.revenue * 0.08, 800000)  # 8%营收或80万最低
        
        if cost > self.main_app.cash:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
        
        self.main_app.cash -= cost
        
        # 营销效果
        market_boost = random.uniform(0.002, 0.008)
        revenue_boost = random.uniform(0.08, 0.18)
        brand_boost = random.uniform(2, 6)
        
        company.metrics.market_share += market_boost
        company.metrics.revenue *= (1 + revenue_boost)
        company.performance_score += brand_boost
        
        # 行业影响
        industry_bonus = self._get_industry_marketing_bonus(company.industry.value)
        company.metrics.revenue *= (1 + industry_bonus)
        
        result = f"""
✅ 市场营销活动成功！

💰 投入资金: J${cost:,.0f}
📊 营销效果:
  • 市场份额增加 +{market_boost*100:.3f}%
  • 营收提升 +{revenue_boost*100:.1f}%
  • 品牌价值提升 +{brand_boost:.1f}分
  • 行业加成 +{industry_bonus*100:.1f}%

📢 营销成果:
  • 品牌知名度显著提升
  • 客户获取成本降低
  • 市场竞争力增强
  • 销售渠道拓展

💡 建议: 持续营销投入，巩固市场地位
"""
        
        return True, result
    
    def _execute_expansion(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行业务扩张"""
        if amount:
            cost = min(amount, self.main_app.cash)
        else:
            cost = max(company.metrics.revenue * 0.15, 2000000)  # 15%营收或200万最低
        
        if cost > self.main_app.cash:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
        
        self.main_app.cash -= cost
        
        # 扩张效果 - 不直接增加员工数，避免数据不一致
        # employee_growth = int(cost / 100000)  # 每10万雇佣1人 - 已改为招聘建议
        asset_growth = cost * random.uniform(1.1, 1.8)
        capacity_growth = random.uniform(0.1, 0.25)
        suggested_hiring_budget = int(cost * 0.3)  # 建议用30%资金招聘
        
        # company.metrics.employees += employee_growth  # 🔧 修复：不再直接修改员工数
        company.metrics.assets += asset_growth
        company.metrics.revenue *= (1 + capacity_growth)
        company.metrics.growth_rate += random.uniform(0.03, 0.08)
        
        # 检查阶段提升 - 使用实际员工数量
        stage_msg = ""
        actual_employees = len(company.staff_list)
        if company.stage == CompanyStage.STARTUP and actual_employees > 100:
            company.stage = CompanyStage.GROWTH
            stage_msg = "🎉 公司进入成长期！"
        elif company.stage == CompanyStage.GROWTH and actual_employees > 500:
            company.stage = CompanyStage.MATURE
            stage_msg = "🎉 公司进入成熟期！"
        
        result = f"""
✅ 业务扩张成功完成！

💰 投入资金: J${cost:,.0f}
📊 扩张成果:
  • 资产增长: J${asset_growth:,.0f}
  • 产能提升: +{capacity_growth*100:.1f}%
  • 增长率: +{company.metrics.growth_rate*100:.1f}%
  • 建议招聘预算: J${suggested_hiring_budget:,.0f}

🏗️ 扩张详情:
  • 新建/租赁办公场所
  • 扩充生产线/服务能力
  • 建立新的销售网点
  • 进入新的市场区域

{stage_msg}

💡 建议: 关注管理效率，避免扩张过快带来的管理问题
"""
        
        return True, result
    
    def _execute_efficiency(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行效率优化"""
        if amount:
            cost = min(amount, self.main_app.cash)
        else:
            cost = max(company.metrics.revenue * 0.05, 500000)  # 5%营收或50万最低
        
        if cost > self.main_app.cash:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
        
        self.main_app.cash -= cost
        
        # 效率提升
        profit_improvement = company.metrics.revenue * random.uniform(0.03, 0.10)
        cost_reduction = random.uniform(0.05, 0.15)
        debt_reduction = random.uniform(0.02, 0.06)
        
        company.metrics.profit += profit_improvement
        company.metrics.debt_ratio = max(0.1, company.metrics.debt_ratio - debt_reduction)
        company.performance_score += random.uniform(4, 8)
        
        # 降低运营成本
        company.metrics.liabilities *= (1 - cost_reduction * 0.5)
        
        result = f"""
✅ 效率优化项目成功！

💰 投入资金: J${cost:,.0f}
📊 优化成果:
  • 利润提升: J${profit_improvement:,.0f}
  • 成本降低: -{cost_reduction*100:.1f}%
  • 债务率减少: -{debt_reduction*100:.1f}%
  • 表现评分: {company.performance_score:.1f}/100

⚡ 优化措施:
  • 流程再造和标准化
  • 自动化系统升级
  • 供应链优化
  • 组织架构调整

💡 效益分析:
  • 人均产值提高
  • 资源利用率提升
  • 管理成本降低
  • 响应速度加快

💡 建议: 建立持续改进机制，定期优化运营流程
"""
        
        return True, result
    
    def _execute_technology(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行技术升级"""
        if amount:
            cost = min(amount, self.main_app.cash)
        else:
            cost = max(company.metrics.revenue * 0.12, 1500000)  # 12%营收或150万最低
        
        if cost > self.main_app.cash:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
        
        self.main_app.cash -= cost
        
        # 技术升级效果
        tech_level_boost = random.uniform(0.10, 0.20)
        automation_bonus = random.uniform(0.05, 0.12)
        innovation_bonus = random.uniform(3, 7)
        
        company.metrics.revenue *= (1 + tech_level_boost)
        company.metrics.profit *= (1 + automation_bonus)
        company.performance_score += innovation_bonus
        
        # 技术资产
        company.metrics.assets += cost * 0.7
        
        result = f"""
✅ 技术升级项目成功！

💰 投入资金: J${cost:,.0f}
📊 升级效果:
  • 技术水平提升: +{tech_level_boost*100:.1f}%
  • 自动化收益: +{automation_bonus*100:.1f}%
  • 创新能力: +{innovation_bonus:.1f}分
  • 技术资产: J${cost * 0.7:,.0f}

💻 技术成果:
  • 核心系统全面升级
  • 引入先进生产设备
  • 建立数字化管理平台
  • 提升产品技术含量

🔬 技术优势:
  • 生产效率大幅提升
  • 产品质量显著改善
  • 成本控制能力增强
  • 市场竞争力提高

💡 建议: 持续关注行业技术趋势，保持技术领先地位
"""
        
        return True, result
    
    def _execute_talent(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行人才培养"""
        if amount:
            cost = min(amount, self.main_app.cash)
        else:
            cost = max(company.metrics.employees * 50000, 1000000)  # 每人5万或100万最低
        
        if cost > self.main_app.cash:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
        
        self.main_app.cash -= cost
        
        # 人才效果 - 改为培训现有员工，不虚拟增加员工
        talent_boost = random.uniform(0.08, 0.15)
        productivity_boost = random.uniform(0.06, 0.12)
        
        # 🔧 修复：提升现有员工表现，而非虚拟增加员工数
        for staff in company.staff_list:
            staff['performance'] = min(100, staff['performance'] + random.uniform(2, 8))
        
        suggested_hiring_budget = int(cost * 0.4)  # 建议用40%资金招聘
        # company.metrics.employees += new_employees  # 🔧 修复：不再虚拟增加员工
        company.metrics.revenue *= (1 + talent_boost)
        company.metrics.profit *= (1 + productivity_boost)
        company.performance_score += random.uniform(3, 6)
        
        result = f"""
✅ 人才培养计划成功！

💰 投入资金: J${cost:,.0f}
📊 人才成果:
  • 员工技能提升: 现有员工表现+2~8分
  • 人才效能提升: +{talent_boost*100:.1f}%
  • 生产力提升: +{productivity_boost*100:.1f}%
  • 建议招聘预算: J${suggested_hiring_budget:,.0f}

👥 人才措施:
  • 高薪招聘行业精英
  • 员工技能培训提升
  • 建立激励奖励机制
  • 完善职业发展通道

🎯 人才优势:
  • 核心竞争力增强
  • 创新能力提升
  • 管理效率改善
  • 企业文化建设

💡 建议: 建立长期人才发展战略，留住核心人才
"""
        
        return True, result
    
    def _execute_brand(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行品牌建设"""
        if amount:
            cost = min(amount, self.main_app.cash)
        else:
            cost = max(company.metrics.revenue * 0.06, 1200000)  # 6%营收或120万最低
        
        if cost > self.main_app.cash:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
        
        self.main_app.cash -= cost
        
        # 品牌效果
        brand_value_boost = random.uniform(0.08, 0.16)
        market_premium = random.uniform(0.03, 0.08)
        loyalty_boost = random.uniform(0.05, 0.12)
        
        company.metrics.revenue *= (1 + brand_value_boost)
        company.metrics.market_share += market_premium * 0.5
        company.performance_score += random.uniform(5, 10)
        
        # 降低风险(品牌溢价)
        company.risk_level = max(1, company.risk_level - 1)
        
        result = f"""
✅ 品牌建设项目成功！

💰 投入资金: J${cost:,.0f}
📊 品牌效果:
  • 品牌价值提升: +{brand_value_boost*100:.1f}%
  • 市场溢价: +{market_premium*100:.1f}%
  • 客户忠诚度: +{loyalty_boost*100:.1f}%
  • 风险等级降低: {company.risk_level}/5 ⭐

🏆 品牌成果:
  • 品牌知名度全面提升
  • 建立独特品牌形象
  • 获得市场溢价能力
  • 客户粘性显著增强

📢 品牌策略:
  • 全媒体品牌推广
  • 赞助重要行业活动
  • 建立品牌体验中心
  • 开展公益社会活动

💡 建议: 持续维护品牌形象，提升品牌文化内涵
"""
        
        return True, result
    
    def _execute_innovation(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行创新研发"""
        if amount:
            cost = min(amount, self.main_app.cash)
        else:
            cost = max(company.metrics.revenue * 0.15, 2000000)  # 15%营收或200万最低
        
        if cost > self.main_app.cash:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
        
        self.main_app.cash -= cost
        
        # 创新风险较高但收益也高
        success_rate = 0.65 + (company.performance_score / 100) * 0.25  # 65-90%成功率
        
        if random.random() < success_rate:
            # 创新成功
            breakthrough_boost = random.uniform(0.20, 0.35)
            market_disruption = random.uniform(0.05, 0.15)
            future_potential = random.uniform(0.08, 0.15)
            
            company.metrics.revenue *= (1 + breakthrough_boost)
            company.metrics.profit *= (1 + breakthrough_boost * 1.2)
            company.metrics.growth_rate += future_potential
            company.metrics.market_share += market_disruption
            company.performance_score += random.uniform(8, 15)
            
            # 生成重大新闻
            company.generate_news_event('product')
            
            result = f"""
🎉 创新研发取得重大突破！

💰 投入资金: J${cost:,.0f}
📊 创新成果:
  • 突破性增长: +{breakthrough_boost*100:.1f}%
  • 市场颠覆效应: +{market_disruption*100:.1f}%
  • 未来发展潜力: +{future_potential*100:.1f}%
  • 表现评分飞跃: {company.performance_score:.1f}/100

💡 创新亮点:
  • 推出颠覆性产品/服务
  • 获得核心技术专利
  • 建立技术壁垒优势
  • 引领行业发展方向

🚀 市场影响:
  • 重新定义行业标准
  • 获得巨大先发优势
  • 吸引大量客户关注
  • 提升投资者信心

💡 建议: 加快成果商业化，建立专利保护体系
"""
        else:
            # 创新失败
            minor_gain = random.uniform(0.02, 0.05)
            experience_gain = random.uniform(1, 3)
            
            company.metrics.revenue *= (1 + minor_gain)
            company.performance_score += experience_gain
            
            result = f"""
⚠️ 创新研发未达预期

💰 投入资金: J${cost:,.0f}
📊 项目结果:
  • 技术突破有限: +{minor_gain*100:.1f}%
  • 积累宝贵经验: +{experience_gain:.1f}分
  • 为下次创新奠定基础

🔍 失败分析:
  • 技术路线可能过于激进
  • 市场时机尚不成熟
  • 资源投入可能不足
  • 外部环境存在限制

📚 经验收获:
  • 识别了技术难点
  • 培养了研发团队
  • 建立了创新机制
  • 积累了失败经验

💡 建议: 总结经验教训，调整创新策略，准备下次突破
"""
        
        return True, result
    
    def _execute_acquisition(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行收购并购"""
        # 收购需要特殊处理，这里是简化版本
        cost = amount or 10000000  # 默认1000万收购
        
        # 🔧 修复：使用公司账户而非个人账户
        if cost > company.company_cash:
            shortage = cost - company.company_cash
            return False, f"""❌ 公司账户资金不足
  需要: J${cost:,.0f}
  现有: J${company.company_cash:,.0f}
  缺口: J${shortage:,.0f}
  
💡 建议: 先向公司注资 J${shortage:,.0f}"""
        
        if cost < 5000000:
            return False, "❌ 收购金额不能少于500万"
        
        # 扣除公司资金
        company.company_cash -= cost
        
        # 收购效果
        synergy_effect = random.uniform(0.10, 0.25)
        market_consolidation = random.uniform(0.02, 0.08)
        scale_economy = random.uniform(0.05, 0.12)
        
        company.metrics.revenue *= (1 + synergy_effect)
        company.metrics.assets += cost * 0.8
        company.metrics.market_share += market_consolidation
        # 🔧 修复：收购时建议招聘预算而非虚拟员工
        suggested_hiring_budget = int(cost / 10)  # 建议用10%资金招聘收购来的人才
        # company.metrics.employees += int(cost / 200000)  # 每20万1个员工 - 改为招聘建议
        
        result = f"""
✅ 收购项目成功完成！

💰 收购金额: J${cost:,.0f}
📊 并购效果:
  • 协同效应: +{synergy_effect*100:.1f}%
  • 市场整合: +{market_consolidation*100:.2f}%
  • 规模经济: +{scale_economy*100:.1f}%
  • 建议招聘预算: J${suggested_hiring_budget:,.0f}

🤝 收购成果:
  • 成功整合目标企业
  • 扩大市场覆盖范围
  • 获得核心技术资产
  • 实现规模经济效应

📈 战略价值:
  • 快速获得市场份额
  • 消除潜在竞争对手
  • 获得优质客户资源
  • 增强产业链控制力

💡 建议: 关注整合效果，实现1+1>2的协同效应
"""
        
        return True, result
    
    def _execute_partnership(self, company: JCCompany, amount: Optional[float]) -> Tuple[bool, str]:
        """执行战略合作"""
        cost = amount or 5000000  # 默认500万合作投资
        
        # 🔧 修复：使用公司账户而非个人账户
        if cost > company.company_cash:
            shortage = cost - company.company_cash
            return False, f"""❌ 公司账户资金不足
  需要: J${cost:,.0f}
  现有: J${company.company_cash:,.0f}
  缺口: J${shortage:,.0f}
  
💡 建议: 先向公司注资 J${shortage:,.0f}"""
        
        if cost < 1000000:
            return False, "❌ 合作投资不能少于100万"
        
        # 扣除公司资金
        company.company_cash -= cost
        
        # 合作效果
        cooperation_boost = random.uniform(0.06, 0.14)
        resource_sharing = random.uniform(0.03, 0.08)
        risk_reduction = random.uniform(0.02, 0.05)
        
        company.metrics.revenue *= (1 + cooperation_boost)
        company.metrics.growth_rate += resource_sharing
        company.risk_level = max(1, company.risk_level - 1)
        
        result = f"""
✅ 战略合作协议签署成功！

💰 合作投资: J${cost:,.0f}
📊 合作效果:
  • 合作增效: +{cooperation_boost*100:.1f}%
  • 资源共享: +{resource_sharing*100:.1f}%
  • 风险分散: -{risk_reduction*100:.1f}%
  • 风险等级: {company.risk_level}/5 ⭐

🔗 合作内容:
  • 建立战略合作联盟
  • 共享研发和技术资源
  • 联合开拓新市场
  • 优化供应链管理

🎯 合作价值:
  • 降低单独发展风险
  • 获得互补核心能力
  • 扩大市场影响力
  • 提升竞争优势

💡 建议: 维护合作关系，探索更深层次的合作机会
"""
        
        return True, result
    
    def _get_industry_marketing_bonus(self, industry: str) -> float:
        """获取行业营销加成"""
        bonuses = {
            'technology': 0.05,
            'retail': 0.08,
            'finance': 0.03,
            'healthcare': 0.04,
            'consumer_goods': 0.07,
            'telecom': 0.06
        }
        return bonuses.get(industry, 0.04)
    
    def _set_operation_cooldown(self, company_id: str, operation_type: str):
        """设置操作冷却时间"""
        if company_id not in self.operation_cooldowns:
            self.operation_cooldowns[company_id] = {}
        
        # 不同操作有不同冷却时间
        cooldown_hours = {
            'research': 24,
            'marketing': 12,
            'expansion': 48,
            'efficiency': 18,
            'technology': 36,
            'talent': 24,
            'brand': 30,
            'innovation': 72,
            'acquisition': 168,  # 一周
            'partnership': 120   # 5天
        }
        
        hours = cooldown_hours.get(operation_type, 24)
        cooldown_end = datetime.now() + timedelta(hours=hours)
        self.operation_cooldowns[company_id][operation_type] = cooldown_end.isoformat()
    
    def _is_operation_on_cooldown(self, company_id: str, operation_type: str) -> bool:
        """检查操作是否在冷却中"""
        if company_id not in self.operation_cooldowns:
            return False
        
        if operation_type not in self.operation_cooldowns[company_id]:
            return False
        
        cooldown_end = datetime.fromisoformat(self.operation_cooldowns[company_id][operation_type])
        return datetime.now() < cooldown_end
    
    def _get_remaining_cooldown(self, company_id: str, operation_type: str) -> float:
        """获取剩余冷却时间(小时)"""
        if not self._is_operation_on_cooldown(company_id, operation_type):
            return 0
        
        cooldown_end = datetime.fromisoformat(self.operation_cooldowns[company_id][operation_type])
        remaining = cooldown_end - datetime.now()
        return max(0, remaining.total_seconds() / 3600)
    
    def _get_operation_cooldowns(self, company_id: str) -> Dict[str, float]:
        """获取所有操作的冷却时间"""
        if company_id not in self.operation_cooldowns:
            return {}
        
        cooldowns = {}
        for operation, cooldown_end_str in self.operation_cooldowns[company_id].items():
            cooldown_end = datetime.fromisoformat(cooldown_end_str)
            if datetime.now() < cooldown_end:
                remaining = cooldown_end - datetime.now()
                cooldowns[operation] = round(remaining.total_seconds() / 3600, 1)
        
        return cooldowns
    
    def _update_stock_price_after_operation(self, company: JCCompany, operation_type: str):
        """操作后更新股价"""
        if not company.is_public or not hasattr(self.main_app, 'market_data'):
            return
        
        if company.symbol not in self.main_app.market_data.stocks:
            return
        
        # 根据操作类型调整股价
        price_impacts = {
            'research': random.uniform(0.02, 0.05),
            'marketing': random.uniform(0.01, 0.03),
            'expansion': random.uniform(0.03, 0.06),
            'efficiency': random.uniform(0.02, 0.04),
            'technology': random.uniform(0.04, 0.07),
            'talent': random.uniform(0.02, 0.04),
            'brand': random.uniform(0.02, 0.05),
            'innovation': random.uniform(0.05, 0.10),
            'acquisition': random.uniform(0.03, 0.08),
            'partnership': random.uniform(0.01, 0.04)
        }
        
        impact = price_impacts.get(operation_type, 0.02)
        stock_data = self.main_app.market_data.stocks[company.symbol]
        old_price = stock_data['price']
        new_price = old_price * (1 + impact)
        
        stock_data['price'] = new_price
        stock_data['change'] = new_price - old_price
        stock_data['last_updated'] = datetime.now().isoformat()
        
        company.update_stock_price(new_price) 