from langchain.chat_models import ChatOpenAI
from app.core.config import settings

def get_chat_model(callbacks=None, streaming=True):
    return ChatOpenAI(
        model_name=settings.llm_model_name, # 或者 "gpt-4" 等
        openai_api_key=settings.openai_api_key,
        temperature=0.7,
        streaming=streaming,
        callbacks=callbacks,
    )