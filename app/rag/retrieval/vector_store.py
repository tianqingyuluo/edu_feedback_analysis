# from langchain.vectorstores import Chroma
# from langchain.schema import Document
# from typing import List, Dict, Any
#
# from app.core.config import settings
# from app.core.logging import app_logger
# import os
#
# def create_or_load_vector_store(
#     documents: List[Dict[str, Any]],
#     embedding_model,
#     persist_directory: str = settings.chroma_persist_path
# ) -> Chroma:
#     """
#     创建或加载ChromaDB向量存储。
#     """
#     if not os.path.exists(persist_directory):
#         os.makedirs(persist_directory)
#         app_logger.info(f"创建 ChromaDB 在: {persist_directory}")
#
#         # 将字典格式的文档转换为LangChain的Document对象
#         langchain_docs = [
#             Document(page_content=doc["page_content"], metadata=doc["metadata"])
#             for doc in documents
#         ]
#
#         vector_store = Chroma.from_documents(
#             documents=langchain_docs,
#             embedding=embedding_model,
#             persist_directory=persist_directory,
#         )
#         vector_store.persist()  # 持久化到磁盘
#         app_logger.info("向量数据库创建并且持久化到磁盘")
#     else:
#         app_logger.info(f"加载 ChromaDB: {persist_directory}")
#         vector_store = Chroma(
#             persist_directory=persist_directory, embedding_function=embedding_model
#         )
#         app_logger.info("向量数据库已加载")
#     return vector_store
#
#
# def get_retriever(vector_store: Chroma, search_kwargs: Dict[str, Any] = {"k": 10}):
#     """
#     从向量存储获取检索器。
#     """
#     return vector_store.as_retriever(search_kwargs=search_kwargs)

import os
from typing import List, Dict, Any, Set

from langchain.schema import Document
from langchain.vectorstores import Chroma

from app.core.config import settings
from app.core.logging import app_logger


def create_or_update_vector_store_with_deduplication(
    documents: List[Dict[str, Any]],
    embedding_model,
    persist_directory: str = settings.chroma_persist_path,
    metadata_id_key: str = "source",  # 指定哪个 metadata 字段是唯一ID
) -> Chroma:
    """
    创建或加载/更新ChromaDB向量存储，并基于metadata进行去重。

    Args:
        documents: 待处理的文档列表，每个文档是一个字典。
        embedding_model: 使用的嵌入模型。
        persist_directory: 数据库持久化路径。
        metadata_id_key: 在 metadata 中用作唯一标识的键名，默认为 'source'。
    """
    langchain_docs = [
        Document(page_content=doc["page_content"], metadata=doc["metadata"])
        for doc in documents
    ]

    vector_store = None
    if not os.path.exists(persist_directory) or not os.listdir(persist_directory):
        os.makedirs(persist_directory, exist_ok=True)
        app_logger.info(f"创建新的 ChromaDB 在: {persist_directory}")
        vector_store = Chroma.from_documents(
            documents=langchain_docs,
            embedding=embedding_model,
            persist_directory=persist_directory,
        )
        app_logger.info(f"向量数据库已创建，包含 {len(langchain_docs)} 个文档。")
    else:
        app_logger.info(f"从磁盘加载已有的 ChromaDB: {persist_directory}")
        vector_store = Chroma(
            persist_directory=persist_directory, embedding_function=embedding_model
        )

        # 去重逻辑
        # 获取数据库中所有文档的元数据
        # include=['metadatas'] 确保只拉取元数据，非常高效
        existing_docs_metadata = vector_store.get(include=["metadatas"])
        existing_ids: Set[str] = set()

        # 从元数据中提取出所有的唯一ID
        if existing_docs_metadata and "metadatas" in existing_docs_metadata:
            for meta in existing_docs_metadata["metadatas"]:
                if meta and metadata_id_key in meta:
                    existing_ids.add(meta[metadata_id_key])

        app_logger.info(f"数据库中已存在 {len(existing_ids)} 个唯一文档。")

        # 筛选出本次需要新添加的文档
        new_docs_to_add = []
        for doc in langchain_docs:
            # 检查当前文档的ID是否已经存在于数据库中
            doc_id = doc.metadata.get(metadata_id_key)
            if doc_id is None:
                app_logger.warning(
                    f"发现文档缺少唯一ID key '{metadata_id_key}'，将跳过: {doc.page_content[:50]}..."
                )
                continue

            if doc_id not in existing_ids:
                new_docs_to_add.append(doc)

        # 如果有新文档，则执行添加操作
        if new_docs_to_add:
            app_logger.info(
                f"发现 {len(new_docs_to_add)} 篇新文档，正在添加到向量数据库..."
            )
            vector_store.add_documents(documents=new_docs_to_add)
            app_logger.info("新文档添加成功。")
        else:
            app_logger.info("未发现需要添加的新文档。")

    return vector_store

def get_retriever(vector_store: Chroma, search_kwargs: Dict[str, Any] = {"k": 10}):
    """
    从向量存储获取检索器。
    """
    return vector_store.as_retriever(search_kwargs=search_kwargs)