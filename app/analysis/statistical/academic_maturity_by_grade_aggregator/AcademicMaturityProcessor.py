# AcademicMaturityProcessor.py
import pandas as pd
from typing import List, Dict, Any
import numpy as np

# ========== 1. 一级分组 & 二级指标 (保持不变) ==========
GROUPS = {
    "学习行为": [
        "课前预学", "课堂参与", "课后复习", "自习时间", "课外阅读时间"
    ],
    "学习互动": [
        "同学合作", "师生交流频度", "小组合作", "学习同学方法", "参与科研团队"
    ],
    "课程评价": [
        "思政课总体满意度", "专业课知识融合", "专业课实践结合", "专业课前沿内容", "教师总体满意度"
    ],
    "能力发展": [
        "问题解决能力提升", "自主学习能力提升", "合作能力提升", "表达沟通能力提升", "实践创新提升"
    ],
    "资源满意度": [
        "教室设备满意度", "实训室满意度", "图书馆满意度", "网络资源满意度", "学校整体满意度"
    ]
}

# COLUMN_MAP 同样基于 GROUPS 定义，无需手动添加未在 GROUPS 中的列
COLUMN_MAP = {k: k for k in set(sum(GROUPS.values(), []))}


# 定义“越多越好”的评分函数 (内部函数，避免污染全局命名空间)
def _apply_more_is_better_score(series: pd.Series) -> pd.Series:
    """
    对“越多越好”的列进行评分：先截断（1%-99%），再Min-Max归一化，应用于整个Series。
    """
    if series.empty or series.isnull().all():
        return pd.Series(np.nan, index=series.index)

    # 仅对非NaN值进行操作
    series_clean = series.dropna()
    if series_clean.empty:
        return pd.Series(np.nan, index=series.index)

    lower = series_clean.quantile(0.01)
    upper = series_clean.quantile(0.99)
    # clip操作会返回一个副本
    clipped_series = series.clip(lower=lower, upper=upper)

    min_val = clipped_series.min()
    max_val = clipped_series.max()

    if max_val == min_val:  # 避免除以0的情况
        # 如果所有有效值都相同，且为0，则归一化为0，否则为1（表示最高分）
        return pd.Series(0.0 if min_val == 0 else 1.0, index=series.index)

    # 对clipped_series进行归一化，保留原始的NaN位置
    normalized_series = (clipped_series - min_val) / (max_val - min_val)
    return normalized_series


# ========== 2. 主入口 ==========
def process_maturity_to_json(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    输入原始 df → 返回 MetricGroup[]
      每个 Metric.data = [大一, 大二, 大三, 大四]  4 个值
    """
    # 复制 DataFrame 以避免修改原始输入
    processed_df = df.copy()

    # --- 1. 对指定列进行“越多越好”的归一化处理（本次二级清洗的范围）---
    cols_to_normalize_more_is_better = [
        '自习时间',
        '课外阅读时间',
        '网络课程时间',
        '实验科研时间',
        '竞赛活动时间',
        '其他学习时间'
    ]

    for col in cols_to_normalize_more_is_better:
        if col in processed_df.columns:
            # 对整个列应用“越多越好”的评分函数
            processed_df[col] = _apply_more_is_better_score(processed_df[col])
        else:
            print(f"Warning: Column '{col}' not found in the input DataFrame. Skipping normalization for this column.")

    # 中文年级 -> 数字
    grade_map = {"大一": 1, "大二": 2, "大三": 3, "大四": 4}
    # 使用 .loc 进行赋值，避免 SettingWithCopyWarning
    processed_df.loc[:, "年级数字"] = processed_df["年级"].map(grade_map)

    # 按年级聚合（均值）
    # 过滤出 COLUMN_MAP 中的所有列名，并且这些列名必须在 processed_df 中存在
    # 并且必须是数值类型（非数值类型无法求均值，即便清洗了也可能还有非数值的原始列）
    valid_cols_for_agg = [
        col_df for col_frontend, col_df in COLUMN_MAP.items()
        if col_df in processed_df.columns and pd.api.types.is_numeric_dtype(processed_df[col_df])
    ]

    if "年级数字" not in processed_df.columns or not pd.api.types.is_numeric_dtype(processed_df["年级数字"]):
        raise ValueError("DataFrame '年级'列转换成的'年级数字'列缺失或不是数字类型（可能年级值是 NaN），无法进行分组聚合。")

    agg_dict = {c: "mean" for c in valid_cols_for_agg}

    if not agg_dict:  # 如果没有可聚合的列，返回空结果
        print(
            "Warning: No numeric columns found for aggregation after processing and filtering. Returning empty result.")
        return []

    grouped = processed_df.groupby("年级数字").agg(agg_dict).round(4)  # 保留 4 位小数

    # 确保 1-4 年级全齐（缺则补 NaN）
    full_grades = pd.Series([1, 2, 3, 4], name='年级数字')
    # 使用 reindex 确保所有年级都有，缺失的将填充 NaN
    grouped = grouped.reindex(full_grades).sort_index()

    # 组装前端结构
    result: List[Dict[str, Any]] = []
    for group_name, indicators in GROUPS.items():
        metrics: List[Dict[str, Any]] = []
        for ind in indicators:
            # 确保指标在 COLUMN_MAP 中有定义，且对应的DataFrame列在grouped结果中
            # COLUMN_MAP 已经只包含 GROUPS 中的指标，所以这里只需检查 grouped.columns
            col_df = COLUMN_MAP.get(ind)  # 使用 .get() 避免 KeyErrors

            if col_df is not None and col_df in grouped.columns:
                # 4 个年级值 ×100 转 float
                data_vals = [float((val * 100).round(2)) if pd.notna(val) else None
                             for val in grouped[col_df].values]
                metrics.append({"name": ind, "data": data_vals})
            else:
                # 如果某个指标的列在聚合结果中缺失（可能原始df就没有，或者非数值被过滤）
                # 依然为前端提供占位符
                print(
                    f"Info: Indicator '{ind}' (mapped to '{col_df}') not found in aggregated data or was non-numeric. Creating placeholder.")
                metrics.append({"name": ind, "data": [None, None, None, None]})  # 默认填充4个None

        if metrics:  # 只有当一个组有实际指标时才添加这个组
            result.append({"name": group_name, "metrics": metrics})
    return result
