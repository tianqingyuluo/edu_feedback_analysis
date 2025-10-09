import traceback
from typing import Dict, Optional
import os
from app.core.logging import app_logger
from app.rag.processor.data_loader import load_documents
from app.rag.processor.text_spliter import split_documents
from app.rag.model.embedding_model import get_embedding_model
from app.rag.retrieval.vector_store import create_or_update_vector_store_with_deduplication, get_retriever
from app.rag.tools.llm_generator_tool import get_chat_model, create_rag_chain, stream_response
from app.core.config import settings
# from rag.rag_agent import RAGAgent # 如果使用Agent


class RAGService:
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.llm = get_chat_model()
        self.vector_stores: Dict[int, any] = {}  # 支持多个知识库
        self.rag_chains: Dict[int, any] = {}  # 支持多个RAG链
        self.current_kb_id: Optional[int] = None  # 当前活跃的知识库ID
        # self.rag_agent = None # 如果使用Agent

    def initialize_knowledge_base(self, file_paths: list[str], kb_id: int = None):
        """
        初始化知识库：加载、分割、嵌入并存储文档。
        """
        if kb_id is None:
            kb_id = 1  # 默认知识库ID
            
        app_logger.info(f"初始化RAG知识库 {kb_id}...")
        
        # 1. 加载文档
        documents = load_documents(file_paths)
        if not documents:
            app_logger.info("没有新文档载入")
            return
            
        # 2. 分割文档
        split_docs = split_documents(documents)
        app_logger.info(f"Split into {len(split_docs)} chunks.")

        # 3. 为每个知识库创建独立的向量存储路径
        kb_persist_path = os.path.join(settings.chroma_persist_path, f"kb_{kb_id}")
        
        # 4. 创建或加载向量存储
        vector_store = create_or_update_vector_store_with_deduplication(
            split_docs,
            self.embedding_model,
            kb_persist_path,
        )
        self.vector_stores[kb_id] = vector_store
        app_logger.info(f"知识库 {kb_id} 初始化完成")

        # 5. 创建RAG链
        retriever = get_retriever(vector_store)
        rag_chain, callback = create_rag_chain(retriever, streaming=True)
        self.rag_chains[kb_id] = (rag_chain, callback)
        self.current_kb_id = kb_id
        app_logger.info(f"知识库 {kb_id} 的RAG链成功创建")

        # 6. 初始化Agent (如果使用)
        # self.rag_agent = RAGAgent(vector_store, self.llm)

    def set_active_knowledge_base(self, kb_id: int):
        """设置当前活跃的知识库"""
        if kb_id in self.vector_stores:
            self.current_kb_id = kb_id
            app_logger.info(f"切换到知识库 {kb_id}")
            return True
        else:
            app_logger.warning(f"知识库 {kb_id} 不存在或未初始化")
            return False

    def get_knowledge_base_status(self, kb_id: int) -> Dict:
        """获取知识库状态"""
        if kb_id in self.vector_stores:
            return {
                "kb_id": kb_id,
                "initialized": True,
                "active": self.current_kb_id == kb_id
            }
        else:
            return {
                "kb_id": kb_id,
                "initialized": False,
                "active": False
            }

    def delete_knowledge_base(self, kb_id: int) -> bool:
        """删除知识库"""
        try:
            # 从内存中移除
            if kb_id in self.vector_stores:
                del self.vector_stores[kb_id]
            if kb_id in self.rag_chains:
                del self.rag_chains[kb_id]
            
            # 如果删除的是当前活跃的知识库，重置当前ID
            if self.current_kb_id == kb_id:
                self.current_kb_id = None
                
            # 删除向量存储文件
            kb_persist_path = os.path.join(settings.chroma_persist_path, f"kb_{kb_id}")
            if os.path.exists(kb_persist_path):
                import shutil
                shutil.rmtree(kb_persist_path)
                app_logger.info(f"删除知识库 {kb_id} 的向量存储文件")
            
            return True
        except Exception as e:
            app_logger.error(f"删除知识库 {kb_id} 失败: {str(e)}")
            return False

    def query(self, question: str, kb_id: int = None) -> str:
        """
        使用RAG链查询问题。
        """
        # 确定使用的知识库
        target_kb_id = kb_id if kb_id is not None else self.current_kb_id
        
        if target_kb_id is None or target_kb_id not in self.vector_stores:
            return "知识库未初始化，请先上传并处理文档。"

        app_logger.info(f"Querying knowledge base {target_kb_id}: {question}")
        try:
            # 每次查询都创建新的RAG链，避免状态问题
            from app.rag.retrieval.vector_store import get_retriever
            from app.rag.tools.llm_generator_tool import create_rag_chain
            
            retriever = get_retriever(self.vector_stores[target_kb_id])
            rag_chain, _ = create_rag_chain(retriever, streaming=False)
            
            # 使用新创建的RAG链查询
            response = rag_chain.invoke(question)
            return response
        except Exception as e:
            app_logger.info(f"Error during query: {e}")
            return f"An error occurred: {e}"

    async def stream_query(self, question: str, kb_id: int = None):
        """
        流式查询问题
        """
        # 确定使用的知识库
        target_kb_id = kb_id if kb_id is not None else self.current_kb_id
        
        if target_kb_id is None or target_kb_id not in self.vector_stores:
            yield "知识库未初始化！请先上传并处理文档。"
            return
        
        app_logger.info(f"向知识库 {target_kb_id} 发起流式请求：{question}")
        
        try:
            # 每次流式查询都创建新的RAG链和回调处理器，避免回调状态问题
            from app.rag.retrieval.vector_store import get_retriever
            from app.rag.tools.llm_generator_tool import create_rag_chain, stream_response
            
            retriever = get_retriever(self.vector_stores[target_kb_id])
            rag_chain, callback = create_rag_chain(retriever, streaming=True)
            
            async for token in stream_response((rag_chain, callback), question):
                yield token
        except Exception as e:
            app_logger.info(f"在请求中发生错误: {e}")
            app_logger.info(traceback.format_exc())
            yield f"{e}"
