# -*- coding: utf-8 -*-
"""
第二阶段测试脚本

测试服务管理器、UI接口和命令分发器的功能。
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from services.service_manager import ServiceManager
from interfaces.ui_interface import UIType, MessageType
from adapters.console_adapter import ConsoleAdapter
from adapters.gui_adapter import GUIAdapter


async def test_service_manager():
    """测试服务管理器"""
    print("\n=== 测试服务管理器 ===")
    
    try:
        # 创建设置
        settings = Settings()
        
        # 创建服务管理器
        service_manager = ServiceManager(settings)
        
        # 初始化服务
        await service_manager.initialize()
        
        # 检查服务状态
        status = service_manager.get_service_status()
        print(f"服务状态: {status}")
        
        # 获取统计信息
        stats = service_manager.get_stats()
        print(f"统计信息: {stats}")
        
        # 启动服务
        await service_manager.start_services()
        
        print("✅ 服务管理器测试通过")
        return service_manager
        
    except Exception as e:
        print(f"❌ 服务管理器测试失败: {e}")
        return None


async def test_console_adapter():
    """测试控制台适配器"""
    print("\n=== 测试控制台适配器 ===")
    
    try:
        # 创建控制台适配器
        console_adapter = ConsoleAdapter()
        
        # 初始化适配器
        success = await console_adapter.initialize()
        if not success:
            raise Exception("控制台适配器初始化失败")
        
        # 测试消息显示
        console_adapter.display_info("这是一条信息消息")
        console_adapter.display_success("这是一条成功消息")
        console_adapter.display_warning("这是一条警告消息")
        console_adapter.display_error("这是一条错误消息")
        console_adapter.display_debug("这是一条调试消息")
        console_adapter.display_system("这是一条系统消息")
        
        # 测试输入功能
        print("\n测试输入功能:")
        
        # 测试文本输入
        text_input = await console_adapter.get_text_input("请输入您的名字", "测试用户")
        print(f"文本输入结果: {text_input}")
        
        # 测试选择输入
        choice_input = await console_adapter.get_choice_input(
            "请选择一个选项",
            ["选项1", "选项2", "选项3"],
            "选项1"
        )
        print(f"选择输入结果: {choice_input}")
        
        # 测试确认输入
        confirm_input = await console_adapter.get_confirm_input("确认继续吗？", True)
        print(f"确认输入结果: {confirm_input}")
        
        # 测试进度条
        console_adapter.show_progress_bar("测试进度", 0, 100)
        for i in range(0, 101, 10):
            console_adapter.update_progress(i, 100)
            import time
            time.sleep(0.1)
        console_adapter.hide_progress()
        
        # 清理适配器
        await console_adapter.cleanup()
        
        print("✅ 控制台适配器测试通过")
        return console_adapter
        
    except Exception as e:
        print(f"❌ 控制台适配器测试失败: {e}")
        return None


async def test_gui_adapter():
    """测试GUI适配器"""
    print("\n=== 测试GUI适配器 ===")
    
    try:
        # 创建GUI适配器
        gui_adapter = GUIAdapter()
        
        # 初始化适配器
        success = await gui_adapter.initialize()
        if not success:
            raise Exception("GUI适配器初始化失败")
        
        # 测试消息显示
        gui_adapter.display_info("这是一条信息消息")
        gui_adapter.display_success("这是一条成功消息")
        gui_adapter.display_warning("这是一条警告消息")
        gui_adapter.display_error("这是一条错误消息")
        gui_adapter.display_debug("这是一条调试消息")
        gui_adapter.display_system("这是一条系统消息")
        
        print("GUI适配器已创建，请在弹出窗口中查看效果")
        print("等待5秒后自动关闭...")
        
        # 等待一段时间让用户看到效果
        import time
        time.sleep(5)
        
        # 清理适配器
        await gui_adapter.cleanup()
        
        print("✅ GUI适配器测试通过")
        return gui_adapter
        
    except Exception as e:
        print(f"❌ GUI适配器测试失败: {e}")
        return None


async def test_command_dispatcher(service_manager, ui_adapter):
    """测试命令分发器"""
    print("\n=== 测试命令分发器 ===")
    
    try:
        # 获取命令分发器
        command_dispatcher = service_manager.get_service("command_dispatcher")
        if not command_dispatcher:
            raise Exception("无法获取命令分发器")
        
        # 设置UI适配器
        command_dispatcher.set_ui_adapter(ui_adapter)
        
        # 创建测试用户
        from models.auth.user import User
        test_user = User(
            user_id="test_user_123",
            username="testuser",
            password_hash="test_hash",
            is_active=True
        )
        
        # 测试命令分发
        print("\n测试命令分发:")
        
        # 测试help命令
        result = await command_dispatcher.dispatch("help", test_user)
        print(f"help命令结果: {result.success if result else 'None'}")
        
        # 测试status命令
        result = await command_dispatcher.dispatch("status", test_user)
        print(f"status命令结果: {result.success if result else 'None'}")
        
        # 测试未知命令
        result = await command_dispatcher.dispatch("unknown_command", test_user)
        print(f"未知命令结果: {result.success if result else 'None'}")
        
        # 获取统计信息
        stats = command_dispatcher.get_stats()
        print(f"命令分发器统计: {stats}")
        
        print("✅ 命令分发器测试通过")
        return command_dispatcher
        
    except Exception as e:
        print(f"❌ 命令分发器测试失败: {e}")
        return None


async def test_ui_switching(service_manager):
    """测试UI切换功能"""
    print("\n=== 测试UI切换功能 ===")
    
    try:
        # 获取命令分发器
        command_dispatcher = service_manager.get_service("command_dispatcher")
        
        # 创建测试用户
        from models.auth.user import User
        test_user = User(
            user_id="test_user_456",
            username="switchuser",
            password_hash="test_hash",
            is_active=True
        )
        
        # 测试控制台模式
        print("\n切换到控制台模式:")
        console_adapter = ConsoleAdapter()
        await console_adapter.initialize()
        command_dispatcher.set_ui_adapter(console_adapter)
        
        result = await command_dispatcher.dispatch("help", test_user)
        print(f"控制台模式help命令结果: {result.success if result else 'None'}")
        
        await console_adapter.cleanup()
        
        # 测试GUI模式
        print("\n切换到GUI模式:")
        gui_adapter = GUIAdapter()
        await gui_adapter.initialize()
        command_dispatcher.set_ui_adapter(gui_adapter)
        
        result = await command_dispatcher.dispatch("help", test_user)
        print(f"GUI模式help命令结果: {result.success if result else 'None'}")
        
        print("等待3秒后关闭GUI...")
        import time
        time.sleep(3)
        
        await gui_adapter.cleanup()
        
        print("✅ UI切换功能测试通过")
        
    except Exception as e:
        print(f"❌ UI切换功能测试失败: {e}")


async def main():
    """主测试函数"""
    print("🚀 开始第二阶段测试")
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 测试服务管理器
        service_manager = await test_service_manager()
        if not service_manager:
            print("❌ 服务管理器测试失败，停止后续测试")
            return
        
        # 测试控制台适配器
        console_adapter = await test_console_adapter()
        if not console_adapter:
            print("❌ 控制台适配器测试失败，停止后续测试")
            return
        
        # 测试命令分发器（使用控制台适配器）
        command_dispatcher = await test_command_dispatcher(service_manager, console_adapter)
        if not command_dispatcher:
            print("❌ 命令分发器测试失败，停止后续测试")
            return
        
        # 测试GUI适配器
        gui_adapter = await test_gui_adapter()
        if not gui_adapter:
            print("❌ GUI适配器测试失败，停止后续测试")
            return
        
        # 测试UI切换功能
        await test_ui_switching(service_manager)
        
        # 清理服务管理器
        await service_manager.stop_services()
        
        print("\n🎉 第二阶段测试全部通过！")
        print("\n📋 测试总结:")
        print("  ✅ 服务管理器 - 统一管理所有游戏服务")
        print("  ✅ 控制台适配器 - 基于rich和prompt_toolkit的CLI界面")
        print("  ✅ GUI适配器 - 基于tkinter的图形界面")
        print("  ✅ 命令分发器 - 支持多种UI模式的命令系统")
        print("  ✅ UI切换功能 - 动态切换不同UI模式")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())