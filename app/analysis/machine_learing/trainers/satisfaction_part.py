import pandas as pd
import pickle
import asyncio

from app.analysis.machine_learing.models import ModelVersionManager
from app.core.config import settings


# ================================
# 1. 读取数据
# ================================
def load_data(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(file_path, sep=',', engine='python', encoding='utf-8')
    df = df.applymap(lambda x: x.strip('\t') if isinstance(x, str) else x)
    return df

# ================================
# 2. 定义分类
# ================================
def get_categories() -> dict:
    xxqk = ['课前预学','课堂参与','课后复习','延伸阅读','完成作业时间','自习时间','课外阅读时间','网络课程时间','实验科研时间',
            '社团活动时间','竞赛活动时间','其他学习时间','同学合作','参与科研团队','参与学科竞赛','学习同学方法','师生交流频度']
    sz = ['思政课总体满意度','思政课设置满意度','思政课内容满意度','思政课质量满意度','思政课效果满意度']
    zy = ['专业课知识融合','专业课解决问题能力','专业课交叉融合','专业课实践结合','专业课努力程度','专业课前沿内容',
          '传统讲授','课堂互动','案例讨论','小组合作']
    ty = ['体育教育满意度']
    my = ['美育教育满意度']
    ld = ['劳动教育满意度']
    xy = ['社团活动满意度','校园文化满意度','创新创业满意度','国际交流满意度','社会实践满意度']
    sx = ['实习内容满意度','实习时间满意度','实习场地满意度','实习指导满意度']
    zwts = ['问题解决能力提升','自主学习能力提升','合作能力提升','表达沟通能力提升','未来规划能力提升','人文底蕴提升',
            '科学精神提升','学会学习提升','健康生活提升','责任担当提升','实践创新提升','自我提升']
    lsj = ['教师履职满意度','关爱学生满意度','教学投入满意度','教师总体满意度','课程目标解释','激发学习兴趣',
           '课后辅导答疑','立德树人','创造性思考']
    sxfw = ['一站式服务','实训安全管理','教师参与活动','学术讲座多','心理健康满意度','职业规划满意度',
            '班主任工作满意度','学业指导满意度','资助工作满意度']
    jctj = ['教室设备满意度','实训室满意度','图书馆满意度','网络资源满意度','体育设施满意度','住宿条件满意度','学校整体满意度']

    categories = {
        '学习情况': xxqk,
        '思政课': sz,
        '专业课': zy,
        '体育教育': ty,
        '美育教育': my,
        '劳动教育': ld,
        '校园生活': xy,
        '实习': sx,
        '自我提升': zwts,
        '老师教育': lsj,
        '学校服务': sxfw,
        '学校基础条件': jctj
    }
    return categories

# ================================
# 3. 计算每类均值
# ================================
def calculate_category_means(df: pd.DataFrame, categories: dict) -> pd.DataFrame:
    for cat, cols in categories.items():
        df[cat + '_均值'] = df[cols].mean(axis=1)
    return df

# ================================
# 4. 满意度映射
# ================================
def map_satisfaction(x: float) -> str:
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

def apply_satisfaction_mapping(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    for col in feature_cols:
        df[col + "_等级"] = df[col].apply(map_satisfaction)
    return df

# ================================
# 5. 计算相关系数
# ================================
def calculate_correlation(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    return df[feature_cols].corr()

# ================================
# 6. 异步训练函数（使用传入 df）
# ================================
async def async_train(df: pd.DataFrame):
    categories = get_categories()
    df = calculate_category_means(df, categories)

    feature_cols = [c + '_均值' for c in categories.keys()]
    df = apply_satisfaction_mapping(df, feature_cols)

    corr = calculate_correlation(df, feature_cols)

    # 保存模型
    model_data = {
        "dataframe": df,
        "categories": categories,
        "feature_cols": feature_cols,
        "correlation": corr
    }

    version_manager = ModelVersionManager(settings.machine_learning_models_path)
    version = await version_manager.get_next_version('satisfaction_part')
    model_path = settings.machine_learning_models_path + f'satisfaction_part_v{version}.pkl'

    with open(model_path, "wb") as f:
       pickle.dump({
            "model_data": model_data
    }, f)
    print(f"✅ 模型已保存到 {model_path}")

