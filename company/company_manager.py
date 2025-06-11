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
from .company_storage import CompanyStorageManager


class CompanyManager:
    """公司管理器"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.companies: Dict[str, JCCompany] = {}  # {company_id: JCCompany}
        self.stock_symbols: Dict[str, str] = {}    # {symbol: company_id}
        self.user_companies: Dict[str, List[str]] = {}  # {user_id: [company_ids]}
        self.storage_manager = CompanyStorageManager()
        
        # 初始化JC股票更新器
        try:
            from .jc_stock_updater import JCStockUpdater
            self.jc_stock_updater = JCStockUpdater(self, main_app.market_data)
            print("✅ JC股票更新器初始化成功")
        except Exception as e:
            print(f"❌ JC股票更新器初始化失败: {e}")
            self.jc_stock_updater = None
        
        self.load_companies()
        
    def load_companies(self):
        """加载公司数据"""
        try:
            # 使用新的存储管理器加载数据
            self.companies, self.user_companies = self.storage_manager.load_companies()
            
            # 重建股票代码映射
            self.stock_symbols = {}
            for company in self.companies.values():
                if company.is_public and company.symbol:
                    self.stock_symbols[company.symbol] = company.company_id
            
            # 如果没有数据，创建示例公司
            if not self.companies:
                print("创建示例公司数据...")
                sample_companies = create_sample_companies()
                for company in sample_companies:
                    self.companies[company.company_id] = company
                    if company.is_public and company.symbol:
                        self.stock_symbols[company.symbol] = company.company_id
                self.save_companies()
            
            # 启动JC股票更新器
            if self.jc_stock_updater and len([c for c in self.companies.values() if c.is_public]) > 0:
                print(f"🚀 启动JC股票价格更新器，监控 {len([c for c in self.companies.values() if c.is_public])} 只上市股票")
                self.jc_stock_updater.start_price_updates()
                
        except Exception as e:
            print(f"加载公司数据失败: {e}")
            
    def save_companies(self):
        """保存公司数据"""
        try:
            success = self.storage_manager.save_companies(self.companies, self.user_companies)
            if not success:
                print("使用存储管理器保存失败，尝试备用方法...")
                # 备用保存方法
                self._fallback_save()
        except Exception as e:
            print(f"保存公司数据失败: {e}")
    
    def _fallback_save(self):
        """备用保存方法"""
        try:
            os.makedirs('data', exist_ok=True)
            data = {
                'companies': [self._legacy_company_to_dict(company) for company in self.companies.values()],
                'user_companies': self.user_companies,
                'last_updated': datetime.now().isoformat()
            }
            
            with open('data/jc_companies_fallback.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("已使用备用方法保存公司数据")
        except Exception as e:
            print(f"备用保存方法也失败: {e}")
            
    def _legacy_company_to_dict(self, company: JCCompany) -> Dict:
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
        """创建新公司 - 简化版本，建议使用创建向导"""
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
        
    def create_company_with_wizard_data(self, wizard_data: Dict) -> Tuple[bool, str]:
        """使用创建向导数据创建公司"""
        try:
            from .company_types import CompanyType, BusinessMetrics, CompanyFinancials
            import uuid
            
            # 生成公司ID和股票代码
            company_id = str(uuid.uuid4())[:8]
            symbol = self._generate_symbol(wizard_data['company_name'])
            
            # 创建业务指标
            initial_funding = wizard_data.get('initial_funding', 1000000)
            metrics = BusinessMetrics(
                revenue=0.0,
                profit=0.0,
                assets=initial_funding,
                liabilities=0.0,
                employees=wizard_data.get('initial_employees', 10),
                market_share=0.01,
                growth_rate=0.0,
                debt_ratio=0.0
            )
            
            # 创建财务数据
            financials = CompanyFinancials()
            
            # 创建公司对象
            company = JCCompany(
                company_id=company_id,
                name=wizard_data['company_name'],
                symbol=symbol,
                industry=IndustryCategory(wizard_data['industry']),
                company_type=CompanyType(wizard_data.get('company_type', 'private')),
                stage=CompanyStage.STARTUP,
                founded_date=datetime.now().strftime("%Y-%m-%d"),
                description=wizard_data.get('description', ''),
                headquarters=wizard_data.get('headquarters', '北京'),
                website=f"www.{wizard_data['company_name'].lower().replace(' ', '')}.com",
                ceo_name=wizard_data.get('ceo_name', '创始人'),
                metrics=metrics,
                financials=financials,
                is_public=False,
                stock_price=10.0,
                shares_outstanding=1000000,
                market_cap=10000000.0,
                performance_score=50.0,
                risk_level='中等',
                created_by_user=wizard_data['user_id']
            )
            
            # 添加到公司字典
            self.companies[company_id] = company
            
            # 添加到用户公司列表
            if wizard_data['user_id'] not in self.user_companies:
                self.user_companies[wizard_data['user_id']] = []
            self.user_companies[wizard_data['user_id']].append(company_id)
            
            # 保存数据
            self.save_companies()
            
            return True, f"🎉 成功创建公司 {company.name}！\n📋 公司ID: {company_id}\n🏢 行业: {wizard_data['industry']}\n💰 初始资金: ¥{initial_funding:,.0f}"
            
        except Exception as e:
            return False, f"❌ 创建公司失败: {str(e)}"
        
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
            self.stock_symbols[company.symbol] = company.company_id
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
        
    def find_company_by_identifier(self, identifier: str, user_only: bool = False) -> Optional[JCCompany]:
        """
        智能查找公司
        支持5种查找方式：
        1. 精确匹配公司ID
        2. 大小写不敏感的公司ID匹配  
        3. 股票代码匹配(大小写不敏感)
        4. 公司名称模糊匹配
        5. 股票代码部分匹配
        """
        company = None
        identifier_lower = identifier.lower()
        
        # 如果只查找用户的公司，先筛选范围
        search_companies = self.companies
        if user_only:
            user_companies = self.get_user_companies(self.main_app.user_manager.current_user)
            search_companies = {c.company_id: c for c in user_companies}
        
        # 1. 先尝试精确匹配公司ID
        if identifier in search_companies:
            company = search_companies[identifier]
        
        # 2. 尝试大小写不敏感的公司ID匹配
        if not company:
            for company_id, c in search_companies.items():
                if company_id.lower() == identifier_lower:
                    company = c
                    break
                    
        # 3. 尝试作为股票代码查找(大小写不敏感)
        if not company:
            for c in search_companies.values():
                if c.symbol.lower() == identifier_lower:
                    company = c
                    break
        
        # 4. 尝试模糊匹配公司名称
        if not company:
            for c in search_companies.values():
                if identifier_lower in c.name.lower():
                    company = c
                    break
        
        # 5. 尝试匹配股票代码的部分内容
        if not company:
            for c in search_companies.values():
                if identifier_lower in c.symbol.lower():
                    company = c
                    break
                    
        return company

    def show_company_info(self, identifier: str) -> str:
        """显示公司详细信息"""
        company = self.find_company_by_identifier(identifier)
                    
        if not company:
            # 提供更详细的错误信息和建议
            user_companies = self.get_user_companies(self.main_app.user_manager.current_user)
            if user_companies:
                suggestions = []
                for uc in user_companies:
                    suggestions.append(f"  • {uc.name}: 公司ID={uc.company_id}, 股票代码={uc.symbol}")
                suggestions_text = "\n".join(suggestions)
                
                return f"""
