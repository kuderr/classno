import typing as t

from classno import _casting
from classno import _dunders
from classno import _getattrs
from classno import _setattrs
from classno import _validation
from classno import constants as c


# TODO: move somewhere
def set_keys(cls: t.Type, keys_attr: str) -> None:
    attr = getattr(cls, keys_attr)
    if not attr:
        attr = tuple(cls.__fields__)
        setattr(cls, keys_attr, attr)


def repr_handler(cls: t.Type) -> None:
    cls.__repr__ = _dunders.__repr__


def eq_handler(cls: t.Type) -> None:
    cls.__eq__ = _dunders.__eq__
    cls._cmp_factory = _dunders._cmp_factory
    set_keys(cls, c._CLASSNO_EQ_KEYS_ATTR)


def hash_handler(cls: t.Type) -> None:
    cls.__hash__ = _dunders.__hash__
    set_keys(cls, c._CLASSNO_HASH_KEYS_ATTR)


def order_handler(cls: t.Type) -> None:
    cls.__lt__ = _dunders.__lt__
    cls.__le__ = _dunders.__le__
    cls.__gt__ = _dunders.__gt__
    cls.__ge__ = _dunders.__ge__
    cls._cmp_factory = _dunders._cmp_factory
    set_keys(cls, c._CLASSNO_ORDER_KEYS_ATTR)


def slots_handler(cls: t.Type) -> None:
    cls.__slots__ = tuple(f.name for f in cls.__fields__.values())


def frozen_handler(cls: t.Type) -> None:
    cls.__setattr__ = cls.__delattr__ = _setattrs.frozen_setattr


def private_handler(cls: t.Type) -> None:
    cls.__setattr__ = _setattrs.privates_setattr
    cls.__getattr__ = _getattrs.privates_getattr


def validation_handler(cls: t.Type) -> None:
    cls.__setattr__ = _setattrs.validated_setattr


def lossy_autocast_handler(cls: t.Type) -> None:
    cls.__setattr__ = _setattrs.lossy_autocast_setattr


def private_validation_handler(cls: t.Type) -> None:
    cls.__setattr__ = _setattrs.private_validated_setattr


_CLASS_HANDLERS_MAP: dict[c.Features, t.Callable[[t.Type], None]] = {
    # TODO: dont override
    c.Features.REPR: repr_handler,
    # TODO: raise error if not set and keys set
    c.Features.EQ: eq_handler,
    c.Features.HASH: hash_handler,
    c.Features.ORDER: order_handler,
    # TODO: raise if set
    c.Features.SLOTS: slots_handler,
    c.Features.FROZEN: frozen_handler,
    c.Features.PRIVATE: private_handler,
    c.Features.VALIDATION: validation_handler,
    c.Features.LOSSY_AUTOCAST: lossy_autocast_handler,
    # TODO: make set/getattrs builder?
    c.Features.PRIVATE | c.Features.VALIDATION: private_validation_handler,
}


def validation_obj_handler(obj: object) -> None:
    _validation.validate_fields(obj)


def lossy_autocast_obj_handler(obj: object) -> None:
    _casting.cast_fields(obj)


_OBJECT_HANDLERS_MAP: dict[c.Features, t.Callable[[object], None]] = {
    # TODO: should this two work together? if yes – in what order?
    c.Features.VALIDATION: validation_obj_handler,
    c.Features.LOSSY_AUTOCAST: lossy_autocast_obj_handler,
}
