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
            quantity = data.get('quantity', 0)
            if quantity != 0:
                total_value += abs(quantity) * 100  # 简化计算

        # 添加家庭资产价值
        home_assets_value = user_data.get('home_assets_value', 0)
        total_value += home_assets_value

        # 基础交易成就
        if 'first_trade' not in achievements and trades_count >= 1:
            new_achievements.append('first_trade')
        if 'trader_bronze' not in achievements and trades_count >= 10:
            new_achievements.append('trader_bronze')
        if 'trader_silver' not in achievements and trades_count >= 50:
            new_achievements.append('trader_silver')
        if 'trader_gold' not in achievements and trades_count >= 200:
            new_achievements.append('trader_gold')
        if 'trader_master' not in achievements and trades_count >= 1000:
            new_achievements.append('trader_master')

        # 盈利成就
        if 'profitable_trader' not in achievements and total_profit >= 10000:
            new_achievements.append('profitable_trader')
        if 'profit_master' not in achievements and total_profit >= 100000:
            new_achievements.append('profit_master')
        if 'profit_legend' not in achievements and total_profit >= 500000:
            new_achievements.append('profit_legend')
        if 'profit_god' not in achievements and total_profit >= 10000000:
            new_achievements.append('profit_god')

        # 投资组合成就
        portfolio_count = len(portfolio_positions)
        if 'diversified' not in achievements and portfolio_count >= 5:
            new_achievements.append('diversified')
        if 'portfolio_master' not in achievements and portfolio_count >= 10:
            new_achievements.append('portfolio_master')
        if 'portfolio_legend' not in achievements and portfolio_count >= 20:
            new_achievements.append('portfolio_legend')

        # 财富成就
        if 'millionaire' not in achievements and total_value >= 1000000:
            new_achievements.append('millionaire')
        if 'multi_millionaire' not in achievements and total_value >= 10000000:
            new_achievements.append('multi_millionaire')
        if 'billionaire' not in achievements and total_value >= 100000000:
            new_achievements.append('billionaire')

        # 登录连击成就
        login_streak = user_data.get('login_streak', 0)
        if 'streak_trader' not in achievements and login_streak >= 5:
            new_achievements.append('streak_trader')
        if 'loyal_trader' not in achievements and login_streak >= 15:
            new_achievements.append('loyal_trader')
        if 'dedicated_trader' not in achievements and login_streak >= 30:
            new_achievements.append('dedicated_trader')
        if 'veteran_trader' not in achievements and login_streak >= 100:
            new_achievements.append('veteran_trader')

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
        if 'trading_machine' not in achievements and today_trades >= 50:
            new_achievements.append('trading_machine')

        # 公司相关成就
        companies_created = user_data.get('companies_created', 0)
        companies_ipo = user_data.get('companies_ipo', 0)
        company_max_value = user_data.get('company_max_value', 0)
        company_developments = user_data.get('company_developments', 0)
        companies_acquired = user_data.get('companies_acquired', 0)

        if 'company_founder' not in achievements and companies_created >= 1:
            new_achievements.append('company_founder')
        if 'serial_entrepreneur' not in achievements and companies_created >= 5:
            new_achievements.append('serial_entrepreneur')
        if 'ipo_master' not in achievements and companies_ipo >= 1:
            new_achievements.append('ipo_master')
        if 'ceo_legend' not in achievements and company_max_value >= 1000000000:
            new_achievements.append('ceo_legend')
        if 'company_developer' not in achievements and company_developments >= 10:
            new_achievements.append('company_developer')
        if 'merger_king' not in achievements and companies_acquired >= 5:
            new_achievements.append('merger_king')

        # 商品交易相关成就
        commodity_trades = user_data.get('commodity_trades', 0)
        forex_trades = user_data.get('forex_trades', 0)
        futures_value = user_data.get('futures_value', 0)
        gold_profit = user_data.get('gold_profit', 0)
        oil_profit = user_data.get('oil_profit', 0)

        if 'commodity_trader' not in achievements and commodity_trades >= 1:
            new_achievements.append('commodity_trader')
        if 'forex_expert' not in achievements and forex_trades >= 50:
            new_achievements.append('forex_expert')
        if 'futures_master' not in achievements and futures_value >= 500000:
            new_achievements.append('futures_master')
        if 'gold_digger' not in achievements and gold_profit >= 50000:
            new_achievements.append('gold_digger')
        if 'oil_baron' not in achievements and oil_profit >= 100000:
            new_achievements.append('oil_baron')

        # 游戏应用相关成就
        apps_used = user_data.get('apps_used', set())
        if isinstance(apps_used, list):
            apps_used = set(apps_used)
        
        blackjack_wins = user_data.get('blackjack_wins', 0)
        poker_streak = user_data.get('poker_streak', 0)
        roulette_profit = user_data.get('roulette_profit', 0)
        horse_predictions = user_data.get('horse_predictions', 0)
        slot_jackpots = user_data.get('slot_jackpots', 0)
        dice_streak = user_data.get('dice_streak', 0)
        texas_holdem_wins = user_data.get('texas_holdem_wins', 0)
        ai_analysis_uses = user_data.get('ai_analysis_uses', 0)
        chart_uses = user_data.get('chart_uses', 0)
        news_analysis_uses = user_data.get('news_analysis_uses', 0)

        if 'gambler' not in achievements and len(apps_used) >= 1:
            new_achievements.append('gambler')
        if 'blackjack_winner' not in achievements and blackjack_wins >= 10:
            new_achievements.append('blackjack_winner')
        if 'poker_shark' not in achievements and poker_streak >= 5:
            new_achievements.append('poker_shark')
        if 'roulette_master' not in achievements and roulette_profit >= 25000:
            new_achievements.append('roulette_master')
        if 'horse_whisperer' not in achievements and horse_predictions >= 5:
            new_achievements.append('horse_whisperer')
        if 'slot_jackpot' not in achievements and slot_jackpots >= 1:
            new_achievements.append('slot_jackpot')
        if 'dice_lucky' not in achievements and dice_streak >= 5:
            new_achievements.append('dice_lucky')
        if 'texas_holdem_pro' not in achievements and texas_holdem_wins >= 1:
            new_achievements.append('texas_holdem_pro')
        if 'app_explorer' not in achievements and len(apps_used) >= 5:
            new_achievements.append('app_explorer')
        if 'app_master' not in achievements and len(apps_used) >= 10:
            new_achievements.append('app_master')
        if 'analyst' not in achievements and ai_analysis_uses >= 50:
            new_achievements.append('analyst')
        if 'chart_master' not in achievements and chart_uses >= 100:
            new_achievements.append('chart_master')
        if 'news_reader' not in achievements and news_analysis_uses >= 20:
            new_achievements.append('news_reader')

        # 检查游戏传奇成就（需要在所有游戏类型中获胜）
        gaming_achievements = ['blackjack_winner', 'poker_shark', 'roulette_master', 
                              'horse_whisperer', 'slot_jackpot', 'dice_lucky', 'texas_holdem_pro']
        if 'gaming_legend' not in achievements and all(ach in achievements for ach in gaming_achievements):
            new_achievements.append('gaming_legend')

        # 家庭资产相关成就
        home_assets = user_data.get('home_assets', {})
        home_assets_value = sum(sum(asset_data.values()) if isinstance(asset_data, dict) else 0 
                               for asset_data in home_assets.values())
        
        luxury_value = home_assets.get('luxury_value', 0)
        cars_owned = len(home_assets.get('cars', {}))
        etf_owned = len(home_assets.get('etf', {}))
        art_value = home_assets.get('art_value', 0)

        if 'home_decorator' not in achievements and home_assets_value > 0:
            new_achievements.append('home_decorator')
        if 'luxury_collector' not in achievements and luxury_value >= 100000:
            new_achievements.append('luxury_collector')
        if 'car_enthusiast' not in achievements and cars_owned >= 3:
            new_achievements.append('car_enthusiast')
        if 'etf_investor' not in achievements and etf_owned >= 1:
            new_achievements.append('etf_investor')
        if 'fund_manager' not in achievements and etf_owned >= 10:
            new_achievements.append('fund_manager')
        if 'art_connoisseur' not in achievements and art_value >= 500000:
            new_achievements.append('art_connoisseur')
        if 'mansion_owner' not in achievements and home_assets_value >= 10000000:
            new_achievements.append('mansion_owner')

        # 市场相关成就
        indices_tracked = user_data.get('indices_tracked', 0)
        market_predictions = user_data.get('market_predictions', 0)
        volatility_profit = user_data.get('volatility_profit', 0)
        contrarian_profit = user_data.get('contrarian_profit', 0)

        if 'index_tracker' not in achievements and indices_tracked >= 10:
            new_achievements.append('index_tracker')
        if 'market_guru' not in achievements and market_predictions >= 70:
            new_achievements.append('market_guru')
        if 'volatility_master' not in achievements and volatility_profit >= 200000:
            new_achievements.append('volatility_master')
        if 'contrarian' not in achievements and contrarian_profit >= 100000:
            new_achievements.append('contrarian')

        # 特殊隐藏成就检查
        consecutive_profitable_trades = user_data.get('consecutive_profitable_trades', 0)
        daily_trading_hours = user_data.get('daily_trading_hours', 0)
        perfect_day_trades = user_data.get('perfect_day_trades', 0)
        bankruptcy_recoveries = user_data.get('bankruptcy_recoveries', 0)

        if 'lucky_seven' not in achievements and consecutive_profitable_trades >= 7:
            new_achievements.append('lucky_seven')
        if 'marathon_trader' not in achievements and daily_trading_hours >= 24:
            new_achievements.append('marathon_trader')
        if 'perfect_timing' not in achievements and perfect_day_trades >= 1:
            new_achievements.append('perfect_timing')
        if 'phoenix' not in achievements and bankruptcy_recoveries >= 1 and total_value >= 1000000:
            new_achievements.append('phoenix')
        if 'midas_touch' not in achievements and consecutive_profitable_trades >= 20:
            new_achievements.append('midas_touch')

        # 计算奖励
        total_reward = 0
        experience_gained = 0
        achievement_messages = []

        for achievement_id in new_achievements:
            if achievement_id in self.achievement_definitions:
                achievement = self.achievement_definitions[achievement_id]
                tier_emoji = {'bronze': '🥉', 'silver': '🥈', 'gold': '🥇', 'legendary': '👑'}.get(achievement['tier'], '🏆')
                
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
                total_value += abs(quantity) * 100

        # 添加家庭资产价值
        home_assets_value = user_data.get('home_assets_value', 0)
        total_value += home_assets_value
        
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
                    'reward': achievement['reward'],
                    'experience': achievement.get('experience', 100)
                })

        # 基础交易进度
        add_progress('trader_bronze', trades_count, 10)
        add_progress('trader_silver', trades_count, 50)
        add_progress('trader_gold', trades_count, 200)
        add_progress('trader_master', trades_count, 1000)

        # 盈利进度
        add_progress('profitable_trader', total_profit, 10000, lambda x: f"${x:,.0f}")
        add_progress('profit_master', total_profit, 100000, lambda x: f"${x:,.0f}")
        add_progress('profit_legend', total_profit, 500000, lambda x: f"${x:,.0f}")
        add_progress('profit_god', total_profit, 10000000, lambda x: f"${x:,.0f}")

        # 财富进度
        add_progress('millionaire', total_value, 1000000, lambda x: f"${x:,.0f}")
        add_progress('multi_millionaire', total_value, 10000000, lambda x: f"${x:,.0f}")
        add_progress('billionaire', total_value, 100000000, lambda x: f"${x:,.0f}")

        # 投资组合进度
        portfolio_count = len(portfolio_positions)
        add_progress('diversified', portfolio_count, 5)
        add_progress('portfolio_master', portfolio_count, 10)
        add_progress('portfolio_legend', portfolio_count, 20)

        # 登录连击进度
        login_streak = user_data.get('login_streak', 0)
        add_progress('streak_trader', login_streak, 5)
        add_progress('loyal_trader', login_streak, 15)
        add_progress('dedicated_trader', login_streak, 30)
        add_progress('veteran_trader', login_streak, 100)

        # 公司相关进度
        companies_created = user_data.get('companies_created', 0)
        add_progress('serial_entrepreneur', companies_created, 5)
        company_developments = user_data.get('company_developments', 0)
        add_progress('company_developer', company_developments, 10)
        companies_acquired = user_data.get('companies_acquired', 0)
        add_progress('merger_king', companies_acquired, 5)

        # 商品交易进度
        forex_trades = user_data.get('forex_trades', 0)
        add_progress('forex_expert', forex_trades, 50)
        futures_value = user_data.get('futures_value', 0)
        add_progress('futures_master', futures_value, 500000, lambda x: f"${x:,.0f}")

        # 游戏相关进度
        blackjack_wins = user_data.get('blackjack_wins', 0)
        add_progress('blackjack_winner', blackjack_wins, 10)
        roulette_profit = user_data.get('roulette_profit', 0)
        add_progress('roulette_master', roulette_profit, 25000, lambda x: f"${x:,.0f}")

        # 应用使用进度
        apps_used = len(user_data.get('apps_used', set()))
        add_progress('app_explorer', apps_used, 5)
        add_progress('app_master', apps_used, 10)

        # 家庭资产进度
        etf_owned = len(user_data.get('home_assets', {}).get('etf', {}))
        add_progress('fund_manager', etf_owned, 10)
        add_progress('mansion_owner', home_assets_value, 10000000, lambda x: f"${x:,.0f}")

        # 按进度排序（接近完成的在前）
        progress_list.sort(key=lambda x: (x['completed'], x['progress']), reverse=True)
        
        return progress_list

    def get_achievements_by_category(self, user_data):
        """按类别获取成就"""
        achievements = user_data.get('achievements', [])
        categories = {}
        
        for achievement_id, achievement in self.achievement_definitions.items():
            category = achievement['category']
            if category not in categories:
                categories[category] = {
                    'name': self._get_category_name(category),
                    'unlocked': [],
                    'locked': [],
                    'total': 0,
                    'completed': 0
                }
            
            categories[category]['total'] += 1
            if achievement_id in achievements:
                categories[category]['unlocked'].append(achievement)
                categories[category]['completed'] += 1
            else:
                categories[category]['locked'].append(achievement)
        
        # 计算完成率
        for category_data in categories.values():
            category_data['completion_rate'] = (category_data['completed'] / category_data['total'] * 100) if category_data['total'] > 0 else 0
            
        return categories

    def _get_category_name(self, category):
        """获取类别中文名称"""
        category_names = {
            'trading': '交易成就',
            'profit': '盈利成就',
            'portfolio': '投资组合',
            'wealth': '财富积累',
            'loyalty': '忠诚度',
            'risk': '风险管理',
            'advanced': '高级交易',
            'banking': '银行服务',
            'progression': '等级成长',
            'meta': '元成就',
            'special': '特殊成就',
            'company': '企业经营',
            'commodity': '商品交易',
            'gaming': '游戏娱乐',
            'home': '家庭资产',
            'apps': '应用使用',
            'market': '市场分析'
        }
        return category_names.get(category, '其他成就')

    def get_nearly_completed_achievements(self, user_data, portfolio, cash, trades_count, total_profit, threshold=80):
        """获取即将完成的成就"""
        progress_list = self.get_achievement_progress(user_data, portfolio, cash, trades_count, total_profit)
        return [ach for ach in progress_list if ach['progress'] >= threshold and not ach['completed']]

    def get_achievement_statistics(self, user_data):
        """获取成就统计信息"""
        achievements = user_data.get('achievements', [])
        total_achievements = len(self.achievement_definitions)
        completed_achievements = len(achievements)
        completion_rate = (completed_achievements / total_achievements * 100) if total_achievements > 0 else 0
        
        # 按等级统计
        tier_stats = {'bronze': 0, 'silver': 0, 'gold': 0, 'legendary': 0}
        total_reward = 0
        total_experience = 0
        
        for achievement_id in achievements:
            if achievement_id in self.achievement_definitions:
                achievement = self.achievement_definitions[achievement_id]
                tier = achievement.get('tier', 'bronze')
                if tier in tier_stats:
                    tier_stats[tier] += 1
                total_reward += achievement.get('reward', 0)
                total_experience += achievement.get('experience', 0)
        
        return {
            'total': total_achievements,
            'completed': completed_achievements,
            'completion_rate': completion_rate,
            'tier_stats': tier_stats,
            'total_reward': total_reward,
            'total_experience': total_experience
        }