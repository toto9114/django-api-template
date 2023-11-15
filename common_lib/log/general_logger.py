import logging
import socket
import sys
import os
from typing import Union
from logging import handlers
from os.path import join
from pathlib import Path
from datetime import datetime
from pythonjsonlogger import jsonlogger

from .handler import CustomSocketHandler
from _version import __version__


class CustomDatadogFormatter(jsonlogger.JsonFormatter):
    APP_NAME = None
    PROCESS_NUM: int = 0
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
        log_record["appName"] = self.APP_NAME

        log_record["version"] = __version__
        log_record["process_num"] = self.PROCESS_NUM
        log_record["event"] = log_record.get("event", "log")


def initialize_logger(
    app_name: str,
    log_dir: str,
    rotation_day: int = 7,
    process_num: int = 0,
    log_level: str = "INFO",
    tcp_host: Union[str, None] = None,
    tcp_port: Union[int, None] = None,
    extra_default: Union[dict, None] = None,
):
    """
    logger를 초기화합니다.
    :param app_name: (필수) APP_NAME 및 logger name
    :param log_dir: (필수) log가 저장될 디렉터리
    :param rotation_day: (선택, 기본값=7) 로그 회전주기 (일 단위)
    :param process_num: (선택, 기본값=0) 여러 프로세스가 실행될 경우 프로세스의 번호
    :param log_level: (선택, 기본값=INFO) log level
    :param tcp_host: (선택) TCP 방식 (Datadog) Log Agent Host
    :param tcp_port: (선택) TCP 방식 (Datadog) Log Agent Port
    :param extra_default: (선택) Logger에 항상 기록될 값
    :return:
    """
    # json_formatter = CustomJsonFormatter('(timestamp) (level) (name) (taggerVersion) (reqId) (companyId) (message)')
    log_format = "%(asctime)-15s {hostname} %(name)s {process_num} %(levelname)-6s %(message)s".format(
        process_num=process_num, hostname=socket.gethostname()
    )
    formatter = logging.Formatter(log_format)

    log_level_str = str(log_level).upper()
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

    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)

    # Rotating File Handler
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    fh_file = handlers.TimedRotatingFileHandler(
        filename=join(log_dir, "%s.%1d.log" % (app_name, process_num)),
        when="D",
        backupCount=rotation_day,
    )
    fh_file.setLevel(log_level)
    fh_file.setFormatter(formatter)
    logger.addHandler(fh_file)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # Stream Handler
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    # TCP (Datadog) Handler
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    if tcp_host is not None and tcp_port is not None:
        data_dog_formatter = CustomDatadogFormatter(
            "%(timestamp)s %(message)s %(level)s %(name)s %(version)s"
        )
        CustomDatadogFormatter.APP_NAME = app_name
        CustomDatadogFormatter.PROCESS_NUM = process_num
        CustomDatadogFormatter.EXTRA = extra_default

        tcp_handler = CustomSocketHandler(host=tcp_host, port=tcp_port)
        tcp_handler.setLevel(log_level)
        tcp_handler.setFormatter(data_dog_formatter)
        logger.addHandler(tcp_handler)
    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
