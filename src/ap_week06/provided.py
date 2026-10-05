"""Supplied sampling, metric and margin functions. No TODOs or rendering imports."""
from __future__ import annotations
import math
import numpy as np
from .domain import Path, Obstacle, PlanningModelError

MAX_SAMPLES = 10_000


def _finite_number(value, name):
    if type(value) not in (int, float):
        raise PlanningModelError(f"{name} must be a finite real number")
    try:
        result = float(value)
    except (ValueError, OverflowError) as error:
        raise PlanningModelError(f"{name} must be a finite real number") from error
    if not math.isfinite(result):
        raise PlanningModelError(f"{name} must be a finite real number")
    return result


def sample_path(path: Path, resolution_m: float, method: str) -> np.ndarray:
    """Sample a 2-D polyline without changing it, at most MAX_SAMPLES points.

    Interpolated mode splits each segment into ceil(length / resolution) equal
    intervals and emits shared endpoints once. Waypoints mode copies saved points.
    Both modes validate the same resolution contract. The capacity guard runs
    before any sample array is allocated.
    """
    if not isinstance(path, Path) or path.dimension != 2:
        raise PlanningModelError("path must be a two-dimensional Path")
    if not 2 <= len(path.waypoints) <= 32:
        raise PlanningModelError("path must have between 2 and 32 waypoints")
    resolution = _finite_number(resolution_m, "resolution_m")
    if not 0.05 <= resolution <= 1.0:
        raise PlanningModelError("resolution_m must lie in [0.05, 1.0]")
    if not isinstance(method, str) or method not in ("waypoints", "interpolated"):
        raise PlanningModelError("method must be 'waypoints' or 'interpolated'")
    points = path.as_array()
    lengths = [math.dist(a, b) for a, b in zip(points[:-1], points[1:])]
    if any(not math.isfinite(length) or length <= 0 for length in lengths):
        raise PlanningModelError("segments must have positive finite length")
    if method == "waypoints":
        return points.copy()
    intervals = []
    sample_count = 1
    for length in lengths:
        ratio = length / resolution
        if not math.isfinite(ratio) or ratio > MAX_SAMPLES - 1:
            raise PlanningModelError("interpolation exceeds the 10000-sample limit")
        count = max(1, math.ceil(ratio))
        sample_count += count
        if sample_count > MAX_SAMPLES:
            raise PlanningModelError("interpolation exceeds the 10000-sample limit")
        intervals.append(count)
    sampled = [points[0].copy()]
    for left, right, count, length in zip(points[:-1], points[1:], intervals, lengths):
        # Permit tiny rounding only, never a tolerance scaled to absolute coordinates.
        spacing_limit = resolution + max(1e-12, 8.0 * math.ulp(length))
        for step in range(1, count + 1):
            fraction = step / count
            point = (1.0 - fraction) * left + fraction * right
            spacing = math.dist(sampled[-1], point)
            if not math.isfinite(spacing) or spacing <= 0.0 or spacing > spacing_limit:
                raise PlanningModelError("requested sample spacing is not representable")
            sampled.append(point)
    array = np.array(sampled, dtype=np.float64)
    if not np.isfinite(array).all():
        raise PlanningModelError("sample coordinates are not representable")
    return array


def path_metrics(path: Path, samples: np.ndarray, obstacle: Obstacle) -> dict[str, float]:
    """Return original-path length/turning and sampled point clearance.

    Clearance is signed distance to the disk boundary. Turning is the sum of
    absolute changes of direction in radians, not a time-dependent motion metric.
    """
    if not isinstance(path, Path) or path.dimension != 2:
        raise PlanningModelError("path must be a two-dimensional Path")
    if not isinstance(obstacle, Obstacle):
        raise PlanningModelError("obstacle must be an Obstacle")
    try:
        raw_samples = np.asarray(samples)
        if np.iscomplexobj(raw_samples):
            raise ValueError("samples must contain real coordinates")
        sampled = np.asarray(raw_samples, dtype=np.float64)
    except (TypeError, ValueError, OverflowError, FloatingPointError) as error:
        raise PlanningModelError("samples must be a representable real array") from error
    if sampled.ndim != 2 or sampled.shape[1] != 2 or len(sampled) == 0:
        raise PlanningModelError("samples must have shape (N, 2), N >= 1")
    if not np.isfinite(sampled).all():
        raise PlanningModelError("samples must be finite")
    try:
        length = path.length()
        distances = [math.dist(point, obstacle.center.values) for point in sampled]
        clearance = min(distances) - obstacle.radius_m
        points = path.as_array()
        directions = []
        for left, right in zip(points[:-1], points[1:]):
            dx, dy = float(right[0]) - float(left[0]), float(right[1]) - float(left[1])
            norm = math.hypot(dx, dy)
            if not math.isfinite(norm) or norm <= 0:
                raise ValueError("segments must have positive finite length")
            directions.append((dx / norm, dy / norm))
        turns = [abs(math.atan2(a[0] * b[1] - a[1] * b[0],
                               a[0] * b[0] + a[1] * b[1]))
                 for a, b in zip(directions[:-1], directions[1:])]
        turning = math.fsum(turns)
    except (ValueError, OverflowError, FloatingPointError) as error:
        raise PlanningModelError("path metrics are not representable") from error
    result = {"length_m": float(length), "clearance_m": float(clearance),
              "total_turn_rad": float(turning)}
    if not all(math.isfinite(value) for value in distances + list(result.values())):
        raise PlanningModelError("path metrics are not representable")
    return result


def constraint_margins(length_m, clearance_m, min_clearance_m, max_length_m):
    """Positive is permitted and zero is accepted. Never round for the decision."""
    length = _finite_number(length_m, "length_m")
    clearance = _finite_number(clearance_m, "clearance_m")
    minimum = _finite_number(min_clearance_m, "min_clearance_m")
    maximum = _finite_number(max_length_m, "max_length_m")
    result = {"clearance_margin_m": clearance - minimum,
              "length_margin_m": maximum - length}
    if not all(math.isfinite(value) for value in result.values()):
        raise PlanningModelError("constraint margins are not representable")
    return result
