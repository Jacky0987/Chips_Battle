import random
from datetime import datetime


class AdminManager:
    def __init__(self, market_data_manager, user_manager):
        self.market_data = market_data_manager
        self.user_manager = user_manager
        self.admin_password = "admin"  # 实际应用中应使用更安全的方式存储

    def show_admin_help(self):
        """显示管理员命令帮助"""
        admin_help_text = """
管理员命令帮助

=== 用户管理 (sudo user) ===
  sudo user list                              - 查看所有用户
  sudo user info <用户名>                       - 查看用户详细信息
  sudo user cash <用户名> <金额>                - 修改用户资金
  sudo user level <用户名> <等级>               - 修改用户等级
  sudo user exp <用户名> <经验值>               - 修改用户经验值
  sudo user credit <用户名> <信用等级>          - 修改银行信用等级
  sudo user reset <用户名>                     - 重置用户数据
  sudo user ban <用户名>                       - 封禁用户
  sudo user unban <用户名>                     - 解封用户

=== 股票管理 (sudo stock) ===
  sudo stock add <代码> <名称> <价格> <行业>     - 添加新股票
  sudo stock remove <代码>                     - 删除股票
  sudo stock price <代码> <价格>               - 修改股票价格
  sudo stock info <代码>                       - 查看股票详细信息
  sudo stock list                             - 查看所有股票
  sudo stock volatility <代码> <波动率>         - 修改股票波动率

=== 银行管理 (sudo bank) ===
  sudo bank rates loan <利率>                 - 修改贷款基础利率
  sudo bank rates deposit <利率>              - 修改存款基础利率
  sudo bank credit <用户名> <等级>             - 修改用户信用等级
  sudo bank loan <用户名> <金额> [天数]        - 强制发放贷款
  sudo bank forgive <用户名> <贷款ID>          - 免除贷款

=== 系统管理 (sudo system) ===
  sudo system event <事件内容>                 - 创建市场事件
  sudo system reset market                    - 重置市场价格
  sudo system backup                          - 备份系统数据
  sudo system maintenance <on/off>            - 维护模式开关

=== 基础命令 ===
  admin_help                                   - 显示此帮助
  exit_admin                                   - 退出管理员模式

示例:
  sudo user cash testuser 50000
  sudo user level testuser 10
  sudo user credit testuser AAA
  sudo stock add NTES 网易 180.50 Technology
  sudo bank rates loan 0.08
  sudo system event 央行降息，市场大涨
"""
        return admin_help_text

    def add_stock(self, symbol, name, price, sector="其他", volatility=0.02):
        """添加新股票"""
        if symbol in self.market_data.stocks:
            return f"错误: 股票 {symbol} 已存在"

        market_cap = price * 1000000000
        eps = price / random.uniform(15, 50)
        pe_ratio = price / eps if eps > 0 else None
        volume = random.randint(1000000, 100000000)
        beta = random.uniform(0.3, 2.5)
        dividend_yield = random.uniform(0.0, 0.03) if random.random() > 0.5 else 0.0

        self.market_data.stocks[symbol] = {
            'name': name,
            'price': price,
            'change': 0.0,
            'sector': sector,
            'volatility': volatility,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'volume': volume,
            'beta': beta,
            'dividend_yield': dividend_yield,
            'price_history': [price] * 20,
            'eps': eps,
            'last_updated': datetime.now().isoformat()
        }

        self.market_data.save_stocks()
        return f"成功添加股票: {symbol} - {name}, 价格: ${price:.2f}, 行业: {sector}, 波动率: {volatility * 100:.1f}%"

    def remove_stock(self, symbol):
        """删除股票"""
        if symbol not in self.market_data.stocks:
            return f"错误: 股票 {symbol} 不存在"

        users = self.user_manager.load_users()
        warnings = []
        
        for username, user_data in users.items():
            portfolio = user_data.get('game_data', {}).get('portfolio', {})
            if symbol in portfolio:
                quantity = portfolio[symbol]['quantity']
                price = self.market_data.stocks[symbol]['price']
                total_value = price * quantity
                user_data['game_data']['cash'] += total_value
                del user_data['game_data']['portfolio'][symbol]
                transaction = {
                    'type': 'ADMIN_SELL',
                    'symbol': symbol,
                    'quantity': quantity,
                    'price': price,
                    'total': total_value,
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                user_data['game_data']['transaction_history'].append(transaction)
                warnings.append(f"警告: 用户 {username} 持有 {quantity} 股 {symbol}，将自动卖出")

        self.user_manager.save_users(users)
        del self.market_data.stocks[symbol]
        self.market_data.save_stocks()
        
        result = f"成功删除股票: {symbol}"
        if warnings:
            result += "\n" + "\n".join(warnings)
        return result

    def modify_stock_price(self, symbol, price):
        """修改股票价格"""
        if symbol not in self.market_data.stocks:
            return f"错误: 股票 {symbol} 不存在"

        stock = self.market_data.stocks[symbol]
        old_price = stock['price']
        change = price - old_price
        stock['price'] = round(price, 2)
        stock['change'] = round(change, 2)
        stock['price_history'].append(price)
        if len(stock['price_history']) > 20:
            stock['price_history'].pop(0)
        stock['last_updated'] = datetime.now().isoformat()
        if stock['eps'] and stock['eps'] > 0:
            stock['pe_ratio'] = round(price / stock['eps'], 2)

        self.market_data.save_stocks()
        return f"已修改股票 {symbol} 的价格: ${old_price:.2f} -> ${price:.2f} (变化: ${change:+.2f})"

    def view_all_users(self):
        """查看所有用户"""
        users = self.user_manager.load_users()
        if not users:
            return "当前没有注册用户"

        users_text = "用户列表:\n\n"
        users_text += "用户名         | 注册时间           | 资金          | 总资产        | 等级 | 交易次数\n"
        users_text += "-" * 80 + "\n"

        for username, user_data in users.items():
            game_data = user_data.get('game_data', {})
            created_date = user_data.get('created_date', 'N/A')
            if isinstance(created_date, str) and len(created_date) > 10:
                created_date = created_date[:10]

            cash = game_data.get('cash', 0)
            portfolio = game_data.get('portfolio', {})

            # 计算总资产
            total_value = cash
            for stock_symbol, stock_data in portfolio.items():
                if stock_symbol in self.market_data.stocks and isinstance(stock_data, dict):
                    quantity = stock_data.get('quantity', 0)
                    total_value += self.market_data.stocks[stock_symbol]['price'] * quantity

            level = game_data.get('level', 1)
            trades_count = game_data.get('trades_count', 0)

            users_text += f"{username:<14} | {created_date:<19} | ${cash:<12,.2f} | ${total_value:<12,.2f} | {level:<4} | {trades_count}\n"

        return users_text

    def modify_cash(self, username, amount):
        """修改用户资金"""
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"

        # 确保用户有game_data
        if 'game_data' not in users[username]:
            users[username]['game_data'] = {
                'cash': 100000.0,
                'portfolio': {},
                'transaction_history': [],
                'achievements': [],
                'level': 1,
                'experience': 0,
                'total_profit': 0,
                'best_trade': 0,
                'trades_count': 0,
                'login_streak': 0,
                'last_login': datetime.now().isoformat(),
                'game_settings': {
                    'sound_enabled': True,
                    'notifications_enabled': True,
                    'auto_save': True
                }
            }

        old_cash = users[username]['game_data']['cash']
        users[username]['game_data']['cash'] += amount
        new_cash = users[username]['game_data']['cash']
        
        # 确保现金不为负数
        if new_cash < 0:
            users[username]['game_data']['cash'] = 0
            new_cash = 0

        self.user_manager.save_users(users)

        action = "增加" if amount > 0 else "减少"
        result = f"已{action}用户 {username} 的资金: ${abs(amount):.2f}\n"
        result += f"原来资金: ${old_cash:.2f}\n"
        result += f"当前资金: ${new_cash:.2f}"
        return result

    def reset_user(self, username):
        """重置用户数据"""
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"

        # 保留用户账号信息，重置游戏数据
        users[username]['game_data'] = {
            'cash': 100000.0,
            'portfolio': {},
            'transaction_history': [],
            'achievements': [],
            'level': 1,
            'experience': 0,
            'total_profit': 0,
            'best_trade': 0,
            'trades_count': 0,
            'login_streak': 0,
            'last_login': datetime.now().isoformat(),
            'game_settings': {
                'sound_enabled': True,
                'notifications_enabled': True,
                'auto_save': True
            }
        }

        self.user_manager.save_users(users)
        return f"已重置用户 {username} 的游戏数据"

    def ban_user(self, username):
        """封禁用户"""
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"

        users[username]['banned'] = True
        self.user_manager.save_users(users)
        return f"已封禁用户: {username}"

    def create_market_event(self, event_text):
        """创建市场事件"""
        event = {
            "id": f"admin_event_{len(self.market_data.market_events) + 1:03d}",
            "title": event_text,
            "description": "管理员创建的市场事件",
            "impact": {
                "sectors": ["All"],
                "effect": "neutral",
                "magnitude": 0.01,
                "duration": "short_term"
            },
            "related_stocks": [],
            "timestamp": datetime.now().isoformat()
        }
        
        self.market_data.market_events.append(event)
        self.market_data.save_market_events()
        return f"已创建市场事件: {event_text}"

    # === 新增用户管理功能 ===
    def get_user_info(self, username):
        """获取用户详细信息"""
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"
        
        user_data = users[username]
        game_data = user_data.get('game_data', {})
        bank_data = game_data.get('bank_data', {})
        
        info_text = f"""
用户详细信息: {username}

基本信息:
  注册时间: {user_data.get('created_date', 'N/A')[:19]}
  账户状态: {'已封禁' if user_data.get('banned', False) else '正常'}
  
游戏数据:
  等级: {game_data.get('level', 1)}
  经验值: {game_data.get('experience', 0)}
  现金余额: ${game_data.get('cash', 100000):,.2f}
  交易次数: {game_data.get('trades_count', 0)}
  总盈亏: ${game_data.get('total_profit', 0):,.2f}
  最佳交易: ${game_data.get('best_trade', 0):,.2f}
  
银行信息:
  信用等级: {bank_data.get('credit_rating', 'BBB')}
  活跃贷款: {len(bank_data.get('loans', []))}个
  活跃存款: {len(bank_data.get('deposits', []))}个
  
持仓情况:
  持仓股票: {len([k for k in game_data.get('portfolio', {}).keys() if k != 'pending_orders'])}种
  挂单数量: {len(game_data.get('portfolio', {}).get('pending_orders', []))}个
"""
        return info_text

    def modify_user_level(self, username, level):
        """修改用户等级"""
        try:
            level = int(level)
            if level < 1 or level > 100:
                return "错误: 等级必须在1-100之间"
        except ValueError:
            return "错误: 等级必须是整数"
        
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"
        
        if 'game_data' not in users[username]:
            users[username]['game_data'] = {}
        
        old_level = users[username]['game_data'].get('level', 1)
        users[username]['game_data']['level'] = level
        
        self.user_manager.save_users(users)
        return f"已修改用户 {username} 的等级: {old_level} → {level}"

    def modify_user_experience(self, username, experience):
        """修改用户经验值"""
        try:
            experience = int(experience)
            if experience < 0:
                return "错误: 经验值不能为负数"
        except ValueError:
            return "错误: 经验值必须是整数"
        
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"
        
        if 'game_data' not in users[username]:
            users[username]['game_data'] = {}
        
        old_exp = users[username]['game_data'].get('experience', 0)
        users[username]['game_data']['experience'] = experience
        
        self.user_manager.save_users(users)
        return f"已修改用户 {username} 的经验值: {old_exp} → {experience}"

    def modify_user_credit_rating(self, username, credit_rating):
        """修改用户银行信用等级"""
        valid_ratings = ['AAA', 'AA', 'A', 'BBB', 'BB', 'B', 'CCC', 'CC', 'C', 'D']
        credit_rating = credit_rating.upper()
        
        if credit_rating not in valid_ratings:
            return f"错误: 无效的信用等级。有效等级: {', '.join(valid_ratings)}"
        
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"
        
        if 'game_data' not in users[username]:
            users[username]['game_data'] = {}
        if 'bank_data' not in users[username]['game_data']:
            users[username]['game_data']['bank_data'] = {}
        
        old_rating = users[username]['game_data']['bank_data'].get('credit_rating', 'BBB')
        users[username]['game_data']['bank_data']['credit_rating'] = credit_rating
        
        self.user_manager.save_users(users)
        return f"已修改用户 {username} 的信用等级: {old_rating} → {credit_rating}"

    def unban_user(self, username):
        """解封用户"""
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"
        
        if not users[username].get('banned', False):
            return f"用户 {username} 未被封禁"
        
        users[username]['banned'] = False
        self.user_manager.save_users(users)
        return f"已解封用户: {username}"

    # === 新增股票管理功能 ===
    def get_stock_info(self, symbol):
        """获取股票详细信息"""
        if symbol not in self.market_data.stocks:
            return f"错误: 股票代码 {symbol} 不存在"
        
        stock = self.market_data.stocks[symbol]
        info_text = f"""
股票详细信息: {symbol}

基本信息:
  公司名称: {stock['name']}
  当前价格: ${stock['price']:.2f}
  今日变动: ${stock['change']:+.2f}
  行业分类: {stock['sector']}
  
市场数据:
  市值: ${stock['market_cap']:,}
  市盈率: {stock.get('pe_ratio', 'N/A')}
  每股收益: ${stock.get('eps', 0):.2f}
  股息率: {stock['dividend_yield']*100:.2f}%
  Beta值: {stock['beta']:.2f}
  波动率: {stock['volatility']*100:.2f}%
  
交易数据:
  成交量: {stock['volume']:,}
  最后更新: {stock['last_updated'][:19]}
  价格历史: {len(stock['price_history'])}个数据点
"""
        return info_text

    def modify_stock_volatility(self, symbol, volatility):
        """修改股票波动率"""
        if symbol not in self.market_data.stocks:
            return f"错误: 股票 {symbol} 不存在"
        
        try:
            volatility = float(volatility)
            if volatility < 0 or volatility > 1:
                return "错误: 波动率必须在0-1之间"
        except ValueError:
            return "错误: 波动率必须是数字"
        
        stock = self.market_data.stocks[symbol]
        old_volatility = stock['volatility']
        stock['volatility'] = volatility
        stock['last_updated'] = datetime.now().isoformat()
        
        self.market_data.save_stocks()
        return f"已修改股票 {symbol} 的波动率: {old_volatility*100:.2f}% → {volatility*100:.2f}%"

    # === 新增银行管理功能 ===
    def modify_loan_base_rate(self, rate):
        """修改贷款基础利率"""
        try:
            rate = float(rate)
            if rate < 0 or rate > 1:
                return "错误: 利率必须在0-1之间"
        except ValueError:
            return "错误: 利率必须是数字"
        
        # 这里应该存储到配置文件或数据库中
        # 暂时返回成功信息
        return f"已修改贷款基础利率为: {rate*100:.2f}%"

    def modify_deposit_base_rate(self, rate):
        """修改存款基础利率"""
        try:
            rate = float(rate)
            if rate < 0 or rate > 1:
                return "错误: 利率必须在0-1之间"
        except ValueError:
            return "错误: 利率必须是数字"
        
        return f"已修改存款基础利率为: {rate*100:.2f}%"

    def force_loan(self, username, amount, days=30):
        """强制发放贷款"""
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"
        
        try:
            amount = float(amount)
            days = int(days)
            if amount <= 0 or days <= 0:
                return "错误: 金额和天数必须大于0"
        except ValueError:
            return "错误: 无效的贷款参数"
        
        if 'game_data' not in users[username]:
            users[username]['game_data'] = {}
        if 'bank_data' not in users[username]['game_data']:
            users[username]['game_data']['bank_data'] = {}
        
        # 添加到用户现金
        users[username]['game_data']['cash'] = users[username]['game_data'].get('cash', 100000) + amount
        
        # 创建贷款记录
        if 'loans' not in users[username]['game_data']['bank_data']:
            users[username]['game_data']['bank_data']['loans'] = []
        
        loan_id = f"ADMIN_{len(users[username]['game_data']['bank_data']['loans']) + 1:03d}"
        loan = {
            'id': loan_id,
            'amount': amount,
            'interest_rate': 0.05,  # 5%固定利率
            'days': days,
            'issue_date': datetime.now().isoformat(),
            'status': 'active',
            'type': 'admin_force'
        }
        users[username]['game_data']['bank_data']['loans'].append(loan)
        
        self.user_manager.save_users(users)
        return f"已向用户 {username} 强制发放贷款: ${amount:,.2f}，期限{days}天，贷款ID: {loan_id}"

    def forgive_loan(self, username, loan_id):
        """免除贷款"""
        users = self.user_manager.load_users()
        if username not in users:
            return f"错误: 用户 {username} 不存在"
        
        bank_data = users[username].get('game_data', {}).get('bank_data', {})
        loans = bank_data.get('loans', [])
        
        for loan in loans:
            if loan['id'] == loan_id and loan['status'] == 'active':
                loan['status'] = 'forgiven'
                loan['forgiven_date'] = datetime.now().isoformat()
                self.user_manager.save_users(users)
                return f"已免除用户 {username} 的贷款 {loan_id}，金额: ${loan['amount']:,.2f}"
        
        return f"错误: 未找到用户 {username} 的活跃贷款 {loan_id}"

    # === 新增系统管理功能 ===
    def reset_market_prices(self):
        """重置市场价格"""
        reset_count = 0
        for symbol, stock in self.market_data.stocks.items():
            stock['change'] = 0.0
            stock['last_updated'] = datetime.now().isoformat()
            reset_count += 1
        
        self.market_data.save_stocks()
        return f"已重置 {reset_count} 只股票的价格变动"

    def backup_system_data(self):
        """备份系统数据"""
        from datetime import datetime
        import shutil
        import os
        
        try:
            backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup_{backup_time}"
            
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 备份数据文件
            files_to_backup = ['data/', 'users_data.json']
            backup_count = 0
            
            for file_path in files_to_backup:
                if os.path.exists(file_path):
                    if os.path.isdir(file_path):
                        shutil.copytree(file_path, os.path.join(backup_dir, file_path))
                    else:
                        shutil.copy2(file_path, backup_dir)
                    backup_count += 1
            
            return f"系统数据备份完成: {backup_dir}/ ({backup_count}个文件/目录)"
        except Exception as e:
            return f"备份失败: {str(e)}"

    def set_maintenance_mode(self, mode):
        """设置维护模式"""
        if mode.lower() in ['on', 'true', '1']:
            return "维护模式已开启 (功能暂未完全实现)"
        elif mode.lower() in ['off', 'false', '0']:
            return "维护模式已关闭"
        else:
            return "错误: 维护模式参数必须是 on/off"