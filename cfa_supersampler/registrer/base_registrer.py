from typing import Tuple


class BaseRegistrer:
    def get_offset(self, index: int) -> Tuple[float, float]:
        raise NotImplementedError

    def get_relative_offset(self, index: int, ref: int) -> Tuple[float, float]:
        raise NotImplementedError
