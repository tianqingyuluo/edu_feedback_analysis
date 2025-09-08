import pandas as pd
import numpy as np
import json
import pickle
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

from app.analysis.machine_learing.models import ModelVersionManager
from app.core.config import settings


# -------------------------------
# Step 1: 数据预处理
# -------------------------------
def clean_dataframe(df, feature_cols):
    """清洗传入的 DataFrame"""
    df = df.map(lambda x: x.strip('\t') if isinstance(x, str) else x)
    df[feature_cols] = df[feature_cols].astype(float)
    return df


# -------------------------------
# Step 2: 数据标准化 + PCA
# -------------------------------
def run_pca(df, feature_cols, n_components=7):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df[feature_cols].values)

    pca = PCA(n_components=n_components, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    explained_ratios = pca.explained_variance_ratio_
    cum_var = np.cumsum(explained_ratios)

    chart_data = {
        "xAxis": [f"主成分{i}" for i in range(1, len(explained_ratios) + 1)],
        "bar": explained_ratios.tolist(),
        "line": cum_var.tolist()
    }

    return X_pca, chart_data, pca


# -------------------------------
# Step 3: 聚类评估
# -------------------------------
def evaluate_clusters(X_pca, k_range=range(2, 10)):
    wcss, silhouette_scores = [], []
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X_pca)
        wcss.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_pca, kmeans.labels_))

    return {"k": list(k_range), "wcss": wcss, "silhouette": silhouette_scores}


# -------------------------------
# Step 4: 聚类建模 + 标签
# -------------------------------
def run_kmeans(X_pca, df, n_clusters=4):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["cluster"] = kmeans.fit_predict(X_pca)

    cluster_mapping = {
        0: "科研学霸型",
        1: "社团活跃型",
        2: "学业挣扎型",
        3: "自主学习型"
    }
    df["student_persona"] = df["cluster"].map(cluster_mapping)

    persona_counts = df["student_persona"].value_counts()
    result_json = {
        "labels": persona_counts.index.tolist(),
        "values": persona_counts.values.tolist()
    }
    return df, result_json, kmeans


# -------------------------------
# Step 5: PCA 降维导出 JSON
# -------------------------------
def export_pca_json(X_pca, df, n_sample=1000):
    pca_df = pd.DataFrame({
        "pc1": X_pca[:, 0],
        "pc2": X_pca[:, 1],
        "student_persona": df["student_persona"]
    })
    sampled_df_2d = pca_df.sample(n=min(n_sample, len(pca_df)), random_state=42)

    pca_3d_df = pd.DataFrame({
        "pc1": X_pca[:, 0],
        "pc2": X_pca[:, 1],
        "pc3": X_pca[:, 2],
        "student_persona": df["student_persona"]
    })
    sampled_df_3d = pca_3d_df.sample(n=min(n_sample, len(pca_3d_df)), random_state=42)

    return {
        "pca_scatter": sampled_df_2d.to_dict(orient="records"),
        "pca_3d_scatter": sampled_df_3d.to_dict(orient="records")
    }


# -------------------------------
# Step 6: 主运行函数
# -------------------------------
async def async_train(df: pd.DataFrame):
    """传入 DataFrame，运行 PCA + KMeans，并保存模型和结果"""

    feature_cols = [
        '课前预学','课堂参与','课后复习','延伸阅读',
        '完成作业时间','自习时间','课外阅读时间','网络课程时间',
        '实验科研时间','社团活动时间','竞赛活动时间','其他学习时间',
        '同学合作','参与科研团队','参与学科竞赛','学习同学方法','师生交流频度'
    ]

    df = clean_dataframe(df, feature_cols)
    X_pca, chart_data, pca_model = run_pca(df, feature_cols)
    df, result_json, kmeans_model = run_kmeans(X_pca, df)

    # 保存模型（pkl）
    version_manager = ModelVersionManager(settings.machine_learning_models_path)
    version = await version_manager.get_next_version('student_portrait')
    model_path = settings.machine_learning_models_path + f'student_portrait_v{version}.pkl'

    with open(model_path, "wb") as f:
        pickle.dump({
            "pca_model": pca_model,
            "kmeans_model": kmeans_model
        }, f)


    print(f"✅ 模型已保存到 {model_path}")


