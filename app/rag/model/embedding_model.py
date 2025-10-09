from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
from .doubao_embeddings import DoubaoEmbeddings

def get_embedding_model():
    if "openai" in settings.embedding_model_name:
        return OpenAIEmbeddings(
            openai_api_key=settings.openai_embedding_api_key,
            openai_api_base=settings.embedding_openai_api_base,
            model=settings.embedding_model_name,
            # async_client=True
        )
    elif "doubao" in settings.embedding_model_name:
        return DoubaoEmbeddings()
