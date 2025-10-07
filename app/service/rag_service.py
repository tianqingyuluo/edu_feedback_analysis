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
        self.vector_store = None
        self.rag_chain = None
        # self.rag_agent = None # 如果使用Agent

    def initialize_knowledge_base(self, file_paths: list[str]):
        """
        初始化知识库：加载、分割、嵌入并存储文档。
        """
        app_logger.info("初始化rag知识库...")
        # 1. 加载文档
        documents = load_documents(file_paths)
        if not documents:
            app_logger.info("没有新文档载入")
        else:
            # 2. 分割文档
            split_docs = split_documents(documents)
            app_logger.info(f"Split into {len(split_docs)} chunks.")



        # 3. 创建或加载向量存储
        self.vector_store = create_or_update_vector_store_with_deduplication(
            split_docs,
            self.embedding_model,
            settings.chroma_persist_path,
        )
        app_logger.info("知识库初始化完成")

        # 4. 创建RAG链
        retriever = get_retriever(self.vector_store)
        self.rag_chain = create_rag_chain(retriever, streaming=True) # 创建一个
        app_logger.info("RAG链成功创建")

        # 5. 初始化Agent (如果使用)
        # self.rag_agent = RAGAgent(self.vector_store, self.llm)

    def query(self, question: str) -> str:
        """
        使用RAG链查询问题。
        """
        if not self.rag_chain:
            return "知识库未初始化，请先上传并处理文档。"

        app_logger.info(f"Querying: {question}")
        try:
            # 使用RAG链直接查询
            response = self.rag_chain.invoke(question)
            # 使用Agent:
            # response = self.rag_agent.run(question)
            return response
        except Exception as e:
            app_logger.info(f"Error during query: {e}")
            return f"An error occurred: {e}"

    async def stream_query(self, question: str):
        """
        流式查询问题 (需要修改llm_generator.py中的create_rag_chain以支持流式)
        """
        # 需要修改llm_generator.py中的create_rag_chain，使其返回一个async iterator
        # 例如，使用AsyncIteratorCallbackHandler
        if not self.rag_chain:
            yield "知识库未初始化！请先上传并处理文档。"
            return
        
        app_logger.info(f"发起流式请求：{question}")
        
        try:
            async for token in stream_response(self.rag_chain, question):
                yield token
        except Exception as e:
            app_logger.info(f"在请求中发生错误: {e}")
            yield f"{e}"
