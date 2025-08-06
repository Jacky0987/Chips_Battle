"""
JC公司系统 - 公司类型定义
定义各种公司类型、行业分类和基础数据结构
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import random


class CompanyType(Enum):
    """公司类型"""
    STARTUP = "startup"          # 初创公司
    PRIVATE = "private"          # 私人公司  
    PUBLIC = "public"           # 上市公司
    STATE_OWNED = "state_owned" # 国有企业
    FOREIGN = "foreign"         # 外资企业


class IndustryCategory(Enum):
    """行业分类"""
    TECHNOLOGY = "technology"           # 科技
    FINANCE = "finance"                # 金融
    HEALTHCARE = "healthcare"          # 医疗
    ENERGY = "energy"                 # 能源
    MANUFACTURING = "manufacturing"    # 制造业
    RETAIL = "retail"                 # 零售
    REAL_ESTATE = "real_estate"       # 房地产
    TRANSPORTATION = "transportation"  # 交通运输
    TELECOMMUNICATIONS = "telecom"     # 电信
    UTILITIES = "utilities"           # 公用事业
    CONSUMER_GOODS = "consumer_goods" # 消费品
    AGRICULTURE = "agriculture"       # 农业


class CompanyStage(Enum):
    """公司发展阶段"""
    SEED = "seed"                # 种子期
    STARTUP = "startup"          # 初创期
    GROWTH = "growth"            # 成长期
    MATURE = "mature"            # 成熟期
    DECLINING = "declining"      # 衰退期


@dataclass
class BusinessMetrics:
    """经营指标"""
    revenue: float = 0.0              # 营业收入
    profit: float = 0.0               # 净利润
    assets: float = 0.0               # 总资产
    liabilities: float = 0.0          # 总负债
    employees: int = 0                # 员工数量
    market_share: float = 0.0         # 市场份额
    growth_rate: float = 0.0          # 增长率
    debt_ratio: float = 0.0           # 负债率
    
    def calculate_equity(self):
        """计算净资产"""
        return self.assets - self.liabilities
        
    def calculate_roe(self):
        """计算净资产收益率"""
        equity = self.calculate_equity()
        return self.profit / equity if equity > 0 else 0.0
        
    def calculate_roa(self):
        """计算总资产收益率"""
        return self.profit / self.assets if self.assets > 0 else 0.0


@dataclass
class CompanyFinancials:
    """公司财务数据"""
    quarterly_reports: List[Dict] = field(default_factory=list)
    annual_reports: List[Dict] = field(default_factory=list)
    cash_flow: Dict = field(default_factory=dict)
    balance_sheet: Dict = field(default_factory=dict)
    income_statement: Dict = field(default_factory=dict)
    
    def add_quarterly_report(self, quarter, year, metrics: BusinessMetrics):
        """添加季度报告"""
        report = {
            'quarter': quarter,
            'year': year,
            'date': datetime.now().isoformat(),
            'metrics': {
                'revenue': metrics.revenue,
                'profit': metrics.profit,
                'assets': metrics.assets,
                'liabilities': metrics.liabilities,
                'employees': metrics.employees,
                'market_share': metrics.market_share,
                'growth_rate': metrics.growth_rate
            }
        }
        self.quarterly_reports.append(report)
        
        # 保持最近8个季度的数据
        if len(self.quarterly_reports) > 8:
            self.quarterly_reports = self.quarterly_reports[-8:]


@dataclass
class CompanyNews:
    """公司新闻事件"""
    news_id: str
    title: str
    content: str
    impact_type: str  # positive, negative, neutral
    impact_magnitude: float  # 0.0-1.0
    publish_date: str
    category: str  # earnings, product, management, legal, market


@dataclass
class JCCompany:
    """JC公司实体"""
    company_id: str
    name: str
    symbol: str  # 股票代码
    industry: IndustryCategory
    company_type: CompanyType
    stage: CompanyStage
    
    # 基础信息
    founded_date: str
    description: str
    headquarters: str
    website: str
    ceo_name: str
    
    # 经营数据
    metrics: BusinessMetrics
    financials: CompanyFinancials
    
    # 🆕 公司独立账户系统
    company_cash: float = 0.0  # 公司现金账户
    total_investment: float = 0.0  # 累计投资额
    
    # 🆕 员工管理系统  
    staff_list: List[Dict] = field(default_factory=list)  # 员工列表
    max_staff: int = 10000  # 最大员工数
    
    # 股票相关
    is_public: bool = False
    stock_price: float = 0.0
    shares_outstanding: int = 0
    market_cap: float = 0.0
    ipo_price: Optional[float] = None
    ipo_date: Optional[str] = None
    
    # 动态数据
    news_events: List[CompanyNews] = field(default_factory=list)
    performance_score: float = 50.0  # 0-100
    risk_level: int = 3  # 1-5, 1最低风险
    
    # 游戏相关
    created_by_user: Optional[str] = None
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """初始化后处理"""
        if self.is_public and self.shares_outstanding > 0:
            self.market_cap = self.stock_price * self.shares_outstanding
            
    def invest_capital(self, amount: float) -> Tuple[bool, str]:
        """向公司注资"""
        if amount <= 0:
            return False, "❌ 注资金额必须大于0"
            
        self.company_cash += amount
        self.total_investment += amount
        self.metrics.assets += amount
        
        # 更新最后修改时间
        self.last_updated = datetime.now().isoformat()
        
        return True, f"✅ 成功向公司注资 J${amount:,.0f}，公司账户余额: J${self.company_cash:,.0f}"
    
    def get_hire_candidates(self, position: str) -> List[Dict]:
        """获取招聘候选人列表"""
        candidates = []
        
        # 基础薪资根据职位确定
        position_salary_ranges = {
            '实习生': (3000, 6000),
            '助理': (6000, 10000),
            '工程师': (10000, 20000),
            '高级工程师': (18000, 35000),
            '经理': (25000, 45000),
            '总监': (40000, 80000),
            '副总': (60000, 120000),
        }
        
        base_min, base_max = position_salary_ranges.get(position, (8000, 15000))
        
        # 生成3-4个候选人
        for i in range(random.randint(3, 4)):
            # 随机生成候选人属性
            performance = random.uniform(60, 95)
            experience = random.randint(1, 12)
            leadership = random.uniform(50, 90) if position in ['经理', '总监', '副总'] else random.uniform(30, 70)
            innovation = random.uniform(40, 90)
            
            # 根据能力调整薪资
            ability_factor = (performance + experience * 5 + leadership + innovation) / 350
            salary = int(base_min + (base_max - base_min) * ability_factor)
            
            # 生成姓名
            surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
            given_names = ['志强', '志明', '志华', '志刚', '志伟', '志军', '志敏', '志勇', '志峰', '志龙', '思雨', '雨萱', '雨欣', '思琪', '思瑶', '思涵', '思颖', '思慧', '思婷', '思蓝']
            name = random.choice(surnames) + random.choice(given_names)
            
            # 特殊技能
            special_skills = []
            if performance > 85:
                special_skills.append('执行力强')
            if experience > 8:
                special_skills.append('经验丰富')
            if leadership > 75:
                special_skills.append('领导能力')
            if innovation > 80:
                special_skills.append('创新思维')
            if random.random() < 0.3:
                special_skills.append(random.choice(['多语言能力', '项目管理', '数据分析', '团队协作', '客户关系']))
            
            # 潜在风险
            risks = []
            if performance < 70:
                risks.append('表现波动')
            if experience < 3:
                risks.append('经验不足')
            if random.random() < 0.15:
                risks.append(random.choice(['职业稳定性', '薪资期望高', '学习能力一般']))
            
            candidates.append({
                'id': i + 1,
                'name': name,
                'position': position,
                'salary': salary,
                'performance': performance,
                'experience': experience,
                'leadership': leadership,
                'innovation': innovation,
                'special_skills': special_skills,
                'risks': risks,
                'total_score': performance + experience * 3 + leadership * 0.7 + innovation * 0.8
            })
        
        # 按总分排序
        candidates.sort(key=lambda x: x['total_score'], reverse=True)
        return candidates
    
    def hire_staff_from_candidates(self, candidate: Dict) -> Tuple[bool, str]:
        """从候选人中招聘员工"""
        if len(self.staff_list) >= self.max_staff:
            return False, f"❌ 员工数量已达上限 ({self.max_staff}人)"
        
        # 检查公司账户余额（至少支付3个月工资）
        required_cash = candidate['salary'] * 3
        if self.company_cash < required_cash:
            return False, f"❌ 公司账户余额不足，需要至少 J${required_cash:,.0f} 支付3个月薪资"
        
        # 添加员工 - 使用安全的ID生成
        next_id = max([staff['id'] for staff in self.staff_list], default=0) + 1
        new_staff = {
            'id': next_id,
            'name': candidate['name'],
            'position': candidate['position'],
            'salary': candidate['salary'],
            'hire_date': datetime.now().isoformat(),
            'performance': candidate['performance'],
            'experience': candidate['experience'],
            'leadership': candidate['leadership'],
            'innovation': candidate['innovation'],
            'special_skills': candidate['special_skills'],
            'total_score': candidate['total_score']
        }
        
        self.staff_list.append(new_staff)
        self.metrics.employees = len(self.staff_list)  # 🔧 修复：同步更新metrics中的员工数
        
        # 扣除预付薪资
        self.company_cash -= required_cash
        
        # 根据员工能力给公司带来额外效益
        if candidate['performance'] > 85:
            efficiency_bonus = random.uniform(0.01, 0.03)
            self.metrics.profit *= (1 + efficiency_bonus)
            bonus_msg = f"\n🌟 优秀员工为公司带来 {efficiency_bonus*100:.1f}% 的效率提升！"
        else:
            bonus_msg = ""
        
        skills_msg = f"\n💼 特殊技能: {', '.join(candidate['special_skills'])}" if candidate['special_skills'] else ""
        
        return True, f"✅ 成功招聘 {candidate['name']} 为 {candidate['position']}，月薪 J${candidate['salary']:,.0f}{skills_msg}{bonus_msg}"
    
    def hire_staff(self, staff_name: str, position: str, salary: float) -> Tuple[bool, str]:
        """简单招聘员工（向后兼容）"""
        if len(self.staff_list) >= self.max_staff:
            return False, f"❌ 员工数量已达上限 ({self.max_staff}人)"
            
        # 检查公司账户余额（至少支付3个月工资）
        required_cash = salary * 3
        if self.company_cash < required_cash:
            return False, f"❌ 公司账户余额不足，需要至少 J${required_cash:,.0f} 支付3个月薪资"
            
        # 添加员工 - 使用安全的ID生成
        next_id = max([staff['id'] for staff in self.staff_list], default=0) + 1
        new_staff = {
            'id': next_id,
            'name': staff_name,
            'position': position,
            'salary': salary,
            'hire_date': datetime.now().isoformat(),
            'performance': random.uniform(70, 95),  # 初始表现分
            'experience': random.randint(1, 10),  # 工作经验年数
            'leadership': random.uniform(40, 80),
            'innovation': random.uniform(40, 80),
            'special_skills': [],
            'total_score': 0
        }
        
        self.staff_list.append(new_staff)
        self.metrics.employees = len(self.staff_list)  # 🔧 修复：同步更新metrics中的员工数
        
        # 扣除预付薪资
        self.company_cash -= required_cash
        
        return True, f"✅ 成功招聘 {staff_name} 为 {position}，月薪 J${salary:,.0f}"
    
    def get_company_account_info(self) -> str:
        """获取公司账户信息"""
        # 安全计算平均表现分
        avg_performance = sum(staff['performance'] for staff in self.staff_list) / len(self.staff_list) if self.staff_list else 0
        total_salary = sum(staff['salary'] for staff in self.staff_list)
        monthly_cash_flow = self.company_cash - total_salary
        
        # 安全计算可运营月数
        if total_salary > 0:
            operational_months = int(self.company_cash / total_salary)
        else:
            operational_months = "∞"
            
        return f"""
