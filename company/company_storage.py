"""
公司数据存储管理器
专门处理JC公司的持久化存储和加载
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .company_types import JCCompany, CompanyType, IndustryCategory, CompanyStage, BusinessMetrics, CompanyFinancials, CompanyNews


class CompanyStorageManager:
    """公司数据存储管理器"""
    
    def __init__(self, data_path: str = "data/jc_companies.json"):
        self.data_path = data_path
        self.backup_path = data_path.replace(".json", "_backup.json")
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """确保数据目录存在"""
        data_dir = os.path.dirname(self.data_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
    
    def save_companies(self, companies: Dict[str, JCCompany], user_companies: Dict[str, List[str]]) -> bool:
        """保存公司数据"""
        try:
            # 备份当前文件
            self._create_backup()
            
            # 准备数据
            save_data = {
                'version': '2.0',
                'last_updated': datetime.now().isoformat(),
                'companies': [self._company_to_dict(company) for company in companies.values()],
                'user_companies': user_companies,
                'statistics': self._generate_statistics(companies),
            }
            
            # 原子写入
            temp_path = self.data_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            # 替换原文件
            if os.path.exists(self.data_path):
                os.replace(temp_path, self.data_path)
            else:
                os.rename(temp_path, self.data_path)
            
            return True
            
        except Exception as e:
            print(f"保存公司数据失败: {e}")
            # 尝试恢复备份
            self._restore_backup()
            return False
    
    def load_companies(self) -> Tuple[Dict[str, JCCompany], Dict[str, List[str]]]:
        """加载公司数据"""
        companies = {}
        user_companies = {}
        
        try:
            if not os.path.exists(self.data_path):
                print("公司数据文件不存在，将创建新数据")
                return companies, user_companies
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查数据版本
            version = data.get('version', '1.0')
            if version != '2.0':
                print(f"检测到旧版本数据 ({version})，正在迁移...")
                companies, user_companies = self._migrate_data(data)
            else:
                # 加载公司数据
                for company_data in data.get('companies', []):
                    try:
                        company = self._dict_to_company(company_data)
                        companies[company.company_id] = company
                    except Exception as e:
                        print(f"加载公司 {company_data.get('company_id', 'unknown')} 失败: {e}")
                        continue
                
                user_companies = data.get('user_companies', {})
            
            print(f"成功加载 {len(companies)} 家公司，{len(user_companies)} 个用户记录")
            
        except json.JSONDecodeError as e:
            print(f"数据文件格式错误: {e}")
            # 尝试加载备份
            return self._load_backup()
        except Exception as e:
            print(f"加载公司数据失败: {e}")
            return companies, user_companies
        
        return companies, user_companies
    
    def _company_to_dict(self, company: JCCompany) -> Dict:
        """将公司对象转换为字典"""
        return {
            # 基础信息
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
            
            # 经营数据
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
            
            # 财务数据
            'financials': {
                'quarterly_reports': company.financials.quarterly_reports,
                'annual_reports': company.financials.annual_reports,
                'cash_flow': company.financials.cash_flow,
                'balance_sheet': company.financials.balance_sheet,
                'income_statement': company.financials.income_statement
            },
            
            # 公司账户
            'company_cash': company.company_cash,
            'total_investment': company.total_investment,
            
            # 员工系统
            'staff_list': company.staff_list,
            'max_staff': company.max_staff,
            
            # 股票信息
            'is_public': company.is_public,
            'stock_price': company.stock_price,
            'shares_outstanding': company.shares_outstanding,
            'market_cap': company.market_cap,
            'ipo_price': company.ipo_price,
            'ipo_date': company.ipo_date,
            
            # 动态数据
            'news_events': [
                {
                    'news_id': news.news_id,
                    'title': news.title,
                    'content': news.content,
                    'impact_type': news.impact_type,
                    'impact_magnitude': news.impact_magnitude,
                    'publish_date': news.publish_date,
                    'category': news.category
                } for news in company.news_events
            ],
            'performance_score': company.performance_score,
            'risk_level': company.risk_level,
            
            # 游戏相关
            'created_by_user': company.created_by_user,
            'last_updated': company.last_updated
        }
    
    def _dict_to_company(self, data: Dict) -> JCCompany:
        """将字典转换为公司对象"""
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
            company_cash=data.get('company_cash', 0.0),
            total_investment=data.get('total_investment', 0.0),
            staff_list=data.get('staff_list', []),
            max_staff=data.get('max_staff', 500),
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
    
    def _create_backup(self):
        """创建备份文件"""
        try:
            if os.path.exists(self.data_path):
                import shutil
                shutil.copy2(self.data_path, self.backup_path)
        except Exception as e:
            print(f"创建备份失败: {e}")
    
    def _restore_backup(self):
        """恢复备份文件"""
        try:
            if os.path.exists(self.backup_path):
                import shutil
                shutil.copy2(self.backup_path, self.data_path)
                print("已恢复备份数据")
        except Exception as e:
            print(f"恢复备份失败: {e}")
    
    def _load_backup(self) -> Tuple[Dict[str, JCCompany], Dict[str, List[str]]]:
        """加载备份数据"""
        try:
            if os.path.exists(self.backup_path):
                print("尝试加载备份数据...")
                with open(self.backup_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return self._migrate_data(data)
        except Exception as e:
            print(f"加载备份数据失败: {e}")
        
        return {}, {}
    
    def _migrate_data(self, old_data: Dict) -> Tuple[Dict[str, JCCompany], Dict[str, List[str]]]:
        """迁移旧版本数据"""
        companies = {}
        user_companies = old_data.get('user_companies', {})
        
        for company_data in old_data.get('companies', []):
            try:
                # 补充缺失的字段
                if 'company_cash' not in company_data:
                    company_data['company_cash'] = 0.0
                if 'total_investment' not in company_data:
                    company_data['total_investment'] = 0.0
                if 'staff_list' not in company_data:
                    company_data['staff_list'] = []
                if 'max_staff' not in company_data:
                    company_data['max_staff'] = 500
                
                company = self._dict_to_company(company_data)
                companies[company.company_id] = company
            except Exception as e:
                print(f"迁移公司数据失败: {e}")
                continue
        
        print(f"数据迁移完成，迁移了 {len(companies)} 家公司")
        return companies, user_companies
    
    def _generate_statistics(self, companies: Dict[str, JCCompany]) -> Dict:
        """生成统计信息"""
        if not companies:
            return {}
        
        public_companies = [c for c in companies.values() if c.is_public]
        total_market_cap = sum(c.market_cap for c in public_companies)
        
        industry_stats = {}
        for company in companies.values():
            industry = company.industry.value
            if industry not in industry_stats:
                industry_stats[industry] = 0
            industry_stats[industry] += 1
        
        return {
            'total_companies': len(companies),
            'public_companies': len(public_companies),
            'total_market_cap': total_market_cap,
            'industry_distribution': industry_stats,
            'generated_at': datetime.now().isoformat()
        }
    
    def export_company_data(self, company_id: str, companies: Dict[str, JCCompany]) -> Optional[str]:
        """导出单个公司数据"""
        if company_id not in companies:
            return None
        
        try:
            company = companies[company_id]
            export_data = self._company_to_dict(company)
            
            export_path = f"data/exports/company_{company_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return export_path
            
        except Exception as e:
            print(f"导出公司数据失败: {e}")
            return None
    
    def import_company_data(self, file_path: str) -> Optional[JCCompany]:
        """导入公司数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            company = self._dict_to_company(data)
            return company
            
        except Exception as e:
            print(f"导入公司数据失败: {e}")
            return None 