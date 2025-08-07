#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
银行数据库迁移脚本

为bank_cards表添加缺失的字段以支持卡账一体化
"""

import asyncio
import sqlite3
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class BankMigration:
    """银行数据库迁移器"""
    
    def __init__(self):
        self.console = Console()
        self.db_path = Path(__file__).parent.parent / "data" / "database" / "chips_battle.db"
    
    async def migrate(self):
        """执行迁移"""
        self.console.print(Panel(
            Text("🔄 正在执行银行数据库迁移...", style="bold blue"),
            title="数据库迁移",
            border_style="blue"
        ))
        
        try:
            # 连接数据库
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bank_cards'")
            if not cursor.fetchone():
                self.console.print("❌ bank_cards表不存在")
                return False
            
            # 检查字段是否已存在
            cursor.execute("PRAGMA table_info(bank_cards)")
            columns = {row[1] for row in cursor.fetchall()}
            
            migrations_needed = []
            
            # 检查需要添加的字段
            required_fields = [
                ("currency_id", "INTEGER REFERENCES currencies(id) DEFAULT 1"),
                ("account_name", "VARCHAR(100) DEFAULT '默认账户'"),
                ("account_type", "VARCHAR(20) DEFAULT 'savings'"),
                ("account_number", "VARCHAR(20)"),  # 先不加UNIQUE约束
                ("balance", "NUMERIC(20, 8) DEFAULT 0"),
                ("available_balance", "NUMERIC(20, 8) DEFAULT 0"),
                ("frozen_balance", "NUMERIC(20, 8) DEFAULT 0"),
                ("is_default", "BOOLEAN DEFAULT 1"),
                ("daily_transfer_limit", "NUMERIC(20, 8) DEFAULT 100000"),
                ("monthly_transfer_limit", "NUMERIC(20, 8) DEFAULT 1000000"),
                ("interest_rate", "NUMERIC(8, 6) DEFAULT 0.015"),
                ("last_interest_date", "DATETIME")  # 移除DEFAULT CURRENT_TIMESTAMP
            ]
            
            for field_name, field_def in required_fields:
                if field_name not in columns:
                    migrations_needed.append((field_name, field_def))
            
            if not migrations_needed:
                self.console.print("✅ 所有字段都已存在，无需迁移")
                return True
            
            # 执行迁移
            for field_name, field_def in migrations_needed:
                try:
                    cursor.execute(f"ALTER TABLE bank_cards ADD COLUMN {field_name} {field_def}")
                    self.console.print(f"✅ 已添加字段: {field_name}")
                except sqlite3.OperationalError as e:
                    self.console.print(f"❌ 添加字段 {field_name} 失败: {e}")
                    return False
            
            # 为现有卡片生成账户号码
            cursor.execute("SELECT card_id FROM bank_cards WHERE account_number IS NULL OR account_number = ''")
            cards_without_account = cursor.fetchall()
            
            for (card_id,) in cards_without_account:
                account_number = self._generate_account_number()
                cursor.execute(
                    "UPDATE bank_cards SET account_number = ? WHERE card_id = ?",
                    (account_number, card_id)
                )
            
            # 设置last_interest_date的默认值
            cursor.execute("UPDATE bank_cards SET last_interest_date = CURRENT_TIMESTAMP WHERE last_interest_date IS NULL")
            
            # 添加UNIQUE约束
            try:
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_bank_cards_account_number ON bank_cards(account_number)")
                self.console.print("✅ 已添加account_number唯一约束")
            except sqlite3.OperationalError as e:
                self.console.print(f"⚠️ 添加account_number唯一约束失败: {e}")
            
            # 提交更改
            conn.commit()
            
            self.console.print(Panel(
                Text("🎉 银行数据库迁移完成！", style="bold green"),
                title="迁移成功",
                border_style="green"
            ))
            
            return True
            
        except Exception as e:
            self.console.print(Panel(
                Text(f"❌ 数据库迁移失败: {str(e)}", style="bold red"),
                title="迁移失败",
                border_style="red"
            ))
            return False
            
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _generate_account_number(self) -> str:
        """生成账户号码"""
        import random
        import string
        
        # 生成16位账户号码
        prefix = "8888"  # 银行账户前缀
        middle_digits = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        return prefix + middle_digits


async def main():
    """主函数"""
    import sys
    
    migration = BankMigration()
    success = await migration.migrate()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())