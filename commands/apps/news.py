from commands.base import AppCommand, CommandResult, CommandContext
from services.news_service import NewsService
from typing import Dict, Any

class NewsCommand(AppCommand):
    """新闻命令 - 获取和显示新闻信息"""
    
    @property
    def name(self) -> str:
        return "news"
    
    @property
    def description(self) -> str:
        return "新闻命令 - 查看市场新闻和动态"
    
    @property
    def aliases(self) -> list[str]:
        return ["headlines", "info", "updates"]
    
    def __init__(self, news_service: NewsService):
        super().__init__()
        self.news_service = news_service
    
    async def execute(self, args: list, context: CommandContext) -> CommandResult:
        if not args:
            return self._show_latest_news()
        
        subcommand = args[0].lower()
        
        if subcommand == 'help':
            return self.format_success("新闻命令帮助\n\n用法:\n  news                         - 显示最新新闻\n  news latest [数量]           - 显示最新新闻 (默认10条)\n  news view <ID>               - 查看新闻详情\n  news market                  - 显示有市场影响的新闻\n  news categories              - 显示新闻分类\n  news sources                 - 显示新闻来源\n  news category <分类>         - 按分类查看新闻\n  news search <关键词>         - 搜索新闻\n  news stats                   - 显示新闻统计")
        elif subcommand == 'latest':
            limit = int(args[1]) if len(args) > 1 else 10
            return self._show_latest_news(limit)
        elif subcommand == 'view':
            if len(args) < 2:
                return self.format_error("用法: news view <新闻ID>")
            try:
                news_id = int(args[1])
                return self._view_news_detail(news_id)
            except ValueError:
                return self.format_error("新闻ID必须是数字")
        elif subcommand == 'market':
            return self._show_market_news()
        elif subcommand == 'categories':
            return self._show_categories()
        elif subcommand == 'sources':
            return self._show_sources()
        elif subcommand in ['tech', 'finance', 'sports', 'politics']:
            count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 5
            return self._show_news_by_category(subcommand, count)
        elif subcommand == 'category':
            if len(args) < 2:
                return self.format_error("用法: news category <分类名>")
            category = args[1]
            return self._show_news_by_category(category)
        elif subcommand == 'source':
            if len(args) < 2:
                return self.format_error("用法: news source <来源> [数量]")
            source = args[1]
            count = int(args[2]) if len(args) > 2 and args[2].isdigit() else 5
            return self._show_news_by_source(source, count)
        elif subcommand == 'search':
            if len(args) < 2:
                return self.format_error("用法: news search <关键词>")
            keyword = ' '.join(args[1:])
            return self._search_news(keyword)
        elif subcommand == 'stats':
            return self._show_news_stats()
        elif subcommand.isdigit():
            # Handle number-only commands
            return self._show_latest_news(int(subcommand))
        else:
            return self.format_error("未知的子命令。可用命令: latest, view, market, categories, category, source, search, stats")
    
    def _show_latest_news(self, limit: int = 10) -> CommandResult:
        """显示最新新闻"""
        news_list = self.news_service.get_latest_news(limit)
        
        if not news_list:
            return self.format_success("新闻头条\n📰 暂无新闻")
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📰 最新市场动态                          │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        for i, news in enumerate(news_list, 1):
            # 格式化时间
            time_str = news.created_at.strftime("%m-%d %H:%M")
            
            # 根据分类选择图标
            category_icons = {
                'market': '📈',
                'economy': '💰',
                'technology': '💻',
                'policy': '📋',
                'international': '🌍',
                'company': '🏢'
            }
            icon = category_icons.get(news.category, '📰')
            
            # 市场影响指示器
            impact_indicator = ""
            if news.market_impact:
                if news.market_impact > 0.5:
                    impact_indicator = " 🔥"
                elif news.market_impact > 0.3:
                    impact_indicator = " ⚡"
                elif news.market_impact > 0.1:
                    impact_indicator = " 📊"
            
            # 截断标题以适应显示
            title = news.title[:45] + "..." if len(news.title) > 45 else news.title
            
            output.append(f"│ {i:>2}. {icon} [{time_str}] {title:<40}{impact_indicator:<3} │")
            
            # 如果有市场影响，显示相关股票
            if news.affected_stocks:
                stocks_str = ", ".join(news.affected_stocks[:3])  # 只显示前3个
                if len(news.affected_stocks) > 3:
                    stocks_str += f" +{len(news.affected_stocks)-3}更多"
                output.append(f"│     📊 影响股票: {stocks_str:<45} │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 使用提示                                                 │")
        output.append("│ • news view <ID>     - 查看新闻详情                         │")
        output.append("│ • news market        - 查看市场影响新闻                     │")
        output.append("│ • news category <类> - 按分类查看新闻                       │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success("新闻头条\n" + "\n".join(output))
    
    def _view_news_detail(self, news_id: int) -> CommandResult:
        """查看新闻详情"""
        news = self.news_service.get_news_by_id(news_id)
        
        if not news:
            return self.format_error(f"新闻ID {news_id} 不存在")
        
        # 根据分类选择图标
        category_icons = {
            'market': '📈',
            'economy': '💰',
            'technology': '💻',
            'policy': '📋',
            'international': '🌍',
            'company': '🏢'
        }
        icon = category_icons.get(news.category, '📰')
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│ {icon} 新闻详情 #{news.id}                                    │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        # 标题 (可能需要分行)
        title_lines = [news.title[i:i+57] for i in range(0, len(news.title), 57)]
        for i, line in enumerate(title_lines):
            if i == 0:
                output.append(f"│ 📰 {line:<58} │")
            else:
                output.append(f"│    {line:<58} │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        # 基本信息
        time_str = news.created_at.strftime("%Y-%m-%d %H:%M:%S")
        output.append(f"│ 🕒 发布时间: {time_str:<20}                        │")
        output.append(f"│ 📂 新闻分类: {news.category:<20}                        │")
        
        # 市场影响
        if news.market_impact is not None:
            impact_level = "高" if news.market_impact > 0.5 else "中" if news.market_impact > 0.3 else "低"
            impact_color = "🔥" if news.market_impact > 0.5 else "⚡" if news.market_impact > 0.3 else "📊"
            output.append(f"│ {impact_color} 市场影响: {impact_level} ({news.market_impact:.1%})                           │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        # 新闻内容 (分行显示)
        content_lines = [news.content[i:i+57] for i in range(0, len(news.content), 57)]
        output.append("│ 📝 新闻内容                                                 │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        for line in content_lines:
            output.append(f"│ {line:<59} │")
        
        # 相关股票
        if news.affected_stocks:
            output.append("├─────────────────────────────────────────────────────────────┤")
            output.append("│ 📊 相关股票                                                 │")
            
            # 每行显示3个股票代码
            stocks = news.affected_stocks
            for i in range(0, len(stocks), 3):
                stock_group = stocks[i:i+3]
                stocks_str = "  ".join(f"{stock:<8}" for stock in stock_group)
                output.append(f"│ {stocks_str:<59} │")
        
        # 新闻来源
        if hasattr(news, 'source') and news.source:
            output.append("├─────────────────────────────────────────────────────────────┤")
            output.append(f"│ 📡 新闻来源: {news.source:<20}                        │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 相关操作                                                 │")
        
        if news.affected_stocks:
            # 显示相关股票的快速操作提示
            main_stock = news.affected_stocks[0] if news.affected_stocks else None
            if main_stock:
                output.append(f"│ • stock view {main_stock:<8} - 查看相关股票详情                │")
                output.append(f"│ • stock buy {main_stock} <量>   - 买入相关股票                │")
        
        output.append("│ • news market        - 查看更多市场新闻                     │")
        output.append("│ • news latest        - 返回最新新闻列表                     │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success("\n".join(output))
    
    def _show_market_news(self) -> CommandResult:
        """显示有市场影响的新闻"""
        market_news = self.news_service.get_market_impact_news()
        
        if not market_news:
            return self.format_success("📰 暂无市场影响新闻")
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📈 市场影响新闻                          │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ ID │ 影响 │ 时间     │ 标题                        │ 股票 │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        for news in market_news[:15]:  # 只显示前15条
            time_str = news.created_at.strftime("%m-%d %H:%M")
            
            # 影响等级图标
            if news.market_impact > 0.5:
                impact_icon = "🔥"
            elif news.market_impact > 0.3:
                impact_icon = "⚡"
            else:
                impact_icon = "📊"
            
            # 截断标题
            title = news.title[:25] + "..." if len(news.title) > 25 else news.title
            
            # 相关股票 (只显示第一个)
            main_stock = news.affected_stocks[0] if news.affected_stocks else "--"
            
            output.append(f"│{news.id:>3} │ {impact_icon}   │ {time_str} │ {title:<27} │ {main_stock:<4} │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 🔥 高影响  ⚡ 中影响  📊 低影响                             │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 使用 'news view <ID>' 查看详细内容                       │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success("\n".join(output))
    
    def _show_categories(self) -> CommandResult:
        """显示新闻分类"""
        categories = self.news_service.get_news_categories()
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📂 新闻分类                              │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        category_info = {
            'market': ('📈', '市场动态', '股市行情、交易数据、市场分析'),
            'economy': ('💰', '经济新闻', '宏观经济、政策解读、经济指标'),
            'technology': ('💻', '科技资讯', '科技创新、产品发布、行业趋势'),
            'policy': ('📋', '政策法规', '监管政策、法律法规、政府公告'),
            'international': ('🌍', '国际新闻', '国际市场、贸易动态、全球经济'),
            'company': ('🏢', '公司动态', '企业公告、财报发布、人事变动')
        }
        
        for category in categories:
            if category in category_info:
                icon, name, desc = category_info[category]
                output.append(f"│ {icon} {name:<12} │ {desc:<35} │")
                output.append(f"│   使用: news category {category:<8}                          │")
                output.append("├─────────────────────────────────────────────────────────────┤")
        
        output.append("│ 💡 使用 'news category <分类>' 查看特定分类新闻             │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success("新闻分类列表\n" + "\n".join(output))
    
    def _show_news_by_category(self, category: str, count: int = 5) -> CommandResult:
        """按分类显示新闻"""
        # 这里应该调用 news_service 的相应方法
        # 暂时返回模拟数据
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        count_text = f"前{count}条" if count < 10 else ""
        output.append(f"│                📂 {category.upper()} 新闻头条 {count_text}                        │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📊 功能开发中...                                            │")
        output.append("│                                                             │")
        output.append("│ 即将支持按分类筛选新闻功能                                  │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 当前可用功能                                             │")
        output.append("│ • news latest        - 查看最新新闻                         │")
        output.append("│ • news market        - 查看市场影响新闻                     │")
        output.append("│ • news categories    - 查看所有分类                         │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success(f"{category.upper()} 新闻头条\n" + "\n".join(output))
    
    def _search_news(self, keyword: str) -> CommandResult:
        """搜索新闻"""
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│                🔍 搜索: {keyword:<20}                    │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📊 功能开发中...                                            │")
        output.append("│                                                             │")
        output.append("│ 即将支持新闻搜索功能                                        │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 当前可用功能                                             │")
        output.append("│ • news latest        - 查看最新新闻                         │")
        output.append("│ • news market        - 查看市场影响新闻                     │")
        output.append("│ • news view <ID>     - 查看新闻详情                         │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success("\n".join(output))
    
    def _show_news_stats(self) -> CommandResult:
        """显示新闻统计"""
        stats = self.news_service.get_news_stats()
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📊 新闻统计                              │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        if stats:
            output.append(f"│ 📰 新闻总数:     {stats.get('total_news', 0):>8} 条                      │")
            output.append(f"│ 📈 今日新闻:     {stats.get('today_news', 0):>8} 条                      │")
            output.append(f"│ 🔥 高影响新闻:   {stats.get('high_impact_news', 0):>8} 条                      │")
            
            if 'category_stats' in stats:
                output.append("├─────────────────────────────────────────────────────────────┤")
                output.append("│ 📂 分类统计                                                 │")
                
                for category, count in stats['category_stats'].items():
                    category_icons = {
                        'market': '📈',
                        'economy': '💰',
                        'technology': '💻',
                        'policy': '📋',
                        'international': '🌍',
                        'company': '🏢'
                    }
                    icon = category_icons.get(category, '📰')
                    output.append(f"│ {icon} {category:<12} {count:>8} 条                           │")
        else:
            output.append("│ 📊 暂无统计数据                                             │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 新闻系统功能                                             │")
        output.append("│ • 自动生成市场新闻                                          │")
        output.append("│ • 新闻影响股价变动                                          │")
        output.append("│ • 多分类新闻管理                                            │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success("\n".join(output))
    
    def _show_sources(self) -> CommandResult:
        """显示新闻来源"""
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📡 可用新闻来源                          │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ • reuters        - 路透社                                   │")
        output.append("│ • bloomberg      - 彭博社                                   │")
        output.append("│ • wsj            - 华尔街日报                               │")
        output.append("│ • ft             - 金融时报                                 │")
        output.append("│ • cnbc           - CNBC                                     │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success("可用新闻来源\n" + "\n".join(output))
    
    def _show_news_by_source(self, source: str, count: int = 5) -> CommandResult:
        """按来源显示新闻"""
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│                📡 {source.upper()} 新闻头条                          │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📊 功能开发中...                                            │")
        output.append("│                                                             │")
        output.append("│ 即将支持按来源筛选新闻功能                                  │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 当前可用功能                                             │")
        output.append("│ • news latest        - 查看最新新闻                         │")
        output.append("│ • news market        - 查看市场影响新闻                     │")
        output.append("│ • news sources       - 查看所有来源                         │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return self.format_success(f"{source.upper()} 新闻头条\n" + "\n".join(output))
    
    def get_help(self) -> str:
        return """
新闻命令 - 查看市场新闻和动态

用法:
  news                         - 显示最新新闻
  news latest [数量]           - 显示最新新闻 (默认10条)
  news view <ID>               - 查看新闻详情
  news market                  - 显示有市场影响的新闻
  news categories              - 显示新闻分类
  news category <分类>         - 按分类查看新闻
  news search <关键词>         - 搜索新闻 (开发中)
  news stats                   - 显示新闻统计

示例:
  news
  news latest 20
  news view 123
  news market
  news categories
  news category market
  news search "科技股"
  news stats

说明:
  新闻系统提供实时市场动态，包括：
  • 自动生成的市场新闻
  • 新闻对股价的影响分析
  • 多分类新闻管理
  • 新闻搜索和统计功能
"""