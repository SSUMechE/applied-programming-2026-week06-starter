"""Provided path construction and validation in the unchanged Week 5 scene."""
import math
from .cases import supplied_case
from .domain import Configuration, Path, PlanningModelError
from .model import ParametricPlanningProblem, PlanningSettings


def validate_grid_parameters(height_min_m, height_max_m, count):
    """Provided input check. Return normalized endpoints and the integer count."""
    values = (height_min_m, height_max_m)
    if any(type(value) not in (int, float) for value in values):
        raise PlanningModelError("height bounds must be finite real numbers")
    try:
        low, high = map(float, values)
    except (OverflowError, ValueError) as error:
        raise PlanningModelError("height bounds must be finite") from error
    if not all(math.isfinite(value) for value in (low, high)):
        raise PlanningModelError("height bounds must be finite")
    if not 0.0 <= low < high <= 3.0:
        raise PlanningModelError("height bounds require 0 <= low < high <= 3")
    if type(count) is not int or not 2 <= count <= 41:
        raise PlanningModelError("count must be an integer from 2 to 41")
    return low, high, count


def problem_at_height(height_m, settings=None):
    """Build one announced path. H=0 has two points, without duplicate points."""
    if settings is None:
        settings = PlanningSettings()
    if type(height_m) not in (int, float):
        raise PlanningModelError("height_m must be a finite real number")
    try:
        height = float(height_m)
    except (OverflowError, ValueError) as error:
        raise PlanningModelError("height_m must be finite") from error
    if not math.isfinite(height) or not 0.0 <= height <= 3.0:
        raise PlanningModelError("height_m must lie in [0, 3]")
    case = supplied_case()
    coordinates = [(0, 0), (4, 0)] if height == 0 else [
        (0, 0), (0, height), (4, height), (4, 0)]
    case["path"] = Path([Configuration(xy) for xy in coordinates])
    return ParametricPlanningProblem(**case, settings=settings)


def supplied_candidates(settings=None):
    """Return six fresh paths of different shapes in the announced order."""
    if settings is None:
        settings = PlanningSettings()
    coordinates = {
        "detour_2": [(0, 0), (0, 2), (4, 2), (4, 0)],
        "direct": [(0, 0), (4, 0)],
        "triangle": [(0, 0), (2, 1.5), (4, 0)],
        "low_detour": [(0, 0), (0, 0.5), (4, 0.5), (4, 0)],
        "corner_cut": [(0, 0), (1, 1), (3, 1), (4, 0)],
        "long_zigzag": [(0, 0), (0, 2), (1, 2), (1, 1),
                        (3, 1), (3, 2), (4, 2), (4, 0)],
    }
    candidates = {}
    for candidate_id, path_xy in coordinates.items():
        case = supplied_case()
        case["path"] = Path([Configuration(xy) for xy in path_xy])
        candidates[candidate_id] = ParametricPlanningProblem(**case, settings=settings)
    return candidates
