"""
AppMarket系统 - 应用商店核心功能
提供应用安装、管理和运行服务
"""

import json
import random
import importlib.util
import os
from datetime import datetime

class AppMarket:
    """应用商店管理系统"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.available_apps = self._initialize_apps()
        self.user_apps = {}  # 用户已安装的应用
        self.load_user_apps()
    
    def _initialize_apps(self):
        """初始化可用应用 - 从配置文件自动加载"""
        apps = {}
        
        # 首先尝试从配置文件加载
        config_path = "data/app_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                for app_config in config.get('apps', []):
                    try:
                        # 动态加载应用
                        module_name = app_config['module_name']
                        class_name = app_config['class_name']
                        app_id = app_config['app_id']
                        
                        spec = importlib.util.spec_from_file_location(
                            f"{app_id}_app", 
                            os.path.join('apps', f"{module_name}.py")
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # 创建应用实例
                        app_class = getattr(module, class_name)
                        app_instance = app_class()
                        
                        # 更新应用信息（从配置覆盖）
                        app_instance.name = app_config.get('name', app_instance.name)
                        app_instance.description = app_config.get('description', app_instance.description)
                        app_instance.price = app_config.get('price', app_instance.price)
                        app_instance.category = app_config.get('category', app_instance.category)
                        app_instance.version = app_config.get('version', app_instance.version)
                        app_instance.emoji = app_config.get('emoji', app_instance.emoji)
                        app_instance.is_premium = app_config.get('is_premium', False)
                        app_instance.tags = app_config.get('tags', [])
                        
                        apps[app_id] = app_instance
                        print(f"✅ 成功加载应用: {app_instance.name}")
                        
                    except Exception as e:
                        print(f"❌ 无法加载应用 {app_config.get('app_id', 'unknown')}: {e}")
                        continue
                
                print(f"📱 共加载 {len(apps)} 个应用")
                return apps
                
            except Exception as e:
                print(f"❌ 读取应用配置文件失败: {e}")
        
        # 回退到硬编码方式
        print("⚠️ 配置文件不存在，使用硬编码方式加载应用")
        return self._initialize_apps_fallback()
    
    def _initialize_apps_fallback(self):
        """回退的应用初始化方法（硬编码）"""
        apps = {}
        
        # 动态加载apps文件夹中的应用
        try:
            
            # 应用映射表
            app_mappings = [
                ('slot_machine', 'slot_machine.app.py', 'SlotMachineApp'),
                ('blackjack', 'blackjack.app.py', 'BlackjackApp'),
                ('texas_holdem', 'texas_holdem.app.py', 'TexasHoldemApp'),
                ('dice_game', 'dice.app.py', 'DiceGameApp'),
                ('ai_analysis', 'ai_analysis.app.py', 'AIAnalysisApp'),
                ('advanced_chart', 'advanced_chart.app.py', 'AdvancedChartApp'),
                ('poker_game', 'poker_game.app.py', 'PokerGameApp'),
                ('news_analyzer', 'news_analyzer.app.py', 'NewsAnalyzerApp'),
                ('horse_racing', 'horse_racing.app.py', 'HorseRacingApp'),
                ('roulette', 'roulette.app.py', 'RouletteApp'),
                ('sic_bo', 'sic_bo.app.py', 'SicBoApp'),
            ]
            
            apps_dir = 'apps'
            if os.path.exists(apps_dir):
                for app_id, filename, class_name in app_mappings:
                    try:
                        spec = importlib.util.spec_from_file_location(
                            f"{app_id}_app", 
                            os.path.join(apps_dir, filename)
                        )
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        app_class = getattr(module, class_name)
                        apps[app_id] = app_class()
                        print(f"✅ 成功加载应用: {app_id}")
                    except Exception as e:
                        print(f"❌ 无法加载应用 {app_id}: {e}")
            
        except Exception as e:
            print(f"❌ 无法加载apps目录中的应用: {e}")
        
        return apps
    
    def load_user_apps(self):
        """加载用户已安装的应用"""
        try:
            user_data = self.main_app.user_data
            if user_data and 'installed_apps' in user_data:
                self.user_apps = user_data['installed_apps']
                print(f"[DEBUG] 加载了 {len(self.user_apps)} 个已安装应用: {list(self.user_apps.keys())}")
            else:
                self.user_apps = {}
                print("[DEBUG] 没有找到已安装应用数据，初始化为空")
        except Exception as e:
            print(f"[DEBUG] 加载应用数据时出错: {e}")
            self.user_apps = {}
    
    def save_user_apps(self):
        """保存用户应用数据"""
        try:
            if not self.main_app.user_data:
                self.main_app.user_data = {}
            
            # 确保数据同步到主应用的user_data
            self.main_app.user_data['installed_apps'] = self.user_apps.copy()
            
            # 立即调用保存
            self.main_app.save_game_data()
            
            print(f"[DEBUG] 保存了 {len(self.user_apps)} 个应用: {list(self.user_apps.keys())}")
        except Exception as e:
            print(f"[DEBUG] 保存应用数据时出错: {e}")
            # 即使出错也要确保数据在内存中同步
            if hasattr(self.main_app, 'user_data') and self.main_app.user_data:
                self.main_app.user_data['installed_apps'] = self.user_apps.copy()
    
    def show_market(self, category=None):
        """显示应用商店"""
        if category:
            return self._show_category(category)
        
        # 按类别分组
        categories = {}
        for app_id, app in self.available_apps.items():
            cat = app.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(app)
        
        market_text = f"""
