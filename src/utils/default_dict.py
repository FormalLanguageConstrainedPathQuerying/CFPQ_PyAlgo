from typing import TypeVar, Dict, Generic, Callable

_KT = TypeVar("_KT")
_VT = TypeVar("_VT")


class DefaultKeyDependentDict(Dict[_KT, _VT], Generic[_KT, _VT]):
    def __init__(self, value_factory: Callable[[_KT], _VT]):
        self.value_factory = value_factory
        super().__init__()

    def __getitem__(self, key: _KT) -> _VT:
        if key not in self:
            self[key] = self.value_factory(key)
        return super().__getitem__(key)

    def __sizeof__(self) -> int:
        return sum(v.__sizeof__() for v in self.values())
