import pickle
from datetime import datetime, timezone

import pandas as pd

from app.analysis.machine_learing.models import ModelVersionManager
from app.core.config import settings
from app.analysis.machine_learing.trainers.what_if_decision_simulator_lgbmclassfier import preprocess, normalize, pick_up_features
from app.schemas.what_if_decision_simulator import (
    WhatIfInput,
    WhatIfOutput,
    ClassProbability,
    PredictionOutput,
    FeaturesOutput,
)
from app.utils.model_cache import cached_model_load


def load_model_sync(model_name: str, task_id: str, version: int = None):
    """
    同步方式加载指定的模型

    :param task_id: 分析任务id
    :param model_name: 模型名称
    :param version: 模型版本号，如果为 None 则加载最新版本
    :return: 加载的模型对象
    """
    # 创建模型版本管理器
    version_manager = ModelVersionManager(settings.machine_learning_models_path)

    try:
        # 获取模型文件路径
        model_path = version_manager.get_model_path_by_taskid(model_name, task_id, version)

        # 加载模型
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        return model
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到模型文件: {model_name} (版本: {version})")
    except Exception as e:
        raise Exception(f"加载模型时出错: {str(e)}")

@cached_model_load(expire_time=1800)
async def load_model(model_name: str, task_id: str, version: int = None):
    """
    加载指定的模型

    :param task_id: 分析任务id
    :param model_name: 模型名称
    :param version: 模型版本号，如果为 None 则加载最新版本
    :return: 加载的模型对象
    """
    # 创建模型版本管理器
    version_manager = ModelVersionManager(settings.machine_learning_models_path)

    try:
        # 获取模型文件路径
        model_path = version_manager.get_model_path_by_taskid(model_name, task_id, version)

        # 加载模型
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        return model
    except FileNotFoundError:
        raise FileNotFoundError(f"找不到模型文件: {model_name} (版本: {version})")
    except Exception as e:
        raise Exception(f"加载模型时出错: {str(e)}")

def send_feature_importance(df: pd.DataFrame, y: pd.Series, score: float):
    df_copy = df.copy()
    df_copy = preprocess(df_copy)
    df_copy = normalize(df_copy)
    _, _, features = pick_up_features(df_copy, y, score)
    features_with_rank = []
    for feature in features:
        unique_count = df_copy[feature].nunique()
        features_with_rank.append(
            FeaturesOutput(
                feature_classes=unique_count,
                feature_name=feature
            )
        )
    return features_with_rank

def what_if_simulation(model, input_data: WhatIfInput) -> WhatIfOutput:
    # 1. 构造输入特征 DataFrame
    df_input = pd.DataFrame([input_data.features])

    # 2. 预测概率
    raw_probs = model.predict_proba(df_input)
    class_labels = model.classes_
    prob_dict = {f"{c}": prob for c, prob in zip(class_labels, raw_probs[0])}

    # 3. 排序 Top-K
    top_k = 3
    sorted_probs = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
    top_k_list = [
        ClassProbability(class_label=k.split('_')[1], probability=v)
        for k, v in sorted_probs[:top_k]
    ]

    # 5. 构造输出结构
    return WhatIfOutput(
        prediction=PredictionOutput(
            predicted_class=int(model.predict(df_input)[0]),
            probabilities=prob_dict,
            top_k_classes=top_k_list
        ),
        metadata={
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )