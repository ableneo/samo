import os
from pathlib import Path
from typing import List, Union

from pydantic import BaseModel, Field, model_validator

from chatbot.constants import (
    CONFIG_FILE_PATH,
    VECTOR_DB__PARENT_DATA_FILE_PATH,
    VECTOR_DB__PERSIST_DIRECTORY_PATH,
)
from chatbot.models.base import Prompt


class OpenAIConfig(BaseModel):
    embedding_model: str
    chat_model: str
    api_key: str

    @model_validator(mode="after")
    def validate_openai(self):
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        openai_available_models = [model_data.id for model_data in client.models.list().data]

        assert self.chat_model in openai_available_models, ValueError(
            f"Chat model '{self.chat_model}' is not valid model of OpenAI API."
        )
        assert self.embedding_model in openai_available_models, ValueError(
            f"Embedding model '{self.embedding_model}' is not valid model of OpenAI API."
        )

        return self


class APIVersion1Config(BaseModel):
    multi_query_prompt: List[Prompt]
    rag_prompt: List[Prompt]


class APIVersioning(BaseModel):
    v1: APIVersion1Config


class VectorDBConfig(BaseModel):
    parent_data_file: Path = Field(default=Path(VECTOR_DB__PARENT_DATA_FILE_PATH))
    persist_directory: Path = Field(default=Path(VECTOR_DB__PERSIST_DIRECTORY_PATH))


class ServerConfig(BaseModel):
    app_name: str = Field(default="ableneo-chatbot")
    chat_dir: Path = Path(".", "logs")
    feedback_dir: Path = Path(".", "feedback")

    openai: OpenAIConfig
    vector_db: VectorDBConfig = Field(default_factory=VectorDBConfig)

    api: APIVersioning


def load_config(config_yaml: Union[str, Path]) -> ServerConfig:
    from pathlib import Path

    import yaml

    if isinstance(config_yaml, str):
        config_yaml = Path(config_yaml)

    config = yaml.safe_load(config_yaml.read_text(encoding="utf-8"))

    return ServerConfig(**config)


server_config = load_config(config_path) if (config_path := os.getenv(CONFIG_FILE_PATH)) else None
if server_config is not None:
    os.environ["OPENAI_API_KEY"] = server_config.openai.api_key
