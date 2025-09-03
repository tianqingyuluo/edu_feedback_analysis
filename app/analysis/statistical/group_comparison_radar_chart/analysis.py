"""
雷达图分析模块
负责对预处理后的数据进行各类分析
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans


def prepare_radar_data(df, groups_dict, radar_dimensions):
    """
    准备雷达图数据
    
    Args:
        df: 输入的DataFrame
        groups_dict: 分组字典 {group_name: group_df}
        radar_dimensions: 雷达图维度列表
    
    Returns:
        radar_data: 适合ECharts雷达图的JSON数据结构
    """
    radar_data = {
        "comment": "",
        "academies": []
    }


    for i, (group_name, group_df) in enumerate(groups_dict.items()):
        if len(group_df) < 1:  # 最小样本量要求
            continue

        # 清理群体名称中的特殊字符
        striped_group_name = str(group_name).replace('\t', '').replace('\n', '').strip()
        clean_group_name_list = striped_group_name.split(" ")
        radar_data["academies"].append({
            "name": clean_group_name_list[0],
            "majors": []
        })
        radar_data["academies"][-1]["majors"].append({
            "name": clean_group_name_list[1],
            "groups": []
        })
        radar_data["academies"][-1]["majors"][-1]["groups"].append({
            "name": clean_group_name_list[2],
            "data": []
        })

        # 计算各维度平均值
        dimension_columns = [f"{dim}综合得分" for dim in radar_dimensions]
        # 检查所有维度列是否存在
        existing_columns = [col for col in dimension_columns if col in group_df.columns]
        if len(existing_columns) != len(dimension_columns):
            print(f"警告：群体 {clean_group_name_list[2]} 缺少 {len(dimension_columns) - len(existing_columns)} 个维度列")

        # 确保均值转换为Python原生类型以便JSON序列化
        if existing_columns:
            mean_values = group_df[existing_columns].mean()
            values = [float(v) for v in mean_values.tolist()]
        else:
            values = [0.0] * len(radar_dimensions)

        # 添加到数据结构
        radar_data["academies"][-1]["majors"][-1]["groups"][-1]["data"] = values

    return radar_data


def analyze_college_groups(df, feature_groups, radar_dimensions):
    """
    按学院分组进行分析
    
    Args:
        df: 输入的DataFrame
        feature_groups: 特征分组字典
        radar_dimensions: 雷达图维度列表
    
    Returns:
        dict: 学院分组的雷达图数据
    """
    college_groups = {}
    # 我们需要调用返回每一个学院里的每一个专业的每一个年级的组
    for academy in df['学院'].unique():
        college_df = df[df['学院'] == academy]
        for major in college_df['专业'].unique():
            major_df = college_df[college_df['专业'] == major]
            for grade in major_df['年级'].unique():
                grade_df = major_df[major_df['年级'] == grade]
                college_groups[f"{academy} {major} {grade}"] = grade_df
    
    return prepare_radar_data(df, college_groups, radar_dimensions)


def perform_radar_analysis(df, feature_groups, radar_dimensions):
    """
    执行完整的雷达图分析，生成三种分组方案的雷达图数据
    
    Args:
        df: 输入的DataFrame
        feature_groups: 特征分组字典
        radar_dimensions: 雷达图维度列表
    
    Returns:
        dict: 包含三种分组方案雷达图数据的字典
    """
    # 执行分析
    college_radar = analyze_college_groups(df, feature_groups, radar_dimensions)
    
    return college_radar