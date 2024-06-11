import sys
from pathlib import Path
from typing import Optional

import click

from chatbot.exceptions import CommandException
from chatbot.utils import Logger, cli_args
from chatbot.utils.run_server import _run_server


@click.group()
def cli():
    pass


@click.group()
def knowledge_base():
    pass


@knowledge_base.command()
@click.option(
    "--data-root",
    required=True,
    type=click.Path(exists=True, dir_okay=True, path_type=Path),
    help="Path to data directory",
)
@click.option("--data-type", required=True, type=click.STRING, default=".txt", help="Data file type.")
@click.option("--encoding", type=click.STRING, help="Encoding of data.")
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to yaml config file",
)
def init(data_root: Path, data_type: str, config_file: Path, encoding: Optional[str]):
    import os

    from chatbot.config import load_config
    from chatbot.vector_db import VectorDB

    config = load_config(config_file)
    os.environ["OPENAI_API_KEY"] = config.openai.api_key

    # As config is loaded during python initialization, set config based on provided config file
    VectorDB.set_instance(config)

    VectorDB.initial_save_documents(data_root, data_type, encoding=encoding)


@click.group()
def server():
    pass


@server.command()
@cli_args.HOST
@cli_args.PORT
@cli_args.APP_NAME
@click.option(
    "--config-file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to yaml config file",
)
def run(host, port, app_name, config_file):
    try:
        _run_server(host, port, app_name, config_file)
    except CommandException as e:
        Logger.error("Failed to start server: {}".format(e))
        sys.exit(1)


cli.add_command(knowledge_base)
cli.add_command(server)

if __name__ == "__main__":
    cli()