💼 公司账户信息 - {self.name}

💰 财务状况:
  公司现金: J${self.company_cash:,.0f}
  累计投资: J${self.total_investment:,.0f}
  总资产: J${self.metrics.assets:,.0f}
  净资产: J${self.metrics.calculate_equity():,.0f}
  负债: J${self.metrics.liabilities:,.0f}

👥 员工状况:
  员工总数: {len(self.staff_list)}/{self.max_staff}人
  每月薪资支出: J${total_salary:,.0f}
  平均表现分: {avg_performance:.1f}/100

📊 运营能力:
  月度现金流: J${monthly_cash_flow:,.0f}
  可运营月数: {operational_months}个月
"""
        
    def batch_expand_staff(self, expansion_budget: float, target_positions: Dict[str, int] = None) -> Tuple[bool, str]:
        """批量招聘扩张
        
        Args:
            expansion_budget: 扩张预算
            target_positions: 目标职位配置 {'职位': 人数}，如果为None则自动配置
        """
        if expansion_budget <= 0:
            return False, "❌ 扩张预算必须大于0"
            
        if self.company_cash < expansion_budget:
            return False, f"❌ 公司账户余额不足，需要 J${expansion_budget:,.0f}，当前余额: J${self.company_cash:,.0f}"
        
        # 🔧 修复：使用实际员工数量进行判断
        current_staff_count = len(self.staff_list)
        
        # 自动配置职位结构
        if not target_positions:
            # 根据公司实际员工规模自动分配职位
            if current_staff_count < 20:
                # 小公司：基础职位为主
                target_positions = {
                    '工程师': 2,
                    '助理': 1,
                    '实习生': 2
                }
            elif current_staff_count < 100:
                # 中型公司：增加管理层
                target_positions = {
                    '工程师': 3,
                    '高级工程师': 2,
                    '经理': 1,
                    '助理': 2,
                    '实习生': 2
                }
            else:
                # 大公司：完整层级
                target_positions = {
                    '高级工程师': 3,
                    '工程师': 4,
                    '经理': 2,
                    '总监': 1,
                    '助理': 3,
                    '实习生': 2
                }
        
        # 计算扩张成本
        total_new_staff = sum(target_positions.values())
        
        # 检查员工数量限制
        if current_staff_count + total_new_staff > self.max_staff:
            available_slots = self.max_staff - current_staff_count
            return False, f"❌ 员工数量将超过限制，当前: {current_staff_count}, 计划新增: {total_new_staff}, 上限: {self.max_staff}\n💡 可用名额: {available_slots}人"
        
        # 估算薪资成本（3个月预付）- 使用保守估算
        estimated_cost = 0
        position_salary_ranges = {
            '实习生': 4500,
            '助理': 8000,
            '工程师': 15000,
            '高级工程师': 26000,
            '经理': 35000,
            '总监': 60000,
            '副总': 90000,
        }
        
        for position, count in target_positions.items():
            # 使用稍高于基础薪资的估算，考虑能力加成
            base_salary = position_salary_ranges.get(position, 12000)
            estimated_salary = int(base_salary * 1.1)  # 预估10%能力加成
            estimated_cost += estimated_salary * count * 3  # 3个月预付
        
        if estimated_cost > expansion_budget:
            return False, f"❌ 预算不足，预计成本: J${estimated_cost:,.0f}，可用预算: J${expansion_budget:,.0f}\n💡 建议预算至少: J${estimated_cost:,.0f}"
        
        # 执行批量招聘
        hired_staff = []
        total_cost = 0
        
        for position, count in target_positions.items():
            for i in range(count):
                # 生成员工属性
                performance = random.uniform(65, 90)
                experience = random.randint(1, 8)
                leadership = random.uniform(40, 80)
                innovation = random.uniform(40, 85)
                
                # 薪资计算
                base_salary = position_salary_ranges.get(position, 12000)
                ability_factor = (performance + experience * 3) / 120
                salary = int(base_salary * (0.8 + 0.4 * ability_factor))
                
                # 生成姓名
                surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
                given_names = ['志强', '志明', '志华', '志刚', '志伟', '志军', '志敏', '志勇', '志峰', '志龙', '思雨', '雨萱', '雨欣', '思琪', '思瑶', '思涵']
                name = random.choice(surnames) + random.choice(given_names)
                
                # 添加员工 - 使用安全的ID生成
                next_id = max([staff['id'] for staff in self.staff_list], default=0) + len(hired_staff) + 1
                new_staff = {
                    'id': next_id,
                    'name': name,
                    'position': position,
                    'salary': salary,
                    'hire_date': datetime.now().isoformat(),
                    'performance': performance,
                    'experience': experience,
                    'leadership': leadership,
                    'innovation': innovation,
                    'special_skills': [],
                    'total_score': performance + experience * 3
                }
                
                hired_staff.append(new_staff)
                total_cost += salary * 3  # 3个月预付
        
        # 检查实际成本是否超出预算
        if total_cost > expansion_budget:
            return False, f"❌ 实际成本超出预算，需要: J${total_cost:,.0f}，预算: J${expansion_budget:,.0f}\n💡 建议预算: J${total_cost:,.0f}"
        
        # 更新公司数据
        self.staff_list.extend(hired_staff)
        self.metrics.employees = len(self.staff_list)  # 🔧 修复：同步更新metrics中的员工数
        self.company_cash -= total_cost
        
        # 扩张效益
        expansion_boost = min(0.15, total_new_staff * 0.01)  # 每个新员工贡献1%，最多15%
        self.metrics.revenue *= (1 + expansion_boost)
        self.metrics.assets += expansion_budget * 0.3  # 办公设备等固定资产
        
        # 生成报告
        position_summary = {}
        for staff in hired_staff:
            pos = staff['position']
            if pos not in position_summary:
                position_summary[pos] = {'count': 0, 'total_salary': 0}
            position_summary[pos]['count'] += 1
            position_summary[pos]['total_salary'] += staff['salary']
        
        summary_text = "\n📋 招聘详情:\n"
        for pos, data in position_summary.items():
            avg_salary = data['total_salary'] / data['count']
            summary_text += f"  • {pos}: {data['count']}人，平均薪资 J${avg_salary:,.0f}\n"
        
        return True, f"""✅ 批量扩张成功！