══════════════════════════════════════════════════════════════════════════════════════════
                                🏪 应用商店 - AppMarket 🏪                                
                              发现更多有趣的应用和工具                                     
══════════════════════════════════════════════════════════════════════════════════════════

💰 当前余额: ${self.main_app.cash:,.2f}
📱 已安装应用: {len(self.user_apps)}个

📂 应用分类:
"""
        
        for category, apps in categories.items():
            market_text += f"\n🏷️ {category} ({len(apps)}个应用):\n"
            for app in apps:
                status = "✅ 已安装" if app.app_id in self.user_apps else f"💰 ${app.price:,}"
                market_text += f"  • [{app.app_id}] {app.name} - {status}\n"
                market_text += f"    {app.description[:50]}...\n"
        
        market_text += f"""

🎮 快速操作:
  appmarket                      # 查看应用商店
  appmarket <类别>               # 查看特定类别
  install <应用ID>               # 购买并安装应用
  uninstall <应用ID>             # 卸载应用
  appmarket.app <应用ID> [参数]  # 运行已安装的应用

📱 已安装应用管理:
  appmarket my                   # 查看我的应用
  appmarket usage                # 查看使用统计

🆔 常用应用ID:
  游戏娱乐: slot_machine, blackjack, texas_holdem, dice_game, poker_game
  分析工具: ai_analysis, news_analyzer, advanced_chart

💡 提示: 购买应用后即可无限次使用，是投资理财之余的好选择！
"""
        
        return market_text
    
    def _show_category(self, category):
        """显示特定类别的应用"""
        apps_in_category = [app for app in self.available_apps.values() if app.category == category]
        
        if not apps_in_category:
            return f"❌ 没有找到类别 '{category}' 的应用"
        
        category_text = f"""
🏷️ {category} 类别应用详情

"""
        
        for app in apps_in_category:
            is_installed = app.app_id in self.user_apps
            status = "✅ 已安装" if is_installed else f"💰 ${app.price:,}"
            
            category_text += f"""
─────────────────────────────────────────────────────
 {app.name}                                           
─────────────────────────────────────────────────────
 应用ID: {app.app_id}                                
 价格: {status}                                       
 版本: {app.version}                                  
 描述: {app.description}                              
─────────────────────────────────────────────────────
"""
            
            if is_installed:
                app_data = self.user_apps[app.app_id]
                category_text += f"""
📊 使用统计:
  安装时间: {app_data.get('install_date', 'N/A')[:10]}
  使用次数: {app_data.get('usage_count', 0)}
  
🎮 运行命令: appmarket.app {app.app_id}
"""
        
        return category_text
    
    def install_app(self, app_id):
        """购买并安装应用"""
        if app_id not in self.available_apps:
            # 显示建议的应用ID
            available_ids = list(self.available_apps.keys())
            suggestion = f"\n💡 可用应用ID: {', '.join(available_ids)}"
            return f"❌ 应用 '{app_id}' 不存在{suggestion}"
        
        if app_id in self.user_apps:
            return f"❌ 应用 '{app_id}' 已经安装"
        
        app = self.available_apps[app_id]
        
        if self.main_app.cash < app.price:
            return f"❌ 余额不足，需要 ${app.price:,}，当前余额 ${self.main_app.cash:,.2f}"
        
        # 扣除费用
        self.main_app.cash -= app.price
        
        # 安装应用
        self.user_apps[app_id] = {
            'install_date': datetime.now().isoformat(),
            'usage_count': 0,
            'total_spent': 0  # 在应用内消费
        }
        
        # 更新应用安装时间
        app.install_date = datetime.now().isoformat()
        
        self.save_user_apps()
        
        return f"""
✅ 应用安装成功！

📱 应用信息:
  ID: {app_id}
  名称: {app.name}
  类别: {app.category}
  价格: ${app.price:,}
  版本: {app.version}

