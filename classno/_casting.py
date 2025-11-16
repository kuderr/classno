import collections
import contextlib
import types
import typing as t

from classno import _errors
from classno import exceptions as excs


def cast_fields(obj):
    fields = obj.__fields__
    errors = []

    for field in fields.values():
        attr = getattr(obj, field.name)
        try:
            attr = cast_value(attr, field.hint)
            object.__setattr__(obj, field.name, attr)
        except TypeError as e:
            errors.append(
                _errors.ErrorFormatter.casting_error(attr, field.hint, str(e))
            )

    if errors:
        raise excs.CastingError(errors)


def cast_dict(value, hint):
    keys_type, val_type = t.get_args(hint)

    new_dict = {}
    for key, val in value.items():
        # Cast both keys and values
        new_key = cast_value(key, keys_type)
        new_val = cast_value(val, val_type)
        new_dict[new_key] = new_val

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
    if isinstance(hint, types.UnionType) or (origin is not None and origin is t.Union):
        union_args = t.get_args(hint)

        # Special handling for None values in Optional types
        if value is None and type(None) in union_args:
            return None

        # First check: Is value already one of the union member types?
        # If yes, return it unchanged (don't cast between union members)
        for sub_hint in union_args:
            if sub_hint is type(None):
                continue
            # For simple types, check isinstance
            if not t.get_origin(sub_hint) and isinstance(value, sub_hint):
                return value
            # For generic types (List[int], Dict[str, int], etc.), check origin
            sub_origin = t.get_origin(sub_hint)
            if sub_origin and isinstance(value, sub_origin):
                # Value matches container type, try to cast/validate inner elements
                with contextlib.suppress(TypeError):
                    return cast_value(value, sub_hint)
                # Cast/validation failed, but container matches, return as-is
                return value

        # Value is not a union member, try casting to each type in order
        for sub_hint in union_args:
            if sub_hint is type(None) and value is not None:
                continue

            # Try casting to this type
            with contextlib.suppress(TypeError):
                return cast_value(value, sub_hint)

        raise TypeError(
            _errors.ErrorFormatter.casting_error(
                value, hint, "Cannot cast to any type in Union"
            )
        )

    # Simple type: int, bool, str, CustomClass, etc.
    if not origin and not isinstance(value, hint):
        try:
            # Special handling for bool - only cast if value looks boolean
            if hint is bool and isinstance(value, str):
                lower_val = value.lower()
                if lower_val in ("true", "1", "yes"):
                    return True
                elif lower_val in ("false", "0", "no", ""):
                    return False
                else:
                    # Not a boolean-like string, raise error
                    raise TypeError(f"Cannot cast '{value}' to bool")
            return hint(value)
        except (ValueError, TypeError) as e:
            raise TypeError(
                _errors.ErrorFormatter.casting_error(value, hint, str(e))
            ) from e

    if origin:
        # For collections, check if value is already correct origin type
        if isinstance(value, origin):
            # Value is already correct type (e.g., list for List[int])
            handler = CASTING_ORIGIN_HANDLER.get(origin)
            if handler:
                # Cast elements to correct types
                return handler(value, hint)
            # No handler, return as-is
            return value

        # Value is not the correct origin type, try to cast
        handler = CASTING_ORIGIN_HANDLER.get(origin)
        if handler:
            return handler(value, hint)
        else:
            # Fallback for unknown collection types
            # If it's iterable but not str/bytes, try to cast as collection
            if hasattr(origin, "__iter__") and not issubclass(origin, (str, bytes)):
                return cast_collection(value, hint)
            else:
                raise TypeError(_errors.ErrorFormatter.casting_no_handler(origin))

    if isinstance(value, hint):
        return value

    # This should never be reached, but explicit is better than implicit
    raise TypeError(_errors.ErrorFormatter.casting_error(value, hint, "Unable to cast"))
