import pandas as pd

from .data_preprocessing import data_cleaning


def preprocess_data(df: pd.DataFrame):
    """读取数据并去除制表符"""
    df = data_cleaning(df)
    df = df.map(lambda x: x.strip('\t') if isinstance(x, str) else x)
    return df

def compute_category_means(df: pd.DataFrame):
    """计算每个类别的均值"""
    categories = {
        '学习情况': ['课前预学','课堂参与','课后复习','延伸阅读','完成作业时间','自习时间','课外阅读时间','网络课程时间','实验科研时间',
                     '社团活动时间','竞赛活动时间','其他学习时间','同学合作','参与科研团队','参与学科竞赛','学习同学方法','师生交流频度'],
        '思政课': ['思政课总体满意度','思政课设置满意度','思政课内容满意度','思政课质量满意度','思政课效果满意度'],
        '专业课': ['专业课知识融合','专业课解决问题能力','专业课交叉融合','专业课实践结合','专业课努力程度','专业课前沿内容',
                   '传统讲授','课堂互动','案例讨论','小组合作'],
        '体育教育': ['体育教育满意度'],
        '美育教育': ['美育教育满意度'],
        '劳动教育': ['劳动教育满意度'],
        '校园生活': ['社团活动满意度','校园文化满意度','创新创业满意度','国际交流满意度','社会实践满意度'],
        '实习': ['实习内容满意度','实习时间满意度','实习场地满意度','实习指导满意度'],
        '自我提升': ['问题解决能力提升','自主学习能力提升','合作能力提升','表达沟通能力提升','未来规划能力提升','人文底蕴提升',
                     '科学精神提升','学会学习提升','健康生活提升','责任担当提升','实践创新提升','自我提升'],
        '老师教育': ['教师履职满意度','关爱学生满意度','教学投入满意度','教师总体满意度','课程目标解释','激发学习兴趣',
                     '课后辅导答疑','立德树人','创造性思考'],
        '学校服务': ['一站式服务','实训安全管理','教师参与活动','学术讲座多','心理健康满意度','职业规划满意度',
                     '班主任工作满意度','学业指导满意度','资助工作满意度'],
        '学校基础条件': ['教室设备满意度','实训室满意度','图书馆满意度','网络资源满意度','体育设施满意度','住宿条件满意度','学校整体满意度']
    }

    for cat, cols in categories.items():
        df[cat + '_均值'] = df[cols].mean(axis=1)

    feature_cols = [c + '_均值' for c in categories.keys()]
    return df, feature_cols, categories

def map_satisfaction_level(df: pd.DataFrame, feature_cols: list):
    """将均值映射到满意度等级"""
    def map_level(x):
        if x >= 0.9:
            return "满意"
        elif x >= 0.75:
            return "较满意"
        elif x >= 0.6:
            return "一般"
        elif x >= 0.4:
            return "较不满意"
        else:
            return "不满意"

    for col in feature_cols:
        df[col + "_等级"] = df[col].apply(map_level)

    return df

def generate_satisfaction_json(df: pd.DataFrame, categories: dict):
    """生成每个类别的满意度统计 JSON"""
    satisfaction_order = ["满意","较满意","一般","较不满意","不满意"]
    result = {}
    for cat in categories.keys():
        counts = df[cat + "_均值_等级"].value_counts().reindex(satisfaction_order, fill_value=0)
        result[cat] = {
            "labels": satisfaction_order,
            "values": counts.values.tolist()
        }
    return result

def compute_correlation_matrix(df: pd.DataFrame, feature_cols: list):
    """计算均值特征的相关性矩阵 JSON"""
    corr = df[feature_cols].corr()
    corr_dict = {
        "labels": [label.replace('_均值', '') for label in corr.columns.tolist()],
        "matrix": corr.values.tolist()
    }
    return corr_dict

def analyze_feedback_satisfaction(df: pd.DataFrame):
    """分析满意度并生成 JSON"""
    df = preprocess_data(df)
    df, feature_cols, categories = compute_category_means(df)
    df = map_satisfaction_level(df, feature_cols)
    satisfaction_json = generate_satisfaction_json(df, categories)
    correlation_json = compute_correlation_matrix(df, feature_cols)

    return {
        "satisfactionPartData": satisfaction_json,
        "heatmapData": correlation_json
    }