💼 扩张概况:
  新增员工: {total_new_staff}人
  总成本: J${total_cost:,.0f}
  营收提升: +{expansion_boost*100:.1f}%
  员工总数: {len(self.staff_list)}人

{summary_text}
💰 财务状况:
  剩余预算: J${expansion_budget - total_cost:,.0f}
  公司余额: J${self.company_cash:,.0f}
  月薪支出: J${sum(staff['salary'] for staff in self.staff_list):,.0f}
"""
        
    def batch_expand_by_amount(self, staff_amount: int) -> Tuple[bool, str]:
        """按人数快速扩张
        
        Args:
            staff_amount: 目标新增员工数量（单次扩张限制：1-50人）
            
        Note:
            - 单次扩张最多50人，但公司总员工数可达到max_staff上限
            - 系统会根据公司规模智能配置职位结构
            - 需要提前支付3个月薪资作为预付款
        """
        if staff_amount <= 0 or staff_amount > 50:
            return False, "❌ 单次扩张数量必须在1-50人之间"
        
        # 🔧 修复：使用实际员工数量进行判断
        current_staff_count = len(self.staff_list)
        
        # 检查员工数量限制
        if current_staff_count + staff_amount > self.max_staff:
            available_slots = self.max_staff - current_staff_count
            return False, f"❌ 员工数量将超过限制，当前: {current_staff_count}, 计划新增: {staff_amount}, 上限: {self.max_staff}\n💡 可用名额: {available_slots}人"
        
        # 根据公司规模和目标人数智能配置职位结构
        target_positions = self._calculate_position_distribution(current_staff_count, staff_amount)
        
        # 计算预计成本
        position_salary_ranges = {
            '实习生': 4500,
            '助理': 8000,
            '工程师': 15000,
            '高级工程师': 26000,
            '经理': 35000,
            '总监': 60000,
            '副总': 90000,
        }
        
        estimated_cost = 0
        for position, count in target_positions.items():
            base_salary = position_salary_ranges.get(position, 12000)
            estimated_salary = int(base_salary * 1.1)  # 预估10%能力加成
            estimated_cost += estimated_salary * count * 3  # 3个月预付
        
        # 检查公司账户余额
        if self.company_cash < estimated_cost:
            return False, f"❌ 公司账户余额不足，预计成本: J${estimated_cost:,.0f}，当前余额: J${self.company_cash:,.0f}\n💡 建议先注资至少: J${estimated_cost - self.company_cash:,.0f}"
        
        # 执行批量招聘
        hired_staff = []
        total_cost = 0
        
        for position, count in target_positions.items():
            for i in range(count):
                # 生成员工属性
                performance = random.uniform(65, 90)
                experience = random.randint(1, 8)
                leadership = random.uniform(40, 80)
                innovation = random.uniform(40, 85)
                
                # 薪资计算
                base_salary = position_salary_ranges.get(position, 12000)
                ability_factor = (performance + experience * 3) / 120
                salary = int(base_salary * (0.8 + 0.4 * ability_factor))
                
                # 生成姓名
                surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴', '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
                given_names = ['志强', '志明', '志华', '志刚', '志伟', '志军', '志敏', '志勇', '志峰', '志龙', '思雨', '雨萱', '雨欣', '思琪', '思瑶', '思涵']
                name = random.choice(surnames) + random.choice(given_names)
                
                # 添加员工 - 使用安全的ID生成
                next_id = max([staff['id'] for staff in self.staff_list], default=0) + len(hired_staff) + 1
                new_staff = {
                    'id': next_id,
                    'name': name,
                    'position': position,
                    'salary': salary,
                    'hire_date': datetime.now().isoformat(),
                    'performance': performance,
                    'experience': experience,
                    'leadership': leadership,
                    'innovation': innovation,
                    'special_skills': [],
                    'total_score': performance + experience * 3
                }
                
                hired_staff.append(new_staff)
                total_cost += salary * 3  # 3个月预付
        
        # 更新公司数据
        self.staff_list.extend(hired_staff)
        self.metrics.employees = len(self.staff_list)  # 🔧 修复：同步更新metrics中的员工数
        self.company_cash -= total_cost
        
        # 扩张效益
        expansion_boost = min(0.12, staff_amount * 0.008)  # 每个新员工贡献0.8%，最多12%
        self.metrics.revenue *= (1 + expansion_boost)
        self.metrics.assets += total_cost * 0.2  # 办公设备等固定资产
        
        # 生成报告
        position_summary = {}
        for staff in hired_staff:
            pos = staff['position']
            if pos not in position_summary:
                position_summary[pos] = {'count': 0, 'total_salary': 0}
            position_summary[pos]['count'] += 1
            position_summary[pos]['total_salary'] += staff['salary']
        
        summary_text = "\n📋 招聘详情:\n"
        for pos, data in position_summary.items():
            avg_salary = data['total_salary'] / data['count']
            summary_text += f"  • {pos}: {data['count']}人，平均薪资 J${avg_salary:,.0f}\n"
        
        return True, f"""✅ 快速扩张成功！

