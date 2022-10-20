from typing import Tuple

from .base_registrer import BaseRegistrer


class LinearRegistrer(BaseRegistrer):
    def __init__(self, x_offset: float, y_offset: float, count: int):
        assert count > 1
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._count = count

    def get_offset(self, index: int) -> Tuple[float, float]:
        return self._x_offset * index / (self._count - 1), self._y_offset * index / (
            self._count - 1
        )

    def get_relative_offset(self, index: int, ref: int):
        x_offset = self._x_offset * (index - ref) / (self._count - 1)
        y_offset = self._y_offset * (index - ref) / (self._count - 1)
        return x_offset, y_offset
