"""
JC公司管理器 - 统一管理所有公司相关业务
包括公司创建、管理、IPO、股票交易等
"""

import os
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from .company_types import JCCompany, CompanyType, IndustryCategory, CompanyStage, BusinessMetrics, CompanyFinancials, create_sample_companies
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
            
    def save_user_data(self):
        """保存用户数据"""
        try:
            # 保存用户的现金数据
            if hasattr(self.main_app, 'user_manager') and hasattr(self.main_app.user_manager, 'save_user_data'):
                self.main_app.user_manager.save_user_data(self.main_app.user_manager.current_user, self.main_app.cash)
        except Exception as e:
            print(f"保存用户数据失败: {e}")
    
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

    def evaluate_acquisition(self, target_id: str) -> Tuple[bool, str]:
        """评估收购价格 - 支持上市和未上市公司"""
        company = self.find_company_by_identifier(target_id)
        if not company:
            return False, "❌ 未找到指定公司"
        
        if company.created_by_user == self.main_app.user_manager.current_user:
            return False, "❌ 不能收购自己创建的公司"
        
        # 🔧 修复股本数据异常
        if company.is_public and company.shares_outstanding < 100000:
            # 股本异常小，自动修正为合理数值
            company.shares_outstanding = random.randint(50000000, 100000000)
            company.market_cap = company.stock_price * company.shares_outstanding
            self.save_companies()
        
        # 差异化估值计算
        if company.is_public:
            # 上市公司：市场估值 + 综合调整
            base_value = company.market_cap
            
            # 📊 综合估值调整因子
            financial_score = self._calculate_financial_score(company)
            premium_rate = 0.2 + (financial_score - 50) * 0.006  # 20%-50%基础溢价
            premium_rate = max(0.1, min(0.6, premium_rate))
            
            estimated_value = base_value * (1 + premium_rate)
            
            valuation_report = f"""
📊 上市公司收购估值 - {company.name} ({company.symbol})

💹 股票信息:
  当前股价: J${company.stock_price:.2f}
  总股本: {company.shares_outstanding:,}股
  市值: J${company.market_cap:,.0f}
  
💰 财务分析:
  总资产: J${company.metrics.assets:,.0f}
  净资产: J${company.metrics.calculate_equity():,.0f}
  年收入: J${company.metrics.revenue:,.0f}
  年利润: J${company.metrics.profit:,.0f}
  资产负债率: {company.metrics.debt_ratio*100:.1f}%
  净资产收益率: {company.metrics.calculate_roe()*100:.1f}%

📈 综合评估:
  财务评分: {financial_score:.1f}/100
  收购溢价: {premium_rate*100:.1f}%
  估值方法: 市场价值 + 财务调整
  收购价格: J${estimated_value:,.0f}

💡 收购建议: company acquire {target_id} {estimated_value:.0f}
"""
        else:
            # 未上市公司：财务指标估值
            revenue_multiple = self._get_industry_revenue_multiple(company.industry)
            profit_multiple = self._get_industry_profit_multiple(company.industry)
            
            # 多种估值方法
            revenue_valuation = company.metrics.revenue * revenue_multiple
            profit_valuation = max(0, company.metrics.profit * profit_multiple)
            asset_valuation = company.metrics.calculate_equity() * 1.2
            
            # 加权平均估值
            base_value = (revenue_valuation * 0.4 + profit_valuation * 0.4 + asset_valuation * 0.2)
            
            # 财务调整
            financial_score = self._calculate_financial_score(company)
            premium_rate = 0.25 + (financial_score - 50) * 0.007  # 25%-60%基础溢价
            premium_rate = max(0.15, min(0.7, premium_rate))
            
            estimated_value = base_value * (1 + premium_rate)
            
            valuation_report = f"""
📊 未上市公司收购估值 - {company.name}

💼 公司概况:
  行业分类: {company.industry.value.title()}
  发展阶段: {company.stage.value.title()}
  员工数量: {len(company.staff_list) if hasattr(company, 'staff_list') and company.staff_list else company.metrics.employees}人
  
💰 财务分析:
  年收入: J${company.metrics.revenue:,.0f}
  年利润: J${company.metrics.profit:,.0f}
  总资产: J${company.metrics.assets:,.0f}
  净资产: J${company.metrics.calculate_equity():,.0f}
  资产负债率: {company.metrics.debt_ratio*100:.1f}%
  
📊 估值分析:
  收入倍数法: J${revenue_valuation:,.0f} ({revenue_multiple:.1f}倍)
  利润倍数法: J${profit_valuation:,.0f} ({profit_multiple:.1f}倍)
  资产评估法: J${asset_valuation:,.0f}
  加权估值: J${base_value:,.0f}
  财务评分: {financial_score:.1f}/100
  收购溢价: {premium_rate*100:.1f}%
  最终价格: J${estimated_value:,.0f}

💡 收购建议: company acquire {target_id} {estimated_value:.0f}
"""
        
        return True, valuation_report

    def _calculate_financial_score(self, company) -> float:
        """计算公司财务评分 (0-100)"""
        score = 50  # 基础分
        
        # 盈利能力 (30分)
        if company.metrics.profit > 0:
            roe = company.metrics.calculate_roe()
            profit_score = min(roe * 300, 30)  # ROE每1%贡献3分，最多30分
            score += profit_score
        else:
            score -= 15  # 亏损扣分
        
        # 成长性 (25分)
        growth_score = min(company.metrics.growth_rate * 100, 25)
        score += growth_score
        
        # 财务健康度 (25分)
        if company.metrics.debt_ratio < 0.3:
            score += 15
        elif company.metrics.debt_ratio < 0.6:
            score += 10
        elif company.metrics.debt_ratio < 0.8:
            score += 5
        else:
            score -= 10
        
        # 市场地位 (10分)
        market_score = company.metrics.market_share * 200
        score += min(market_score, 10)
        
        # 资产效率 (10分)
        roa = company.metrics.calculate_roa()
        asset_score = min(roa * 100, 10)
        score += asset_score
        
        return max(0, min(100, score))

    def _get_industry_revenue_multiple(self, industry):
        """获取行业收入倍数"""
        industry_multiples = {
            IndustryCategory.TECHNOLOGY: random.uniform(8, 15),
            IndustryCategory.FINANCE: random.uniform(3, 8),
            IndustryCategory.HEALTHCARE: random.uniform(5, 12),
            IndustryCategory.ENERGY: random.uniform(2, 6),
            IndustryCategory.MANUFACTURING: random.uniform(1, 4),
            IndustryCategory.RETAIL: random.uniform(1, 3),
            IndustryCategory.REAL_ESTATE: random.uniform(4, 10),
            IndustryCategory.TRANSPORTATION: random.uniform(2, 5),
            IndustryCategory.TELECOMMUNICATIONS: random.uniform(3, 7),
            IndustryCategory.UTILITIES: random.uniform(2, 5),
            IndustryCategory.CONSUMER_GOODS: random.uniform(2, 6),
            IndustryCategory.AGRICULTURE: random.uniform(1, 3),
        }
        return industry_multiples.get(industry, random.uniform(2, 8))
    
    def _get_industry_profit_multiple(self, industry):
        """获取行业利润倍数"""
        industry_multiples = {
            IndustryCategory.TECHNOLOGY: random.uniform(20, 35),
            IndustryCategory.FINANCE: random.uniform(12, 25),
            IndustryCategory.HEALTHCARE: random.uniform(15, 30),
            IndustryCategory.ENERGY: random.uniform(8, 18),
            IndustryCategory.MANUFACTURING: random.uniform(10, 20),
            IndustryCategory.RETAIL: random.uniform(8, 15),
            IndustryCategory.REAL_ESTATE: random.uniform(12, 25),
            IndustryCategory.TRANSPORTATION: random.uniform(8, 15),
            IndustryCategory.TELECOMMUNICATIONS: random.uniform(10, 20),
            IndustryCategory.UTILITIES: random.uniform(10, 18),
            IndustryCategory.CONSUMER_GOODS: random.uniform(12, 22),
            IndustryCategory.AGRICULTURE: random.uniform(8, 15),
        }
        return industry_multiples.get(industry, random.uniform(10, 25))

    def sell_company(self, company_id: str, price: float = None) -> Tuple[bool, str]:
        """出售公司功能 - 增强版估值"""
        company = self.find_company_by_identifier(company_id)
        if not company:
            return False, "❌ 未找到指定公司"
        
        if company.created_by_user != self.main_app.user_manager.current_user:
            return False, "❌ 只能出售自己创建的公司"
        
        if price is None:
            # 显示估值报告
            # 🔧 修复股本数据异常
            if company.is_public and company.shares_outstanding < 100000:
                company.shares_outstanding = random.randint(50000000, 100000000)
                company.market_cap = company.stock_price * company.shares_outstanding
                self.save_companies()
            
            if company.is_public:
                # 上市公司出售估值
                base_value = company.market_cap
                premium = base_value * 0.1  # 10%溢价
                estimated_value = base_value + premium
                
                # 员工遣散费计算
                staff_count = len(company.staff_list) if hasattr(company, 'staff_list') and company.staff_list else 0
                severance_cost = staff_count * 50000
                
                net_proceeds = estimated_value - severance_cost
                
                report = f"""
📊 公司出售估值报告 - {company.name}

💰 资产评估:
  上市状态: 📈 已上市
  估值方法: 市场估值 + 综合分析
  
💹 股票信息:
  股价: J${company.stock_price:.2f}每股
  总股本: {company.shares_outstanding:,}股
  市值: J${company.market_cap:,.0f}
  
💼 财务状况:
  总资产: J${company.metrics.assets:,.0f}
  总负债: J${company.metrics.liabilities:,.0f}
  净资产: J${company.metrics.calculate_equity():,.0f}
  年收入: J${company.metrics.revenue:,.0f}
  年利润: J${company.metrics.profit:,.0f}
  现金储备: J${company.company_cash:,.0f}

👥 人力资源:
  员工数量: {staff_count}人
  员工遣散费: J${severance_cost:,.0f} (每人5万)

🎯 估算价值:
  市值: J${base_value:,.0f}
  市场溢价: J${premium:,.0f}
  总估值: J${estimated_value:,.0f}
  员工补偿: -J${severance_cost:,.0f}
  实际收益: J${net_proceeds:,.0f}

📋 出售方式:
  1. 市场出售 (推荐价格): company sell {company_id} {estimated_value:.0f}
  2. 快速出售 (85%价格): company sell {company_id} {estimated_value * 0.85:.0f}
  3. 自定义价格: company sell {company_id} <您的报价>

⚠️  注意: 出售公司后将无法撤销，请慎重考虑！
"""
            else:
                # 未上市公司出售估值
                revenue_multiple = self._get_industry_revenue_multiple(company.industry)
                profit_multiple = self._get_industry_profit_multiple(company.industry)
                
                revenue_valuation = company.metrics.revenue * revenue_multiple
                profit_valuation = max(0, company.metrics.profit * profit_multiple)
                asset_valuation = company.metrics.calculate_equity()
                
                # 综合估值
                base_value = (revenue_valuation * 0.4 + profit_valuation * 0.3 + asset_valuation * 0.3)
                premium = base_value * 0.15  # 15%溢价
                estimated_value = base_value + premium
                
                # 员工遣散费
                staff_count = len(company.staff_list) if hasattr(company, 'staff_list') and company.staff_list else 0
                severance_cost = staff_count * 50000
                
                net_proceeds = estimated_value - severance_cost
                
                report = f"""
📊 公司出售估值报告 - {company.name}

💰 资产评估:
  上市状态: 🔒 未上市
  估值方法: 财务指标估值
  
💼 财务状况:
  年收入: J${company.metrics.revenue:,.0f}
  年利润: J${company.metrics.profit:,.0f}
  总资产: J${company.metrics.assets:,.0f}
  净资产: J${company.metrics.calculate_equity():,.0f}
  现金储备: J${company.company_cash:,.0f}

📊 估值分析:
  收入倍数法: J${revenue_valuation:,.0f} ({revenue_multiple:.1f}倍)
  利润倍数法: J${profit_valuation:,.0f} ({profit_multiple:.1f}倍)
  资产评估法: J${asset_valuation:,.0f}
  综合估值: J${base_value:,.0f}
  出售溢价: J${premium:,.0f}

👥 人力资源:
  员工数量: {staff_count}人
  员工遣散费: J${severance_cost:,.0f}

🎯 最终估值:
  出售价格: J${estimated_value:,.0f}
  员工补偿: -J${severance_cost:,.0f}
  实际收益: J${net_proceeds:,.0f}

📋 出售方式:
  1. 推荐价格: company sell {company_id} {estimated_value:.0f}
  2. 快速出售: company sell {company_id} {estimated_value * 0.85:.0f}
  3. 自定义价格: company sell {company_id} <您的报价>
"""
            
            return True, report
        else:
            # 执行出售
            # 🔧 修复股本数据异常
            if company.is_public and company.shares_outstanding < 100000:
                company.shares_outstanding = random.randint(50000000, 100000000)
                company.market_cap = company.stock_price * company.shares_outstanding
            
            if company.is_public:
                market_value = company.market_cap
                reasonable_min = market_value * 0.5
                reasonable_max = market_value * 1.5
            else:
                estimated_value = company.metrics.calculate_equity()
                reasonable_min = estimated_value * 0.5
                reasonable_max = estimated_value * 1.5
            
            if price < reasonable_min or price > reasonable_max:
                return False, f"❌ 出售价格不合理，建议范围: J${reasonable_min:,.0f} - J${reasonable_max:,.0f}"
            
            # 计算员工遣散费
            staff_count = len(company.staff_list) if hasattr(company, 'staff_list') and company.staff_list else 0
            severance_cost = staff_count * 50000
            
            # 检查是否足够支付遣散费
            if price < severance_cost:
                return False, f"❌ 出售价格不足以支付员工遣散费 J${severance_cost:,.0f}"
            
            # 执行出售
            net_proceeds = price - severance_cost
            self.main_app.cash += net_proceeds
            
            # 从用户公司列表中移除
            self.user_companies[self.main_app.user_manager.current_user].remove(company.company_id)
            
            # 生成出售新闻
            if company.is_public:
                news = f"{company.name}被收购，交易价格 J${price:,.0f}"
                company.generate_news_event()
            
            # 保存数据
            self.save_companies()
            self.save_user_data()
            
            return True, f"✅ 成功出售 {company.name}，获得收益 J${net_proceeds:,.0f}（已扣除员工遣散费 J${severance_cost:,.0f}）"

    def delist_company(self, company_id: str) -> Tuple[bool, str]:
        """撤回IPO退市功能"""
        company = self.find_company_by_identifier(company_id)
        if not company:
            return False, "❌ 未找到指定公司"
        
        if company.created_by_user != self.main_app.user_manager.current_user:
            return False, "❌ 只能操作自己创建的公司"
        
        if not company.is_public:
            return False, "❌ 公司尚未上市，无需退市"
        
        # 计算退市成本和影响
        # 股东补偿：按当前市值的80%退还
        shareholder_compensation = company.market_cap * 0.8
        
        # 退市费用：法律费用、监管费用等
        delisting_cost = company.market_cap * 0.05  # 5%的退市费用
        
        # 总成本
        total_cost = shareholder_compensation + delisting_cost
        
        # 检查公司资金是否充足
        available_funds = company.company_cash + company.metrics.calculate_equity()
        
        if available_funds < total_cost:
            return False, f"""❌ 退市资金不足
💰 退市成本分析:
  股东补偿: J${shareholder_compensation:,.0f} (市值80%)
  退市费用: J${delisting_cost:,.0f} (市值5%)
  总成本: J${total_cost:,.0f}
  可用资金: J${available_funds:,.0f}
  资金缺口: J${total_cost - available_funds:,.0f}

💡 建议: 先向公司注资或提高公司盈利能力"""
        
        # 预览退市影响
        report = f"""
📋 退市预览 - {company.name} ({company.symbol})

💹 当前上市状态:
  股价: J${company.stock_price:.2f}
  股本: {company.shares_outstanding:,}股
  市值: J${company.market_cap:,.0f}
  IPO日期: {company.ipo_date[:10] if company.ipo_date else 'N/A'}

💰 退市成本:
  股东补偿: J${shareholder_compensation:,.0f}
  退市费用: J${delisting_cost:,.0f}
  总成本: J${total_cost:,.0f}

📊 退市后状态:
  公司类型: 私人公司
  估值方式: 财务指标估值
  股票交易: 停止
  
⚠️  退市影响:
  • 失去公开市场流动性
  • 融资渠道受限
  • 监管要求降低
  • 估值可能下降

确认退市请输入: company delist {company_id} confirm
"""
        
        return True, report

    def confirm_delist_company(self, company_id: str) -> Tuple[bool, str]:
        """确认执行退市"""
        company = self.find_company_by_identifier(company_id)
        if not company or not company.is_public:
            return False, "❌ 公司状态异常"
        
        if company.created_by_user != self.main_app.user_manager.current_user:
            return False, "❌ 只能操作自己创建的公司"
        
        # 计算成本
        shareholder_compensation = company.market_cap * 0.8
        delisting_cost = company.market_cap * 0.05
        total_cost = shareholder_compensation + delisting_cost
        
        # 执行退市
        company.is_public = False
        company.stock_price = 0.0
        old_shares = company.shares_outstanding
        company.shares_outstanding = 0
        company.market_cap = 0.0
        from company.company_types import CompanyType
        company.company_type = CompanyType.PRIVATE
        
        # 扣除退市成本
        company.company_cash -= total_cost
        company.metrics.assets -= total_cost
        
        # 生成退市新闻
        company.generate_news_event('management')
        
        # 保存数据
        self.save_companies()
        
        return True, f"""✅ {company.name} 成功退市
        
📊 退市完成:
  原股本: {old_shares:,}股
  补偿金额: J${shareholder_compensation:,.0f}
  退市费用: J${delisting_cost:,.0f}
  公司余额: J${company.company_cash:,.0f}
  
💼 公司现状:
  类型: 私人公司
  员工: {len(company.staff_list) if hasattr(company, 'staff_list') and company.staff_list else 0}人
  资产: J${company.metrics.assets:,.0f}
"""

    def secondary_offering(self, company_id: str, offering_price: float, shares_to_issue: int) -> Tuple[bool, str]:
        """股票增发功能 - 增强版"""
        company = self.find_company_by_identifier(company_id)
        if not company:
            return False, "❌ 未找到指定公司"
        
        if company.created_by_user != self.main_app.user_manager.current_user:
            return False, "❌ 只能操作自己创建的公司"
        
        if not company.is_public:
            return False, "❌ 公司尚未上市，无法进行股票增发"
        
        # 🔧 修复股本数据异常
        if company.shares_outstanding < 100000:
            company.shares_outstanding = random.randint(50000000, 100000000)
            company.market_cap = company.stock_price * company.shares_outstanding
            self.save_companies()
        
        # 价格控制：不能偏离市价±50%
        price_lower = company.stock_price * 0.5
        price_upper = company.stock_price * 1.5
        if offering_price < price_lower or offering_price > price_upper:
            return False, f"""❌ 增发价格偏离市场价过多
  当前股价: J${company.stock_price:.2f}
  建议价格区间: J${price_lower:.2f} - J${price_upper:.2f}
  您的价格: J${offering_price:.2f}"""
        
        # 股本限制：单次增发不超过现有股本50%
        max_issuance = int(company.shares_outstanding * 0.5)
        if shares_to_issue > max_issuance:
            return False, f"""❌ 增发股数过多
  现有股本: {company.shares_outstanding:,}股
  最大增发: {max_issuance:,}股 (现有股本的50%)
  您的增发: {shares_to_issue:,}股"""
        
        if shares_to_issue <= 0:
            return False, "❌ 增发股数必须大于0"
        
        # 计算募集资金
        proceeds = offering_price * shares_to_issue
        
        # 计算股价稀释效应
        old_market_cap = company.market_cap
        new_total_shares = company.shares_outstanding + shares_to_issue
        
        # 新市值 = 原市值 + 募集资金（部分反映市场信心）
        market_confidence = random.uniform(0.7, 1.0)  # 市场对增发的信心
        new_market_cap = old_market_cap + (proceeds * market_confidence)
        new_stock_price = new_market_cap / new_total_shares
        
        # 执行增发
        company.shares_outstanding = new_total_shares
        company.stock_price = new_stock_price
        company.market_cap = new_market_cap
        company.company_cash += proceeds
        company.metrics.assets += proceeds
        
        # 生成增发新闻
        news_content = f"{company.name}完成股票增发，发行{shares_to_issue:,}股，募集资金J${proceeds:,.0f}"
        company.generate_news_event('management')
        
        # 保存数据
        self.save_companies()
        
        # 计算稀释影响
        dilution_effect = (company.stock_price - offering_price) / offering_price * 100
        
        return True, f"""✅ 股票增发完成 - {company.name}

📊 增发详情:
  增发价格: J${offering_price:.2f}/股
  增发数量: {shares_to_issue:,}股
  募集资金: J${proceeds:,.0f}

💹 股本变化:
  原股本: {company.shares_outstanding - shares_to_issue:,}股
  新股本: {company.shares_outstanding:,}股
  增加比例: {shares_to_issue/(company.shares_outstanding - shares_to_issue)*100:.1f}%

📈 价格影响:
  增发前股价: J${old_market_cap/(company.shares_outstanding - shares_to_issue):.2f}
  增发后股价: J${company.stock_price:.2f}
  稀释效应: {dilution_effect:+.1f}%
  新市值: J${company.market_cap:,.0f}

💰 资金状况:
  募集资金: J${proceeds:,.0f}
  公司现金: J${company.company_cash:,.0f}
  总资产: J${company.metrics.assets:,.0f}

📰 市场反应: {news_content}
"""

    def get_company_detail(self, company_id: str) -> Tuple[bool, str]:
        """获取公司详细信息 - 全面展示"""
        company = self.find_company_by_identifier(company_id)
        if not company:
            return False, "❌ 未找到指定公司"
        
        # 🔧 修复股本数据异常
        if company.is_public and company.shares_outstanding < 100000:
            company.shares_outstanding = random.randint(50000000, 100000000)
            company.market_cap = company.stock_price * company.shares_outstanding
            self.save_companies()
        
        # 基础信息
        detail_info = f"""
🏢 {company.name} ({company.symbol}) - 详细信息

📋 基本信息:
  公司ID: {company.company_id}
  行业分类: {company.industry.value.title()}
  公司类型: {company.company_type.value.title()}
  发展阶段: {company.stage.value.title()}
  成立时间: {company.founded_date}
  总部地址: {company.headquarters}
  网站: {company.website}
  首席执行官: {company.ceo_name}
  创建者: {company.created_by_user or '系统'}
  更新时间: {company.last_updated[:19] if company.last_updated else 'N/A'}

💰 财务状况:
  营业收入: J${company.metrics.revenue:,.0f}
  净利润: J${company.metrics.profit:,.0f}
  总资产: J${company.metrics.assets:,.0f}
  总负债: J${company.metrics.liabilities:,.0f}
  净资产: J${company.metrics.calculate_equity():,.0f}
  公司现金: J${company.company_cash:,.0f}
  累计投资: J${company.total_investment:,.0f}

📊 经营指标:
  营收增长率: {company.metrics.growth_rate*100:+.1f}%
  净资产收益率: {company.metrics.calculate_roe()*100:.1f}%
  总资产收益率: {company.metrics.calculate_roa()*100:.1f}%
  资产负债率: {company.metrics.debt_ratio*100:.1f}%
  市场份额: {company.metrics.market_share*100:.2f}%
"""
        
        # 人力资源详情
        staff_count = len(company.staff_list) if hasattr(company, 'staff_list') and company.staff_list else 0
        if staff_count > 0:
            total_salary = sum(staff['salary'] for staff in company.staff_list)
            avg_salary = total_salary / staff_count if staff_count > 0 else 0
            
            # 按职位统计
            position_stats = {}
            for staff in company.staff_list:
                pos = staff['position']
                if pos not in position_stats:
                    position_stats[pos] = {'count': 0, 'total_salary': 0}
                position_stats[pos]['count'] += 1
                position_stats[pos]['total_salary'] += staff['salary']
            
            hr_info = f"""
👥 人力资源 ({staff_count}/{company.max_staff}):
  员工总数: {staff_count}人
  月薪总额: J${total_salary:,.0f}
  平均薪资: J${avg_salary:,.0f}
  年薪成本: J${total_salary * 12:,.0f}

📊 职位分布:"""
            for pos, data in position_stats.items():
                avg_pos_salary = data['total_salary'] / data['count']
                hr_info += f"\n  • {pos}: {data['count']}人，平均薪资 J${avg_pos_salary:,.0f}"
        else:
            hr_info = f"""
👥 人力资源 (0/{company.max_staff}):
  员工总数: 0人
  💡 提示: 使用 'company hire' 命令招聘员工"""
        
        detail_info += hr_info
        
        # 股票信息（如果上市）
        if company.is_public:
            pe_ratio = company.calculate_pe_ratio()
            pb_ratio = company.calculate_pb_ratio()
            
            pe_display = f"{pe_ratio:.1f}" if pe_ratio is not None else "N/A"
            pb_display = f"{pb_ratio:.1f}" if pb_ratio is not None else "N/A"
            
            stock_info = f"""

💹 股票信息:
  上市状态: ✅ 已上市
  当前股价: J${company.stock_price:.2f}
  总股本: {company.shares_outstanding:,}股
  流通市值: J${company.market_cap:,.0f}
  IPO价格: J${company.ipo_price:.2f}
  IPO日期: {company.ipo_date[:10] if company.ipo_date else 'N/A'}
  股价涨跌: {((company.stock_price - company.ipo_price) / company.ipo_price * 100):+.1f}%
  市盈率(PE): {pe_display}倍
  市净率(PB): {pb_display}倍
"""
        else:
            can_ipo, ipo_msg = company.can_go_public()
            stock_info = f"""

🔒 股票信息:
  上市状态: ❌ 未上市
  IPO条件: {'✅ 满足' if can_ipo else '❌ 不满足'}
  限制原因: {ipo_msg if not can_ipo else '可申请IPO'}
  预估价值: J${company.metrics.calculate_equity():,.0f}
"""
        
        detail_info += stock_info
        
        # 投资评级
        rating, grade = company.get_investment_rating()
        detail_info += f"""
📊 投资评级:
  综合评分: {company.performance_score:.1f}/100
  投资建议: {rating} ({grade})
  风险等级: {'⭐' * company.risk_level} ({company.risk_level}/5)
"""
        
        # 最近新闻
        if company.news_events:
            recent_news = sorted(company.news_events, key=lambda x: x.publish_date, reverse=True)[:3]
            detail_info += "\n📰 最近新闻:\n"
            for i, news in enumerate(recent_news, 1):
                impact_icon = "📈" if news.impact_type == "positive" else "📉" if news.impact_type == "negative" else "📊"
                detail_info += f"  {i}. {impact_icon} {news.title}\n"
                detail_info += f"     {news.publish_date[:10]} | {news.category.title()}\n"
        
        # 操作建议
        detail_info += f"""
💡 可用操作:
  📊 财务: company invest {company_id} <金额> (注资)
  👥 人事: company hire {company_id} (招聘) | company expand {company_id} (扩张)"""
        
        if company.created_by_user == self.main_app.user_manager.current_user:
            if company.is_public:
                detail_info += f"""
  💹 股票: company offering {company_id} <价格> <股数> (增发)
  📤 退出: company delist {company_id} (退市) | company sell {company_id} (出售)"""
            else:
                can_ipo, _ = company.can_go_public()
                if can_ipo:
                    detail_info += f"\n  🚀 上市: company ipo {company_id} <价格> <股数>"
                detail_info += f"\n  📤 退出: company sell {company_id} (出售)"
        
        return True, detail_info

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