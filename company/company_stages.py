"""
JC公司发展阶段管理系统
定义不同发展阶段的特性、升级条件和专有功能
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

from .company_types import CompanyStage, JCCompany


@dataclass
class StageRequirement:
    """阶段升级要求"""
    min_revenue: float
    min_employees: int
    min_performance_score: float
    min_market_share: float
    max_debt_ratio: float
    min_age_days: int
    special_conditions: List[str] = None


@dataclass
class StageFeatures:
    """阶段特性"""
    stage: CompanyStage
    name: str
    description: str
    max_employees: int
    revenue_multiplier: float
    risk_modifier: int
    available_operations: List[str]
    upgrade_benefits: List[str]
    special_abilities: List[str]


class CompanyStageManager:
    """公司阶段管理器"""
    
    def __init__(self):
        self.stage_requirements = self._init_stage_requirements()
        self.stage_features = self._init_stage_features()
        
    def _init_stage_requirements(self) -> Dict[CompanyStage, StageRequirement]:
        """初始化阶段升级要求"""
        return {
            CompanyStage.GROWTH: StageRequirement(
                min_revenue=5000000,      # 500万营收
                min_employees=50,         # 50名员工
                min_performance_score=60, # 60分表现
                min_market_share=0.005,   # 0.5%市场份额
                max_debt_ratio=0.7,       # 最高70%负债率
                min_age_days=90,          # 成立90天
                special_conditions=[
                    "完成至少3次成功的运营投资",
                    "连续3个季度盈利"
                ]
            ),
            
            CompanyStage.MATURE: StageRequirement(
                min_revenue=50000000,     # 5000万营收
                min_employees=200,        # 200名员工
                min_performance_score=75, # 75分表现
                min_market_share=0.02,    # 2%市场份额
                max_debt_ratio=0.5,       # 最高50%负债率
                min_age_days=365,         # 成立1年
                special_conditions=[
                    "建立完整的管理体系",
                    "拥有核心技术或专利",
                    "年度盈利超过1000万"
                ]
            ),
            
            CompanyStage.EXPANSION: StageRequirement(
                min_revenue=200000000,    # 2亿营收
                min_employees=500,        # 500名员工
                min_performance_score=85, # 85分表现
                min_market_share=0.05,    # 5%市场份额
                max_debt_ratio=0.4,       # 最高40%负债率
                min_age_days=730,         # 成立2年
                special_conditions=[
                    "成功进入3个以上细分市场",
                    "建立全国性销售网络",
                    "完成至少1次成功收购"
                ]
            ),
            
            CompanyStage.CORPORATE: StageRequirement(
                min_revenue=1000000000,   # 10亿营收
                min_employees=2000,       # 2000名员工
                min_performance_score=90, # 90分表现
                min_market_share=0.1,     # 10%市场份额
                max_debt_ratio=0.3,       # 最高30%负债率
                min_age_days=1460,        # 成立4年
                special_conditions=[
                    "成为行业领导者",
                    "建立国际业务",
                    "拥有多个子公司或品牌"
                ]
            )
        }
    
    def _init_stage_features(self) -> Dict[CompanyStage, StageFeatures]:
        """初始化阶段特性"""
        return {
            CompanyStage.STARTUP: StageFeatures(
                stage=CompanyStage.STARTUP,
                name="初创阶段",
                description="刚刚成立的新兴企业，充满活力但面临高风险",
                max_employees=100,
                revenue_multiplier=1.0,
                risk_modifier=2,
                available_operations=[
                    "research", "marketing", "efficiency", "talent"
                ],
                upgrade_benefits=[
                    "灵活的组织结构",
                    "快速决策能力",
                    "创新思维活跃"
                ],
                special_abilities=[
                    "天使投资吸引：更容易获得初期投资",
                    "政策扶持：享受创业优惠政策",
                    "人才吸引：用股权激励吸引优秀人才"
                ]
            ),
            
            CompanyStage.GROWTH: StageFeatures(
                stage=CompanyStage.GROWTH,
                name="成长阶段",
                description="业务快速发展的企业，开始建立市场地位",
                max_employees=500,
                revenue_multiplier=1.2,
                risk_modifier=1,
                available_operations=[
                    "research", "marketing", "expansion", "efficiency", 
                    "technology", "talent", "brand"
                ],
                upgrade_benefits=[
                    "规模经济初现",
                    "品牌认知度提升",
                    "管理体系完善"
                ],
                special_abilities=[
                    "风险投资：获得VC投资机会",
                    "市场扩张：快速进入新市场",
                    "人才梯队：建立培训体系"
                ]
            ),
            
            CompanyStage.MATURE: StageFeatures(
                stage=CompanyStage.MATURE,
                name="成熟阶段",
                description="稳定发展的成熟企业，具备较强竞争力",
                max_employees=2000,
                revenue_multiplier=1.4,
                risk_modifier=0,
                available_operations=[
                    "research", "marketing", "expansion", "efficiency",
                    "technology", "talent", "brand", "innovation", 
                    "acquisition", "partnership"
                ],
                upgrade_benefits=[
                    "稳定的现金流",
                    "强大的市场地位",
                    "完善的管理制度"
                ],
                special_abilities=[
                    "IPO准备：具备上市条件",
                    "战略投资：可投资其他企业",
                    "行业影响：对行业发展有影响力"
                ]
            ),
            
            CompanyStage.EXPANSION: StageFeatures(
                stage=CompanyStage.EXPANSION,
                name="扩张阶段", 
                description="大规模扩张的企业，向行业领导者迈进",
                max_employees=5000,
                revenue_multiplier=1.6,
                risk_modifier=-1,
                available_operations=[
                    "research", "marketing", "expansion", "efficiency",
                    "technology", "talent", "brand", "innovation",
                    "acquisition", "partnership", "internationalization"
                ],
                upgrade_benefits=[
                    "多元化业务布局",
                    "国际市场开拓",
                    "产业链整合能力"
                ],
                special_abilities=[
                    "国际扩张：进入海外市场",
                    "产业整合：收购上下游企业",
                    "平台建设：构建生态系统"
                ]
            ),
            
            CompanyStage.CORPORATE: StageFeatures(
                stage=CompanyStage.CORPORATE,
                name="集团阶段",
                description="大型企业集团，行业领导者地位",
                max_employees=20000,
                revenue_multiplier=2.0,
                risk_modifier=-2,
                available_operations=[
                    "research", "marketing", "expansion", "efficiency",
                    "technology", "talent", "brand", "innovation",
                    "acquisition", "partnership", "internationalization",
                    "diversification", "monopolization"
                ],
                upgrade_benefits=[
                    "行业领导地位",
                    "全球化布局",
                    "多元化发展"
                ],
                special_abilities=[
                    "行业标准：制定行业标准",
                    "政策影响：影响政府政策",
                    "生态主导：主导产业生态"
                ]
            )
        }
    
    def check_stage_upgrade(self, company: JCCompany) -> Tuple[bool, str, Optional[CompanyStage]]:
        """检查公司是否可以升级阶段"""
        current_stage = company.stage
        
        # 如果已经是最高阶段
        if current_stage == CompanyStage.CORPORATE:
            return False, "已达到最高发展阶段", None
        
        # 确定下一阶段
        stage_order = [
            CompanyStage.STARTUP,
            CompanyStage.GROWTH, 
            CompanyStage.MATURE,
            CompanyStage.EXPANSION,
            CompanyStage.CORPORATE
        ]
        
        current_index = stage_order.index(current_stage)
        next_stage = stage_order[current_index + 1]
        
        # 检查升级条件
        can_upgrade, reason = self._check_upgrade_requirements(company, next_stage)
        
        if can_upgrade:
            return True, f"✅ 符合{self.stage_features[next_stage].name}升级条件", next_stage
        else:
            return False, reason, None
    
    def _check_upgrade_requirements(self, company: JCCompany, target_stage: CompanyStage) -> Tuple[bool, str]:
        """检查升级要求"""
        requirements = self.stage_requirements[target_stage]
        
        # 检查营收
        if company.metrics.revenue < requirements.min_revenue:
            return False, f"营收不足：需要 J${requirements.min_revenue:,.0f}，当前 J${company.metrics.revenue:,.0f}"
        
        # 检查员工数
        if company.metrics.employees < requirements.min_employees:
            return False, f"员工不足：需要 {requirements.min_employees}人，当前 {company.metrics.employees}人"
        
        # 检查表现评分
        if company.performance_score < requirements.min_performance_score:
            return False, f"表现评分不足：需要 {requirements.min_performance_score}分，当前 {company.performance_score:.1f}分"
        
        # 检查市场份额
        if company.metrics.market_share < requirements.min_market_share:
            return False, f"市场份额不足：需要 {requirements.min_market_share*100:.2f}%，当前 {company.metrics.market_share*100:.3f}%"
        
        # 检查债务率
        if company.metrics.debt_ratio > requirements.max_debt_ratio:
            return False, f"债务率过高：需要低于 {requirements.max_debt_ratio*100:.0f}%，当前 {company.metrics.debt_ratio*100:.1f}%"
        
        # 检查成立时间
        founded_date = datetime.strptime(company.founded_date, "%Y-%m-%d")
        days_since_founded = (datetime.now() - founded_date).days
        
        if days_since_founded < requirements.min_age_days:
            return False, f"成立时间不足：需要 {requirements.min_age_days}天，当前 {days_since_founded}天"
        
        # 检查特殊条件（简化处理）
        if requirements.special_conditions:
            # 这里可以根据公司历史数据检查特殊条件
            # 简化处理：基于公司表现评分判断
            special_score = company.performance_score + (company.metrics.growth_rate * 100)
            required_special_score = {
                CompanyStage.GROWTH: 80,
                CompanyStage.MATURE: 120,
                CompanyStage.EXPANSION: 160,
                CompanyStage.CORPORATE: 200
            }.get(target_stage, 100)
            
            if special_score < required_special_score:
                return False, f"特殊条件不满足：综合评估分数需要 {required_special_score}，当前 {special_score:.1f}"
        
        return True, "符合所有升级条件"
    
    def execute_stage_upgrade(self, company: JCCompany, new_stage: CompanyStage) -> str:
        """执行阶段升级"""
        old_stage = company.stage
        company.stage = new_stage
        
        # 应用阶段升级效果
        features = self.stage_features[new_stage]
        
        # 获得阶段奖励
        revenue_bonus = company.metrics.revenue * 0.1  # 10%营收奖励
        company.metrics.revenue += revenue_bonus
        
        # 降低风险等级
        company.risk_level = max(1, company.risk_level + features.risk_modifier)
        
        # 提升表现评分
        company.performance_score += 10
        
        # 生成升级新闻
        company.generate_news_event('management')
        
        upgrade_message = f"""
