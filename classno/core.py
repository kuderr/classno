import typing as t

from classno import _fields
from classno import _hooks
from classno import constants as c


class MetaClassno(type):
    def __new__(cls, name, bases, attrs):
        klass = super().__new__(cls, name, bases, attrs)
        klass.__set_fields_hook__(klass)
        klass.__process_cls_features_hook__(klass)
        return klass

    # Called on SubClassno(...)
    def __call__(cls, *args, **kwargs):
        # def __init__ is called here
        obj = type.__call__(cls, *args, **kwargs)
        # Process object fields data and __init__ input
        cls.__init_hook__(obj, *args, **kwargs)

        cls.__process_obj_features_hook__(obj)
        obj.__post__init__(*args, **kwargs)
        return obj


class Classno(metaclass=MetaClassno):
    __fields__: t.ClassVar[dict[str, _fields.Field]] = {}
    __features__: t.ClassVar[c.Features] = c.Features.DEFAULT

    __eq_keys__: t.ClassVar[set[str]] = set()
    __hash_keys__: t.ClassVar[set[str]] = set()
    __order_keys__: t.ClassVar[set[str]] = set()

    __init_hook__ = _hooks.init_obj
    __set_fields_hook__ = _hooks.set_fields
    __process_cls_features_hook__ = _hooks.process_cls_features
    __process_obj_features_hook__ = _hooks.process_obj_features

    def __init__(self, *args, **kwargs) -> None: ...
    def __post__init__(self, *args, **kwargs) -> None: ...

    def as_dict(self):
        return {f.name: getattr(self, f.name) for f in self.__fields__.values()}

    def as_kwargs(self):
        return ", ".join(f"{k!s}={v!r}" for k, v in self.as_dict().items())
