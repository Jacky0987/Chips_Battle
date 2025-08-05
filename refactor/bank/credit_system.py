from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List
import json

class CreditRating(Enum):
    """信用等级"""
    AAA = "AAA"  # 最高信用
    AA = "AA"
    A = "A"
    BBB = "BBB"  # 投资级
    BB = "BB"
    B = "B"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"      # 违约

class CreditManager:
    """信用管理系统"""
    
    def __init__(self):
        self.rating_thresholds = {
            900: CreditRating.AAA,
            850: CreditRating.AA,
            800: CreditRating.A,
            750: CreditRating.BBB,
            700: CreditRating.BB,
            650: CreditRating.B,
            600: CreditRating.CCC,
            550: CreditRating.CC,
            500: CreditRating.C,
            0: CreditRating.D
        }
        
    def calculate_credit_score(self, user_data):
        """计算信用评分"""
        score = 700  # 基础分数
        
        # 交易历史影响 (0-100分)
        trades_count = user_data.get('trades_count', 0)
        if trades_count > 0:
            trade_score = min(100, trades_count * 2)
            score += trade_score * 0.2
            
        # 盈利能力影响 (0-100分)
        total_profit = user_data.get('total_profit', 0)
        if total_profit > 0:
            profit_score = min(100, total_profit / 1000)  # 每1000盈利1分
            score += profit_score * 0.15
        elif total_profit < 0:
            loss_penalty = min(100, abs(total_profit) / 500)  # 每500亏损扣1分
            score -= loss_penalty * 0.1
            
        # 资产规模影响 (0-100分)
        net_worth = user_data.get('cash', 0)  # 简化计算
        if net_worth > 100000:
            wealth_score = min(100, (net_worth - 100000) / 10000)
            score += wealth_score * 0.25
            
        # 贷款历史影响
        bank_data = user_data.get('bank_data', {})
        loans = bank_data.get('loans', [])
        
        if loans:
            repaid_on_time = len([l for l in loans if l.get('status') == 'repaid_on_time'])
            defaulted = len([l for l in loans if l.get('status') == 'defaulted'])
            total_loans = len(loans)
            
            if total_loans > 0:
                repayment_rate = repaid_on_time / total_loans
                score += (repayment_rate - 0.5) * 200  # 50%基准
                
                if defaulted > 0:
                    score -= defaulted * 50  # 每次违约扣50分
                    
        # 账户历史长度
        created_date = user_data.get('created_date')
        if created_date:
            try:
                create_time = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                days_old = (datetime.now() - create_time).days
                history_score = min(50, days_old / 10)  # 每10天1分，最高50分
                score += history_score
            except:
                pass
                
        return max(300, min(950, int(score)))
        
    def get_credit_rating(self, user_data):
        """获取信用等级"""
        score = self.calculate_credit_score(user_data)
        
        for threshold, rating in self.rating_thresholds.items():
            if score >= threshold:
                return rating.value
                
        return CreditRating.D.value
        
    def get_rating_benefits(self, rating):
        """获取信用等级福利"""
        benefits = {
            'AAA': {
                'loan_rate_discount': 0.03,
                'max_loan_multiplier': 2.0,
                'special_services': ['VIP通道', '专属理财师', '优先审批'],
                'deposit_rate_bonus': 0.01
            },
            'AA': {
                'loan_rate_discount': 0.025,
                'max_loan_multiplier': 1.8,
                'special_services': ['快速审批', '专属客服'],
                'deposit_rate_bonus': 0.008
            },
            'A': {
                'loan_rate_discount': 0.02,
                'max_loan_multiplier': 1.6,
                'special_services': ['优先客服'],
                'deposit_rate_bonus': 0.006
            },
            'BBB': {
                'loan_rate_discount': 0.01,
                'max_loan_multiplier': 1.4,
                'special_services': [],
                'deposit_rate_bonus': 0.004
            },
            'BB': {
                'loan_rate_discount': 0.005,
                'max_loan_multiplier': 1.2,
                'special_services': [],
                'deposit_rate_bonus': 0.002
            },
            'B': {
                'loan_rate_discount': 0.0,
                'max_loan_multiplier': 1.0,
                'special_services': [],
                'deposit_rate_bonus': 0.0
            },
            'CCC': {
                'loan_rate_discount': -0.01,
                'max_loan_multiplier': 0.8,
                'special_services': [],
                'deposit_rate_bonus': 0.0
            },
            'CC': {
                'loan_rate_discount': -0.02,
                'max_loan_multiplier': 0.6,
                'special_services': [],
                'deposit_rate_bonus': 0.0
            },
            'C': {
                'loan_rate_discount': -0.03,
                'max_loan_multiplier': 0.4,
                'special_services': [],
                'deposit_rate_bonus': 0.0
            },
            'D': {
                'loan_rate_discount': -0.05,
                'max_loan_multiplier': 0.2,
                'special_services': ['需要担保'],
                'deposit_rate_bonus': 0.0
            }
        }
        
        return benefits.get(rating, benefits['B'])
        
    def show_credit_report(self, user_data):
        """显示信用报告"""
        score = self.calculate_credit_score(user_data)
        rating = self.get_credit_rating(user_data)
        benefits = self.get_rating_benefits(rating)
        
        # 计算各项得分
        base_score = 700
        
        # 交易得分
        trades_count = user_data.get('trades_count', 0)
        trade_score = min(100, trades_count * 2) * 0.2 if trades_count > 0 else 0
        
        # 盈利得分
        total_profit = user_data.get('total_profit', 0)
        if total_profit > 0:
            profit_score = min(100, total_profit / 1000) * 0.15
        else:
            profit_score = -min(100, abs(total_profit) / 500) * 0.1
            
        # 财富得分
        net_worth = user_data.get('cash', 0)
        wealth_score = min(100, max(0, (net_worth - 100000) / 10000)) * 0.25
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                                📊 个人信用报告 📊                                        ║
║                              JackyCoin 信用评估中心                                      ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