👥 扩张概况:
  目标员工: {staff_amount}人
  实际招聘: {len(hired_staff)}人
  总成本: J${total_cost:,.0f}
  营收提升: +{expansion_boost*100:.1f}%
  员工总数: {len(self.staff_list)}人

{summary_text}
💰 财务状况:
  公司余额: J${self.company_cash:,.0f}
  月薪支出: J${sum(staff['salary'] for staff in self.staff_list):,.0f}
  
💡 提示: 快速扩张模式已根据公司规模自动配置最优职位结构
"""

    def _calculate_position_distribution(self, current_count: int, target_amount: int) -> Dict[str, int]:
        """计算职位分配
        
        Args:
            current_count: 当前员工数
            target_amount: 目标新增员工数
        
        Returns:
            Dict: 职位分配 {'职位': 人数}
        """
        total_after_expansion = current_count + target_amount
        
        # 根据扩张后的总规模决定职位结构
        if total_after_expansion <= 20:
            # 小公司：基础岗位为主
            base_ratio = {
                '实习生': 0.3,      # 30%
                '助理': 0.2,        # 20%
                '工程师': 0.5       # 50%
            }
        elif total_after_expansion <= 50:
            # 小中型公司：增加一些高级岗位
            base_ratio = {
                '实习生': 0.25,         # 25%
                '助理': 0.2,            # 20%
                '工程师': 0.4,          # 40%
                '高级工程师': 0.1,      # 10%
                '经理': 0.05            # 5%
            }
        elif total_after_expansion <= 100:
            # 中型公司：更完整的层级
            base_ratio = {
                '实习生': 0.2,          # 20%
                '助理': 0.15,           # 15%
                '工程师': 0.35,         # 35%
                '高级工程师': 0.2,      # 20%
                '经理': 0.08,           # 8%
                '总监': 0.02            # 2%
            }
        else:
            # 大公司：完整管理结构
            base_ratio = {
                '实习生': 0.15,         # 15%
                '助理': 0.15,           # 15%
                '工程师': 0.3,          # 30%
                '高级工程师': 0.25,     # 25%
                '经理': 0.1,            # 10%
                '总监': 0.04,           # 4%
                '副总': 0.01            # 1%
            }
        
        # 分配具体人数
        positions = {}
        remaining = target_amount
        
        # 按比例分配
        position_list = list(base_ratio.keys())
        for i, (position, ratio) in enumerate(base_ratio.items()):
            if i == len(position_list) - 1:  # 最后一个职位获得剩余所有名额
                count = remaining
            else:
                count = max(1, int(target_amount * ratio))
                count = min(count, remaining)  # 不能超过剩余名额
            
            if count > 0:
                positions[position] = count
                remaining -= count
            
            if remaining <= 0:
                break
        
        # 确保至少有一些基础员工
        if not positions:
            positions = {'工程师': target_amount}
        
        return positions

    def pay_monthly_salaries(self) -> Tuple[bool, str]:
        """支付月度薪资"""
        if not self.staff_list:
            return True, "✅ 当前无员工需要支付薪资"
            
        total_salary = sum(staff['salary'] for staff in self.staff_list)
        
        if self.company_cash < total_salary:
            # 资金不足，需要解雇员工或注资
            return False, f"❌ 公司账户余额不足支付薪资 J${total_salary:,.0f}，当前余额: J${self.company_cash:,.0f}"
        
        self.company_cash -= total_salary
        
        # 更新员工表现（随机小幅波动）
        for staff in self.staff_list:
            staff['performance'] += random.uniform(-2, 3)
            staff['performance'] = max(10, min(100, staff['performance']))
            
        return True, f"✅ 成功支付月度薪资 J${total_salary:,.0f}，余额: J${self.company_cash:,.0f}"
        
    def update_stock_price(self, new_price: float):
        """更新股价"""
        if self.is_public:
            old_price = self.stock_price
            self.stock_price = new_price
            self.market_cap = new_price * self.shares_outstanding
            
            # 计算涨跌幅
            change_pct = (new_price - old_price) / old_price if old_price > 0 else 0
            return change_pct
        return 0.0
        
    def calculate_pe_ratio(self):
        """计算市盈率"""
        if self.is_public and self.metrics.profit > 0:
            eps = self.metrics.profit / self.shares_outstanding
            return self.stock_price / eps
        return None
        
    def calculate_pb_ratio(self):
        """计算市净率"""
        if self.is_public and self.metrics.calculate_equity() > 0:
            book_value_per_share = self.metrics.calculate_equity() / self.shares_outstanding
            return self.stock_price / book_value_per_share
        return None
        
    def can_go_public(self):
        """检查是否可以IPO"""
        if self.is_public:
            return False, "公司已上市"
            
        if self.stage == CompanyStage.SEED:
            return False, "公司处于种子期，需要更多发展"
            
        if self.metrics.revenue < 100000000:  # 1亿营收
            return False, "营收不足1亿，暂不满足上市条件"
            
        if self.metrics.profit <= 0:
            return False, "公司尚未盈利，暂不满足上市条件"
            
        # 🔧 修复：使用实际员工数量进行IPO检查
        actual_employees = len(self.staff_list)
        if actual_employees < 200:
            return False, f"员工数量不足200人，当前: {actual_employees}人"
            
        return True, "满足上市条件"
        
    def go_public(self, ipo_price: float, shares_to_issue: int):
        """公司上市"""
        can_ipo, reason = self.can_go_public()
        if not can_ipo:
            return False, reason
            
        self.is_public = True
        self.ipo_price = ipo_price
        self.ipo_date = datetime.now().isoformat()
        self.stock_price = ipo_price
        self.shares_outstanding = shares_to_issue
        self.market_cap = ipo_price * shares_to_issue
        self.company_type = CompanyType.PUBLIC
        
        # 增加现金(IPO募资)
        ipo_proceeds = ipo_price * shares_to_issue
        self.metrics.assets += ipo_proceeds
        
        return True, f"IPO成功，募资 J${ipo_proceeds:,.0f}"
        
    def generate_news_event(self, event_type: str = None):
        """生成新闻事件"""
        if not event_type:
            event_type = random.choice(['earnings', 'product', 'management', 'market'])
            
        news_templates = {
            'earnings': {
                'positive': [
                    f"{self.name}季度业绩超预期，净利润增长{random.randint(10, 50)}%",
                    f"{self.name}发布亮眼财报，营收创历史新高",
                    f"{self.name}盈利能力大幅提升，毛利率上升至{random.randint(25, 45)}%"
                ],
                'negative': [
                    f"{self.name}季度亏损扩大，同比下降{random.randint(10, 30)}%",
                    f"{self.name}业绩不及预期，营收下滑{random.randint(5, 20)}%",
                    f"{self.name}面临成本上升压力，利润率下降"
                ]
            },
            'product': {
                'positive': [
                    f"{self.name}发布革命性新产品，市场反响热烈",
                    f"{self.name}获得重大技术突破，申请多项专利",
                    f"{self.name}新产品预订量超预期，供不应求"
                ],
                'negative': [
                    f"{self.name}产品存在质量问题，启动召回程序",
                    f"{self.name}新品发布延期，研发遇到技术难题",
                    f"{self.name}面临激烈竞争，市场份额下降"
                ]
            },
            'management': {
                'positive': [
                    f"{self.name}任命新CEO，具有丰富行业经验",
                    f"{self.name}管理层增持股票，显示信心",
                    f"{self.name}获得知名投资机构战略投资"
                ],
                'negative': [
                    f"{self.name}CEO突然离职，公司治理引发关注",
                    f"{self.name}高管团队重组，经营策略面临调整",
                    f"{self.name}遭遇重要客户流失，业务承压"
                ]
            }
        }
        
        impact_type = random.choice(['positive', 'negative'])
        templates = news_templates.get(event_type, {}).get(impact_type, [])
        
        if templates:
            title = random.choice(templates)
            
            news = CompanyNews(
                news_id=f"{self.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=title,
                content=f"详细内容: {title}。这一消息对公司{self.industry.value}业务产生重要影响。",
                impact_type=impact_type,
                impact_magnitude=random.uniform(0.02, 0.15),
                publish_date=datetime.now().isoformat(),
                category=event_type
            )
            
            self.news_events.append(news)
            
            # 保持最近50条新闻
            if len(self.news_events) > 50:
                self.news_events = self.news_events[-50:]
                
            return news
        return None
        
    def update_performance_score(self):
        """更新公司表现评分"""
        score = 50.0  # 基础分
        
        # 盈利能力 (30%)
        if self.metrics.profit > 0:
            roe = self.metrics.calculate_roe()
            score += min(roe * 100, 15)  # ROE最多贡献15分
        else:
            score -= 10  # 亏损扣分
            
        # 成长性 (25%)
        growth_score = min(self.metrics.growth_rate * 25, 12.5)
        score += growth_score
        
        # 财务健康度 (20%)
        if self.metrics.debt_ratio < 0.3:
            score += 10
        elif self.metrics.debt_ratio < 0.6:
            score += 5
        else:
            score -= 5
            
        # 市场地位 (15%)
        market_score = self.metrics.market_share * 15
        score += market_score
        
        # 新闻影响 (10%)
        recent_news = [n for n in self.news_events if 
                      (datetime.now() - datetime.fromisoformat(n.publish_date)).days <= 30]
        for news in recent_news:
            if news.impact_type == 'positive':
                score += news.impact_magnitude * 5
            else:
                score -= news.impact_magnitude * 5
                
        self.performance_score = max(0, min(100, score))
        return self.performance_score
        
    def get_investment_rating(self):
        """获取投资评级"""
        score = self.performance_score
        
        if score >= 85:
            return "强烈买入", "A+"
        elif score >= 75:
            return "买入", "A"
        elif score >= 65:
            return "持有", "B+"
        elif score >= 55:
            return "中性", "B"
        elif score >= 45:
            return "谨慎", "B-"
        elif score >= 35:
            return "减持", "C"
        else:
            return "卖出", "D"
            
    def get_display_info(self):
        """获取显示信息"""
        rating, grade = self.get_investment_rating()
        
        info = f"""
