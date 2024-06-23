import typing as t

from classno import _fields
from classno import constants as c


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


def preprocess_features(cls: t.Type) -> None:
    fields = cls.__fields__
    features = cls.__features__

    # process if all these methods already set in cls
    if c.Features.EQ not in features:
        cls.__eq__ = None
    if c.Features.ORDER not in features:
        cls.__lt__ = cls.__le__ = cls.__gt__ = cls.__ge__ = None
    if c.Features.HASH not in features:
        cls.__hash__ = None
    if c.Features.SLOTS in features:
        cls.__slots__ = tuple(f.name for f in fields.values())


def raise_frozen_attr_exc(self, *args, **kwargs):
    raise Exception(f"Cannot modify attrs of class {self.__class__.__name__}")


def postprocess_features(cls: t.Type) -> None:
    features = cls.__features__

    if c.Features.FROZEN in features:
        cls.__setattr__ = cls.__delattr__ = raise_frozen_attr_exc
    if c.Features.PRIVATE in features:
        cls.__setattr__ = privates_setattr


def privates_setattr(self, name: str, value: t.Any) -> None:
    if name in self.__fields__:
        raise Exception("privates only")

    if name.startswith("_") and name[1:] in self.__fields__:
        return super(self.__class__, self).__setattr__(name[1:], value)

    return super(self.__class__, self).__setattr__(name, value)
