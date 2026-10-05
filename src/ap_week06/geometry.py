"""Provided finite path-length calculation. Students do not edit this module."""
import math
import numpy as np


def polyline_length(points):
    """Return consecutive Euclidean distances summed in metres."""
    array = np.asarray(points, dtype=np.float64)
    if array.ndim != 2 or len(array) < 2 or not np.isfinite(array).all():
        raise ValueError("points must be a finite array of shape (N, D), N >= 2")
    try:
        lengths = [math.dist(a, b) for a, b in zip(array[:-1], array[1:])]
        total = math.fsum(lengths)
    except (ValueError, OverflowError) as error:
        raise ValueError("path length is not representable") from error
    if not math.isfinite(total):
        raise ValueError("path length is not representable")
    return float(total)
