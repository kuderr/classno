import typing as t

from classno import _casting
from classno import _dunders
from classno import _fields
from classno import _getattrs
from classno import _setattrs
from classno import _validation
from classno import constants as c


def init_obj(self, *args, **kwargs):
    missing_fields = []

    for field in self.__fields__.values():
        if field.name in kwargs:
            object.__setattr__(self, field.name, kwargs[field.name])
        elif field.default is not c.MISSING:
            object.__setattr__(self, field.name, field.default)
        elif field.default_factory is not c.MISSING:
            object.__setattr__(self, field.name, field.default_factory())
        else:
            missing_fields.append(field.name)

    if missing_fields:
        raise TypeError(
            f"{self.__class__.__name__}.__init__() missing {len(missing_fields)} "
            f"required arguments: {', '.join(f'{arg}' for arg in missing_fields)}"
        )


def set_fields(cls: t.Type) -> None:
    hints = t.get_type_hints(cls)

    fields = {}
    for name, hint in hints.items():
        if name in c._CLASSNO_ATTRS:
            continue

        attr = getattr(cls, name, c.MISSING)
        f = attr if isinstance(attr, _fields.Field) else _fields.field(default=attr)

        f.name = name
        f.hint = hint

        fields[name] = f

    cls.__fields__ = fields


def set_keys(cls: t.Type, keys_attr: str) -> None:
    attr = getattr(cls, keys_attr)
    if not attr:
        attr = tuple(cls.__fields__)
        setattr(cls, keys_attr, attr)


def process_cls_features(cls: t.Type) -> None:
    fields = cls.__fields__
    features = cls.__features__

    # TODO: dont override
    if c.Features.REPR in features:
        cls.__repr__ = _dunders.__repr__
    # TODO: raise error if not set and keys set
    if c.Features.EQ in features:
        cls.__eq__ = _dunders.__eq__
        cls._eq_value = _dunders._eq_value
        set_keys(cls, c._CLASSNO_EQ_KEYS_ATTR)
    if c.Features.HASH in features:
        cls.__hash__ = _dunders.__hash__
        cls._hash_value = _dunders._hash_value
        set_keys(cls, c._CLASSNO_HASH_KEYS_ATTR)
    if c.Features.ORDER in features:
        cls._order_value = _dunders._order_value
        for method in _dunders._ORDER_DUNDERS:
            setattr(cls, method.__name__, method)
        set_keys(cls, c._CLASSNO_ORDER_KEYS_ATTR)

    # TODO: raise if set
    if c.Features.SLOTS in features:
        cls.__slots__ = tuple(f.name for f in fields.values())
    if c.Features.FROZEN in features:
        cls.__setattr__ = cls.__delattr__ = _setattrs.frozen_setattr
    if c.Features.PRIVATE in features:
        cls.__setattr__ = _setattrs.privates_setattr
        cls.__getattr__ = _getattrs.privates_getattr
    if c.Features.VALIDATION in features:
        cls.__setattr__ = _setattrs.validated_setattr
    if c.Features.LOSSY_AUTOCAST in features:
        cls.__setattr__ = _setattrs.lossy_autocast_setattr

    # TODO(kuderr): make it prettier
    if c.Features.VALIDATION | c.Features.PRIVATE in features:
        cls.__setattr__ = _setattrs.private_validated_setattr


def process_obj_features(obj: object) -> None:
    features = obj.__features__

    # TODO: should it work together? if yes – in what order?
    if c.Features.VALIDATION in features:
        _validation.validate_fields(obj)
    if c.Features.LOSSY_AUTOCAST in features:
        _casting.cast_fields(obj)
