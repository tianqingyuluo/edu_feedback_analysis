import pandas as pd
import json
import os


# 1. 数据清洗
def clean_data(df):
    required_cols = ['专业', '课堂参与', '教学投入满意度']
    df = df[required_cols].dropna()
    df = df[(df['课堂参与'] >= 0) & (df['课堂参与'] <= 100) &
            (df['教学投入满意度'] >= 0) & (df['教学投入满意度'] <= 100)]
    df['专业'] = df['专业'].str.strip()
    return df


# 2. 数据聚合
def aggregate_data(df):
    grouped = df.groupby('专业').agg({
        '课堂参与': 'mean',
        '教学投入满意度': 'mean'
    }).reset_index()
    grouped.columns = ['专业', '平均课堂参与度', '平均教学投入满意度']
    return grouped


# 3. 生成JSON
def generate_json(df, output_json):
    data_dict = {
        "metadata": {
            "description": "师生互动关联数据（按专业聚合）",
            "生成时间": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "数据维度": {
                "专业数量": len(df),
                "平均课堂参与度范围": [df['平均课堂参与度'].min(), df['平均课堂参与度'].max()],
                "平均教学满意度范围": [df['平均教学投入满意度'].min(), df['平均教学投入满意度'].max()]
            }
        },
        "data": df.to_dict(orient='records')
    }
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(data_dict, f, indent=4, ensure_ascii=False)


# 主程序
if __name__ == '__main__':
    # 输入输出路径
    INPUT_FILE = '../../../data/intermediate/初步清洗_比赛数据.csv'
    OUTPUT_JSON = '师生互动数据.json'

    try:
        # 检查路径
        if not os.path.exists(INPUT_FILE):
            raise FileNotFoundError(f"输入文件不存在: {INPUT_FILE}")

        # 执行流程
        raw_df = pd.read_csv(INPUT_FILE)
        clean_df = clean_data(raw_df)

        if len(clean_df) == 0:
            raise ValueError("清洗后没有有效数据")

        aggregated_df = aggregate_data(clean_df)
        generate_json(aggregated_df, OUTPUT_JSON)

        print(f"成功生成JSON文件: {OUTPUT_JSON}")
        print(f"处理数据概览:")
        print(f"- 专业数量: {len(aggregated_df)}")
        print(
            f"- 数据范围: 参与度 {aggregated_df['平均课堂参与度'].min():.2f}~{aggregated_df['平均课堂参与度'].max():.2f}, "
            f"满意度 {aggregated_df['平均教学投入满意度'].min():.2f}~{aggregated_df['平均教学投入满意度'].max():.2f}")

    except Exception as e:
        print(f"执行失败: {str(e)}")
        import traceback
        traceback.print_exc()
