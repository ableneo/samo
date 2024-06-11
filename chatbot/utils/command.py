import os
import subprocess
import sys
from typing import Dict, List, Optional

from chatbot.exceptions import CommandException


def _exec_cmd(cmd, extra_env: Optional[Dict] = None):
    # If not extra env provided create empty dict
    extra_env = extra_env or {}

    proc = subprocess.Popen(
        cmd,
        env={**os.environ, **extra_env},
        text=True,
    )

    _outs, _errs = proc.communicate()
    return_code = proc.poll()
    comp_process = subprocess.CompletedProcess(
        proc.args,
        returncode=return_code,
        stdout=_outs,
        stderr=_errs,
    )
    if return_code != 0:
        raise CommandException(comp_process)


def _build_wsgi_command(host, port, app_name, *args) -> List[str]:
    if sys.platform == "win32":

        wsgi_server = "waitress"
        wsgi_args = [
            *args,
            f"--host={host}",
            f"--port={port}",
        ]
    else:

        wsgi_server = "gunicorn"
        wsgi_args = [*args, "-b", f"{host}:{port}"]

    return [sys.executable, "-m", wsgi_server, *wsgi_args, app_name]
