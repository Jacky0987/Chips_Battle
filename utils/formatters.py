from typing import Any, List, Dict, Optional
from decimal import Decimal
from datetime import datetime


def format_currency(amount: Decimal, currency_code: str = 'JCY') -> str:
    """格式化货币金额
    
    Args:
        amount: 金额
        currency_code: 货币代码
        
    Returns:
        格式化后的货币字符串
    """
    if currency_code == 'JCY':
        symbol = 'J$'
    elif currency_code == 'USD':
        symbol = '$'
    elif currency_code == 'CNY':
        symbol = '¥'
    elif currency_code == 'EUR':
        symbol = '€'
    elif currency_code == 'GBP':
        symbol = '£'
    elif currency_code == 'JPY':
        symbol = '¥'
    else:
        symbol = currency_code
    
    # 格式化数字，添加千位分隔符
    formatted_amount = f"{amount:,.2f}"
    
    return f"{symbol}{formatted_amount}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """格式化百分比
    
    Args:
        value: 数值 (0.1 = 10%)
        decimal_places: 小数位数
        
    Returns:
        格式化后的百分比字符串
    """
    return f"{value * 100:.{decimal_places}f}%"


def format_datetime(dt: datetime, format_type: str = 'default') -> str:
    """格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_type: 格式类型
        
    Returns:
        格式化后的日期时间字符串
    """
    if format_type == 'date':
        return dt.strftime('%Y-%m-%d')
    elif format_type == 'time':
        return dt.strftime('%H:%M:%S')
    elif format_type == 'short':
        return dt.strftime('%m/%d %H:%M')
    else:  # default
        return dt.strftime('%Y-%m-%d %H:%M:%S')


def format_table(headers: List[str], rows: List[List[Any]], 
                 max_width: int = 80) -> str:
    """格式化表格
    
    Args:
        headers: 表头列表
        rows: 数据行列表
        max_width: 最大宽度
        
    Returns:
        格式化后的表格字符串
    """
    if not headers or not rows:
        return ""
    
    # 计算每列的最大宽度
    col_widths = [len(str(header)) for header in headers]
    
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 调整列宽以适应最大宽度
    total_width = sum(col_widths) + len(headers) * 3 - 1
    if total_width > max_width:
        # 按比例缩减列宽
        scale = (max_width - len(headers) * 3 + 1) / sum(col_widths)
        col_widths = [max(8, int(w * scale)) for w in col_widths]
    
    # 构建表格
    result = []
    
    # 表头
    header_row = " | ".join(str(headers[i]).ljust(col_widths[i]) 
                           for i in range(len(headers)))
    result.append(header_row)
    
    # 分隔线
    separator = "-+-".join("-" * col_widths[i] for i in range(len(headers)))
    result.append(separator)
    
    # 数据行
    for row in rows:
        data_row = " | ".join(str(row[i] if i < len(row) else "").ljust(col_widths[i]) 
                             for i in range(len(headers)))
        result.append(data_row)
    
    return "\n".join(result)


def format_list(items: List[str], bullet: str = "•", indent: int = 2) -> str:
    """格式化列表
    
    Args:
        items: 列表项
        bullet: 项目符号
        indent: 缩进空格数
        
    Returns:
        格式化后的列表字符串
    """
    if not items:
        return ""
    
    indent_str = " " * indent
    return "\n".join(f"{indent_str}{bullet} {item}" for item in items)


def format_progress_bar(current: int, total: int, width: int = 20, 
                       fill: str = "█", empty: str = "░") -> str:
    """格式化进度条
    
    Args:
        current: 当前进度
        total: 总进度
        width: 进度条宽度
        fill: 填充字符
        empty: 空白字符
        
    Returns:
        格式化后的进度条字符串
    """
    if total <= 0:
        return f"[{empty * width}] 0%"
    
    percentage = min(100, max(0, (current / total) * 100))
    filled_width = int((current / total) * width)
    
    bar = fill * filled_width + empty * (width - filled_width)
    return f"[{bar}] {percentage:.1f}%"


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的文件大小字符串
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    return f"{size:.1f} {units[unit_index]}"


def format_duration(seconds: int) -> str:
    """格式化时间长度
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化后的时间长度字符串
    """
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes}分钟"
        else:
            return f"{minutes}分{remaining_seconds}秒"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes == 0:
            return f"{hours}小时"
        else:
            return f"{hours}小时{remaining_minutes}分钟"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        if remaining_hours == 0:
            return f"{days}天"
        else:
            return f"{days}天{remaining_hours}小时"


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_number(number: float, decimal_places: int = 2, 
                 use_separator: bool = True) -> str:
    """格式化数字
    
    Args:
        number: 数字
        decimal_places: 小数位数
        use_separator: 是否使用千位分隔符
        
    Returns:
        格式化后的数字字符串
    """
    if use_separator:
        return f"{number:,.{decimal_places}f}"
    else:
        return f"{number:.{decimal_places}f}"