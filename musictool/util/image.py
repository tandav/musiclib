import random
import string

import cv2
import numpy as np

from musictool import config


def overlay_rect(
    im: np.ndarray,
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: tuple[int, int, int],
    alpha: float,
) -> np.ndarray:
    x1, y1 = pt1
    x2, y2 = pt2
    if y2 - y1 > 0 and x2 - x1 > 0:
        sub_im = im[y1:y2, x1:x2]
        rect = np.full_like(sub_im, fill_value=255)
        rect[:, :, 0] = color[0]
        rect[:, :, 1] = color[1]
        rect[:, :, 2] = color[2]
        # print('*********>', x1,x2,y1,y2,alpha, sub_im.shape, rect.shape)
        im[y1:y2, x1:x2] = cv2.addWeighted(rect, alpha, sub_im, 1 - alpha, gamma=0)
    return im


def overlay_image(im: np.ndarray, overlay: np.ndarray, alpha: float,) -> np.ndarray:
    return cv2.addWeighted(overlay, alpha, im, 1 - alpha, gamma=0)


def minmax_scaler(value, oldmin, oldmax, newmin=0.0, newmax=1.0):
    '''
    >>> minmax_scaler(50, 0, 100, 0.0, 1.0)
    0.5
    '''
    return (value - oldmin) * (newmax - newmin) / (oldmax - oldmin) + newmin


def rel_to_abs_w(value): return int(minmax_scaler(value, 0, 1, 0, config.frame_width))
def rel_to_abs_h(value): return int(minmax_scaler(value, 0, 1, 0, config.frame_height))


def rel_to_abs(x, y):
    """xy: coordinates in fractions of screen"""
    return rel_to_abs_w(x), rel_to_abs_h(y)


def random_xy():
    return random.randrange(config.frame_width), random.randrange(config.frame_height)


def random_text(words=tuple(''.join(random.choices(string.ascii_letters, k=random.randint(1, 15))) for _ in range(200))):
    return random.choice(words)
