"""
JC公司系统专用GUI界面
提供CLI风格的图案展示和场景模拟
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import random
from datetime import datetime
from typing import Dict, Optional

from .company_types import JCCompany, CompanyStage


class CompanyGUI:
    """公司系统GUI界面"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.window = None
        self.current_company = None
        self.animation_timer = None
        self.scene_elements = []
        self.update_timer = None  # 自动更新定时器
        self.current_scene = "office"  # 当前场景类型
        
    def open_company_center(self, company_id: Optional[str] = None):
        """打开公司管理中心"""
        if self.window:
            self.window.destroy()
        
        # 检查是否有根窗口，如果没有就创建一个
        if not hasattr(self.main_app, 'root') or not self.main_app.root:
            self.main_app.root = tk.Tk()
            self.main_app.root.withdraw()  # 隐藏主窗口
            
        self.window = tk.Toplevel(self.main_app.root)
        self.window.title("JC企业管理中心")
        self.window.geometry("1400x900")
        self.window.configure(bg='#0a0a0a')
        
        # 设置公司
        if company_id and company_id in self.main_app.company_manager.companies:
            self.current_company = self.main_app.company_manager.companies[company_id]
        
        self._create_gui_layout()
        self._start_animations()
        self._start_auto_updates()  # 启动自动更新
        
    def _create_gui_layout(self):
        """创建GUI布局"""
        # 主框架
        main_frame = tk.Frame(self.window, bg='#0a0a0a')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题区域
        self._create_header(main_frame)
        
        # 内容区域
        content_frame = tk.Frame(main_frame, bg='#0a0a0a')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板 - 场景展示
        left_panel = tk.Frame(content_frame, bg='#1a1a1a', width=500)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        left_panel.pack_propagate(False)
        
        self._create_scene_panel(left_panel)
        
        # 右侧面板 - 控制和信息
        right_panel = tk.Frame(content_frame, bg='#1a1a1a', width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        self._create_control_panel(right_panel)
        
    def _create_header(self, parent):
        """创建头部区域"""
        header_frame = tk.Frame(parent, bg='#0a0a0a', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # 标题
        title_label = tk.Label(
            header_frame,
            text="🏢 JC企业管理中心",
            font=('Consolas', 24, 'bold'),
            fg='#00ff88',
            bg='#0a0a0a'
        )
        title_label.pack(pady=10)
        
        # 分隔线
        separator = tk.Frame(header_frame, bg='#00ff88', height=2)
        separator.pack(fill=tk.X, pady=5)
        
    def _create_scene_panel(self, parent):
        """创建场景展示面板"""
        scene_frame = tk.LabelFrame(
            parent,
            text="🌆 企业场景",
            font=('Consolas', 14, 'bold'),
            fg='#00ff88',
            bg='#1a1a1a',
            bd=2
        )
        scene_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 场景显示区域
        self.scene_display = scrolledtext.ScrolledText(
            scene_frame,
            font=('Consolas', 10),
            fg='#00ff88',
            bg='#0a0a0a',
            insertbackground='#00ff88',
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.scene_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 场景控制按钮
        scene_buttons = tk.Frame(scene_frame, bg='#1a1a1a')
        scene_buttons.pack(fill=tk.X, padx=5, pady=5)
        
        scenes = [
            ("🏢 办公大楼", "office"),
            ("🏭 生产车间", "factory"),
            ("💼 董事会议", "meeting"),
            ("📊 数据中心", "datacenter"),
            ("🚀 创新实验室", "lab")
        ]
        
        for i, (text, scene_type) in enumerate(scenes):
            btn = tk.Button(
                scene_buttons,
                text=text,
                font=('Consolas', 9),
                fg='#00ff88',
                bg='#2a2a2a',
                activeforeground='#ffffff',
                activebackground='#00ff88',
                command=lambda s=scene_type: self._switch_scene(s),
                width=12
            )
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky='ew')
        
        # 初始场景
        self._switch_scene("office")
        
    def _create_control_panel(self, parent):
        """创建控制面板"""
        # 公司选择器
        company_frame = tk.LabelFrame(
            parent,
            text="🏢 公司选择",
            font=('Consolas', 12, 'bold'),
            fg='#00ff88',
            bg='#1a1a1a'
        )
        company_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self._create_company_selector(company_frame)
        
        # 公司信息
        if self.current_company:
            info_frame = tk.LabelFrame(
                parent,
                text="📊 公司状态",
                font=('Consolas', 12, 'bold'),
                fg='#00ff88',
                bg='#1a1a1a'
            )
            info_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self._create_company_info(info_frame)
            
            # 操作按钮
            action_frame = tk.LabelFrame(
                parent,
                text="🎮 快捷操作",
                font=('Consolas', 12, 'bold'),
                fg='#00ff88',
                bg='#1a1a1a'
            )
            action_frame.pack(fill=tk.X, padx=5, pady=5)
            
            self._create_action_buttons(action_frame)
        
        # 创建公司按钮
        create_frame = tk.Frame(parent, bg='#1a1a1a')
        create_frame.pack(fill=tk.X, padx=5, pady=10)
        
        create_btn = tk.Button(
            create_frame,
            text="🚀 创建新公司",
            font=('Consolas', 12, 'bold'),
            fg='#ffffff',
            bg='#ff6600',
            activeforeground='#000000',
            activebackground='#ffaa00',
            command=self._start_company_creation,
            height=2
        )
        create_btn.pack(fill=tk.X)
        
    def _create_company_selector(self, parent):
        """创建公司选择器"""
        user_companies = self.main_app.company_manager.get_user_companies(
            self.main_app.user_manager.current_user
        )
        
        if not user_companies:
            no_company_label = tk.Label(
                parent,
                text="您还没有创建任何公司",
                font=('Consolas', 10),
                fg='#888888',
                bg='#1a1a1a'
            )
            no_company_label.pack(pady=10)
            return
        
        # 公司下拉框
        company_var = tk.StringVar()
        company_names = [f"{c.name} ({c.symbol})" for c in user_companies]
        
        company_combo = ttk.Combobox(
            parent,
            textvariable=company_var,
            values=company_names,
            state="readonly",
            font=('Consolas', 10)
        )
        company_combo.pack(fill=tk.X, padx=5, pady=5)
        
        if self.current_company:
            current_name = f"{self.current_company.name} ({self.current_company.symbol})"
            if current_name in company_names:
                company_combo.set(current_name)
        elif company_names:
            company_combo.set(company_names[0])
            
        def on_company_change(event):
            selected = company_combo.get()
            if selected:
                company_name = selected.split(' (')[0]
                for company in user_companies:
                    if company.name == company_name:
                        self.current_company = company
                        self._refresh_interface()
                        break
        
        company_combo.bind('<<ComboboxSelected>>', on_company_change)
        
    def _create_company_info(self, parent):
        """创建公司信息显示"""
        company = self.current_company
        
        info_text = scrolledtext.ScrolledText(
            parent,
            font=('Consolas', 9),
            fg='#00ff88',
            bg='#0a0a0a',
            height=15,
            state=tk.DISABLED
        )
        info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 显示公司信息
        info_content = f"""
🏢 {company.name} ({company.symbol})
{'='*40}

📈 发展阶段: {company.stage.value.title()}
🏭 行业领域: {company.industry.value.title()}
📅 成立时间: {company.founded_date}
⭐ 表现评分: {company.performance_score:.1f}/100
🎯 风险等级: {company.risk_level}/5

💰 财务状况:
  营业收入: J${company.metrics.revenue:,.0f}
  净利润: J${company.metrics.profit:,.0f}
  总资产: J${company.metrics.assets:,.0f}
  负债: J${company.metrics.liabilities:,.0f}
  净资产: J${company.metrics.calculate_equity():,.0f}

👥 人力资源:
  员工总数: {company.metrics.employees}人
  人均产值: J${company.metrics.revenue/company.metrics.employees:,.0f}

📊 市场表现:
  市场份额: {company.metrics.market_share*100:.3f}%
  增长率: {company.metrics.growth_rate*100:.1f}%
  债务率: {company.metrics.debt_ratio*100:.1f}%

{'📈 已上市' if company.is_public else '🏢 未上市'}
{f'股价: J${company.stock_price:.2f}' if company.is_public else ''}
{f'市值: J${company.market_cap:,.0f}' if company.is_public else ''}
"""
        
        info_text.config(state=tk.NORMAL)
        info_text.delete(1.0, tk.END)
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        # 保存引用以便后续更新
        self.company_info_text = info_text
        
    def _create_action_buttons(self, parent):
        """创建操作按钮"""
        actions = [
            ("🔬 研发投入", "research", "#3366cc"),
            ("📢 市场营销", "marketing", "#ff6600"),
            ("🏗️ 业务扩张", "expansion", "#cc3366"),
            ("⚡ 效率优化", "efficiency", "#33cc66"),
            ("💻 技术升级", "technology", "#6633cc"),
            ("👥 人才培养", "talent", "#cc6633"),
            ("🏆 品牌建设", "brand", "#33cccc"),
            ("💡 创新研发", "innovation", "#cccc33"),
        ]
        
        for i, (text, action, color) in enumerate(actions):
            btn = tk.Button(
                parent,
                text=text,
                font=('Consolas', 9),
                fg='#ffffff',
                bg=color,
                activeforeground='#000000',
                activebackground='#ffffff',
                command=lambda a=action: self._execute_action(a),
                width=15
            )
            btn.grid(row=i//2, column=i%2, padx=2, pady=2, sticky='ew')
        
        # 配置列权重
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
    def _switch_scene(self, scene_type):
        """切换场景"""
        self.current_scene = scene_type
        self.scene_display.config(state=tk.NORMAL)
        self.scene_display.delete(1.0, tk.END)
        
        scene_content = self._generate_scene(scene_type)
        self.scene_display.insert(tk.END, scene_content)
        self.scene_display.config(state=tk.DISABLED)
        
        # 设置动画元素
        self.scene_elements = self._get_scene_elements(scene_type)
        
    def _generate_scene(self, scene_type):
        """生成场景内容"""
        scenes = {
            "office": self._generate_office_scene,
            "factory": self._generate_factory_scene,
            "meeting": self._generate_meeting_scene,
            "datacenter": self._generate_datacenter_scene,
            "lab": self._generate_lab_scene
        }
        
        generator = scenes.get(scene_type, self._generate_office_scene)
        return generator()
    
    def _generate_office_scene(self):
        """生成办公室场景"""
        company = self.current_company
        
        # 根据公司规模调整场景
        if company:
            if company.metrics.employees < 50:
                building_height = 3
                building_width = 20
            elif company.metrics.employees < 200:
                building_height = 8
                building_width = 30
            else:
                building_height = 15
                building_width = 40
        else:
            building_height = 5
            building_width = 25
        
        scene = f"""
                    🌤️  ☁️     🌤️
                  ☁️       ☁️

            🏢 {company.name if company else 'JC企业'} 总部大楼

{'█' * building_width}
"""
        
        # 生成楼层
        for floor in range(building_height):
            if floor == 0:
                # 底层
                line = "█"
                for i in range(building_width - 2):
                    if i % 6 == 1:
                        line += "🚪"
                    elif i % 6 == 3:
                        line += "🪟"
                    else:
                        line += " "
                line += "█"
            else:
                # 其他楼层
                line = "█"
                for i in range(building_width - 2):
                    if i % 4 == 1 or i % 4 == 3:
                        if random.random() < 0.7:
                            line += "💡"  # 有灯的窗户
                        else:
                            line += "⬛"  # 没灯的窗户
                    else:
                        line += " "
                line += "█"
            
            scene += line + "\n"
        
        scene += "█" * building_width + "\n"
        
        # 地面活动
        scene += f"""
🚗  🚶  🚗     🚶  🚗    🚶  🚗

💼 当前活动:
"""
        
        if company:
            # 根据公司状态生成活动
            activities = []
            
            # 根据发展阶段生成活动
            if company.stage == CompanyStage.STARTUP:
                activities.append(f"👥 {company.metrics.employees}名员工正在努力工作")
                activities.append(f"💰 筹集资金: J${company.metrics.revenue*0.2:,.0f}")
                activities.append(f"📈 寻找客户: {int(company.metrics.market_share*10000)}个潜在客户")
            elif company.stage == CompanyStage.DEVELOPMENT:
                activities.append(f"👥 {company.metrics.employees}名员工正在努力工作")
                activities.append(f"💰 扩大生产: 日产值J${company.metrics.revenue/365:,.0f}")
                activities.append(f"📈 市场拓展: 占据{company.metrics.market_share*100:.3f}%市场份额")
            elif company.stage == CompanyStage.EXPANSION:
                activities.append(f"👥 {company.metrics.employees}名员工正在努力工作")
                activities.append(f"💰 业务扩张: 新开{int(company.metrics.growth_rate*10)}个分支机构")
                activities.append(f"📈 国际化: 进入{int(company.metrics.market_share*100)}个新市场")
            elif company.stage == CompanyStage.MATURE:
                activities.append(f"👥 {company.metrics.employees}名员工正在努力工作")
                activities.append(f"💰 稳定盈利: 净利润J${company.metrics.profit:,.0f}")
                activities.append(f"📈 维持地位: 保持{company.metrics.market_share*100:.3f}%市场份额")
            else:  # CompanyStage.DECLINE
                activities.append(f"👥 {company.metrics.employees}名员工正在努力工作")
                activities.append(f"💰 业务重组: 优化成本J${company.metrics.revenue*0.1:,.0f}")
                activities.append(f"📈 战略调整: 寻找新增长点")
            
            # 根据表现评分添加特殊活动
            if company.performance_score > 80:
                activities.append("⭐ 公司表现优异，员工士气高涨")
            elif company.performance_score > 60:
                activities.append("📈 公司运营良好，稳步发展")
            elif company.performance_score > 40:
                activities.append("⚠️ 公司面临挑战，需要改进")
            else:
                activities.append("❌ 公司经营困难，急需调整策略")
            
            for activity in activities:
                scene += f"   {activity}\n"
        else:
            scene += "   🏢 选择一个公司查看详细活动\n"
        
        return scene
    
    def _generate_factory_scene(self):
        """生成工厂场景"""
        company = self.current_company
        
        scene = f"""
           🏭 {company.name if company else 'JC企业'} 生产基地

    🌫️       🌫️       🌫️    ← 工厂烟囱
     |         |         |
   ╔═══╤═══╤═══╤═══╤═══╤═══╗
   ║ 🏗️│🔧 │⚙️ │🔩 │⚡ │📦 ║ ← 生产线A
   ╠═══╪═══╪═══╪═══╪═══╪═══╣
   ║ 🤖│⚡ │🔧 │⚙️ │📦 │🚛 ║ ← 生产线B  
   ╠═══╪═══╪═══╪═══╪═══╪═══╣
   ║ 👷│👷 │👷 │👷 │👷 │📋 ║ ← 质检区
   ╚═══╧═══╧═══╧═══╧═══╧═══╝

🚛 ← 物流运输        🏪 → 仓储区域

📊 生产状态:
"""
        
        if company:
            productivity = company.performance_score / 100
            capacity_utilization = min(100, company.metrics.employees / 5)
            
            # 根据行业调整生产线
            if "tech" in company.industry.value.lower():
                line_a = "📱│💻 │🖥️ │🖨️ │⚡ │📦"
                line_b = "🤖│⚡ │🔧 │⚙️ │📦 │🚛"
            elif "manufacturing" in company.industry.value.lower():
                line_a = "🚗│🔧 │⚙️ │🔩 │⚡ │📦"
                line_b = "🤖│⚡ │🔧 │⚙️ │📦 │🚛"
            elif "food" in company.industry.value.lower():
                line_a = "🍞│🥬 │🍳 │🥫 │⚡ │📦"
                line_b = "🤖│⚡ │🔧 │⚙️ │📦 │🚛"
            else:
                line_a = "🏗️│🔧 │⚙️ │🔩 │⚡ │📦"
                line_b = "🤖│⚡ │🔧 │⚙️ │📦 │🚛"
            
            # 重新生成场景以包含行业特定元素
            scene = f"""
           🏭 {company.name if company else 'JC企业'} 生产基地

    🌫️       🌫️       🌫️    ← 工厂烟囱
     |         |         |
   ╔═══╤═══╤═══╤═══╤═══╤═══╗
   ║ {line_a} ║ ← 生产线A
   ╠═══╪═══╪═══╪═══╪═══╪═══╣
   ║ {line_b} ║ ← 生产线B  
   ╠═══╪═══╪═══╪═══╪═══╪═══╣
   ║ 👷│👷 │👷 │👷 │👷 │📋 ║ ← 质检区
   ╚═══╧═══╧═══╧═══╧═══╧═══╝

🚛 ← 物流运输        🏪 → 仓储区域

📊 生产状态:
"""
            
            production_stats = [
                f"⚡ 产能利用率: {capacity_utilization:.1f}%",
                f"🎯 生产效率: {productivity*100:.1f}%",
                f"👷 工人数量: {company.metrics.employees}人",
                f"📦 日产值: J${company.metrics.revenue/365:,.0f}",
                f"🔧 设备状态: {'良好' if productivity > 0.7 else '需维护'}"
            ]
            
            # 根据表现评分添加特殊状态
            if company.performance_score > 80:
                production_stats.append("🌟 生产线运行高效，产品质量优秀")
            elif company.performance_score > 60:
                production_stats.append("✅ 生产线运行正常，产品合格率高")
            elif company.performance_score > 40:
                production_stats.append("⚠️ 生产线存在瓶颈，需要优化")
            else:
                production_stats.append("❌ 生产线效率低下，急需改进")
            
            for stat in production_stats:
                scene += f"   {stat}\n"
        else:
            scene += "   🏭 选择一个公司查看生产详情\n"
        
        return scene
    
    def _generate_meeting_scene(self):
        """生成会议室场景"""
        company = self.current_company
        
        scene = f"""
        💼 {company.name if company else 'JC企业'} 董事会议室

    ╔══════════════════════════════════════╗
    ║  📺 营收报告 📊 市场分析 📈 发展规划  ║
    ╚══════════════════════════════════════╝
           |                    |
           v                    v
    
    🪑    👔         👔         👔    🪑
       ╔═══════════════════════════════╗
    👔 ║                               ║ 👔
       ║        📊 会议桌 📋           ║
    👔 ║                               ║ 👔  
       ╚═══════════════════════════════╝
    🪑    👔         👔         👔    🪑

💬 会议内容:
"""
        
        if company:
            topics = [
                f"📈 Q4营收: J${company.metrics.revenue/4:,.0f}",
                f"💰 净利润率: {(company.metrics.profit/company.metrics.revenue)*100:.1f}%",
                f"🎯 市场策略: 提升{company.metrics.market_share*100:.3f}%份额",
                f"🚀 发展目标: {company.stage.value.title()}阶段推进",
                f"⭐ 绩效评估: {company.performance_score:.1f}/100分"
            ]
            
            # 根据发展阶段添加特定议题
            if company.stage == CompanyStage.STARTUP:
                topics.append("💡 讨论融资计划和产品开发")
                topics.append("👥 招聘关键人才和团队建设")
            elif company.stage == CompanyStage.DEVELOPMENT:
                topics.append("📈 制定市场扩张策略")
                topics.append("🏗️ 计划新工厂建设和设备采购")
            elif company.stage == CompanyStage.EXPANSION:
                topics.append("🌐 研究国际市场进入策略")
                topics.append("🤝 考虑并购和战略合作机会")
            elif company.stage == CompanyStage.MATURE:
                topics.append("💎 优化运营效率和成本控制")
                topics.append("🔄 探索业务转型和创新方向")
            else:  # CompanyStage.DECLINE
                topics.append("🛠️ 制定业务重组和扭亏计划")
                topics.append("🚪 评估资产出售和收缩策略")
            
            # 根据表现评分添加风险提示
            if company.performance_score < 30:
                topics.append("🔴 高风险警告: 公司面临严重经营困难")
            elif company.performance_score < 50:
                topics.append("🟠 中等风险: 公司经营面临挑战")
            
            for topic in topics:
                scene += f"   💼 {topic}\n"
                
            if company.is_public:
                scene += f"   📈 股价表现: J${company.stock_price:.2f}\n"
            else:
                scene += "   🏢 讨论IPO上市计划\n"
        else:
            scene += "   💼 选择一个公司参加董事会议\n"
        
        return scene
    
    def _generate_datacenter_scene(self):
        """生成数据中心场景"""
        company = self.current_company
        
        scene = f"""
      💻 {company.name if company else 'JC企业'} 数据中心

    ╔═══════════════════════════════════════╗
    ║  🖥️ 💾 🖥️ 💾 🖥️ 💾 🖥️ 💾 🖥️  ║ 服务器A
    ║  💡 ⚡ 💡 ⚡ 💡 ⚡ 💡 ⚡ 💡  ║
    ╠═══════════════════════════════════════╣
    ║  🖥️ 💾 🖥️ 💾 🖥️ 💾 🖥️ 💾 🖥️  ║ 服务器B
    ║  💡 ⚡ 💡 ⚡ 💡 ⚡ 💡 ⚡ 💡  ║
    ╚═══════════════════════════════════════╝
           🌐 ← 网络连接 → 🌐

    👨‍💻 运维工程师    📊 数据分析师    🔒 安全专家

📊 系统状态:
"""
        
        if company:
            tech_level = company.performance_score / 20  # 转换为1-5级
            uptime = 95 + (tech_level * 1)  # 95-100%
            
            # 根据行业调整数据中心类型
            if "tech" in company.industry.value.lower():
                server_a = "🖥️ 💾 📱 💾 🖥️"
                server_b = "🖥️ 💾 🤖 💾 🖥️"
                scene = f"""
      💻 {company.name if company else 'JC企业'} 数据中心

    ╔═══════════════════════════════════════╗
    ║  {server_a}  ║ 服务器A
    ║  💡 ⚡ 💡 ⚡ 💡 ⚡ 💡 ⚡ 💡  ║
    ╠═══════════════════════════════════════╣
    ║  {server_b}  ║ 服务器B
    ║  💡 ⚡ 💡 ⚡ 💡 ⚡ 💡 ⚡ 💡  ║
    ╚═══════════════════════════════════════╝
           🌐 ← 网络连接 → 🌐

    👨‍💻 运维工程师    📊 数据分析师    🔒 安全专家

📊 系统状态:
"""
            
            data_stats = [
                f"⚡ 系统运行时间: {uptime:.1f}%",
                f"💾 数据处理能力: {tech_level:.1f}/5.0级",
                f"🔒 安全等级: {'高' if tech_level > 3 else '中'}",
                f"📈 数据吞吐量: {company.metrics.revenue/1000000:.1f}MB/s",
                f"🌐 网络状态: {'稳定' if tech_level > 2 else '需优化'}"
            ]
            
            # 根据表现评分添加系统状态
            if company.performance_score > 80:
                data_stats.append("🌟 系统性能优秀，无故障运行")
            elif company.performance_score > 60:
                data_stats.append("✅ 系统运行稳定，响应迅速")
            elif company.performance_score > 40:
                data_stats.append("⚠️ 系统存在性能瓶颈，需要优化")
            else:
                data_stats.append("❌ 系统故障频发，急需升级")
            
            for stat in data_stats:
                scene += f"   {stat}\n"
        else:
            scene += "   💻 选择一个公司查看数据中心\n"
        
        return scene
    
    def _generate_lab_scene(self):
        """生成实验室场景"""
        company = self.current_company
        
        scene = f"""
      🔬 {company.name if company else 'JC企业'} 创新实验室

    ╔═══════════════════════════════════════╗
    ║ 🧪  ⚗️  🔬  📋  💡  🧬  ⚙️  🔍 ║ 实验台A
    ║                                       ║
    ║ 👨‍🔬  👩‍🔬  📊  💻  🔧  ⚡  📈  🎯 ║ 实验台B
    ╚═══════════════════════════════════════╝

    📋 研发项目:     🏆 专利墙:     💡 创新成果:
      🔬 项目A        📜 专利1        ⚙️ 产品A
      🧪 项目B        📜 专利2        💻 产品B  
      ⚗️ 项目C        📜 专利3        🔍 产品C

🔬 研发状态:
"""
        
        if company:
            innovation_level = company.performance_score / 25  # 转换为1-4级
            
            # 根据行业调整研发项目
            if "tech" in company.industry.value.lower():
                projects = ["📱 智能手机", "💻 笔记本电脑", "⌚ 智能手表"]
                patents = ["🔋 快充技术", "📱 折叠屏", "🧠 AI芯片"]
                innovations = ["📱 新产品发布", "💻 性能提升", "⌚ 健康监测"]
            elif "manufacturing" in company.industry.value.lower():
                projects = ["🚗 新能源车", "🔧 智能制造", "🏭 自动化设备"]
                patents = ["🔋 电池技术", "🔧 机器人", "🏭 生产线"]
                innovations = ["🚗 续航提升", "🔧 效率优化", "🏭 成本降低"]
            elif "food" in company.industry.value.lower():
                projects = ["🥬 健康食品", "🍞 营养面包", "🥫 方便食品"]
                patents = ["🥬 保鲜技术", "🍞 发酵工艺", "🥫 包装技术"]
                innovations = ["🥬 营养强化", "🍞 口感改善", "🥫 保质期延长"]
            else:
                projects = ["🔬 基础研究", "🧪 应用研究", "⚙️ 工艺改进"]
                patents = ["🔬 理论突破", "🧪 实验方法", "⚙️ 生产工艺"]
                innovations = ["🔬 新发现", "🧪 新材料", "⚙️ 新工艺"]
            
            # 重新生成场景以包含行业特定元素
            scene = f"""
      🔬 {company.name if company else 'JC企业'} 创新实验室

    ╔═══════════════════════════════════════╗
    ║ 🧪  ⚗️  🔬  📋  💡  🧬  ⚙️  🔍 ║ 实验台A
    ║                                       ║
    ║ 👨‍🔬  👩‍🔬  📊  💻  🔧  ⚡  📈  🎯 ║ 实验台B
    ╚═══════════════════════════════════════╝

    📋 研发项目:     🏆 专利墙:     💡 创新成果:
      🔬 {projects[0]}        📜 {patents[0]}        ⚙️ {innovations[0]}
      🧪 {projects[1]}        📜 {patents[1]}        💻 {innovations[1]}  
      ⚗️ {projects[2]}        📜 {patents[2]}        🔍 {innovations[2]}

🔬 研发状态:
"""
            
            research_stats = [
                f"💡 创新能力: {innovation_level:.1f}/4.0级",
                f"🔬 研发投入: {company.metrics.revenue*0.1:,.0f}J$ (预估)",
                f"👨‍🔬 研发人员: {int(company.metrics.employees*0.2)}人",
                f"📋 活跃项目: {int(innovation_level*2)}个",
                f"🏆 技术水平: {'领先' if innovation_level > 3 else '先进' if innovation_level > 2 else '标准'}"
            ]
            
            # 根据表现评分添加研发状态
            if company.performance_score > 80:
                research_stats.append("🌟 研发进展顺利，多项突破在即")
            elif company.performance_score > 60:
                research_stats.append("✅ 研发按计划进行，成果显著")
            elif company.performance_score > 40:
                research_stats.append("⚠️ 研发遇到瓶颈，需要调整方向")
            else:
                research_stats.append("❌ 研发停滞不前，急需资源投入")
            
            for stat in research_stats:
                scene += f"   {stat}\n"
        else:
            scene += "   🔬 选择一个公司查看研发实验室\n"
        
        return scene
    
    def _get_scene_elements(self, scene_type):
        """获取场景动画元素"""
        elements = {
            "office": ["💡", "👥", "📊", "💼"],
            "factory": ["⚙️", "🔧", "🚛", "📦"],
            "meeting": ["👔", "📈", "💼", "📊"],
            "datacenter": ["💻", "⚡", "🌐", "💾"],
            "lab": ["🔬", "💡", "🧪", "⚗️"]
        }
        return elements.get(scene_type, ["💡"])
    
    def _start_animations(self):
        """开始动画效果"""
        if self.animation_timer:
            self.window.after_cancel(self.animation_timer)
        
        self._animate_scene()
        
    def _animate_scene(self):
        """动画场景"""
        if not self.window or not self.window.winfo_exists():
            return
        
        # 实现更复杂的动画效果
        if hasattr(self, 'scene_display') and self.scene_elements:
            # 获取当前场景内容
            content = self.scene_display.get(1.0, tk.END)
            
            # 随机选择一个动画元素进行闪烁
            if self.scene_elements:
                element = random.choice(self.scene_elements)
                # 在内容中找到该元素并添加动画效果
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if element in line and random.random() < 0.3:  # 30%概率闪烁
                        # 简单的闪烁效果（通过颜色变化实现）
                        # 这里可以扩展为更复杂的动画
                        pass
        
        # 继续下一帧动画
        self.animation_timer = self.window.after(1000, self._animate_scene)
    
    def _start_auto_updates(self):
        """启动自动更新"""
        if self.update_timer:
            self.window.after_cancel(self.update_timer)
        
        self._auto_update()
        
    def _auto_update(self):
        """自动更新界面"""
        if not self.window or not self.window.winfo_exists():
            return
        
        # 更新公司信息
        if self.current_company and hasattr(self, 'company_info_text'):
            self._update_company_info()
        
        # 重新生成当前场景
        if self.current_scene:
            self._switch_scene(self.current_scene)
        
        # 每5秒更新一次
        self.update_timer = self.window.after(5000, self._auto_update)
    
    def _update_company_info(self):
        """更新公司信息显示"""
        if not self.current_company or not hasattr(self, 'company_info_text'):
            return
        
        company = self.current_company
        info_content = f"""
🏢 {company.name} ({company.symbol})
{'='*40}

📈 发展阶段: {company.stage.value.title()}
🏭 行业领域: {company.industry.value.title()}
📅 成立时间: {company.founded_date}
⭐ 表现评分: {company.performance_score:.1f}/100
🎯 风险等级: {company.risk_level}/5

💰 财务状况:
  营业收入: J${company.metrics.revenue:,.0f}
  净利润: J${company.metrics.profit:,.0f}
  总资产: J${company.metrics.assets:,.0f}
  负债: J${company.metrics.liabilities:,.0f}
  净资产: J${company.metrics.calculate_equity():,.0f}

👥 人力资源:
  员工总数: {company.metrics.employees}人
  人均产值: J${company.metrics.revenue/company.metrics.employees:,.0f}

📊 市场表现:
  市场份额: {company.metrics.market_share*100:.3f}%
  增长率: {company.metrics.growth_rate*100:.1f}%
  债务率: {company.metrics.debt_ratio*100:.1f}%

{'📈 已上市' if company.is_public else '🏢 未上市'}
{f'股价: J${company.stock_price:.2f}' if company.is_public else ''}
{f'市值: J${company.market_cap:,.0f}' if company.is_public else ''}
"""
        
        self.company_info_text.config(state=tk.NORMAL)
        self.company_info_text.delete(1.0, tk.END)
        self.company_info_text.insert(tk.END, info_content)
        self.company_info_text.config(state=tk.DISABLED)
    
    def _start_company_creation(self):
        """启动公司创建向导"""
        self.main_app.print_to_output("🚀 启动公司创建向导...")
        
        # 关闭当前窗口
        if self.window:
            self.window.destroy()
        
        # 启动创建流程
        from .company_creation import CompanyCreationWizard
        wizard = CompanyCreationWizard(self.main_app)
        result = wizard.start_creation()
        self.main_app.print_to_output(result)
    
    def _execute_action(self, action):
        """执行快捷操作"""
        if not self.current_company:
            self.main_app.print_to_output("❌ 请先选择一个公司", '#FF0000')
            return
        
        from .company_operations import CompanyOperations
        operations = CompanyOperations(self.main_app)
        
        success, result = operations.execute_operation(
            self.current_company.company_id, 
            action
        )
        
        color = '#00FF00' if success else '#FF0000'
        self.main_app.print_to_output(result, color)
        
        if success:
            # 刷新界面
            self._refresh_interface()
    
    def _refresh_interface(self):
        """刷新界面"""
        if self.window and self.window.winfo_exists():
            # 重新创建控制面板
            for widget in self.window.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.LabelFrame) and "公司状态" in subchild.cget("text"):
                                    subchild.destroy()
                                    self._create_company_info(child)
                                    break
    
    def close(self):
        """关闭GUI"""
        if self.animation_timer:
            self.window.after_cancel(self.animation_timer)
        if self.update_timer:
            self.window.after_cancel(self.update_timer)
        if self.window:
            self.window.destroy()
            self.window = None