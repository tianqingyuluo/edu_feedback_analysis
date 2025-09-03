"""
雷达图分析统一入口函数模块
提供统一接口调用雷达图分析功能
"""

import pandas as pd

from .data_preprocessing import preprocess_radar_data
from .analysis import perform_radar_analysis


def create_radar_echarts_json(df):
    """
    创建完整的雷达图ECharts JSON数据（统一入口函数）
    
    Args:
        df (pd.DataFrame): 输入的DataFrame
    
    Returns:
        dict: 完整的雷达图JSON数据，可直接用于ECharts
    """
    # 1. 数据预处理
    processed_df, feature_groups, radar_dimensions = preprocess_radar_data(df)
    
    # 2. 执行分析
    echarts_json = perform_radar_analysis(processed_df, feature_groups, radar_dimensions)
    
    # # 3. 组织JSON输出
    # echarts_json = create_radar_echarts_json_from_analysis(radar_results)
    
    return echarts_json


def analyze_radar_data(df):
    """
    分析雷达图数据，生成三种分组方案的雷达图JSON数据
    
    Args:
        df (pd.DataFrame): 输入的DataFrame
    
    Returns:
        dict: 包含三种分组方案雷达图数据的字典
    """
    # 1. 数据预处理
    processed_df, feature_groups, radar_dimensions = preprocess_radar_data(df)
    
    # 2. 执行分析
    radar_results = perform_radar_analysis(processed_df, feature_groups, radar_dimensions)
    
    return radar_results