🎉 恭喜！{company.name} 成功升级！

📈 发展阶段升级:
  从 {self.stage_features[old_stage].name} → {features.name}
  
🎁 升级奖励:
  • 营收奖励: +J${revenue_bonus:,.0f}
  • 风险等级: {company.risk_level}/5 ⭐
  • 表现评分: {company.performance_score:.1f}/100
  
🚀 新阶段特性:
  • {features.description}
  • 最大员工数: {features.max_employees:,}人
  • 营收倍数: {features.revenue_multiplier}x
  
💪 解锁能力:
"""
        
        for ability in features.special_abilities:
            upgrade_message += f"  • {ability}\n"
        
        upgrade_message += f"""
📋 可用操作:
  {', '.join(features.available_operations)}
  
🎯 下一阶段目标:
"""
        
        # 显示下一阶段要求
        stage_order = [
            CompanyStage.STARTUP, CompanyStage.GROWTH, CompanyStage.MATURE,
            CompanyStage.EXPANSION, CompanyStage.CORPORATE
        ]
        
        if new_stage != CompanyStage.CORPORATE:
            current_index = stage_order.index(new_stage)
            next_stage = stage_order[current_index + 1]
            next_requirements = self.stage_requirements[next_stage]
            next_features = self.stage_features[next_stage]
            
            upgrade_message += f"  目标阶段: {next_features.name}\n"
            upgrade_message += f"  营收目标: J${next_requirements.min_revenue:,.0f}\n"
            upgrade_message += f"  员工目标: {next_requirements.min_employees:,}人\n"
            upgrade_message += f"  表现目标: {next_requirements.min_performance_score}分\n"
        else:
            upgrade_message += "  🏆 已达到最高发展阶段！\n"
        
        return upgrade_message
    
    def get_stage_info(self, stage: CompanyStage) -> str:
        """获取阶段信息"""
        features = self.stage_features[stage]
        
        info = f"""
