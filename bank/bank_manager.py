from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

from .bank_types import BANK_TYPES, BankRelationship, BankCategory
from .task_system import TaskManager, TaskType
from .credit_system import CreditManager

class BankManager:
    """银行系统管理器"""
    
    def __init__(self, main_app):
        self.main_app = main_app
        self.banks = BANK_TYPES
        self.task_manager = TaskManager()
        self.credit_manager = CreditManager()
        self.user_relationships = {}  # user_id -> {bank_id: BankRelationship}
        self.user_bank_data = {}      # user_id -> bank_data
        
    def get_user_bank_data(self, user_id):
        """获取用户银行数据"""
        if user_id not in self.user_bank_data:
            self.user_bank_data[user_id] = {
                'relationships': {},
                'active_loans': {},
                'deposits': {},
                'credit_history': [],
                'preferred_bank': 'JC_COMMERCIAL'
            }
        return self.user_bank_data[user_id]
        
    def get_bank_relationship(self, user_id, bank_id):
        """获取用户与银行的关系"""
        if user_id not in self.user_relationships:
            self.user_relationships[user_id] = {}
            
        if bank_id not in self.user_relationships[user_id]:
            user_data = self.main_app.user_data or {}
            self.user_relationships[user_id][bank_id] = BankRelationship(bank_id, user_data)
            
        return self.user_relationships[user_id][bank_id]
        
    def check_bank_unlock(self, user_data, bank_id):
        """检查银行是否解锁"""
        if bank_id not in self.banks:
            return False, "银行不存在"
            
        bank = self.banks[bank_id]
        user_level = user_data.get('level', 1)
        
        if user_level < bank.unlock_level:
            return False, f"需要等级 {bank.unlock_level}，当前等级 {user_level}"
            
        # 检查其他解锁条件
        for req_key, req_value in bank.unlock_requirements.items():
            if req_key == 'total_trades':
                if user_data.get('trades_count', 0) < req_value:
                    return False, f"需要完成 {req_value} 笔交易"
            elif req_key == 'portfolio_value':
                # 需要计算投资组合价值
                portfolio_value = self._calculate_portfolio_value(user_data)
                if portfolio_value < req_value:
                    return False, f"需要投资组合价值达到 J${req_value:,}"
            elif req_key == 'net_worth':
                net_worth = user_data.get('cash', 0) + self._calculate_portfolio_value(user_data)
                if net_worth < req_value:
                    return False, f"需要净资产达到 J${req_value:,}"
            # 可以添加更多条件检查
                    
        return True, "银行已解锁"
        
    def _calculate_portfolio_value(self, user_data):
        """计算投资组合价值"""
        # 简化计算，实际应该从市场数据获取实时价格
        portfolio = user_data.get('portfolio', {})
        total_value = 0
        
        for symbol, position in portfolio.items():
            if symbol != 'pending_orders' and isinstance(position, dict):
                quantity = position.get('quantity', 0)
                if quantity > 0:
                    # 简化：假设平均价格为100
                    total_value += quantity * 100
                    
        return total_value
        
    def show_bank_system_menu(self):
        """显示银行系统主菜单"""
        user_id = self.main_app.user_manager.current_user
        user_data = self.main_app.user_data or {}
        
        menu_text = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                            🏦 JackyCoin 银行系统 🏦                                      ║
║                          多银行服务·专业理财·信用管理                                     ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

💰 您的财务状况:
  现金余额: J${user_data.get('cash', 0):,.2f}
  信用等级: {self.credit_manager.get_credit_rating(user_data)}
  总资产: J${user_data.get('cash', 0) + self._calculate_portfolio_value(user_data):,.2f}

🏦 可用银行服务:

"""
        
        # 显示所有银行
        for bank_id, bank in self.banks.items():
            unlocked, unlock_msg = self.check_bank_unlock(user_data, bank_id)
            
            if unlocked:
                relationship = self.get_bank_relationship(user_id, bank_id)
                status = relationship.get_status_display()
                
                menu_text += f"""
