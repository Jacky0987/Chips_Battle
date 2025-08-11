#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 统一启动器
支持CLI和GUI两种模式的统一入口点
"""

import sys
import os
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn


class GameLauncher:
    """游戏启动器类，负责统一管理CLI和GUI模式的启动"""
    
    def __init__(self):
        self.console = Console()
        self.settings = Settings()
        self.logger = logging.getLogger(__name__)
        self.project_root = project_root
        
        # 配置日志
        self._setup_logging()
        
        # 加载游戏信息
        self.game_info = self._load_game_info()
        
        # 记录启动信息
        self.logger.info("Chips Battle 启动器开始运行")
        self.logger.info(f"Python版本: {sys.version}")
        self.logger.info(f"工作目录: {os.getcwd()}")
        self.logger.info(f"项目根目录: {self.project_root}")
        
    def _setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=getattr(logging, self.settings.LOG_LEVEL),
            format=self.settings.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.project_root / 'chips_battle.log', encoding='utf-8')
            ]
        )
        
    def _load_game_info(self) -> Dict[str, Any]:
        """加载游戏信息配置"""
        try:
            info_file = project_root / "data" / "config.json"
            if info_file.exists():
                with open(info_file, 'r', encoding='utf-8') as f:
                    import json
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"加载游戏信息配置失败: {e}")
        
        # 返回默认配置
        return {
            "game": {
                "name": "CHIPS BATTLE REMAKE",
                "version": "v3.0 Alpha",
                "subtitle": "命令驱动的金融模拟游戏",
                "welcome_title": "欢迎来到 Chips Battle"
            }
        }
    
    def _show_startup_banner(self):
        """显示启动横幅"""
        game_data = self.game_info.get("game", {})
        
        # 创建欢迎面板
        welcome_text = Text()
        welcome_text.append(game_data.get("welcome_title", "欢迎来到 Chips Battle"), style="bold cyan")
        welcome_text.append("\n", style="reset")
        welcome_text.append(game_data.get("name", "CHIPS BATTLE REMAKE"), style="bold green")
        welcome_text.append(" ", style="reset")
        welcome_text.append(game_data.get("version", "v3.0 Alpha"), style="bold yellow")
        welcome_text.append("\n", style="reset")
        welcome_text.append(game_data.get("subtitle", "命令驱动的金融模拟游戏"), style="italic blue")
        
        panel = Panel(
            welcome_text,
            title="[bold red]🎮[/bold red]",
            border_style="bold cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
        
    def _parse_arguments(self) -> argparse.Namespace:
        """解析命令行参数"""
        parser = argparse.ArgumentParser(
            description="Chips Battle Remake - 命令驱动的金融模拟游戏",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
启动模式:
  --console, -c    启动控制台模式（默认）
  --gui, -g        启动图形界面模式
  --help, -h        显示帮助信息
  --version, -v     显示版本信息

示例:
  %(prog)s --console     # 启动控制台模式
  %(prog)s --gui         # 启动图形界面模式
  %(prog)s -c            # 启动控制台模式（简写）
  
向后兼容:
  python main.py                 # 原有入口（已重构为轻量级）
  python console.py              # 直接启动控制台模式
            """
        )
        
        # 添加参数
        parser.add_argument(
            '--console', '-c',
            action='store_true',
            help='启动控制台模式（默认）'
        )
        
        parser.add_argument(
            '--gui', '-g',
            action='store_true',
            help='启动图形界面模式'
        )
        
        parser.add_argument(
            '--auto', '-a',
            action='store_true',
            help='自动检测启动模式（默认）'
        )
        
        parser.add_argument(
            '--version', '-v',
            action='version',
            version=f'%(prog)s {self.settings.VERSION}'
        )
        
        parser.add_argument(
            '--debug',
            action='store_true',
            help='启用调试模式'
        )
        
        return parser.parse_args()
    
    def _show_loading_animation(self, message: str = "正在启动..."):
        """显示加载动画"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"[cyan]{message}", total=100)
            
            # 模拟加载过程
            for i in range(1, 101):
                progress.update(task, advance=1)
                import time
                time.sleep(0.02)  # 快速加载，让用户看到效果
    
    def _launch_console_mode(self):
        """启动控制台模式"""
        self.logger.info("启动控制台模式")
        
        # 显示启动横幅
        self._show_startup_banner()
        
        # 显示加载动画
        self._show_loading_animation("正在初始化控制台模式...")
        
        # 导入并启动控制台模式
        try:
            from console import ConsoleGame
            
            # 创建控制台游戏实例
            console_game = ConsoleGame()
            
            # 运行游戏
            self.console.print("[green]✓[/green] 控制台模式初始化完成")
            self.console.print()
            
            # 启动游戏主循环
            asyncio.run(console_game.run())
            
        except ImportError as e:
            self.console.print(f"[red]✗[/red] 无法导入控制台模块: {e}")
            self.logger.error(f"导入控制台模块失败: {e}", exc_info=True)
            sys.exit(1)
        except Exception as e:
            self.console.print(f"[red]✗[/red] 启动控制台模式失败: {e}")
            self.logger.error(f"启动控制台模式失败: {e}", exc_info=True)
            sys.exit(1)
    
    def _launch_gui_mode(self):
        """启动图形界面模式"""
        self.logger.info("启动图形界面模式")
        
        # 显示启动横幅
        self._show_startup_banner()
        
        # 显示加载动画
        self._show_loading_animation("正在初始化图形界面模式...")
        
        # 导入并启动GUI模式
        try:
            from terminal.gui_main import ChipsBattleGUI
            import tkinter as tk
            
            # 创建GUI实例
            gui_app = ChipsBattleGUI()
            
            # 启动GUI主循环
            self.console.print("[green]✓[/green] 图形界面模式初始化完成")
            self.console.print("[yellow]提示: 图形界面将在新窗口中打开[/yellow]")
            self.console.print()
            
            # 启动GUI
            gui_app.run()
            
        except ImportError as e:
            self.console.print(f"[red]✗[/red] 无法导入GUI模块: {e}")
            self.logger.error(f"导入GUI模块失败: {e}", exc_info=True)
            sys.exit(1)
        except Exception as e:
            self.console.print(f"[red]✗[/red] 启动图形界面模式失败: {e}")
            self.logger.error(f"启动图形界面模式失败: {e}", exc_info=True)
            sys.exit(1)
    
    def _detect_mode(self) -> str:
        """自动检测启动模式
        
        Returns:
            启动模式 ('console' 或 'gui')
        """
        try:
            # 检查是否支持图形界面
            import tkinter
            root = tkinter.Tk()
            root.withdraw()  # 隐藏窗口
            root.destroy()
            
            # 检查是否在图形界面环境中
            # 在macOS上，检查DISPLAY环境变量
            if os.environ.get('DISPLAY') or sys.platform == 'darwin':
                # 在macOS上，默认使用控制台模式，除非明确指定GUI
                self.logger.info("检测到图形环境，但默认使用控制台模式")
                return 'console'
            else:
                self.logger.info("未检测到图形环境，使用控制台模式")
                return 'console'
                
        except Exception as e:
            self.logger.warning(f"图形界面检测失败: {e}，使用控制台模式")
            return 'console'
    
    def run(self):
        """运行启动器"""
        try:
            # 解析命令行参数
            args = self._parse_arguments()
            
            # 如果启用了调试模式，更新设置
            if args.debug:
                self.settings.DEBUG = True
                self.logger.setLevel(logging.DEBUG)
                self.logger.info("调试模式已启用")
            
            # 确定启动模式
            if args.gui:
                # GUI模式
                self.logger.info("选择的启动模式: gui")
                self._launch_gui_mode()
            elif args.console:
                # 控制台模式
                self.logger.info("选择的启动模式: console")
                self._launch_console_mode()
            else:
                # 自动检测模式
                mode = self._detect_mode()
                self.logger.info(f"选择的启动模式: {mode}")
                print(f"🔍 自动检测到启动模式: {mode.upper()}")
                if mode == 'gui':
                    self._launch_gui_mode()
                else:
                    self._launch_console_mode()
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]用户中断，程序退出[/yellow]")
            self.logger.info("用户中断程序")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"[red]✗[/red] 启动器运行失败: {e}")
            self.logger.error(f"启动器运行失败: {e}", exc_info=True)
            sys.exit(1)
        finally:
            self.logger.info("Chips Battle 启动器结束运行")


def main():
    """主入口函数"""
    launcher = GameLauncher()
    launcher.run()


if __name__ == "__main__":
    main()