❌ 未找到公司: {identifier}

💡 您拥有的公司:
{suggestions_text}

🔍 查找方式:
  • 使用完整公司ID: company info {user_companies[0].company_id}
  • 使用股票代码: company info {user_companies[0].symbol}
  • 使用公司名称: company info {user_companies[0].name}
  • 查看所有公司: company my
"""
            else:
                return f"""
❌ 未找到公司: {identifier}

💡 您还没有创建任何公司，请先创建:
  • 向导创建: company wizard
  • 快速创建: company create <公司名> <行业>
"""
            
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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{i}. {status_icon} {company.name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🆔 公司ID:   【{company.company_id}】
   📊 股票代码: 【{company.symbol}】
   🏭 行业:     {company.industry.value.title()} | 阶段: {company.stage.value.title()}
   📊 状态:     {'📈 已上市' if company.is_public else '🏢 未上市'}
   ⭐ 表现:     {performance_icon} {company.performance_score:.1f}/100
   {'💰 股价:     J$' + f'{company.stock_price:.2f}' if company.is_public else '💎 估值:     J$' + f'{company.metrics.calculate_equity():,.0f}'}
   👥 员工:     {company.metrics.employees}人
   💵 营收:     J${company.metrics.revenue:,.0f}
"""

            if not company.is_public:
                can_ipo, ipo_msg = company.can_go_public()
                companies_text += f"   🚀 IPO:      {'✅ 可申请' if can_ipo else '❌ ' + ipo_msg}\n"
                
        companies_text += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎮 快速管理指令:
  company manage <公司ID>           - 🎯 进入管理中心
  company info <公司ID>             - 📊 查看详细信息  
  company develop <公司ID> <类型>    - 📈 投资发展
  company ipo <公司ID> <价格> <股数> - 🚀 申请IPO上市
  company news <公司ID>             - 📰 查看公司新闻