├─ {bank.logo} {bank.name}
│  └─ 等级: {status['level_name']} (Lv.{status['level']})
│  └─ 信任度: {status['trust_score']:.1f}% ({status['trust_level']})
│  └─ 贷款利率: {(bank.current_loan_rate - status['rate_discount'])*100:.2f}%
│  └─ 存款利率: {(bank.current_deposit_rate + status['rate_discount']*0.5)*100:.2f}%
│  └─ 专长: {', '.join(bank.specialties[:2])}
"""
            else:
                menu_text += f"""
├─ {bank.logo} {bank.name} 🔒
│  └─ 解锁条件: {unlock_msg}
│  └─ 解锁等级: Lv.{bank.unlock_level}
"""
        
        menu_text += f"""

🎯 银行操作:
  bank list                     - 查看所有银行详情
  bank select <银行ID>          - 选择银行进行操作
  bank tasks                    - 查看银行任务
  bank relationship             - 查看银行关系
  bank rates                    - 查看利率表

📊 快速服务:
  bank loan <金额> [银行ID]      - 申请贷款
  bank deposit <金额> [银行ID]   - 进行存款
  bank credit                   - 查看信用报告

💡 银行系统特色:
  • 不同银行有不同专长和利率
  • 完成银行任务提升关系等级
  • 信用等级影响贷款额度和利率
  • 高等级客户享受专属服务
"""
        
        return menu_text
        
    def show_bank_list(self):
        """显示银行列表详情"""
        user_data = self.main_app.user_data or {}
        user_id = self.main_app.user_manager.current_user
        
        list_text = f"""
🏦 JackyCoin 银行系统 - 银行列表

"""
        
        for category in BankCategory:
            category_banks = [bank for bank in self.banks.values() if bank.category == category]
            if not category_banks:
                continue
                
            category_names = {
                BankCategory.CENTRAL: "🏛️ 中央银行",
                BankCategory.COMMERCIAL: "🏦 商业银行", 
                BankCategory.INVESTMENT: "📈 投资银行",
                BankCategory.TRADING: "⚡ 交易银行",
                BankCategory.CRYPTO: "🪙 数字银行",
                BankCategory.WEALTH: "💎 私人银行"
            }
            
            list_text += f"\n{category_names[category]}:\n" + "─" * 80 + "\n"
            
            for bank in category_banks:
                unlocked, unlock_msg = self.check_bank_unlock(user_data, bank.bank_id)
                
                list_text += f"\n{bank.logo} {bank.name} ({'✅' if unlocked else '🔒'})\n"
                list_text += f"   描述: {bank.description}\n"
                list_text += f"   贷款利率: {bank.base_loan_rate*100:.2f}% | 存款利率: {bank.base_deposit_rate*100:.2f}%\n"
                list_text += f"   最大贷款倍数: {bank.max_loan_multiplier}x\n"
                list_text += f"   专长: {', '.join(bank.specialties)}\n"
                
                if unlocked:
                    relationship = self.get_bank_relationship(user_id, bank.bank_id)
                    status = relationship.get_status_display()
                    list_text += f"   您的等级: {status['level_name']} | 信任度: {status['trust_score']:.1f}%\n"
                else:
                    list_text += f"   解锁要求: 等级{bank.unlock_level} | {unlock_msg}\n"
                
                list_text += "\n"
                
        list_text += f"""
🎮 银行操作指南:
  bank select <银行ID>    - 选择特定银行进行详细操作
  bank tasks <银行ID>     - 查看特定银行的任务
  bank loan <金额> <银行ID> - 在指定银行申请贷款

