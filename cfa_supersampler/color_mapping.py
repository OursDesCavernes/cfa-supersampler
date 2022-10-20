from typing import Tuple

from rawpy._rawpy import RawPy


def get_color_mapping(raw: RawPy) -> Tuple[int, ...]:
    color_map = {
        "R": 0,
        "G": 1,
        "B": 2,
    }
    return tuple(color_map[c] for c in raw.color_desc.decode("ascii"))
