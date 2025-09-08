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


def get_categories(model_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    获取模型中的分类信息

    :param model_data: 模型数据
    :return: 分类字典
    """
    return model_data.get("categories", {})


def get_feature_columns(model_data: Dict[str, Any]) -> List[str]:
    """
    获取模型中的特征列

    :param model_data: 模型数据
    :return: 特征列列表
    """
    return model_data.get("feature_cols", [])


def get_scaler(model_data: Dict[str, Any]):
    """
    获取模型中的标准化器

    :param model_data: 模型数据
    :return: 标准化器
    """
    return model_data.get("scaler")


def get_pca(model_data: Dict[str, Any]):
    """
    获取模型中的PCA模型

    :param model_data: 模型数据
    :return: PCA模型
    """
    return model_data.get("pca")


def get_kmeans(model_data: Dict[str, Any]):
    """
    获取模型中的KMeans模型

    :param model_data: 模型数据
    :return: KMeans模型
    """
    return model_data.get("kmeans")


def get_random_forest(model_data: Dict[str, Any]):
    """
    获取模型中的随机森林模型

    :param model_data: 模型数据
    :return: 随机森林模型
    """
    return model_data.get("rf_model")


def get_feature_importances(model_data: Dict[str, Any]) -> pd.Series:
    """
    获取模型中的特征重要性

    :param model_data: 模型数据
    :return: 特征重要性
    """
    return model_data.get("feature_importances", pd.Series())


def preprocess_input_data(input_data: pd.DataFrame, categories: Dict[str, List[str]]) -> pd.DataFrame:
    """
    预处理输入数据

    :param input_data: 输入数据
    :param categories: 分类字典
    :return: 预处理后的数据
    """
    df = input_data.copy()
    
    # 计算各类均值
    for cat, cols in categories.items():
        df[cat + '_均值'] = df[cols].mean(axis=1)
    
    return df


def predict_satisfaction_clusters(model_data: Dict[str, Any], input_data: pd.DataFrame) -> Dict[str, Any]:
    """
    预测满意度聚类

    :param model_data: 模型数据
    :param input_data: 输入数据
    :return: 预测结果
    """
    # 获取模型组件
    categories = get_categories(model_data)
    feature_cols = get_feature_columns(model_data)
    scaler = get_scaler(model_data)
    pca = get_pca(model_data)
    kmeans = get_kmeans(model_data)
    
    # 预处理数据
    df = preprocess_input_data(input_data, categories)
    
    # 标准化
    X_scaled = scaler.transform(df[feature_cols])
    
    # PCA降维
    X_pca = pca.transform(X_scaled)
    
    # 聚类预测
    cluster_labels = kmeans.predict(X_pca)
    
    # 构造结果
    result = {
        "cluster_labels": cluster_labels.tolist(),
        "category_means": {col: df[col].tolist() for col in feature_cols},
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n_clusters": kmeans.n_clusters,
            "feature_columns": feature_cols
        }
    }
    
    return result


def analyze_feature_importance(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    分析特征重要性

    :param model_data: 模型数据
    :return: 特征重要性分析结果
    """
    feature_importances = get_feature_importances(model_data)
    
    # 转换为字典格式
    importance_dict = feature_importances.to_dict()
    
    # 排序特征重要性
    sorted_importance = dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    return {
        "feature_importances": sorted_importance,
        "top_features": list(sorted_importance.keys())[:10],  # 前10个重要特征
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


def get_cluster_analysis(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取聚类分析结果

    :param model_data: 模型数据
    :return: 聚类分析结果
    """
    dataframe = model_data.get("dataframe", pd.DataFrame())
    kmeans = get_kmeans(model_data)
    
    if '群体类别' not in dataframe.columns:
        return {"error": "未找到群体类别列"}
    
    # 统计每个聚类的样本数量
    cluster_counts = dataframe['群体类别'].value_counts().to_dict()
    
    # 计算每个聚类的特征均值
    feature_cols = get_feature_columns(model_data)
    cluster_means = {}
    
    for cluster_id in sorted(cluster_counts.keys()):
        cluster_data = dataframe[dataframe['群体类别'] == cluster_id]
        cluster_means[f"cluster_{cluster_id}"] = {
            col: float(cluster_data[col].mean()) for col in feature_cols
        }
    
    return {
        "cluster_counts": cluster_counts,
        "cluster_means": cluster_means,
        "n_clusters": kmeans.n_clusters,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


def comprehensive_satisfaction_analysis(model_data: Dict[str, Any], input_data: pd.DataFrame) -> Dict[str, Any]:
    """
    综合满意度分析

    :param model_data: 模型数据
    :param input_data: 输入数据
    :return: 综合分析结果
    """

    # 聚类预测
    cluster_result = predict_satisfaction_clusters(model_data, input_data)
    
    # 特征重要性分析
    importance_result = analyze_feature_importance(model_data)
    
    # 聚类分析
    cluster_analysis = get_cluster_analysis(model_data)
    
    # 合并结果
    comprehensive_result = {
        "cluster_prediction": cluster_result,
        "feature_importance": importance_result,
        "cluster_analysis": cluster_analysis,
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_type": "comprehensive_satisfaction_analysis"
        }
    }
    
    return comprehensive_result