🏢 {self.name} ({self.symbol})

📊 基本信息:
  行业分类: {self.industry.value.title()}
  公司类型: {self.company_type.value.title()}
  发展阶段: {self.stage.value.title()}
  成立时间: {self.founded_date}
  总部地址: {self.headquarters}
  首席执行官: {self.ceo_name}

💰 财务状况:
  营业收入: J${self.metrics.revenue:,.0f}
  净利润: J${self.metrics.profit:,.0f}
  总资产: J${self.metrics.assets:,.0f}
  净资产: J${self.metrics.calculate_equity():,.0f}
  员工数量: {self.metrics.employees:,}人
  
📈 经营指标:
  营收增长率: {self.metrics.growth_rate*100:+.1f}%
  净资产收益率: {self.metrics.calculate_roe()*100:.1f}%
  资产负债率: {self.metrics.debt_ratio*100:.1f}%
  市场份额: {self.metrics.market_share*100:.2f}%
"""

        if self.is_public:
            pe_ratio = self.calculate_pe_ratio()
            pb_ratio = self.calculate_pb_ratio()
            
            info += f"""
💹 股票信息:
  当前股价: J${self.stock_price:.2f}
  总股本: {self.shares_outstanding:,}股
  市值: J${self.market_cap:,.0f}
  IPO价格: J${self.ipo_price:.2f}
  市盈率: {pe_ratio:.1f if pe_ratio is not None else 'N/A'}倍
  市净率: {pb_ratio:.1f if pb_ratio is not None else 'N/A'}倍
  
