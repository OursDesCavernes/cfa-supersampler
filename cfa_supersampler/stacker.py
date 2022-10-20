from typing import Tuple

import png
import rawpy
from PIL import Image
from numpy import ndarray, zeros, uint16, repeat, array, tile, uint32, uint8
from rawpy._rawpy import RawPy

from cfa_supersampler.autocrop import autocrop
from cfa_supersampler.registrer import BaseRegistrer


class Stacker:
    input_crop: Tuple[int, int, int, int]
    output: ndarray
    alpha: ndarray
    wb: ndarray
    input_scaled_color_mask: ndarray
    _reference_frame: int = 0

    def __init__(self, registrer: BaseRegistrer, sample_factor: int = 1):
        self.sample_factor = sample_factor
        self.registrer = registrer
        self.image_path_list: list[str] = []

    def add_image_path(self, path: str):
        print("Adding", path)
        self.image_path_list.append(path)

    @property
    def reference_frame(self) -> int:
        if self.image_path_list and self._reference_frame is None:
            return int(len(self.image_path_list) / 2)
        return self._reference_frame

    @reference_frame.setter
    def reference_frame(self, index: int):
        assert isinstance(index, int)
        assert 0 <= index < len(self.image_path_list)
        self._reference_frame = index

    def autocrop(self):
        with rawpy.imread(self.image_path_list[self.reference_frame]) as raw:
            arw: ndarray = raw.raw_image
            self.input_crop = autocrop(arw)

    def init_output(self):
        x_first, x_last, y_first, y_last = self.input_crop
        width = (x_last - x_first) * self.sample_factor * 3
        hight = (y_last - y_first) * self.sample_factor
        self.output = zeros(shape=(hight, width), dtype=uint32)
        self.alpha = zeros(shape=(hight, width), dtype=uint8)

    def init_input_color_mask(self):
        with rawpy.imread(self.image_path_list[self.reference_frame]) as raw:
            rgb_pattern = {
                "R": [1, 0, 0],
                "G": [0, 1, 0],
                "B": [0, 0, 1],
            }
            color_map = [rgb_pattern[c] for c in raw.color_desc.decode("ascii")]
            scaled_pattern = repeat(
                repeat(
                    raw.raw_pattern,
                    self.sample_factor,
                    axis=1,
                ),
                self.sample_factor,
                axis=0,
            )
            input_color_pattern = array(
                [
                    sum([color_map[x] for x in line], [])
                    for line in scaled_pattern
                ]
            )
            self.input_scaled_color_mask = tile(
                input_color_pattern, tuple(int(d / 2) for d in raw.raw_image.shape)
            ).astype(dtype=uint16)
            print(
                "init_input_color_mask()",
                raw.raw_image.shape,
                self.input_scaled_color_mask.shape,
            )

    def stack_images(self):
        self.init_output()
        for index, path in enumerate(self.image_path_list):
            print("Stacking", path, flush=True)
            with rawpy.imread(path) as raw:
                x_offset, y_offset = self.registrer.get_relative_offset(
                    index, self.reference_frame
                )
                self.stack_image(
                    raw=raw,
                    x_offset=x_offset,
                    y_offset=y_offset,
                )

    def scale_input(self, arr: ndarray) -> ndarray:
        return repeat(
            repeat(
                arr,
                3 * self.sample_factor,
                axis=1,
            ),
            self.sample_factor,
            axis=0,
        )

    def stack_image(
        self,
        raw: RawPy,
        x_offset: float,
        y_offset: float,
    ):
        x_first, x_last, y_first, y_last = self.input_crop

        def scale(x: float) -> int:
            return int(x * self.sample_factor)

        def crop(arr: ndarray) -> ndarray:
            return arr[
                scale(y_first + y_offset) : scale(y_last + y_offset),
                scale(x_first + x_offset) * 3 : scale(x_last + x_offset) * 3,
            ]

        input_image_scaled: ndarray = self.scale_input(raw.raw_image)
        input_image_scaled_crop = crop(input_image_scaled)
        input_scaled_color_mask_crop = crop(self.input_scaled_color_mask)
        self.output += input_image_scaled_crop * input_scaled_color_mask_crop
        self.alpha += input_scaled_color_mask_crop
        print(raw.raw_image.shape, self.output.shape, x_offset, y_offset)

    def show_pillow(self):
        assert isinstance(self.output, ndarray)
        image = Image.fromarray(self.output, mode="RGB")
        image.show()

    def save_tif(self, path: str):
        normalized_stack = self.normalize_output()
        image = Image.fromarray(normalized_stack.astype(uint16), mode="RGB")
        image.save(fp=path)

    def save_png(self, path: str):
        normalized_stack = self.normalize_output()
        image = png.fromarray(
            normalized_stack.astype(uint16),
            mode="RGB",
        )
        image.save(file=path)

    def normalize_output(self, output_max=40000) -> ndarray:
        assert isinstance(self.output, ndarray)
        normalized_stack = self.output / self.alpha
        normalized_stack *= output_max / normalized_stack.max()
        return normalized_stack
