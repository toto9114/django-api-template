import abc
from dataclasses import dataclass, _MISSING_TYPE
from types import GenericAlias
from apispec.exceptions import DuplicateComponentNameError
from typing import TypeVar, Generic, Any


from enum import EnumMeta


T = TypeVar("T")


class ApiSpecSchema:
    def __init__(self, spec, default_value_none: bool = False):
        self.spec = spec
        self.default_value_none = default_value_none

    def add_schema(self, cls: dataclass):
        schema = {"properties": {}}
        if "__dataclass_fields__" not in dir(cls):
            return
        for name, field in cls.__dataclass_fields__.items():
            _type = field.type
            default_value = (
                None if type(field.default) in [_MISSING_TYPE] else field.default
            )
            if default_value is None:
                default_value = (
                    None
                    if type(field.default_factory) in [_MISSING_TYPE]
                    else field.default_factory
                )
            schema["properties"][name] = self._generate_schema(
                _type=_type, default_value=default_value
            )
        try:
            class_name = cls.__name__
            self.spec.components.schema(class_name, schema)
        except DuplicateComponentNameError:
            pass

    def _add_number(self, optional_status, default_value):
        schema = {"type": "number"}
        if optional_status:
            schema["nullable"] = True
        if default_value:
            schema["default"] = default_value
            if self.default_value_none:
                schema["default"] = None
        return schema

    def _add_str(self, optional_status, default_value):
        schema = {
            "type": "string",
        }
        if optional_status:
            schema["nullable"] = True
        if default_value:
            schema["default"] = default_value
            if self.default_value_none:
                schema["default"] = None
        return schema

    def _add_dict(self, optional_status):
        schema = {"type": "object"}
        if optional_status:
            schema["nullable"] = True
            if self.default_value_none:
                schema["default"] = None
        return schema

    # TODO: Enum
    def _add_enum(self, field_type, optional_status):
        enum_list = []
        enum_type = None
        for _enum in field_type:
            enum_list.append(_enum.value)
            enum_type = str(type(_enum.value))
        schema = {"type": enum_type, "enum": enum_list}
        if optional_status:
            schema["nullable"] = True
            if self.default_value_none:
                schema["default"] = None
        return schema

    def _add_bool(self, optional_status, default_value):
        schema = {"type": "boolean"}
        if default_value:
            schema["default"] = default_value
        if optional_status:
            schema["nullable"] = True
            if self.default_value_none:
                schema["default"] = None
        return schema

    @staticmethod
    def _check_dataclass(field_type):
        if isinstance(field_type, abc.ABCMeta):
            return True
        return False

    @staticmethod
    def _check_optional(field_type):
        if field_type.__name__ == "Optional":
            return True
        return False

    def _add_dataclass(self, field_type, optional_status):
        self.add_schema(field_type)
        if optional_status:
            if self.default_value_none:
                return {
                    "$ref": f"#/components/schemas/{str(field_type.__name__)}",
                    "nullable": True,
                    "default": None,
                    "type": "object",
                }
            return {
                "$ref": f"#/components/schemas/{str(field_type.__name__)}",
                "nullable": True,
                "type": "object",
            }
        return {
            "$ref": f"#/components/schemas/{str(field_type.__name__)}",
            "type": "object",
        }

    def _add_list(self, field_type, optional_status, default_value):
        sub_type = field_type.__args__
        schema = {
            "type": "array",
            "items": {
                "allOf": [
                    self._generate_schema(_type=type, default_value=None)
                    for type in sub_type
                ]
            },
        }
        if default_value == list:
            schema["default"] = list()
        if optional_status:
            schema["nullable"] = True
            if self.default_value_none:
                schema["default"] = None
        return schema

    def _add_tuple(self, field_type, optional_status, default_value):
        sub_type = field_type.__args__
        schema = {
            "type": "array",
            "items": {
                "oneOf": [self._generate_schema(_type=type) for type in sub_type],
                "maxItems": len(sub_type),
                "minItems": len(sub_type),
            },
        }
        if default_value:
            schema["default"] = default_value
        if optional_status:
            schema["nullable"] = True
            if self.default_value_none:
                schema["default"] = None
        return schema

    def _add_any(self, optional_status, default_value):
        schema = {
            "anyOf": [
                {"type": "string"},
                {"type": "number"},
                {"type": "boolean"},
                {"type": "array"},
                {"type": "object"},
            ]
        }
        if default_value:
            schema["default"] = default_value
        if optional_status:
            schema["nullable"] = True
            if self.default_value_none:
                schema["default"] = None
        return schema

    def _add_union(self, field_type):
        field_type_args = field_type.__args__
        schema = {"type": "object", "oneOf": []}
        for field_type_ele in field_type_args:
            self.add_schema(field_type_ele)
            schema["oneOf"].append(self._generate_schema(field_type_ele))
        return schema

    def _generate_schema(self, _type: Generic[T], default_value=None):
        optional = self._check_optional(field_type=_type)
        _type = _type.__args__[0] if optional else _type

        if str(type(default_value)) == "<class 'function'>":
            default_value = None

        if type(_type) is GenericAlias or _type.__name__ == "List":
            if _type.__origin__ == list or _type.__name__ == "List":
                return self._add_list(
                    field_type=_type,
                    optional_status=optional,
                    default_value=default_value,
                )
            if _type.__origin__ is tuple:
                return self._add_tuple(
                    field_type=_type,
                    optional_status=optional,
                    default_value=[default_value],
                )
            if _type.__origin__ is dict:
                return self._add_dict(optional_status=optional)
        elif _type is bool:
            return self._add_bool(optional_status=optional, default_value=default_value)
        # Todo: Enum
        elif type(_type) is EnumMeta:
            return self._add_enum(field_type=_type, optional_status=optional)
        elif _type is Any:
            return self._add_any(optional_status=optional, default_value=default_value)
        elif _type.__name__ == "Union":
            return self._add_union(field_type=_type)
        else:
            check_dataclass_status = self._check_dataclass(field_type=_type)
            if check_dataclass_status:
                return self._add_dataclass(
                    field_type=_type,
                    optional_status=optional,
                )
            else:
                if _type.__name__ in ["int", "float"]:
                    return self._add_number(
                        optional_status=optional, default_value=default_value
                    )
                return self._add_str(
                    optional_status=optional, default_value=default_value
                )
