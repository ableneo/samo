from functools import partial
from typing import Dict, Optional

from langchain.schema.output_parser import StrOutputParser

from chatbot.core.llm.interfaces import ChainInterface
from chatbot.utils.fn import reciprocal_rank_fusion
from chatbot.vector_db import VectorDB


class ReciprocalRankFusionChain(ChainInterface):
    _default_chain_kwargs: Dict = {"temperature": 0}

    def get_chain(self, chat_kwargs: Optional[Dict] = None, **kwargs):
        chat_kwargs = chat_kwargs or {}
        top_n = kwargs.pop("top_n", 5)

        # Get VectorDB Instance
        vector_db = VectorDB.get_instance()

        # Build MultiQuery Generation pipeline
        generate_queries_chain = (
            self.get_prompt() | self.get_chat_instance(**chat_kwargs) | StrOutputParser() | (lambda x: x.split("\n"))
        )

        # Build Reciprocal Rank Fusion Generation
        final_chain = generate_queries_chain | vector_db.parent_dr.map() | partial(reciprocal_rank_fusion, top_n=top_n)
        return final_chain


class RagChain(ChainInterface):
    _default_chain_kwargs: Dict = {
        "temperature": 0.1,
        "streaming": True,
    }

    def get_chain(self, chat_kwargs: Dict, **kwargs):
        final_chain = self.get_prompt() | self.get_chat_instance(**chat_kwargs)

        return final_chain
