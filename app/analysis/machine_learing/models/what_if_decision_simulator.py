import pickle
from datetime import datetime, timezone

import pandas as pd

from app.analysis.machine_learing.models import ModelVersionManager
from app.core.config import settings
from app.schemas.what_if_decision_simulator import (
    WhatIfInput,
    WhatIfOutput,
    ClassProbability,
    PredictionOutput,
)


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