# -*- coding: utf-8 -*-
"""
计算器命令

提供数学计算功能。
"""

import math
import re
from typing import List
from commands.base import AppCommand, CommandResult, CommandContext


class CalculatorCommand(AppCommand):
    """计算器命令"""
    
    def __init__(self):
        super().__init__()
    
    @property
    def name(self) -> str:
        return "calc"
    
    @property
    def aliases(self) -> List[str]:
        return ["calculator", "math", "compute"]
    
    @property
    def description(self) -> str:
        return "计算器 - 执行数学计算和表达式求值"
    
    @property
    def usage(self) -> str:
        return "calc <表达式> 或 calc <操作> [参数...]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行计算器命令
        
        Args:
            args: 命令参数列表
            context: 命令执行上下文
            
        Returns:
            命令执行结果
        """
        try:
            if not args:
                return self._show_help()
            
            # 检查是否是特殊操作
            if args[0].lower() == "help":
                return self._show_help()
            elif args[0].lower() == "functions":
                return self._show_functions()
            elif args[0].lower() == "constants":
                return self._show_constants()
            
            # 合并所有参数为一个表达式
            expression = ' '.join(args)
            
            # 计算表达式
            result = await self._calculate(expression)
            return self.success(f"🧮 计算结果:\n\n{expression} = {result}")
            
        except Exception as e:
            self.logger.error(f"计算器命令执行失败: {e}")
            return self.error(f"计算失败: {str(e)}")
    
    def _show_help(self) -> CommandResult:
        """显示帮助信息"""
        help_text = """
🧮 计算器命令帮助:

📊 基本用法:
  calc <表达式>           - 计算数学表达式
  calc functions          - 显示可用函数
  calc constants          - 显示可用常数
  calc help               - 显示此帮助信息

🔢 支持的运算:
  + - * /                 - 基本四则运算
  ** 或 ^                 - 幂运算
  % 或 mod                - 取模运算
  // 或 div               - 整除运算
  ( )                     - 括号分组

📐 数学函数:
  sin, cos, tan           - 三角函数
  asin, acos, atan        - 反三角函数
  log, log10, ln          - 对数函数
  sqrt, cbrt              - 开方函数
  abs, ceil, floor        - 取值函数
  exp, pow                - 指数函数

🔢 常数:
  pi, e                   - 数学常数
  inf, nan                - 特殊值

💡 示例:
  calc 2 + 3 * 4                    # 基本运算: 14
  calc sqrt(16) + 2^3               # 函数和幂运算: 12
  calc sin(pi/2)                    # 三角函数: 1
  calc log(e) + ln(10)              # 对数运算
  calc (1 + sqrt(5)) / 2            # 黄金比例

⚠️ 注意:
  - 三角函数使用弧度制
  - 支持科学计数法 (如 1e6)
  - 表达式中可以使用空格
"""
        return self.success(help_text)
    
    def _show_functions(self) -> CommandResult:
        """显示可用函数"""
        functions_text = """
📐 可用数学函数:

🔺 三角函数:
  sin(x)     - 正弦函数
  cos(x)     - 余弦函数
  tan(x)     - 正切函数
  asin(x)    - 反正弦函数
  acos(x)    - 反余弦函数
  atan(x)    - 反正切函数
  atan2(y,x) - 两参数反正切函数

📊 对数函数:
  log(x)     - 自然对数 (ln)
  log10(x)   - 常用对数
  log2(x)    - 以2为底的对数
  ln(x)      - 自然对数 (同log)

🔢 幂函数和开方:
  sqrt(x)    - 平方根
  cbrt(x)    - 立方根
  pow(x,y)   - x的y次方
  exp(x)     - e的x次方

📏 取值函数:
  abs(x)     - 绝对值
  ceil(x)    - 向上取整
  floor(x)   - 向下取整
  round(x)   - 四舍五入
  trunc(x)   - 截断取整

🎲 其他函数:
  max(x,y)   - 最大值
  min(x,y)   - 最小值
  gcd(x,y)   - 最大公约数
  factorial(x) - 阶乘

💡 示例:
  calc sin(pi/4)         # 0.7071...
  calc log10(1000)       # 3
  calc sqrt(pow(3,2) + pow(4,2))  # 5
"""
        return self.success(functions_text)
    
    def _show_constants(self) -> CommandResult:
        """显示可用常数"""
        constants_text = """
🔢 可用数学常数:

📐 基本常数:
  pi         - 圆周率 (3.14159...)
  e          - 自然常数 (2.71828...)
  tau        - 2π (6.28318...)

🔢 特殊值:
  inf        - 正无穷大
  -inf       - 负无穷大
  nan        - 非数值 (Not a Number)

📊 物理常数:
  c          - 光速 (299792458 m/s)
  g          - 重力加速度 (9.80665 m/s²)
  h          - 普朗克常数 (6.626e-34 J·s)

🔬 数学常数:
  phi        - 黄金比例 (1.618...)
  gamma      - 欧拉常数 (0.5772...)
  sqrt2      - √2 (1.414...)
  sqrt3      - √3 (1.732...)

💡 示例:
  calc pi * 2            # 2π
  calc e^2               # e的平方
  calc phi * 100         # 黄金比例的100倍
  calc sqrt2 + sqrt3     # √2 + √3

