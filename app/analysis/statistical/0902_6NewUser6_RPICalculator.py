# RPIProcessor.py
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class RPIProcessor:
    """资源感知度(RPI)处理器：权重->RPI->JSON"""

    # 资源字段与中文名映射（可省，但保持一致）
    RESOURCE_MAP = {
        '教室设备满意度': '教室设备',
        '实训室满意度': '实训室',
        '图书馆满意度': '图书馆',
        '网络资源满意度': '网络资源',
        '体育设施满意度': '体育设施',
        '住宿条件满意度': '住宿条件'
    }

    @classmethod
    def process_dataframe_to_json(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        输入原始 DataFrame → 计算 RPI → 返回前端 JSON
        """
        # 1️⃣ 计算权重
        weights = cls._calc_weights(df)
        # 2️⃣ 计算 RPI 并写回
        df = cls._calc_rpi(df, weights)
        # 3️⃣ 组装 JSON
        return cls._assemble_json(df)

    # ---------- 内部辅助 ----------
    @classmethod
    def _calc_weights(cls, df: pd.DataFrame) -> Dict[str, float]:
        """基于与「学校整体满意度」的相关性计算权重"""
        target = '学校整体满意度'
        weights = {}
        for col in cls.RESOURCE_MAP:
            corr = df[col].corr(df[target])
            weights[col] = abs(corr) if pd.notna(corr) else 0

        total = sum(weights.values())
        if total == 0:
            return {k: 1 / len(cls.RESOURCE_MAP) for k in cls.RESOURCE_MAP}
        return {k: v / total for k, v in weights.items()}

    @classmethod
    def _calc_rpi(cls, df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
        """计算 RPI 并写入 DataFrame"""
        df = df.copy()
        rpi = sum(df[col] * w for col, w in weights.items()) * 100
        df['RPI'] = np.clip(rpi, 0, 100)
        return df

    @classmethod
    def _assemble_json(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """学院→专业→年级 嵌套 JSON"""
        grade_order = {'freshmen': 0, 'sophomore': 1, 'junior': 2, 'senior': 3}

        academies_json = []
        for ac_name in df['学院'].unique():
            ac_df = df[df['学院'] == ac_name]
            majors_json = []
            for maj_name in ac_df['专业'].unique():
                maj_df = ac_df[ac_df['专业'] == maj_name]
                grades_json = []
                for gr_name in sorted(maj_df['年级'].unique(), key=lambda x: grade_order.get(x, 99)):
                    gr_df = maj_df[maj_df['年级'] == gr_name]
                    if gr_df.empty:
                        continue
                    # 各资源均值×100
                    res_values = [float((gr_df[col].mean() * 100).round(2)) for col in cls.RESOURCE_MAP]
                    # RPI 均值
                    rpi_val = float(gr_df['RPI'].mean().round(2))
                    grades_json.append({
                        'name': gr_name,
                        'data': res_values + [rpi_val]  # 七资源 + RPI
                    })
                if grades_json:
                    majors_json.append({'name': maj_name, 'grades': grades_json})
            if majors_json:
                academies_json.append({'name': ac_name, 'majors': majors_json})
        return academies_json


# ---------- 快速测试 ----------
if __name__ == '__main__':
    df = pd.read_csv('D:\python\edu_feedback_analysis\data\intermediate\初步清洗_比赛数据_2.csv')
    result = RPIProcessor.process_dataframe_to_json(df)
    print(f'生成 {len(result)} 个学院数据')
    print(result)