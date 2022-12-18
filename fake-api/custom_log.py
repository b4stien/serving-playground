from datetime import datetime
import logging
import sys
from typing import Set

from custom_json import dumps


class JSONLineFormatter(object):
    def __init__(self, *, key_order, with_default_order=True):
        if not isinstance(key_order, dict):
            raise TypeError(
                "This formatter has to be instantiated with a dict "
                "describing how to sort keys in JSON dumped "
                "dictionnary."
            )
        if with_default_order:
            key_order = {**key_order, "logger": -10, "datetime": -9}
        self._key_order = key_order

    def _item_sort_key(self, key_value):
        key, _ = key_value
        return self._key_order.get(key, 99)

    def format(self, record):
        will_log = {}
        if isinstance(record.msg, str):
            will_log_msg = record.msg
            if record.args and isinstance(record.args, tuple):
                will_log_msg = record.msg % record.args
            will_log["message"] = will_log_msg
        elif isinstance(record.msg, dict):
            will_log = {**will_log, **record.msg}
        else:
            raise NotImplementedError(
                "The formatter (`JSONLineFormatter`) attached to this "
                "logger only knows how to log dicts (or strings which "
                "will be converted to dicts) dumped into json strings."
            )

        will_log["logger"] = record.name
        will_log["datetime"] = datetime.now()

        try:
            return dumps(will_log, item_sort_key=self._item_sort_key)
        except TypeError as e:
            raise ValueError(
                f"The dict you provided could not be serialized to JSON "
                f'using `json`. Original error was: "{e}".'
            )


def make_handler(key_order=None, stream=sys.stdout):
    if key_order is None:
        key_order = {}
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONLineFormatter(key_order=key_order))
    return handler


# Keep track of already configured loggers to avoid putting two
# or more handlers on the same logger.
_has_been_set_loggers: Set[str] = set()


def get_logger(
    logger_name,
    *,
    level=logging.INFO,
    default_handler=True,
    propagate=False,
    handlers=None,
):
    logger = logging.getLogger(logger_name)

    if logger_name in _has_been_set_loggers:
        return logger

    logger.propagate = propagate
    logger.setLevel(level)
    if default_handler:
        logger.addHandler(make_handler())
    if handlers:
        for h in handlers:
            logger.addHandler(h)

    _has_been_set_loggers.add(logger_name)

    return logger
