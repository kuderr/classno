import contextlib
import types
import typing as t
import collections

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

    # Use the origin type to construct the collection
    origin = t.get_origin(hint) or hint
    return origin(new_collection)


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


def cast_frozenset(value, hint):
    """Cast to frozenset type."""
    tp, *_ = t.get_args(hint)
    new_set = set()
    for el in value:
        new_set.add(cast_value(el, tp))
    return frozenset(new_set)


def cast_deque(value, hint):
    """Cast to collections.deque type."""
    tp, *_ = t.get_args(hint)
    new_deque = collections.deque()
    for el in value:
        new_deque.append(cast_value(el, tp))
    return new_deque


CASTING_ORIGIN_HANDLER = {
    dict: cast_dict,
    list: cast_collection,
    set: cast_collection,
    tuple: cast_tuple,
    frozenset: cast_frozenset,
    collections.deque: cast_deque,
    # Dict-like collections can reuse the dict caster
    collections.defaultdict: cast_dict,
    collections.OrderedDict: cast_dict,
    collections.Counter: cast_dict,
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
        try:
            return hint(value)
        except (ValueError, TypeError) as e:
            raise TypeError(f"Cannot cast {value} to {hint}: {e}") from e

    if origin:
        handler = CASTING_ORIGIN_HANDLER.get(origin)
        if handler:
            return handler(value, hint)
        else:
            # Fallback for unknown collection types
            # If it's iterable but not str/bytes, try to cast as collection
            if hasattr(origin, '__iter__') and not issubclass(origin, (str, bytes)):
                return cast_collection(value, hint)
            else:
                raise TypeError(f"No casting handler for type {origin}")

    if isinstance(value, hint):
        return value
    
    # This should never be reached, but explicit is better than implicit
    raise TypeError(f"Unable to cast {value} of type {type(value)} to {hint}")
