import pandas as pd


def data_cleaning(df: pd.DataFrame) -> pd.DataFrame:

    # 列名
    col = '完成作业时间'

    # 1. 归一化处理
    time_norm = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    # 2. 分位数
    p65 = time_norm.quantile(0.65)
    p80 = time_norm.quantile(0.80)

    # 3. 量化评分
    def score(val):
        if p65 <= val <= p80:
            return 1.0
        elif val < p65:
            return val / p65
        else:  # val > p80
            return max(0, 1 - (val - p80) / (1 - p80))

    df[col] = time_norm.apply(score)  # 覆盖原列

    # 列名
    col = '社团活动时间'

    # 1. 归一化处理
    time_norm = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    # 2. 分位数
    p65 = time_norm.quantile(0.5)
    p80 = time_norm.quantile(0.7)

    # 3. 量化评分
    def score(val):
        if p65 <= val <= p80:
            return 1.0
        elif val < p65:
            return val / p65
        else:  # val > p80
            return max(0, 1 - (val - p80) / (1 - p80))

    df[col] = time_norm.apply(score)  # 覆盖原列

    # 列名列表
    cols = [
        '自习时间',
        '课外阅读时间',
        '网络课程时间',
        '实验科研时间',
        '竞赛活动时间',
        '其他学习时间'
    ]

    # 处理每一列
    for col in cols:
        # 去除极端值影响（1%~99% 截断）
        lower = df[col].quantile(0.01)
        upper = df[col].quantile(0.99)
        df[col] = df[col].clip(lower, upper)

        # 归一化（越多越好）
        df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())

    return df