🎯 信用评估结果:
  信用评分: {score} 分
  信用等级: {rating} ({self._get_rating_description(rating)})
  评估时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 评分构成明细:
┌─────────────────┬─────────┬─────────┬─────────────────────────────┐
│ 评分因子        │ 权重    │ 得分    │ 详情                        │
├─────────────────┼─────────┼─────────┼─────────────────────────────┤
│ 基础分数        │ 固定    │ {base_score:>7} │ 所有用户基础信用分          │
│ 交易活跃度      │ 20%     │ {trade_score:>7.1f} │ 交易次数: {trades_count}            │
│ 盈利能力        │ 15%     │ {profit_score:>7.1f} │ 总盈亏: J${total_profit:,.0f}        │
│ 资产规模        │ 25%     │ {wealth_score:>7.1f} │ 净资产: J${net_worth:,.0f}          │
│ 贷款历史        │ 30%     │ {"计算中":>7} │ 还款记录分析中              │
│ 账户历史        │ 10%     │ {"计算中":>7} │ 开户时长评估中              │
└─────────────────┴─────────┴─────────┴─────────────────────────────┘

💰 信用等级福利:
  贷款利率优惠: {benefits['loan_rate_discount']*100:+.2f}%
  贷款额度倍数: {benefits['max_loan_multiplier']:.1f}x
  存款利率加成: {benefits['deposit_rate_bonus']*100:+.2f}%

🎖️ 专属服务:
"""
        
        if benefits['special_services']:
            for service in benefits['special_services']:
                report += f"  ✅ {service}\n"
        else:
            report += "  暂无专属服务\n"
            
        report += f"""

📈 信用提升建议:
{self._get_improvement_suggestions(score, user_data)}

📋 信用历史记录:
  开户时间: {user_data.get('created_date', '未知')[:10]}
  最近更新: {datetime.now().strftime('%Y-%m-%d')}
  历史最高评分: {score} (当前)
  
⚠️  重要提示:
  • 信用评分每次交易后自动更新
  • 按时还款可显著提升信用等级
  • 频繁违约将严重影响信用记录
  • 高信用等级客户享受更多优惠

💡 信用等级说明:
  AAA-A: 优秀信用，享受最优利率
  BBB-BB: 良好信用，投资级别
  B-CCC: 一般信用，标准服务
  CC-D: 较差信用，需要改善
"""
        
        return report
        
    def _get_rating_description(self, rating):
        """获取等级描述"""
        descriptions = {
            'AAA': '卓越信用',
            'AA': '优秀信用',
            'A': '良好信用',
            'BBB': '投资级信用',
            'BB': '中等信用',
            'B': '一般信用',
            'CCC': '较差信用',
            'CC': '很差信用',
            'C': '极差信用',
            'D': '违约风险'
        }
        return descriptions.get(rating, '未知等级')
        
    def _get_improvement_suggestions(self, score, user_data):
        """获取信用提升建议"""
        suggestions = []
        
        if score < 750:
            trades_count = user_data.get('trades_count', 0)
            if trades_count < 50:
                suggestions.append("• 增加交易频率，提升交易活跃度评分")
                
            total_profit = user_data.get('total_profit', 0)
            if total_profit < 0:
                suggestions.append("• 改善交易策略，提升盈利能力")
                
            net_worth = user_data.get('cash', 0)
            if net_worth < 200000:
                suggestions.append("• 增加资产积累，提升财富规模评分")
                
        if score < 800:
            suggestions.append("• 及时偿还贷款，建立良好还款记录")
            suggestions.append("• 避免频繁违约，保持稳定的信用记录")
            
        if score < 850:
            suggestions.append("• 维持长期稳定的交易表现")
            suggestions.append("• 考虑增加定期存款，展示财务稳定性")
            
        if not suggestions:
            suggestions.append("• 您的信用状况优秀，请继续保持！")
            suggestions.append("• 可以考虑申请更高额度的信用产品")
            
        return "\n".join(suggestions) 