💡 提示: 不同银行有不同的利率和服务，选择最适合您需求的银行！
"""
        
        return list_text
        
    def select_bank(self, bank_id):
        """选择银行进行操作"""
        if bank_id not in self.banks:
            return f"❌ 银行 {bank_id} 不存在\n\n可用银行: {', '.join(self.banks.keys())}"
            
        user_data = self.main_app.user_data or {}
        unlocked, unlock_msg = self.check_bank_unlock(user_data, bank_id)
        
        if not unlocked:
            return f"❌ 银行未解锁: {unlock_msg}"
            
        bank = self.banks[bank_id]
        user_id = self.main_app.user_manager.current_user
        relationship = self.get_bank_relationship(user_id, bank_id)
        status = relationship.get_status_display()
        
        # 获取该银行的可用任务
        available_tasks = self.task_manager.get_available_tasks(user_data, bank_id)
        active_tasks = [t for t in self.task_manager.get_active_tasks(user_id) if t.bank_id == bank_id]
        
        bank_detail = f"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                        {bank.logo} {bank.name} - 银行服务中心                           
╚══════════════════════════════════════════════════════════════════════════════════════════╝

🏦 银行信息:
  类别: {bank.category.value.title()}
  描述: {bank.description}
  专长服务: {', '.join(bank.specialties)}

💰 当前利率:
  贷款利率: {(bank.current_loan_rate - status['rate_discount'])*100:.3f}% 
  存款利率: {(bank.current_deposit_rate + status['rate_discount']*0.5)*100:.3f}%
  最大贷款倍数: {bank.max_loan_multiplier * status['loan_bonus']:.1f}x

👤 您的客户信息:
  等级: {status['level_name']} (Lv.{status['level']})
  信任度: {status['trust_score']:.1f}% ({status['trust_level']})
  累计业务: J${status['total_business']:,.2f}
  利率折扣: {status['rate_discount']*100:.2f}%
  额度加成: {(status['loan_bonus']-1)*100:.1f}%

📋 银行任务:
  可接受任务: {len(available_tasks)}个
  进行中任务: {len(active_tasks)}个

🎯 银行服务:
  bank loan <金额> {bank_id}        - 申请贷款
  bank deposit <金额> {bank_id}     - 进行存款  
  bank tasks {bank_id}              - 查看银行任务
  bank repay <贷款ID>               - 偿还贷款
  bank withdraw <存款ID>            - 提取存款

💡 关系提升建议:
  • 按时偿还贷款可提升信任度
  • 完成银行任务获得关系积分
  • 大额存款业务提升业务量
  • 推荐新客户获得额外奖励
"""
        
        return bank_detail
        
    def show_bank_tasks(self, bank_id=None):
        """显示银行任务"""
        user_data = self.main_app.user_data or {}
        user_id = self.main_app.user_manager.current_user
        
        if bank_id:
            if bank_id not in self.banks:
                return f"❌ 银行 {bank_id} 不存在"
                
            unlocked, unlock_msg = self.check_bank_unlock(user_data, bank_id)
            if not unlocked:
                return f"❌ 银行未解锁: {unlock_msg}"
                
            available_tasks = self.task_manager.get_available_tasks(user_data, bank_id)
            active_tasks = [t for t in self.task_manager.get_active_tasks(user_id) if t.bank_id == bank_id]
            bank_name = self.banks[bank_id].name
            
        else:
            available_tasks = self.task_manager.get_available_tasks(user_data)
            active_tasks = self.task_manager.get_active_tasks(user_id)
            bank_name = "所有银行"
            
        tasks_text = f"""
📋 {bank_name} - 银行任务中心

🔄 进行中的任务 ({len(active_tasks)}个):
"""
        
        if active_tasks:
            for task in active_tasks:
                bank = self.banks[task.bank_id]
                progress = task._calculate_overall_progress()
                deadline_str = task.deadline.strftime("%Y-%m-%d") if task.deadline else "无期限"
                
                tasks_text += f"""
├─ {bank.logo} {task.title} [{task.difficulty.value.title()}]
│  └─ 银行: {bank.name}
│  └─ 进度: {progress*100:.1f}% {'🟢' if progress > 0.7 else '🟡' if progress > 0.3 else '🔴'}
│  └─ 截止: {deadline_str}
│  └─ 奖励: J${task.reward.cash_bonus:,.0f} + {task.reward.relationship_points}关系积分
"""
        else:
            tasks_text += "\n  暂无进行中的任务\n"
            
        tasks_text += f"\n📥 可接受的任务 ({len(available_tasks)}个):\n"
        
        if available_tasks:
            for task in available_tasks[:10]:  # 显示前10个
                bank = self.banks[task.bank_id]
                difficulty_emojis = {
                    'easy': '🟢', 'medium': '🟡', 'hard': '🟠', 'expert': '🔴'
                }
                
                tasks_text += f"""
├─ {bank.logo} {task.title} {difficulty_emojis[task.difficulty.value]}
│  └─ 银行: {bank.name}
│  └─ 类型: {task.task_type.value.title()}
│  └─ 要求: {task.description}
│  └─ 奖励: J${task.reward.cash_bonus:,.0f}"""
                
                if task.reward.special_privileges:
                    tasks_text += f" + 特权: {', '.join(task.reward.special_privileges[:2])}"
                tasks_text += "\n"
                
            if len(available_tasks) > 10:
                tasks_text += f"\n  ... 还有 {len(available_tasks) - 10} 个任务\n"
        else:
            tasks_text += "\n  暂无可接受的任务，提升等级或完成解锁条件后可获得更多任务\n"
            
        tasks_text += f"""

🎮 任务操作:
  bank accept <任务ID>     - 接受任务
  bank progress            - 查看任务进度详情
  bank complete <任务ID>   - 完成任务(自动检测)

💡 任务提示:
  • 不同银行有不同类型的任务
  • 完成任务可提升银行关系等级
  • 高难度任务奖励更丰厚
  • 部分任务可重复完成
"""
        
        return tasks_text
        
    def apply_loan(self, amount, bank_id="JC_COMMERCIAL"):
        """申请贷款"""
        try:
            amount = float(amount)
            if amount <= 0:
                return "❌ 贷款金额必须大于0"
        except ValueError:
            return "❌ 无效的贷款金额"
            
        user_data = self.main_app.user_data or {}
        unlocked, unlock_msg = self.check_bank_unlock(user_data, bank_id)
        
        if not unlocked:
            return f"❌ 银行未解锁: {unlock_msg}"
            
        # 获取银行和用户关系
        bank = self.banks[bank_id]
        user_id = self.main_app.user_manager.current_user
        relationship = self.get_bank_relationship(user_id, bank_id)
        
        # 计算最大贷款额度
        base_limit = user_data.get('cash', 0) * bank.max_loan_multiplier
        final_limit = base_limit * relationship.get_loan_limit_bonus()
        
        if amount > final_limit:
            return f"❌ 贷款金额超过限额 J${final_limit:,.2f}"
            
        # 计算利率
        base_rate = bank.current_loan_rate
        final_rate = base_rate - relationship.get_rate_discount()
        
        # 创建贷款
        loan_id = f"{bank_id}_{len(user_data.get('bank_data', {}).get('loans', [])) + 1:06d}"
        loan = {
            'id': loan_id,
            'bank_id': bank_id,
            'amount': amount,
            'interest_rate': final_rate,
            'issue_date': datetime.now().isoformat(),
            'due_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'status': 'active',
            'monthly_payment': amount * (final_rate / 12 + 1 / 30)  # 简化计算
        }
        
        # 保存贷款记录
        if 'bank_data' not in user_data:
            user_data['bank_data'] = {}
        if 'loans' not in user_data['bank_data']:
            user_data['bank_data']['loans'] = []
            
        user_data['bank_data']['loans'].append(loan)
        
        # 增加现金
        self.main_app.cash += amount
        user_data['cash'] = self.main_app.cash
        
        # 更新银行关系
        relationship.update_relationship(amount, 'loan_taken')
        
        return f"""
✅ 贷款申请成功！

💰 贷款详情:
  贷款编号: {loan_id}
  贷款银行: {bank.name}
  贷款金额: J${amount:,.2f}
  年利率: {final_rate*100:.3f}%
  月还款: J${loan['monthly_payment']:,.2f}
  到期日期: {loan['due_date'][:10]}

💳 账户变动:
  贷款金额: +J${amount:,.2f}
  当前余额: J${self.main_app.cash:,.2f}

📊 客户状态:
  银行等级: {relationship.get_status_display()['level_name']}
  信任度: {relationship.trust_score:.1f}%

💡 提示: 按时还款可提升您在 {bank.name} 的信用等级
"""
        
    def apply_deposit(self, amount, term_type='demand', bank_id="JC_COMMERCIAL"):
        """申请存款"""
        try:
            amount = float(amount)
            if amount <= 0:
                return "❌ 存款金额必须大于0"
        except ValueError:
            return "❌ 无效的存款金额"
            
        if amount > self.main_app.cash:
            return f"❌ 资金不足，您只有 J${self.main_app.cash:,.2f}"
            
        user_data = self.main_app.user_data or {}
        unlocked, unlock_msg = self.check_bank_unlock(user_data, bank_id)
        
        if not unlocked:
            return f"❌ 银行未解锁: {unlock_msg}"
            
        # 获取银行和用户关系
        bank = self.banks[bank_id]
        user_id = self.main_app.user_manager.current_user
        relationship = self.get_bank_relationship(user_id, bank_id)
        
        # 计算利率和期限
        base_rate = bank.current_deposit_rate
        rate_bonus = relationship.get_rate_discount()  # 存款时是加成
        final_rate = base_rate + rate_bonus
        
        term_config = {
            'demand': {'days': 0, 'rate_bonus': 1.0, 'name': '活期'},
            'short': {'days': 90, 'rate_bonus': 1.2, 'name': '短期(90天)'},
            'medium': {'days': 180, 'rate_bonus': 1.5, 'name': '中期(180天)'},
            'long': {'days': 365, 'rate_bonus': 2.0, 'name': '长期(365天)'}
        }
        
        if term_type not in term_config:
            return "❌ 无效的存款期限类型"
            
        term_info = term_config[term_type]
        final_rate *= term_info['rate_bonus']
        
        # 创建存款记录
        deposit_id = f"{bank_id}_D_{len(user_data.get('bank_data', {}).get('deposits', [])) + 1:06d}"
        deposit = {
            'id': deposit_id,
            'bank_id': bank_id,
            'amount': amount,
            'interest_rate': final_rate,
            'term_type': term_type,
            'issue_date': datetime.now().isoformat(),
            'maturity_date': (datetime.now() + timedelta(days=term_info['days'])).isoformat() if term_info['days'] > 0 else None,
            'status': 'active'
        }
        
        # 保存存款记录
        if 'bank_data' not in user_data:
            user_data['bank_data'] = {}
        if 'deposits' not in user_data['bank_data']:
            user_data['bank_data']['deposits'] = []
            
        user_data['bank_data']['deposits'].append(deposit)
        
        # 扣除现金
        self.main_app.cash -= amount
        user_data['cash'] = self.main_app.cash
        
        # 更新银行关系
        relationship.update_relationship(amount, 'deposit_made')
        
        return f"""
✅ 存款成功！

💰 存款详情:
  存款编号: {deposit_id}
  存款银行: {bank.name}
  存款金额: J${amount:,.2f}
  年利率: {final_rate*100:.3f}%
  存款期限: {term_info['name']}
  到期日期: {deposit['maturity_date'][:10] if deposit['maturity_date'] else '无期限'}

💳 账户变动:
  存款金额: -J${amount:,.2f}
  当前余额: J${self.main_app.cash:,.2f}

📊 预期收益:
  年化收益: J${amount * final_rate:,.2f}
  {'期满收益: J$' + str(amount * final_rate * term_info['days'] / 365) + f' ({term_info["days"]}天)' if term_info['days'] > 0 else '按日计息'}

💡 提示: 存款可提升您在 {bank.name} 的客户等级
"""

    def repay_loan(self, loan_id):
        """偿还贷款"""
        user_data = self.main_app.user_data or {}
        bank_data = user_data.get('bank_data', {})
        loans = bank_data.get('loans', [])
        
        # 查找贷款
        loan = None
        for l in loans:
            if l['id'] == loan_id and l['status'] == 'active':
                loan = l
                break
                
        if not loan:
            return f"❌ 未找到ID为 {loan_id} 的活跃贷款"
            
        # 计算应还金额
        principal = loan['amount']
        interest_rate = loan['interest_rate']
        issue_date = datetime.fromisoformat(loan['issue_date'])
        days_elapsed = (datetime.now() - issue_date).days
        interest = principal * interest_rate * days_elapsed / 365
        total_repayment = principal + interest
        
        if self.main_app.cash < total_repayment:
            return f"❌ 资金不足，需要 J${total_repayment:,.2f}，您只有 J${self.main_app.cash:,.2f}"
            
        # 执行还款
        self.main_app.cash -= total_repayment
        user_data['cash'] = self.main_app.cash
        loan['status'] = 'repaid'
        loan['repaid_date'] = datetime.now().isoformat()
        loan['repaid_amount'] = total_repayment
        
        # 更新银行关系
        bank_id = loan['bank_id']
        user_id = self.main_app.user_manager.current_user
        relationship = self.get_bank_relationship(user_id, bank_id)
        relationship.update_relationship(total_repayment, 'loan_repaid')
        
        bank = self.banks[bank_id]
        
        return f"""
✅ 贷款还款成功！

💰 还款详情:
  贷款编号: {loan_id}
  还款银行: {bank.name}
  本金: J${principal:,.2f}
  利息: J${interest:,.2f}
  总还款: J${total_repayment:,.2f}
  借款天数: {days_elapsed}天

💳 账户变动:
  还款金额: -J${total_repayment:,.2f}
  当前余额: J${self.main_app.cash:,.2f}

📊 信用提升:
  按时还款记录已更新
  银行关系等级可能提升

💡 提示: 良好的还款记录有助于获得更低利率
"""

    def withdraw_deposit(self, deposit_id):
        """提取存款"""
        user_data = self.main_app.user_data or {}
        bank_data = user_data.get('bank_data', {})
        deposits = bank_data.get('deposits', [])
        
        # 查找存款
        deposit = None
        for d in deposits:
            if d['id'] == deposit_id and d['status'] == 'active':
                deposit = d
                break
                
        if not deposit:
            return f"❌ 未找到ID为 {deposit_id} 的活跃存款"
            
        # 检查是否可以提取
        issue_date = datetime.fromisoformat(deposit['issue_date'])
        days_elapsed = (datetime.now() - issue_date).days
        
        is_early_withdrawal = False
        penalty = 0.0
        
        if deposit['maturity_date']:
            maturity_date = datetime.fromisoformat(deposit['maturity_date'])
            if datetime.now() < maturity_date:
                is_early_withdrawal = True
                penalty = deposit['amount'] * 0.01  # 1%提前支取罚金
                
        # 计算利息
        principal = deposit['amount']
        interest_rate = deposit['interest_rate']
        interest = principal * interest_rate * days_elapsed / 365
        
        if is_early_withdrawal:
            interest *= 0.5  # 提前支取利息减半
            
        total_withdrawal = principal + interest - penalty
        
        # 执行提取
        self.main_app.cash += total_withdrawal
        user_data['cash'] = self.main_app.cash
        deposit['status'] = 'withdrawn'
        deposit['withdrawal_date'] = datetime.now().isoformat()
        deposit['withdrawal_amount'] = total_withdrawal
        
        bank_id = deposit['bank_id']
        bank = self.banks[bank_id]
        
        return f"""
✅ 存款提取成功！

💰 提取详情:
  存款编号: {deposit_id}
  存款银行: {bank.name}
  本金: J${principal:,.2f}
  利息: J${interest:,.2f}
  {'提前支取罚金: -J$' + f'{penalty:,.2f}' if penalty > 0 else ''}
  实际到账: J${total_withdrawal:,.2f}
  存款天数: {days_elapsed}天

💳 账户变动:
  提取金额: +J${total_withdrawal:,.2f}
  当前余额: J${self.main_app.cash:,.2f}

{'⚠️ 提前支取: 利息减半并收取1%罚金' if is_early_withdrawal else '🎉 到期支取: 获得全额利息'}

💡 提示: 长期存款可获得更高利率
"""

    def show_account_summary(self, bank_id=None):
        """显示账户摘要"""
        user_data = self.main_app.user_data or {}
        bank_data = user_data.get('bank_data', {})
        user_id = self.main_app.user_manager.current_user
        
        if bank_id:
            # 显示特定银行的账户信息
            bank = self.banks.get(bank_id)
            if not bank:
                return "❌ 银行不存在"
                
            relationship = self.get_bank_relationship(user_id, bank_id)
            status = relationship.get_status_display()
            
            # 筛选该银行的贷款和存款
            bank_loans = [l for l in bank_data.get('loans', []) if l['bank_id'] == bank_id and l['status'] == 'active']
            bank_deposits = [d for d in bank_data.get('deposits', []) if d['bank_id'] == bank_id and d['status'] == 'active']
            
            total_loan_amount = sum(l['amount'] for l in bank_loans)
            total_deposit_amount = sum(d['amount'] for d in bank_deposits)
            
            return f"""
🏦 {bank.logo} {bank.name} - 账户详情

👤 客户信息:
  客户等级: {status['level_name']} ({relationship.relationship_level}/10)
  信任度: {relationship.trust_score:.1f}%
  累计业务: J${relationship.total_business:,.2f}
  特殊权限: {len(relationship.special_privileges)}项

💰 资产负债:
  活跃贷款: {len(bank_loans)}笔 (J${total_loan_amount:,.2f})
  活跃存款: {len(bank_deposits)}笔 (J${total_deposit_amount:,.2f})
  净资产: J${total_deposit_amount - total_loan_amount:,.2f}

📊 利率优惠:
  贷款利率折扣: {relationship.get_rate_discount()*100:.2f}%
  存款利率加成: {relationship.get_rate_discount()*100:.2f}%
  贷款额度加成: {(relationship.get_loan_limit_bonus()-1)*100:.1f}%

🎯 服务特色:
"""
            for specialty in bank.specialties:
                return f"  • {specialty}\n"
                
            return """
🎮 可用操作:
  bank loan <金额>           - 申请贷款
  bank deposit <金额> <期限> - 申请存款
  bank tasks                - 查看银行任务
"""
        else:
            # 显示所有银行的概览
            credit_rating = self.credit_manager.get_credit_rating(user_data)
            all_loans = bank_data.get('loans', [])
            all_deposits = bank_data.get('deposits', [])
            
            active_loans = [l for l in all_loans if l['status'] == 'active']
            active_deposits = [d for d in all_deposits if d['status'] == 'active']
            
            total_loan_amount = sum(l['amount'] for l in active_loans)
            total_deposit_amount = sum(d['amount'] for d in active_deposits)
            
            return f"""
🏦 银行系统 - 账户总览

📊 信用状况:
  信用评级: {credit_rating.value}
  综合评分: {self.credit_manager.calculate_credit_score(user_data):.0f}/100

💰 资产负债概览:
  现金余额: J${self.main_app.cash:,.2f}
  银行存款: J${total_deposit_amount:,.2f}
  未偿贷款: J${total_loan_amount:,.2f}
  净银行资产: J${total_deposit_amount - total_loan_amount:,.2f}

🏛️ 银行关系:
"""
            for bank_id, bank in self.banks.items():
                unlocked, _ = self.check_bank_unlock(user_data, bank_id)
                if unlocked:
                    relationship = self.get_bank_relationship(user_id, bank_id)
                    bank_loans = len([l for l in active_loans if l['bank_id'] == bank_id])
                    bank_deposits = len([d for d in active_deposits if d['bank_id'] == bank_id])
                    
                    return f"""  {bank.logo} {bank.name}: 等级{relationship.relationship_level} | 贷款{bank_loans}笔 | 存款{bank_deposits}笔
"""
                else:
                    return f"  {bank.logo} {bank.name}: 🔒 未解锁\n"

    def save_bank_data(self):
        """保存银行数据"""
        try:
            os.makedirs('data', exist_ok=True)
            
            # 保存用户银行关系数据
            relationships_data = {}
            for user_id, user_relationships in self.user_relationships.items():
                relationships_data[user_id] = {}
                for bank_id, relationship in user_relationships.items():
                    relationships_data[user_id][bank_id] = {
                        'relationship_level': relationship.relationship_level,
                        'trust_score': relationship.trust_score,
                        'total_business': relationship.total_business,
                        'special_privileges': relationship.special_privileges
                    }
                    
            with open('data/bank_relationships.json', 'w', encoding='utf-8') as f:
                json.dump(relationships_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存银行数据失败: {e}")
            
    def load_bank_data(self):
        """加载银行数据"""
        try:
            if os.path.exists('data/bank_relationships.json'):
                with open('data/bank_relationships.json', 'r', encoding='utf-8') as f:
                    relationships_data = json.load(f)
                
                # 恢复用户银行关系
                for user_id, user_relationships in relationships_data.items():
                    if user_id not in self.user_relationships:
                        self.user_relationships[user_id] = {}
                        
                    for bank_id, rel_data in user_relationships.items():
                        if bank_id in self.banks:
                            relationship = BankRelationship(bank_id, {})
                            relationship.relationship_level = rel_data['relationship_level']
                            relationship.trust_score = rel_data['trust_score']
                            relationship.total_business = rel_data['total_business']
                            relationship.special_privileges = rel_data['special_privileges']
                            self.user_relationships[user_id][bank_id] = relationship
                            
        except Exception as e:
            print(f"加载银行数据失败: {e}") 