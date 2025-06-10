class AchievementSystem:
    def __init__(self, achievement_definitions):
        self.achievement_definitions = achievement_definitions

    def check_achievements(self, user_data, portfolio, cash, trades_count, total_profit):
        """检查并解锁成就"""
        achievements = user_data.get('achievements', [])
        new_achievements = []

        # 计算总资产
        from datetime import datetime
        total_value = cash
        portfolio_positions = {k: v for k, v in portfolio.items() if k != 'pending_orders'}
        for symbol, data in portfolio_positions.items():
            # 这里需要从应用获取市场数据，暂时简化处理
            quantity = data.get('quantity', 0)
            if quantity != 0:
                total_value += abs(quantity) * 100  # 简化计算

        # 基础交易成就
        if 'first_trade' not in achievements and trades_count >= 1:
            new_achievements.append('first_trade')
        if 'trader_bronze' not in achievements and trades_count >= 10:
            new_achievements.append('trader_bronze')
        if 'trader_silver' not in achievements and trades_count >= 50:
            new_achievements.append('trader_silver')
        if 'trader_gold' not in achievements and trades_count >= 200:
            new_achievements.append('trader_gold')

        # 盈利成就
        if 'profitable_trader' not in achievements and total_profit >= 10000:
            new_achievements.append('profitable_trader')
        if 'profit_master' not in achievements and total_profit >= 100000:
            new_achievements.append('profit_master')
        if 'profit_legend' not in achievements and total_profit >= 500000:
            new_achievements.append('profit_legend')

        # 投资组合成就
        portfolio_count = len(portfolio_positions)
        if 'diversified' not in achievements and portfolio_count >= 5:
            new_achievements.append('diversified')
        if 'portfolio_master' not in achievements and portfolio_count >= 10:
            new_achievements.append('portfolio_master')

        # 财富成就
        if 'millionaire' not in achievements and total_value >= 1000000:
            new_achievements.append('millionaire')
        if 'multi_millionaire' not in achievements and total_value >= 10000000:
            new_achievements.append('multi_millionaire')

        # 登录连击成就
        login_streak = user_data.get('login_streak', 0)
        if 'streak_trader' not in achievements and login_streak >= 5:
            new_achievements.append('streak_trader')
        if 'loyal_trader' not in achievements and login_streak >= 15:
            new_achievements.append('loyal_trader')
        if 'dedicated_trader' not in achievements and login_streak >= 30:
            new_achievements.append('dedicated_trader')

        # 银行相关成就
        bank_data = user_data.get('bank_data', {})
        if 'banker' not in achievements and bank_data:
            new_achievements.append('banker')

        # 统计相关成就
        stop_loss_count = user_data.get('stop_loss_used', 0)
        take_profit_count = user_data.get('take_profit_used', 0)
        limit_orders_executed = user_data.get('limit_orders_executed', 0)
        short_trades_count = user_data.get('short_trades_count', 0)
        on_time_loan_repayments = user_data.get('on_time_loan_repayments', 0)
        total_deposits = user_data.get('total_deposits', 0)

        if 'risk_manager' not in achievements and stop_loss_count >= 5:
            new_achievements.append('risk_manager')
        if 'profit_taker' not in achievements and take_profit_count >= 5:
            new_achievements.append('profit_taker')
        if 'limit_order_pro' not in achievements and limit_orders_executed >= 20:
            new_achievements.append('limit_order_pro')
        if 'short_seller' not in achievements and short_trades_count >= 10:
            new_achievements.append('short_seller')
        if 'loan_repayer' not in achievements and on_time_loan_repayments >= 5:
            new_achievements.append('loan_repayer')
        if 'saver' not in achievements and total_deposits >= 50000:
            new_achievements.append('saver')

        # 等级成就
        level = user_data.get('level', 1)
        if 'level_up_master' not in achievements and level >= 10:
            new_achievements.append('level_up_master')

        # 成就数量成就
        if 'achievement_hunter' not in achievements and len(achievements) >= 20:
            new_achievements.append('achievement_hunter')

        # 时间相关隐藏成就
        current_hour = datetime.now().hour
        if 'early_bird' not in achievements and current_hour < 6 and trades_count > 0:
            new_achievements.append('early_bird')
        if 'night_owl' not in achievements and current_hour >= 23 and trades_count > 0:
            new_achievements.append('night_owl')

        # 检查单日交易成就
        today_trades = user_data.get('today_trades_count', 0)
        if 'day_trader' not in achievements and today_trades >= 10:
            new_achievements.append('day_trader')
        if 'speed_trader' not in achievements and today_trades >= 25:
            new_achievements.append('speed_trader')

        # 计算奖励
        total_reward = 0
        experience_gained = 0
        achievement_messages = []

        for achievement_id in new_achievements:
            if achievement_id in self.achievement_definitions:
                achievement = self.achievement_definitions[achievement_id]
                tier_emoji = {'bronze': '🥉', 'silver': '🥈', 'gold': '🥇'}.get(achievement['tier'], '🏆')
                
                total_reward += achievement['reward']
                experience_gained += achievement.get('experience', 100)
                
                achievement_messages.append(f"{tier_emoji} 成就解锁: {achievement['name']} - {achievement['desc']}")
                achievement_messages.append(f"奖励: ${achievement['reward']:,} + {achievement.get('experience', 100)}经验")
                if achievement.get('hidden', False):
                    achievement_messages.append("🔮 隐藏成就奖励!")

        return new_achievements, total_reward, experience_gained, achievement_messages

    def check_level_up(self, level, experience):
        """检查等级提升"""
        level_ups = 0
        total_reward = 0
        remaining_exp = experience

        while True:
            required_exp = level * 1000
            if remaining_exp >= required_exp:
                level += 1
                remaining_exp -= required_exp
                level_reward = level * 500
                total_reward += level_reward
                level_ups += 1
            else:
                break

        level_up_messages = []
        if level_ups > 0:
            level_up_messages.append(f"🎉 等级提升! 当前等级: {level}")
            level_up_messages.append(f"等级奖励: ${total_reward}")

        return level, remaining_exp, total_reward, level_up_messages

    def check_login_streak(self, user_data):
        """检查登录连击奖励"""
        streak = user_data.get('login_streak', 0)
        login_bonus = 0
        login_message = ""

        if streak > 0:
            login_bonus = min(streak * 100, 1000)  # 最高1000奖励
            login_message = f"🎁 连续登录奖励: 第{streak}天，获得${login_bonus}"

        return login_bonus, login_message 

    def get_achievement_progress(self, user_data, portfolio, cash, trades_count, total_profit):
        """获取成就进度"""
        achievements = user_data.get('achievements', [])
        progress_list = []
        
        # 计算总资产
        from datetime import datetime
        total_value = cash
        portfolio_positions = {k: v for k, v in portfolio.items() if k != 'pending_orders'}
        for symbol, data in portfolio_positions.items():
            quantity = data.get('quantity', 0)
            if quantity != 0:
                total_value += abs(quantity) * 100  # 简化计算
        
        # 定义进度检查函数
        def add_progress(achievement_id, current_value, target_value, format_func=None):
            if achievement_id not in achievements and achievement_id in self.achievement_definitions:
                achievement = self.achievement_definitions[achievement_id]
                progress = min(current_value / target_value * 100, 100)
                if format_func:
                    current_str = format_func(current_value)
                    target_str = format_func(target_value)
                else:
                    current_str = str(current_value)
                    target_str = str(target_value)
                
                progress_list.append({
                    'id': achievement_id,
                    'name': achievement['name'],
                    'desc': achievement['desc'],
                    'category': achievement['category'],
                    'tier': achievement['tier'],
                    'progress': progress,
                    'current': current_str,
                    'target': target_str,
                    'completed': progress >= 100,
                    'hidden': achievement.get('hidden', False)
                })
        
        # 交易相关进度
        add_progress('trader_bronze', trades_count, 10)
        add_progress('trader_silver', trades_count, 50)
        add_progress('trader_gold', trades_count, 200)
        
        # 盈利相关进度
        add_progress('profitable_trader', total_profit, 10000, lambda x: f"${x:,.0f}")
        add_progress('profit_master', total_profit, 100000, lambda x: f"${x:,.0f}")
        add_progress('profit_legend', total_profit, 500000, lambda x: f"${x:,.0f}")
        
        # 投资组合进度
        portfolio_count = len(portfolio_positions)
        add_progress('diversified', portfolio_count, 5)
        add_progress('portfolio_master', portfolio_count, 10)
        
        # 财富进度
        add_progress('millionaire', total_value, 1000000, lambda x: f"${x:,.0f}")
        add_progress('multi_millionaire', total_value, 10000000, lambda x: f"${x:,.0f}")
        
        # 登录连击进度
        login_streak = user_data.get('login_streak', 0)
        add_progress('streak_trader', login_streak, 5, lambda x: f"{x}天")
        add_progress('loyal_trader', login_streak, 15, lambda x: f"{x}天")
        add_progress('dedicated_trader', login_streak, 30, lambda x: f"{x}天")
        
        # 其他统计进度
        stop_loss_count = user_data.get('stop_loss_used', 0)
        take_profit_count = user_data.get('take_profit_used', 0)
        limit_orders_executed = user_data.get('limit_orders_executed', 0)
        short_trades_count = user_data.get('short_trades_count', 0)
        on_time_loan_repayments = user_data.get('on_time_loan_repayments', 0)
        total_deposits = user_data.get('total_deposits', 0)
        
        add_progress('risk_manager', stop_loss_count, 5)
        add_progress('profit_taker', take_profit_count, 5)
        add_progress('limit_order_pro', limit_orders_executed, 20)
        add_progress('short_seller', short_trades_count, 10)
        add_progress('loan_repayer', on_time_loan_repayments, 5)
        add_progress('saver', total_deposits, 50000, lambda x: f"${x:,.0f}")
        
        # 等级进度
        level = user_data.get('level', 1)
        add_progress('level_up_master', level, 10, lambda x: f"等级{x}")
        
        # 成就数量进度
        add_progress('achievement_hunter', len(achievements), 20)
        
        return progress_list
    
    def get_achievements_by_category(self, user_data):
        """按类别分组获取成就"""
        achievements = user_data.get('achievements', [])
        categories = {}
        
        for achievement_id, achievement in self.achievement_definitions.items():
            category = achievement['category']
            if category not in categories:
                categories[category] = {
                    'name': self._get_category_name(category),
                    'unlocked': [],
                    'locked': [],
                    'total': 0
                }
            
            categories[category]['total'] += 1
            
            if achievement_id in achievements:
                categories[category]['unlocked'].append({
                    'id': achievement_id,
                    'name': achievement['name'],
                    'desc': achievement['desc'],
                    'tier': achievement['tier'],
                    'reward': achievement['reward'],
                    'experience': achievement.get('experience', 100)
                })
            else:
                if not achievement.get('hidden', False):
                    categories[category]['locked'].append({
                        'id': achievement_id,
                        'name': achievement['name'],
                        'desc': achievement['desc'],
                        'tier': achievement['tier'],
                        'reward': achievement['reward'],
                        'experience': achievement.get('experience', 100)
                    })
        
        return categories
    
    def _get_category_name(self, category):
        """获取分类名称"""
        category_names = {
            'trading': '📈 交易技能',
            'profit': '💰 盈利能力',
            'portfolio': '📊 投资组合',
            'wealth': '💎 财富积累',
            'loyalty': '👑 忠诚度',
            'risk': '🛡️ 风险管理',
            'advanced': '⚡ 高级交易',
            'banking': '🏦 银行业务',
            'skill': '🎯 专业技能',
            'special': '🌟 特殊时刻',
            'progress': '📈 等级进步',
            'meta': '🏆 成就大师'
        }
        return category_names.get(category, category)
    
    def get_nearly_completed_achievements(self, user_data, portfolio, cash, trades_count, total_profit, threshold=80):
        """获取即将完成的成就（进度超过阈值）"""
        progress_list = self.get_achievement_progress(user_data, portfolio, cash, trades_count, total_profit)
        nearly_completed = [p for p in progress_list if p['progress'] >= threshold and not p['completed']]
        return sorted(nearly_completed, key=lambda x: x['progress'], reverse=True)
    
    def get_achievement_statistics(self, user_data):
        """获取成就统计信息"""
        achievements = user_data.get('achievements', [])
        total_achievements = len(self.achievement_definitions)
        unlocked_achievements = len(achievements)
        
        # 按等级统计
        tier_stats = {'bronze': 0, 'silver': 0, 'gold': 0}
        total_rewards = 0
        total_experience = 0
        
        for achievement_id in achievements:
            if achievement_id in self.achievement_definitions:
                achievement = self.achievement_definitions[achievement_id]
                tier = achievement.get('tier', 'bronze')
                tier_stats[tier] += 1
                total_rewards += achievement.get('reward', 0)
                total_experience += achievement.get('experience', 100)
        
        # 按分类统计
        category_stats = {}
        for achievement_id, achievement in self.achievement_definitions.items():
            category = achievement['category']
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'unlocked': 0}
            category_stats[category]['total'] += 1
            if achievement_id in achievements:
                category_stats[category]['unlocked'] += 1
        
        completion_rate = (unlocked_achievements / total_achievements) * 100 if total_achievements > 0 else 0
        
        return {
            'total_achievements': total_achievements,
            'unlocked_achievements': unlocked_achievements,
            'completion_rate': completion_rate,
            'tier_stats': tier_stats,
            'category_stats': category_stats,
            'total_rewards': total_rewards,
            'total_experience': total_experience
        }