⚠️ 注意:
  - 常数名称区分大小写
  - 可以在表达式中直接使用
  - 物理常数使用SI单位
"""
        return self.success(constants_text)
    
    async def _calculate(self, expression: str) -> str:
        """计算数学表达式
        
        Args:
            expression: 数学表达式字符串
            
        Returns:
            计算结果字符串
        """
        try:
            # 预处理表达式
            processed_expr = self._preprocess_expression(expression)
            
            # 创建安全的计算环境
            safe_dict = self._create_safe_environment()
            
            # 计算表达式
            result = eval(processed_expr, {"__builtins__": {}}, safe_dict)
            
            # 格式化结果
            return self._format_result(result)
            
        except ZeroDivisionError:
            raise ValueError("除零错误")
        except OverflowError:
            raise ValueError("数值溢出")
        except ValueError as e:
            raise ValueError(f"数值错误: {str(e)}")
        except SyntaxError:
            raise ValueError("表达式语法错误")
        except Exception as e:
            raise ValueError(f"计算错误: {str(e)}")
    
    def _preprocess_expression(self, expression: str) -> str:
        """预处理表达式"""
        # 移除空格
        expr = expression.replace(" ", "")
        
        # 替换常见符号
        expr = expr.replace("^", "**")  # 幂运算
        expr = re.sub(r'(\d+)\s*mod\s*(\d+)', r'(\1 % \2)', expr)  # 取模
        expr = re.sub(r'(\d+)\s*div\s*(\d+)', r'(\1 // \2)', expr)  # 整除
        
        # 处理隐式乘法 (如 2pi -> 2*pi)
        # 但要避免函数名被误处理 (如 ln(e) 不应该变成 ln*e, log10(100) 不应该变成 log*10*(100))
        # 定义已知的函数名列表（不包括常数），避免它们被拆分
        function_names = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'atan2', 
                         'log', 'log10', 'log2', 'ln', 'sqrt', 'cbrt', 'pow', 'exp', 
                         'abs', 'ceil', 'floor', 'round', 'trunc', 'max', 'min', 
                         'gcd', 'factorial']
        
        # 先保护函数名，用临时标记替换
        protected_functions = {}
        for i, func_name in enumerate(sorted(function_names, key=len, reverse=True)):
            placeholder = f'__FUNC_{i}__'
            if func_name in expr:
                expr = expr.replace(func_name, placeholder)
                protected_functions[placeholder] = func_name
        
        # 处理隐式乘法
        expr = re.sub(r'(\d+)([a-zA-Z]+)(?![a-zA-Z0-9_])', r'\1*\2', expr)  # 数字+变量
        expr = re.sub(r'([a-zA-Z]+)(?![a-zA-Z0-9_])(\d+)', r'\1*\2', expr)  # 变量+数字
        expr = re.sub(r'\)(\d+)', r')*\1', expr)  # 括号后的数字
        expr = re.sub(r'(\d+)\(', r'\1*(', expr)  # 数字后的括号
        
        # 恢复函数名
        for placeholder, func_name in protected_functions.items():
            expr = expr.replace(placeholder, func_name)
        
        return expr
    
    def _create_safe_environment(self) -> dict:
        """创建安全的计算环境"""
        safe_dict = {
            # 基本数学函数
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'atan2': math.atan2,
            'log': math.log, 'log10': math.log10, 'log2': math.log2,
            'ln': math.log,
            'sqrt': math.sqrt, 'cbrt': lambda x: x**(1/3),
            'pow': math.pow, 'exp': math.exp,
            'abs': abs, 'ceil': math.ceil, 'floor': math.floor,
            'round': round, 'trunc': math.trunc,
            'max': max, 'min': min,
            'gcd': math.gcd, 'factorial': math.factorial,
            
            # 数学常数
            'pi': math.pi, 'e': math.e, 'tau': math.tau,
            'inf': math.inf, 'nan': math.nan,
            'phi': (1 + math.sqrt(5)) / 2,  # 黄金比例
            'gamma': 0.5772156649015329,  # 欧拉常数
            'sqrt2': math.sqrt(2), 'sqrt3': math.sqrt(3),
            
            # 物理常数
            'c': 299792458,  # 光速
            'g': 9.80665,    # 重力加速度
            'h': 6.62607015e-34,  # 普朗克常数
        }
        
        return safe_dict
    
    def _format_result(self, result) -> str:
        """格式化计算结果"""
        if isinstance(result, complex):
            if result.imag == 0:
                result = result.real
            else:
                return f"{result.real:g} + {result.imag:g}i"
        
        if isinstance(result, float):
            if math.isnan(result):
                return "NaN (非数值)"
            elif math.isinf(result):
                return "∞ (无穷大)" if result > 0 else "-∞ (负无穷大)"
            elif result.is_integer():
                return str(int(result))
            else:
                # 智能格式化小数
                if abs(result) < 1e-10:
                    return "0"
                elif abs(result) > 1e10 or abs(result) < 1e-4:
                    return f"{result:.6e}"  # 科学计数法
                else:
                    return f"{result:.10g}"  # 去除尾随零
        
        return str(result)