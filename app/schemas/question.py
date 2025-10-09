from pydantic import BaseModel

class Question(BaseModel):
    """
    ai 问答
    """
    question: str