💡 提示: 公司ID用【】标注，复制时请去掉【】符号
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
        """公司发展投资"""
        if company_id not in self.companies:
            return False, "❌ 公司不存在"
        
        company = self.companies[company_id]
        
        # 检查是否为公司创始人
        if company.created_by_user != self.main_app.user_manager.current_user:
            return False, "❌ 您不是该公司的创始人"
        
        development_types = {
            'research': self._develop_research,
            'marketing': self._develop_marketing,
            'expansion': self._develop_expansion,
            'efficiency': self._develop_efficiency,
            'technology': self._develop_technology,
            'talent': self._develop_talent,
            'brand': self._develop_brand,
            'innovation': self._develop_innovation
        }
        
        if development_type not in development_types:
            available_types = ', '.join(development_types.keys())
            return False, f"❌ 无效的发展类型。可用类型: {available_types}"
        
        return development_types[development_type](company)
        
    def _develop_research(self, company: JCCompany) -> Tuple[bool, str]:
        """研发投资"""
        base_cost = max(company.metrics.revenue * 0.04, 500000)  # 营收的4%或50万最低
        
        # 优先使用公司账户
        if company.company_cash < base_cost:
            shortage = base_cost - company.company_cash
            return False, f"❌ 公司账户资金不足，需要 J${base_cost:,.0f}，当前余额: J${company.company_cash:,.0f}\n💡 建议先使用 'company invest {company.company_id} {shortage:,.0f}' 注资"
        
        # 从公司账户扣除资金
        company.company_cash -= base_cost
        
        # 提升效果
        research_boost = random.uniform(0.1, 0.2)
        company.metrics.profit *= (1 + research_boost)
        company.metrics.growth_rate += 0.03
        company.metrics.assets += base_cost * 0.7  # 研发资产
        
        # 有一定概率获得专利（增加价值）
        if random.random() < 0.3:
            patent_value = base_cost * random.uniform(0.5, 1.5)
            company.metrics.assets += patent_value
            bonus_msg = f"\n🎉 获得重要研发专利，增值 J${patent_value:,.0f}！"
        else:
            bonus_msg = ""

        # 更新公司数据
        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        
        return True, f"✅ 研发投资成功！投入 J${base_cost:,.0f}，利润预计提升 {research_boost*100:.1f}%{bonus_msg}\n💼 公司账户余额: J${company.company_cash:,.0f}"
        
    def _develop_marketing(self, company: JCCompany) -> Tuple[bool, str]:
        """市场营销投资"""
        base_cost = max(company.metrics.revenue * 0.06, 800000)  # 营收的6%或80万最低
        
        # 优先使用公司账户
        if company.company_cash < base_cost:
            shortage = base_cost - company.company_cash
            return False, f"❌ 公司账户资金不足，需要 J${base_cost:,.0f}，当前余额: J${company.company_cash:,.0f}\n💡 建议先使用 'company invest {company.company_id} {shortage:,.0f}' 注资"
        
        # 从公司账户扣除资金
        company.company_cash -= base_cost
        
        # 提升效果
        marketing_boost = random.uniform(0.08, 0.15)
        market_share_gain = random.uniform(0.001, 0.003)
        
        company.metrics.revenue *= (1 + marketing_boost)
        company.metrics.market_share += market_share_gain
        
        # 行业加成
        industry_bonus = self._get_industry_marketing_bonus(company.industry.value)
        if industry_bonus > 0:
            additional_boost = marketing_boost * industry_bonus
            company.metrics.revenue *= (1 + additional_boost)
            bonus_msg = f"\n🎯 {company.industry.value}行业营销加成 +{additional_boost*100:.1f}%"
        else:
            bonus_msg = ""
        
        # 更新公司数据
        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        
        return True, f"✅ 市场营销成功！营收提升 {marketing_boost*100:.1f}%，市场份额增加 {market_share_gain*100:.3f}%{bonus_msg}\n💼 公司账户余额: J${company.company_cash:,.0f}"
        
    def _develop_expansion(self, company: JCCompany) -> Tuple[bool, str]:
        """业务扩张投资（包含员工扩张）"""
        base_cost = max(company.metrics.revenue * 0.1, 1200000)  # 营收的10%或120万最低
        
        # 优先使用公司账户
        if company.company_cash < base_cost:
            shortage = base_cost - company.company_cash
            return False, f"❌ 公司账户资金不足，需要 J${base_cost:,.0f}，当前余额: J${company.company_cash:,.0f}\n💡 建议先使用 'company invest {company.company_id} {shortage:,.0f}' 注资"
        
        # 从公司账户扣除资金
        company.company_cash -= base_cost
        
        # 扩张效果 - 🔧 修复：不虚拟增加员工
        expansion_boost = random.uniform(0.12, 0.20)
        new_locations = random.randint(1, 3)
        suggested_hiring_budget = int(base_cost * 0.4)  # 建议用40%资金招聘
        
        company.metrics.revenue *= (1 + expansion_boost)
        # company.metrics.employees += new_employees  # 🔧 修复：不再虚拟增加员工
        company.metrics.assets += base_cost * 0.8  # 扩张资产（办公场所、设备等）
        company.metrics.market_share += random.uniform(0.002, 0.005)
        
        # 扩张风险调整
        if random.random() < 0.2:  # 20%概率扩张过快带来管理问题
            risk_penalty = random.uniform(0.02, 0.05)
            company.metrics.profit *= (1 - risk_penalty)
            company.risk_level = min(5, company.risk_level + 1)
            risk_msg = f"\n⚠️ 扩张速度较快，管理成本增加 {risk_penalty*100:.1f}%"
        else:
            risk_msg = ""
        
        # 更新公司数据
        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        
        return True, f"✅ 业务扩张成功！新增 {new_locations} 个业务点，营收提升 {expansion_boost*100:.1f}%{risk_msg}\n💡 建议招聘预算: J${suggested_hiring_budget:,.0f}\n💼 公司账户余额: J${company.company_cash:,.0f}"

    def _develop_efficiency(self, company: JCCompany) -> Tuple[bool, str]:
        """效率提升投资"""
        base_cost = max(company.metrics.employees * 20000, 300000)  # 每员工2万或30万最低
        
        # 优先使用公司账户
        if company.company_cash < base_cost:
            shortage = base_cost - company.company_cash
            return False, f"❌ 公司账户资金不足，需要 J${base_cost:,.0f}，当前余额: J${company.company_cash:,.0f}\n💡 建议先使用 'company invest {company.company_id} {shortage:,.0f}' 注资"
        
        # 从公司账户扣除资金
        company.company_cash -= base_cost
        
        # 提升效果
        efficiency_boost = random.uniform(0.06, 0.12)
        cost_reduction = random.uniform(0.03, 0.08)
        
        # 效率提升主要影响利润率
        company.metrics.profit *= (1 + efficiency_boost + cost_reduction)
        company.metrics.growth_rate += 0.01
        
        # 有机会减少员工流失（降低未来招聘成本）
        if random.random() < 0.4:
            retention_bonus = random.uniform(0.02, 0.05)
            company.metrics.profit *= (1 + retention_bonus)
            retention_msg = f"\n👥 员工满意度提升，流失率降低，额外利润提升 {retention_bonus*100:.1f}%"
        else:
            retention_msg = ""
        
        # 更新公司数据
        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        
        return True, f"✅ 效率提升成功！运营效率提升 {efficiency_boost*100:.1f}%，成本削减 {cost_reduction*100:.1f}%{retention_msg}\n💼 公司账户余额: J${company.company_cash:,.0f}"

    def _develop_technology(self, company: JCCompany) -> Tuple[bool, str]:
        """技术升级投资"""
        base_cost = max(company.metrics.revenue * 0.05, 1000000)  # 营收的5%或100万最低
        
        # 优先使用公司账户
        if company.company_cash < base_cost:
            shortage = base_cost - company.company_cash
            return False, f"❌ 公司账户资金不足，需要 J${base_cost:,.0f}，当前余额: J${company.company_cash:,.0f}\n💡 建议先使用 'company invest {company.company_id} {shortage:,.0f}' 注资"
        
        # 从公司账户扣除资金
        company.company_cash -= base_cost
        
        # 提升效果
        tech_boost = random.uniform(0.08, 0.15)
        company.metrics.revenue *= (1 + tech_boost)
        company.metrics.profit *= (1 + tech_boost * 1.2)
        company.metrics.assets += base_cost * 0.6  # 技术资产
        
        # 更新公司数据
        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        
        return True, f"✅ 技术升级成功！投入 J${base_cost:,.0f}，预计营收提升 {tech_boost*100:.1f}%\n💼 公司账户余额: J${company.company_cash:,.0f}"

    def _develop_talent(self, company: JCCompany) -> Tuple[bool, str]:
        """人才培养投资"""
        base_cost = max(company.metrics.employees * 50000, 500000)  # 每员工5万或50万最低
        
        # 优先使用公司账户
        if company.company_cash < base_cost:
            shortage = base_cost - company.company_cash
            return False, f"❌ 公司账户资金不足，需要 J${base_cost:,.0f}，当前余额: J${company.company_cash:,.0f}\n💡 建议先使用 'company invest {company.company_id} {shortage:,.0f}' 注资"
        
        # 从公司账户扣除资金
        company.company_cash -= base_cost
        
        # 提升效果 - 🔧 修复：改为培训现有员工，不虚拟增加员工
        talent_boost = random.uniform(0.06, 0.12)
        suggested_hiring_budget = int(base_cost * 0.5)  # 建议用50%资金招聘
        
        # 🔧 修复：提升现有员工表现，而非虚拟增加员工数
        for staff in company.staff_list:
            staff['performance'] = min(100, staff['performance'] + random.uniform(3, 8))
        
        # company.metrics.employees += new_employees  # 🔧 修复：不再虚拟增加员工
        company.metrics.profit *= (1 + talent_boost)
        company.metrics.growth_rate += 0.02
        
        # 更新公司数据
        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        
        return True, f"✅ 人才培养成功！员工技能提升，效率提升 {talent_boost*100:.1f}%\n💡 建议招聘预算: J${suggested_hiring_budget:,.0f}\n💼 公司账户余额: J${company.company_cash:,.0f}"

    def _develop_brand(self, company: JCCompany) -> Tuple[bool, str]:
        """品牌建设投资"""
        base_cost = max(company.metrics.revenue * 0.03, 800000)  # 营收的3%或80万最低
        
        # 优先使用公司账户
        if company.company_cash < base_cost:
            shortage = base_cost - company.company_cash
            return False, f"❌ 公司账户资金不足，需要 J${base_cost:,.0f}，当前余额: J${company.company_cash:,.0f}\n💡 建议先使用 'company invest {company.company_id} {shortage:,.0f}' 注资"
        
        # 从公司账户扣除资金
        company.company_cash -= base_cost
        
        # 提升效果
        brand_boost = random.uniform(0.05, 0.10)
        company.metrics.market_share += brand_boost * 0.5
        company.metrics.revenue *= (1 + brand_boost)
        company.risk_level = max(1, company.risk_level - 1)  # 降低风险
        
        # 更新公司数据
        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        
        return True, f"✅ 品牌建设成功！市场份额增加 {brand_boost*50:.2f}%，风险等级降低\n💼 公司账户余额: J${company.company_cash:,.0f}"

    def _develop_innovation(self, company: JCCompany) -> Tuple[bool, str]:
        """创新研发投资"""
        base_cost = max(company.metrics.revenue * 0.08, 1500000)  # 营收的8%或150万最低
        
        # 优先使用公司账户
        if company.company_cash < base_cost:
            shortage = base_cost - company.company_cash
            return False, f"❌ 公司账户资金不足，需要 J${base_cost:,.0f}，当前余额: J${company.company_cash:,.0f}\n💡 建议先使用 'company invest {company.company_id} {shortage:,.0f}' 注资"
        
        # 从公司账户扣除资金
        company.company_cash -= base_cost
        
        # 提升效果（创新投资风险较高但收益也高）
        success_rate = 0.7  # 70%成功率
        if random.random() < success_rate:
            innovation_boost = random.uniform(0.15, 0.25)
            company.metrics.revenue *= (1 + innovation_boost)
            company.metrics.profit *= (1 + innovation_boost * 1.3)
            company.metrics.growth_rate += 0.05
            
            # 生成创新新闻
            company.generate_news_event('product')
            
            result = f"✅ 创新研发大获成功！营收预计提升 {innovation_boost*100:.1f}%"
        else:
            # 失败情况，但不是完全损失
            minor_boost = random.uniform(0.02, 0.05)
            company.metrics.revenue *= (1 + minor_boost)
            result = f"⚠️ 创新研发效果一般，仅获得 {minor_boost*100:.1f}% 的营收提升"
        
        # 更新公司数据
        company.last_updated = datetime.now().isoformat()
        self.save_companies()
        
        return True, f"{result}\n💼 公司账户余额: J${company.company_cash:,.0f}"

    def evaluate_acquisition(self, acquirer_id: str, target_symbol: str) -> Tuple[bool, str]:
        """评估收购价格和可行性（第一步）"""
        # 🔧 修复：支持股票代码作为收购方识别符
        acquirer = self.find_company_by_identifier(acquirer_id, user_only=True)
        if not acquirer:
            # 提供详细的错误信息和用户公司列表
            user_companies = self.get_user_companies(self.main_app.user_manager.current_user)
            if user_companies:
                suggestions = []
                for uc in user_companies:
                    suggestions.append(f"  • {uc.name}: 公司ID={uc.company_id}, 股票代码={uc.symbol}")
                suggestions_text = "\n".join(suggestions)
                
                return False, f"""❌ 未找到收购方公司: {acquirer_id}

💡 您拥有的公司:
{suggestions_text}

🔍 正确用法:
  company acquire <您的公司ID或股票代码> <目标股票代码>"""
            else:
                return False, """❌ 您还没有创建任何公司

💡 请先创建公司:
  company wizard    # 创建向导
  company create <公司名> <行业>"""
            
        # 🔧 修复：同时支持通过股票代码和公司ID查找目标公司
        target = None
        
        # 先尝试通过股票代码查找
        target = self.get_company_by_symbol(target_symbol)
        
        # 如果没找到，再尝试通过公司ID查找
        if not target:
            target = self.find_company_by_identifier(target_symbol, user_only=False)
        
        if not target:
            # 提供更详细的错误信息和建议
            all_companies = list(self.companies.values())
            if all_companies:
                suggestions = []
                for company in all_companies[:10]:  # 显示前10个公司
                    status = "📈 已上市" if company.is_public else "🏢 未上市"
                    suggestions.append(f"  • {company.name}: ID={company.company_id}, 代码={company.symbol} ({status})")
                suggestions_text = "\n".join(suggestions)
                
                return False, f"""❌ 未找到目标公司: {target_symbol}

💡 可选择的公司:
{suggestions_text}
{'...' if len(all_companies) > 10 else ''}

🔍 使用方法:
  company acquire <您的公司> <目标公司ID或股票代码>
  
📖 查看所有公司: company market"""
            else:
                return False, "❌ 系统中暂无其他公司可供收购"
            
        if not target.is_public:
            return False, f"""❌ 目标公司 {target.name} ({target_symbol}) 未上市，无法收购

💡 只有已上市的公司才能被收购
📊 该公司当前状态: 未上市 (营收: J${target.metrics.revenue:,.0f})
🚀 上市条件: 营收需达到1亿元且表现评分>70分

📖 查看已上市公司: company market"""
            
        # 检查是否为收购方创始人
        if acquirer.created_by_user != self.main_app.user_manager.current_user:
            return False, "❌ 您不是收购方公司的创始人"
            
        # 检查是否为同一家公司
        if acquirer.company_id == target.company_id:
            return False, "❌ 不能收购自己的公司"
            
        # 计算收购估值
        base_price = target.stock_price
        market_cap = target.market_cap
        
        # 计算合理收购溢价（20%-50%不等，根据公司表现）
        if target.performance_score > 80:
            premium_rate = 0.35 + random.uniform(0.05, 0.15)  # 35%-50%
        elif target.performance_score > 60:
            premium_rate = 0.25 + random.uniform(0.05, 0.10)  # 25%-35%
        else:
            premium_rate = 0.20 + random.uniform(0.0, 0.10)   # 20%-30%
        
        acquisition_price = base_price * (1 + premium_rate)
        total_cost = acquisition_price * target.shares_outstanding
        
        # 计算协同效应价值
        synergy_value = self._calculate_synergy_value(acquirer, target)
        
        # 生成评估报告
        evaluation_report = f"""
🔍 收购评估报告 - {target.name} ({target.symbol})

📊 目标公司基本信息:
  公司名称: {target.name}
  行业: {target.industry.value}
  当前股价: J${base_price:.2f}
  市值: J${market_cap:,.0f}
  总股本: {target.shares_outstanding:,}股
  表现评分: {target.performance_score:.1f}/100

💰 收购价格评估:
  当前股价: J${base_price:.2f}
  收购溢价: {premium_rate*100:.1f}%
  收购价格: J${acquisition_price:.2f}/股
  总收购成本: J${total_cost:,.0f}

🏢 收购方资金状况:
  公司名称: {acquirer.name}
  账户余额: J${acquirer.company_cash:,.0f}
  资金充足度: {'✅ 充足' if acquirer.company_cash >= total_cost else f'❌ 不足（缺口: J${total_cost - acquirer.company_cash:,.0f}）'}

📈 协同效应分析:
{synergy_value['report']}

💡 收购建议:
"""
        
        if acquirer.company_cash < total_cost:
            shortage = total_cost - acquirer.company_cash
            evaluation_report += f"""  ❌ 资金不足，需要补充 J${shortage:,.0f}
  💡 建议: company invest {acquirer_id} {shortage:,.0f}
  
⚠️  请先筹集足够资金再考虑收购"""
        else:
            roi_estimate = synergy_value.get('expected_roi', 0)
            if roi_estimate > 0.15:
                recommendation = "🟢 强烈推荐收购"
            elif roi_estimate > 0.08:
                recommendation = "🟡 谨慎推荐收购"
            else:
                recommendation = "🔴 不推荐收购"
                
            evaluation_report += f"""  {recommendation}
  📊 预期ROI: {roi_estimate*100:.1f}%
  🔄 整合难度: {'高' if abs(len(acquirer.staff_list) - len(target.staff_list)) > 50 else '中' if abs(len(acquirer.staff_list) - len(target.staff_list)) > 20 else '低'}
  
✅ 确认收购命令: company acquire {acquirer_id} {target.symbol} confirm"""
        
        return True, evaluation_report
    
    def confirm_acquire_company(self, acquirer_id: str, target_symbol: str) -> Tuple[bool, str]:
        """确认执行收购（第二步）"""
        # 重新验证收购条件
        acquirer = self.find_company_by_identifier(acquirer_id, user_only=True)
        if not acquirer:
            return False, f"❌ 未找到收购方公司: {acquirer_id}"
            
        # 🔧 修复：同时支持通过股票代码和公司ID查找目标公司
        target = self.get_company_by_symbol(target_symbol)
        if not target:
            target = self.find_company_by_identifier(target_symbol, user_only=False)
            
        if not target:
            return False, f"❌ 目标公司 {target_symbol} 不存在"
            
        if not target.is_public:
            return False, f"❌ 目标公司 {target.name} 未上市，无法收购"
            
        if acquirer.created_by_user != self.main_app.user_manager.current_user:
            return False, "❌ 您不是收购方公司的创始人"
            
        if acquirer.company_id == target.company_id:
            return False, "❌ 不能收购自己的公司"
        
        # 重新计算收购价格（市场价格可能有波动）
        base_price = target.stock_price
        
        # 计算收购溢价
        if target.performance_score > 80:
            premium_rate = 0.35 + random.uniform(0.05, 0.15)
        elif target.performance_score > 60:
            premium_rate = 0.25 + random.uniform(0.05, 0.10)
        else:
            premium_rate = 0.20 + random.uniform(0.0, 0.10)
        
        acquisition_price = base_price * (1 + premium_rate)
        total_cost = acquisition_price * target.shares_outstanding
        
        # 检查资金充足性
        if acquirer.company_cash < total_cost:
            shortage = total_cost - acquirer.company_cash
            return False, f"""❌ 收购方公司账户资金不足
  需要: J${total_cost:,.0f}
  现有: J${acquirer.company_cash:,.0f}
  缺口: J${shortage:,.0f}
  
💡 建议: company invest {acquirer_id} {shortage:,.0f}"""
            
        # 执行收购 - 使用公司账户
        acquirer.company_cash -= total_cost
        
        # 🔧 新增：保存收购前的数据用于报告
        original_revenue = acquirer.metrics.revenue
        original_employees = len(acquirer.staff_list)
        original_market_share = acquirer.metrics.market_share
        
        # 合并公司数据
        acquirer.metrics.revenue += target.metrics.revenue
        acquirer.metrics.profit += target.metrics.profit * 0.85  # 考虑整合成本
        acquirer.metrics.assets += target.metrics.assets
        
        # 🔧 修复：将目标公司员工合并到收购方员工列表
        acquired_employees = 0
        if hasattr(target, 'staff_list') and target.staff_list:
            next_id_base = max([staff['id'] for staff in acquirer.staff_list], default=0)
            for i, staff in enumerate(target.staff_list, 1):
                # 70%的员工会被保留
                if random.random() < 0.7:
                    staff['id'] = next_id_base + i
                    staff['hire_date'] = datetime.now().isoformat()
                    staff['note'] = f"通过收购{target.name}加入"
                    acquirer.staff_list.append(staff)
                    acquired_employees += 1
            
        # 同步更新员工数量
        acquirer.metrics.employees = len(acquirer.staff_list)
        acquirer.metrics.market_share += target.metrics.market_share * 0.8  # 80%市场份额保留
        
        # 从市场移除目标公司
        if target.symbol in self.main_app.market_data.stocks:
            del self.main_app.market_data.stocks[target.symbol]
            
        # 从公司列表移除
        del self.companies[target.company_id]
        
        # 生成收购新闻
        news_title = f"{acquirer.name}成功收购{target.name}，斥资{total_cost/1e8:.1f}亿元"
        acquirer.news_events.append(CompanyNews(
            news_id=f"{acquirer.symbol}_acquisition_{datetime.now().strftime('%Y%m%d')}",
            title=news_title,
            content=f"{acquirer.name}以每股{acquisition_price:.2f}元的价格成功收购{target.name}全部股份，实现战略整合。",
            impact_type="positive",
            impact_magnitude=0.12,
            publish_date=datetime.now().isoformat(),
            category="management"
        ))
        
        # 保存数据
        self.save_companies()
        self.main_app.market_data.save_stocks()
        
        # 生成收购完成报告
        completion_report = f"""
✅ 收购交易成功完成！

🤝 交易详情:
  收购方: {acquirer.name} ({acquirer.symbol})
  被收购方: {target.name} ({target.symbol})
  收购价格: J${acquisition_price:.2f}/股 (溢价 {premium_rate*100:.1f}%)
  交易总额: J${total_cost:,.0f}

📊 整合效果:
  新增营收: J${target.metrics.revenue:,.0f} (+{((target.metrics.revenue/original_revenue)*100):.1f}%)
  保留员工: {acquired_employees}人 (保留率: {(acquired_employees/len(target.staff_list)*100):.1f}%)
  市场份额: +{target.metrics.market_share*0.8:.2f}%
  总员工数: {len(acquirer.staff_list)}人 (新增: {len(acquirer.staff_list)-original_employees}人)

💰 财务状况:
  交易后余额: J${acquirer.company_cash:,.0f}
  预期年化收益: J${target.metrics.profit*0.85:,.0f}
  投资回报周期: {(total_cost/(target.metrics.profit*0.85)):.1f}年

🏆 战略价值:
  • 实现规模经济效应
  • 扩大市场影响力
  • 获得{target.name}的核心资产和技术
  • 增强行业竞争优势

💡 建议: 关注整合期员工稳定性，优化业务流程实现协同效应
"""
        
        return True, completion_report
    
    def _calculate_synergy_value(self, acquirer, target) -> dict:
        """计算收购协同效应价值"""
        synergies = {}
        
        # 行业协同（同行业收购有更高协同效应）
        if acquirer.industry == target.industry:
            market_synergy = 0.15
            synergies['market_synergy'] = f"🏭 行业协同效应: +{market_synergy*100:.1f}% (同行业整合优势)"
        else:
            market_synergy = 0.08
            synergies['market_synergy'] = f"🔄 多元化效应: +{market_synergy*100:.1f}% (跨行业风险分散)"
        
        # 规模协同
        combined_revenue = acquirer.metrics.revenue + target.metrics.revenue
        scale_effect = min(0.12, combined_revenue / 100000000 * 0.02)  # 每亿营收增加2%效率，最高12%
        synergies['scale_effect'] = f"📈 规模经济: +{scale_effect*100:.1f}% (合并后营收: J${combined_revenue:,.0f})"
        
        # 员工协同（技能互补）
        staff_synergy = min(0.08, (len(acquirer.staff_list) + len(target.staff_list)) / 200 * 0.05)
        synergies['staff_synergy'] = f"👥 人才整合: +{staff_synergy*100:.1f}% (合并后团队: {len(acquirer.staff_list) + len(target.staff_list)}人)"
        
        # 市场协同
        market_power = (acquirer.metrics.market_share + target.metrics.market_share) * 0.003
        synergies['market_power'] = f"🎯 市场力量: +{market_power*100:.1f}% (合并市场份额: {(acquirer.metrics.market_share + target.metrics.market_share):.1f}%)"
        
        # 综合ROI估算
        total_synergy = market_synergy + scale_effect + staff_synergy + market_power
        synergies['expected_roi'] = total_synergy
        
        synergy_report = ""
        for key, value in synergies.items():
            if key != 'expected_roi':
                synergy_report += f"  {value}\n"
        
        synergy_report += f"  💎 综合协同价值: +{total_synergy*100:.1f}% ROI"
        
        return {'report': synergy_report, 'expected_roi': total_synergy}

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