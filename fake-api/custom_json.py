"""Tooling around JSON.

Mainly add `datetime.datetime` and `uuid.UUID` to serializable types.
Hugely inspired by Flask own internal JSONEncoder.

"""
import datetime
from functools import partial
import uuid

import simplejson
import simplejson.errors


class UnrecognizedType(TypeError):
    pass


def oh_to_jsonable_key(key):
    """Cast a variable to an acceptable jsonable key."""
    if isinstance(key, str):
        return str
    if isinstance(key, uuid.UUID):
        return str(key)
    raise UnrecognizedType(
        f"Unknown given key type  `{type(key)}`, can't transform into a jsonable key."
    )


def oh_to_jsonable_value(value, *, recurse=False):
    """Transform "anything" into a "jsonable thing".

    A "jsonable thing" is an object that can trivially be transformed
    into JSON, specced here https://www.json.org/json-en.html.

    As far as we're concerned, in Python land, a "jsonable thing" is
    any object made from the combination of primitive values - strings,
    booleans, numbers (int or float), None - dicts and lists.

    In addition, a dict in such a "jsonable thing" must have strings
    (and only strings) as keys.

    """
    # Our custom hook
    if hasattr(value, "_oh_to_jsonable_value"):
        return value._oh_to_jsonable_value(recurse=recurse)

    # Iterables
    if isinstance(value, (tuple, list, set)):
        return list(
            [oh_to_jsonable_value(i, recurse=True) if recurse else i for i in value]
        )

    # Dicts
    if isinstance(value, dict):
        return {
            oh_to_jsonable_key(k): oh_to_jsonable_value(v, recurse=True)
            if recurse
            else v
            for k, v in value.items()
        }

    # Primitive JSON values
    if isinstance(value, (str, int, float, bool)):
        return value
    if value is None:
        return value

    # Special values that we know how to transform
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if isinstance(value, datetime.date):
        return value.isoformat()
    if isinstance(value, uuid.UUID):
        return str(value)

    raise UnrecognizedType(
        f"Unknown given value type `{type(value)}`, can't transform into a jsonable value."
    )


class JSONEncoder(simplejson.JSONEncoder):
    def default(self, o):
        """Beware, this is run *after* simplejson has tried to encode
        the value, meaning if it succeeds in serializing `o`, this code
        won't run.

        Consequently, we can't change how an already serializable `o`
        will be serialized. We can't impact how the keys are going to
        be serialized either, this "hook" will only be run on values.

        To overcome these two limitations, one can use
        `oh_to_jsonable_value` "before" attempting a `json.dumps`.

        """
        if hasattr(o, "_oh_to_json"):
            return o._oh_to_json()

        try:
            return oh_to_jsonable_value(o, recurse=False)
        except UnrecognizedType:
            pass

        return simplejson.JSONEncoder.default(self, o)


dumps = partial(simplejson.dumps, use_decimal=True, cls=JSONEncoder)
loads = partial(simplejson.loads, use_decimal=True)

JSONDecodeError = simplejson.errors.JSONDecodeError
