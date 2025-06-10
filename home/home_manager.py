"""
家庭资产投资管理系统
"""

from .etf_funds import create_etf_funds
from .luxury_cars import create_luxury_cars


class HomeManager:
    """家庭资产投资管理系统"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.etf_funds = create_etf_funds()
        self.luxury_cars = create_luxury_cars()
        self.user_assets = {}  # 用户拥有的资产
        self.load_user_assets()
    
    def load_user_assets(self):
        """加载用户资产数据"""
        user_data = self.main_app.user_data
        if user_data and 'home_assets' in user_data:
            self.user_assets = user_data['home_assets']
        else:
            self.user_assets = {}
    
    def save_user_assets(self):
        """保存用户资产数据"""
        if not self.main_app.user_data:
            self.main_app.user_data = {}
        self.main_app.user_data['home_assets'] = self.user_assets
        self.main_app.save_game_data()
    
    def show_home_menu(self):
        """显示家庭投资理财主菜单"""
        total_etf_value = sum(
            self.etf_funds[etf_id].get_value() * quantity 
            for etf_id, quantity in self.user_assets.get('etf', {}).items()
        )
        total_car_value = sum(
            self.luxury_cars[car_id].get_value() * quantity 
            for car_id, quantity in self.user_assets.get('cars', {}).items()
        )
        total_portfolio_value = total_etf_value + total_car_value
        
        return f"""
══════════════════════════════════════════════════════════════════════════════════════════
                            🏠 家庭投资理财中心 🏠                                         
                        探索多元化投资机会，打造财富人生                                   
══════════════════════════════════════════════════════════════════════════════════════════

💰 投资概况:
  现金余额: ${self.main_app.cash:,.2f}
  ETF投资总值: ${total_etf_value:,.2f}
  豪车收藏总值: ${total_car_value:,.2f}
  投资组合总值: ${total_portfolio_value:,.2f}

🏡 家居功能:
  🏠 home interior          - 查看我的家居和藏品展示
  📊 home portfolio         - 投资组合管理
  📈 home etf              - ETF基金投资市场
  🚗 home cars             - 豪华车收藏市场
  🌍 home market           - 综合投资市场概览

💡 快速操作:
  home buy etf <基金ID> <份额>     - 购买ETF基金
  home buy car <车辆ID> <数量>     - 购买豪华车收藏
  home sell etf <基金ID> <份额>    - 出售ETF基金
  home sell car <车辆ID> <数量>    - 出售豪华车
  home info etf <基金ID>          - 查看ETF详细信息
  home info car <车辆ID>          - 查看豪车详细信息

🏆 投资理念: 分散投资，长期持有，追求稳健收益与生活品质的完美结合！
"""

    def show_home_interior(self):
        """显示家居内景和藏品展示"""
        # 计算藏品价值
        etf_items = []
        car_items = []
        total_value = 0
        
        # ETF基金藏品
        for etf_id, quantity in self.user_assets.get('etf', {}).items():
            if quantity > 0 and etf_id in self.etf_funds:
                etf = self.etf_funds[etf_id]
                etf.update_price()
                value = etf.get_value() * quantity
                total_value += value
                etf_items.append({
                    'name': etf.name,
                    'quantity': quantity,
                    'value': value,
                    'rarity': etf.rarity_info['name']
                })
        
        # 豪华车藏品
        for car_id, quantity in self.user_assets.get('cars', {}).items():
            if quantity > 0 and car_id in self.luxury_cars:
                car = self.luxury_cars[car_id]
                car.update_price()
                value = car.get_value() * quantity
                total_value += value
                car_items.append({
                    'name': car.name,
                    'quantity': quantity,
                    'value': value,
                    'brand': car.brand,
                    'year': car.year
                })
        
        # 根据藏品价值确定家居等级
        if total_value >= 10000000:  # 1000万
            home_level = "豪华别墅"
            home_emoji = "🏰"
            home_desc = "顶级豪华别墅，配备私人车库、酒窖和艺术品展示厅"
        elif total_value >= 5000000:  # 500万
            home_level = "高档公寓"
            home_emoji = "🏢"
            home_desc = "市中心高档公寓，俯瞰城市美景，配备专业展示柜"
        elif total_value >= 1000000:  # 100万
            home_level = "精装住宅"
            home_emoji = "🏠"
            home_desc = "精装修住宅，拥有专门的收藏展示区域"
        elif total_value >= 100000:  # 10万
            home_level = "温馨小屋"
            home_emoji = "🏡"
            home_desc = "温馨的小屋，开始了投资理财的人生"
        else:
            home_level = "简约居所"
            home_emoji = "🏘️"
            home_desc = "简约而温馨的起居空间"
        
        interior_display = f"""
