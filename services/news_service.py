from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dal.database import get_session
from models.news.news import News
from models.stock.stock import Stock
from core.event_bus import EventBus, TimeTickEvent
from services.time_service import TimeService
import json
import os
import random
from decimal import Decimal

class NewsService:
    """新闻服务，管理动态新闻生成和发布"""
    
    def __init__(self, event_bus: EventBus, time_service: TimeService):
        self.event_bus = event_bus
        self.time_service = time_service
        self._templates_cache = None
        self.event_bus.subscribe(TimeTickEvent, self.on_time_tick)

    def on_time_tick(self, event: TimeTickEvent):
        """处理时间流逝事件，随机生成新闻"""
        # 每小时有20%概率生成新闻
        if random.random() < 0.2:
            self._generate_random_news()

    def _load_news_templates(self) -> Dict[str, Any]:
        """加载新闻模板文件"""
        if self._templates_cache is None:
            templates_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'definitions', 'news_templates.json')
            with open(templates_file, 'r', encoding='utf-8') as f:
                self._templates_cache = json.load(f)
        return self._templates_cache
    
    def _generate_random_news(self) -> Optional[News]:
        """生成随机新闻"""
        templates = self._load_news_templates()
        news_types = list(templates['templates'].keys())
        
        if not news_types:
            return None
        
        news_type = random.choice(news_types)
        template_group = templates['templates'][news_type]
        
        # 随机选择模板
        template = random.choice(template_group['templates'])
        
        # 生成新闻内容
        title = self._fill_template(template['title'], news_type)
        content = self._fill_template(template['content'], news_type)
        
        # 创建新闻
        news = self._create_news(
            title=title,
            content=content,
            category=news_type,
            impact_type=template_group.get('impact_type', 'neutral'),
            impact_strength=template_group.get('impact_strength', 0.0)
        )
        
        return news
    
    def _fill_template(self, template: str, news_type: str) -> str:
        """填充新闻模板"""
        templates = self._load_news_templates()
        variables = templates.get('variables', {})
        
        # 替换变量
        for var_name, var_values in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in template:
                value = random.choice(var_values)
                template = template.replace(placeholder, value)
        
        # 替换股票相关变量
        if '{stock_name}' in template or '{ticker}' in template:
            stock = self._get_random_stock()
            if stock:
                template = template.replace('{stock_name}', stock.name)
                template = template.replace('{ticker}', stock.ticker)
        
        # 替换价格变化
        if '{price_change}' in template:
            change = random.uniform(-10.0, 10.0)
            template = template.replace('{price_change}', f"{change:.2f}%")
        
        # 替换数值
        if '{amount}' in template:
            amount = random.randint(100, 10000)
            template = template.replace('{amount}', str(amount))
        
        return template
    
    def _get_random_stock(self) -> Optional[Stock]:
        """获取随机股票"""
        with get_session() as session:
            stocks = session.query(Stock).all()
            return random.choice(stocks) if stocks else None
    
    def _create_news(self, title: str, content: str, category: str, 
                    impact_type: str = 'neutral', impact_strength: float = 0.0) -> News:
        """创建新闻记录"""
        with get_session() as session:
            news = News(
                title=title,
                content=content,
                category=category,
                impact_type=impact_type,
                impact_strength=Decimal(str(impact_strength)),
                published_at=self.time_service.get_current_time()
            )
            session.add(news)
            session.commit()
            session.refresh(news)
            
            # 发布新闻事件
            self.event_bus.publish('news_published', {
                'news_id': news.id,
                'title': news.title,
                'category': news.category,
                'impact_type': news.impact_type,
                'impact_strength': float(news.impact_strength)
            })
            
            return news
    
    def get_latest_news(self, limit: int = 10, category: Optional[str] = None) -> List[News]:
        """获取最新新闻"""
        with get_session() as session:
            query = session.query(News)
            
            if category:
                query = query.filter_by(category=category)
            
            news_list = query.order_by(News.published_at.desc()).limit(limit).all()
            return news_list
    
    def get_news_by_id(self, news_id: int) -> Optional[News]:
        """根据ID获取新闻"""
        with get_session() as session:
            return session.query(News).filter_by(id=news_id).first()
    
    def get_market_impact_news(self, hours_back: int = 24) -> List[News]:
        """获取有市场影响的新闻"""
        cutoff_time = self.time_service.get_current_time() - timedelta(hours=hours_back)
        
        with get_session() as session:
            news_list = session.query(News).filter(
                News.published_at >= cutoff_time,
                News.impact_type != 'neutral'
            ).order_by(News.published_at.desc()).all()
            
            return news_list
    
    def create_manual_news(self, title: str, content: str, category: str = 'general',
                          impact_type: str = 'neutral', impact_strength: float = 0.0) -> News:
        """手动创建新闻"""
        return self._create_news(title, content, category, impact_type, impact_strength)
    
    def get_news_categories(self) -> List[str]:
        """获取新闻分类列表"""
        templates = self._load_news_templates()
        return list(templates.get('templates', {}).keys())
    
    def get_news_stats(self) -> Dict[str, Any]:
        """获取新闻统计信息"""
        with get_session() as session:
            total_news = session.query(News).count()
            
            # 按分类统计
            categories = {}
            for category in self.get_news_categories():
                count = session.query(News).filter_by(category=category).count()
                categories[category] = count
            
            # 最近24小时新闻数量
            recent_cutoff = self.time_service.get_current_time() - timedelta(hours=24)
            recent_count = session.query(News).filter(News.published_at >= recent_cutoff).count()
            
            return {
                'total_news': total_news,
                'categories': categories,
                'recent_24h': recent_count
            }