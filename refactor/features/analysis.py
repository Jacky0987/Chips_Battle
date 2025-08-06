import random
from datetime import datetime, timedelta


class AnalysisFeatures:
    def __init__(self, market_data_manager, trading_engine):
        self.market_data = market_data_manager
        self.trading_engine = trading_engine

    def show_market_overview(self):
        """显示市场概况"""
        gainers = [(s, d['change'] / (d['price'] - d['change']) * 100 if d['price'] != d['change'] else 0) for s, d in
                   self.market_data.stocks.items() if d['change'] > 0]
        losers = [(s, d['change'] / (d['price'] - d['change']) * 100 if d['price'] != d['change'] else 0) for s, d in
                  self.market_data.stocks.items() if d['change'] < 0]
        gainers.sort(key=lambda x: x[1], reverse=True)
        losers.sort(key=lambda x: x[1])

        # Calculate market breadth
        advance_decline_ratio = len(gainers) / len(losers) if losers else float('inf')
        market_volatility = sum(d['volatility'] * 100 for d in self.market_data.stocks.values()) / len(self.market_data.stocks)

        # Sector performance
        sectors = {}
        for symbol, data in self.market_data.stocks.items():
            sector = data['sector']
            if sector not in sectors:
                sectors[sector] = {'count': 0, 'total_change': 0}
            sectors[sector]['count'] += 1
            sectors[sector]['total_change'] += data['change'] / (data['price'] - data['change']) * 100 if data[
                                                                                                              'price'] != \
                                                                                                          data[
                                                                                                              'change'] else 0

        market_text = f"""
    市场概况报告 [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]

    市场动态:
      上涨股票: {len(gainers)} | 下跌股票: {len(losers)} | 横盘股票: {len(self.market_data.stocks) - len(gainers) - len(losers)}
      市场广度: {advance_decline_ratio:.2f} (上涨/下跌比)
      市场波动率: {market_volatility:.2f}% (平均股票波动率)

    行业表现:
    {'-' * 50}
    {'行业':<12} | {'股票数':>6} | {'平均涨跌':>8}
    {'-' * 50}
    """
        for sector, info in sorted(sectors.items(), key=lambda x: x[1]['total_change'] / x[1]['count'], reverse=True):
            avg_change = info['total_change'] / info['count']
            market_text += f"{sector:<12} | {info['count']:>6} | {avg_change:+8.2f}%\n"

        market_text += f"""
    领涨股票:
    {'-' * 50}
    {'代码':<6} | {'名称':<15} | {'涨跌幅':>8}
    {'-' * 50}
    """
        for symbol, change_pct in gainers[:3]:
            market_text += f"{symbol:<6} | {self.market_data.stocks[symbol]['name']:<15} | {change_pct:+8.2f}%\n"

        market_text += f"""
    领跌股票:
    {'-' * 50}
    {'代码':<6} | {'名称':<15} | {'涨跌幅':>8}
    {'-' * 50}
    """
        for symbol, change_pct in losers[:3]:
            market_text += f"{symbol:<6} | {self.market_data.stocks[symbol]['name']:<15} | {change_pct:+8.2f}%\n"

        # Market outlook
        sentiment = "看涨" if advance_decline_ratio > 1.5 else "看跌" if advance_decline_ratio < 0.7 else "中性"
        market_text += f"""
    市场展望:
      当前趋势: {sentiment}
      - {'关注领涨行业，寻找强势股票机会。' if sentiment == '看涨' else '谨慎操作，关注低估值防御性股票。' if sentiment == '看跌' else '保持观望，等待明确趋势信号。'}
      - 波动率{'较高' if market_volatility > 3 else '较低'}，建议{'关注风险管理' if market_volatility > 3 else '适度增加仓位'}。
      - 使用 'news' 命令查看近期市场事件影响。

    风险提示: 市场分析基于模拟数据，实际投资需结合多方信息。
    """
        return market_text

    def show_market_news(self):
        """显示市场新闻"""
        if not self.market_data.market_events:
            return "暂无市场动态。"

        # Sort events by timestamp (most recent first)
        recent_events = sorted(self.market_data.market_events, key=lambda x: x['timestamp'], reverse=True)[:3]

        news_text = f"""
    市场动态 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    最新消息:
    """
        for event in recent_events:
            timestamp = event['timestamp'][:19]
            related_stocks = ", ".join(event['related_stocks']) if event['related_stocks'] else "无特定股票"
            impact = event['impact']
            news_text += f"""
    [{timestamp}] {event['title']}
      详情: {event['description']}
      影响行业: {', '.join(impact['sectors'])}
      影响方向: {'上涨' if impact['effect'] == 'positive' else '下跌' if impact['effect'] == 'negative' else '中性'}
      预计幅度: {impact['magnitude'] * 100:.2f}%
      持续时间: {'短期' if impact['duration'] == 'short_term' else '中期' if impact['duration'] == 'medium_term' else '长期'}
      相关股票: {related_stocks}
    """

        news_text += """
    建议:
      - 关注受影响行业的股票价格变动
      - 结合技术分析调整交易策略
      - 使用 'quote <代码>' 查看具体股票详情
    """
        return news_text

    def show_technical_analysis(self, symbol):
        """显示技术分析"""
        if symbol not in self.market_data.stocks:
            return f"错误: 股票代码 {symbol} 不存在"

        data = self.market_data.stocks[symbol]
        price = data['price']
        change = data['change']
        price_history = data['price_history']

        # Calculate technical indicators
        sma_20 = sum(price_history[-20:]) / min(len(price_history), 20)
        sma_50 = sum(price_history[-50:]) / min(len(price_history), 50) if len(price_history) >= 50 else sma_20
        rsi = random.uniform(20, 80)  # Simulated RSI
        macd = (sum(price_history[-12:]) / min(len(price_history), 12)) - (
                    sum(price_history[-26:]) / min(len(price_history), 26))  # Simplified MACD
        std_dev = (sum((p - price) ** 2 for p in price_history[-20:]) / min(len(price_history),
                                                                            20)) ** 0.5  # 20-day standard deviation
        bollinger_upper = sma_20 + 2 * std_dev
        bollinger_lower = sma_20 - 2 * std_dev

        # Sector averages for comparison
        sector_stocks = [s for s, d in self.market_data.stocks.items() if d['sector'] == data['sector']]
        sector_pe_avg = sum(self.market_data.stocks[s]['pe_ratio'] or 0 for s in sector_stocks) / len(
            sector_stocks) if sector_stocks else data['pe_ratio']
        sector_beta_avg = sum(self.market_data.stocks[s]['beta'] for s in sector_stocks) / len(sector_stocks) if sector_stocks else \
        data['beta']

        # Recommendation logic
        recommendation = "持有"
        if rsi < 30 and price < sma_50:
            recommendation = "强烈买入"
        elif rsi < 50 and price < sma_20:
            recommendation = "买入"
        elif rsi > 70 and price > sma_50:
            recommendation = "强烈卖出"
        elif rsi > 50 and price > sma_20:
            recommendation = "卖出"

        analysis_text = f"""
    技术分析报告 - {symbol} ({data['name']}) [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]

    基本信息:
      当前价格: ${price:.2f} | 日内变动: ${change:+.2f} ({(change / (price - change) * 100 if price != change else 0):+.2f}%)
      52周范围: ${min(price_history):.2f} - ${max(price_history):.2f}
      成交量: {data['volume']:,} | 波动率: {data['volatility'] * 100:.2f}% (行业平均: {data['volatility'] * 100 * 1.1:.2f}%)

    技术指标:
      20日均线: ${sma_20:.2f} | 50日均线: ${sma_50:.2f}
      RSI (14天): {rsi:.2f} ({'超买' if rsi > 70 else '超卖' if rsi < 30 else '正常'})
      MACD: {macd:+.2f} | 布林带: ${bollinger_lower:.2f} - ${bollinger_upper:.2f}
      20日标准差: ${std_dev:.2f}

    基本面指标:
      市盈率: {data['pe_ratio']:.2f} (行业平均: {sector_pe_avg:.2f})
      Beta: {data['beta']:.2f} (行业平均: {sector_beta_avg:.2f})
      股息率: {data['dividend_yield'] * 100:.2f}% | 每股收益: ${data['eps']:.2f}

    投资建议: {recommendation}
      - RSI和均线分析表明 {recommendation.lower()}机会。
      - 当前价格{'高于' if price > sma_50 else '低于'}50日均线，趋势{'看涨' if price > sma_50 else '看跌'}。
      - 波动率{'高于' if data['volatility'] > 0.04 else '低于'}行业平均水平，风险{'较高' if data['volatility'] > 0.04 else '较低'}。
      - 市盈率{'高于' if data['pe_ratio'] > sector_pe_avg else '低于'}行业平均，可能{'被高估' if data['pe_ratio'] > sector_pe_avg else '被低估'}。

    风险提示: 本分析基于模拟数据，仅供参考。投资决策需结合市场动态和个人风险承受能力。
    """
        return analysis_text

    def show_sector_analysis(self):
        """显示行业分析"""
        sectors = {}
        for symbol, data in self.market_data.stocks.items():
            sector = data.get('sector', 'Unknown')  # Default to 'Unknown' if sector is missing
            if sector not in sectors:
                sectors[sector] = {
                    'count': 0,
                    'total_change': 0,
                    'total_volatility': 0,
                    'total_pe': 0,
                    'valid_pe': 0,
                    'symbols': [],
                    'market_cap': 0,
                    'total_volume': 0,
                    'price_sum': 0
                }

            # Increment count
            sectors[sector]['count'] += 1

            # Handle market_cap
            market_cap = data.get('market_cap')
            if market_cap is not None and isinstance(market_cap, (int, float)):
                sectors[sector]['market_cap'] += market_cap

            # Handle change
            change = data.get('change')
            price = data.get('price', 0)
            if change is not None and isinstance(change, (int, float)):
                sectors[sector]['total_change'] += change
                sectors[sector]['price_sum'] += price

            # Handle volatility
            volatility = data.get('volatility')
            if volatility is not None and isinstance(volatility, (int, float)):
                sectors[sector]['total_volatility'] += volatility

            # Handle volume
            volume = data.get('volume', 0)
            if isinstance(volume, (int, float)):
                sectors[sector]['total_volume'] += volume

            # Handle price and symbols
            if change is not None and price is not None and isinstance(change, (int, float)) and isinstance(price, (int, float)):
                sectors[sector]['symbols'].append((symbol, change, price))

            # Handle pe_ratio
            pe_ratio = data.get('pe_ratio')
            if pe_ratio is not None and isinstance(pe_ratio, (int, float)):
                sectors[sector]['total_pe'] += pe_ratio
                sectors[sector]['valid_pe'] += 1

        sector_text = f"""
══════════════════════════════════════════════════════════════════════════════════════════════════════════════
                                          📈 行业分析报告                                                      
                                   [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]                                   
══════════════════════════════════════════════════════════════════════════════════════════════════════════════

🏭 行业表现概览:
────────────────────────────────────────────────────────────────────────────────────────────────────────────
 行业名称        │ 股票数 │ 平均涨跌 │ 平均波动率 │ 平均市盈率 │ 总市值(百万) │ 成交量(万)   
────────────────────────────────────────────────────────────────────────────────────────────────────────────"""

        sorted_sectors = sorted(sectors.items(),
                                key=lambda x: x[1]['total_change'] / x[1]['count'] if x[1]['count'] > 0 else 0,
                                reverse=True)
        
        # 记录最佳和最差行业用于图表
        best_sector = sorted_sectors[0] if sorted_sectors else None
        worst_sector = sorted_sectors[-1] if sorted_sectors else None
        
        for sector, info in sorted_sectors:
            avg_change = info['total_change'] / info['count'] if info['count'] > 0 else 0
            avg_volatility = (info['total_volatility'] / info['count'] * 100) if info['count'] > 0 else 0
            avg_pe = info['total_pe'] / info['valid_pe'] if info['valid_pe'] > 0 else 'N/A'
            avg_volume = info['total_volume'] / info['count'] / 10000 if info['count'] > 0 else 0  # 转换为万
            market_cap_millions = info['market_cap'] / 1000000  # 转换为百万
            
            # 表现指示器
            performance_icon = "🔥" if avg_change > 2 else "📈" if avg_change > 0 else "📉" if avg_change > -2 else "💥"
            
            sector_text += f"\n {performance_icon}{sector:<12} │ {info['count']:>6} │ {avg_change:>+7.2f}% │ {avg_volatility:>9.2f}% │ {avg_pe if isinstance(avg_pe, str) else f'{avg_pe:.1f}':>10} │ {market_cap_millions:>11.0f} │ {avg_volume:>11.0f}"

            # Top performer in sector
            if info['symbols']:
                top_stock = max(info['symbols'], key=lambda x: x[1], default=('N/A', 0, 0))
                bottom_stock = min(info['symbols'], key=lambda x: x[1], default=('N/A', 0, 0))
                sector_text += f"\n   🌟领涨: {top_stock[0]} (+{top_stock[1]:.2f}%)  💔领跌: {bottom_stock[0]} ({bottom_stock[1]:+.2f}%)"

        sector_text += f"""
╰────────────────┴────────┴──────────┴────────────┴────────────┴──────────────┴──────────────╯

📊 行业表现图表:
{self._create_sector_performance_chart(sorted_sectors)}

💡 投资建议:
  🎯 领涨行业: {best_sector[0] if best_sector else '无数据'}
     └─ 平均涨幅: {(best_sector[1]['total_change'] / best_sector[1]['count']):+.2f}% if best_sector else 0
     └─ 建议策略: 关注其中的优质个股，但注意高位风险
  
  🛡️ 防御配置: {', '.join([s[0] for s in sorted_sectors if s[1]['count'] > 0 and (s[1]['total_volatility'] / s[1]['count']) < 0.03][:3])}
     └─ 低波动率行业，适合稳健投资
  
  💎 价值机会: {', '.join([s[0] for s in sorted_sectors if s[1]['valid_pe'] > 0 and (s[1]['total_pe'] / s[1]['valid_pe']) < 15][:3])}
     └─ 市盈率较低，可能存在价值投资机会

🔔 风险提示:
  • 行业轮动是常态，建议定期重新平衡配置
  • 单一行业集中度不宜超过总资产的30%
  • 关注宏观经济政策对不同行业的影响差异
  • 新兴行业虽有高增长潜力，但风险也相对较高
"""
        return sector_text

    def _create_sector_performance_chart(self, sorted_sectors, chart_width=50):
        """创建ASCII行业表现图表"""
        if not sorted_sectors:
            return "暂无数据可显示"
        
        chart_text = ""
        max_change = max([abs(s[1]['total_change'] / s[1]['count']) for s in sorted_sectors if s[1]['count'] > 0], default=1)
        
        for sector, info in sorted_sectors[:8]:  # 只显示前8个行业
            avg_change = info['total_change'] / info['count'] if info['count'] > 0 else 0
            
            # 计算条形图长度
            if max_change > 0:
                bar_length = int(abs(avg_change) / max_change * chart_width)
            else:
                bar_length = 0
            
            # 选择条形图字符和颜色指示
            if avg_change > 0:
                bar_char = "█"
                indicator = "📈"
            else:
                bar_char = "▓"
                indicator = "📉"
            
            # 构建条形图
            bar = bar_char * min(bar_length, chart_width)
            spaces = " " * (chart_width - len(bar))
            
            chart_text += f"{indicator} {sector[:12]:<12} │{bar}{spaces}│ {avg_change:+6.2f}%\n"
        
        return chart_text

    def show_sector_chart(self, sector_name=None):
        """显示特定行业的详细图表分析"""
        if sector_name:
            return self._show_specific_sector_chart(sector_name)
        
        # 显示所有行业的简化图表
        sectors = {}
        for symbol, data in self.market_data.stocks.items():
            sector = data.get('sector', 'Unknown')
            if sector not in sectors:
                sectors[sector] = {
                    'symbols': [],
                    'total_change': 0,
                    'count': 0,
                    'market_cap': 0
                }
            
            change = data.get('change', 0)
            price = data.get('price', 0)
            market_cap = data.get('market_cap', 0)
            
            sectors[sector]['symbols'].append((symbol, change, price))
            sectors[sector]['total_change'] += change
            sectors[sector]['count'] += 1
            sectors[sector]['market_cap'] += market_cap

        chart_text = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                        📊 行业表现实时图表                                                    ║
