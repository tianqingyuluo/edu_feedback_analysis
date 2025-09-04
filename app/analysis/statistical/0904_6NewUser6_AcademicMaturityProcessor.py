# AcademicMaturityProcessor.py
import pandas as pd
from typing import List, Dict, Any

# ========== 1. 一级分组 & 二级指标 ==========
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

# 如果 csv 列名是英文，在这里写反向映射；目前直接中文可不改
COLUMN_MAP = {k: k for k in set(sum(GROUPS.values(), []))}   # 按需覆盖


# ========== 2. 主入口 ==========
def process_maturity_to_json(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    输入原始 df → 返回 MetricGroup[]
      每个 Metric.data = [大一, 大二, 大三, 大四]  4 个值
    """
    # 中文年级 -> 数字
    grade_map = {"大一": 1, "大二": 2, "大三": 3, "大四": 4}
    df["年级数字"] = df["年级"].map(grade_map)

    # 按年级聚合（均值）
    need_cols = list(COLUMN_MAP.values())
    agg_dict = {c: "mean" for c in need_cols}
    grouped = df.groupby("年级数字").agg(agg_dict).round(4)  # 保留 4 位小数

    # 确保 1-4 年级全齐（缺则补 NaN）
    for g in [1, 2, 3, 4]:
        if g not in grouped.index:
            grouped.loc[g] = np.nan
    grouped = grouped.sort_index()  # 1→4

    # 组装前端结构
    result: List[Dict[str, Any]] = []
    for group_name, indicators in GROUPS.items():
        metrics: List[Dict[str, Any]] = []
        for ind in indicators:
            col = COLUMN_MAP[ind]
            # 4 个年级值 ×100 转 float
            data_vals = [float((val * 100).round(2)) if pd.notna(val) else None
                         for val in grouped[col].values]
            metrics.append({"name": ind, "data": data_vals})
        result.append({"name": group_name, "metrics": metrics})

    return result


# ========== 3. 快速测试 ==========
if __name__ == "__main__":
    df = pd.read_csv('D:\python\edu_feedback_analysis\data\intermediate\初步清洗_比赛数据_2.csv')
    print(process_maturity_to_json(df))