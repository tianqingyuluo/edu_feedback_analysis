from typing import Any

from pydantic import BaseModel

class WhatIfInput(BaseModel):
    """
    whatif决策模拟器的前端输入数据模型
    """
    features: dict[str, Any] # 特征名称 -> 特征值

class ClassProbability(BaseModel):
    """
    预测某一类别的概率
    """
    class_label: str
    probability: float

class PredictionOutput(BaseModel):
    """
    whatif决策模拟器后端输出数据模型
    """
    predicted_class: int
    probabilities: dict[str, float]
    top_k_classes: list[ClassProbability]  # 前k个最有可能的满意等级的概率

class WhatIfOutput(BaseModel):
    prediction: PredictionOutput
    metadata: dict[str, Any]