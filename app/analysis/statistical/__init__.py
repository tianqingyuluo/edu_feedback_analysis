"""
统计分析模块
提供各种教育数据分析功能，生成适合ECharts可视化的JSON数据
"""

from .group_comparison_radar_chart import create_radar_echarts_json
from .bubble_chart_analysis import create_bubble_echarts_json
from .sankey_analysis import create_sankey_echarts_json

__all__ = [
    'create_radar_echarts_json',
    'create_bubble_echarts_json',
    'create_sankey_echarts_json',
]