══════════════════════════════════════════════════════════════════════════════════════════
                               {home_emoji} 我的家 - {home_level} {home_emoji}                               
                              {home_desc}                               
══════════════════════════════════════════════════════════════════════════════════════════

🏠 房屋信息:
  等级: {home_level}
  总藏品价值: ${total_value:,.2f}
  现金余额: ${self.main_app.cash:,.2f}
  投资品类: {len([k for k in [etf_items, car_items] if k])}种

🎨 艺术品与收藏展示厅
─────────────────────────────────────────────────────────────────────────────────
                                📈 金融投资藏品                                  
─────────────────────────────────────────────────────────────────────────────────
"""
        
        if etf_items:
            interior_display += "\n💎 ETF基金收藏:\n"
            for item in sorted(etf_items, key=lambda x: x['value'], reverse=True):
                rarity_emoji = {"普通": "⚪", "稀有": "🔵", "史诗": "🟣", "传说": "🟠"}.get(item['rarity'], "⚪")
                interior_display += f"  {rarity_emoji} {item['name']} × {item['quantity']}\n"
                interior_display += f"     💰 价值: ${item['value']:,.2f} | 稀有度: {item['rarity']}\n"
        else:
            interior_display += "\n💎 ETF基金收藏: 暂无收藏\n"
        
        interior_display += "\n" + "─" * 85 + "\n"
        
        if car_items:
            interior_display += "\n🚗 豪华车收藏车库:\n"
            for item in sorted(car_items, key=lambda x: x['value'], reverse=True):
                interior_display += f"  🏎️ {item['brand']} {item['name']} ({item['year']}) × {item['quantity']}\n"
                interior_display += f"     💰 价值: ${item['value']:,.2f} | 经典收藏\n"
        else:
            interior_display += "\n🚗 豪华车收藏车库: 暂无收藏\n"
        
        # 添加房间功能区域
        interior_display += f"""

🏡 功能区域:
─────────────────────────────────────────────────────────────────────
   📊 投资室        🍷 酒窖          🎮 娱乐室        📚 书房        
 分析投资数据     珍藏美酒佳酿     休闲娱乐放松     学习投资知识     
                                                                 
 home portfolio   (未来功能)      appmarket       help            
─────────────────────────────────────────────────────────────────────

🌟 升级提示:
  当前等级: {home_level}
  下级要求: {"已达最高等级" if home_level == "豪华别墅" else f"藏品价值达到{['$100,000', '$1,000,000', '$5,000,000', '$10,000,000'][['简约居所', '温馨小屋', '精装住宅', '高档公寓'].index(home_level) + 1] if home_level != '豪华别墅' else ''}"}

💡 家居管理:
  home portfolio              - 查看详细投资组合
  home market                 - 浏览投资市场
  home buy <类型> <ID> <数量>  - 购买新的收藏品
  home sell <类型> <ID> <数量> - 出售收藏品

🎯 生活哲学: 投资不仅是财富的增长，更是生活品质的提升！
"""
        
        return interior_display

    def show_etf_market(self):
        """显示ETF基金市场"""
        etf_text = f"""
📊 ETF基金投资市场

══════════════════════════════════════════════════════════════════════════════════════════
                              📊 ETF基金投资中心 📊                                       
                           专业管理·分散风险·稳定收益                                      
══════════════════════════════════════════════════════════════════════════════════════════

💰 您的资金: ${self.main_app.cash:,.2f}

🏆 可投资ETF基金:

