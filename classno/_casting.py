import contextlib
import types
import typing as t

from classno import exceptions as excs


def cast_fields(obj):
    fields = obj.__fields__
    errors = []

    for field in fields.values():
        attr = getattr(obj, field.name)
        try:
            attr = cast_value(attr, field.hint)
            object.__setattr__(obj, field.name, attr)
        except TypeError:
            errors.append(
                f"For field {field.name}, failed to cast value {attr!r} "
                + f"of type {type(attr)} to {field.hint}"
            )

    if errors:
        raise excs.CastingError(errors)


def cast_dict(value, hint):
    keys_type, val_type = t.get_args(hint)
    for key in value:
        if not isinstance(key, keys_type):
            raise TypeError

    new_dict = {}
    for key, val in value.items():
        new_dict[key] = cast_value(val, val_type)

    return new_dict


def cast_collection(value, hint):
    new_collection = []
    tp, *_ = t.get_args(hint)
    for el in value:
        new_collection.append(cast_value(el, tp))

    return hint(new_collection)


def cast_tuple(value, hint):
    new_value = []
    tps = t.get_args(hint)
    if len(tps) == 2 and tps[-1] is Ellipsis:
        tp = tps[0]
        for el in value:
            new_value.append(cast_value(el, tp))
        return tuple(new_value)

    if len(tps) != len(value):
        raise TypeError

    for tp, val in zip(tps, value):
        new_value.append(cast_value(val, tp))

    return tuple(new_value)


CASTING_ORIGIN_HANDLER = {
    dict: cast_dict,
    list: cast_collection,
    set: cast_collection,
    tuple: cast_tuple,
}


def cast_value(value, hint):
    origin = t.get_origin(hint)

    # Unions: str | None, int | float, etc.
    if isinstance(hint, types.UnionType):
        for sub_hint in t.get_args(hint):
            with contextlib.suppress(TypeError):
                return cast_value(value, sub_hint)

        raise TypeError

    # Simple type: int, bool, str, CustomClass, etc.
    if not origin and not isinstance(value, hint):
        return hint(value)

    if origin:
        return CASTING_ORIGIN_HANDLER[origin](value, hint)

    if isinstance(value, hint):
        return value
