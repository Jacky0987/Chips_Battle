"""
JC公司系统 - 公司类型定义
定义各种公司类型、行业分类和基础数据结构
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Optional
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
            
        if self.metrics.employees < 200:
            return False, "员工数量不足200人"
            
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
  市盈率: {pe_ratio:.1f}倍 (如果pe_ratio is not None else 'N/A')
  市净率: {pb_ratio:.1f}倍 (如果pb_ratio is not None else 'N/A')
  
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