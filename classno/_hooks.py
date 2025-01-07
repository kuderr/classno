import typing as t

from classno import _feature_handlers
from classno import _fields
from classno import _setattrs
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


def process_cls_features(cls: t.Type) -> None:
    for feature in _feature_handlers._CLASS_HANDLERS_MAP:
        if feature in cls.__features__:
            _feature_handlers._CLASS_HANDLERS_MAP[feature](cls)

    cls.__setattr__ = _setattrs.setattr_processor


# NOTE(kuderr): it could be set just into __setattr__ logic?
def process_obj_features(obj: object) -> None:
    for feature in _feature_handlers._OBJECT_HANDLERS_MAP:
        if feature in obj.__features__:
            _feature_handlers._OBJECT_HANDLERS_MAP[feature](obj)
