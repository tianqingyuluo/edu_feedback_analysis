import pandas as pd
import json


def create_bubble_echarts_json(df):
    """
    创建师生互动气泡图ECharts JSON数据

    Args:
        df: 输入的DataFrame

    Returns:
        list: 学院和专业的数据结构，匹配MetricGroup接口
    """
    df['学院'] = df['学院'].str.strip()
    df['专业'] = df['专业'].str.strip()

    # 按学院和专业聚合数据 - 使用size()来计数
    grouped = df.groupby(['学院', '专业']).agg({
        '课堂参与': 'mean',
        '教学投入满意度': 'mean'
    })

    # 添加计数列
    grouped['专业人数'] = df.groupby(['学院', '专业']).size()

    grouped = grouped.reset_index()

    # 确保数值列是float类型
    grouped['课堂参与'] = grouped['课堂参与'].astype(float)
    grouped['教学投入满意度'] = grouped['教学投入满意度'].astype(float)
    grouped['专业人数'] = grouped['专业人数'].astype(int)

    # 构建学院和专业的数据结构，匹配MetricGroup接口
    metric_groups = []
    for academy_name in grouped['学院'].unique():
        academy_data = grouped[grouped['学院'] == academy_name]

        metrics = []
        for _, row in academy_data.iterrows():
            metrics.append({
                "name": row['专业'],
                "data": [
                    float(row['课堂参与']),  # x轴：课堂参与度
                    float(row['教学投入满意度']),  # y轴：教学满意度
                    int(row['专业人数'])  # 气泡大小：专业人数
                ]
            })

        metric_groups.append({
            "name": academy_name,
            "metrics": metrics
        })

    return metric_groups
