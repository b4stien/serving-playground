import time
import wsgiref.util

from flask import Flask

from custom_log import get_logger


class CustomFlaskApp(Flask):
    logger = get_logger("flask")


http_logger = get_logger("flask_http")


class LoggingMiddleware(object):
    """Gather and log every available bits of informations."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Log incoming HTTP request
        base_will_log = {
            "log_moment": "before",
            "method": environ.get("REQUEST_METHOD"),
            "uri": wsgiref.util.request_uri(environ),
        }

        will_log = {**base_will_log}
        http_logger.info(will_log)

        def fake_start_response(status, headers, exc_info=None):
            # Log our response to the HTTP request, reuse the first
            # log item
            will_log = {**base_will_log}
            will_log["log_moment"] = "after"
            will_log["status_code"] = int(status.split(" ")[0])

            http_logger.info(will_log)

            return start_response(status, headers, exc_info)

        return self.app(environ, fake_start_response)


flask_app = CustomFlaskApp(__name__)


@flask_app.route("/ok")
def ok():
    time.sleep(1)
    return "Ok"


@flask_app.route("/sleep-9")
def sleep_9():
    time.sleep(9)
    return "Slept 9"


@flask_app.route("/boom")
def boom():
    raise Exception("Boom")


logged_flask_app = LoggingMiddleware(flask_app)
