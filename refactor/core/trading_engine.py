from datetime import datetime
import uuid


class TradingEngine:
    def __init__(self, market_data_manager):
        self.market_data = market_data_manager
        
    def buy_stock(self, user_portfolio, symbol, quantity, cash, order_type="market", limit_price=None):
        """执行买入股票操作"""
        if symbol not in self.market_data.stocks:
            return False, f"错误: 股票代码 {symbol} 不存在", cash

        stock = self.market_data.stocks[symbol]
        current_price = stock['price']

        if order_type == "limit":
            if limit_price is None:
                return False, "错误: 限价单必须指定限价", cash
            if limit_price < current_price:
                # 限价低于当前价格，创建挂单
                return self._create_limit_order(user_portfolio, symbol, quantity, limit_price, "BUY", cash)
            else:
                # 限价高于当前价格，按当前价格成交
                price = current_price
        else:
            # 市价单
            price = current_price

        return self._execute_buy_order(user_portfolio, symbol, quantity, price, cash, order_type)

    def sell_stock(self, user_portfolio, symbol, quantity, cash, order_type="market", limit_price=None):
        """执行卖出股票操作"""
        if symbol not in self.market_data.stocks:
            return False, f"错误: 股票代码 {symbol} 不存在", cash

        # 检查是否有足够的持仓（包括做空）
        if not self._check_sell_position(user_portfolio, symbol, quantity):
            owned = user_portfolio.get(symbol, {'quantity': 0})['quantity']
            return False, f"错误: 持股不足! 拥有 {owned} 股，尝试卖出 {quantity} 股", cash

        stock = self.market_data.stocks[symbol]
        current_price = stock['price']

        if order_type == "limit":
            if limit_price is None:
                return False, "错误: 限价单必须指定限价", cash
            if limit_price > current_price:
                # 限价高于当前价格，创建挂单
                return self._create_limit_order(user_portfolio, symbol, quantity, limit_price, "SELL", cash)
            else:
                # 限价低于当前价格，按当前价格成交
                price = current_price
        else:
            # 市价单
            price = current_price

        return self._execute_sell_order(user_portfolio, symbol, quantity, price, cash, order_type)

    def short_sell(self, user_portfolio, symbol, quantity, cash, order_type="market", limit_price=None):
        """做空股票"""
        if symbol not in self.market_data.stocks:
            return False, f"错误: 股票代码 {symbol} 不存在", cash

        stock = self.market_data.stocks[symbol]
        current_price = stock['price']

        if order_type == "limit":
            if limit_price is None:
                return False, "错误: 限价单必须指定限价", cash
            if limit_price > current_price:
                # 限价高于当前价格，创建挂单
                return self._create_limit_order(user_portfolio, symbol, quantity, limit_price, "SHORT", cash)
            else:
                price = current_price
        else:
            price = current_price

        return self._execute_short_order(user_portfolio, symbol, quantity, price, cash)

    def cover_short(self, user_portfolio, symbol, quantity, cash):
        """平仓做空"""
        if symbol not in user_portfolio:
            return False, f"错误: 没有 {symbol} 的做空仓位", cash

        position = user_portfolio[symbol]
        if position['quantity'] >= 0:
            return False, f"错误: {symbol} 不是做空仓位", cash

        short_quantity = abs(position['quantity'])
        if quantity > short_quantity:
            return False, f"错误: 做空数量不足! 做空 {short_quantity} 股，尝试平仓 {quantity} 股", cash

        stock = self.market_data.stocks[symbol]
        current_price = stock['price']

        return self._execute_cover_order(user_portfolio, symbol, quantity, current_price, cash)

    def create_stop_loss_order(self, user_portfolio, symbol, quantity, stop_price, cash):
        """创建止损单"""
        if symbol not in user_portfolio:
            return False, f"错误: 没有持有 {symbol} 股票", cash

        position = user_portfolio[symbol]
        owned_quantity = abs(position['quantity'])
        
        if quantity > owned_quantity:
            return False, f"错误: 持股不足! 拥有 {owned_quantity} 股，尝试设置 {quantity} 股止损", cash

        return self._create_stop_order(user_portfolio, symbol, quantity, stop_price, "STOP_LOSS", cash)

    def create_take_profit_order(self, user_portfolio, symbol, quantity, target_price, cash):
        """创建止盈单"""
        if symbol not in user_portfolio:
            return False, f"错误: 没有持有 {symbol} 股票", cash

        position = user_portfolio[symbol]
        owned_quantity = abs(position['quantity'])
        
        if quantity > owned_quantity:
            return False, f"错误: 持股不足! 拥有 {owned_quantity} 股，尝试设置 {quantity} 股止盈", cash

        return self._create_stop_order(user_portfolio, symbol, quantity, target_price, "TAKE_PROFIT", cash)

    def _execute_buy_order(self, user_portfolio, symbol, quantity, price, cash, order_type):
        """执行买入订单"""
        stock = self.market_data.stocks[symbol]
        
        # Apply slippage for large orders
        slippage = 0.0005 * (quantity / 1000)
        adjusted_price = price * (1 + slippage)

        # Calculate transaction cost with fee
        total_cost = adjusted_price * quantity
        transaction_fee = total_cost * 0.001
        total_cost_with_fee = total_cost + transaction_fee

        if total_cost_with_fee > cash:
            return False, f"错误: 资金不足! 需要 ${total_cost_with_fee:.2f}，但只有 ${cash:.2f}", cash

        # Execute transaction
        new_cash = cash - total_cost_with_fee
        if symbol in user_portfolio and user_portfolio[symbol]['quantity'] > 0:
            # Update average cost for long position
            current_quantity = user_portfolio[symbol]['quantity']
            current_cost = user_portfolio[symbol]['avg_cost'] * current_quantity
            new_quantity = current_quantity + quantity
            new_avg_cost = (current_cost + total_cost) / new_quantity
            user_portfolio[symbol] = {
                'quantity': new_quantity,
                'avg_cost': new_avg_cost,
                'position_type': 'long'
            }
        elif symbol in user_portfolio and user_portfolio[symbol]['quantity'] < 0:
            # 平仓做空
            short_quantity = abs(user_portfolio[symbol]['quantity'])
            if quantity >= short_quantity:
                # 完全平仓或转为多头
                remaining_quantity = quantity - short_quantity
                if remaining_quantity > 0:
                    user_portfolio[symbol] = {
                        'quantity': remaining_quantity,
                        'avg_cost': adjusted_price,
                        'position_type': 'long'
                    }
                else:
                    del user_portfolio[symbol]
            else:
                # 部分平仓
                user_portfolio[symbol]['quantity'] += quantity
        else:
            # 新建多头仓位
            user_portfolio[symbol] = {
                'quantity': quantity,
                'avg_cost': adjusted_price,
                'position_type': 'long'
            }

        # Create transaction record
        transaction = {
            'type': f'{order_type.upper()}_BUY',
            'symbol': symbol,
            'quantity': quantity,
            'price': adjusted_price,
            'total': total_cost,
            'fee': transaction_fee,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        order_type_name = "限价买入" if order_type == "limit" else "市价买入"
        success_message = f"""
    交易成功 ✓

    操作: {order_type_name}
    股票: {symbol} - {stock['name']}
    数量: {quantity} 股
    价格: ${adjusted_price:.2f}/股
    交易费用: ${transaction_fee:.2f}
    总额: ${total_cost_with_fee:.2f}
    余额: ${new_cash:.2f}
    获得经验: +10
    """

        return True, success_message, new_cash, transaction

    def _execute_sell_order(self, user_portfolio, symbol, quantity, price, cash, order_type):
        """执行卖出订单"""
        stock = self.market_data.stocks[symbol]
        
        # Apply slippage for large orders
        slippage = 0.0005 * (quantity / 1000)
        adjusted_price = price * (1 - slippage)
        
        total_value = adjusted_price * quantity
        transaction_fee = total_value * 0.001
        net_proceeds = total_value - transaction_fee

        # Calculate profit/loss
        position = user_portfolio[symbol]
        avg_cost = position['avg_cost']
        trade_profit = (adjusted_price - avg_cost) * quantity - transaction_fee

        # Execute transaction
        new_cash = cash + net_proceeds
        user_portfolio[symbol]['quantity'] -= quantity
        if user_portfolio[symbol]['quantity'] == 0:
            del user_portfolio[symbol]

        # Create transaction record
        transaction = {
            'type': f'{order_type.upper()}_SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': adjusted_price,
            'total': total_value,
            'fee': transaction_fee,
            'profit': trade_profit,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        order_type_name = "限价卖出" if order_type == "limit" else "市价卖出"
        success_message = f"""
    交易成功 ✓

    操作: {order_type_name}
    股票: {symbol} - {stock['name']}
    数量: {quantity} 股
    价格: ${adjusted_price:.2f}/股
    交易费用: ${transaction_fee:.2f}
    净收入: ${net_proceeds:.2f}
    本笔盈亏: ${trade_profit:+.2f}
    余额: ${new_cash:.2f}
    获得经验: +10
    """

        return True, success_message, new_cash, transaction, trade_profit

    def _execute_short_order(self, user_portfolio, symbol, quantity, price, cash):
        """执行做空订单"""
        stock = self.market_data.stocks[symbol]
        
        # Apply slippage
        slippage = 0.0005 * (quantity / 1000)
        adjusted_price = price * (1 - slippage)
        
        # 做空需要保证金（通常是50%）
        margin_required = adjusted_price * quantity * 0.5
        transaction_fee = adjusted_price * quantity * 0.001
        total_cost = margin_required + transaction_fee

        if total_cost > cash:
            return False, f"错误: 保证金不足! 需要 ${total_cost:.2f}，但只有 ${cash:.2f}", cash

        # Execute short sale
        new_cash = cash - total_cost
        proceeds = adjusted_price * quantity - transaction_fee

        if symbol in user_portfolio:
            if user_portfolio[symbol]['quantity'] > 0:
                # 有多头仓位，先平仓
                long_quantity = user_portfolio[symbol]['quantity']
                if quantity >= long_quantity:
                    # 完全平仓并建立空头
                    remaining_short = quantity - long_quantity
                    if remaining_short > 0:
                        user_portfolio[symbol] = {
                            'quantity': -remaining_short,
                            'avg_cost': adjusted_price,
                            'position_type': 'short'
                        }
                    else:
                        del user_portfolio[symbol]
                else:
                    # 部分平仓
                    user_portfolio[symbol]['quantity'] -= quantity
            else:
                # 增加空头仓位
                current_short = abs(user_portfolio[symbol]['quantity'])
                total_short = current_short + quantity
                # 重新计算平均成本
                current_cost = user_portfolio[symbol]['avg_cost'] * current_short
                new_avg_cost = (current_cost + adjusted_price * quantity) / total_short
                user_portfolio[symbol] = {
                    'quantity': -total_short,
                    'avg_cost': new_avg_cost,
                    'position_type': 'short'
                }
        else:
            # 新建空头仓位
            user_portfolio[symbol] = {
                'quantity': -quantity,
                'avg_cost': adjusted_price,
                'position_type': 'short'
            }

        # Create transaction record
        transaction = {
            'type': 'SHORT_SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': adjusted_price,
            'total': proceeds,
            'fee': transaction_fee,
            'margin': margin_required,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        success_message = f"""
    做空成功 ✓

    操作: 做空
    股票: {symbol} - {stock['name']}
    数量: {quantity} 股
    价格: ${adjusted_price:.2f}/股
    卖出所得: ${proceeds:.2f}
    保证金: ${margin_required:.2f}
    交易费用: ${transaction_fee:.2f}
    余额: ${new_cash:.2f}
    获得经验: +15
    """

        return True, success_message, new_cash, transaction

    def _execute_cover_order(self, user_portfolio, symbol, quantity, price, cash):
        """执行平仓做空订单"""
        stock = self.market_data.stocks[symbol]
        position = user_portfolio[symbol]
        
        # Apply slippage
        slippage = 0.0005 * (quantity / 1000)
        adjusted_price = price * (1 + slippage)
        
        total_cost = adjusted_price * quantity
        transaction_fee = total_cost * 0.001
        total_cost_with_fee = total_cost + transaction_fee

        if total_cost_with_fee > cash:
            return False, f"错误: 资金不足! 需要 ${total_cost_with_fee:.2f}，但只有 ${cash:.2f}", cash

        # Calculate profit/loss for short position
        short_avg_cost = position['avg_cost']
        trade_profit = (short_avg_cost - adjusted_price) * quantity - transaction_fee

        # Execute cover
        new_cash = cash - total_cost_with_fee
        user_portfolio[symbol]['quantity'] += quantity
        
        if user_portfolio[symbol]['quantity'] == 0:
            del user_portfolio[symbol]

        # Create transaction record
        transaction = {
            'type': 'COVER_SHORT',
            'symbol': symbol,
            'quantity': quantity,
            'price': adjusted_price,
            'total': total_cost,
            'fee': transaction_fee,
            'profit': trade_profit,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        success_message = f"""
    平仓成功 ✓

    操作: 平仓做空
    股票: {symbol} - {stock['name']}
    数量: {quantity} 股
    价格: ${adjusted_price:.2f}/股
    平仓成本: ${total_cost_with_fee:.2f}
    本笔盈亏: ${trade_profit:+.2f}
    余额: ${new_cash:.2f}
    获得经验: +15
    """

        return True, success_message, new_cash, transaction, trade_profit

    def _create_limit_order(self, user_portfolio, symbol, quantity, limit_price, order_type, cash):
        """创建限价单"""
        # 初始化挂单列表
        if 'pending_orders' not in user_portfolio:
            user_portfolio['pending_orders'] = []

        order_id = str(uuid.uuid4())[:8]
        order = {
            'id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'limit_price': limit_price,
            'order_type': order_type,
            'status': 'pending',
            'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        user_portfolio['pending_orders'].append(order)

        order_type_name = {
            'BUY': '限价买入',
            'SELL': '限价卖出',
            'SHORT': '限价做空'
        }.get(order_type, order_type)

        success_message = f"""
    挂单成功 ✓

    订单类型: {order_type_name}
    股票: {symbol}
    数量: {quantity} 股
    限价: ${limit_price:.2f}
    订单号: {order_id}
    状态: 等待成交
    
    当市场价格达到限价时将自动执行
    """

        return True, success_message, cash

    def _create_stop_order(self, user_portfolio, symbol, quantity, trigger_price, order_type, cash):
        """创建止损/止盈单"""
        if 'pending_orders' not in user_portfolio:
            user_portfolio['pending_orders'] = []

        order_id = str(uuid.uuid4())[:8]
        order = {
            'id': order_id,
            'symbol': symbol,
            'quantity': quantity,
            'trigger_price': trigger_price,
            'order_type': order_type,
            'status': 'pending',
            'created_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        user_portfolio['pending_orders'].append(order)

        order_type_name = {
            'STOP_LOSS': '止损单',
            'TAKE_PROFIT': '止盈单'
        }.get(order_type, order_type)

        success_message = f"""
    挂单成功 ✓

    订单类型: {order_type_name}
    股票: {symbol}
    数量: {quantity} 股
    触发价格: ${trigger_price:.2f}
    订单号: {order_id}
    状态: 等待触发
    
    当价格达到触发条件时将自动执行
    """

        return True, success_message, cash

    def check_pending_orders(self, user_portfolio, cash):
        """检查并执行挂单"""
        if 'pending_orders' not in user_portfolio:
            return [], cash

        executed_orders = []
        remaining_orders = []
        current_cash = cash

        for order in user_portfolio['pending_orders']:
            symbol = order['symbol']
            if symbol not in self.market_data.stocks:
                remaining_orders.append(order)
                continue

            current_price = self.market_data.stocks[symbol]['price']
            should_execute = False
            
            # 检查限价单执行条件
            if order['order_type'] in ['BUY', 'SELL', 'SHORT']:
                limit_price = order['limit_price']
                if order['order_type'] == 'BUY' and current_price <= limit_price:
                    should_execute = True
                elif order['order_type'] in ['SELL', 'SHORT'] and current_price >= limit_price:
                    should_execute = True
            
            # 检查止损/止盈单执行条件
            elif order['order_type'] in ['STOP_LOSS', 'TAKE_PROFIT']:
                trigger_price = order['trigger_price']
                position = user_portfolio.get(symbol, {})
                
                if position.get('quantity', 0) > 0:  # 多头仓位
                    if order['order_type'] == 'STOP_LOSS' and current_price <= trigger_price:
                        should_execute = True
                    elif order['order_type'] == 'TAKE_PROFIT' and current_price >= trigger_price:
                        should_execute = True
                elif position.get('quantity', 0) < 0:  # 空头仓位
                    if order['order_type'] == 'STOP_LOSS' and current_price >= trigger_price:
                        should_execute = True
                    elif order['order_type'] == 'TAKE_PROFIT' and current_price <= trigger_price:
                        should_execute = True

            if should_execute:
                # 执行订单
                if order['order_type'] == 'BUY':
                    success, message, new_cash, *extra = self._execute_buy_order(
                        user_portfolio, symbol, order['quantity'], current_price, current_cash, "limit"
                    )
                elif order['order_type'] == 'SELL' or order['order_type'] in ['STOP_LOSS', 'TAKE_PROFIT']:
                    success, message, new_cash, *extra = self._execute_sell_order(
                        user_portfolio, symbol, order['quantity'], current_price, current_cash, "limit"
                    )
                elif order['order_type'] == 'SHORT':
                    success, message, new_cash, *extra = self._execute_short_order(
                        user_portfolio, symbol, order['quantity'], current_price, current_cash
                    )
                else:
                    success = False

                if success:
                    current_cash = new_cash
                    order['status'] = 'executed'
                    order['executed_price'] = current_price
                    order['executed_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    executed_orders.append(order)
                else:
                    remaining_orders.append(order)
            else:
                remaining_orders.append(order)

        # 更新挂单列表
        user_portfolio['pending_orders'] = remaining_orders
        
        return executed_orders, current_cash

    def cancel_order(self, user_portfolio, order_id):
        """取消挂单"""
        if 'pending_orders' not in user_portfolio:
            return False, "没有待执行的订单"

        for i, order in enumerate(user_portfolio['pending_orders']):
            if order['id'] == order_id:
                cancelled_order = user_portfolio['pending_orders'].pop(i)
                return True, f"订单 {order_id} 已取消\n股票: {cancelled_order['symbol']}, 数量: {cancelled_order['quantity']}"

        return False, f"未找到订单 {order_id}"

    def _check_sell_position(self, user_portfolio, symbol, quantity):
        """检查卖出仓位是否足够"""
        if symbol not in user_portfolio:
            return False
        
        position = user_portfolio[symbol]
        owned_quantity = position.get('quantity', 0)
        
        # 多头仓位检查
        if owned_quantity > 0:
            return owned_quantity >= quantity
        
        return False

    def calculate_total_value(self, cash, portfolio):
        """计算投资组合总价值"""
        try:
            total = cash
            for symbol, data in portfolio.items():
                if symbol == 'pending_orders':
                    continue
                    
                if symbol not in self.market_data.stocks:
                    # 股票已被删除，跳过
                    continue
                    
                if not isinstance(data, dict):
                    # 数据格式错误，跳过
                    continue
                
                current_price = self.market_data.stocks[symbol]['price']
                quantity = data.get('quantity', 0)
                avg_cost = data.get('avg_cost', current_price)
                
                if quantity > 0:  # 多头仓位
                    total += current_price * quantity
                elif quantity < 0:  # 空头仓位
                    # 空头仓位的总价值计算：
                    # 原始保证金 + 浮动盈亏
                    short_quantity = abs(quantity)
                    margin = avg_cost * short_quantity  # 原始卖出金额作为保证金
                    floating_pnl = (avg_cost - current_price) * short_quantity  # 浮动盈亏
                    total += margin + floating_pnl
                    
        except Exception as e:
            print(f"计算总资产时出错: {e}")
            return cash  # 出错时返回现金余额
        
        return max(total, 0)  # 确保总资产不为负数

    def calculate_portfolio_metrics(self, portfolio, total_value):
        """计算投资组合指标"""
        if total_value == 0:
            return {
                'beta': 0,
                'volatility': 0,
                'sector_weights': {},
                'max_position_weight': 0,
                'long_positions': 0,
                'short_positions': 0
            }

        portfolio_beta = 0
        portfolio_volatility = 0
        sector_weights = {}
        position_weights = []
        long_positions = 0
        short_positions = 0

        for symbol, data in portfolio.items():
            if symbol == 'pending_orders' or symbol not in self.market_data.stocks:
                continue
                
            stock = self.market_data.stocks[symbol]
            quantity = data['quantity']
            current_price = stock['price']
            
            if quantity > 0:  # 多头仓位
                long_positions += 1
                weight = (current_price * quantity) / total_value
            else:  # 空头仓位
                short_positions += 1
                avg_cost = data['avg_cost']
                short_quantity = abs(quantity)
                weight = (avg_cost * short_quantity) / total_value
            
            portfolio_beta += abs(weight) * stock['beta']
            portfolio_volatility += abs(weight) * stock['volatility']
            
            sector = stock['sector']
            sector_weights[sector] = sector_weights.get(sector, 0) + abs(weight) * 100
            position_weights.append(abs(weight) * 100)

        return {
            'beta': portfolio_beta,
            'volatility': portfolio_volatility,
            'sector_weights': sector_weights,
            'max_position_weight': max(position_weights) if position_weights else 0,
            'long_positions': long_positions,
            'short_positions': short_positions
        } 