import traceback

from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader
from app.core.logging import app_logger
from app.utils.detect_file_encoding_with_cchardet import detect_file_encoding_with_cchardet
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
                # 检测文件编码并使用正确的编码加载文本文件
                encoding, confidence = detect_file_encoding_with_cchardet(file_path)
                if encoding and confidence > 0.7:
                    app_logger.info(f"检测到文件 {file_path} 编码为: {encoding} (置信度: {confidence:.2f})")
                    loader = TextLoader(file_path, encoding=encoding)
                else:
                    # 如果检测失败，尝试常见编码
                    for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']:
                        try:
                            app_logger.info(f"尝试使用编码 {enc} 加载文件: {file_path}")
                            loader = TextLoader(file_path, encoding=enc)
                            loaded_docs = loader.load()
                            app_logger.info(f"成功使用编码 {enc} 加载文件: {file_path}")
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # 如果所有编码都失败，使用默认编码并忽略错误
                        app_logger.warning(f"无法确定文件 {file_path} 的编码，使用默认编码并忽略错误字符")
                        loader = TextLoader(file_path, encoding='utf-8', encoding_errors='ignore')
            elif file_path.lower().endswith(".csv"):
                # CSV文件也需要处理编码问题
                encoding, confidence = detect_file_encoding_with_cchardet(file_path)
                if encoding and confidence > 0.7:
                    app_logger.info(f"检测到CSV文件 {file_path} 编码为: {encoding} (置信度: {confidence:.2f})")
                    loader = CSVLoader(file_path, encoding=encoding)
                else:
                    # 如果检测失败，尝试常见编码
                    for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'big5']:
                        try:
                            app_logger.info(f"尝试使用编码 {enc} 加载CSV文件: {file_path}")
                            loader = CSVLoader(file_path, encoding=enc)
                            loaded_docs = loader.load()
                            app_logger.info(f"成功使用编码 {enc} 加载CSV文件: {file_path}")
                            break
                        except UnicodeDecodeError:
                            continue
                    else:
                        # 如果所有编码都失败，使用默认编码并忽略错误
                        app_logger.warning(f"无法确定CSV文件 {file_path} 的编码，使用默认编码并忽略错误字符")
                        loader = CSVLoader(file_path, encoding='utf-8', encoding_errors='ignore')
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
            app_logger.info(traceback.format_exc())
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