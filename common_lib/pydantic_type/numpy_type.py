import numpy as np
from pydantic import BaseModel


class TypedNpArray(np.ndarray):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_type

    @classmethod
    def validate_type(cls, val):
        return np.array(val, dtype=cls.inner_type)


class NpArrayMeta(type):
    def __getitem__(self, t):
        return type("NpArray", (TypedNpArray,), {"inner_type": t})


class NpArray(np.ndarray, metaclass=NpArrayMeta):
    pass


# 사용 예시
class Model(BaseModel):
    values: NpArray[float]