"""
        
        for etf_id, etf in self.etf_funds.items():
            etf.update_price()  # 更新价格
            rarity_info = etf.get_rarity_info()
            holding = self.user_assets.get(f"etf_{etf_id}", {}).get('quantity', 0)
            
            etf_text += f"""
─────────────────────────────────────────────────────────────────────────────────────────
 {etf.emoji} {etf.name} {rarity_info['color']}                                              
─────────────────────────────────────────────────────────────────────────────────────────
 ID: {etf_id:<10} | 净值: ${etf.current_price:>8.2f} | 趋势: {etf.get_price_trend():<10} 
 费用率: {etf.expense_ratio:.2f}%   | 分红率: {etf.dividend_yield:.2f}%   | 持有: {holding}份           
 稀有度: {rarity_info['name']:<4} | 行业: {etf.sector:<12}                        
─────────────────────────────────────────────────────────────────────────────────────────
 📝 {etf.description[:60]}...                                                                
─────────────────────────────────────────────────────────────────────────────────────────

"""
        
        etf_text += f"""
🎮 交易操作:
  home buy etf <ETF_ID> <份额>     # 购买ETF份额
  home sell etf <ETF_ID> <份额>    # 赎回ETF份额
  home info etf <ETF_ID>           # 查看详细信息

💡 投资建议:
  • ETF基金适合长期投资，分散风险
  • 关注费用率，选择低成本基金
  • 定期定额投资效果更佳
  • 注意稀有度，传奇ETF升值潜力巨大
"""
        
        return etf_text

    def show_cars_market(self):
        """显示豪华车收藏市场"""
        cars_text = f"""
🚗 豪华车收藏投资市场

══════════════════════════════════════════════════════════════════════════════════════════
                             🚗 豪华车收藏投资中心 🚗                                      
                          稀有典藏·升值保值·彰显品味                                       
══════════════════════════════════════════════════════════════════════════════════════════

💰 您的资金: ${self.main_app.cash:,.2f}

🏆 可收藏豪华车型:

"""
        
        for car_id, car in self.luxury_cars.items():
            car.update_price()  # 更新价格
            rarity_info = car.get_rarity_info()
            holding = self.user_assets.get(f"car_{car_id}", {}).get('quantity', 0)
            
            cars_text += f"""
─────────────────────────────────────────────────────────────────────────────────────────
 {car.emoji} {car.name} {rarity_info['color']}                                              
─────────────────────────────────────────────────────────────────────────────────────────
 ID: {car_id:<10} | 价格: ${car.current_price:>10,.0f} | 趋势: {car.get_price_trend():<10} 
 品牌: {car.brand:<8} | 年份: {car.year:<6} | 持有: {holding}辆                 
 稀有度: {rarity_info['name']:<4} | 车况: 优秀                        
─────────────────────────────────────────────────────────────────────────────────────────
 📝 {car.description[:60]}...                                                                
─────────────────────────────────────────────────────────────────────────────────────────

"""
        
        cars_text += f"""
🎮 交易操作:
  home buy car <CAR_ID> <数量>     # 购买豪华车
  home sell car <CAR_ID> <数量>    # 出售豪华车
  home info car <CAR_ID>           # 查看详细信息

💡 投资建议:
  • 豪华车具有保值升值特性
  • 限量版和稀有车型升值潜力更大
  • 关注品牌影响力和历史意义
  • 传奇级豪车是终极收藏目标
