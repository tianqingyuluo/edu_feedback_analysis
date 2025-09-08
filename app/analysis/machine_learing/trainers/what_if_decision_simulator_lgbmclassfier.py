import asyncio
import pickle
from concurrent.futures.thread import ThreadPoolExecutor
from lightgbm import LGBMClassifier
from sklearn.feature_selection import SelectKBest, mutual_info_classif
import pandas as pd
import numpy as np
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import TomekLinks
from sklearn.model_selection import StratifiedShuffleSplit, cross_val_score
import lightgbm as lgb
import optuna
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score

from app.core.logging import app_logger
from app.core.config import settings
from app.analysis.machine_learing.models import ModelVersionManager

def preprocess(X):
    """去除文字列"""
    X = X.iloc[:, 5:]
    return X

def normalize(X):
    """去归一化"""
    for col in X.columns:
        scaler = len(np.unique(X[col]))-1
        if scaler == 1: # 去除二元选择器
            X.drop(col, axis=1, inplace=True)
            continue
        temp: pd.Series = X[col]
        X[col] = temp.multiply(scaler).astype(int)
    return X

def pick_up_features(X: pd.DataFrame, y: pd.Series, score: float) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """
    自动根据传入的目标指标筛选相关的关系最近n条指标（相关度阈值）

    :param X: 经过统一初始处理过的dataframe
    :param y: 选择预测的列
    :param score: 相关度阈值
    :return:
    """
    # X = X.iloc[:, 5:]
    # X = X.loc[:,X.max()<=1] # 筛选掉非离散变量
    # for col in X.columns:
    #     scaler = len(np.unique(X[col]))-1
    #     if scaler == 1: # 去除二元选择器
    #         X.drop(col, axis=1, inplace=True)
    #         continue
    #     temp: pd.Series = X[col]
    #     X[col] = temp.multiply(scaler).astype(int)
    try:
        X.drop(y.name, axis=1, inplace=True)
    except Exception:
        app_logger.warn(f"在训练whatif决策器模型时发生问题：没有该列: {y.name}")
    y = y.multiply(len(np.unique(y)-1)).astype(int)

    # 互信息算法
    selector_mi = SelectKBest(score_func=mutual_info_classif, k='all')
    selector_mi.fit_transform(X, y)

    mi_scores = pd.DataFrame({
        'feature': X.columns,
        'mutual_info_score': selector_mi.scores_
    }).sort_values('mutual_info_score', ascending=False)

    selected_features = mi_scores[mi_scores['mutual_info_score'] >= score]['feature'].tolist()

    X = X[selected_features]

    return X, y, selected_features

def training_with_EMOTE_bayes_search(X, y) -> LGBMClassifier:
    """
    使用EMOTE进行过采样，并使用贝叶斯搜索进行超参数优化

    :param X: 训练集特征
    :param y: 训练集标签
    :return:
    """
    sss = StratifiedShuffleSplit(n_splits=1, test_size=0.2, random_state=42)

    # 分割数据
    for train_index, test_index in sss.split(X, y):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    pipeline = Pipeline([
    ('smote', SMOTE(sampling_strategy={ 1: 200, 2: 800}, random_state=42)),
    ('tomek', TomekLinks())  # 在过采样后再应用Tomek
    ])
    X_resampled, y_resampled = pipeline.fit_resample(X_train, y_train)

    base_params = {
            # 'device': 'gpu',
            # 'gpu_platform_id': 0,
            # 'gpu_device_id': 0,
            'objective': 'multiclass',
            'num_class': len(np.unique(y.values)),
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'verbose': -1,
        }

    # 定义贝叶斯优化目标函数
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 30, 300),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'num_leaves': trial.suggest_int('num_leaves', 20, 150),
            'max_depth': trial.suggest_int('max_depth', 2, 12),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-3, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-3, 10.0, log=True),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 50),
            'min_child_weight': trial.suggest_float('min_child_weight', 1e-4, 0.1, log=True),
        }

        all_params = {**base_params, **params}
        lgb_model = lgb.LGBMClassifier(**all_params)

        # 分层k折验证
        stratified_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        scores = cross_val_score(lgb_model, X_resampled, y_resampled, cv=stratified_cv, scoring='f1_macro')

        return np.mean(scores)

    study = optuna.study.create_study(
        direction='maximize',  # 最大化准确率
        sampler=optuna.samplers.TPESampler(seed=42)  # 使用TPE采样器
    )
    app_logger.info("开始贝叶斯优化...")
    study.optimize(objective, n_trials=100)  # 100次试验
    # 输出最佳结果
    app_logger.info("\n优化完成")
    app_logger.info("最佳分数:", study.best_value)
    app_logger.info("最佳参数:", study.best_params)

    # 用最佳参数训练最终模型
    best_params = {**base_params, **study.best_params}
    final_model = lgb.LGBMClassifier(**best_params)

    # 添加早停训练
    final_model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        callbacks=[
            lgb.early_stopping(stopping_rounds=30, verbose=True),
            lgb.log_evaluation(50)
        ]
    )

    # 最终评估
    y_pred = final_model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    app_logger.info(f"\n 最终测试集准确率: {test_accuracy:.4f}")

    # 分析模型特征重要性
    feature_importance = final_model.feature_importances_
    feature_names = X_train.columns if hasattr(X_train, 'columns') else range(X_train.shape[1])

    # 排序并显示最重要的特征
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': feature_importance
    }).sort_values('importance', ascending=False)

    app_logger.info("Top 20重要特征:")
    app_logger.info(importance_df.head(20))

    # 绘制学习曲线
    lgb.plot_metric(final_model)

    return final_model

def train(X: pd.DataFrame, y: pd.Series, score: float) -> LGBMClassifier:
    """
    开始训练
    :param X: 总数据集
    :param y: 目标指标
    :return: 训练好的lgb分类器
    """
    X = preprocess(X)
    X = normalize(X)
    X, y , _ = pick_up_features(X, y, score)
    model = training_with_EMOTE_bayes_search(X, y)

    return model

async def async_train(X: pd.DataFrame, y: pd.Series, score: float) -> LGBMClassifier:
    """
    开始训练
    :param X: 总数据集
    :param y: 目标指标
    :return: 训练好的lgb分类器
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as executor:
        model = await loop.run_in_executor(executor, train, X, y, score)

    version_manager = ModelVersionManager(settings.machine_learning_models_path)
    version = await version_manager.get_next_version('what-if_decision_simulator_LGBMClassfier')
    path = settings.machine_learning_models_path + f'what-if_decision_simulator_LGBMClassfier_v{version}'

    def save_model_sync():
        with open(str(path), 'wb') as f:
            pickle.dump(model, f)

    await loop.run_in_executor(None, save_model_sync)

    app_logger.info(f"模型已经保存到：{settings.machine_learning_models_path/'what-if_decision_simulator_LGBMClassfier'}")