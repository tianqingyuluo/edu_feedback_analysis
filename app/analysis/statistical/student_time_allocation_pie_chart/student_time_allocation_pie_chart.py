import pandas as pd
import json
from pathlib import Path

# 8 个指标顺序（前端硬编码用）
METRICS = [
    '作业时间', '自习时间', '课外阅读', '网络课程',
    '实验科研', '社团活动', '学科竞赛', '其他学习'
]

# DataFrame 列 → 指标顺序 一一对应
COLS = [
    '完成作业时间', '自习时间', '课外阅读时间', '网络课程时间',
    '实验科研时间', '社团活动时间', '竞赛活动时间', '其他学习时间'
]

def build_academy_array(df: pd.DataFrame) -> list:
    if {'学院', '专业', '年级'}.difference(df.columns):
        raise ValueError('缺少 学院/专业/年级 列')
    if not set(COLS).issubset(df.columns):
        raise ValueError('缺少部分时间列')

    # 先拿到 学院→专业→年级→8 指标列表
    grouped = (
        df.groupby(['学院', '专业', '年级'])[COLS]
          .mean()
          .round(3)
          .apply(list, axis=1)
    )

    # 转成前端要的 Academy[]
    academy_map = {}
    for (academy, major, grade), data in grouped.items():
        academy_map.setdefault(academy, {}) \
                   .setdefault(major, []) \
                   .append({'name': grade, 'data': data})

    return [
        {
            'name': ac,
            'majors': [
                {'name': maj, 'grades': grades} for maj, grades in maj_map.items()
            ]
        }
        for ac, maj_map in academy_map.items()
    ]

