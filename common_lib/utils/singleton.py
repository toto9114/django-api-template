from typing import ClassVar, Dict, TypeVar, Type
from functools import wraps
from abc import ABC


C = TypeVar("C")


def singleton(class_):
    class class_w(class_):
        _instance: ClassVar[Dict[str, class_]] = {}

        def __new__(class_, name: str = "default", *args, **kwargs):
            identifier = f"{class_.__name__}:{name}"

            if identifier not in class_w._instance.keys():
                class_w._instance[identifier] = super(class_w, class_).__new__(
                    class_, *args, **kwargs
                )
                class_w._instance[identifier]._sealed = False
            return class_w._instance[identifier]

        def __init__(self, *args, **kwargs):
            if self._sealed:
                return

            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True

    class_w.__name__ = class_.__name__
    return class_w


class Singleton(ABC):
    _instance: ClassVar[Dict[str, Type[C]]] = {}

    def __new__(cls, name: str = "default", *args, **kwargs) -> C:
        identifier = f"{cls.__name__}:{name}"

        if identifier not in cls._instance.keys():
            cls._instance[identifier] = super(Singleton, cls).__new__(
                cls, *args, **kwargs
            )
        return cls._instance[identifier]


def initialize_once(init_method):
    @wraps(init_method)
    def _impl(self, name: str = "default", *method_args, **method_kwargs):
        initialized = getattr(self, "__initialized", False)
        if initialized:
            return
        else:
            self.__initialized = True
            return init_method(self, name, *method_args, **method_kwargs)

    return _impl
