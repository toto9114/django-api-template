import logging
import socket
import os
from typing import Union
from datetime import datetime
from pathlib import Path
from os.path import join

from flask import Flask, current_app, request
from pythonjsonlogger import jsonlogger

from .handler import CustomSocketHandler
from _version import __version__


class CustomDatadogFormatter(jsonlogger.JsonFormatter):
    EXTRA: Union[dict, None] = None

    def add_fields(self, log_record, record, message_dict):
        super(CustomDatadogFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            # this doesn't use record.created, so it is slightly off
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname

        if self.EXTRA is not None and isinstance(self.EXTRA, dict):
            for key, value in self.EXTRA.items():
                log_record[key] = value

        log_record["hostname"] = socket.gethostname()
        log_record["pid"] = os.getpid()
        log_record["reqId"] = log_record.get("reqId", None)
        log_record["companyId"] = log_record.get("companyId", None)
        log_record["appName"] = current_app.config["APP_NAME"]

        log_record["version"] = __version__
        log_record["request"] = {
            "header": dict(request.headers),
            "url": request.url,
            "path": request.path,
            "method": request.method,
            "params": dict(request.args),
        }

        log_record["response"] = log_record.get("response", None)
        log_record["event"] = log_record.get("event", "log")


def get_logger(app_name=None):
    return logging.getLogger(app_name if app_name else current_app.config["APP_NAME"])


def initialize_logger(app: Flask):
    pid = os.getpid()
    log_format = (
        "%(asctime)-15s {hostname} %(name)s {pid} %(levelname)-6s %(message)s".format(
            pid=pid, hostname=socket.gethostname()
        )
    )
    formatter = logging.Formatter(log_format)
    log_level_str = str(app.config["LOG_LEVEL"]).upper()
    if log_level_str == "DEBUG":
        log_level = logging.DEBUG
    elif log_level_str == "INFO":
        log_level = logging.INFO
    elif log_level_str == "WARNING" or log_level_str == "WARN":
        log_level = logging.WARN
    elif log_level_str == "ERROR":
        log_level = logging.ERROR
    else:
        log_level = logging.NOTSET

    logger = logging.getLogger(app.config["APP_NAME"])
    logger.setLevel(log_level)

    if "LOGGER_HOST" in app.config.keys():
        logger_host = app.config["LOGGER_HOST"]
    elif "LOG_HOST" in app.config.keys():
        logger_host = app.config["LOG_HOST"]
    else:
        logger_host = None

    if "LOGGER_PORT" in app.config.keys():
        logger_port = int(app.config["LOGGER_PORT"])
    elif "LOG_PORT" in app.config.keys():
        logger_port = int(app.config["LOG_PORT"])
    else:
        logger_port = None

    # TCP (Datadog) Handler
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if logger_host is not None:
        data_dog_formatter = CustomDatadogFormatter(
            "%(timestamp)s %(message)s %(level)s %(name)s %(version)s %(reqId)s %(companyId)s %(response)s"
        )
        tcp_handler = CustomSocketHandler(host=logger_host, port=logger_port)
        tcp_handler.setLevel(log_level)
        tcp_handler.setFormatter(data_dog_formatter)
        logger.addHandler(tcp_handler)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Rotating File Handler
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Path(app.config["LOG_DIR"]).mkdir(parents=True, exist_ok=True)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=join(app.config["LOG_DIR"], f'{app.config["APP_NAME"]}.{pid}.log'),
        when="D",
        backupCount=7,
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Console Handler
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if app.config.get("LOG_CONSOLE"):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
