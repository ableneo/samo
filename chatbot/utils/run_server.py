from pathlib import Path

from chatbot.constants import CONFIG_FILE_PATH
from chatbot.utils.command import _build_wsgi_command, _exec_cmd


def _run_server(host, port, app_name, config_file, *wsgi_args):
    command = _build_wsgi_command(host, port, app_name, *wsgi_args)

    env = {CONFIG_FILE_PATH: str(Path(config_file).absolute())}

    _exec_cmd(command, extra_env=env)