🏢 {features.name} 详细信息

📋 阶段描述:
  {features.description}

📊 阶段特性:
  • 最大员工数: {features.max_employees:,}人
  • 营收倍数: {features.revenue_multiplier}x
  • 风险调整: {features.risk_modifier:+d}

🎮 可用操作:
"""
        
        for operation in features.available_operations:
            operation_names = {
                'research': '🔬 研发投入',
                'marketing': '📢 市场营销',
                'expansion': '🏗️ 业务扩张',
                'efficiency': '⚡ 效率优化',
                'technology': '💻 技术升级',
                'talent': '👥 人才培养',
                'brand': '🏆 品牌建设',
                'innovation': '💡 创新研发',
                'acquisition': '🤝 收购并购',
                'partnership': '🔗 战略合作',
                'internationalization': '🌍 国际化',
                'diversification': '🔄 多元化',
                'monopolization': '👑 垄断化'
            }
            
            op_name = operation_names.get(operation, operation)
            info += f"  • {op_name}\n"
        
        info += f"""
💪 特殊能力:
"""
        
        for ability in features.special_abilities:
            info += f"  • {ability}\n"
        
        info += f"""
🎁 升级优势:
"""
        
        for benefit in features.upgrade_benefits:
            info += f"  • {benefit}\n"
        
        return info
    
    def get_upgrade_requirements(self, current_stage: CompanyStage) -> str:
        """获取下一阶段升级要求"""
        stage_order = [
            CompanyStage.STARTUP, CompanyStage.GROWTH, CompanyStage.MATURE,
            CompanyStage.EXPANSION, CompanyStage.CORPORATE
        ]
        
        if current_stage == CompanyStage.CORPORATE:
            return "🏆 已达到最高发展阶段，无需升级"
        
        current_index = stage_order.index(current_stage)
        next_stage = stage_order[current_index + 1]
        
        requirements = self.stage_requirements[next_stage]
        features = self.stage_features[next_stage]
        
        req_text = f"""
