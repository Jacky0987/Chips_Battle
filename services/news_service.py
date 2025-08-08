from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func
from dal.database import get_session
from models.news.news import News
from models.stock.stock import Stock
from core.event_bus import EventBus, TimeTickEvent, NewsPublishedEvent
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

    async def on_time_tick(self, event: TimeTickEvent):
        """处理时间流逝事件，随机生成新闻"""
        # 每小时有20%概率生成新闻
        if random.random() < 0.2:
            await self._generate_random_news()

    def _load_news_templates(self) -> Dict[str, Any]:
        """加载新闻模板文件"""
        if self._templates_cache is None:
            templates_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'definitions', 'news_templates.json')
            with open(templates_file, 'r', encoding='utf-8') as f:
                self._templates_cache = json.load(f)
        return self._templates_cache
    
    async def _generate_random_news(self) -> Optional[News]:
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
        title = await self._fill_template(template['title'], news_type)
        content = await self._fill_template(template['content'], news_type)
        
        # 创建新闻
        news = await self._create_news(
            title=title,
            content=content,
            category=news_type,
            impact_type=template_group.get('impact_type', 'neutral'),
            impact_strength=template_group.get('impact_strength', 0.0)
        )
        
        return news
    
    async def _fill_template(self, template: str, news_type: str) -> str:
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
            stock = await self._get_random_stock()
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
    
    async def _get_random_stock(self) -> Optional[Stock]:
        """获取随机股票"""
        async with get_session() as session:
            result = await session.execute(select(Stock))
            stocks = result.scalars().all()
            return random.choice(stocks) if stocks else None
    
    async def _create_news(self, title: str, content: str, category: str, 
                    impact_type: str = 'neutral', impact_strength: float = 0.0) -> News:
        """创建新闻记录"""
        async with get_session() as session:
            async with session.begin():
                news = News(
                    title=title,
                    content=content,
                    category=category,
                    impact_type=impact_type,
                    impact_strength=Decimal(str(impact_strength)),
                    published_at=self.time_service.get_game_time().current_time
                )
                session.add(news)
                await session.flush()
                await session.refresh(news)
            
            # 发布新闻事件
            impact_tags = [f"{news.category}:{news.impact_type}"]
            await self.event_bus.publish(NewsPublishedEvent(
                news_id=news.id, 
                headline=news.title, 
                impact_tags=impact_tags, 
                severity=float(news.impact_strength)
            ))
            
            return news
    
    async def get_latest_news(self, limit: int = 10, category: Optional[str] = None) -> List[News]:
        """获取最新新闻"""
        async with get_session() as session:
            query = select(News)
            
            if category:
                query = query.filter_by(category=category)
            
            result = await session.execute(query.order_by(News.published_at.desc()).limit(limit))
            return result.scalars().all()
    
    async def get_news_by_id(self, news_id: int) -> Optional[News]:
        """根据ID获取新闻"""
        async with get_session() as session:
            result = await session.execute(select(News).filter_by(id=news_id))
            return result.scalars().first()
    
    async def get_market_impact_news(self, hours_back: int = 24) -> List[News]:
        """获取有市场影响的新闻"""
        cutoff_time = self.time_service.get_game_time().current_time - timedelta(hours=hours_back)
        
        async with get_session() as session:
            result = await session.execute(select(News).filter(
                News.published_at >= cutoff_time,
                News.impact_type != 'neutral'
            ).order_by(News.published_at.desc()))
            
            return result.scalars().all()
    
    async def create_manual_news(self, title: str, content: str, category: str = 'general',
                          impact_type: str = 'neutral', impact_strength: float = 0.0) -> News:
        """手动创建新闻"""
        return await self._create_news(title, content, category, impact_type, impact_strength)
    
    def get_news_categories(self) -> List[str]:
        """获取新闻分类列表"""
        templates = self._load_news_templates()
        return list(templates.get('templates', {}).keys())
    
    async def get_news_stats(self) -> Dict[str, Any]:
        """获取新闻统计信息"""
        async with get_session() as session:
            total_news_result = await session.execute(select(func.count(News.id)))
            total_news = total_news_result.scalar_one()
            
            # 按分类统计
            categories = {}
            for category in self.get_news_categories():
                count_result = await session.execute(select(func.count(News.id)).filter_by(category=category))
                categories[category] = count_result.scalar_one()
            
            # 最近24小时新闻数量
            recent_cutoff = self.time_service.get_game_time().current_time - timedelta(hours=24)
            recent_count_result = await session.execute(select(func.count(News.id)).filter(News.published_at >= recent_cutoff))
            recent_count = recent_count_result.scalar_one()
            
            return {
                'total_news': total_news,
                'categories': categories,
                'recent_24h': recent_count
            }