from flask import request, jsonify
from pydantic import ValidationError

from chatbot.utils import Logger

from .requests import FeedbackRequest, HistoryRequest, PromptRequest, EmbedDataRequest
from .routers import rag_chain_router
from .service import chat_service


@rag_chain_router.route("/", methods=["GET"])
def chat_testing():
    return chat_service.index()


@rag_chain_router.route("/prompt", methods=["POST"])
def chat_prompt():
    request_data = request.data.decode("utf-8")

    # Validation of request body
    try:
        PromptRequest.parse_raw(request_data)
    except ValidationError as validation_error:
        Logger.warning(str(validation_error))
        return str(validation_error), 400
    else:
        return chat_service._api_prompt(request_data)


@rag_chain_router.route("/history", methods=["POST"])
def chat_history():
    request_data = request.data.decode("utf-8")

    # Validation of request body
    try:
        HistoryRequest.parse_raw(request_data)
    except ValidationError as validation_error:
        Logger.warning(str(validation_error))
        return str(validation_error), 400
    else:
        return chat_service._api_history(request_data)


@rag_chain_router.route("/feedback", methods=["POST"])
def chat_feedback():
    request_data = request.data.decode("utf-8")

    # Validation of request body
    try:
        FeedbackRequest.parse_raw(request_data)
    except ValidationError as validation_error:
        Logger.warning(str(validation_error))
        return str(validation_error), 400

    return chat_service._api_feedback(request_data)

@rag_chain_router.route("/embedData", methods=["POST"])
def embed_data():
    request_data = request.json

    # Validation of request body
    try:
        validated_data = EmbedDataRequest(**request_data)
    except ValidationError as validation_error:
        Logger.warning(str(validation_error))
        return jsonify({"error": "Validation Error", "details": validation_error.errors()}), 400

    return chat_service.embed_data(validated_data)
