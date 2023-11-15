from common_lib.errors.exception import ManagedErrorWithExtraInfo
from common_lib.error_codes.validate.validate_error import ValidateErrorCommonStatus
import ujson as json
from types import GenericAlias
from typing import Union


class DataclassValidations:
    @staticmethod
    def isfloat(num: str):
        try:
            float(num)
            return True
        except Exception:
            return False

    @staticmethod
    def isinteger(num: str):
        if num.lstrip("+-").isnumeric():
            return True
        else:
            return False

    def _validate_number_in_str(self, value: str):
        return_val = value
        if self.isinteger(value):
            return_val = int(value)
        elif self.isfloat(value):
            return_val = float(value)
        return return_val

    def _validate_boolean_in_str(self, value: str):
        return_val = value
        if value.lower() in ["true", "false"]:
            return_val = json.loads(value.lower())
        return return_val

    def _validate_string(self, _type, variable_value):
        return_val = variable_value
        if isinstance(return_val, str):
            if _type in [int, float]:
                return_val = self._validate_number_in_str(return_val)
            elif _type == bool:
                return_val = self._validate_boolean_in_str(return_val)
        if _type == str:
            return_val = str(return_val)
        return return_val

    def _validate_number(self, _type, value):
        if _type == float:
            if isinstance(value, int):
                return float(value)
        if _type == int:
            if isinstance(value, float):
                return int(value)
        return value

    @staticmethod
    def _type_checking(name, _type, variable_value):
        if type(variable_value) != _type:
            if getattr(_type, "__origin__", None):
                if _type.__origin__ == Union:
                    if type(variable_value) == dict:
                        return
                    sub_types = _type.__args__
                    for sub_type in sub_types:
                        if type(variable_value) == sub_type:
                            return
            error = ValidateErrorCommonStatus.WRONG_TYPE
            error.message = error.message.format(name, type(variable_value), _type)
            raise ManagedErrorWithExtraInfo(error)

    def _type_recursive(self, name, _type, value):
        if type(_type) == GenericAlias:
            if _type.__origin__ == list:
                if isinstance(value, list):
                    sub_type = _type.__args__
                    return [self._type_recursive(name, sub_type[0], x) for x in value]
            elif _type.__origin__ == tuple:
                if isinstance(value, tuple):
                    sub_type = _type.__args__
                    return tuple(
                        self._type_recursive(name, sub_type[0], x) for x in value
                    )
            elif _type.__origin__ == dict:
                if isinstance(value, dict):
                    sub_type = _type.__args__
                    return {
                        self._type_recursive(
                            name, sub_type[0], key
                        ): self._type_recursive(name, sub_type[1], val)
                        for key, val in value.items()
                    }
        else:
            value = self._validate_number(_type, value)
            _ret_val = self._validate_string(_type, value)
            self._type_checking(name, _type, _ret_val)
            return _ret_val

    def __post_init__(self):
        """Run validation methods if declared.
        The validation method can be a simple check
        that raises ValueError or a transformation to
        the field value.
        The validation is performed by calling a function named:
            `validate_<field_name>(self, value, field) -> field.type`
        """

        for name, field in self.__dataclass_fields__.items():
            method = getattr(self, f"validate_{name}", None)
            variable_value = getattr(self, name)
            if field.type.__name__ not in ["Optional", "Any"]:
                variable_value = self._type_recursive(name, field.type, variable_value)
                setattr(self, name, variable_value)
            if method:
                setattr(self, name, method(variable_value, field=field))
