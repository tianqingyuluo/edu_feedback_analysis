import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd
import pickle
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import app_logger
from app.analysis.machine_learing.models import ModelVersionManager
from app.analysis.machine_learing.trainers import (
    what_if_decision_simulator_lgbmclassfier as wi_trainer,
)
from app.analysis import statistical
from app.db.models.analysis import (
    AnalysisTask,
    GroupComparisonRadarChartData,
    TeacherStudentInteractionBubbleChartData,
    StudentTimeAllocationPieChartData,
    CorrelationBasedEHIBuilderData,
    CorrelationBasedRPIBuilderData,
    AcademicMaturityProcessorData,
    SatisfactionPartData,
    SatisfactionWholeData,
    StudentPortraitData,
    StudentSatisfactionRouteSankeyChartData
)
from app.service.analysis_service import AnalysisService
from app.service.analysis_summary_rag_service import AnalysisSummaryRAGService
from app.enum.enums import AnalysisStatusEnum


class AnalysisTaskManager:
    """分析任务管理器 - 统一管理模型训练、预测和统计分析"""

    def __init__(self, output_dir: str = None):
        """
        初始化分析任务管理器

        Args:
            output_dir: 输出目录，如果为None则使用配置中的默认路径
        """
        self.output_dir = (
            Path(output_dir)
            if output_dir
            else Path(settings.machine_learning_models_path)
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 模型版本管理器
        self.version_manager = ModelVersionManager(str(self.output_dir))

        self.analysis_service = AnalysisService()
        
        # 分析总结服务
        self.summary_service = AnalysisSummaryRAGService()

        # 支持的模型类型
        self.supported_models = {
            # "satisfaction_part": {
            #     "trainer": sp_trainer.async_train,
            #     "requires_target": False,
            #     "description": "部分满意度分析模型",
            # },
            # "satisfaction_whole": {
            #     "trainer": sw_trainer.async_train,
            #     "requires_target": False,
            #     "description": "整体满意度分析模型",
            # },
            # "student_portrait": {
            #     "trainer": stup_trainer.async_train,
            #     "requires_target": False,
            #     "description": "学生画像分析模型",
            # },
            "what_if_decision_simulator": {
                "trainer": wi_trainer.async_train,
                "requires_target": True,
                "description": "What-If决策模拟器",
            },
        }

        # 支持的统计分析类型
        self.supported_analyses = {
            "group_comparison_radar_chart": {
                "function": statistical.create_radar_echarts_json,
                "description": "雷达图分析",
            },
            "teacher_student_interaction_bubble_chart": {
                "function": statistical.create_bubble_echarts_json,
                "description": "师生互动气泡图分析",
            },
            "student_time_allocation_pie_chart": {
                "function": statistical.build_academy_array,
                "description": "学生时间分配饼图分析",
            },
            "academic_maturity_by_grade_aggregator": {
                "function": statistical.process_maturity_to_json,
                "description": "学术成熟度按年级聚合折线图分析",
            },
            "correlation_based_EHI_builder": {
                "function": statistical.DataProcessor.process_dataframe_to_json,
                "description": "基于EHI的关联性分析仪表盘+雷达图",
            },
            "correlation_based_RPI_builder": {
                "function": statistical.RPIProcessor.process_dataframe_to_json,
                "description": "基于RPI的关联性分析仪表盘+雷达图+热力图",
            },
            "student_portrait_chart": {
                "function": statistical.analyze_student_persona,
                "description": "学生画像分析",
            },
            "satisfaction_part_chart": {
                "function": statistical.analyze_feedback_satisfaction,
                "description": "部分满意度分析",
            },
            "satisfaction_whole_chart": {
                "function": statistical.analyze_feedback,
                "description": "整体满意度分析",
            },
            "student_satisfaction_route_sankey_chart": {
                "function": statistical.analysis,
                "description": "学生满意度路线图分析"
            }
        }

        # 用来存储各个分析项和对应的数据库记录的映射
        self.db_map = {
            "satisfaction_part_chart" : SatisfactionPartData,
            "satisfaction_whole_chart" : SatisfactionWholeData,
            "student_portrait_chart" : StudentPortraitData,
            "group_comparison_radar_chart" : GroupComparisonRadarChartData,
            "teacher_student_interaction_bubble_chart" : TeacherStudentInteractionBubbleChartData,
            "student_time_allocation_pie_chart" : StudentTimeAllocationPieChartData,
            "correlation_based_EHI_builder" :CorrelationBasedEHIBuilderData,
            "correlation_based_RPI_builder" : CorrelationBasedRPIBuilderData,
            "academic_maturity_by_grade_aggregator" : AcademicMaturityProcessorData,
            "student_satisfaction_route_sankey_chart" : StudentSatisfactionRouteSankeyChartData,
        }

    async def create_analysis_task(
        self,
        data_id: int,
        db: AsyncSession,
        models_to_train: List[str] = None,
        analyses_to_run: List[str] = None,
        target_column: str = "学校整体满意度",
        feature_score_threshold: float = 0.16,

    ) -> AnalysisTask:
        """
        创建分析任务（仅创建任务记录，不执行分析）

        Args:
            data_id: 数据ID
            models_to_train: 要训练的模型列表，如果为None则训练所有模型
            analyses_to_run: 要运行的统计分析列表，如果为None则运行所有分析
            target_column: 目标列名（仅what_if模型需要）
            feature_score_threshold: 特征选择分数阈值（仅what_if模型需要）

        Returns:
            创建的分析任务对象
        """
        # 创建任务记录
        # new_task = AnalysisTask(
        #     data_id=data_id,
        #     status=AnalysisStatusEnum.PENDING.value(),
        #     summary="",
        # )
        task = await self.analysis_service.create_analysis_task(data_id, db)

        # 保存任务配置
        task_config = {
            "models_to_train": models_to_train if models_to_train else list(self.supported_models.keys()),
            "analyses_to_run": analyses_to_run if analyses_to_run else list(self.supported_analyses.keys()),
            "target_column": target_column,
            "feature_score_threshold": feature_score_threshold,
            "description": "",
        }

        # 创建任务目录
        task_id = str(task.id)
        task_dir = self.output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # 保存任务配置
        config_file = task_dir / "config.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(task_config, f, ensure_ascii=False, indent=2, default=str)

        app_logger.info(f"创建分析任务: {task_id}")
        return task

    async def execute_analysis_task(
        self,
        task_id: str,
        data: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        执行分析任务（训练模型并运行统计分析）

        Args:
            task_id: 任务ID
            data: 输入数据

        Returns:
            任务结果字典
        """
        task_dir = self.output_dir / task_id
        if not task_dir.exists():
            raise FileNotFoundError(f"任务目录不存在: {task_id}")

        # 加载任务配置
        config_file = task_dir / "config.json"
        if not config_file.exists():
            raise FileNotFoundError(f"任务配置文件不存在: {config_file}")

        with open(config_file, "r", encoding="utf-8") as f:
            task_config = json.load(f)

        # 记录任务信息
        task_info = {
            "task_id": task_id,
            "description": task_config.get("description"),
            "created_at": datetime.now().isoformat(),
            "status": AnalysisStatusEnum.PROCESSING.value,
            "models_trained": [],
            "analyses_completed": [],
            "output_dir": str(task_dir),
        }

        try:
            # 1. 训练模型
            models_to_train = task_config.get("models_to_train", [])
            model_results = {}
            
            for model_name in models_to_train:
                if model_name not in self.supported_models:
                    app_logger.warning(f"不支持的模型类型: {model_name}")
                    continue

                app_logger.info(f"开始训练模型: {model_name}")
                model_config = self.supported_models[model_name]

                try:
                    if model_name == "what_if_decision_simulator":
                        # what_if模型需要目标列
                        target_column = task_config.get("target_column")
                        if target_column is None:
                            raise ValueError(
                                "what_if_decision_simulator模型需要指定target_column"
                            )

                        if target_column not in data.columns:
                            raise ValueError(f"数据中找不到目标列: {target_column}")

                        y = data[target_column]
                        feature_score_threshold = task_config.get("feature_score_threshold", 0.1)
                        model_result = await model_config["trainer"](
                            data, y, feature_score_threshold, task_id
                        )
                    else:
                        # 其他模型只需要数据
                        model_result = await model_config["trainer"](data)

                    model_results[model_name] = {
                        "status": "success",
                        "message": f"模型 {model_name} 训练成功",
                    }
                    task_info["models_trained"].append(model_name)

                    app_logger.info(f"模型 {model_name} 训练完成")

                except Exception as e:
                    model_results[model_name] = {
                        "status": "failed",
                        "message": f"模型 {model_name} 训练失败: {str(e)}",
                    }
                    app_logger.error(f"模型 {model_name} 训练失败: {str(e)}")

            # 2. 运行统计分析
            analyses_to_run = task_config.get("analyses_to_run", [])
            analysis_results = {}
            
            for analysis_name in analyses_to_run:
                if analysis_name not in self.supported_analyses:
                    app_logger.warning(f"不支持的统计分析类型: {analysis_name}")
                    continue

                app_logger.info(f"开始运行统计分析: {analysis_name}")
                analysis_config = self.supported_analyses[analysis_name]

                try:
                    analysis_result = analysis_config["function"](data)
                    analysis_results[analysis_name] = {
                        "status": "success",
                        "result": analysis_result,
                    }
                    task_info["analyses_completed"].append(analysis_name)

                    app_logger.info(f"统计分析 {analysis_name} 完成")

                except Exception as e:
                    analysis_results[analysis_name] = {
                        "status": "failed",
                        "message": f"统计分析 {analysis_name} 运行失败: {str(e)}",
                    }
                    app_logger.error(f"统计分析 {analysis_name} 运行失败: {str(e)}")

            # 3. 保存任务结果
            task_info["status"] = AnalysisStatusEnum.COMPLETED.value
            task_info["completed_at"] = datetime.now().isoformat()

            results = {
                "task_info": task_info,
                "model_results": model_results,
                "analysis_results": analysis_results,
            }

            # 保存结果到文件
            results_file = task_dir / "results.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)

            app_logger.info(f"分析任务 {task_id} 完成")
            return results

        except Exception as e:
            task_info["status"] = "failed"
            task_info["error"] = str(e)
            task_info["failed_at"] = datetime.now().isoformat()

            app_logger.error(f"分析任务 {task_id} 失败: {str(e)}")

            # 保存失败结果
            results = {"task_info": task_info, "error": str(e)}

            results_file = task_dir / "results.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)

            return results

    async def generate_comprehensive_analysis(
        self,
        task_id: str,
        db: AsyncSession,
        input_data: pd.DataFrame = None,
        model_versions: Dict[str, int] = None,
    ) -> Dict[str, Any]:
        """
        生成综合分析报告，包括所有模型的预测结果和统计分析

        Args:
            task_id: 任务ID
            input_data: 输入数据（用于模型预测），如果为None则使用任务原始数据
            model_versions: 指定模型版本，如果为None则使用最新版本

        Returns:
            综合分析结果
        """
        task_dir = self.output_dir / task_id
        if not task_dir.exists():
            raise FileNotFoundError(f"任务目录不存在: {task_dir}")

        # 加载任务信息
        results_file = task_dir / "results.json"
        if not results_file.exists():
            raise FileNotFoundError(f"任务结果文件不存在: {results_file}")

        with open(results_file, "r", encoding="utf-8") as f:
            task_results = json.load(f)

        task_info = task_results["task_info"]

        app_logger.info(f"开始生成综合分析报告: {task_id}")

        comprehensive_results = {
            "task_id": task_id,
            "generated_at": datetime.now().isoformat(),
            "model_predictions": {},
            "statistical_analyses": {},
            "comments": {},
        }

        try:
            # 1. 加载模型并进行预测
            trained_models = task_info.get("models_trained", [])

            for model_name in trained_models:
                if model_name == "what_if_decision_simulator":
                    # what_if模型是特殊处理，不在这里进行预测
                    continue

                app_logger.info(f"加载模型并进行预测: {model_name}")

                try:
                    # 加载模型
                    version = model_versions.get(model_name) if model_versions else None


                    model_data = await self._load_model_data(model_name, version)

                    # 进行预测
                    if model_name == "satisfaction_part":
                        from app.analysis.machine_learing.models.satisfaction_part import (
                            get_satisfaction_summary,
                        )

                        prediction_result = get_satisfaction_summary(
                            model_data
                        )
                    elif model_name == "satisfaction_whole":
                        from app.analysis.machine_learing.models.satisfaction_whole import (
                            comprehensive_satisfaction_analysis,
                        )

                        prediction_result = comprehensive_satisfaction_analysis(
                            model_data, input_data
                        )
                    elif model_name == "student_portrait":
                        from app.analysis.machine_learing.models.student_portrait import (
                            comprehensive_student_portrait_analysis,
                        )

                        prediction_result = comprehensive_student_portrait_analysis(
                            model_data, input_data
                        )
                    else:
                        prediction_result = {"error": f"未知的模型类型: {model_name}"}

                    # 调用LLM来给模型结果进行总结
                    comment = self.summary_service.summarize_model_prediction(model_name, prediction_result)
                    prediction_result["comment"] = comment

                    task_data = self.db_map[model_name](
                        task_id= int(task_id),
                        data= prediction_result,
                        comment=comment,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(task_data)
                    await db.commit()

                    comprehensive_results["model_predictions"][model_name] = (
                        prediction_result
                    )
                    comprehensive_results['comments'][model_name] = comment

                    app_logger.info(f"模型 {model_name} 预测完成")

                except Exception as e:
                    comprehensive_results["model_predictions"][model_name] = {
                        "error": f"模型 {model_name} 预测失败: {str(e)}"
                    }
                    app_logger.error(f"模型 {model_name} 预测失败: {str(e)}")
                    app_logger.error(traceback.format_exc())

            # 2. 重新运行统计分析（如果提供了新的输入数据）
            if input_data is not None:
                completed_analyses = task_info.get("analyses_completed", [])

                for analysis_name in completed_analyses:
                    if analysis_name not in self.supported_analyses:
                        continue

                    app_logger.info(f"重新运行统计分析: {analysis_name}")

                    try:
                        analysis_config = self.supported_analyses[analysis_name]
                        analysis_result = analysis_config["function"](input_data)
                        comprehensive_results["statistical_analyses"][analysis_name] = (
                            analysis_result
                        )

                        app_logger.info(f"统计分析 {analysis_name} 完成")

                    except Exception as e:
                        comprehensive_results["statistical_analyses"][analysis_name] = {
                            "error": f"统计分析 {analysis_name} 运行失败: {str(e)}"
                        }
                        app_logger.error(f"统计分析 {analysis_name} 运行失败: {str(e)}")

            else:
                analysis_result = task_results.get("analysis_results", {})
                for analysis_name, analysis_data in analysis_result.items():
                    comprehensive_results["statistical_analyses"][analysis_name] = (
                        analysis_data.get("result", {})
                    )
                    # 生成统计分析的AI总结
                    analysis_comment = self.summary_service.summarize_statistical_analysis(analysis_name, analysis_data.get("result", {}))
                    comprehensive_results['comments'][analysis_name] = analysis_comment

                    task_data = self.db_map[analysis_name](
                        task_id= int(task_id),
                        data= analysis_data.get("result", {}),
                        comment=analysis_comment,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(task_data)
                    await db.commit()

            # 3. 保存综合分析结果
            comprehensive_file = task_dir / "comprehensive_analysis.json"
            with open(comprehensive_file, "w", encoding="utf-8") as f:
                json.dump(
                    comprehensive_results, f, ensure_ascii=False, indent=2, default=str
                )

            app_logger.info(f"综合分析报告生成完成: {task_id}")
            return comprehensive_results

        except Exception as e:
            app_logger.error(f"生成综合分析报告失败: {str(e)}")
            app_logger.error(traceback.format_exc())
            return {
                "task_id": task_id,
                "error": f"生成综合分析报告失败: {str(e)}",
                "generated_at": datetime.now().isoformat(),
            }

    async def _load_model_data(
        self, model_name: str, version: int = None
    ) -> Dict[str, Any]:
        """
        加载模型数据

        Args:
            model_name: 模型名称
            version: 模型版本，如果为None则加载最新版本

        Returns:
            模型数据字典
        """
        # 获取模型文件路径
        model_path = self.version_manager.get_model_path(model_name, version)
        app_logger.info(f"模型文件路径: {model_path}")

        # 加载模型
        with open(model_path, "rb") as f:
            model_data = pickle.load(f)

        return model_data.get("model_data", model_data)

    def load_what_if_model_for_prediction(self, model_name: str, version: int = None):
        """
        加载What-If决策模拟器模型（仅在预测时调用）

        Args:
            model_name: 模型名称
            version: 模型版本，如果为None则加载最新版本

        Returns:
            加载的模型对象
        """
        app_logger.info(f"加载What-If决策模拟器模型: {model_name}")

        # 获取模型文件路径
        model_path = self.version_manager.get_model_path(model_name, version)

        # 加载模型
        with open(model_path, "rb") as f:
            model = pickle.load(f)

        app_logger.info(f"What-If决策模拟器模型加载完成: {model_name}")
        return model

    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        列出所有分析任务

        Returns:
            任务列表
        """
        tasks = []

        for task_dir in self.output_dir.iterdir():
            if not task_dir.is_dir():
                continue

            results_file = task_dir / "results.json"
            if not results_file.exists():
                continue

            try:
                with open(results_file, "r", encoding="utf-8") as f:
                    task_results = json.load(f)

                task_info = task_results.get("task_info", {})
                tasks.append(
                    {
                        "task_id": task_info.get("task_id"),
                        "task_name": task_info.get("task_name"),
                        "status": task_info.get("status"),
                        "created_at": task_info.get("created_at"),
                        "completed_at": task_info.get("completed_at"),
                        "models_trained": task_info.get("models_trained", []),
                        "analyses_completed": task_info.get("analyses_completed", []),
                    }
                )
            except Exception as e:
                app_logger.error(f"读取任务信息失败: {task_dir}, 错误: {str(e)}")

        return sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_task_results(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务结果

        Args:
            task_id: 任务ID

        Returns:
            任务结果
        """
        task_dir = self.output_dir / task_id
        if not task_dir.exists():
            raise FileNotFoundError(f"任务目录不存在: {task_id}")

        results_file = task_dir / "results.json"
        if not results_file.exists():
            raise FileNotFoundError(f"任务结果文件不存在: {task_id}")

        with open(results_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_comprehensive_analysis(self, task_id: str) -> Dict[str, Any]:
        """
        获取综合分析报告

        Args:
            task_id: 任务ID

        Returns:
            综合分析结果
        """
        task_dir = self.output_dir / task_id
        if not task_dir.exists():
            raise FileNotFoundError(f"任务目录不存在: {task_id}")

        comprehensive_file = task_dir / "comprehensive_analysis.json"
        if not comprehensive_file.exists():
            raise FileNotFoundError(f"综合分析报告文件不存在: {task_id}")

        with open(comprehensive_file, "r", encoding="utf-8") as f:
            return json.load(f)
