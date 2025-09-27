import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from .data_preprocessing import data_cleaning


def preprocess_features(df: pd.DataFrame):
    """读取数据并计算每个类别的均值特征"""
    df = data_cleaning(df)
    df = df.map(lambda x: x.strip('\t') if isinstance(x, str) else x)

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
        df[cat+'_均值'] = df[cols].mean(axis=1)

    feature_cols = [c+'_均值' for c in categories.keys()]
    return df, feature_cols, categories

def cluster_and_reduce(df: pd.DataFrame, feature_cols: list, n_clusters: int = 5):
    """标准化、PCA降维并聚类"""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[feature_cols])

    pca = PCA(n_components=0.95, random_state=0)
    X_pca = pca.fit_transform(X_scaled)

    kmeans = KMeans(n_clusters=n_clusters, random_state=0)
    df['群体类别'] = kmeans.fit_predict(X_pca)

    return df, X_scaled, scaler, pca, kmeans

def assign_group_labels(df: pd.DataFrame, feature_cols: list):
    """根据群体均值排序分配中文标签"""
    group_means = df.groupby('群体类别')[feature_cols].mean()
    mean_scores = group_means.mean(axis=1).sort_values(ascending=False)
    labels_order = ["满意","较满意","一般","较不满意","不满意"]
    label_map = {idx: labels_order[i] for i, idx in enumerate(mean_scores.index)}
    df['群体名称'] = df['群体类别'].map(label_map)
    group_means.index = group_means.index.map(label_map)
    return df, group_means, labels_order, label_map

def generate_feature_json(group_means: pd.DataFrame):
    """生成群体特征均值 JSON"""
    categories = list(group_means.columns)
    groups = list(group_means.index)
    result_json = {
        "labels": [cat.replace('_均值','') for cat in categories],
        "series": []
    }
    for group_name in groups:
        series_data = {
            "name": group_name,
            "data": [round(group_means.loc[group_name, cat], 3) for cat in categories]
        }
        result_json["series"].append(series_data)
    return result_json

def generate_group_count_json(df: pd.DataFrame, labels_order: list):
    """生成群体数量统计 JSON"""
    group_counts = df['群体名称'].value_counts().reindex(labels_order)
    count_json = {"labels": group_counts.index.tolist(), "values": group_counts.values.tolist()}
    return count_json

def compute_feature_importance(X_scaled: np.ndarray, df: pd.DataFrame, feature_cols: list):
    """计算特征重要性"""
    clf = RandomForestClassifier(random_state=0)
    clf.fit(X_scaled, df['群体类别'])
    importances = pd.Series(clf.feature_importances_, index=feature_cols).sort_values(ascending=False)
    top_importances = importances.head(10)
    labels = [label.replace('_均值','') for label in top_importances.index]
    values = [round(value, 4) for value in top_importances.values]
    return {"labels": labels, "values": values}

def analyze_feedback(df: pd.DataFrame):
    """整合分析流程，返回三个 JSON 并保存模型"""
    df, feature_cols, categories = preprocess_features(df)
    df, X_scaled, scaler, pca, kmeans = cluster_and_reduce(df, feature_cols)
    df, group_means, labels_order, label_map = assign_group_labels(df, feature_cols)

    feature_json = generate_feature_json(group_means)
    count_json = generate_group_count_json(df, labels_order)
    importance_json = compute_feature_importance(X_scaled, df, feature_cols)

    # 保存模型到 pkl
    # model_bundle = {
    #     "scaler": scaler,
    #     "pca": pca,
    #     "kmeans": kmeans,
    #     "feature_cols": feature_cols,
    #     "categories": categories,
    #     "label_map": label_map
    # }

    return {
        "satisfactionDistributionData": count_json,
        "overallSatisfactionData": feature_json,
        "SatisfactionContributionData": importance_json
    }