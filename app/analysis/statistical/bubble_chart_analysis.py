import pandas as pd
import json


def clean_data(df):
    """
    清洗数据
    
    Args:
        df: 输入的DataFrame
    
    Returns:
        DataFrame: 清洗后的DataFrame
    """
    required_cols = ['专业', '课堂参与', '教学投入满意度']
    # 检查必需列是否存在
    existing_cols = [col for col in required_cols if col in df.columns]
    if len(existing_cols) < len(required_cols):
        missing_cols = set(required_cols) - set(existing_cols)
        raise ValueError(f"缺少必需列: {missing_cols}")
    
    df = df[existing_cols].dropna()
    df = df[(df['课堂参与'] >= 0) & (df['课堂参与'] <= 100) &
            (df['教学投入满意度'] >= 0) & (df['教学投入满意度'] <= 100)]
    df['专业'] = df['专业'].str.strip()
    return df


def aggregate_data(df):
    """
    聚合数据
    
    Args:
        df: 输入的DataFrame
    
    Returns:
        DataFrame: 聚合后的DataFrame
    """
    grouped = df.groupby('专业').agg({
        '课堂参与': 'mean',
        '教学投入满意度': 'mean'
    }).reset_index()
    grouped.columns = ['专业', '平均课堂参与度', '平均教学投入满意度']
    # 确保数值列是float类型以便JSON序列化
    grouped['平均课堂参与度'] = grouped['平均课堂参与度'].astype(float)
    grouped['平均教学投入满意度'] = grouped['平均教学投入满意度'].astype(float)
    return grouped


def create_bubble_echarts_json(df):
    """
    创建师生互动气泡图ECharts JSON数据
    
    Args:
        df: 输入的DataFrame
    
    Returns:
        dict: 适合ECharts气泡图的JSON数据结构
    """
    # 数据清洗和聚合
    clean_df = clean_data(df)
    aggregated_df = aggregate_data(clean_df)
    
    # 转换为ECharts格式
    data_records = []
    for _, row in aggregated_df.iterrows():
        data_records.append({
            "name": row['专业'],
            "value": [
                row['平均课堂参与度'],
                row['平均教学投入满意度']
            ]
        })
    
    # 构建完整的ECharts JSON结构
    echarts_data = {
        "metadata": {
            "description": "师生互动关联数据（按专业聚合）",
            "生成时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "数据维度": {
                "专业数量": len(aggregated_df),
                "平均课堂参与度范围": [float(aggregated_df['平均课堂参与度'].min()), float(aggregated_df['平均课堂参与度'].max())],
                "平均教学满意度范围": [float(aggregated_df['平均教学投入满意度'].min()), float(aggregated_df['平均教学投入满意度'].max())]
            }
        },
        "data": data_records
    }
    
    return echarts_data