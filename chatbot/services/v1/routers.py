from flask import Blueprint

from chatbot.services.v1.rag_chatbot.routers import rag_chain_router

v1_router = Blueprint("v1", __name__, url_prefix="/v1")

# Add services
v1_router.register_blueprint(rag_chain_router)
