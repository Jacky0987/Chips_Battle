#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 轻量级入口文件
重构后的主程序入口，委托给统一的启动器

注意：此文件已重构为轻量级入口，核心逻辑已迁移到console.py
新的启动方式：
- python launcher.py --console    # 控制台模式
- python launcher.py --gui        # 图形界面模式
"""

import sys
import os
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入统一的启动器
from launcher import GameLauncher


def main():
    """主入口函数 - 委托给GameLauncher"""
    launcher = GameLauncher()
    launcher.run()


if __name__ == "__main__":
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 为了向后兼容，解析命令行参数
    parser = argparse.ArgumentParser(
        description='Chips Battle Remake v3.0 Alpha - 专业金融交易模拟系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
启动模式:
  python main.py          # 控制台模式（默认）
  python main.py --gui    # GUI模式
  python main.py --cli    # 强制控制台模式
  
注意: 建议使用新的启动器:
  python launcher.py --console    # 控制台模式
  python launcher.py --gui        # 图形界面模式
        '''
    )
    
    parser.add_argument(
        '--gui', 
        action='store_true',
        help='启动GUI模式（图形界面）'
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='强制启动控制台模式'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='启用调试模式'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Chips Battle Remake v3.0 Alpha'
    )
    
    # 添加位置参数用于直接命令执行
    parser.add_argument(
        'command',
        nargs='*',
        help='要直接执行的命令（可选）'
    )
    
    args = parser.parse_args()
    
    # 设置调试模式
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("🐛 调试模式已启用")
    
    # 确定启动模式
    if args.gui and not args.cli:
        print("🖥️  启动GUI模式...")
        print("📊 Chips Battle Remake v3.0 Alpha - 专业交易系统")
        print("🎮 正在初始化图形界面...")
        
        # 启动GUI模式
        try:
            from terminal.gui_main import ChipsBattleGUI
            gui = ChipsBattleGUI()
            gui.run()
        except ImportError as e:
            print(f"GUI模块导入失败: {e}")
            print("请确保所有GUI依赖已正确安装")
            sys.exit(1)
        except Exception as e:
            print(f"GUI启动失败: {e}")
            sys.exit(1)
    else:
        if args.cli:
            print("💻 强制启动控制台模式...")
        else:
            print("💻 启动控制台模式（默认）...")
            print("💡 提示: 使用 'python main.py --gui' 启动图形界面")
            print("💡 新建议: 使用 'python launcher.py --console' 启动控制台模式")
        
        # 运行控制台游戏
        try:
            # 如果有命令参数，使用console.py的直接命令执行
            if args.command:
                from console import run_direct_command
                import asyncio
                success = asyncio.run(run_direct_command(args.command))
                sys.exit(0 if success else 1)
            else:
                # 否则启动正常游戏
                main()
        except KeyboardInterrupt:
            print("\n🎮 游戏已退出")
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)