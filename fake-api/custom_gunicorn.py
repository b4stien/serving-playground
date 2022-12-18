import logging
import os

from gunicorn.app.base import Application
from gunicorn.config import Config
from gunicorn.workers.sync import SyncWorker

from flask_app import logged_flask_app
from custom_log import get_logger

LOG_LEVELS = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


prefork_logger = get_logger("gunicorn.prefork")
postfork_logger = get_logger("gunicorn.postfork")


class GunicornLogger(object):
    def __init__(self, cfg):
        self._internal_logger = prefork_logger

    def critical(self, msg, *args, **kwargs):
        self._internal_logger.critical(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._internal_logger.error(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._internal_logger.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self._internal_logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._internal_logger.debug(msg, *args, **kwargs)

    def exception(self, msg, *args, **kwargs):
        self._internal_logger.exception(msg, *args, **kwargs)

    def access(self, resp, req, environ, request_time):
        self._internal_logger.info(
            {
                "status_code": resp.status_code,
                "path": req.path,
                "method": req.method,
                "time_ms": int(request_time.total_seconds() * 1000),
            }
        )

    def close_on_exec(self):
        pass


class CustomGunicornApplication(Application):
    def __init__(self, *, usage=None, prog=None, socket):
        self.__socket = socket
        super().__init__(usage, prog)

    def do_load_config(self):
        self.cfg = Config()
        self.cfg.set("bind", self.__socket)
        self.cfg.set("workers", 1)
        self.cfg.set("logger_class", GunicornLogger)
        self.cfg.set("timeout", 5)
        self.cfg.set(
            "pre_fork", lambda arbitrer, prefork_worked: print("Yo", os.getpid())
        )
        self.cfg.set(
            "post_fork",
            lambda foo, postfork_worked: setattr(
                postfork_worked.log, "_internal_logger", postfork_logger
            ),
        )

    def load(self):
        return logged_flask_app
