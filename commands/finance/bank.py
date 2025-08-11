# -*- coding: utf-8 -*-
"""
银行命令

提供银行相关的所有功能，包括账户管理、存取款、转账、贷款等。
"""

from typing import List
from commands.base import FinanceCommand, CommandResult, CommandContext
from commands.bank import bank_commands


class BankCommand(FinanceCommand):
    """银行命令"""
    
    def __init__(self):
        super().__init__()
    
    @property
    def name(self) -> str:
        return "bank"
    
    @property
    def aliases(self) -> List[str]:
        return ["b", "banking"]
    
    @property
    def description(self) -> str:
        return "银行系统 - 管理银行卡、账户、存取款、转账、贷款等"
    
    @property
    def usage(self) -> str:
        return "bank [子命令] [参数...]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行银行命令
        
        Args:
            args: 命令参数列表
            context: 命令执行上下文
            
        Returns:
            命令执行结果
        """
        try:
            user = context.user
            if not user:
                return self.error("无法获取用户信息")
            
            # 调用现有的银行命令处理逻辑
            result_message = await bank_commands.bank(user.user_id, args)
            
            # 检查是否是错误消息
            if result_message.startswith("未知的银行命令:") or "❌" in result_message:
                return self.error(result_message)
            
            return self.success(result_message)
            
        except Exception as e:
            self.logger.error(f"银行命令执行失败: {e}")
            return self.error(f"银行命令执行失败: {str(e)}")
    
    def get_help(self) -> str:
        """获取银行命令帮助信息"""
        return """
🏦 银行系统帮助:

📋 基本命令:
  bank                    - 显示银行概览
  bank help              - 显示此帮助信息

💳 银行卡管理:
  bank apply_card        - 查看可申请的银行
  bank apply_card <银行>  - 申请指定银行的银行卡
  bank cards             - 查看我的银行卡

🏛️ 账户管理:
  bank accounts          - 查看我的银行账户

💰 存取款:
  bank deposit <账户ID> <金额> [描述]    - 存款
  bank withdraw <账户ID> <金额> [描述]   - 取款
  bank transfer <转出账户> <转入用户> <转入账户> <金额> [描述] - 转账

💸 贷款管理:
  bank loan              - 查看贷款信息
  bank loan apply <类型> <金额> <期限> [用途] - 申请贷款
  bank loan list         - 查看贷款列表
  bank repay <贷款ID> <金额> [账户ID]    - 还款

📊 信用管理:
  bank credit            - 查看信用档案

🎯 银行任务:
  bank task              - 任务中心概览
  bank task list [银行]   - 查看可用任务
  bank task recommend    - 查看推荐任务
  bank task my           - 查看我的任务
  bank task accept <任务ID> - 接取任务
  bank task submit <任务ID> - 提交任务

💡 提示:
  - 使用银行卡前需要先申请
  - 建议从邮政储蓄银行(PSBJC)开始
  - 完成银行任务可以获得奖励和信用分
"""