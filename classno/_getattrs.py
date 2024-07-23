import typing as t


def privates_getattr(self, name: str) -> t.Any:
    if name.startswith("_") and name[1:] in self.__fields__:
        name = name[1:]

    return super(self.__class__, self).__getattribute__(name)
