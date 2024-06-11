# TODO: kudos & refactoring
class CommandException(Exception):
    @classmethod
    def from_completed_process(cls, process):
        lines = [
            f"Command exited with non-zero code: {process.returncode}",
            f"Command: {process.args}",
        ]
        if process.stdout:
            lines += [
                "",
                "STDOUT:",
                process.stdout,
            ]
        if process.stderr:
            lines += [
                "",
                "STDERR:",
                process.stderr,
            ]
        return cls("\n".join(lines))
