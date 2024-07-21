import typing as t

from classno import _casting
from classno import _validation


def private_validated_setattr(self, name: str, value: t.Any) -> None:
    if name in self.__fields__:
        raise Exception("privates only")

    if name.startswith("_") and name[1:] not in self.__fields__:
        raise Exception(f"Attr {name} not found")

    field = self.__fields__[name[1:]]
    try:
        _validation.validate_value_hint(value, field.hint)
    except TypeError:
        raise TypeError(
            f"For field {field.name} expected type of {field.hint}, "
            f"got {value} of type {type(value)}"
        )

    return super(self.__class__, self).__setattr__(name, value)


def validated_setattr(self, name: str, value: t.Any) -> None:
    if name not in self.__fields__:
        raise Exception(f"Attr {name} not found")

    field = self.__fields__[name]
    try:
        _validation.validate_value_hint(value, field.hint)
    except TypeError:
        raise TypeError(
            f"For field {field.name} expected type of {field.hint}, "
            f"got {value} of type {type(value)}"
        )

    return super(self.__class__, self).__setattr__(name, value)


def lossy_autocast_setattr(self, name: str, value: t.Any) -> None:
    if name not in self.__fields__:
        raise Exception(f"Attr {name} not found")

    field = self.__fields__[name]
    casted_value = _casting.cast_value(value, field.hint)
    return super(self.__class__, self).__setattr__(name, casted_value)


def raise_frozen_attr_exc(self, *args, **kwargs):
    raise Exception(f"Cannot modify attrs of class {self.__class__.__name__}")


def privates_setattr(self, name: str, value: t.Any) -> None:
    if name in self.__fields__:
        raise Exception("privates only")

    if name.startswith("_") and name[1:] in self.__fields__:
        return super(self.__class__, self).__setattr__(name[1:], value)

    return super(self.__class__, self).__setattr__(name, value)
