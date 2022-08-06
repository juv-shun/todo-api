import logging

import arrow
from pythonjsonlogger import jsonlogger


class JsonFormatter(jsonlogger.JsonFormatter):
    def parse(self):
        return [
            "time",
            "level",
            "name",
            "message",
        ]

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if not log_record.get("time"):
            now = arrow.now().to("Asia/Tokyo").replace(microsecond=0).isoformat()
            log_record["time"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname


def init_logger():
    formatter = JsonFormatter()

    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logger = logging.getLogger(_log)
        logger.propagate = False

        for h in logger.handlers:
            h.setFormatter(formatter)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            logger.addHandler(handler)
