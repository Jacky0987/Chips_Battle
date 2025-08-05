"""
指数管理系统 - 负责指数的计算、更新和展示
"""

import json
import os
from datetime import datetime
import pytz


class IndexManager:
    """指数管理系统"""
    
    def __init__(self, market_data_manager):
        self.market_data = market_data_manager
        self.indices = {}
        self.load_indices()
    
    def load_indices(self):
        """加载指数数据"""
        try:
            indices_file = os.path.join("data", "indices.json")
            if os.path.exists(indices_file):
                with open(indices_file, 'r', encoding='utf-8') as f:
                    self.indices = json.load(f)
                print(f"[DEBUG] 加载了 {len(self.indices)} 个指数")
            else:
                print("[DEBUG] 指数文件不存在，创建默认指数")
                self.create_default_indices()
        except Exception as e:
            print(f"[DEBUG] 加载指数数据出错: {e}")
            self.create_default_indices()
    
    def save_indices(self):
        """保存指数数据"""
        try:
            indices_file = os.path.join("data", "indices.json")
            with open(indices_file, 'w', encoding='utf-8') as f:
                json.dump(self.indices, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DEBUG] 保存指数数据出错: {e}")
    
    def create_default_indices(self):
        """创建默认指数"""
        self.indices = {
            "SP500": {
                "name": "标普500指数",
                "description": "美国500家最大上市公司的股价加权指数",
                "base_value": 5000.0,
                "current_value": 5000.0,
                "change": 0.0,
                "change_percent": 0.0,
                "category": "综合指数",
                "currency": "USD",
                "country": "US",
                "constituents": [
                    {"symbol": "AAPL", "weight": 7.2},
                    {"symbol": "MSFT", "weight": 6.8},
                    {"symbol": "GOOGL", "weight": 4.1},
                    {"symbol": "AMZN", "weight": 3.2},
                    {"symbol": "NVDA", "weight": 2.8}
                ],
                "value_history": [5000.0],
                "last_updated": datetime.now(pytz.UTC).isoformat()
            }
        }
        self.save_indices()
    
    def update_all_indices(self):
        """更新所有指数"""
        for index_code in self.indices:
            self.update_index(index_code)
        self.save_indices()
    
    def update_index(self, index_code):
        """更新单个指数"""
        if index_code not in self.indices:
            return
        
        index_data = self.indices[index_code]
        constituents = index_data["constituents"]
        
        if not constituents:
            return
        
        total_weighted_change = 0.0
        total_weight = 0.0
        
        # 计算加权平均变化
        for constituent in constituents:
            symbol = constituent["symbol"]
            weight = constituent["weight"]
            
            if symbol in self.market_data.stocks:
                stock = self.market_data.stocks[symbol]
                price = stock["price"]
                change = stock.get("change", 0)
                
                # 计算变化百分比
                if price > 0:
                    change_percent = (change / (price - change)) * 100
                    total_weighted_change += change_percent * weight
                    total_weight += weight
        
        if total_weight > 0:
            # 计算指数变化
            weighted_change_percent = total_weighted_change / total_weight
            
            # 更新指数值
            base_value = index_data["base_value"]
            old_value = index_data["current_value"]
            new_value = base_value * (1 + weighted_change_percent / 100)
            
            index_data["current_value"] = round(new_value, 2)
            index_data["change"] = round(new_value - old_value, 2)
            index_data["change_percent"] = round((new_value - old_value) / old_value * 100, 2)
            
            # 更新历史数据
            if "value_history" not in index_data:
                index_data["value_history"] = [base_value]
            
            index_data["value_history"].append(new_value)
            if len(index_data["value_history"]) > 20:
                index_data["value_history"].pop(0)
            
            index_data["last_updated"] = datetime.now(pytz.UTC).isoformat()
    
    def get_index_info(self, index_code):
        """获取指数信息"""
        if index_code not in self.indices:
            return None
        return self.indices[index_code]
    
    def get_all_indices(self):
        """获取所有指数"""
        return self.indices
    
    def show_indices_overview(self):
        """显示指数概览"""
        if not self.indices:
            return "📊 暂无指数数据"
        
        overview_text = f"""
📊 指数市场概览

总计指数: {len(self.indices)}个

"""
        
        for code, data in self.indices.items():
            current_value = data["current_value"]
            change = data["change"]
            change_percent = data["change_percent"]
            
            trend_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            
            overview_text += f"  [{code}] {data['name']}\n"
            overview_text += f"    当前值: {current_value:,.2f} {trend_emoji} {change:+.2f} ({change_percent:+.2f}%)\n"
        
        overview_text += f"""
💡 使用说明:
  index <代码>    # 查看指数详情
  index list     # 显示所有指数列表
"""
        return overview_text
    
    def show_index_detail(self, index_code):
        """显示指数详情"""
        if index_code not in self.indices:
            available_codes = ", ".join(self.indices.keys())
            return f"❌ 指数 '{index_code}' 不存在\n💡 可用指数: {available_codes}"
        
        index_data = self.indices[index_code]
        current_value = index_data["current_value"]
        change = index_data["change"]
        change_percent = index_data["change_percent"]
        
        trend_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        
        detail_text = f"""
📊 指数详情 - {index_data['name']}

╔══════════════════════════════════════════════════════════════════════════════════╗
║  {index_code} - {index_data['name']}                                             ║
╚══════════════════════════════════════════════════════════════════════════════════╝

📈 指数表现:
  当前值: {current_value:,.2f}
  变动: {change:+.2f} ({change_percent:+.2f}%) {trend_emoji}
  基准值: {index_data['base_value']:,.2f}

📋 基本信息:
  描述: {index_data['description']}
  类别: {index_data['category']}
  货币: {index_data['currency']}
  地区: {index_data['country']}
  成分股数量: {len(index_data['constituents'])}股

🏢 主要成分股:
"""
        
        # 显示成分股信息
        for i, constituent in enumerate(index_data['constituents'][:10], 1):
            symbol = constituent['symbol']
            weight = constituent['weight']
            
            if symbol in self.market_data.stocks:
                stock = self.market_data.stocks[symbol]
                price = stock['price']
                stock_change = stock.get('change', 0)
                stock_change_percent = (stock_change / (price - stock_change)) * 100 if price > stock_change else 0
                
                detail_text += f"  {i:2d}. [{symbol}] {stock['name'][:25]:<25} 权重: {weight:5.1f}% "
                detail_text += f"价格: ${price:8.2f} ({stock_change_percent:+5.1f}%)\n"
            else:
                detail_text += f"  {i:2d}. [{symbol}] 权重: {weight:5.1f}% (数据不可用)\n"
        
        # 显示历史趋势
        if "value_history" in index_data and len(index_data["value_history"]) > 1:
            history = index_data["value_history"][-10:]  # 最近10个点
            detail_text += f"\n📈 近期走势:\n  "
            for i, value in enumerate(history):
                if i > 0:
                    prev_value = history[i-1]
                    if value > prev_value:
                        detail_text += "📈"
                    elif value < prev_value:
                        detail_text += "📉"
                    else:
                        detail_text += "➡️"
                detail_text += f"{value:6.0f} "
                if (i + 1) % 5 == 0:
                    detail_text += "\n  "
        
        detail_text += f"""

📊 分析指标:
  波动率: {self.calculate_index_volatility(index_code):.2%}
  最高点: {max(index_data.get('value_history', [current_value])):,.2f}
  最低点: {min(index_data.get('value_history', [current_value])):,.2f}

⚠️ 免责声明: 指数数据仅供参考，投资需谨慎
"""
        
        return detail_text
    
    def calculate_index_volatility(self, index_code):
        """计算指数波动率"""
        if index_code not in self.indices:
            return 0.0
        
        history = self.indices[index_code].get("value_history", [])
        if len(history) < 2:
            return 0.0
        
        # 计算日变化率
        changes = []
        for i in range(1, len(history)):
            if history[i-1] != 0:
                change = (history[i] - history[i-1]) / history[i-1]
                changes.append(change)
        
        if not changes:
            return 0.0
        
        # 计算标准差作为波动率
        mean_change = sum(changes) / len(changes)
        variance = sum((x - mean_change) ** 2 for x in changes) / len(changes)
        volatility = variance ** 0.5
        
        return volatility
    
    def show_indices_by_category(self, category):
        """按类别显示指数"""
        category_indices = {}
        for code, data in self.indices.items():
            index_category = data.get("category", "其他")
            if category.lower() in index_category.lower():
                category_indices[code] = data
        
        if not category_indices:
            available_categories = set(data.get("category", "其他") for data in self.indices.values())
            return f"❌ 没有找到类别 '{category}' 的指数\n💡 可用类别: {', '.join(available_categories)}"
        
        category_text = f"""
📊 {category} 指数

"""
        for code, data in category_indices.items():
            current_value = data["current_value"]
            change = data["change"]
            change_percent = data["change_percent"]
            
            trend_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            color_indicator = "🟢" if change > 0 else "🔴" if change < 0 else "🟡"
            
            category_text += f"{color_indicator} [{code}] {data['name']}\n"
            category_text += f"  当前值: {current_value:,.2f} {trend_emoji} {change:+.2f} ({change_percent:+.2f}%)\n"
            category_text += f"  描述: {data['description']}\n\n"
        
        return category_text
    
    def compare_indices(self, index1, index2):
        """比较两个指数"""
        if index1 not in self.indices or index2 not in self.indices:
            return f"❌ 指数不存在，可用指数: {', '.join(self.indices.keys())}"
        
        data1 = self.indices[index1]
        data2 = self.indices[index2]
        
        compare_text = f"""
📊 指数比较分析

╔══════════════════════════════════════════════════════════════════════════════════╗
║  {index1} vs {index2}                                                           ║
╚══════════════════════════════════════════════════════════════════════════════════╝

📈 {data1['name']}:
  当前值: {data1['current_value']:,.2f}
  变动: {data1['change']:+.2f} ({data1['change_percent']:+.2f}%)
  基准值: {data1['base_value']:,.2f}
  类别: {data1['category']}

📈 {data2['name']}:
  当前值: {data2['current_value']:,.2f}
  变动: {data2['change']:+.2f} ({data2['change_percent']:+.2f}%)
  基准值: {data2['base_value']:,.2f}
  类别: {data2['category']}

🔍 比较分析:
  相对表现: {data1['name']} {"优于" if data1['change_percent'] > data2['change_percent'] else "劣于" if data1['change_percent'] < data2['change_percent'] else "等同于"} {data2['name']}
  波动率差异: {abs(self.calculate_index_volatility(index1) - self.calculate_index_volatility(index2)):.2%}
  
📊 成分股对比:
  {data1['name']}: {len(data1['constituents'])}只成分股
  {data2['name']}: {len(data2['constituents'])}只成分股
"""
        
        return compare_text
    
    def get_index_list(self):
        """获取指数列表"""
        if not self.indices:
            return "📊 暂无指数数据"
        
        list_text = f"""
📊 指数列表

总计: {len(self.indices)}个指数

代码    名称                    当前值        变动        类别
{"="*75}
"""
        
        for code, data in self.indices.items():
            name = data['name'][:15] + "..." if len(data['name']) > 18 else data['name']
            current_value = data['current_value']
            change_percent = data['change_percent']
            category = data['category'][:8] + "..." if len(data['category']) > 10 else data['category']
            
            trend_symbol = "↗" if change_percent > 0 else "↘" if change_percent < 0 else "→"
            
            list_text += f"{code:<8} {name:<20} {current_value:>10,.2f} {trend_symbol} {change_percent:>6.2f}% {category}\n"
        
        list_text += f"""
{"="*75}

💡 使用 'index <代码>' 查看详细信息
"""
        return list_text 