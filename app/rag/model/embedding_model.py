from langchain.embeddings import OpenAIEmbeddings
from app.core.config import settings

def get_embedding_model():
    return OpenAIEmbeddings(openai_api_key=settings.openai_embedding_api_key)