import pickle
from datetime import datetime, timezone
from typing import Dict, List, Any

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


def get_correlation_matrix(model_data: Dict[str, Any]) -> pd.DataFrame:
    """
    获取模型中的相关系数矩阵

    :param model_data: 模型数据
    :return: 相关系数矩阵
    """
    return model_data.get("correlation", pd.DataFrame())


def calculate_satisfaction_level(value: float) -> str:
    """
    根据数值计算满意度等级

    :param value: 满意度数值
    :return: 满意度等级
    """
    if value >= 0.9:
        return "满意"
    elif value >= 0.75:
        return "较满意"
    elif value >= 0.6:
        return "一般"
    elif value >= 0.4:
        return "较不满意"
    else:
        return "不满意"


def analyze_satisfaction_part(model_data: Dict[str, Any], input_data: pd.DataFrame) -> Dict[str, Any]:
    """
    分析部分满意度数据

    :param model_data: 模型数据
    :param input_data: 输入数据
    :return: 分析结果
    """
    # 获取分类信息
    categories = get_categories(model_data)
    
    # 计算各类均值
    df = input_data.copy()
    for cat, cols in categories.items():
        df[cat + '_均值'] = df[cols].mean(axis=1)
    
    # 获取特征列
    feature_cols = get_feature_columns(model_data)
    
    # 应用满意度映射
    for col in feature_cols:
        df[col + "_等级"] = df[col].apply(calculate_satisfaction_level)
    
    # 计算相关系数
    corr = df[feature_cols].corr()
    
    # 构造结果
    result = {
        "category_means": {col: df[col].tolist() for col in feature_cols},
        "satisfaction_levels": {col + "_等级": df[col + "_等级"].tolist() for col in feature_cols},
        "correlation_matrix": corr.to_dict(),
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "categories": categories,
            "feature_columns": feature_cols
        }
    }
    
    return result


def get_satisfaction_summary(model_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    获取满意度分析摘要

    :param model_data: 模型数据
    :return: 摘要信息
    """
    categories = get_categories(model_data)
    feature_cols = get_feature_columns(model_data)
    correlation_matrix = get_correlation_matrix(model_data)
    
    # 计算每个类别的平均满意度等级
    dataframe = model_data.get("dataframe", pd.DataFrame())
    
    summary = {}
    for col in feature_cols:
        if col in dataframe.columns:
            avg_value = dataframe[col].mean()
            satisfaction_level = calculate_satisfaction_level(avg_value)
            summary[col] = {
                "average_value": float(avg_value),
                "satisfaction_level": satisfaction_level
            }
    
    return {
        "summary": summary,
        "categories": categories,
        "feature_count": len(feature_cols),
        "metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }