import pickle
from datetime import datetime, timezone
from typing import Dict, List, Any, Tuple

import numpy as np
import pandas as pd

from app.analysis.machine_learing.models import ModelVersionManager
from app.core.config import settings


def load_model_sync(model_name: str, version: int = None):
    """
    同步方式加载指定的模型

    :param model_name: 模型名称
    :param version: 模型版本号，如果为 None 则加载最新版本
    :return: 加载的模型对象
    """
    # 创建模型版本管理器
    version_manager = ModelVersionManager(settings.machine_learning_models_path)

    try:
        # 获取模型文件路径
        model_path = version_manager.get_model_path(model_name, version)

        # 加载模型
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        return model
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到模型文件: {model_name} (版本: {version})")
    except Exception as e:
        raise Exception(f"加载模型时出错: {str(e)}")


async def load_model(model_name: str, version: int = None):
    """
    加载指定的模型

    :param model_name: 模型名称
    :param version: 模型版本号，如果为 None 则加载最新版本
    :return: 加载的模型对象
    """
    # 创建模型版本管理器
    version_manager = ModelVersionManager(settings.machine_learning_models_path)

    try:
        # 获取模型文件路径
        model_path = version_manager.get_model_path(model_name, version)

        # 加载模型
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        return model
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到模型文件: {model_name} (版本: {version})")
    except Exception as e:
        raise Exception(f"加载模型时出错: {str(e)}")


def get_pca_model(model_data: Dict[str, Any]):
    """
    获取模型中的PCA模型

    :param model_data: 模型数据
    :return: PCA模型
    """
    return model_data.get("pca_model")


def get_kmeans_model(model_data: Dict[str, Any]):
    """
    获取模型中的KMeans模型

    :param model_data: 模型数据
    :return: KMeans模型
    """
    return model_data.get("kmeans_model")


def clean_input_data(df: pd.DataFrame, feature_cols: List[str]) -> pd.DataFrame:
    """
    清洗输入数据

    :param df: 输入数据
    :param feature_cols: 特征列
    :return: 清洗后的数据
    """
    df_clean = df.copy()
    df_clean = df_clean.map(lambda x: x.strip('\t') if isinstance(x, str) else x)
    df_clean[feature_cols] = df_clean[feature_cols].astype(float)
    return df_clean


def predict_student_persona(model_data: Dict[str, Any], input_data: pd.DataFrame) -> Dict[str, Any]:
    """
    预测学生画像

    :param model_data: 模型数据
    :param input_data: 输入数据
    :return: 预测结果
    """
    # 获取模型组件
    pca_model = get_pca_model(model_data)
    kmeans_model = get_kmeans_model(model_data)
    
    # 定义特征列
    feature_cols = [
        '课前预学','课堂参与','课后复习','延伸阅读',
        '完成作业时间','自习时间','课外阅读时间','网络课程时间',
        '实验科研时间','社团活动时间','竞赛活动时间','其他学习时间',
        '同学合作','参与科研团队','参与学科竞赛','学习同学方法','师生交流频度'
    ]
    
    # 清洗数据
    df_clean = clean_input_data(input_data, feature_cols)
    
    # 标准化（使用PCA模型中的scaler）
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_clean[feature_cols].values)
    
    # PCA降维
    X_pca = pca_model.transform(X_scaled)
    
    # KMeans聚类预测
    cluster_labels = kmeans_model.predict(X_pca)
    
    # 映射学生画像标签
    cluster_mapping = {
        0: "科研学霸型",
        1: "社团活跃型",
        2: "学业挣扎型",
        3: "自主学习型"
    }
    
    persona_labels = [cluster_mapping[label] for label in cluster_labels]
    
    # 构造结果
    result = {
        "cluster_labels": cluster_labels.tolist(),
        "persona_labels": persona_labels,
        "feature_values": {col: df_clean[col].tolist() for col in feature_cols},
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_clusters": kmeans_model.n_clusters,
            "feature_columns": feature_cols
        }
    }
    
    return result


