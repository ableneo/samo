import logging
import os

logger_level = os.getenv("LOGGER_LEVEL", "INFO")


# disabling debug logs for openai, urllib3, chromadb
logging.getLogger("openai").setLevel(logger_level)
logging.getLogger("urllib3").setLevel(logger_level)
logging.getLogger("chromadb").setLevel(logger_level)

Logger = logging.getLogger("root")
Logger.setLevel(logger_level)

# Create a handler for output to stdout
handler = logging.StreamHandler()
handler.setLevel(logger_level)

if logger_level == "DEBUG":
    Logger.warning("Logger level set to DEBUG. Don't use DEBUG in production...")


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if "extraFields" in record.__dict__:
            record.message_with_extra = f"{record.msg} - {record.extraFields}"
        else:
            record.message_with_extra = record.msg
        return super(CustomFormatter, self).format(record)


formatter = CustomFormatter("[%(asctime)s] [%(process)d] [%(levelname)s] %(message_with_extra)s")
handler.setFormatter(formatter)

# Add the handler to the logger
Logger.addHandler(handler)
