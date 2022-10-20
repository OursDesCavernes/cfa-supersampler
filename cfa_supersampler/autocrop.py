from numpy import ndarray


def autocrop(arw=ndarray, margin: int = 100, threshold=90):
    x_first = 0
    x_last = 0
    y_first = 0
    y_last = 0
    xc = 0
    yc = 0
    im_min = arw.min()
    for line in arw:
        yc = yc + 1
        line_max = line.max()
        if line_max > im_min + threshold and y_first == 0:
            y_first = yc
        if line_max < im_min + threshold and y_first > 0:
            y_last = yc
            break
    y_med = int((y_first + y_last) / 2)
    line_min = arw[y_med].min()
    for x in arw[y_med]:
        xc = xc + 1
        if x > line_min + threshold and x_first == 0:
            x_first = xc
        if x < line_min + threshold and x_first > 0:
            x_last = xc
            break
    return x_first - margin, x_last + margin, y_first - margin, y_last + margin
