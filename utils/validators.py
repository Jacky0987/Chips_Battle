from typing import Any, Optional, Union, List, Dict
from decimal import Decimal, InvalidOperation
import re
from datetime import datetime


def validate_amount(amount: Any, min_value: Optional[Decimal] = None, 
                   max_value: Optional[Decimal] = None) -> tuple[bool, str, Optional[Decimal]]:
    """验证金额
    
    Args:
        amount: 待验证的金额
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        (是否有效, 错误信息, 转换后的金额)
    """
    try:
        # 转换为Decimal
        if isinstance(amount, str):
            # 移除货币符号和空格
            cleaned = re.sub(r'[^\d.-]', '', amount)
            decimal_amount = Decimal(cleaned)
        elif isinstance(amount, (int, float)):
            decimal_amount = Decimal(str(amount))
        elif isinstance(amount, Decimal):
            decimal_amount = amount
        else:
            return False, "无效的金额格式", None
        
        # 检查是否为有限数
        if not decimal_amount.is_finite():
            return False, "金额不能为无穷大或NaN", None
        
        # 检查最小值
        if min_value is not None and decimal_amount < min_value:
            return False, f"金额不能小于 {min_value}", None
        
        # 检查最大值
        if max_value is not None and decimal_amount > max_value:
            return False, f"金额不能大于 {max_value}", None
        
        return True, "", decimal_amount
        
    except (InvalidOperation, ValueError, TypeError):
        return False, "无效的金额格式", None


def validate_positive_amount(amount: Any) -> tuple[bool, str, Optional[Decimal]]:
    """验证正数金额
    
    Args:
        amount: 待验证的金额
        
    Returns:
        (是否有效, 错误信息, 转换后的金额)
    """
    return validate_amount(amount, min_value=Decimal('0.01'))


def validate_non_negative_amount(amount: Any) -> tuple[bool, str, Optional[Decimal]]:
    """验证非负金额
    
    Args:
        amount: 待验证的金额
        
    Returns:
        (是否有效, 错误信息, 转换后的金额)
    """
    return validate_amount(amount, min_value=Decimal('0'))


def validate_positive_integer(value: Any, min_value: int = 1, 
                            max_value: Optional[int] = None) -> tuple[bool, str, Optional[int]]:
    """验证正整数
    
    Args:
        value: 待验证的值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        (是否有效, 错误信息, 转换后的整数)
    """
    try:
        if isinstance(value, str):
            int_value = int(value)
        elif isinstance(value, (int, float)):
            int_value = int(value)
        else:
            return False, "无效的整数格式", None
        
        if int_value < min_value:
            return False, f"值不能小于 {min_value}", None
        
        if max_value is not None and int_value > max_value:
            return False, f"值不能大于 {max_value}", None
        
        return True, "", int_value
        
    except (ValueError, TypeError):
        return False, "无效的整数格式", None


def validate_percentage(value: Any, min_value: float = 0.0, 
                       max_value: float = 1.0) -> tuple[bool, str, Optional[float]]:
    """验证百分比 (0.0 - 1.0)
    
    Args:
        value: 待验证的值
        min_value: 最小值
        max_value: 最大值
        
    Returns:
        (是否有效, 错误信息, 转换后的浮点数)
    """
    try:
        if isinstance(value, str):
            # 处理百分比格式 (如 "50%")
            if value.endswith('%'):
                float_value = float(value[:-1]) / 100
            else:
                float_value = float(value)
        elif isinstance(value, (int, float, Decimal)):
            float_value = float(value)
        else:
            return False, "无效的百分比格式", None
        
        if float_value < min_value:
            return False, f"百分比不能小于 {min_value * 100}%", None
        
        if float_value > max_value:
            return False, f"百分比不能大于 {max_value * 100}%", None
        
        return True, "", float_value
        
    except (ValueError, TypeError):
        return False, "无效的百分比格式", None


def validate_email(email: str) -> tuple[bool, str]:
    """验证邮箱地址
    
    Args:
        email: 邮箱地址
        
    Returns:
        (是否有效, 错误信息)
    """
    if not email or not isinstance(email, str):
        return False, "邮箱地址不能为空"
    
    # 简单的邮箱验证正则
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "无效的邮箱地址格式"
    
    if len(email) > 254:
        return False, "邮箱地址过长"
    
    return True, ""


def validate_phone(phone: str) -> tuple[bool, str]:
    """验证手机号码
    
    Args:
        phone: 手机号码
        
    Returns:
        (是否有效, 错误信息)
    """
    if not phone or not isinstance(phone, str):
        return False, "手机号码不能为空"
    
    # 移除所有非数字字符
    digits_only = re.sub(r'\D', '', phone)
    
    # 中国手机号验证 (11位，以1开头)
    if len(digits_only) == 11 and digits_only.startswith('1'):
        return True, ""
    
    # 国际号码验证 (7-15位)
    if 7 <= len(digits_only) <= 15:
        return True, ""
    
    return False, "无效的手机号码格式"


