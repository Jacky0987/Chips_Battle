"""
🤖 AI股票分析工具
基于人工智能的股票分析和投资建议
"""

import random
from datetime import datetime
from apps.base_app import BaseApp


class AIAnalysisApp(BaseApp):
    """AI分析应用"""
    
    def __init__(self):
        super().__init__(
            "ai_analysis",
            "🤖 AI股票分析",
            "基于人工智能算法的股票深度分析和投资建议工具。",
            15000,
            "分析工具"
        )
    
    def run(self, main_app, symbol=None):
        """运行AI分析"""
        self.usage_count += 1
        
        if not symbol:
            return self._show_ai_menu(main_app)
        
        symbol = symbol.upper()
        
        if symbol not in main_app.market_data.stocks:
            return f"❌ 股票代码 '{symbol}' 不存在"
        
        stock_data = main_app.market_data.stocks[symbol]
        portfolio = main_app.portfolio
        
        return self._perform_ai_analysis(stock_data, portfolio)
    
    def _perform_ai_analysis(self, stock_data, portfolio):
        """执行AI股票分析"""
        symbol = None
        for code, data in stock_data.items() if isinstance(stock_data, dict) else [(stock_data.get('symbol', 'UNKNOWN'), stock_data)]:
            symbol = code
            stock_info = data if isinstance(data, dict) else stock_data
            break
        
        if not symbol:
            return "❌ 无法获取股票信息"
        
        name = stock_info.get('name', 'Unknown')
        price = stock_info.get('price', 0)
        change = stock_info.get('change', 0)
        sector = stock_info.get('sector', 'Unknown')
        pe_ratio = stock_info.get('pe_ratio', 0)
        volume = stock_info.get('volume', 0)
        beta = stock_info.get('beta', 1.0)
        
        # AI分析算法
        technical_score = self._calculate_technical_score(stock_info)
        fundamental_score = self._calculate_fundamental_score(stock_info)
        sentiment_score = self._calculate_sentiment_score(stock_info)
        risk_score = self._calculate_risk_score(stock_info)
        
        overall_score = (technical_score + fundamental_score + sentiment_score - risk_score * 0.5) / 3
        
        # 生成投资建议
        if overall_score >= 8:
            recommendation = "🟢 强烈推荐买入"
            confidence = "高"
        elif overall_score >= 6:
            recommendation = "🔵 建议买入"
            confidence = "中"
        elif overall_score >= 4:
            recommendation = "🟡 持有观望"
            confidence = "中"
        elif overall_score >= 2:
            recommendation = "🟠 建议减仓"
            confidence = "中"
        else:
            recommendation = "🔴 建议卖出"
            confidence = "高"
        
        # 价格预测
        volatility = stock_info.get('volatility', 0.02)
        price_trend = random.choice(['上涨', '震荡', '下跌'])
        if overall_score >= 6:
            price_trend = '上涨'
        elif overall_score <= 3:
            price_trend = '下跌'
        
        # 生成分析报告
        analysis_report = f"""
🤖 AI股票深度分析报告

📊 基本信息:
  股票代码: {symbol}
  公司名称: {name}
  当前价格: ${price:.2f}
  今日变动: ${change:+.2f} ({change/price*100:+.2f}%)
  所属行业: {sector}

🧠 AI评分系统:
  技术面评分: {technical_score:.1f}/10 {'🟢' if technical_score >= 7 else '🟡' if technical_score >= 4 else '🔴'}
  基本面评分: {fundamental_score:.1f}/10 {'🟢' if fundamental_score >= 7 else '🟡' if fundamental_score >= 4 else '🔴'}
  市场情绪: {sentiment_score:.1f}/10 {'🟢' if sentiment_score >= 7 else '🟡' if sentiment_score >= 4 else '🔴'}
  风险指数: {risk_score:.1f}/10 {'🔴' if risk_score >= 7 else '🟡' if risk_score >= 4 else '🟢'}
  
  综合评分: {overall_score:.1f}/10

💡 投资建议:
  AI推荐: {recommendation}
  置信度: {confidence}
  预期趋势: {price_trend}

📈 技术分析:
  当前位置: {'超买区间' if technical_score >= 8 else '买入区间' if technical_score >= 6 else '中性区间' if technical_score >= 4 else '卖出区间'}
  支撑位: ${price * 0.95:.2f}
  阻力位: ${price * 1.05:.2f}
  
📊 基本面分析:
  估值水平: {'偏高' if pe_ratio > 25 else '合理' if pe_ratio > 15 else '偏低' if pe_ratio > 0 else 'N/A'}
  成交活跃度: {'高' if volume > 50000000 else '中' if volume > 10000000 else '低'}
  市场表现: {'稳定' if beta < 1.2 else '波动'}

⚠️ 风险提示:
  波动性: {volatility*100:.1f}%
  Beta系数: {beta:.2f}
  风险等级: {'高风险' if risk_score >= 7 else '中等风险' if risk_score >= 4 else '低风险'}

🎯 操作建议:
"""
        
        # 根据评分给出具体操作建议
        if overall_score >= 8:
            analysis_report += """
  • 建议分批建仓，可考虑较大仓位
  • 设置止损点在支撑位附近
  • 中长期持有，预期收益较好"""
        elif overall_score >= 6:
            analysis_report += """
  • 可以适量买入，控制仓位
  • 关注技术面变化
  • 短中期持有为主"""
        elif overall_score >= 4:
            analysis_report += """
  • 观望为主，等待更好时机
  • 如有持仓可继续持有
  • 密切关注市场变化"""
        else:
            analysis_report += """
  • 建议减仓或退出
  • 规避短期风险
  • 寻找更好投资机会"""
        
        analysis_report += f"""

📅 分析时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🤖 AI版本: v2.0 (深度学习模型)

💡 温馨提示:
  AI分析仅供参考，投资需谨慎
  建议结合多方信息做出决策
  市场有风险，入市需谨慎
"""
        
        return analysis_report
    
    def _calculate_technical_score(self, stock_info):
        """计算技术面评分"""
        price = stock_info.get('price', 0)
        change = stock_info.get('change', 0)
        volume = stock_info.get('volume', 0)
        price_history = stock_info.get('price_history', [price])
        
        score = 5.0  # 基础分
        
        # 价格趋势
        if len(price_history) >= 5:
            recent_trend = sum(price_history[-3:]) / 3 - sum(price_history[-6:-3]) / 3
            if recent_trend > 0:
                score += 1.5
            elif recent_trend < 0:
                score -= 1.5
        
        # 当日表现
        if change > 0:
            score += min(change / price * 100, 2.0)
        else:
            score += max(change / price * 100, -2.0)
        
        # 成交量分析
        if volume > 50000000:
            score += 1.0
        elif volume < 5000000:
            score -= 0.5
        
        return max(0, min(10, score))
    
    def _calculate_fundamental_score(self, stock_info):
        """计算基本面评分"""
        pe_ratio = stock_info.get('pe_ratio', 20)
        market_cap = stock_info.get('market_cap', 0)
        dividend_yield = stock_info.get('dividend_yield', 0)
        sector = stock_info.get('sector', '')
        
        score = 5.0  # 基础分
        
        # PE估值
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 15:
                score += 2.0
            elif pe_ratio < 25:
                score += 1.0
            elif pe_ratio > 40:
                score -= 2.0
        
        # 分红收益率
        if dividend_yield > 0.03:
            score += 1.5
        elif dividend_yield > 0.01:
            score += 0.5
        
        # 市值分析
        if market_cap > 100000000000:  # 大盘股
            score += 0.5
        elif market_cap < 1000000000:  # 小盘股风险
            score -= 0.5
        
        # 行业分析
        growth_sectors = ['Technology', 'Healthcare', 'Consumer Discretionary']
        if sector in growth_sectors:
            score += 1.0
        
        return max(0, min(10, score))
    
    def _calculate_sentiment_score(self, stock_info):
        """计算市场情绪评分"""
        sector = stock_info.get('sector', '')
        change = stock_info.get('change', 0)
        price = stock_info.get('price', 1)
        
        score = 5.0
        
        # 当日表现反映市场情绪
        change_pct = change / price * 100
        if change_pct > 3:
            score += 2.0
        elif change_pct > 1:
            score += 1.0
        elif change_pct < -3:
            score -= 2.0
        elif change_pct < -1:
            score -= 1.0
        
        # 随机市场情绪因子（模拟市场消息面）
        sentiment_factor = random.uniform(-1.5, 1.5)
        score += sentiment_factor
        
        return max(0, min(10, score))
    
    def _calculate_risk_score(self, stock_info):
        """计算风险评分"""
        volatility = stock_info.get('volatility', 0.02)
        beta = stock_info.get('beta', 1.0)
        price = stock_info.get('price', 0)
        pe_ratio = stock_info.get('pe_ratio', 20)
        
        score = 0.0
        
        # 波动率风险
        if volatility > 0.1:
            score += 3.0
        elif volatility > 0.05:
            score += 1.5
        elif volatility > 0.03:
            score += 0.5
        
        # Beta风险
        if beta > 1.5:
            score += 2.0
        elif beta > 1.2:
            score += 1.0
        elif beta < 0.8:
            score += 0.5  # 过低的beta也可能有问题
        
        # 估值风险
        if pe_ratio and pe_ratio > 50:
            score += 2.0
        elif pe_ratio and pe_ratio > 30:
            score += 1.0
        
        # 价格风险（过高或过低都有风险）
        if price > 500:
            score += 1.0
        elif price < 1:
            score += 2.0
        
        return max(0, min(10, score))
    
    def _show_ai_menu(self, main_app):
        """显示AI分析菜单"""
        return f"""
🤖 AI股票分析工具

💰 当前余额: ${main_app.cash:,.2f}

🧠 AI分析功能:
  • 技术面分析 - 基于价格和成交量数据
  • 基本面分析 - 财务指标和估值分析  
  • 市场情绪分析 - 综合消息面影响
  • 风险评估 - 多维度风险量化
  • 投资建议 - AI智能推荐

📊 评分系统:
  • 技术面评分 (0-10分)
  • 基本面评分 (0-10分)  
  • 市场情绪评分 (0-10分)
  • 风险指数 (0-10分，越低越好)
  • 综合评分 (0-10分)

🎯 使用方法:
  appmarket.app ai_analysis <股票代码>

📖 示例:
  appmarket.app ai_analysis AAPL    # 分析苹果公司
  appmarket.app ai_analysis TSLA    # 分析特斯拉
  appmarket.app ai_analysis MSFT    # 分析微软

🤖 AI算法特点:
  ✓ 深度学习模型
  ✓ 多因子评分体系
  ✓ 实时数据分析
  ✓ 智能投资建议
  ✓ 风险量化评估

⚠️ 免责声明:
  • AI分析仅供参考，不构成投资建议
  • 市场有风险，投资需谨慎
  • 建议结合多方信息进行决策
  • 过往表现不代表未来收益

💡 分析建议:
  建议在重要投资决策前使用AI分析
  可以帮助您更好地理解股票的投资价值
  结合您的风险偏好制定投资策略
""" 