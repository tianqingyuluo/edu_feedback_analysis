import pandas as pd
import numpy as np
from typing import Dict, List, Any


class DataProcessor:
    """数据处理类，使用相关性分析计算权重并返回前端JSON"""

    # 关键指标映射
    KPI_MAPPING = {
        '课前预习得分': '课前预学',
        '课堂互动得分': '课堂参与',
        '课后复习得分': '课后复习',
        '知识拓展得分': '延伸阅读',
        '师生互动质量': '师生交流频度',
        '实践应用能力': '专业课实践结合',
        '合作学习效果': '同学合作'
    }

    @classmethod
    def process_dataframe_to_json(cls, df: pd.DataFrame, outcome_variables: List[str] = None) -> List[Dict[str, Any]]:
        """
        处理DataFrame并返回前端JSON，使用相关性分析计算权重

        Args:
            df: 包含数据的DataFrame
            outcome_variables: 学业成果变量列表，如果为None则使用默认列表

        Returns:
            前端需要的嵌套JSON数据结构
        """
        # 计算相关性权重
        if outcome_variables is None:
            outcome_variables = cls._get_default_outcome_variables()

        weights = cls.calculate_correlation_weights(df, outcome_variables)

        # 使用计算出的权重计算EHI分数
        df = cls._calculate_ehi_scores(df, weights)

        # 组装前端数据
        return cls._assemble_frontend_data(df)

    @classmethod
    def _get_default_outcome_variables(cls) -> List[str]:
        """获取默认的学业成果变量列表"""
        return [
            '问题解决能力提升',  # 学习收获评价 - 分析问题、解决问题能力提升
            '专业课知识融合',  # 专业课评价 - 课程将知识、能力、素养进行了有机融合
            '专业课解决问题能力',  # 专业课评价 - 课程教学培养了我解决复杂问题的综合能力
            '自主学习能力提升',  # 学习收获评价 - 自主学习能力提升
            '合作能力提升',  # 学习收获评价 - 合作能力提升
            '表达沟通能力提升',  # 学习收获评价 - 书面表达和沟通能力提升
            '未来规划能力提升',  # 学习收获评价 - 有能力规划未来工作生活
            '科学精神提升',  # 核心素养提升 - 科学精神（理性思维、批判质疑、勇于探究等）
            '实践创新提升',  # 核心素养提升 - 实践创新（劳动意识、问题解决、技术应用等）
        ]

    @classmethod
    def calculate_correlation_weights(cls, df: pd.DataFrame, outcome_variables: List[str]) -> Dict[str, float]:
        """
        基于学业成果的相关性分析确定权重

        Args:
            df: 包含数据的DataFrame
            outcome_variables: 学业成果变量列表

        Returns:
            基于相关性分析的权重字典
        """

        # 提取关键指标数据
        kpi_data = df[list(cls.KPI_MAPPING.values())].copy()
        kpi_data.columns = list(cls.KPI_MAPPING.keys())

        correlation_weights = {}

        for kpi in kpi_data.columns:
            # 计算与每个成果变量的平均相关性
            corrs = []
            for outcome in outcome_variables:
                if outcome in df.columns:
                    # 确保两个Series长度相同，且无NaN对计算影响
                    temp_data = kpi_data[[kpi]].dropna()
                    temp_outcome = df[[outcome]].loc[temp_data.index].dropna()
                    if not temp_data.empty and not temp_outcome.empty:
                        corr = np.corrcoef(temp_data[kpi], temp_outcome[outcome])[0, 1]
                        if not np.isnan(corr):
                            corrs.append(abs(corr))
            if corrs:
                correlation_weights[kpi] = np.mean(corrs)
            else:
                correlation_weights[kpi] = 0
                print(f"  {kpi} 与学业成果的平均相关性: 无法计算")

        # 归一化权重
        total = sum(correlation_weights.values())
        if total == 0:
            correlation_weights = {k: 1 / len(kpi_data.columns) for k in kpi_data.columns}
        else:
            correlation_weights = {k: v / total for k, v in correlation_weights.items()}

        return correlation_weights

    @classmethod
    def calculate_ehi_with_weights(cls, df: pd.DataFrame, weights: Dict[str, float]) -> pd.Series:
        """
        使用指定权重计算EHI分数

        Args:
            df: 包含数据的DataFrame
            weights: 权重字典

        Returns:
            EHI分数Series
        """
        ehi_scores = 0

        for kpi_key, weight in weights.items():
            csv_col_name = cls.KPI_MAPPING.get(kpi_key)
            if csv_col_name and csv_col_name in df.columns:
                ehi_scores += df[csv_col_name] * weight * 100

        return np.clip(ehi_scores, 0, 100)

    @classmethod
    def _calculate_ehi_scores(cls, df: pd.DataFrame, weights: Dict[str, float]) -> pd.DataFrame:
        """使用指定权重计算EHI分数"""
        result_df = df.copy()
        ehi_scores = cls.calculate_ehi_with_weights(result_df, weights)
        result_df['EHI_score'] = ehi_scores
        return result_df

    @classmethod
    def _assemble_frontend_data(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """组装前端JSON数据"""
        radar_kpi_cols = list(cls.KPI_MAPPING.values())
        academies_data = []

        # 定义年级排序
        grade_order = {'freshmen': 0, 'sophomore': 1, 'junior': 2, 'senior': 3}

        for academy_name in df['学院'].unique():
            academy_majors = []
            academy_df = df[df['学院'] == academy_name]

            for major_name in academy_df['专业'].unique():
                major_grades = []
                major_df = academy_df[academy_df['专业'] == major_name]

                # 按年级排序
                sorted_grades = sorted(
                    major_df['年级'].unique(),
                    key=lambda x: grade_order.get(x, 99)
                )

                for grade_name in sorted_grades:
                    grade_df = major_df[major_df['年级'] == grade_name]

                    if len(grade_df) > 0:
                        # 计算7个指标的平均值并扩大100倍，转换为Python float
                        radar_means = (grade_df[radar_kpi_cols].mean() * 100).round(2)
                        radar_means = [float(x) for x in radar_means]

                        # 计算EHI平均值，转换为Python float
                        ehi_mean = float(grade_df['EHI_score'].mean().round(2))

                        major_grades.append({
                            'name': grade_name,
                            'data': radar_means + [ehi_mean]
                        })

                if major_grades:
                    academy_majors.append({
                        'name': major_name,
                        'grades': major_grades
                    })

            if academy_majors:
                academies_data.append({
                    'name': academy_name,
                    'majors': academy_majors
                })

        return academies_data