📈 升级到 {features.name} 的要求

💰 财务要求:
  • 营业收入: ≥ J${requirements.min_revenue:,.0f}
  • 债务率: ≤ {requirements.max_debt_ratio*100:.0f}%

👥 规模要求:
  • 员工数量: ≥ {requirements.min_employees:,}人
  • 市场份额: ≥ {requirements.min_market_share*100:.2f}%

📊 表现要求:
  • 表现评分: ≥ {requirements.min_performance_score}分
  • 成立时间: ≥ {requirements.min_age_days}天

🎯 特殊条件:
"""
        
        if requirements.special_conditions:
            for condition in requirements.special_conditions:
                req_text += f"  • {condition}\n"
        else:
            req_text += "  • 无特殊条件\n"
        
        req_text += f"""
🎁 升级后获得:
  • {features.description}
  • 解锁新的运营能力
  • 获得阶段升级奖励
  • 降低经营风险
"""
        
        return req_text
    
    def get_all_stages_overview(self) -> str:
        """获取所有阶段概览"""
        overview = """
🏢 JC企业发展阶段体系

════════════════════════════════════════════════════════════════════════════════════════
"""
        
        stage_order = [
            CompanyStage.STARTUP, CompanyStage.GROWTH, CompanyStage.MATURE,
            CompanyStage.EXPANSION, CompanyStage.CORPORATE
        ]
        
        for i, stage in enumerate(stage_order):
            features = self.stage_features[stage]
            
            if stage in self.stage_requirements:
                requirements = self.stage_requirements[stage]
                revenue_req = f"J${requirements.min_revenue:,.0f}"
                employee_req = f"{requirements.min_employees:,}人"
            else:
                revenue_req = "初始阶段"
                employee_req = "不限"
            
            overview += f"""
📊 阶段{i+1}: {features.name}
  • 描述: {features.description}
  • 营收要求: {revenue_req}
  • 员工要求: {employee_req}
  • 营收倍数: {features.revenue_multiplier}x
  • 可用操作: {len(features.available_operations)}种
  • 特殊能力: {len(features.special_abilities)}项
"""
            
            if i < len(stage_order) - 1:
                overview += "  ↓\n"
        
        overview += """
════════════════════════════════════════════════════════════════════════════════════════

💡 发展建议:
  • 每个阶段都有独特的发展机会和挑战
  • 稳步提升各项指标，避免冒进
  • 关注特殊条件的达成
  • 及时升级获得更强能力
"""
        
        return overview 