import cv2
import numpy as np


def overlay_rect(
    im: np.ndarray,
    pt1: tuple[int, int],
    pt2: tuple[int, int],
    color: tuple[int, int, int],
    alpha: float,
) -> np.ndarray:
    print('------->', pt1, pt2, color, alpha)
    x1, y1 = pt1
    x2, y2 = pt2
    sub_im = im[y1:y2, x1:x2]
    rect = np.empty_like(sub_im)
    rect[:, :, 0] = color[0]
    rect[:, :, 1] = color[1]
    rect[:, :, 2] = color[2]
    im[y1:y2, x1:x2] = cv2.addWeighted(rect, alpha, sub_im, 1 - alpha, gamma=0)
    return im


def overlay_image(im0: np.ndarray, overlay: np.ndarray, alpha: float,) -> np.ndarray:
    return cv2.addWeighted(overlay, alpha, im0, 1 - alpha, gamma=0)