📊 投资评级:
  综合评分: {self.performance_score:.1f}/100
  投资建议: {rating} ({grade})
  风险等级: {'⭐' * self.risk_level} ({self.risk_level}/5)
"""
        else:
            can_ipo, ipo_msg = self.can_go_public()
            info += f"""
🔒 未上市公司:
  IPO状态: {'✅ 可申请IPO' if can_ipo else '❌ ' + ipo_msg}
  预估价值: J${self.metrics.calculate_equity():,.0f}
"""

        # 显示最近新闻
        recent_news = sorted(self.news_events, key=lambda x: x.publish_date, reverse=True)[:3]
        if recent_news:
            info += "\n📰 最近新闻:\n"
            for news in recent_news:
                impact_icon = "📈" if news.impact_type == "positive" else "📉" if news.impact_type == "negative" else "📊"
                info += f"  {impact_icon} {news.title}\n"
                info += f"     {news.publish_date[:10]}\n"
                
        return info

    def fire_employee(self, employee_id: int) -> Tuple[bool, str]:
        """解雇员工"""
        # 查找员工
        employee_to_fire = None
        for i, staff in enumerate(self.staff_list):
            if staff['id'] == employee_id:
                employee_to_fire = staff
                break
        
        if not employee_to_fire:
            return False, f"❌ 未找到ID为{employee_id}的员工"
        
        # 计算遣散费（1-3个月薪资）
        severance_pay = employee_to_fire['salary'] * random.uniform(1, 3)
        
        # 检查公司账户余额
        if self.company_cash < severance_pay:
            return False, f"❌ 公司账户余额不足支付遣散费 J${severance_pay:,.0f}，当前余额: J${self.company_cash:,.0f}"
        
        # 执行解雇
        self.staff_list.remove(employee_to_fire)
        self.metrics.employees = len(self.staff_list)  # 同步更新员工数
        self.company_cash -= severance_pay
        
        return True, f"✅ 已解雇员工 {employee_to_fire['name']}（{employee_to_fire['position']}），支付遣散费 J${severance_pay:,.0f}"
    
    def trigger_natural_turnover(self) -> Tuple[int, str]:
        """自然离职（员工主动离职）"""
        if not self.staff_list:
            return 0, ""
        
        # 离职概率基于员工表现和公司状况
        base_turnover_rate = 0.05  # 基础5%月离职率
        
        # 公司表现差会增加离职率
        if self.performance_score < 40:
            base_turnover_rate += 0.1
        elif self.performance_score > 80:
            base_turnover_rate -= 0.02
        
        # 薪资压力影响
        total_monthly_salary = sum(staff['salary'] for staff in self.staff_list)
        if self.company_cash < total_monthly_salary * 2:  # 少于2个月薪资储备
            base_turnover_rate += 0.15
        
        # 计算实际离职人数
        departing_employees = []
        for staff in self.staff_list[:]:  # 使用切片避免修改列表时的问题
            # 表现差的员工更容易离职
            individual_rate = base_turnover_rate
            if staff['performance'] < 60:
                individual_rate += 0.1
            elif staff['performance'] > 90:
                individual_rate -= 0.05
            
            if random.random() < individual_rate:
                departing_employees.append(staff)
        
        # 执行离职
        departing_count = len(departing_employees)
        if departing_count > 0:
            for staff in departing_employees:
                self.staff_list.remove(staff)
            
            self.metrics.employees = len(self.staff_list)  # 同步更新员工数
            
            # 离职潮对公司的负面影响
            if departing_count > len(self.staff_list) * 0.2:  # 超过20%离职
                productivity_loss = random.uniform(0.05, 0.15)
                self.metrics.profit *= (1 - productivity_loss)
                
                return departing_count, f"⚠️ 发生离职潮！{departing_count}名员工离职，影响生产力 -{productivity_loss*100:.1f}%"
            else:
                return departing_count, f"📤 {departing_count}名员工离职"
        
        return 0, ""


def create_sample_companies():
    """创建示例公司"""
    companies = []
    
    # 科技公司
    tech_company = JCCompany(
        company_id="JC_TECH_001",
        name="JackyCoin科技",
        symbol="JCTECH",
        industry=IndustryCategory.TECHNOLOGY,
        company_type=CompanyType.PRIVATE,
        stage=CompanyStage.GROWTH,
        founded_date="2020-01-15",
        description="专注于金融科技和区块链技术的创新公司",
        headquarters="深圳市南山区",
        website="www.jackytech.com",
        ceo_name="张志强",
        metrics=BusinessMetrics(
            revenue=150000000,
            profit=25000000,
            assets=300000000,
            liabilities=100000000,
            employees=350,
            market_share=0.05,
            growth_rate=0.35,
            debt_ratio=0.33
        ),
        financials=CompanyFinancials(),
        performance_score=78.5,
        risk_level=3
    )
    companies.append(tech_company)
    
    # 制造业公司
    mfg_company = JCCompany(
        company_id="JC_MFG_001", 
        name="捷诚制造",
        symbol="JCMFG",
        industry=IndustryCategory.MANUFACTURING,
        company_type=CompanyType.PUBLIC,
        stage=CompanyStage.MATURE,
        founded_date="2015-03-20",
        description="专业的精密制造和自动化设备供应商",
        headquarters="苏州工业园区",
        website="www.jcmfg.com",
        ceo_name="李明华",
        metrics=BusinessMetrics(
            revenue=800000000,
            profit=80000000,
            assets=1200000000,
            liabilities=400000000,
            employees=1500,
            market_share=0.12,
            growth_rate=0.15,
            debt_ratio=0.33
        ),
        financials=CompanyFinancials(),
        is_public=True,
        stock_price=45.60,
        shares_outstanding=100000000,
        ipo_price=25.00,
        ipo_date="2022-06-15",
        performance_score=72.3,
        risk_level=2
    )
    companies.append(mfg_company)
    
    return companies 