💰 账户变动:
  消费金额: ${app.price:,}
  剩余余额: ${self.main_app.cash:,.2f}

🎮 开始使用:
  运行命令: appmarket.app {app_id}
  
📚 查看帮助:
  appmarket my               # 查看我的应用列表
"""
    
    def uninstall_app(self, app_id):
        """卸载应用"""
        if app_id not in self.user_apps:
            return f"❌ 应用 '{app_id}' 未安装"
        
        app_name = self.available_apps[app_id].name if app_id in self.available_apps else app_id
        
        # 删除应用数据
        del self.user_apps[app_id]
        self.save_user_apps()
        
        return f"✅ 应用 [{app_id}] '{app_name}' 已卸载"
    
    def run_app(self, app_id, *args):
        """运行已安装的应用"""
        if app_id not in self.user_apps:
            return f"❌ 应用 '{app_id}' 未安装，请先使用 'install {app_id}' 安装"
        
        if app_id not in self.available_apps:
            return f"❌ 应用 '{app_id}' 不可用"
        
        app = self.available_apps[app_id]
        
        # 更新使用统计
        self.user_apps[app_id]['usage_count'] += 1
        self.save_user_apps()
        
        # 运行应用
        try:
            result = app.run(self.main_app, *args)
            return result
        except Exception as e:
            return f"❌ 应用运行出错: {str(e)}"
    
    def show_my_apps(self):
        """显示用户已安装的应用"""
        # 添加调试信息
        debug_info = f"""
🔧 调试信息:
  内存中的应用数据: {len(self.user_apps)}个
  user_data中的应用: {len(self.main_app.user_data.get('installed_apps', {})) if self.main_app.user_data else 0}个
  user_data存在: {self.main_app.user_data is not None}
  当前用户: {self.main_app.user_manager.current_user}
"""
        
        if not self.user_apps:
            return debug_info + "\n📱 您还没有安装任何应用\n\n💡 输入 'appmarket' 查看可用应用"
        
        my_apps_text = debug_info + f"""
📱 我的应用列表

总共安装: {len(self.user_apps)}个应用
"""
        
        total_spent = 0
        for app_id, app_data in self.user_apps.items():
            if app_id in self.available_apps:
                app = self.available_apps[app_id]
                total_spent += app.price
                
                my_apps_text += f"""
─────────────────────────────────────────────────────
 {app.name}                                           
─────────────────────────────────────────────────────
 ID: {app_id}                                         
 购买价格: ${app.price:,}                             
 安装时间: {app_data['install_date'][:10]}             
 使用次数: {app_data['usage_count']}                   
 应用内消费: ${app_data.get('total_spent', 0):,.2f}   
─────────────────────────────────────────────────────
 🎮 运行: appmarket.app {app_id}                      
 🗑️ 卸载: uninstall {app_id}                         
─────────────────────────────────────────────────────
"""
        
        my_apps_text += f"""
💰 消费统计:
  应用购买总花费: ${total_spent:,}
  应用内消费总额: ${sum(app.get('total_spent', 0) for app in self.user_apps.values()):,.2f}
  
🔧 管理操作:
  uninstall <ID>            # 卸载应用
  appmarket usage           # 查看详细使用统计
  
💡 如果应用列表不正确，请尝试重新登录。
"""
        
        return my_apps_text
    
    def show_usage_stats(self):
        """显示使用统计"""
        if not self.user_apps:
            return "📊 暂无使用统计数据"
        
        stats_text = f"""
📊 应用使用统计报告

📱 总体概况:
  已安装应用: {len(self.user_apps)}个
  总使用次数: {sum(app.get('usage_count', 0) for app in self.user_apps.values())}次
  
🏆 使用排行:
"""
        
        # 按使用次数排序
        sorted_apps = sorted(self.user_apps.items(), 
                           key=lambda x: x[1].get('usage_count', 0), 
                           reverse=True)
        
        for i, (app_id, app_data) in enumerate(sorted_apps[:5], 1):
            if app_id in self.available_apps:
                app_name = self.available_apps[app_id].name
                usage_count = app_data.get('usage_count', 0)
                stats_text += f"  {i}. [{app_id}] {app_name} - {usage_count}次\n"
        
        # 按类别统计
        category_stats = {}
        for app_id in self.user_apps:
            if app_id in self.available_apps:
                category = self.available_apps[app_id].category
                if category not in category_stats:
                    category_stats[category] = 0
                category_stats[category] += self.user_apps[app_id].get('usage_count', 0)
        
        stats_text += f"""
📂 分类使用统计:
"""
        for category, count in category_stats.items():
            stats_text += f"  {category}: {count}次\n"
        
        return stats_text 