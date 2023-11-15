import os
from typing import Optional, Type
from distutils.util import strtobool


class MissingRequiredEnvironmentVariable(Exception):
    def __init__(self, env_name: str):
        _message = f"Missing Required Environment Variable '{env_name}'"
        Exception.__init__(self, _message)
        self.message = _message
        self.env_name = env_name


def load_env(
    env_name: str,
    default: Optional[str] = None,
    required: bool = False,
    as_type: Optional[Type] = None,
) -> Optional[any]:
    if not (isinstance(default, str) or (default is None)):
        raise TypeError(f"type of default allowed only str (current: {type(default)})")

    env_val = os.environ.get(env_name, default)
    if required is True and env_val is None:
        raise MissingRequiredEnvironmentVariable(env_name)

    if as_type is not None and env_val is not None:
        if as_type is bool:
            if str(env_val).upper() in ("TRUE", "YES", "Y", "T"):
                return True
            else:
                return bool(strtobool(str(env_val)))
        return as_type(env_val)
    return env_val
