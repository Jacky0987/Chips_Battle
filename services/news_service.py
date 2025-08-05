import json
import random
from datetime import datetime
from core.event_bus import EventBus
from dal.unit_of_work import SqlAlchemyUnitOfWork
from models.world.news import News

class NewsService:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.templates = self.load_templates()
        event_bus.subscribe("TimeTickEvent", self.generate_news)

    def load_templates(self):
        with open('data/definitions/news_templates.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_news(self, data):
        if random.random() < 0.3:  # 30% 概率生成新闻
            template = random.choice(self.templates)
            # Fill placeholders (simplified)
            headline = template["template"].format(company_name="ExampleCorp", region_name="ExampleRegion")
            news = News(
                headline=headline,
                content="Detailed content...",
                timestamp=datetime.now(),
                source="Reuters",
                impact_tags=template["impact_tags"]
            )
            with SqlAlchemyUnitOfWork() as uow:
                uow.session.add(news)
                uow.commit()
            self.event_bus.publish("NewsPublishedEvent", news) 