from pathlib import Path
from typing import List, Tuple

from flask import Flask, render_template

from chatbot.config import server_config
from chatbot.services.v1.routers import v1_router
from chatbot.vector_db import VectorDB
from chatbot.version import VERSION


def add_access_control_headers(response):
    # TODO this line should not be here
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# Initialize VectorDB
VectorDB.get_instance()

# Create Flask instance
app = Flask(server_config.app_name, template_folder=Path("static/templates").absolute())

app.after_request(add_access_control_headers)

# Add services
app.register_blueprint(v1_router)


# Define server root endpoints
# Health check endpoint to ensure chatbot is running
@app.route("/health")
def health():
    return "OK", 200


# Version of running chatbot
@app.route("/version")
def version():
    return VERSION, 200


@app.route("/")
def index():
    # Create list of registered endpoints
    available_endpoints: List[Tuple] = []
    for url in app.url_map.iter_rules():
        if url.endpoint != "static":
            available_endpoints.append((f"[{' '.join(url.methods)}]", url.rule))

    res = render_template("index.html", endpoints=available_endpoints[::-1])

    return res
