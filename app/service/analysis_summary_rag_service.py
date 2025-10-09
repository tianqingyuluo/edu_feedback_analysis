import json
from typing import Dict, Any, Optional
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from app.rag.model.chat_model import get_chat_model
from app.core.logging import app_logger

class AnalysisSummaryRAGService:
    """
    专门用于分析结果总结的RAG服务类
    """
    
    def __init__(self):
        self.llm = get_chat_model(streaming=False)
        self._init_prompt_templates()
    
    def _init_prompt_templates(self):
        """初始化各种分析类型的提示词模板"""
        # 模型预测结果总结模板
        self.model_prediction_template = """
        你是一位教育数据分析专家，请对以下模型预测结果进行专业总结：

        分析类型：{analysis_type}
        预测结果数据：{prediction_data}

        请提供以下内容的总结：
        1. 关键发现和洞察
        2. 数据的主要趋势和模式
        3. 对教育实践的启示和建议
        4. 需要进一步关注的问题

        请确保总结内容：
- 专业准确，基于数据分析结果
- 简洁明了，避免技术术语过多
- 具有实践指导意义
- 字数控制在200-300字之间

        总结：
        """
        
        # 统计分析结果总结模板
        self.statistical_analysis_template = """
        你是一位教育统计分析专家，请对以下统计分析结果进行专业总结：

        分析类型：{analysis_type}
        统计分析数据：{analysis_data}

        请提供以下内容的总结：
        1. 统计分析的主要发现
        2. 数据间的关系和模式
        3. 对教育管理决策的指导意义
        4. 潜在的问题和改进方向

        请确保总结内容：
- 基于统计分析结果，客观准确
- 突出教育管理价值
- 提供可操作的建议
- 字数控制在200-300字之间

        总结：
        """
        
        # 综合分析总结模板
        self.comprehensive_template = """
        作为教育分析综合性专家，请对以下综合分析报告进行高层次总结：

        分析任务ID：{task_id}
        模型预测结果：{model_predictions}
        统计分析结果：{statistical_analyses}

        请提供一个综合性的分析总结，包括：
        1. 整体分析概况和主要发现
        2. 各项分析结果的关联性和一致性
        3. 对教育质量提升的综合性建议
        4. 未来数据分析的重点方向

        要求：
- 高度概括，突出重点
- 体现系统性思维
- 具有战略指导价值
- 字数控制在300-400字之间

        综合总结：
        """
    
    def summarize_model_prediction(self, analysis_type: str, prediction_data: Dict[str, Any]) -> str:
        """
        对模型预测结果进行总结
        
        Args:
            analysis_type: 分析类型
            prediction_data: 预测结果数据
            
        Returns:
            AI生成的总结文本
        """
        try:
            prompt = ChatPromptTemplate.from_template(self.model_prediction_template)
            chain = prompt | self.llm | StrOutputParser()
            
            # 将数据转换为JSON字符串以便在提示词中使用
            prediction_json = json.dumps(prediction_data, ensure_ascii=False, indent=2)
            
            summary = chain.invoke({
                "analysis_type": analysis_type,
                "prediction_data": prediction_json
            })
            
            app_logger.info(f"模型预测 {analysis_type} 的AI总结生成完成")
            return summary
            
        except Exception as e:
            app_logger.error(f"生成模型预测总结失败: {str(e)}")
            return f"总结生成失败: {str(e)}"
    
    def summarize_statistical_analysis(self, analysis_type: str, analysis_data: Dict[str, Any]) -> str:
        """
        对统计分析结果进行总结
        
        Args:
            analysis_type: 分析类型
            analysis_data: 统计分析数据
            
        Returns:
            AI生成的总结文本
        """
        try:
            prompt = ChatPromptTemplate.from_template(self.statistical_analysis_template)
            chain = prompt | self.llm | StrOutputParser()
            
            # 将数据转换为JSON字符串以便在提示词中使用
            analysis_json = json.dumps(analysis_data, ensure_ascii=False, indent=2)
            
            summary = chain.invoke({
                "analysis_type": analysis_type,
                "analysis_data": analysis_json
            })
            
            app_logger.info(f"统计分析 {analysis_type} 的AI总结生成完成")
            return summary
            
        except Exception as e:
            app_logger.error(f"生成统计分析总结失败: {str(e)}")
            return f"总结生成失败: {str(e)}"
    
    def summarize_comprehensive_analysis(self, task_id: str, model_predictions: Dict[str, Any], 
                                       statistical_analyses: Dict[str, Any]) -> str:
        """
        对综合分析报告进行总结
        
        Args:
            task_id: 任务ID
            model_predictions: 模型预测结果
            statistical_analyses: 统计分析结果
            
        Returns:
            AI生成的综合总结文本
        """
        try:
            prompt = ChatPromptTemplate.from_template(self.comprehensive_template)
            chain = prompt | self.llm | StrOutputParser()
            
            # 将数据转换为JSON字符串以便在提示词中使用
            model_json = json.dumps(model_predictions, ensure_ascii=False, indent=2)
            analysis_json = json.dumps(statistical_analyses, ensure_ascii=False, indent=2)
            
            summary = chain.invoke({
                "task_id": task_id,
                "model_predictions": model_json,
                "statistical_analyses": analysis_json
            })
            
            app_logger.info(f"任务 {task_id} 的综合分析AI总结生成完成")
            return summary
            
        except Exception as e:
            app_logger.error(f"生成综合分析总结失败: {str(e)}")
            return f"总结生成失败: {str(e)}"
    
    async def summarize_model_prediction_async(self, analysis_type: str, prediction_data: Dict[str, Any]) -> str:
        """
        异步对模型预测结果进行总结
        
        Args:
            analysis_type: 分析类型
            prediction_data: 预测结果数据
            
        Returns:
            AI生成的总结文本
        """
        try:
            llm_async = get_chat_model(streaming=False)
            prompt = ChatPromptTemplate.from_template(self.model_prediction_template)
            chain = prompt | llm_async | StrOutputParser()
            
            # 将数据转换为JSON字符串以便在提示词中使用
            prediction_json = json.dumps(prediction_data, ensure_ascii=False, indent=2)
            
            summary = await chain.ainvoke({
                "analysis_type": analysis_type,
                "prediction_data": prediction_json
            })
            
            app_logger.info(f"模型预测 {analysis_type} 的AI总结生成完成（异步）")
            return summary
            
        except Exception as e:
            app_logger.error(f"生成模型预测总结失败（异步）: {str(e)}")
            return f"总结生成失败: {str(e)}"
    
    async def summarize_statistical_analysis_async(self, analysis_type: str, analysis_data: Dict[str, Any]) -> str:
        """
        异步对统计分析结果进行总结
        
        Args:
            analysis_type: 分析类型
            analysis_data: 统计分析数据
            
        Returns:
            AI生成的总结文本
        """
        try:
            llm_async = get_chat_model(streaming=False)
            prompt = ChatPromptTemplate.from_template(self.statistical_analysis_template)
            chain = prompt | llm_async | StrOutputParser()
            
            # 将数据转换为JSON字符串以便在提示词中使用
            analysis_json = json.dumps(analysis_data, ensure_ascii=False, indent=2)
            
            summary = await chain.ainvoke({
                "analysis_type": analysis_type,
                "analysis_data": analysis_json
            })
            
            app_logger.info(f"统计分析 {analysis_type} 的AI总结生成完成（异步）")
            return summary
            
        except Exception as e:
            app_logger.error(f"生成统计分析总结失败（异步）: {str(e)}")
            return f"总结生成失败: {str(e)}"