def validate_id_card(id_card: str) -> tuple[bool, str]:
    """验证身份证号码
    
    Args:
        id_card: 身份证号码
        
    Returns:
        (是否有效, 错误信息)
    """
    if not id_card or not isinstance(id_card, str):
        return False, "身份证号码不能为空"
    
    # 移除空格
    id_card = id_card.replace(' ', '')
    
    # 18位身份证验证
    if len(id_card) == 18:
        # 前17位必须是数字
        if not id_card[:17].isdigit():
            return False, "身份证号码格式错误"
        
        # 最后一位可以是数字或X
        if not (id_card[17].isdigit() or id_card[17].upper() == 'X'):
            return False, "身份证号码格式错误"
        
        return True, ""
    
    # 15位身份证验证
    elif len(id_card) == 15:
        if not id_card.isdigit():
            return False, "身份证号码格式错误"
        
        return True, ""
    
    else:
        return False, "身份证号码长度错误"


def validate_bank_card(card_number: str) -> tuple[bool, str]:
    """验证银行卡号
    
    Args:
        card_number: 银行卡号
        
    Returns:
        (是否有效, 错误信息)
    """
    if not card_number or not isinstance(card_number, str):
        return False, "银行卡号不能为空"
    
    # 移除空格和连字符
    cleaned = re.sub(r'[\s-]', '', card_number)
    
    # 检查是否全为数字
    if not cleaned.isdigit():
        return False, "银行卡号只能包含数字"
    
    # 检查长度 (通常为13-19位)
    if not (13 <= len(cleaned) <= 19):
        return False, "银行卡号长度错误"
    
    # Luhn算法验证
    def luhn_check(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10 == 0
    
    if not luhn_check(cleaned):
        return False, "银行卡号校验失败"
    
    return True, ""


def validate_password_strength(password: str) -> tuple[bool, str, int]:
    """验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        (是否有效, 错误信息, 强度分数 0-100)
    """
    if not password or not isinstance(password, str):
        return False, "密码不能为空", 0
    
    score = 0
    issues = []
    
    # 长度检查
    if len(password) < 6:
        issues.append("密码长度至少6位")
    elif len(password) >= 8:
        score += 25
    else:
        score += 15
    
    # 包含小写字母
    if re.search(r'[a-z]', password):
        score += 15
    else:
        issues.append("应包含小写字母")
    
    # 包含大写字母
    if re.search(r'[A-Z]', password):
        score += 15
    else:
        issues.append("应包含大写字母")
    
    # 包含数字
    if re.search(r'\d', password):
        score += 15
    else:
        issues.append("应包含数字")
    
    # 包含特殊字符
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 15
    else:
        issues.append("应包含特殊字符")
    
    # 长度奖励
    if len(password) >= 12:
        score += 15
    
    # 检查常见弱密码
    weak_passwords = [
        '123456', 'password', '123456789', '12345678', '12345',
        '1234567', '1234567890', 'qwerty', 'abc123', 'password123'
    ]
    
    if password.lower() in weak_passwords:
        score = min(score, 20)
        issues.append("不能使用常见弱密码")
    
    # 检查重复字符
    if len(set(password)) < len(password) * 0.6:
        score -= 10
        issues.append("重复字符过多")
    
    score = max(0, min(100, score))
    
    if issues:
        return False, "; ".join(issues), score
    
    return True, "", score


def validate_date_range(start_date: datetime, end_date: datetime) -> tuple[bool, str]:
    """验证日期范围
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        (是否有效, 错误信息)
    """
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        return False, "无效的日期格式"
    
    if start_date >= end_date:
        return False, "开始日期必须早于结束日期"
    
    # 检查日期是否过于久远
    from core.game_time import GameTime
    now = GameTime.now() if GameTime.is_initialized() else datetime.now()
    if start_date > now:
        return False, "开始日期不能是未来时间"
    
    if end_date > now:
        return False, "结束日期不能是未来时间"
    
    return True, ""


def validate_json_data(data: Any, required_fields: List[str] = None) -> tuple[bool, str]:
    """验证JSON数据
    
    Args:
        data: JSON数据
        required_fields: 必需字段列表
        
    Returns:
        (是否有效, 错误信息)
    """
    if not isinstance(data, dict):
        return False, "数据必须是JSON对象"
    
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return False, f"缺少必需字段: {', '.join(missing_fields)}"
    
    return True, ""


def sanitize_input(text: str, max_length: int = 1000, 
                  allowed_chars: Optional[str] = None) -> str:
    """清理输入文本
    
    Args:
        text: 输入文本
        max_length: 最大长度
        allowed_chars: 允许的字符正则表达式
        
    Returns:
        清理后的文本
    """
    if not isinstance(text, str):
        return ""
    
    # 移除控制字符
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # 应用字符过滤
    if allowed_chars:
        cleaned = re.sub(f'[^{allowed_chars}]', '', cleaned)
    
    # 截断长度
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    # 移除首尾空白
    cleaned = cleaned.strip()
    
    return cleaned