import typing as t


def frozen_delattr(self, name: str) -> t.Never:
    raise Exception(f"Cannot delete attrs of frozen class {self.__class__.__name__}")
