"""
雷达图分析数据预处理模块
负责对原始DataFrame进行清洗和预处理
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def preprocess_radar_data(df):
    """
    对原始DataFrame进行预处理，为雷达图分析做准备
    
    Args:
        df (pd.DataFrame): 原始输入数据框
    
    Returns:
        tuple: (processed_df, feature_groups, radar_dimensions)
            - processed_df: 预处理后的数据框
            - feature_groups: 特征分组字典
            - radar_dimensions: 雷达图维度列表
    """
    # 创建数据副本以避免修改原始数据
    processed_df = df.copy()
    
    # 特征选择：5个核心维度的指标
    feature_groups = {
        "学习行为": ["课前预学", "课堂参与", "课后复习", "自习时间", "课外阅读时间"],
        "学习互动": ["同学合作", "师生交流频度", "小组合作", "学习同学方法", "参与科研团队"],
        "课程评价": ["思政课总体满意度", "专业课知识融合", "专业课实践结合", "专业课前沿内容", "教师总体满意度"],
        "能力发展": ["问题解决能力提升", "自主学习能力提升", "合作能力提升", "表达沟通能力提升", "实践创新提升"],
        "资源满意度": ["教室设备满意度", "实训室满意度", "图书馆满意度", "网络资源满意度", "学校整体满意度"]
    }
    
    # 整合所有特征列
    all_features = []
    for group in feature_groups.values():
        all_features.extend(group)
    
    # 检查所有特征是否在数据中存在
    missing_features = [f for f in all_features if f not in processed_df.columns]
    if missing_features:
        print(f"警告：以下特征在数据中不存在: {missing_features}")
        # 过滤掉不存在的特征
        all_features = [f for f in all_features if f in processed_df.columns]
    
    # 归一化处理（0-100）
    if all_features:  # 确保有特征需要归一化
        scaler = MinMaxScaler(feature_range=(0, 100))
        processed_df[all_features] = scaler.fit_transform(
            processed_df[all_features].fillna(processed_df[all_features].median())
        )
    
    # 计算各维度平均得分
    for dim, features in feature_groups.items():
        # 过滤掉不存在的特征
        existing_features = [f for f in features if f in processed_df.columns]
        if existing_features:
            processed_df[f"{dim}综合得分"] = processed_df[existing_features].mean(axis=1)
        else:
            processed_df[f"{dim}综合得分"] = 0  # 如果没有有效特征，设为0
    
    # 最终雷达图使用5个维度得分
    radar_dimensions = list(feature_groups.keys())
    
    return processed_df, feature_groups, radar_dimensions