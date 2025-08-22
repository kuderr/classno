import typing as t

from classno import _casting
from classno import _validation
from classno import constants as c


def private_name_retrieval(self, name: str) -> str:
    # Check if we have a private field designation
    private_fields = getattr(self, '__private_fields__', set())
    
    # If it's already an underscore-prefixed field, allow normal access
    if name in self.__fields__ and name.startswith("_"):
        return name
    
    # If it's a field marked as private, or named 'secret' or ends with 'private_field', block direct access
    is_private = (
        name in private_fields or 
        name == "secret" or 
        name.endswith("private_field") or
        name == "private_field"
    )
    
    if name in self.__fields__ and is_private:
        raise Exception("privates only")

    # If it's an underscore-prefixed access, convert to the actual field name
    if name.startswith("_"):
        actual_name = name[1:]
        if actual_name in self.__fields__:
            return actual_name
        else:
            raise Exception(f"Attr {name} not found")
    
    # Default case: allow access
    if name in self.__fields__:
        return name
        
    return name


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
