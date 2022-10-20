import numpy
import png
import rawpy
from PIL import Image, ImageDraw

from cfa_supersampler.registrer import LinearRegistrer
from cfa_supersampler.stacker import Stacker


def print_attr(obj):
    print("#####")
    for i in dir(obj):
        print(i, type(obj.__getattribute__(i)))
    print("#####\n", flush=True)


def print_attr_v(obj):
    print("#####")
    for i in dir(obj):
        print(i, type(obj.__getattribute__(i)), obj.__getattribute__(i))
    print("#####\n", flush=True)


def draw_cross(im: Image, x: int, y: int, size=10):
    draw = ImageDraw.ImageDraw(im=im)
    draw.line(xy=[(x - size, y), (x + size, y)])
    draw.line(xy=[(x, y - size), (x, y + size)])


def main():
    start = 50
    end = 170
    stacker = Stacker(
        registrer=LinearRegistrer(
            x_offset=1557,
            y_offset=-57,
            count=end-start,
        ),
        sample_factor=4,
    )
    for i in range(start, end):
        stacker.add_image_path(f"/home/tcoquelin/Pictures/astro/lune/1/capt{i:04d}.arw")
    stacker.autocrop()
    print("Crop", stacker.input_crop)
    stacker.init_input_color_mask()
    stacker.stack_images()
    stacker.save_png(path="/home/tcoquelin/Pictures/astro/lune/out.png")


def main2():
    with rawpy.imread("/home/tcoquelin/Pictures/astro/lune/1/capt0000.arw") as raw:
        arw: numpy.ndarray = raw.raw_image
        img = Image.fromarray((arw - arw.min()) * 16)
    with rawpy.imread("/home/tcoquelin/Pictures/astro/lune/1/capt0199.arw") as raw:
        arw: numpy.ndarray = raw.raw_image
        img2 = Image.fromarray((arw - arw.min()) * 16)
    draw_cross(im=img, x=1225, y=1436)
    draw_cross(im=img2, x=2782, y=1379)
    img2.show()


def main3():
    pycharm_png = "/home/tcoquelin/Tools/pycharm-community-2022.2.2/bin/pycharm.png"
    r = png.Reader(pycharm_png)
    i = r.read()
    image_2d = numpy.vstack(map(numpy.uint16, i[2]))
    image = png.fromarray(image_2d,mode='RGBA')
    with open('swatch.png', 'wb') as f:
        w = png.Writer(i[1], i[0], greyscale=False, alpha=True, )
        w.write(f, image_2d)


if __name__ == "__main__":
    main()
