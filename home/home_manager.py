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
        """显示家庭投资菜单"""
        menu_text = f"""
═══════════════════════════════════════════════════════════════════════════════════════
                                    🏠 家庭投资理财中心
═══════════════════════════════════════════════════════════════════════════════════════

💰 我的资产概览:
  现金余额: J${self.main_app.cash:,.2f}
  投资资产总值: J${self._calculate_total_asset_value():,.2f}
  资产增值: J${self._calculate_total_profit_loss():+,.2f}

🏡 投资板块:
  [1] 🏠 房地产投资         - 购买住宅、商业地产获得租金收益
  [2] 🎨 艺术品收藏         - 投资名画、古董等收藏品
  [3] 🚗 豪华车投资         - 收藏限量版豪车和经典车型
  [4] 📈 ETF基金投资        - 购买各类指数基金分散风险
  [5] 💎 珠宝首饰投资       - 投资钻石、黄金等贵金属
  [6] 🍷 高端消费品         - 红酒、雪茄、手表等奢侈品

🛒 生活服务:
  [7] 🎯 私人定制服务       - 享受高端定制化服务
  [8] 🌟 会员俱乐部         - 加入各类精英会员俱乐部
  [9] 🎓 教育培训投资       - 投资个人技能和知识提升
  [10] 🏥 健康医疗服务      - 高端医疗和健康管理
  [11] 🎪 娱乐休闲消费      - 旅游、娱乐等生活享受

📊 资产管理:
  [12] 📋 查看投资组合      - 详细查看所有投资资产
  [13] 💹 资产收益报告      - 分析投资收益和风险
  [14] 🔄 资产重新配置      - 调整投资组合比例

使用方法:
  home real_estate          - 查看房地产投资
  home art                  - 查看艺术品市场
  home luxury               - 查看奢侈品消费
  home services             - 查看生活服务
  home portfolio            - 查看投资组合
  
💡 温馨提示: 多元化投资可以降低风险，提高长期收益！
═══════════════════════════════════════════════════════════════════════════════════════
"""
        return menu_text

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

    def show_real_estate_market(self):
        """显示房地产投资市场"""
        properties = self._get_real_estate_properties()
        
        result = f"""
🏠 房地产投资市场

💰 投资概览:
  最低投资金额: J$5,000,000 (500万)
  预期年化收益: 8-15%
  投资风险等级: ⭐⭐⭐ (中等)

🏘️ 可投资物业:
{'物业名称':<20} {'类型':<8} {'价格(万)':<12} {'预期收益率':<12} {'地段':<15}
──────────────────────────────────────────────────────────────────────────
"""
        
        for prop in properties:
            result += f"{prop['name']:<18} {prop['type']:<6} {prop['price']/10000:<10.0f} {prop['yield']*100:<10.1f}% {prop['location']:<13}\n"
        
        result += f"""

📈 投资建议:
  • 住宅物业: 稳定租金收入，适合长期投资
  • 商业地产: 收益率较高，但需要更多资金
  • 工业地产: 长期租约，收入稳定
  • 海外地产: 分散地域风险，货币对冲

💡 使用方法:
  home buy real_estate <物业ID> <数量>  - 购买房地产
  home sell real_estate <物业ID> <数量> - 出售房地产
"""
        return result

    def show_art_collection_market(self):
        """显示艺术品收藏市场"""
        artworks = self._get_art_collection_items()
        
        result = f"""
🎨 艺术品收藏市场

🖼️ 收藏概览:
  入门门槛: J$500,000 (50万)
  预期增值: 12-25% (年化)
  投资风险: ⭐⭐⭐⭐ (较高)

🎭 精品推荐:
{'作品名称':<25} {'艺术家':<15} {'类型':<8} {'价格(万)':<10} {'稀有度':<8}
──────────────────────────────────────────────────────────────────────────
"""
        
        for art in artworks:
            rarity_stars = "⭐" * art['rarity_level']
            result += f"{art['name']:<23} {art['artist']:<13} {art['type']:<6} {art['price']/10000:<8.0f} {rarity_stars:<6}\n"
        
        result += f"""

🎯 收藏策略:
  • 新兴艺术家: 价格相对较低，升值潜力大
  • 知名大师: 价格较高但相对稳定
  • 古董文物: 历史价值，稀缺性强
  • 现代艺术: 市场活跃，流动性好

💡 收藏贴士:
  - 关注艺术家的展览和拍卖记录
  - 考虑作品的保存和保险成本
  - 分散投资不同类型和年代的作品

🔧 使用方法:
  home buy art <作品ID> <数量>     - 购买艺术品
  home sell art <作品ID> <数量>    - 出售艺术品
"""
        return result

    def show_luxury_consumption(self):
        """显示奢侈品消费"""
        luxuries = self._get_luxury_items()
        
        result = f"""
🍷 高端奢侈品消费

💎 消费体验:
  品质保证: 顶级奢侈品牌
  升值潜力: 部分限量款具有收藏价值
  身份象征: 彰显个人品味和地位

🛍️ 精选商品:
{'商品名称':<25} {'品牌':<15} {'类型':<10} {'价格(万)':<10} {'稀有度':<8}
──────────────────────────────────────────────────────────────────────────
"""
        
        for luxury in luxuries:
            rarity_display = {1: "普通", 2: "稀有", 3: "传奇", 4: "神话", 5: "至尊"}
            result += f"{luxury['name']:<23} {luxury['brand']:<13} {luxury['category']:<8} {luxury['price']/10000:<8.1f} {rarity_display.get(luxury['rarity'], '未知'):<6}\n"
        
        result += f"""

🎯 消费建议:
  • 手表珠宝: 保值性强，可以传承
  • 限量版酒类: 随时间增值，适合收藏
  • 高端电子产品: 享受最新科技
  • 定制服装: 彰显个人品味

⚠️ 消费提醒:
  - 奢侈品主要用于享受，升值为辅
  - 注意保养和保存条件
  - 理性消费，量力而行

🔧 使用方法:
  home buy luxury <商品ID> <数量>   - 购买奢侈品
  home use luxury <商品ID>          - 使用/体验奢侈品
"""
        return result

    def show_lifestyle_services(self):
        """显示生活服务"""
        services = self._get_lifestyle_services()
        
        result = f"""
🌟 高端生活服务

🎯 服务理念:
  专业定制: 量身定制的个性化服务
  品质保证: 顶级服务提供商
  全程管家: 一站式生活解决方案

🔥 热门服务:
{'服务名称':<25} {'类型':<12} {'价格':<15} {'时长':<10} {'评级':<8}
──────────────────────────────────────────────────────────────────────────
"""
        
        for service in services:
            stars = "⭐" * service['rating']
            result += f"{service['name']:<23} {service['category']:<10} J${service['price']:,}<13 {service['duration']:<8} {stars:<6}\n"
        
        result += f"""

🎨 服务分类:
  • 私人定制: 专属设计师、私人管家
  • 教育培训: 语言学习、技能提升、MBA课程
  • 健康医疗: 高端体检、基因检测、心理咨询
  • 娱乐休闲: 私人游艇、高尔夫会籍、度假村

💰 投资回报:
  - 教育培训可提升个人能力和收入潜力
  - 健康服务是对未来的重要投资
  - 网络建设有助于商业机会发现

🔧 使用方法:
  home buy service <服务ID>         - 购买生活服务
  home club                         - 查看会员俱乐部
"""
        return result

    def show_club_memberships(self):
        """显示会员俱乐部"""
        clubs = self._get_club_memberships()
        
        result = f"""
🏆 精英会员俱乐部

🌟 会员特权:
  专属网络: 结识各行业精英人士
  优质资源: 获取稀缺投资机会
  尊贵体验: 享受顶级设施和服务

🎯 俱乐部推荐:
{'俱乐部名称':<25} {'类型':<12} {'年费(万)':<12} {'门槛':<15} {'特色':<15}
──────────────────────────────────────────────────────────────────────────
"""
        
        for club in clubs:
            result += f"{club['name']:<23} {club['type']:<10} {club['annual_fee']/10000:<10.1f} {club['requirement']:<13} {club['feature']:<13}\n"
        
        result += f"""

🎨 俱乐部类型:
  • 商务俱乐部: 商业networking，投资机会
  • 高尔夫俱乐部: 运动社交，商务洽谈
  • 艺术俱乐部: 文化交流，艺术品投资
  • 美食俱乐部: 顶级餐饮，生活品质

💡 会员收益:
  - 扩展高质量人脉圈
  - 获得独家投资机会
  - 提升个人社会地位
  - 享受专属优质服务

🔧 使用方法:
  home join club <俱乐部ID>         - 申请加入俱乐部
  home club events                  - 查看俱乐部活动
"""
        return result

    def _get_real_estate_properties(self):
        """获取房地产投资选项"""
        return [
            {"id": "luxury_apt_01", "name": "城央豪华公寓", "type": "住宅", "price": 8000000, "yield": 0.08, "location": "市中心"},
            {"id": "office_tower_01", "name": "甲级写字楼", "type": "商办", "price": 15000000, "yield": 0.12, "location": "商务区"},
            {"id": "shopping_mall_01", "name": "大型购物中心", "type": "商业", "price": 50000000, "yield": 0.15, "location": "新区"},
            {"id": "villa_01", "name": "海景别墅", "type": "别墅", "price": 20000000, "yield": 0.06, "location": "海滨"},
            {"id": "warehouse_01", "name": "现代化仓储", "type": "工业", "price": 12000000, "yield": 0.10, "location": "物流园"},
            {"id": "overseas_apt_01", "name": "纽约公寓", "type": "海外", "price": 25000000, "yield": 0.09, "location": "曼哈顿"},
        ]

    def _get_art_collection_items(self):
        """获取艺术品收藏选项"""
        return [
            {"id": "painting_01", "name": "印象派油画", "artist": "莫奈", "type": "油画", "price": 5000000, "rarity_level": 4},
            {"id": "sculpture_01", "name": "现代雕塑", "artist": "罗丹", "type": "雕塑", "price": 3000000, "rarity_level": 3},
            {"id": "antique_01", "name": "明代青花瓷", "artist": "景德镇", "type": "古董", "price": 8000000, "rarity_level": 5},
            {"id": "calligraphy_01", "name": "书法作品", "artist": "王羲之", "type": "书法", "price": 12000000, "rarity_level": 5},
            {"id": "jade_01", "name": "和田玉摆件", "artist": "工艺大师", "type": "玉器", "price": 2000000, "rarity_level": 3},
            {"id": "modern_art_01", "name": "当代艺术", "artist": "毕加索", "type": "现代", "price": 15000000, "rarity_level": 4},
        ]

    def _get_luxury_items(self):
        """获取奢侈品选项"""
        return [
            {"id": "watch_01", "name": "百达翡丽手表", "brand": "Patek Philippe", "category": "手表", "price": 2000000, "rarity": 4},
            {"id": "wine_01", "name": "82年拉菲", "brand": "Lafite", "category": "红酒", "price": 500000, "rarity": 3},
            {"id": "jewelry_01", "name": "卡地亚钻戒", "brand": "Cartier", "category": "珠宝", "price": 1500000, "rarity": 3},
            {"id": "bag_01", "name": "爱马仕铂金包", "brand": "Hermès", "category": "包包", "price": 800000, "rarity": 4},
            {"id": "cigar_01", "name": "古巴雪茄", "brand": "Cohiba", "category": "雪茄", "price": 100000, "rarity": 2},
            {"id": "tech_01", "name": "限量版手机", "brand": "Vertu", "category": "电子", "price": 300000, "rarity": 2},
        ]

    def _get_lifestyle_services(self):
        """获取生活服务选项"""
        return [
            {"id": "butler_01", "name": "私人管家服务", "category": "定制服务", "price": 500000, "duration": "1年", "rating": 5},
            {"id": "mba_01", "name": "顶级MBA课程", "category": "教育培训", "price": 2000000, "duration": "2年", "rating": 5},
            {"id": "health_01", "name": "全套基因检测", "category": "健康医疗", "price": 300000, "duration": "1次", "rating": 4},
            {"id": "yacht_01", "name": "私人游艇租赁", "category": "娱乐休闲", "price": 1000000, "duration": "1年", "rating": 5},
            {"id": "chef_01", "name": "米其林主厨", "category": "定制服务", "price": 200000, "duration": "6个月", "rating": 5},
            {"id": "trainer_01", "name": "私人健身教练", "category": "健康医疗", "price": 150000, "duration": "1年", "rating": 4},
        ]

    def _get_club_memberships(self):
        """获取会员俱乐部选项"""
        return [
            {"id": "business_club_01", "name": "企业家俱乐部", "type": "商务", "annual_fee": 1000000, "requirement": "资产1000万+", "feature": "投资机会"},
            {"id": "golf_club_01", "name": "皇家高尔夫", "type": "运动", "annual_fee": 500000, "requirement": "会员推荐", "feature": "18洞球场"},
            {"id": "art_club_01", "name": "艺术收藏协会", "type": "文化", "annual_fee": 300000, "requirement": "收藏经验", "feature": "拍卖预览"},
            {"id": "wine_club_01", "name": "品酒师协会", "type": "美食", "annual_fee": 200000, "requirement": "品酒认证", "feature": "私人酒窖"},
            {"id": "tech_club_01", "name": "科技创新联盟", "type": "科技", "annual_fee": 800000, "requirement": "科技背景", "feature": "创业孵化"},
        ]

    def buy_real_estate(self, property_id, quantity):
        """购买房地产"""
        properties = self._get_real_estate_properties()
        property_data = next((p for p in properties if p["id"] == property_id), None)
        
        if not property_data:
            return False, "❌ 房产不存在"
            
        total_cost = property_data["price"] * quantity
        
        if self.main_app.cash < total_cost:
            return False, f"❌ 资金不足，需要 J${total_cost:,.0f}"
            
        # 扣除资金
        self.main_app.cash -= total_cost
        
        # 添加到资产
        if "real_estate" not in self.user_assets:
            self.user_assets["real_estate"] = {}
            
        if property_id not in self.user_assets["real_estate"]:
            self.user_assets["real_estate"][property_id] = {
                "name": property_data["name"],
                "quantity": 0,
                "total_cost": 0,
                "purchase_dates": [],
                "annual_yield": property_data["yield"]
            }
            
        self.user_assets["real_estate"][property_id]["quantity"] += quantity
        self.user_assets["real_estate"][property_id]["total_cost"] += total_cost
        self.user_assets["real_estate"][property_id]["purchase_dates"].append(datetime.now().isoformat())
        
        self.save_user_assets()
        
        return True, f"✅ 成功购买 {property_data['name']} x{quantity}，投入 J${total_cost:,.0f}，预期年收益率 {property_data['yield']*100:.1f}%"

    def buy_luxury_item(self, item_id, quantity):
        """购买奢侈品"""
        luxuries = self._get_luxury_items()
        item_data = next((item for item in luxuries if item["id"] == item_id), None)
        
        if not item_data:
            return False, "❌ 商品不存在"
            
        total_cost = item_data["price"] * quantity
        
        if self.main_app.cash < total_cost:
            return False, f"❌ 资金不足，需要 J${total_cost:,.0f}"
            
        # 扣除资金
        self.main_app.cash -= total_cost
        
        # 添加到资产
        if "luxury_items" not in self.user_assets:
            self.user_assets["luxury_items"] = {}
            
        if item_id not in self.user_assets["luxury_items"]:
            self.user_assets["luxury_items"][item_id] = {
                "name": item_data["name"],
                "brand": item_data["brand"],
                "quantity": 0,
                "total_cost": 0,
                "rarity": item_data["rarity"]
            }
            
        self.user_assets["luxury_items"][item_id]["quantity"] += quantity
        self.user_assets["luxury_items"][item_id]["total_cost"] += total_cost
        
        self.save_user_assets()
        
        # 增加体验值
        self.main_app.experience += item_data["rarity"] * 10
        
        return True, f"✅ 成功购买 {item_data['name']} x{quantity}，体验奢华生活！获得经验值 {item_data['rarity'] * 10}"

    def buy_service(self, service_id):
        """购买生活服务"""
        services = self._get_lifestyle_services()
        service_data = next((s for s in services if s["id"] == service_id), None)
        
        if not service_data:
            return False, "❌ 服务不存在"
            
        cost = service_data["price"]
        
        if self.main_app.cash < cost:
            return False, f"❌ 资金不足，需要 J${cost:,.0f}"
            
        # 扣除资金
        self.main_app.cash -= cost
        
        # 添加到服务记录
        if "services" not in self.user_assets:
            self.user_assets["services"] = {}
            
        if service_id not in self.user_assets["services"]:
            self.user_assets["services"][service_id] = {
                "name": service_data["name"],
                "category": service_data["category"],
                "times_used": 0,
                "total_spent": 0,
                "last_used": None
            }
            
        self.user_assets["services"][service_id]["times_used"] += 1
        self.user_assets["services"][service_id]["total_spent"] += cost
        self.user_assets["services"][service_id]["last_used"] = datetime.now().isoformat()
        
        self.save_user_assets()
        
        # 根据服务类型给予不同奖励
        experience_gain = service_data["rating"] * 20
        self.main_app.experience += experience_gain
        
        # 教育类服务可能增加额外能力
        if service_data["category"] == "教育培训":
            self.main_app.level += 1  # 直接提升等级
            
        return True, f"✅ 成功购买 {service_data['name']}服务！获得经验值 {experience_gain}"

    def join_club(self, club_id):
        """加入会员俱乐部"""
        clubs = self._get_club_memberships()
        club_data = next((c for c in clubs if c["id"] == club_id), None)
        
        if not club_data:
            return False, "❌ 俱乐部不存在"
            
        annual_fee = club_data["annual_fee"]
        
        if self.main_app.cash < annual_fee:
            return False, f"❌ 资金不足，年费需要 J${annual_fee:,.0f}"
            
        # 检查是否已经是会员
        if "club_memberships" not in self.user_assets:
            self.user_assets["club_memberships"] = {}
            
        if club_id in self.user_assets["club_memberships"]:
            return False, "❌ 您已经是该俱乐部的会员"
            
        # 扣除年费
        self.main_app.cash -= annual_fee
        
        # 添加会员资格
        self.user_assets["club_memberships"][club_id] = {
            "name": club_data["name"],
            "type": club_data["type"],
            "join_date": datetime.now().isoformat(),
            "annual_fee": annual_fee,
            "next_renewal": (datetime.now() + timedelta(days=365)).isoformat(),
            "benefits_used": 0
        }
        
        self.save_user_assets()
        
        # 会员资格带来声望和经验
        self.main_app.experience += 100
        
        return True, f"✅ 成功加入 {club_data['name']}！开启精英社交圈！"

    def _calculate_total_asset_value(self):
        """计算总资产价值"""
        total_value = 0
        
        # ETF基金价值
        if "etf_funds" in self.user_assets:
            for fund_id, fund_data in self.user_assets["etf_funds"].items():
                # 简化计算，假设ETF有一定的价格波动
                original_value = fund_data["total_cost"]
                current_value = original_value * random.uniform(0.95, 1.15)  # ±15%波动
                total_value += current_value
                
        # 豪车价值
        if "luxury_cars" in self.user_assets:
            for car_id, car_data in self.user_assets["luxury_cars"].items():
                # 豪车可能升值或贬值
                original_value = car_data["total_cost"]
                current_value = original_value * random.uniform(0.8, 1.3)  # ±30%波动
                total_value += current_value
                
        # 房地产价值
        if "real_estate" in self.user_assets:
            for prop_id, prop_data in self.user_assets["real_estate"].items():
                original_value = prop_data["total_cost"]
                # 房地产相对稳定但有升值潜力
                current_value = original_value * random.uniform(1.0, 1.2)  # 0-20%升值
                total_value += current_value
                
        # 艺术品价值 
        if "art_collection" in self.user_assets:
            for art_id, art_data in self.user_assets["art_collection"].items():
                original_value = art_data["total_cost"]
                # 艺术品波动较大
                current_value = original_value * random.uniform(0.7, 1.5)  # ±50%波动
                total_value += current_value
                
        # 奢侈品价值（通常贬值）
        if "luxury_items" in self.user_assets:
            for item_id, item_data in self.user_assets["luxury_items"].items():
                original_value = item_data["total_cost"]
                # 奢侈品主要消费，价值下降
                current_value = original_value * random.uniform(0.3, 0.8)  # 贬值20-70%
                total_value += current_value
                
        return total_value

    def _calculate_total_profit_loss(self):
        """计算总盈亏"""
        total_cost = 0
        current_value = self._calculate_total_asset_value()
        
        # 计算所有投资的总成本
        for asset_type in ["etf_funds", "luxury_cars", "real_estate", "art_collection", "luxury_items"]:
            if asset_type in self.user_assets:
                for asset_id, asset_data in self.user_assets[asset_type].items():
                    total_cost += asset_data.get("total_cost", 0)
                    
        return current_value - total_cost 