"""
        
        return cars_text

    def buy_asset(self, asset_type, asset_id, quantity):
        """购买资产"""
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return "❌ 购买数量必须大于0"
        except ValueError:
            return "❌ 无效的购买数量"
        
        # 获取资产信息
        if asset_type == 'etf':
            if asset_id not in self.etf_funds:
                return f"❌ ETF基金 {asset_id} 不存在"
            asset = self.etf_funds[asset_id]
            asset_key = f"etf_{asset_id}"
        elif asset_type == 'car':
            if asset_id not in self.luxury_cars:
                return f"❌ 豪华车 {asset_id} 不存在"
            asset = self.luxury_cars[asset_id]
            asset_key = f"car_{asset_id}"
        else:
            return "❌ 无效的资产类型，请使用 etf 或 car"
        
        # 更新价格
        asset.update_price()
        total_cost = asset.current_price * quantity
        
        # 检查资金
        if total_cost > self.main_app.cash:
            return f"❌ 资金不足，需要 ${total_cost:,.2f}，当前余额 ${self.main_app.cash:,.2f}"
        
        # 执行购买
        self.main_app.cash -= total_cost
        
        # 更新持仓
        if asset_key not in self.user_assets:
            self.user_assets[asset_key] = {
                'asset_type': asset_type,
                'asset_id': asset_id,
                'quantity': 0,
                'total_cost': 0,
                'purchase_date': None
            }
        
        self.user_assets[asset_key]['quantity'] += quantity
        self.user_assets[asset_key]['total_cost'] += total_cost
        if self.user_assets[asset_key]['purchase_date'] is None:
            from datetime import datetime
            self.user_assets[asset_key]['purchase_date'] = datetime.now().isoformat()
        
        self.save_user_assets()
        
        return f"""
✅ 购买成功！

💎 资产信息:
  名称: {asset.name}
  类型: {asset_type.upper()}
  购买数量: {quantity}
  单价: ${asset.current_price:,.2f}
  总金额: ${total_cost:,.2f}

💰 账户变动:
  支付金额: ${total_cost:,.2f}
  剩余余额: ${self.main_app.cash:,.2f}

📊 持仓更新:
  持有数量: {self.user_assets[asset_key]['quantity']}
  总投入: ${self.user_assets[asset_key]['total_cost']:,.2f}
  平均成本: ${self.user_assets[asset_key]['total_cost'] / self.user_assets[asset_key]['quantity']:,.2f}
"""

    def sell_asset(self, asset_type, asset_id, quantity):
        """出售资产"""
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return "❌ 出售数量必须大于0"
        except ValueError:
            return "❌ 无效的出售数量"
        
        asset_key = f"{asset_type}_{asset_id}"
        
        # 检查持仓
        if asset_key not in self.user_assets or self.user_assets[asset_key]['quantity'] == 0:
            return f"❌ 您没有持有该资产"
        
        if quantity > self.user_assets[asset_key]['quantity']:
            return f"❌ 持仓不足，您持有 {self.user_assets[asset_key]['quantity']} 份"
        
        # 获取资产信息
        if asset_type == 'etf':
            if asset_id not in self.etf_funds:
                return f"❌ ETF基金 {asset_id} 不存在"
            asset = self.etf_funds[asset_id]
        elif asset_type == 'car':
            if asset_id not in self.luxury_cars:
                return f"❌ 豪华车 {asset_id} 不存在"
            asset = self.luxury_cars[asset_id]
        else:
            return "❌ 无效的资产类型"
        
        # 更新价格
        asset.update_price()
        total_value = asset.current_price * quantity
        
        # 计算成本和盈亏
        avg_cost = self.user_assets[asset_key]['total_cost'] / self.user_assets[asset_key]['quantity']
        cost_basis = avg_cost * quantity
        profit_loss = total_value - cost_basis
        
        # 执行出售
        self.main_app.cash += total_value
        self.user_assets[asset_key]['quantity'] -= quantity
        self.user_assets[asset_key]['total_cost'] -= cost_basis
        
        # 如果全部卖出，清理记录
        if self.user_assets[asset_key]['quantity'] == 0:
            self.user_assets[asset_key]['total_cost'] = 0
        
        self.save_user_assets()
        
        return f"""
✅ 出售成功！

💎 资产信息:
  名称: {asset.name}
  类型: {asset_type.upper()}
  出售数量: {quantity}
  当前单价: ${asset.current_price:,.2f}
  总价值: ${total_value:,.2f}

💰 交易结果:
  获得资金: ${total_value:,.2f}
  成本基础: ${cost_basis:,.2f}
  盈亏金额: ${profit_loss:+,.2f}
  盈亏比例: {(profit_loss/cost_basis)*100:+.2f}%

💰 账户更新:
  当前余额: ${self.main_app.cash:,.2f}
  剩余持仓: {self.user_assets[asset_key]['quantity']}
