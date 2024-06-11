from typing import List

from pydantic import BaseModel


class PromptRequest(BaseModel):
    chat_history: List[str]
    chat_id: str
    question: str


class HistoryRequest(BaseModel):
    chat_id: int


class FeedbackRequest(BaseModel):
    chat_id: str
    chat_history: List[str]
    question: str
    answer: str
    feedback: str
    reporter: str
