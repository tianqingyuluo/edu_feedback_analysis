import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from .data_preprocessing import data_cleaning


def analyze_student_persona(df: pd.DataFrame, n_clusters: int = 4, pca_components: int = 7,
                            sample_size: int = 1000, random_state: int = 42,
                            model_path: str = "student_portrait.pkl"):

    df = data_cleaning(df)

    # 去除制表符
    df = df.map(lambda x: x.strip('\t') if isinstance(x, str) else x)

    # 学习相关列
    sx_cols = [
        '课前预学','课堂参与','课后复习','延伸阅读',
        '完成作业时间','自习时间','课外阅读时间','网络课程时间',
        '实验科研时间','社团活动时间','竞赛活动时间','其他学习时间',
        '同学合作','参与科研团队','参与学科竞赛','学习同学方法','师生交流频度'
    ]

    # 转为 float
    df[sx_cols] = df[sx_cols].astype(float)

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[sx_cols].values)

    # PCA
    pca = PCA(n_components=pca_components, random_state=random_state)
    X_pca = pca.fit_transform(X_scaled)

    # KMeans 聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_pca)

    # 映射学生画像（可按需修改）
    cluster_mapping = {
        0: '科研学霸型',
        1: '社团活跃型',
        2: '学业挣扎型',
        3: '自主学习型'
    }
    df['student_persona'] = df['cluster'].map(cluster_mapping)

    # 聚类结果统计
    persona_counts = df['student_persona'].value_counts()
    persona_json = {
        "labels": persona_counts.index.tolist(),
        "values": persona_counts.values.tolist()
    }

    # PCA 二维采样
    pca_df = pd.DataFrame({
        "pc1": X_pca[:, 0],
        "pc2": X_pca[:, 1],
        "student_persona": df["student_persona"]
    })
    sampled_2d = pca_df.sample(n=min(sample_size, len(pca_df)), random_state=random_state)
    pca_2d_json = sampled_2d.to_dict(orient="records")

    # PCA 三维采样
    pca_3d_df = pd.DataFrame({
        "pc1": X_pca[:, 0],
        "pc2": X_pca[:, 1],
        "pc3": X_pca[:, 2],
        "student_persona": df["student_persona"]
    })
    sampled_3d = pca_3d_df.sample(n=min(sample_size, len(pca_3d_df)), random_state=random_state)
    pca_3d_json = sampled_3d.to_dict(orient="records")

    # # 保存模型（包含 scaler, pca, kmeans）
    # model_bundle = {
    #     "scaler": scaler,
    #     "pca": pca,
    #     "kmeans": kmeans,
    #     "cluster_mapping": cluster_mapping
    # }
    # joblib.dump(model_bundle, model_path)

    return {
        "studentTypeData": persona_json,
        "pca_scatter": pca_2d_json,
        "pca_3d_scatter": pca_3d_json,
    }