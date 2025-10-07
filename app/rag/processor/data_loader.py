from langchain.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from app.core.logging import app_logger
from typing import Any

import docx

def load_documents(file_paths: list[str]) -> list[dict[str, Any]]:
    """
    加载多种格式的文档。
    返回一个列表，每个元素包含 'page_content' 和 'metadata'。
    """
    documents = []
    for file_path in file_paths:
        try:
            if file_path.lower().endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.lower().endswith(".txt"):
                loader = TextLoader(file_path)
            elif file_path.lower().endswith(".csv"):
                loader = CSVLoader(file_path)
            elif file_path.lower().endswith(".docx") or file_path.lower().endswith(".doc"):
                documents.append(load_docx(file_path))
                continue
            else:
                app_logger.info(f"不支持的文件格式: {file_path}. 将跳过")
                continue

            loaded_docs = loader.load()
            # LangChain的loader返回的是Document对象，我们将其转换为字典格式
            for doc in loaded_docs:
                documents.append(
                    {"page_content": doc.page_content, "metadata": doc.metadata}
                )
        except Exception as e:
            app_logger.info(f"加载文件 {file_path} 时出现错误: {e}")
    return documents

def load_docx(file_path: str):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return {
                "page_content": text,
                "metadata": {
                    "source": file_path,
                    "title": doc.core_properties.title,
                    "author": doc.core_properties.author,
                    "created": doc.core_properties.created,
                    "modified": doc.core_properties.modified,
                }
           }