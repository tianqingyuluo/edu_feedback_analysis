from typing import List
from langchain_core.embeddings import Embeddings
from app.core.config import settings
import requests
import json


class DoubaoEmbeddings(Embeddings):
    """豆包嵌入模型的自定义实现，直接发送文本字符串而不是token数组"""

    def __init__(self):
        self.api_key = settings.openai_embedding_api_key
        self.api_base = settings.embedding_openai_api_base
        self.model_name = settings.embedding_model_name

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入文档列表"""
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        return self._embed([text])[0]

    def _embed(self, texts: List[str]) -> List[List[float]]:
        """执行实际的嵌入请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # 豆包API期望的请求格式
        data = {
            "model": self.model_name,
            "input": texts,  # 直接发送文本字符串，不进行tokenization
        }

        try:
            response = requests.post(
                f"{self.api_base}/embeddings", headers=headers, json=data, timeout=30
            )

            if response.status_code != 200:
                raise Exception(
                    f"豆包API请求失败: {response.status_code} - {response.text}"
                )

            result = response.json()
            return [item["embedding"] for item in result["data"]]

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求错误: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析错误: {str(e)}")
        except KeyError as e:
            raise Exception(f"响应格式错误，缺少字段: {str(e)}")
