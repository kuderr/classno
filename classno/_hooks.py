import typing as t

from classno import _casting
from classno import _fields
from classno import _setattrs
from classno import _validation
from classno import constants as c


def init_obj(self, *args, **kwargs):
    missing_fields = []

    _setattr = super(self.__class__, self).__setattr__

    for field in self.__fields__.values():
        if field.name in kwargs:
            _setattr(field.name, kwargs[field.name])
        elif field.default is not c.MISSING:
            _setattr(field.name, field.default)
        elif field.default_factory is not c.MISSING:
            _setattr(field.name, field.default_factory())
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


def set_keys(cls: t.Type) -> None:
    for cls_keys_attr in tuple(c._CLASSNO_KEYS_ATTRS):
        attr = getattr(cls, cls_keys_attr)
        if not attr:
            attr = tuple(cls.__fields__)
        setattr(cls, cls_keys_attr, attr)


def process_cls_features(cls: t.Type) -> None:
    fields = cls.__fields__
    features = cls.__features__

    # TODO: process if all these methods already set in cls
    if c.Features.EQ not in features:
        cls.__eq__ = cls._eq_value = None
    if c.Features.ORDER not in features:
        cls.__lt__ = cls.__le__ = cls.__gt__ = cls.__ge__ = cls._order_value = None
    if c.Features.HASH not in features:
        cls.__hash__ = cls._hash_value = None
    if c.Features.SLOTS in features:
        cls.__slots__ = tuple(f.name for f in fields.values())
    if c.Features.FROZEN in features:
        cls.__setattr__ = cls.__delattr__ = _setattrs.raise_frozen_attr_exc
    if c.Features.PRIVATE in features:
        cls.__setattr__ = _setattrs.privates_setattr
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
