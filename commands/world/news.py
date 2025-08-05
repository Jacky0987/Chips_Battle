from commands.base import Command
from dal.unit_of_work import SqlAlchemyUnitOfWork
from models.world.news import News

class NewsCommand(Command):
    name = "news"
    aliases = []
    description = "View recent news"

    def execute(self, *args):
        if args and args[0] == "search":
            # Search logic
            pass
        else:
            with SqlAlchemyUnitOfWork() as uow:
                recent_news = uow.session.query(News).order_by(News.timestamp.desc()).limit(10).all()
                # Format and print 