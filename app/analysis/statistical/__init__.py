"""
统计分析模块
提供各种教育数据分析功能，生成适合ECharts可视化的JSON数据
"""

from .group_comparison_radar_chart import create_radar_echarts_json
from .teacher_student_interaction_bubble_chart.teacher_student_interaction_bubble_chart import create_bubble_echarts_json
from app.analysis.statistical.student_time_allocation_pie_chart.student_time_allocation_pie_chart import build_academy_array
from app.analysis.statistical.academic_maturity_by_grade_aggregator.AcademicMaturityProcessor import process_maturity_to_json
from app.analysis.statistical.correlation_based_EHI_builder.ehiCalculator import DataProcessor
from app.analysis.statistical.correlation_based_RPI_builder.RPICalculator import RPIProcessor

__all__ = [
    'create_radar_echarts_json',
    'create_bubble_echarts_json',
    'build_academy_array',
    'process_maturity_to_json',
    'DataProcessor',
    'RPIProcessor'
]