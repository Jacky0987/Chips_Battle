"""
图表工具模块 - 提供各种ASCII图表绘制功能
符合CLI控制台风格的可视化组件
"""

from datetime import datetime, timedelta
import math


class ChartTools:
    """CLI控制台图表绘制工具类"""
    
    def __init__(self):
        # 图表样式配置 - 只使用上下分隔线
        self.styles = {
            'simple': {
                'horizontal': '─',
                'equals': '═'
            }
        }
        
        # 颜色配置
        self.colors = {
            'header': '#00FF41',
            'data': '#FFFFFF', 
            'positive': '#00FF00',
            'negative': '#FF0000',
            'neutral': '#FFFF00'
        }

    def create_header(self, title, subtitle=None, width=100):
        """创建标题头部，只使用上下分隔线"""
        top_line = "═" * width
        bottom_line = "═" * width
        
        header = f"{top_line}\n"
        
        # 标题行
        title_padding = (width - len(title)) // 2
        header += f"{' ' * title_padding}{title}\n"
        
        # 副标题
        if subtitle:
            subtitle_padding = (width - len(subtitle)) // 2
            header += f"{' ' * subtitle_padding}{subtitle}\n"
        
        header += f"{bottom_line}\n"
        return header

    def create_section_separator(self, title=None, width=80):
        """创建章节分隔符"""
        if title:
            title_len = len(title)
            side_len = (width - title_len - 2) // 2
            return f"{'─' * side_len} {title} {'─' * side_len}"
        else:
            return "─" * width

    def create_table(self, headers, rows, column_widths=None, align='left'):
        """创建表格，不使用左右边框"""
        if not headers or not rows:
            return "无数据"
        
        num_cols = len(headers)
        if column_widths is None:
            # 自动计算列宽
            column_widths = []
            for i in range(num_cols):
                header_width = len(str(headers[i]))
                max_data_width = max(len(str(row[i] if i < len(row) else "")) for row in rows)
                column_widths.append(max(header_width, max_data_width) + 2)
        
        table = ""
        
        # 表头
        header_line = ""
        separator_line = ""
        
        for i, (header, width) in enumerate(zip(headers, column_widths)):
            if align == 'right':
                header_cell = f"{str(header):>{width}}"
            elif align == 'center':
                header_cell = f"{str(header):^{width}}"
            else:
                header_cell = f"{str(header):<{width}}"
            
            header_line += header_cell
            separator_line += "─" * width
            
            if i < num_cols - 1:
                header_line += " | "
                separator_line += "───"
        
        table += header_line + "\n"
        table += separator_line + "\n"
        
        # 数据行
        for row in rows:
            row_line = ""
            for i, width in enumerate(column_widths):
                cell_data = str(row[i] if i < len(row) else "")
                
                if align == 'right':
                    cell = f"{cell_data:>{width}}"
                elif align == 'center':
                    cell = f"{cell_data:^{width}}"
                else:
                    cell = f"{cell_data:<{width}}"
                
                row_line += cell
                if i < num_cols - 1:
                    row_line += " | "
            
            table += row_line + "\n"
        
        return table

    def create_bar_chart(self, data, labels=None, title="", max_width=50, show_values=True):
        """创建横向柱状图，不使用边框"""
        if not data:
            return "无数据"
        
        chart = ""
        if title:
            chart += f"{title}\n\n"
        
        # 找出最大值用于缩放
        max_value = max(abs(val) for val in data)
        if max_value == 0:
            max_value = 1
        
        # 生成标签
        if labels is None:
            labels = [f"项目{i+1}" for i in range(len(data))]
        
        for i, (value, label) in enumerate(zip(data, labels)):
            # 计算条形长度
            if value >= 0:
                bar_length = int((value / max_value) * max_width)
                bar = "█" * bar_length
                spaces = " " * (max_width - bar_length)
                direction = "→"
            else:
                bar_length = int((abs(value) / max_value) * max_width)
                bar = "█" * bar_length
                spaces = " " * (max_width - bar_length)
                direction = "←"
            
            # 值标签
            value_str = f" {value:,.2f}" if show_values else ""
            
            chart += f"{direction} {label[:15]:<15} {bar}{spaces}{value_str}\n"
        
        return chart

    def create_line_chart(self, data, labels=None, title="", width=60, height=15):
        """创建简化的线性图表"""
        if not data or len(data) < 2:
            return "数据不足以生成图表"
        
        chart = ""
        if title:
            chart += f"{title}\n\n"
        
        min_val = min(data)
        max_val = max(data)
        val_range = max_val - min_val if max_val != min_val else 1
        
        # 创建图表网格
        for row in range(height):
            current_level = max_val - (row / (height - 1)) * val_range
            line = ""
            
            for col in range(width):
                data_index = int(col * (len(data) - 1) / (width - 1))
                data_point = data[data_index]
                
                # 判断是否在当前水平线上
                tolerance = val_range / height * 0.5
                if abs(data_point - current_level) <= tolerance:
                    line += "●"
                else:
                    line += " "
            
            line += f" {current_level:>6.2f}"
            chart += line + "\n"
        
        # 底部分隔线
        chart += "─" * width + "\n"
        
        # 时间轴标签（如果有的话）
        if labels and len(labels) >= 2:
            time_axis = f"{labels[0]:<10}" + " " * (width - 20) + f"{labels[-1]:>10}"
            chart += time_axis + "\n"
        
        return chart

    def create_heatmap(self, data, row_labels=None, col_labels=None, title="", cell_width=8):
        """创建热力图显示"""
        if not data or not data[0]:
            return "无数据"
        
        chart = ""
        if title:
            chart += f"{title}\n\n"
        
        rows = len(data)
        cols = len(data[0])
        
        # 列标签
        if col_labels:
            name_line = " " * 12  # 为行标签留空间
            value_line = " " * 12
            
            for i, col_label in enumerate(col_labels[:cols]):
                name_line += f"{col_label[:cell_width]:<{cell_width}}  "
                value_line += "─" * cell_width + "  "
            
            chart += name_line + "\n"
            chart += value_line + "\n"
        
        # 数据行
        for i, row in enumerate(data):
            row_label = row_labels[i][:10] if row_labels and i < len(row_labels) else f"行{i+1}"
            chart_line = f"{row_label:<10}  "
            
            for j, value in enumerate(row[:cols]):
                # 使用简单字符表示数值大小
                if isinstance(value, (int, float)):
                    temp_symbol = "█" if value > 0.5 else "▓" if value > 0 else "░"
                    value_str = f"{value:.2f}" if abs(value) < 100 else f"{value:.0f}"
                else:
                    temp_symbol = "?"
                    value_str = str(value)[:5]
                
                chart_line += f"{temp_symbol} {value_str:>5}   "
            
            chart += chart_line + "\n"
        
        return chart

    def create_sparkline(self, data, width=20):
        """创建迷你趋势线"""
        if not data or len(data) < 2:
            return "─" * width
        
        min_val = min(data)
        max_val = max(data)
        val_range = max_val - min_val if max_val != min_val else 1
        
        sparkline = ""
        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        for i in range(width):
            data_index = int(i * (len(data) - 1) / (width - 1))
            value = data[data_index]
            normalized = (value - min_val) / val_range
            char_index = min(int(normalized * (len(chars) - 1)), len(chars) - 1)
            sparkline += chars[char_index]
        
        return sparkline

    def create_gauge(self, value, min_val=0, max_val=100, width=30, label=""):
        """创建仪表盘样式的进度显示"""
        if value < min_val:
            value = min_val
        elif value > max_val:
            value = max_val
        
        percentage = (value - min_val) / (max_val - min_val)
        filled_length = int(percentage * width)
        
        # 选择填充字符
        if percentage >= 0.8:
            fill_char = "█"
        elif percentage >= 0.6:
            fill_char = "▓"
        elif percentage >= 0.3:
            fill_char = "▒"
        else:
            fill_char = "░"
        
        filled = fill_char * filled_length
        empty = "░" * (width - filled_length)
        gauge = f"[{filled}{empty}]"
        
        percentage_text = f" {percentage*100:.1f}%"
        gauge += percentage_text
        
        if label:
            gauge += f" {label}"
        
        return gauge

    def create_progress_ring(self, percentage, size=5):
        """创建环形进度显示"""
        if percentage < 0:
            percentage = 0
        elif percentage > 100:
            percentage = 100
        
        # 简化的环形显示
        if percentage >= 90:
            ring = "●●●●●"
        elif percentage >= 70:
            ring = "●●●●○"
        elif percentage >= 50:
            ring = "●●●○○"
        elif percentage >= 30:
            ring = "●●○○○"
        elif percentage >= 10:
            ring = "●○○○○"
        else:
            ring = "○○○○○"
        
        return f"({ring}) {percentage:.0f}%"

    def create_status_line(self, items, separator=" | ", width=80):
        """创建状态行显示"""
        status_text = separator.join(str(item) for item in items)
        if len(status_text) > width:
            status_text = status_text[:width-3] + "..."
        return status_text

    def format_number(self, num, decimal_places=2):
        """格式化数字显示"""
        if abs(num) >= 1e9:
            return f"{num/1e9:.{decimal_places}f}B"
        elif abs(num) >= 1e6:
            return f"{num/1e6:.{decimal_places}f}M"
        elif abs(num) >= 1e3:
            return f"{num/1e3:.{decimal_places}f}K"
        else:
            return f"{num:.{decimal_places}f}"

    def format_percentage(self, value, decimal_places=1):
        """格式化百分比显示"""
        return f"{value:+.{decimal_places}f}%" 