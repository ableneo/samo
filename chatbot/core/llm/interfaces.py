from abc import ABC, abstractmethod
from typing import Dict, List

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from chatbot.config import server_config
from chatbot.models.base import Prompt


class ChainInterface(ABC):
    _prompt_template: List[str]
    _model_name: str = server_config.openai.chat_model
    _chat_model: ChatOpenAI
    _default_chain_kwargs: Dict

    def __init__(self, instructions: List[Prompt]):
        self._prompt_template = [f"{_instruction.entity}, {_instruction.instruction}" for _instruction in instructions]

    def get_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(messages=self._prompt_template)

    def get_chat_instance(self, **kwargs) -> ChatOpenAI:
        kwargs = {**self._default_chain_kwargs, **kwargs}

        return ChatOpenAI(model_name=self._model_name, **kwargs)

    @abstractmethod
    def get_chain(self, chat_kwargs: Dict, *args):
        pass
