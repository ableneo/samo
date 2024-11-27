import json
import threading
from pathlib import Path

import jsonpickle
from _operator import itemgetter
from flask import Response, render_template
from langchain.retrievers import ParentDocumentRetriever
from tenacity import retry, wait_exponential

from chatbot.config import server_config
from chatbot.core.llm.chains import RagChain, ReciprocalRankFusionChain
from chatbot.models import ChatInstance
from chatbot.networking.dto.chatdata import ChatData
from chatbot.networking.streaming import ChainStreamHandler, ThreadedGenerator
from chatbot.services import ServiceInterface
from chatbot.utils import Logger
from chatbot.utils.fn import _get_safe_feedback_path, _get_safe_file_path


class ChatbotService(ServiceInterface):
    retriever: ParentDocumentRetriever

    def __init__(
        self,
        chats_path: Path = None,
        feedback_path: Path = None,
    ):

        self.feedback_directory = feedback_path
        self.chats_path = chats_path

    def get_docs_chain(self, g, chat_id, input_prompts, top_n=5):

        reciprocal_chain = ReciprocalRankFusionChain(server_config.api.v1.multi_query_prompt).get_chain(top_n=top_n)

        rag_chat_config = {
            "callbacks": [ChainStreamHandler(g, input_prompts["chat_history"], _get_safe_file_path(self.chats_path, chat_id))]
        }
        rag_chain = RagChain(server_config.api.v1.rag_prompt).get_chain(chat_kwargs=rag_chat_config)

        self.rag_fusion_chain = {
            "context": reciprocal_chain,
            "original_query": itemgetter("original_query"),
            "chat_history": itemgetter("chat_history"),
        } | rag_chain

        Logger.info(
            "Invoking final chain",
            extra={
                "extraFields": {
                    "chat_id": chat_id,
                    "input_prompts": jsonpickle.dumps(input_prompts),
                }
            },
        )
        self.rag_fusion_chain.invoke(input_prompts)

    @retry(wait=wait_exponential(multiplier=1, min=3, max=3))
    def llm_thread(self, g, chat_id, input_prompts):
        try:
            self.get_docs_chain(g, chat_id, input_prompts, top_n=5)
        except Exception as e:  # TODO: us exception output
            Logger.error(
                "Retrying answer generation",
                extra={"extraFields": {"chat_id": chat_id}, "error": str(e)},
            )
            self.get_docs_chain(g, chat_id, input_prompts, top_n=4)
        finally:
            g.close()

    def chain(self, chat_id, prompt):
        g = ThreadedGenerator()
        threading.Thread(target=self.llm_thread, args=(g, chat_id, prompt)).start()
        return g

    def index(self):
        return render_template("chatbot_index.html")

    def _api_prompt(self, request_data) -> Response:

        prompt = ChatData()
        prompt.deserialize(request_data)

        # TODO: Extracted is it meaningful feature?
        chat_instance = ChatInstance()

        if prompt.chat_history is not None:
            chat_instance.chat_history = prompt.chat_history

        chat = chat_instance.get_answer_history_as_string()
        chat += f"{prompt.question}"

        prompt.chat_history.append({"role": "user", "content": f"{prompt.question}"})

        Logger.debug(
            "Starting service for question",
            extra={
                "extraFields": {
                    "history": prompt.chat_history,
                    "chat_id": prompt.chat_id,
                    "question": prompt.question,
                }
            },
        )

        return Response(
            self.chain(
                prompt.chat_id,
                {
                    "original_query": prompt.question,
                    "chat_history": prompt.chat_history,
                },
            ),
            mimetype="text/plain",
        )

    def _api_history(self, request_data) -> Response:
        chat_id = jsonpickle.decode(request_data)["chat_id"]

        if (safe_chat_file_path := _get_safe_file_path(self.chats_path, chat_id)) is None:
            Logger.error(
                "Invalid chat id",
                extra={"extraFields": {"chat_id": chat_id, "method": "_api_history"}},
            )
            return Response("Invalid chat id", status=400)

        if safe_chat_file_path.exists():
            with safe_chat_file_path.open("r") as chat_file:
                chat_content = chat_file.read()

            Logger.info(
                "Getting history for chat id",
                extra={"extraFields": {"chat_id": chat_id, "chat_content": chat_content}},
            )
            return Response(chat_content, mimetype="application/json")
        else:
            return Response(f"History of chat with id {chat_id} doesn't exist.", status=404)

    def _api_feedback(self, request_data) -> Response:
        feedback = ChatData()
        feedback.deserialize(request_data)

        self.feedback_directory.mkdir(parents=True, exist_ok=True)

        safe_chat_file_path = _get_safe_feedback_path(feedback.chat_id)

        if not feedback.chat_id:
            Logger.error(
                "Invalid chat id",
                extra={
                    "extraFields": {
                        "chat_id": feedback.chat_id,
                        "method": "_api_feedback",
                    }
                },
            )
            return Response("Invalid chat id", status=400)

        Logger.info(
            "Feedback received",
            extra={
                "extraFields": {
                    "chat_id": feedback.chat_id,
                    "feedback": feedback.feedback,
                    "method": "_api_feedback",
                }
            },
        )

        json_content = {
            "chat_id": feedback.chat_id,
            "history": feedback.chat_history,
            "question": feedback.question,
            "answer": feedback.answer,
            "user": feedback.reporter,
            "feedback": feedback.feedback,
        }
        with safe_chat_file_path.open("w") as feedback_file:
            json.dump(json_content, feedback_file, indent=2, ensure_ascii=False)

        return Response(jsonpickle.encode({"message": "success"}), mimetype="application/json")

    def embed_data(self, request_data) -> Response:
        data_root, data_type, encoding = request_data.data_root, request_data.data_type, request_data.encoding

        from chatbot.config import server_config
        from chatbot.vector_db import VectorDB

        VectorDB.set_instance(server_config)
        VectorDB.initial_save_documents(data_root, data_type, encoding)

        return Response(jsonpickle.encode({"message": "Successfully embedded new data."}), mimetype="application/json")


# Create ChatbotService
chat_service = ChatbotService(chats_path=server_config.chat_dir, feedback_path=server_config.feedback_dir)
