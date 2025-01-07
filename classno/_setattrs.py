import typing as t

from classno import _casting
from classno import _validation
from classno import constants as c


def private_name_retrieval(self, name: str) -> str:
    if name in self.__fields__:
        raise Exception("privates only")

    if name.startswith("_") and name[1:] not in self.__fields__:
        raise Exception(f"Attr {name} not found")

    return name[1:]


def frozen_handler(self, name: str, value: t.Any) -> t.Never:
    raise Exception(f"Cannot modify attrs of class {self.__class__.__name__}")


def validation_handler(self, name: str, value: t.Any) -> None:
    field = self.__fields__[name]
    try:
        _validation.validate_value_hint(value, field.hint)
    except TypeError:
        raise TypeError(
            f"For field {field.name} expected type of {field.hint}, "
            f"got {value} of type {type(value)}"
        )

    return name, value


def lossy_autocast_handler(self, name: str, value: t.Any) -> tuple[str, t.Any]:
    field = self.__fields__[name]
    casted_value = _casting.cast_value(value, field.hint)
    return name, casted_value


# NOTE(kuderr): order is important here
_NAME_RETRIEVALS = {
    c.Features.PRIVATE: private_name_retrieval,
}

# NOTE(kuderr): order is important here
_HANDLERS = {
    c.Features.FROZEN: frozen_handler,
    c.Features.LOSSY_AUTOCAST: lossy_autocast_handler,
    c.Features.VALIDATION: validation_handler,
}


def setattr_processor(self, name: str, value: t.Any) -> None:
    for feature, func in _NAME_RETRIEVALS.items():
        if feature in self.__features__:
            name = func(self, name)
            break

    for feature, func in _HANDLERS.items():
        if feature in self.__features__:
            name, value = func(self, name, value)

    return object.__setattr__(self, name, value)
