import contextlib
import types
import typing as t
import collections

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
                f"For field {field.name}, expected {field.hint} "
                + f"but got {attr!r} of type {type(attr)}"
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


def validate_frozenset(value, hint):
    """Validate frozenset types."""
    tp, *_ = t.get_args(hint)
    for el in value:
        validate_value_hint(el, tp)


def validate_deque(value, hint):
    """Validate collections.deque types."""
    tp, *_ = t.get_args(hint)
    for el in value:
        validate_value_hint(el, tp)


VALIDATION_ORIGIN_HANDLER = {
    dict: validate_dict,
    list: validate_collection,
    set: validate_collection,
    tuple: validate_tuple,
    frozenset: validate_frozenset,
    collections.deque: validate_deque,
    # Dict-like collections can reuse the dict validator
    collections.defaultdict: validate_dict,
    collections.OrderedDict: validate_dict,
    collections.Counter: validate_dict,
}


def validate_value_hint(value, hint):
    origin = t.get_origin(hint)
    
    # Handle Union types (both typing.Union and types.UnionType)
    if isinstance(hint, types.UnionType) or origin is t.Union:
        for sub_hint in t.get_args(hint):
            with contextlib.suppress(TypeError):
                validate_value_hint(value, sub_hint)
                return
        raise TypeError

    # Simple type: int, bool, str, CustomClass, etc.
    if not origin and not isinstance(value, hint):
        raise TypeError

    if origin and not isinstance(value, origin):
        raise TypeError

    if origin:
        handler = VALIDATION_ORIGIN_HANDLER.get(origin)
        if handler:
            handler(value, hint)
        else:
            # Fallback for unknown collection types
            # If it's iterable but not str/bytes, try to validate as collection
            if hasattr(origin, '__iter__') and not issubclass(origin, (str, bytes)):
                validate_collection(value, hint)
            else:
                raise TypeError(f"No validation handler for type {origin}")
