"""
赛马投注游戏
体验激烈的赛马投注，预测冠军马匹
"""

import random
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_app import BaseApp


class HorseRacingApp(BaseApp):
    """赛马投注游戏"""
    
    def __init__(self):
        super().__init__(
            app_id="horse_racing",
            name="🐎 皇家赛马场",
            description="体验世界级赛马投注，预测冠军马匹，享受速度与激情的碰撞",
            price=7000,
            category="entertainment",
            version="1.0",
            emoji="🐎"
        )
    
    def run(self, main_app, action=None, bet_amount=None, horse_number=None):
        """运行赛马游戏"""
        self.main_app = main_app
        self.update_usage()
        
        if action == "race" and bet_amount is not None:
            try:
                bet = float(bet_amount)
                horse_num = int(horse_number) if horse_number else None
                return self._start_race(bet, horse_num)
            except (ValueError, TypeError):
                return "❌ 无效的投注金额或马匹编号"
        elif action == "rules":
            return self._show_rules()
        else:
            return self._show_racing_menu()
    
    def _start_race(self, bet_amount: float, selected_horse: int = None) -> str:
        """开始赛马比赛"""
        if bet_amount <= 0:
            return "❌ 投注金额必须大于0"
        
        if bet_amount > 10000:
            return "❌ 单次投注不能超过$10,000"
        
        if self.main_app.cash < bet_amount:
            return f"❌ 余额不足，需要${bet_amount:,.2f}，当前余额${self.main_app.cash:,.2f}"
        
        # 生成马匹
        horses = self._generate_horses()
        
        # 如果没有选择马匹，让用户选择
        if selected_horse is None:
            return self._show_horse_selection(horses, bet_amount)
        
        if selected_horse < 1 or selected_horse > len(horses):
            return f"❌ 请选择1-{len(horses)}号马匹"
        
        selected_horse_data = horses[selected_horse - 1]
        
        # 扣除投注金额
        self.main_app.cash -= bet_amount
        
        # 开始比赛
        race_result = self._simulate_race(horses)
        winner = race_result['winner']
        race_details = race_result['details']
        
        # 计算奖金
        payout = 0
        if winner['number'] == selected_horse:
            # 胜利！按赔率计算奖金
            payout = bet_amount * winner['odds']
            self.main_app.cash += payout
            
            # 更新统计
            if not hasattr(self.main_app.user_data, 'horse_racing_stats'):
                self.main_app.user_data.setdefault('horse_racing_stats', {'wins': 0, 'races': 0, 'total_winnings': 0})
            
            self.main_app.user_data['horse_racing_stats']['wins'] += 1
            self.main_app.user_data['horse_racing_stats']['total_winnings'] += (payout - bet_amount)
        
        self.main_app.user_data.setdefault('horse_racing_stats', {'wins': 0, 'races': 0, 'total_winnings': 0})
        self.main_app.user_data['horse_racing_stats']['races'] += 1
        
        # 生成比赛报告
        return self._generate_race_report(selected_horse_data, winner, race_details, bet_amount, payout)
    
    def _generate_horses(self) -> list:
        """生成参赛马匹"""
        horse_names = [
            "雷电疾风", "黄金骑士", "烈火战神", "星光飞驰", "影子奔雷",
            "钻石之心", "风暴领主", "银色子弹", "紫电狂奔", "王者之翼",
            "烈焰之魂", "黑色闪电", "白云飞马", "红色彗星", "蓝色风暴"
        ]
        
        horses = []
        for i in range(8):  # 8匹马参赛
            name = random.choice(horse_names)
            
            # 生成马匹属性
            speed = random.uniform(70, 95)
            stamina = random.uniform(60, 90)
            experience = random.uniform(50, 100)
            condition = random.uniform(80, 100)
            
            # 计算综合实力
            overall_strength = (speed * 0.4 + stamina * 0.25 + experience * 0.2 + condition * 0.15)
            
            # 根据实力计算赔率（实力越强赔率越低）
            base_odds = 10 - (overall_strength / 12)
            odds = max(1.5, round(base_odds + random.uniform(-0.5, 0.5), 1))
            
            # 生成骑师信息
            jockey_names = ["张骑手", "李飞驰", "王疾风", "赵闪电", "刘子弹", "陈雷霆", "林飞马", "周疾速"]
            jockey = random.choice(jockey_names)
            
            horse = {
                'number': i + 1,
                'name': name,
                'jockey': jockey,
                'speed': speed,
                'stamina': stamina,
                'experience': experience,
                'condition': condition,
                'overall_strength': overall_strength,
                'odds': odds,
                'win_chance': overall_strength / 100,
                'recent_form': self._generate_recent_form()
            }
            
            horses.append(horse)
        
        return sorted(horses, key=lambda x: x['odds'])  # 按赔率排序
    
    def _generate_recent_form(self) -> str:
        """生成最近比赛成绩"""
        forms = ['1', '2', '3', '4', '5', 'X']  # 1-5名次，X表示未完赛
        recent = []
        for _ in range(5):
            if random.random() < 0.8:  # 80%概率完赛
                recent.append(random.choice(['1', '2', '3', '4', '5']))
            else:
                recent.append('X')
        return '-'.join(recent)
    
    def _show_horse_selection(self, horses: list, bet_amount: float) -> str:
        """显示马匹选择界面"""
        selection_text = f"""
🐎 皇家赛马场 - 第{random.randint(1, 99)}场比赛

💰 投注金额: ${bet_amount:,.2f}

🏇 参赛马匹:
"""
        
        for horse in horses:
            strength_stars = "⭐" * int(horse['overall_strength'] / 20)
            selection_text += f"""
  {horse['number']}号 - {horse['name']}
    骑师: {horse['jockey']}
    赔率: 1:{horse['odds']}
    状态: {strength_stars} ({horse['overall_strength']:.1f})
    近期成绩: {horse['recent_form']}
    速度: {horse['speed']:.1f} | 耐力: {horse['stamina']:.1f}
"""
        
        selection_text += f"""
🎯 选择马匹投注:
  appmarket.app horse_racing race {bet_amount} <马匹编号>

📊 投注示例:
  appmarket.app horse_racing race {bet_amount} 1    # 投注1号马
  appmarket.app horse_racing race {bet_amount} 3    # 投注3号马

💡 提示: 赔率越低胜算越大，但奖金也越少
"""
        
        return selection_text
    
    def _simulate_race(self, horses: list) -> dict:
        """模拟赛马过程"""
        # 计算每匹马的最终表现
        race_performance = []
        
        for horse in horses:
            # 基础实力
            base_performance = horse['overall_strength']
            
            # 随机因素（赛场状况、发挥等）
            luck_factor = random.uniform(-15, 15)
            
            # 特殊事件
            special_events = []
            if random.random() < 0.1:  # 10%概率特殊事件
                event_type = random.choice(['surge', 'stumble', 'perfect_start'])
                if event_type == 'surge':
                    luck_factor += 10
                    special_events.append(f"{horse['name']}最后冲刺爆发！")
                elif event_type == 'stumble':
                    luck_factor -= 8
                    special_events.append(f"{horse['name']}途中失蹄！")
                elif event_type == 'perfect_start':
                    luck_factor += 5
                    special_events.append(f"{horse['name']}完美起跑！")
            
            final_performance = base_performance + luck_factor
            
            race_performance.append({
                'horse': horse,
                'performance': final_performance,
                'special_events': special_events
            })
        
        # 按表现排序
        race_performance.sort(key=lambda x: x['performance'], reverse=True)
        
        # 生成比赛详情
        race_details = {
            'total_distance': '1600米',
            'track_condition': random.choice(['快速', '良好', '稍重', '重场']),
            'weather': random.choice(['晴朗', '多云', '小雨', '阴天']),
            'rankings': race_performance,
            'race_time': f"{random.uniform(90, 110):.2f}秒"
        }
        
        winner = race_performance[0]['horse']
        
        return {
            'winner': winner,
            'details': race_details
        }
    
    def _generate_race_report(self, selected_horse: dict, winner: dict, race_details: dict, bet_amount: float, payout: float) -> str:
        """生成比赛报告"""
        is_winner = selected_horse['number'] == winner['number']
        
        report = f"""
🏁 比赛结果报告

🏇 您的选择: {selected_horse['number']}号 {selected_horse['name']}
🥇 比赛冠军: {winner['number']}号 {winner['name']}

📊 比赛信息:
  赛道条件: {race_details['track_condition']}
  天气状况: {race_details['weather']}
  比赛时间: {race_details['race_time']}
  赛程距离: {race_details['total_distance']}

🏆 前三名:
"""
        
        for i, result in enumerate(race_details['rankings'][:3]):
            horse = result['horse']
            medal = ["🥇", "🥈", "🥉"][i]
            report += f"  {medal} {horse['number']}号 {horse['name']} (骑师: {horse['jockey']})\n"
        
        # 特殊事件
        all_events = []
        for result in race_details['rankings']:
            all_events.extend(result['special_events'])
        
        if all_events:
            report += f"\n🎬 比赛亮点:\n"
            for event in all_events:
                report += f"  • {event}\n"
        
        # 投注结果
        report += f"\n💰 投注结果:\n"
        report += f"  投注金额: ${bet_amount:,.2f}\n"
        
        if is_winner:
            profit = payout - bet_amount
            report += f"  🎉 恭喜中奖！\n"
            report += f"  奖金: ${payout:,.2f}\n"
            report += f"  净盈利: ${profit:,.2f}\n"
            report += f"  当前余额: ${self.main_app.cash:,.2f}\n"
        else:
            report += f"  ❌ 很遗憾未中奖\n"
            report += f"  当前余额: ${self.main_app.cash:,.2f}\n"
        
        # 统计信息
        stats = self.main_app.user_data.get('horse_racing_stats', {'wins': 0, 'races': 0, 'total_winnings': 0})
        win_rate = (stats['wins'] / stats['races'] * 100) if stats['races'] > 0 else 0
        
        report += f"""
📈 个人统计:
  参赛次数: {stats['races']}
  中奖次数: {stats['wins']}
  胜率: {win_rate:.1f}%
  累计盈亏: ${stats['total_winnings']:,.2f}

🎮 继续游戏:
  appmarket.app horse_racing              # 返回主菜单
  appmarket.app horse_racing race 500     # 投注$500新比赛
"""
        
        return report
    
    def _show_racing_menu(self) -> str:
        """显示赛马主菜单"""
        stats = self.main_app.user_data.get('horse_racing_stats', {'wins': 0, 'races': 0, 'total_winnings': 0})
        win_rate = (stats['wins'] / stats['races'] * 100) if stats['races'] > 0 else 0
        
        return f"""
🐎 皇家赛马场 - 欢迎光临

🏇 世界级赛马投注体验
  • 8匹精选赛马激烈竞速
  • 专业骑师精彩对决
  • 实时赔率动态调整
  • 多种投注策略选择

💰 当前状态:
  可用资金: ${self.main_app.cash:,.2f}
  参赛次数: {stats['races']}
  胜率: {win_rate:.1f}%
  累计盈亏: ${stats['total_winnings']:,.2f}

🎮 开始投注:
  appmarket.app horse_racing race <金额>        # 开始新比赛
  appmarket.app horse_racing race 500           # 投注$500
  appmarket.app horse_racing race 1000          # 投注$1000
  appmarket.app horse_racing rules              # 查看游戏规则

🏆 赔率说明:
  • 1:1.5 - 大热门（胜率高，奖金少）
  • 1:3.0 - 次热门（胜率中等）
  • 1:6.0 - 冷门马（胜率低，奖金高）
  • 1:10.0+ - 超级冷门（高风险高回报）

⚡ 投注限制:
  • 单次最低投注: $50
  • 单次最高投注: $10,000
  • 支持多轮连续投注

🎯 投注策略:
  • 稳健型: 选择低赔率热门马
  • 激进型: 选择高赔率冷门马
  • 分散型: 多次小额投注降低风险

💡 胜负关键因素:
  • 马匹综合实力（速度、耐力、经验）
  • 当前状态和近期表现
  • 赛道条件和天气影响
  • 随机的赛场变数
"""
    
    def _show_rules(self) -> str:
        """显示游戏规则"""
        return """
🐎 皇家赛马场 - 游戏规则

🏇 比赛规则:
  • 每场比赛8匹马参赛
  • 赛程距离1600米
  • 只需预测冠军马匹
  • 按赔率计算奖金

🎯 马匹属性:
  • 速度: 影响冲刺能力
  • 耐力: 影响持久作战
  • 经验: 影响临场发挥
  • 状态: 影响当日表现

📊 赔率计算:
  • 根据马匹实力动态调整
  • 实力越强赔率越低
  • 奖金 = 投注额 × 赔率

🎬 特殊事件:
  • 完美起跑: +5分表现加成
  • 最后冲刺: +10分表现加成
  • 途中失蹄: -8分表现影响

🌟 影响因素:
  • 赛道条件: 快速 > 良好 > 稍重 > 重场
  • 天气状况: 影响马匹发挥
  • 随机变数: 增加比赛悬念

💰 奖金规则:
  • 中奖: 投注额 × 该马赔率
  • 未中奖: 失去投注金额
  • 即时结算到账户余额

⚠️ 投注限制:
  • 单次投注: $50 - $10,000
  • 必须有足够余额
  • 不支持赊账投注

🏆 胜率提升策略:
  1. 关注马匹综合实力评分
  2. 分析近期比赛成绩
  3. 考虑赛道和天气条件
  4. 合理分配投注资金
  5. 避免孤注一掷

💡 风险提示:
  赛马投注存在风险，请理性投注，量力而行。
  建议设置投注预算，避免过度投注影响正常生活。
""" 