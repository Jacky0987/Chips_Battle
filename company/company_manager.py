"""
JC公司管理器 - 统一管理所有公司相关业务
包括公司创建、管理、IPO、股票交易等
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from .company_types import JCCompany, CompanyType, IndustryCategory, CompanyStage, BusinessMetrics, create_sample_companies


class CompanyManager:
    """公司管理器"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.companies: Dict[str, JCCompany] = {}  # {company_id: JCCompany}
        self.stock_symbols: Dict[str, str] = {}    # {symbol: company_id}
        self.user_companies: Dict[str, List[str]] = {}  # {user_id: [company_ids]}
        self.load_companies()
        
    def load_companies(self):
        """加载公司数据"""
        try:
            if os.path.exists('data/jc_companies.json'):
                with open('data/jc_companies.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # 重建公司对象
                for company_data in data.get('companies', []):
                    company = self._dict_to_company(company_data)
                    self.companies[company.company_id] = company
                    if company.is_public and company.symbol:
                        self.stock_symbols[company.symbol] = company.company_id
                        
                self.user_companies = data.get('user_companies', {})
                        
            else:
                # 创建示例公司
                sample_companies = create_sample_companies()
                for company in sample_companies:
                    self.companies[company.company_id] = company
                    if company.is_public and company.symbol:
                        self.stock_symbols[company.symbol] = company.company_id
                self.save_companies()
                
        except Exception as e:
            print(f"加载公司数据失败: {e}")
            
    def save_companies(self):
        """保存公司数据"""
        try:
            os.makedirs('data', exist_ok=True)
            
            data = {
                'companies': [self._company_to_dict(company) for company in self.companies.values()],
                'user_companies': self.user_companies,
                'last_updated': datetime.now().isoformat()
            }
            
            with open('data/jc_companies.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存公司数据失败: {e}")
            
    def _company_to_dict(self, company: JCCompany) -> Dict:
        """将公司对象转换为字典"""
        return {
            'company_id': company.company_id,
            'name': company.name,
            'symbol': company.symbol,
            'industry': company.industry.value,
            'company_type': company.company_type.value,
            'stage': company.stage.value,
            'founded_date': company.founded_date,
            'description': company.description,
            'headquarters': company.headquarters,
            'website': company.website,
            'ceo_name': company.ceo_name,
            'metrics': {
                'revenue': company.metrics.revenue,
                'profit': company.metrics.profit,
                'assets': company.metrics.assets,
                'liabilities': company.metrics.liabilities,
                'employees': company.metrics.employees,
                'market_share': company.metrics.market_share,
                'growth_rate': company.metrics.growth_rate,
                'debt_ratio': company.metrics.debt_ratio
            },
            'financials': {
                'quarterly_reports': company.financials.quarterly_reports,
                'annual_reports': company.financials.annual_reports,
                'cash_flow': company.financials.cash_flow,
                'balance_sheet': company.financials.balance_sheet,
                'income_statement': company.financials.income_statement
            },
            'is_public': company.is_public,
            'stock_price': company.stock_price,
            'shares_outstanding': company.shares_outstanding,
            'market_cap': company.market_cap,
            'ipo_price': company.ipo_price,
            'ipo_date': company.ipo_date,
            'news_events': [
                {
                    'news_id': news.news_id,
                    'title': news.title,
                    'content': news.content,
                    'impact_type': news.impact_type,
                    'impact_magnitude': news.impact_magnitude,
                    'publish_date': news.publish_date,
                    'category': news.category
                }
                for news in company.news_events
            ],
            'performance_score': company.performance_score,
            'risk_level': company.risk_level,
            'created_by_user': company.created_by_user,
            'last_updated': company.last_updated
        }
        
    def _dict_to_company(self, data: Dict) -> JCCompany:
        """将字典转换为公司对象"""
        from .company_types import CompanyNews, CompanyFinancials, BusinessMetrics
        
        # 重建业务指标
        metrics_data = data['metrics']
        metrics = BusinessMetrics(
            revenue=metrics_data['revenue'],
            profit=metrics_data['profit'],
            assets=metrics_data['assets'],
            liabilities=metrics_data['liabilities'],
            employees=metrics_data['employees'],
            market_share=metrics_data['market_share'],
            growth_rate=metrics_data['growth_rate'],
            debt_ratio=metrics_data['debt_ratio']
        )
        
        # 重建财务数据
        financials_data = data['financials']
        financials = CompanyFinancials(
            quarterly_reports=financials_data.get('quarterly_reports', []),
            annual_reports=financials_data.get('annual_reports', []),
            cash_flow=financials_data.get('cash_flow', {}),
            balance_sheet=financials_data.get('balance_sheet', {}),
            income_statement=financials_data.get('income_statement', {})
        )
        
        # 重建新闻事件
        news_events = []
        for news_data in data.get('news_events', []):
            news = CompanyNews(
                news_id=news_data['news_id'],
                title=news_data['title'],
                content=news_data['content'],
                impact_type=news_data['impact_type'],
                impact_magnitude=news_data['impact_magnitude'],
                publish_date=news_data['publish_date'],
                category=news_data['category']
            )
            news_events.append(news)
            
        # 创建公司对象
        company = JCCompany(
            company_id=data['company_id'],
            name=data['name'],
            symbol=data['symbol'],
            industry=IndustryCategory(data['industry']),
            company_type=CompanyType(data['company_type']),
            stage=CompanyStage(data['stage']),
            founded_date=data['founded_date'],
            description=data['description'],
            headquarters=data['headquarters'],
            website=data['website'],
            ceo_name=data['ceo_name'],
            metrics=metrics,
            financials=financials,
            is_public=data['is_public'],
            stock_price=data['stock_price'],
            shares_outstanding=data['shares_outstanding'],
            market_cap=data['market_cap'],
            ipo_price=data.get('ipo_price'),
            ipo_date=data.get('ipo_date'),
            news_events=news_events,
            performance_score=data['performance_score'],
            risk_level=data['risk_level'],
            created_by_user=data.get('created_by_user'),
            last_updated=data['last_updated']
        )
        
        return company
        
    def create_company(self, user_id: str, company_name: str, industry: str, description: str = "") -> Tuple[bool, str]:
        """创建新公司"""
        if not company_name or len(company_name) < 2:
            return False, "公司名称至少需要2个字符"
            
        # 检查名称是否重复
        for company in self.companies.values():
            if company.name == company_name:
                return False, "公司名称已存在"
                
        # 验证行业
        try:
            industry_enum = IndustryCategory(industry.lower())
        except ValueError:
            return False, f"无效的行业分类: {industry}"
            
        # 生成公司ID和股票代码
        company_id = f"JC_{industry.upper()[:3]}_{len(self.companies) + 1:03d}"
        symbol = self._generate_symbol(company_name)
        
        # 检查股票代码重复
        if symbol in self.stock_symbols:
            symbol = f"{symbol}{random.randint(10, 99)}"
            
        # 创建初始业务指标
        initial_metrics = BusinessMetrics(
            revenue=random.randint(1000000, 10000000),  # 100万-1000万初始营收
            profit=random.randint(-500000, 2000000),    # 可能亏损或小幅盈利
            assets=random.randint(5000000, 50000000),   # 500万-5000万资产
            liabilities=random.randint(1000000, 20000000), # 负债
            employees=random.randint(10, 200),          # 10-200员工
            market_share=random.uniform(0.001, 0.01),   # 0.1%-1%市场份额
            growth_rate=random.uniform(-0.1, 0.5),      # -10%到50%增长率
            debt_ratio=random.uniform(0.2, 0.7)         # 20%-70%负债率
        )
        
        # 创建公司
        company = JCCompany(
            company_id=company_id,
            name=company_name,
            symbol=symbol,
            industry=industry_enum,
            company_type=CompanyType.STARTUP,
            stage=CompanyStage.STARTUP,
            founded_date=datetime.now().strftime("%Y-%m-%d"),
            description=description or f"一家专注于{industry_enum.value}领域的创新企业",
            headquarters="JC经济特区",
            website=f"www.{symbol.lower()}.jc",
            ceo_name=f"CEO_{random.randint(1000, 9999)}",  # 可以后续修改
            metrics=initial_metrics,
            financials=CompanyFinancials(),
            created_by_user=user_id,
            performance_score=random.uniform(40, 60),
            risk_level=random.randint(3, 4)  # 初创公司风险较高
        )
        
        # 保存公司
        self.companies[company_id] = company
        
        # 记录用户创建的公司
        if user_id not in self.user_companies:
            self.user_companies[user_id] = []
        self.user_companies[user_id].append(company_id)
        
        self.save_companies()
        
        return True, f"✅ 公司 '{company_name}' 创建成功！\n公司ID: {company_id}\n股票代码: {symbol}"
        
    def _generate_symbol(self, company_name: str) -> str:
        """生成股票代码"""
        # 提取中文首字母或英文首字母
        import re
        
        # 移除特殊字符
        clean_name = re.sub(r'[^\w\u4e00-\u9fff]', '', company_name)
        
        if len(clean_name) >= 4:
            symbol = clean_name[:4].upper()
        elif len(clean_name) >= 2:
            symbol = clean_name[:2].upper() + "JC"
        else:
            symbol = f"JC{random.randint(100, 999)}"
            
        return symbol
        
    def apply_ipo(self, company_id: str, ipo_price: float, shares_to_issue: int) -> Tuple[bool, str]:
        """申请IPO"""
        company = self.companies.get(company_id)
        if not company:
            return False, "公司不存在"
            
        # 检查IPO条件
        can_ipo, reason = company.can_go_public()
        if not can_ipo:
            return False, f"IPO申请被拒: {reason}"
            
        if ipo_price <= 0 or shares_to_issue <= 0:
            return False, "IPO价格和发行股数必须大于0"
            
        # 执行IPO
        success, result = company.go_public(ipo_price, shares_to_issue)
        if success:
            # 将公司股票添加到市场数据
            self.stock_symbols[company.symbol] = company_id
            self._add_to_market_data(company)
            self.save_companies()
            
        return success, result
        
    def _add_to_market_data(self, company: JCCompany):
        """将公司股票添加到市场数据"""
        if not company.is_public:
            return
            
        # 添加到主应用的股票数据中
        stock_data = {
            'name': company.name,
            'price': company.stock_price,
            'change': 0.0,
            'sector': company.industry.value.title(),
            'volatility': 0.02 + company.risk_level * 0.005,  # 风险越高波动越大
            'market_cap': company.market_cap,
            'pe_ratio': company.calculate_pe_ratio(),
            'volume': random.randint(100000, 10000000),
            'beta': random.uniform(0.5, 2.0),
            'dividend_yield': random.uniform(0.0, 0.05),
            'price_history': [company.stock_price] * 20,
            'eps': company.metrics.profit / company.shares_outstanding if company.shares_outstanding > 0 else 0,
            'last_updated': datetime.now().isoformat(),
            'company_id': company.company_id,  # 关联公司ID
            'is_jc_company': True  # 标记为JC原生公司
        }
        
        # 添加到市场数据
        if hasattr(self.main_app, 'market_data'):
            self.main_app.market_data.stocks[company.symbol] = stock_data
            self.main_app.market_data.save_stocks()
            
    def get_company_by_symbol(self, symbol: str) -> Optional[JCCompany]:
        """通过股票代码获取公司"""
        company_id = self.stock_symbols.get(symbol)
        if company_id:
            return self.companies.get(company_id)
        return None
        
    def get_user_companies(self, user_id: str) -> List[JCCompany]:
        """获取用户创建的公司"""
        company_ids = self.user_companies.get(user_id, [])
        return [self.companies[cid] for cid in company_ids if cid in self.companies]
        
    def show_company_market(self) -> str:
        """显示公司市场概览"""
        public_companies = [c for c in self.companies.values() if c.is_public]
        private_companies = [c for c in self.companies.values() if not c.is_public]
        
        market_text = f"""
🏢 JC公司市场 - 原生企业生态

📊 市场概况:
  上市公司: {len(public_companies)}家
  私人公司: {len(private_companies)}家
  总市值: J${sum(c.market_cap for c in public_companies):,.0f}
  
📈 今日活跃股票:
"""
        
        # 按市值排序显示前10家上市公司
        sorted_public = sorted(public_companies, key=lambda x: x.market_cap, reverse=True)[:10]
        
        for i, company in enumerate(sorted_public, 1):
            # 模拟股价变动
            price_change = random.uniform(-0.05, 0.05)
            change_icon = "📈" if price_change > 0 else "📉" if price_change < 0 else "📊"
            
            market_text += f"""
{i:2d}. {change_icon} {company.symbol} - {company.name}
    价格: J${company.stock_price:.2f} ({price_change:+.2%})
    市值: J${company.market_cap:,.0f} | 行业: {company.industry.value.title()}
"""

        market_text += f"""

🏭 行业分布:
"""
        # 统计行业分布
        industry_counts = {}
        for company in self.companies.values():
            industry = company.industry.value
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
            
        for industry, count in sorted(industry_counts.items(), key=lambda x: x[1], reverse=True):
            market_text += f"  {industry.title()}: {count}家\n"
            
        market_text += f"""

🎮 公司管理:
  company create <公司名> <行业>     - 创建新公司
  company list                      - 查看我的公司
  company info <公司ID/股票代码>     - 公司详情
  company ipo <公司ID> <价格> <股数> - 申请IPO
  company news <公司ID>             - 公司新闻
  
💡 行业选择: technology, finance, healthcare, energy, manufacturing, 
           retail, real_estate, transportation, telecom, utilities,
           consumer_goods, agriculture
"""
        
        return market_text
        
    def show_company_info(self, identifier: str) -> str:
        """显示公司详细信息"""
        company = None
        
        # 先尝试作为公司ID查找
        if identifier in self.companies:
            company = self.companies[identifier]
        # 再尝试作为股票代码查找
        elif identifier.upper() in self.stock_symbols:
            company = self.get_company_by_symbol(identifier.upper())
        # 最后尝试模糊匹配公司名称
        else:
            for c in self.companies.values():
                if identifier.lower() in c.name.lower():
                    company = c
                    break
                    
        if not company:
            return f"❌ 未找到公司: {identifier}"
            
        return company.get_display_info()
        
    def show_user_companies(self, user_id: str) -> str:
        """显示用户的公司列表"""
        user_companies = self.get_user_companies(user_id)
        
        if not user_companies:
            return """
📋 我的公司

您还没有创建任何公司。

🎮 创建公司:
  company create <公司名> <行业>

💡 提示: 创建公司后可以通过经营管理最终实现IPO上市
"""

        companies_text = f"""
📋 我的公司 ({len(user_companies)}家)

"""
        
        for i, company in enumerate(user_companies, 1):
            status_icon = "📈" if company.is_public else "🏢"
            performance_icon = "🟢" if company.performance_score > 70 else "🟡" if company.performance_score > 50 else "🔴"
            
            companies_text += f"""
{i}. {status_icon} {company.name} ({company.symbol})
   状态: {'已上市' if company.is_public else '未上市'} | 行业: {company.industry.value.title()}
   表现: {performance_icon} {company.performance_score:.1f}/100 | 阶段: {company.stage.value.title()}
   {'股价: J$' + f'{company.stock_price:.2f}' if company.is_public else '估值: J$' + f'{company.metrics.calculate_equity():,.0f}'}
   员工: {company.metrics.employees}人 | 营收: J${company.metrics.revenue:,.0f}
"""

            if not company.is_public:
                can_ipo, ipo_msg = company.can_go_public()
                companies_text += f"   IPO: {'✅ 可申请' if can_ipo else '❌ ' + ipo_msg}\n"
                
        companies_text += f"""

🎮 管理操作:
  company info <公司ID>             - 查看详情
  company ipo <公司ID> <价格> <股数> - 申请IPO
  company news <公司ID>             - 查看新闻
  company develop <公司ID>          - 公司发展
"""
        
        return companies_text
        
    def show_company_news(self, company_id: str) -> str:
        """显示公司新闻"""
        company = self.companies.get(company_id)
        if not company:
            return f"❌ 公司不存在: {company_id}"
            
        if not company.news_events:
            return f"📰 {company.name} 暂无新闻事件"
            
        news_text = f"""
📰 {company.name} - 公司新闻

"""
        
        # 按时间倒序显示新闻
        sorted_news = sorted(company.news_events, key=lambda x: x.publish_date, reverse=True)
        
        for i, news in enumerate(sorted_news[:20], 1):  # 显示最近20条
            impact_icon = "📈" if news.impact_type == "positive" else "📉" if news.impact_type == "negative" else "📊"
            date_str = news.publish_date[:10]
            
            news_text += f"""
{i:2d}. {impact_icon} {news.title}
    时间: {date_str} | 类别: {news.category.title()} | 影响: {news.impact_magnitude*100:.1f}%
    内容: {news.content}
    
"""

        return news_text
        
    def develop_company(self, company_id: str, development_type: str) -> Tuple[bool, str]:
        """公司发展操作"""
        company = self.companies.get(company_id)
        if not company:
            return False, f"公司不存在: {company_id}"
            
        # 检查用户权限
        current_user = self.main_app.user_manager.current_user
        if company.created_by_user != current_user:
            return False, "您没有权限管理这家公司"
            
        development_options = {
            'research': self._develop_research,
            'marketing': self._develop_marketing,
            'expansion': self._develop_expansion,
            'efficiency': self._develop_efficiency
        }
        
        if development_type not in development_options:
            return False, f"无效的发展类型: {development_type}\n可选: {', '.join(development_options.keys())}"
            
        return development_options[development_type](company)
        
    def _develop_research(self, company: JCCompany) -> Tuple[bool, str]:
        """研发投入"""
        cost = company.metrics.revenue * 0.1  # 10%营收投入研发
        if cost > company.metrics.assets * 0.2:  # 最多20%资产
            return False, "研发投入过大，资金不足"
            
        # 执行研发
        company.metrics.assets -= cost
        
        # 随机效果
        if random.random() < 0.7:  # 70%成功率
            # 成功: 提升增长率和表现评分
            growth_boost = random.uniform(0.05, 0.15)
            company.metrics.growth_rate += growth_boost
            company.performance_score += random.uniform(5, 15)
            
            # 生成正面新闻
            news = company.generate_news_event('product')
            
            result = f"""
✅ 研发投入成功！

💰 投入成本: J${cost:,.0f}
📈 增长率提升: +{growth_boost*100:.1f}%
⭐ 表现评分提升: {company.performance_score:.1f}/100

{f'📰 新闻: {news.title}' if news else ''}
"""
        else:
            # 失败: 仅消耗资金
            result = f"""
❌ 研发项目失败

💸 投入成本: J${cost:,.0f}
📉 未获得预期效果，但积累了宝贵经验
"""

        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        return True, result
        
    def _develop_marketing(self, company: JCCompany) -> Tuple[bool, str]:
        """市场推广"""
        cost = company.metrics.revenue * 0.08  # 8%营收投入营销
        if cost > company.metrics.assets * 0.15:
            return False, "营销预算过大，资金不足"
            
        company.metrics.assets -= cost
        
        # 提升市场份额和营收
        market_boost = random.uniform(0.001, 0.005)
        revenue_boost = random.uniform(0.1, 0.2)
        
        company.metrics.market_share += market_boost
        company.metrics.revenue *= (1 + revenue_boost)
        company.performance_score += random.uniform(3, 8)
        
        result = f"""
✅ 市场推广成功！

💰 投入成本: J${cost:,.0f}
📊 市场份额提升: +{market_boost*100:.3f}%
💵 营收增长: +{revenue_boost*100:.1f}%
⭐ 表现评分: {company.performance_score:.1f}/100
"""

        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        return True, result
        
    def _develop_expansion(self, company: JCCompany) -> Tuple[bool, str]:
        """业务扩张"""
        cost = company.metrics.revenue * 0.15  # 15%营收投入扩张
        if cost > company.metrics.assets * 0.3:
            return False, "扩张资金需求过大"
            
        company.metrics.assets -= cost
        
        # 增加员工和资产
        employee_growth = random.randint(20, 100)
        asset_growth = cost * random.uniform(1.2, 2.0)  # 投入产生1.2-2倍资产
        
        company.metrics.employees += employee_growth
        company.metrics.assets += asset_growth
        company.metrics.growth_rate += random.uniform(0.08, 0.15)
        
        # 提升公司阶段
        if company.stage == CompanyStage.STARTUP and company.metrics.employees > 100:
            company.stage = CompanyStage.GROWTH
            stage_msg = "公司进入成长期！"
        elif company.stage == CompanyStage.GROWTH and company.metrics.employees > 500:
            company.stage = CompanyStage.MATURE
            stage_msg = "公司进入成熟期！"
        else:
            stage_msg = ""
            
        result = f"""
✅ 业务扩张成功！

💰 投入成本: J${cost:,.0f}
👥 新增员工: +{employee_growth}人 (总计: {company.metrics.employees}人)
🏢 资产增长: J${asset_growth:,.0f}
📈 增长率提升: +{(company.metrics.growth_rate)*100:.1f}%

{stage_msg}
"""

        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        return True, result
        
    def _develop_efficiency(self, company: JCCompany) -> Tuple[bool, str]:
        """效率优化"""
        cost = company.metrics.revenue * 0.05  # 5%营收投入效率优化
        
        company.metrics.assets -= cost
        
        # 提升利润率，降低成本
        profit_improvement = company.metrics.revenue * random.uniform(0.02, 0.08)
        company.metrics.profit += profit_improvement
        
        # 降低债务比率
        debt_reduction = random.uniform(0.01, 0.05)
        company.metrics.debt_ratio = max(0.1, company.metrics.debt_ratio - debt_reduction)
        
        company.performance_score += random.uniform(2, 6)
        
        result = f"""
✅ 效率优化成功！

💰 投入成本: J${cost:,.0f}
💵 利润提升: J${profit_improvement:,.0f}
📉 债务率降低: -{debt_reduction*100:.1f}%
⭐ 表现评分: {company.performance_score:.1f}/100

💡 运营效率显著提升
"""

        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        return True, result
        
    def update_all_companies(self):
        """更新所有公司数据"""
        for company in self.companies.values():
            # 更新表现评分
            company.update_performance_score()
            
            # 随机生成新闻事件
            if random.random() < 0.05:  # 5%概率
                company.generate_news_event()
                
            # 更新公开公司股价
            if company.is_public:
                self._update_stock_price(company)
                
        self.save_companies()
        
    def _update_stock_price(self, company: JCCompany):
        """更新股票价格"""
        # 基于公司表现调整股价
        performance_factor = (company.performance_score - 50) / 100  # -0.5 to 0.5
        
        # 基础波动
        base_volatility = 0.02 + company.risk_level * 0.005
        random_change = random.uniform(-base_volatility, base_volatility)
        
        # 表现影响
        performance_impact = performance_factor * 0.1
        
        # 新闻影响
        news_impact = 0.0
        recent_news = [n for n in company.news_events if 
                      (datetime.now() - datetime.fromisoformat(n.publish_date)).days <= 1]
        for news in recent_news:
            if news.impact_type == 'positive':
                news_impact += news.impact_magnitude
            else:
                news_impact -= news.impact_magnitude
                
        total_change = random_change + performance_impact + news_impact
        new_price = company.stock_price * (1 + total_change)
        new_price = max(0.01, new_price)  # 最低1分钱
        
        company.update_stock_price(new_price)
        
        # 同步更新市场数据
        if hasattr(self.main_app, 'market_data') and company.symbol in self.main_app.market_data.stocks:
            stock_data = self.main_app.market_data.stocks[company.symbol]
            old_price = stock_data['price']
            stock_data['price'] = new_price
            stock_data['change'] = new_price - old_price
            stock_data['market_cap'] = company.market_cap
            stock_data['last_updated'] = datetime.now().isoformat()
            
    def get_industry_report(self, industry: str) -> str:
        """获取行业报告"""
        try:
            industry_enum = IndustryCategory(industry.lower())
        except ValueError:
            return f"❌ 无效的行业: {industry}"
            
        # 筛选行业公司
        industry_companies = [c for c in self.companies.values() if c.industry == industry_enum]
        
        if not industry_companies:
            return f"📊 {industry_enum.value.title()} 行业暂无公司"
            
        # 统计分析
        total_companies = len(industry_companies)
        public_companies = [c for c in industry_companies if c.is_public]
        total_market_cap = sum(c.market_cap for c in public_companies)
        avg_performance = sum(c.performance_score for c in industry_companies) / total_companies
        
        total_revenue = sum(c.metrics.revenue for c in industry_companies)
        total_employees = sum(c.metrics.employees for c in industry_companies)
        
        report = f"""
📊 {industry_enum.value.title()} 行业分析报告

🏢 行业概况:
  公司总数: {total_companies}家
  上市公司: {len(public_companies)}家
  总市值: J${total_market_cap:,.0f}
  平均表现: {avg_performance:.1f}/100
  
💰 经营数据:
  行业总营收: J${total_revenue:,.0f}
  总就业人数: {total_employees:,}人
  平均营收: J${total_revenue/total_companies:,.0f}
  
📈 表现排名:
"""
        
        # 按表现排序
        sorted_companies = sorted(industry_companies, key=lambda x: x.performance_score, reverse=True)
        
        for i, company in enumerate(sorted_companies[:10], 1):
            status = "📈" if company.is_public else "🏢"
            report += f"""
{i:2d}. {status} {company.name} ({company.symbol})
    表现: {company.performance_score:.1f}/100 | 员工: {company.metrics.employees}人
    营收: J${company.metrics.revenue:,.0f} | 阶段: {company.stage.value}
"""

        return report 