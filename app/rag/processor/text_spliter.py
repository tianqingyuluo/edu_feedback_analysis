from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any

def split_documents(
    documents: List[Dict[str, Any]], chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """
    将文档分割成更小的文本块。
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True,  # 添加起始索引到metadata
    )

    # LangChain的text_splitter需要Document对象，所以我们先转换
    from langchain.schema import Document

    langchain_docs = [
        Document(page_content=doc["page_content"], metadata=doc["metadata"])
        for doc in documents
    ]

    split_docs = text_splitter.split_documents(langchain_docs)

    # 将分割后的Document对象转换回字典格式
    return [
        {"page_content": doc.page_content, "metadata": doc.metadata}
        for doc in split_docs
    ]