def get_pca_visualization_data(model_data: Dict[str, Any], input_data: pd.DataFrame, n_sample: int = 1000) -> Dict[str, Any]:
    """
    获取PCA可视化数据

    :param model_data: 模型数据
    :param input_data: 输入数据
    :param n_sample: 采样数量
    :return: PCA可视化数据
    """
    # 获取模型组件
    pca_model = get_pca_model(model_data)
    kmeans_model = get_kmeans_model(model_data)
    
    # 定义特征列
    feature_cols = [
        '课前预学','课堂参与','课后复习','延伸阅读',
        '完成作业时间','自习时间','课外阅读时间','网络课程时间',
        '实验科研时间','社团活动时间','竞赛活动时间','其他学习时间',
        '同学合作','参与科研团队','参与学科竞赛','学习同学方法','师生交流频度'
    ]
    
    # 清洗数据
    df_clean = clean_input_data(input_data, feature_cols)
    
    # 标准化
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_clean[feature_cols].values)
    
    # PCA降维
    X_pca = pca_model.transform(X_scaled)
    
    # 预测聚类
    cluster_labels = kmeans_model.predict(X_pca)
    
    # 映射学生画像标签
    cluster_mapping = {
        0: "科研学霸型",
        1: "社团活跃型",
        2: "学业挣扎型",
        3: "自主学习型"
    }
    
    persona_labels = [cluster_mapping[label] for label in cluster_labels]
    
    # 创建2D PCA数据
    pca_2d_df = pd.DataFrame({
        "pc1": X_pca[:, 0],
        "pc2": X_pca[:, 1],
        "student_persona": persona_labels
    })
    
    # 创建3D PCA数据
    pca_3d_df = pd.DataFrame({
        "pc1": X_pca[:, 0],
        "pc2": X_pca[:, 1],
        "pc3": X_pca[:, 2],
        "student_persona": persona_labels
    })
    
    # 采样
    sampled_2d_df = pca_2d_df.sample(n=min(n_sample, len(pca_2d_df)), random_state=42)
    sampled_3d_df = pca_3d_df.sample(n=min(n_sample, len(pca_3d_df)), random_state=42)
    
    return {
        "pca_2d_scatter": sampled_2d_df.to_dict(orient="records"),
        "pca_3d_scatter": sampled_3d_df.to_dict(orient="records"),
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_components": pca_model.n_components_,
            "sample_size": len(sampled_2d_df)
        }
    }


def get_persona_statistics(model_data: Dict[str, Any], input_data: pd.DataFrame) -> Dict[str, Any]:
    """
    获取学生画像统计信息

    :param model_data: 模型数据
    :param input_data: 输入数据
    :return: 统计信息
    """
    # 获取预测结果
    prediction_result = predict_student_persona(model_data, input_data)
    
    # 统计各画像类型的数量
    persona_counts = pd.Series(prediction_result["persona_labels"]).value_counts().to_dict()
    
    # 计算各画像类型的特征均值
    feature_cols = prediction_result["metadata"]["feature_columns"]
    df_clean = clean_input_data(input_data, feature_cols)
    
    persona_means = {}
    for persona_type in persona_counts.keys():
        # 找到对应画像类型的索引
        persona_indices = [i for i, label in enumerate(prediction_result["persona_labels"]) if label == persona_type]
        
        if persona_indices:
            persona_data = df_clean.iloc[persona_indices]
            persona_means[persona_type] = {
                col: float(persona_data[col].mean()) for col in feature_cols
            }
    
    return {
        "persona_counts": persona_counts,
        "persona_means": persona_means,
        "total_samples": len(input_data),
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


def comprehensive_student_portrait_analysis(model_data: Dict[str, Any], input_data: pd.DataFrame) -> Dict[str, Any]:
    """
    综合学生画像分析

    :param model_data: 模型数据
    :param input_data: 输入数据
    :return: 综合分析结果
    """
    # 学生画像预测
    persona_prediction = predict_student_persona(model_data, input_data)
    
    # PCA可视化数据
    pca_visualization = get_pca_visualization_data(model_data, input_data)
    
    # 画像统计信息
    persona_statistics = get_persona_statistics(model_data, input_data)
    
    # 合并结果
    comprehensive_result = {
        "persona_prediction": persona_prediction,
        "pca_visualization": pca_visualization,
        "persona_statistics": persona_statistics,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "comprehensive_student_portrait_analysis"
        }
    }
    
    return comprehensive_result