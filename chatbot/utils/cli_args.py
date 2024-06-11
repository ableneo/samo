import click

HOST = click.option(
    "--host",
    "-h",
    default="127.0.0.1",
    help="The host to connect to",
)

PORT = click.option(
    "--port",
    "-p",
    default=6628,
    help="The port to connect to",
)

APP_NAME = click.option(
    "--app-name",
    default="chatbot.server:app",
    help="The app name",
)