║                                   [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]                                   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

🎯 使用说明: sector_chart <行业名> 查看特定行业详情

📈 实时行业热力图:
"""
        
        sorted_sectors = sorted(sectors.items(), 
                               key=lambda x: x[1]['total_change'] / x[1]['count'] if x[1]['count'] > 0 else 0, 
                               reverse=True)
        
        # 创建热力图风格的显示
        chart_text += self._create_heatmap_display(sorted_sectors)
        
        chart_text += f"""
🔍 可查看的行业详情:
   {' | '.join([s[0] for s in sorted_sectors[:6]])}

💡 使用示例:
   sector_chart Technology  - 查看科技行业详细分析
   sector_chart Financial   - 查看金融行业详细分析
"""
        return chart_text

    def _create_heatmap_display(self, sorted_sectors):
        """创建热力图风格的行业显示"""
        heatmap_text = ""
        cols = 3  # 每行显示3个行业
        
        for i in range(0, len(sorted_sectors), cols):
            row_sectors = sorted_sectors[i:i+cols]
            
            # 行业名称行
            name_line = ""
            chart_line = ""
            value_line = ""
            
            for sector, info in row_sectors:
                avg_change = info['total_change'] / info['count'] if info['count'] > 0 else 0
                
                # 选择颜色和符号
                if avg_change > 2:
                    temp_symbol = "🔥🔥🔥"
                elif avg_change > 1:
                    temp_symbol = "🔥🔥 "
                elif avg_change > 0:
                    temp_symbol = "🔥  "
                elif avg_change > -1:
                    temp_symbol = "❄️  "
                elif avg_change > -2:
                    temp_symbol = "❄️❄️ "
                else:
                    temp_symbol = "❄️❄️❄️"
                
                # 格式化显示
                name_line += f"┌─{sector[:12]:<12}─┐  "
                chart_line += f"│ {temp_symbol} {avg_change:+5.1f}% │  "
                value_line += f"└─{info['count']:>3}股票 {info['market_cap']/1e9:.1f}B─┘  "
            
            heatmap_text += name_line.rstrip() + "\n"
            heatmap_text += chart_line.rstrip() + "\n"
            heatmap_text += value_line.rstrip() + "\n\n"
        
        return heatmap_text

    def _show_specific_sector_chart(self, sector_name):
        """显示特定行业的详细图表"""
        sector_stocks = []
        for symbol, data in self.market_data.stocks.items():
            if data.get('sector', '').lower() == sector_name.lower():
                sector_stocks.append((symbol, data))
        
        if not sector_stocks:
            return f"❌ 未找到行业 '{sector_name}' 的股票数据\n\n可用行业: {', '.join(set(s['sector'] for s in self.market_data.stocks.values()))}"

        # 计算行业统计
        total_market_cap = sum(s[1].get('market_cap', 0) for s in sector_stocks)
        avg_change = sum(s[1].get('change', 0) for s in sector_stocks) / len(sector_stocks)
        avg_pe = sum(s[1].get('pe_ratio', 0) for s in sector_stocks if s[1].get('pe_ratio')) / len([s for s in sector_stocks if s[1].get('pe_ratio')])
        total_volume = sum(s[1].get('volume', 0) for s in sector_stocks)

        chart_text = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                      📊 {sector_name} 行业详细分析                                           ║
║                                   [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]                                   ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝

🏭 行业概况:
  股票数量: {len(sector_stocks)}只
  总市值: ${total_market_cap/1e9:.2f}B
  平均涨跌: {avg_change:+.2f}%
  平均PE: {avg_pe:.1f}
  总成交量: {total_volume:,}

📊 个股表现图表:
"""
        
        # 按涨跌幅排序
        sorted_stocks = sorted(sector_stocks, key=lambda x: x[1].get('change', 0), reverse=True)
        
        # 创建个股表现图表
        chart_text += self._create_stock_performance_chart(sorted_stocks)
        
        # 添加技术分析
        chart_text += f"""

📈 行业技术分析:
{self._sector_technical_analysis(sorted_stocks, sector_name)}

🎯 投资建议:
{self._sector_investment_advice(sorted_stocks, avg_change)}
"""
        return chart_text

    def _create_stock_performance_chart(self, sorted_stocks, chart_width=40):
        """创建个股表现图表"""
        chart_text = ""
        if not sorted_stocks:
            return "无数据可显示"
        
        max_change = max([abs(s[1].get('change', 0)) for s in sorted_stocks], default=1)
        
        for symbol, data in sorted_stocks[:15]:  # 只显示前15只股票
            change = data.get('change', 0)
            price = data.get('price', 0)
            volume = data.get('volume', 0)
            
            # 计算条形图长度
            if max_change > 0:
                bar_length = int(abs(change) / max_change * chart_width)
            else:
                bar_length = 0
            
            # 选择显示样式
            if change > 1:
                bar_char = "█"
                icon = "🚀"
            elif change > 0:
                bar_char = "▓"
                icon = "📈"
            elif change == 0:
                bar_char = "░"
                icon = "⚖️"
            elif change > -1:
                bar_char = "▒"
                icon = "📉"
            else:
                bar_char = "▓"
                icon = "💥"
            
            # 构建条形图
            bar = bar_char * min(bar_length, chart_width)
            spaces = " " * (chart_width - len(bar))
            
            # 成交量指示器
            volume_level = "🔥" if volume > 50000000 else "🔸" if volume > 10000000 else "⚪"
            
            chart_text += f"{icon} {symbol:<6} │{bar}{spaces}│ {change:+6.2f}% ${price:>7.2f} {volume_level}\n"
        
        chart_text += f"\n💡 图例: 🚀涨>1% 📈涨 ⚖️平 📉跌 💥跌>1% | 成交量: 🔥高 🔸中 ⚪低"
        return chart_text

    def _sector_technical_analysis(self, stocks, sector_name):
        """行业技术分析"""
        if not stocks:
            return "数据不足"
        
        prices = [s[1].get('price', 0) for s in stocks]
        changes = [s[1].get('change', 0) for s in stocks]
        volumes = [s[1].get('volume', 0) for s in stocks]
        
        # 计算技术指标
        avg_price = sum(prices) / len(prices)
        price_momentum = sum(changes) / len(changes)
        volume_ratio = sum(volumes) / len(volumes)
        
        # RSI 简化计算
        positive_changes = [c for c in changes if c > 0]
        negative_changes = [abs(c) for c in changes if c < 0]
        
        avg_positive = sum(positive_changes) / len(positive_changes) if positive_changes else 0
        avg_negative = sum(negative_changes) / len(negative_changes) if negative_changes else 0
        
        if avg_negative == 0:
            sector_rsi = 100
        else:
            rs = avg_positive / avg_negative
            sector_rsi = 100 - (100 / (1 + rs))
        
        analysis = f"""
  📊 技术指标:
    平均价格: ${avg_price:.2f}
    动量指数: {price_momentum:+.2f}%
    RSI指数: {sector_rsi:.1f} ({'超买' if sector_rsi > 70 else '超卖' if sector_rsi < 30 else '正常'})
    成交活跃度: {'高' if volume_ratio > 30000000 else '中' if volume_ratio > 10000000 else '低'}
  
  🎯 技术信号:
    趋势方向: {'上升' if price_momentum > 0.5 else '下降' if price_momentum < -0.5 else '横盘'}
    市场情绪: {'乐观' if sector_rsi > 60 else '悲观' if sector_rsi < 40 else '中性'}
    建议操作: {'减仓' if sector_rsi > 75 else '加仓' if sector_rsi < 25 else '持有'}"""
        
        return analysis

    def _sector_investment_advice(self, stocks, avg_change):
        """行业投资建议"""
        rising_stocks = len([s for s in stocks if s[1].get('change', 0) > 0])
        total_stocks = len(stocks)
        rising_ratio = rising_stocks / total_stocks if total_stocks > 0 else 0
        
        advice = f"""
  🎯 投资策略建议:
    行业强度: {rising_ratio*100:.1f}% 股票上涨 ({rising_stocks}/{total_stocks})
    配置建议: {'增持' if rising_ratio > 0.7 else '减持' if rising_ratio < 0.3 else '维持'}
    
  ⚡ 操作提示:
    • {'行业表现强劲，可考虑增加配置' if avg_change > 1 else '行业表现疲软，谨慎操作' if avg_change < -1 else '行业表现平稳，维持现有配置'}
    • {'关注领涨股票的基本面是否支撑' if avg_change > 0 else '关注是否有反弹机会'}
    • 建议单一行业配置不超过总资产的25%
    • 定期监控行业轮动和政策变化"""
        
        return advice

    def show_risk_assessment(self, cash, portfolio):
        """显示风险评估"""
        total_value = self.trading_engine.calculate_total_value(cash, portfolio)
        cash_ratio = cash / total_value if total_value > 0 else 1.0

        # Calculate portfolio metrics
        metrics = self.trading_engine.calculate_portfolio_metrics(portfolio, total_value)
        portfolio_beta = metrics['beta']
        portfolio_volatility = metrics['volatility']
        sector_weights = metrics['sector_weights']
        max_position = metrics['max_position_weight']

        # Simulated Sharpe ratio (risk-free rate assumed at 2%)
        portfolio_return = (total_value - 100000) / 100000
        sharpe_ratio = (portfolio_return - 0.02) / portfolio_volatility if portfolio_volatility > 0 else 0

        risk_level = "低风险" if portfolio_volatility < 0.02 else "中风险" if portfolio_volatility < 0.04 else "高风险"

        risk_text = f"""
    投资组合风险评估 [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]

    资产配置:
      现金占比: {cash_ratio * 100:.2f}% | 股票占比: {(1 - cash_ratio) * 100:.2f}%
      持仓股票数: {len(portfolio)} | 总资产: ${total_value:,.2f}

    风险指标:
      投资组合Beta: {portfolio_beta:.2f} (市场相关性: {'高' if portfolio_beta > 1.2 else '低' if portfolio_beta < 0.8 else '中等'})
      波动率: {portfolio_volatility * 100:.2f}% ({risk_level})
      夏普比率: {sharpe_ratio:.2f} (风险调整后收益)
      最大单一持仓: {max_position:.2f}%

    行业集中度:
    {'-' * 50}
    {'行业':<10} | {'占比':<10} | {'风险等级':<10}
    {'-' * 50}
    """
        for sector, weight in sector_weights.items():
            sector_risk = "高" if weight > 40 else "中" if weight > 20 else "低"
            risk_text += f"{sector:<10} | {weight:>8.2f}% | {sector_risk:<10}\n"

        risk_text += f"""
    风险管理建议:
      - 现金占比{'过低' if cash_ratio < 0.15 else '过高' if cash_ratio > 0.5 else '适中'}，建议维持在15-25%。
      - {'单一持仓集中度较高，建议分散投资。' if max_position > 20 else '持仓分散度合理。'}
      - {'行业集中度较高，建议增加其他行业配置。' if any(w > 40 for w in sector_weights.values()) else '行业配置较为均衡。'}
      - Beta值表明投资组合对市场波动的敏感性{'较高' if portfolio_beta > 1.2 else '较低'}，建议关注市场趋势。

    风险提示: 高波动性资产可能带来较大收益，但也伴随较高风险。建议定期重新平衡投资组合。
    """
        return risk_text

    def show_market_sentiment(self):
        """显示市场情绪分析"""
        # 计算市场情绪指标
        positive_stocks = sum(1 for stock in self.market_data.stocks.values() if stock['change'] > 0)
        total_stocks = len(self.market_data.stocks)
        sentiment_score = (positive_stocks / total_stocks) * 100

        if sentiment_score >= 70:
            sentiment = "极度乐观"
        elif sentiment_score >= 55:
            sentiment = "乐观"
        elif sentiment_score >= 45:
            sentiment = "中性"
        elif sentiment_score >= 30:
            sentiment = "谨慎"
        else:
            sentiment = "悲观"

        sentiment_text = f"""
市场情绪分析

当前情绪: {sentiment} ({sentiment_score:.1f}分)
上涨股票: {positive_stocks}/{total_stocks}

情绪指标:
  恐慌指数: {100 - sentiment_score:.1f}
  贪婪指数: {sentiment_score:.1f}

投资建议:
  • 乐观时期: 适度减仓，防范风险
  • 悲观时期: 逢低买入，寻找机会
  • 中性时期: 保持观望，等待信号

市场谚言: "在别人贪婪时恐惧，在别人恐惧时贪婪"
"""
        return sentiment_text

    def show_economic_calendar(self):
        """显示经济日历"""
        calendar_text = f"""
经济日历 - {datetime.now().strftime("%Y年%m月")}

本周重要事件:
  {datetime.now().strftime("%m-%d")} 周三 - 美联储会议纪要公布
  {(datetime.now() + timedelta(days=1)).strftime("%m-%d")} 周四 - 非农就业数据
  {(datetime.now() + timedelta(days=2)).strftime("%m-%d")} 周五 - 消费者信心指数

对市场影响:
  • 美联储纪要可能影响利率敏感股票
  • 就业数据影响整体市场情绪
  • 消费者信心指数影响消费股

建议关注: 科技股、银行股、消费股
"""
        return calendar_text 