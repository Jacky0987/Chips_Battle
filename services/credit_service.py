from typing import Dict, List, Optional, Tuple, Any
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy import and_, or_, func

from models.auth.user import User
from models.bank.credit_profile import CreditProfile, CreditRating
from models.bank.loan import Loan, LoanPayment
from models.bank.bank_account import BankAccount
from dal.unit_of_work import UnitOfWork


class CreditService:
    """信用服务类
    
    提供信用评估和管理功能，包括：
    - 信用分数计算
    - 信用档案管理
    - 信用历史跟踪
    - 贷款资格评估
    - 信用改进建议
    """
    
    def __init__(self, uow: UnitOfWork):
        self.uow = uow
    
    # ==================== 信用档案管理 ====================
    
    def get_or_create_credit_profile(self, user_id: str) -> CreditProfile:
        """获取或创建信用档案
        
        Args:
            user_id: 用户ID
            
        Returns:
            信用档案对象
        """
        return CreditProfile.get_or_create_profile(self.uow, user_id)
    
    async def update_credit_profile(self, user_id: str, **kwargs) -> Tuple[bool, str]:
        """更新信用档案
        
        Args:
            user_id: 用户ID
            **kwargs: 更新字段
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                credit_profile = self.get_or_create_credit_profile(user_id)
                
                # 更新字段
                for key, value in kwargs.items():
                    if hasattr(credit_profile, key):
                        setattr(credit_profile, key, value)
                
                credit_profile.last_updated = datetime.utcnow()
                
                # 重新计算信用分数
                credit_profile.calculate_credit_score()
                
                await self.uow.commit()
                
                return True, "信用档案更新成功"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"更新失败: {str(e)}"
    
    # ==================== 信用分数计算 ====================
    
    async def recalculate_credit_score(self, user_id: str) -> Tuple[bool, str, int]:
        """重新计算信用分数
        
        Args:
            user_id: 用户ID
            
        Returns:
            (是否成功, 消息, 新分数)
        """
        try:
            async with self.uow:
                credit_profile = self.get_or_create_credit_profile(user_id)
                
                # 更新相关数据
                await self._update_payment_history(user_id, credit_profile)
                await self._update_debt_info(user_id, credit_profile)
                await self._update_account_info(user_id, credit_profile)
                await self._update_loan_info(user_id, credit_profile)
                
                # 计算新分数
                old_score = credit_profile.credit_score
                new_score = credit_profile.calculate_credit_score()
                
                credit_profile.last_updated = datetime.utcnow()
                
                await self.uow.commit()
                
                score_change = new_score - old_score
                change_msg = f"(变化: {score_change:+d})" if score_change != 0 else ""
                
                return True, f"信用分数已更新为 {new_score} {change_msg}", new_score
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"计算失败: {str(e)}", 0
    
    async def _update_payment_history(self, user_id: str, credit_profile: CreditProfile):
        """更新支付历史
        
        Args:
            user_id: 用户ID
            credit_profile: 信用档案
        """
        try:
            async with self.uow:
                stmt = select(LoanPayment).join(Loan).where(Loan.user_id == user_id)
                result = await self.uow.session.execute(stmt)
                payments = result.scalars().all()
            
                if payments:
                    total_payments = len(payments)
                    on_time_payments = sum(1 for p in payments if not p.is_late)
                    
                    payment_history = {
                        'total_payments': total_payments,
                        'on_time_payments': on_time_payments,
                        'late_payments': total_payments - on_time_payments,
                        'on_time_rate': on_time_payments / total_payments if total_payments > 0 else 1.0,
                        'last_updated': datetime.utcnow().isoformat()
                    }
                    
                    credit_profile.update_payment_history(payment_history)
                
        except Exception:
            pass
    
    async def _update_debt_info(self, user_id: str, credit_profile: CreditProfile):
        """更新债务信息
        
        Args:
            user_id: 用户ID
            credit_profile: 信用档案
        """
        try:
            async with self.uow:
                stmt = select(Loan).where(Loan.user_id == user_id)
                result = await self.uow.session.execute(stmt)
                loans = result.scalars().all()
    
                stmt = select(BankAccount).where(and_(BankAccount.user_id == user_id, BankAccount.is_active == True))
                result = await self.uow.session.execute(stmt)
                accounts = result.scalars().all()
            
                if loans and accounts:
                    active_loans = [loan for loan in loans if loan.status == 'approved']
                    total_debt = sum(loan.remaining_balance for loan in active_loans)
                    total_credit_limit = sum(loan.principal_amount for loan in active_loans)
                    
                    total_assets = sum(account.balance for account in accounts)
                    
                    debt_info = {
                        'total_debt': float(total_debt),
                        'total_credit_limit': float(total_credit_limit),
                        'credit_utilization': float(total_debt / total_credit_limit) if total_credit_limit > 0 else 0,
                        'debt_to_income_ratio': 0,  # 需要收入信息
                        'debt_to_asset_ratio': float(total_debt / total_assets) if total_assets > 0 else 0,
                        'number_of_debts': len(active_loans)
                    }
                    
                    credit_profile.update_debt_info(debt_info)
                    
        except Exception:
            pass
    
    async def _update_account_info(self, user_id: str, credit_profile: CreditProfile):
        """更新账户信息
        
        Args:
            user_id: 用户ID
            credit_profile: 信用档案
        """
        try:
            async with self.uow:
                stmt = select(BankAccount).where(BankAccount.user_id == user_id)
                result = await self.uow.session.execute(stmt)
                accounts = result.scalars().all()
    
                if accounts:
                    oldest_account = min(accounts, key=lambda a: a.created_at)
                    account_age_months = (datetime.utcnow() - oldest_account.created_at).days // 30
                    
                    account_info = {
                        'total_accounts': len(accounts),
                        'active_accounts': len([a for a in accounts if a.is_enabled]),
                        'oldest_account_age_months': account_age_months,
                        'average_account_balance': float(sum(a.balance for a in accounts) / len(accounts)),
                        'total_balance': float(sum(a.balance for a in accounts))
                    }
                    
                    credit_profile.update_account_info(account_info)
                
        except Exception:
            pass
    
    async def _update_loan_info(self, user_id: str, credit_profile: CreditProfile):
        """更新贷款信息
        
        Args:
            user_id: 用户ID
            credit_profile: 信用档案
        """
        try:
            async with self.uow:
                stmt = select(Loan).where(Loan.user_id == user_id)
                result = await self.uow.session.execute(stmt)
                all_loans = result.scalars().all()
            
            active_loans = [loan for loan in all_loans if loan.status == 'approved']
            completed_loans = [loan for loan in all_loans if loan.status == 'completed']
            
            loan_info = {
                'total_loans': len(all_loans),
                'active_loans': len(active_loans),
                'completed_loans': len(completed_loans),
                'total_borrowed': float(sum(loan.principal_amount for loan in all_loans)),
                'current_debt': float(sum(loan.remaining_balance for loan in active_loans)),
                'average_loan_amount': float(sum(loan.principal_amount for loan in all_loans) / len(all_loans)) if all_loans else 0
            }
            
            credit_profile.update_loan_info(loan_info)
            
        except Exception:
            pass
    
    # ==================== 信用查询记录 ====================
    
    async def add_credit_inquiry(self, user_id: str, inquiry_type: str, 
                               inquirer: str, purpose: str = None) -> Tuple[bool, str]:
        """添加信用查询记录
        
        Args:
            user_id: 用户ID
            inquiry_type: 查询类型 ('hard' 或 'soft')
            inquirer: 查询方
            purpose: 查询目的
            
        Returns:
            (是否成功, 消息)
        """
        try:
            async with self.uow:
                credit_profile = self.get_or_create_credit_profile(user_id)
                
                if inquiry_type == 'hard':
                    credit_profile.add_hard_inquiry(inquirer, purpose)
                else:
                    credit_profile.add_soft_inquiry(inquirer, purpose)
                
                await self.uow.commit()
                
                return True, f"已记录{inquiry_type}查询"
                
        except Exception as e:
            await self.uow.rollback()
            return False, f"记录失败: {str(e)}"
    
    # ==================== 贷款资格评估 ====================
    
    async def evaluate_loan_eligibility(self, user_id: str, loan_amount: Decimal, 
                                loan_type: str) -> Dict[str, Any]:
        """评估贷款资格
        
        Args:
            user_id: 用户ID
            loan_amount: 贷款金额
            loan_type: 贷款类型
            
        Returns:
            评估结果
        """
        try:
            async with self.uow:
                credit_profile = await self.get_or_create_credit_profile(user_id)
            
            # 计算批准概率
            approval_probability = credit_profile.calculate_loan_approval_probability(
                loan_amount, loan_type
            )
            
            # 建议利率
            suggested_rate = credit_profile.suggest_interest_rate(loan_type, loan_amount)
            
            # 获取贷款条件
            loan_terms = credit_profile.get_loan_terms(loan_type, loan_amount)
            
            # 评估等级
            if approval_probability >= 0.8:
                risk_level = "低风险"
                recommendation = "强烈推荐批准"
            elif approval_probability >= 0.6:
                risk_level = "中等风险"
                recommendation = "建议批准"
            elif approval_probability >= 0.4:
                risk_level = "较高风险"
                recommendation = "谨慎考虑"
            else:
                risk_level = "高风险"
                recommendation = "不建议批准"
            
            return {
                'user_id': user_id,
                'loan_amount': float(loan_amount),
                'loan_type': loan_type,
                'credit_score': credit_profile.credit_score,
                'credit_grade': credit_profile.credit_grade.value,
                'approval_probability': approval_probability,
                'suggested_interest_rate': suggested_rate,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'loan_terms': loan_terms,
                'evaluation_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'user_id': user_id,
                'error': f"评估失败: {str(e)}"
            }
    
    # ==================== 信用改进建议 ====================
    
    async def get_credit_improvement_suggestions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取信用改进建议
        
        Args:
            user_id: 用户ID
            
        Returns:
            改进建议列表
        """
        try:
            async with self.uow:
                credit_profile = await self.get_or_create_credit_profile(user_id)
                return credit_profile.get_credit_improvement_suggestions()
            
        except Exception:
            return []
    
    # ==================== 信用监控 ====================
    
    async def monitor_credit_changes(self, user_id: str) -> Dict[str, Any]:
        """监控信用变化
        
        Args:
            user_id: 用户ID
            
        Returns:
            信用变化报告
        """
        try:
            credit_profile = self.get_or_create_credit_profile(user_id)
            
            # 获取历史分数（简化实现，实际应该存储历史记录）
            old_score = credit_profile.credit_score
            
            # 重新计算当前分数
            success, message, new_score = await self.recalculate_credit_score(user_id)
            
            if not success:
                return {'error': message}
            
            score_change = new_score - old_score
            
            # 分析变化原因
            change_factors = []
            if score_change > 0:
                change_factors.append("信用状况改善")
            elif score_change < 0:
                change_factors.append("信用状况下降")
            else:
                change_factors.append("信用状况稳定")
            
            recommendations = await self.get_credit_improvement_suggestions(user_id)
            return {
                'user_id': user_id,
                'previous_score': old_score,
                'current_score': new_score,
                'score_change': score_change,
                'change_percentage': (score_change / old_score * 100) if old_score > 0 else 0,
                'change_factors': change_factors,
                'monitoring_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {'error': f"监控失败: {str(e)}"}
    
    # ==================== 信用报告 ====================
    
    async def generate_credit_report(self, user_id: str) -> Dict[str, Any]:
        """生成信用报告
        
        Args:
            user_id: 用户ID
            
        Returns:
            信用报告
        """
        try:
            async with self.uow:
                credit_profile = await self.get_or_create_credit_profile(user_id)
                
                # 获取用户基本信息
                stmt = select(User).filter_by(user_id=user_id)
                result = await self.uow.session.execute(stmt)
                user = result.scalars().first()
                
                # 获取账户信息
                stmt = select(BankAccount).where(BankAccount.user_id == user_id)
                result = await self.uow.session.execute(stmt)
                accounts = result.scalars().all()
                
                # 获取贷款信息
                stmt = select(Loan).where(Loan.user_id == user_id)
                result = await self.uow.session.execute(stmt)
                loans = result.scalars().all()
            
            # 获取最近的查询记录
            recent_inquiries = credit_profile.inquiry_history[-10:] if credit_profile.inquiry_history else []
            
            return {
                'report_id': f"CR_{user_id}_{datetime.utcnow().strftime('%Y%m%d')}",
                'user_info': {
                    'user_id': user_id,
                    'username': user.username if user else 'Unknown',
                    'account_age_days': (datetime.utcnow() - user.created_at).days if user else 0
                },
                'credit_summary': {
                    'credit_score': credit_profile.credit_score,
                    'credit_grade': credit_profile.credit_grade.value,
                    'score_range': f"{credit_profile.credit_score - 50} - {credit_profile.credit_score + 50}",
                    'last_updated': credit_profile.last_updated.strftime('%Y-%m-%d')
                },
                'account_summary': {
                    'total_accounts': len(accounts),
                    'active_accounts': len([a for a in accounts if a.is_enabled]),
                    'total_balance': float(sum(a.balance for a in accounts)),
                    'oldest_account_date': min(a.created_at for a in accounts).strftime('%Y-%m-%d') if accounts else None
                },
                'loan_summary': {
                    'total_loans': len(loans),
                    'active_loans': len([l for l in loans if l.status == 'approved']),
                    'total_debt': float(sum(l.remaining_balance for l in loans if l.status == 'approved')),
                    'total_borrowed': float(sum(l.principal_amount for l in loans))
                },
                'payment_history': credit_profile.payment_history or {},
                'debt_information': credit_profile.debt_info or {},
                'recent_inquiries': recent_inquiries,
                'negative_records': credit_profile.negative_records or [],
                'improvement_suggestions': await self.get_credit_improvement_suggestions(user_id),
                'report_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'user_id': user_id,
                'error': f"生成报告失败: {str(e)}"
            }
    
    # ==================== 批量处理 ====================
    
    async def batch_update_credit_scores(self, user_ids: List[str] = None) -> Dict[str, Any]:
        """批量更新信用分数
        
        Args:
            user_ids: 用户ID列表，为空时更新所有用户
            
        Returns:
            更新结果统计
        """
        try:
            if user_ids is None:
                async with self.uow:
                    # 获取所有有信用档案的用户
                    stmt = select(CreditProfile)
                    result = await self.uow.session.execute(stmt)
                    credit_profiles = result.scalars().all()
                    user_ids = [cp.user_id for cp in credit_profiles]
            
            success_count = 0
            error_count = 0
            errors = []
            
            for user_id in user_ids:
                try:
                    success, message, new_score = await self.recalculate_credit_score(user_id)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"{user_id}: {message}")
                except Exception as e:
                    error_count += 1
                    errors.append(f"{user_id}: {str(e)}")
            
            return {
                'total_processed': len(user_ids),
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10],  # 只返回前10个错误
                'processing_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'error': f"批量更新失败: {str(e)}"
            }
    
    # ==================== 统计分析 ====================
    
    async def get_credit_statistics(self) -> Dict[str, Any]:
        """获取信用统计信息
        
        Returns:
            统计信息
        """
        try:
            async with self.uow:
                # 获取所有信用档案
                stmt = select(CreditProfile)
                result = await self.uow.session.execute(stmt)
                credit_profiles = result.scalars().all()
            
            if not credit_profiles:
                return {'message': '暂无信用数据'}
            
            scores = [cp.credit_score for cp in credit_profiles]
            
            # 按等级分组
            grade_counts = {}
            for grade in CreditRating:
                grade_counts[grade.value] = len([
                    cp for cp in credit_profiles if cp.credit_rating == grade.value
                ])
            
            return {
                'total_profiles': len(credit_profiles),
                'average_score': sum(scores) / len(scores),
                'median_score': sorted(scores)[len(scores) // 2],
                'min_score': min(scores),
                'max_score': max(scores),
                'grade_distribution': grade_counts,
                'high_risk_count': len([cp for cp in credit_profiles if cp.credit_score < 600]),
                'excellent_count': len([cp for cp in credit_profiles if cp.credit_score >= 800]),
                'statistics_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'error': f"统计失败: {str(e)}"
            }