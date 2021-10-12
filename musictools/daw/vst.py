import numpy as np


def sine(t, f, a=1., p=0.):
    return a * np.sin(2 * np.pi * f * t + p)
