import tkinter as tk
from tkinter import ttk
import datetime

class AchievementsView:
    def __init__(self, parent):
        """初始化成就视图"""
        self.parent = parent
        self.frame = ttk.Frame(parent)
        
        # 创建标题
        title_frame = ttk.Frame(self.frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(title_frame, text="成就系统", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 已解锁成就标签页
        self.unlocked_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.unlocked_frame, text="已解锁")
        
        # 未解锁成就标签页
        self.locked_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.locked_frame, text="未解锁")
        
        # 创建已解锁成就列表
        self.setup_unlocked_achievements()
        
        # 创建未解锁成就列表
        self.setup_locked_achievements()
        
        # 成就管理器引用
        self.achievement_manager = None
    
    def get_frame(self):
        """获取视图的主框架"""
        return self.frame
    
    def set_achievement_manager(self, achievement_manager):
        """设置成就管理器"""
        self.achievement_manager = achievement_manager
        self.update_achievements()
    
    def setup_unlocked_achievements(self):
        """设置已解锁成就列表"""
        # 创建树形视图
        columns = ("名称", "描述", "解锁时间")
        self.unlocked_tree = ttk.Treeview(self.unlocked_frame, columns=columns, show="headings", height=15)
        
        # 配置列
        self.unlocked_tree.heading("名称", text="名称")
        self.unlocked_tree.heading("描述", text="描述")
        self.unlocked_tree.heading("解锁时间", text="解锁时间")
        
        self.unlocked_tree.column("名称", width=150)
        self.unlocked_tree.column("描述", width=350)
        self.unlocked_tree.column("解锁时间", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.unlocked_frame, orient=tk.VERTICAL, command=self.unlocked_tree.yview)
        self.unlocked_tree.configure(yscrollcommand=scrollbar.set)
        
        self.unlocked_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_locked_achievements(self):
        """设置未解锁成就列表"""
        # 创建树形视图
        columns = ("名称", "描述", "进度")
        self.locked_tree = ttk.Treeview(self.locked_frame, columns=columns, show="headings", height=15)
        
        # 配置列
        self.locked_tree.heading("名称", text="名称")
        self.locked_tree.heading("描述", text="描述")
        self.locked_tree.heading("进度", text="进度")
        
        self.locked_tree.column("名称", width=150)
        self.locked_tree.column("描述", width=350)
        self.locked_tree.column("进度", width=150)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.locked_frame, orient=tk.VERTICAL, command=self.locked_tree.yview)
        self.locked_tree.configure(yscrollcommand=scrollbar.set)
        
        self.locked_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def update_achievements(self):
        """更新成就列表"""
        if not self.achievement_manager:
            return
        
        # 清空现有项
        for item in self.unlocked_tree.get_children():
            self.unlocked_tree.delete(item)
        
        for item in self.locked_tree.get_children():
            self.locked_tree.delete(item)
        
        # 获取已解锁成就
        unlocked_achievements = self.achievement_manager.get_unlocked_achievements()
        
        # 添加已解锁成就到列表
        for achievement in unlocked_achievements:
            self.unlocked_tree.insert("", tk.END, values=(
                achievement.name,
                achievement.description,
                achievement.unlock_date
            ))
        
        # 获取未解锁成就（不包括隐藏成就）
        locked_achievements = self.achievement_manager.get_locked_achievements(include_hidden=False)
        
        # 添加未解锁成就到列表
        for achievement in locked_achievements:
            # 这里可以添加进度信息，如果成就类有提供的话
            progress = "未知" if not hasattr(achievement, "progress") else f"{achievement.progress}%"
            
            self.locked_tree.insert("", tk.END, values=(
                achievement.name,
                achievement.description,
                progress
            ))