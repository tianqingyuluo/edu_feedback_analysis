import asyncio
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.callbacks import AsyncIteratorCallbackHandler
from app.rag.model import get_chat_model

def create_rag_chain(retriever, prompt=None, streaming=True):
    """
    创建一个RAG链，将检索和生成结合起来。
    """
    callback = AsyncIteratorCallbackHandler()
    # 定义Prompt模板
    template = """
    你是专注于高校评教问卷数据的专业分析 Agent，需以教育评估逻辑为基础，结合统计学方法与高校教学管理需求，
    对评教数据进行客观、深入的解读。并且能够回答教师和管理人员的提问。给出可以落地的建议。
    Context: {context}
    Question: {question}

    Answer:
    """
    chat_model = get_chat_model(streaming=streaming, callbacks=[callback] if streaming else None)
        
    if not prompt:
        prompt = ChatPromptTemplate.from_template(template)
    else:
        prompt = ChatPromptTemplate.from_template(prompt)
    # prompt = ChatPromptTemplate.from_template(template)

    # 构建RAG链
    rag_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | prompt
        | chat_model
        | StrOutputParser()
    )
    return rag_chain, callback if streaming else None

async def stream_response(rag_chain, question: str):
    """
    异步流式生成响应
    """
    rag_chain, callback = rag_chain
    
    # 创建一个任务来运行RAG链
    task = asyncio.create_task(rag_chain.ainvoke(question))
    
    try:
        # 流式输出结果
        async for token in callback.aiter():
            yield token
    except Exception as e:
        yield f"Error: {str(e)}"
    finally:
        # 确保任务完成
        await task