"""

    def show_portfolio(self):
        """显示投资组合"""
        if not any(asset.get('quantity', 0) > 0 for asset in self.user_assets.values()):
            return """
📊 我的投资组合

暂无投资，开始您的多元化投资之旅吧！

🎮 快速开始:
  home etf    # 浏览ETF基金
  home cars   # 浏览豪华车收藏
"""
        
        portfolio_text = f"""
📊 我的家庭投资组合

══════════════════════════════════════════════════════════════════════════════════════════
                            📊 投资组合总览 📊                                            
══════════════════════════════════════════════════════════════════════════════════════════

"""
        
        total_invested = 0
        total_current_value = 0
        
        # ETF投资
        etf_holdings = {k: v for k, v in self.user_assets.items() if k.startswith('etf_') and v.get('quantity', 0) > 0}
        if etf_holdings:
            portfolio_text += "📊 ETF基金投资:\n\n"
            for asset_key, holding in etf_holdings.items():
                etf_id = asset_key.replace('etf_', '')
                if etf_id in self.etf_funds:
                    etf = self.etf_funds[etf_id]
                    etf.update_price()
                    
                    current_value = etf.current_price * holding['quantity']
                    profit_loss = current_value - holding['total_cost']
                    profit_pct = (profit_loss / holding['total_cost']) * 100 if holding['total_cost'] > 0 else 0
                    
                    total_invested += holding['total_cost']
                    total_current_value += current_value
                    
                    portfolio_text += f"""  {etf.emoji} {etf.name}
    持有份额: {holding['quantity']} | 当前净值: ${etf.current_price:.2f}
    总投入: ${holding['total_cost']:,.2f} | 当前价值: ${current_value:,.2f}
    盈亏: ${profit_loss:+,.2f} ({profit_pct:+.1f}%) | 趋势: {etf.get_price_trend()}

"""
        
        # 豪华车收藏
        car_holdings = {k: v for k, v in self.user_assets.items() if k.startswith('car_') and v.get('quantity', 0) > 0}
        if car_holdings:
            portfolio_text += "🚗 豪华车收藏:\n\n"
            for asset_key, holding in car_holdings.items():
                car_id = asset_key.replace('car_', '')
                if car_id in self.luxury_cars:
                    car = self.luxury_cars[car_id]
                    car.update_price()
                    
                    current_value = car.current_price * holding['quantity']
                    profit_loss = current_value - holding['total_cost']
                    profit_pct = (profit_loss / holding['total_cost']) * 100 if holding['total_cost'] > 0 else 0
                    
                    total_invested += holding['total_cost']
                    total_current_value += current_value
                    
                    portfolio_text += f"""  {car.emoji} {car.name}
    持有数量: {holding['quantity']} | 当前价格: ${car.current_price:,.0f}
    总投入: ${holding['total_cost']:,.2f} | 当前价值: ${current_value:,.2f}
    盈亏: ${profit_loss:+,.2f} ({profit_pct:+.1f}%) | 趋势: {car.get_price_trend()}

"""
        
        # 总结
        total_profit_loss = total_current_value - total_invested
        total_profit_pct = (total_profit_loss / total_invested) * 100 if total_invested > 0 else 0
        
        portfolio_text += f"""
══════════════════════════════════════════════════════════════════════════════════════════
                                  💰 投资总览 💰                                          
══════════════════════════════════════════════════════════════════════════════════════════
 总投入金额: ${total_invested:>15,.2f}                                                       
 当前价值: ${total_current_value:>17,.2f}                                                   
 总盈亏: ${total_profit_loss:>19,+.2f} ({total_profit_pct:+.1f}%)                            
 现金余额: ${self.main_app.cash:>17,.2f}                                                     
 总资产: ${self.main_app.cash + total_current_value:>19,.2f}                                 
══════════════════════════════════════════════════════════════════════════════════════════

🎮 管理操作:
  home buy <类型> <ID> <数量>   # 继续投资
  home sell <类型> <ID> <数量>  # 出售资产
  home market                  # 查看市场行情
"""
        
        return portfolio_text 