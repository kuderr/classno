import contextlib
import types
import typing as t
from classno import exceptions as excs


def validate_fields(obj):
    fields = obj.__fields__
    errors = []

    for field in fields.values():
        attr = getattr(obj, field.name)
        try:
            validate_value_hint(attr, field.hint)
        except TypeError:
            errors.append(
                f"For field {field.name}, expected {field.hint} but got {attr!r} of type {type(attr).__name__}"
            )

    if errors:
        raise excs.ValidationError(errors)


def validate_dict(value, hint):
    keys_type, val_type = t.get_args(hint)
    for key in value:
        if not isinstance(key, keys_type):
            raise TypeError

    for val in value.values():
        validate_value_hint(val, val_type)


def validate_collection(value, hint):
    tp, *_ = t.get_args(hint)
    for el in value:
        validate_value_hint(el, tp)


def validate_tuple(value, hint):
    tps = t.get_args(hint)
    if len(tps) == 2 and tps[-1] is Ellipsis:
        tp = tps[0]
        for el in value:
            validate_value_hint(el, tp)
        return

    if len(tps) != len(value):
        raise TypeError

    for tp, val in zip(tps, value):
        validate_value_hint(val, tp)


VALIDATION_ORIGIN_HANDLER = {
    dict: validate_dict,
    list: validate_collection,
    set: validate_collection,
    tuple: validate_tuple,
}


def validate_value_hint(value, hint):
    # Unions: str | None, int | float, etc.
    if isinstance(hint, types.UnionType):
        for sub_hint in t.get_args(hint):
            with contextlib.suppress(TypeError):
                validate_value_hint(value, sub_hint)
                return

        raise TypeError

    origin = t.get_origin(hint)

    # Simple type: int, bool, str, CustomClass, etc.
    if not origin and not isinstance(value, hint):
        raise TypeError

    if origin and not isinstance(value, origin):
        raise TypeError

    if origin:
        VALIDATION_ORIGIN_HANDLER[origin](value, hint)
