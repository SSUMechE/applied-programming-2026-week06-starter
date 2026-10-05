"""Supplied deterministic disk checks and geometric replay, not physics.

The evaluator does not import this module. The program that assembles components
chooses a backend for the same problem and passes its functions to CourseAdapter.
Touching the closed disk is rejected. Rectangle boundary positions are accepted.
"""
import math
from .domain import ConfigurationBounds, Obstacle
from .model import ParametricPlanningProblem


class BackendFailure(RuntimeError):
    """The supplied operation could not perform its requested check or replay."""


def _point(xy):
    if not isinstance(xy, (tuple, list)) or len(xy) != 2:
        raise BackendFailure("expected an (x, y) pair")
    if any(type(value) not in (int, float) for value in xy):
        raise BackendFailure("coordinates must be real numbers")
    try:
        point = tuple(float(value) for value in xy)
    except (OverflowError, ValueError) as error:
        raise BackendFailure("coordinates must be finite") from error
    if not all(math.isfinite(value) for value in point):
        raise BackendFailure("coordinates must be finite")
    return point


class CourseBackend:
    """Fixed 2-D scene and three raw operations provided to students."""

    def __init__(self, bounds, obstacle):
        if not isinstance(bounds, ConfigurationBounds) or bounds.dimension != 2:
            raise BackendFailure("backend bounds must be two-dimensional")
        if not isinstance(obstacle, Obstacle):
            raise BackendFailure("backend requires an Obstacle")
        self.bounds = bounds
        self.obstacle = obstacle

    def state_valid(self, xy):
        x, y = _point(xy)
        low, high = self.bounds.lower.values, self.bounds.upper.values
        inside = low[0] <= x <= high[0] and low[1] <= y <= high[1]
        return bool(inside and math.dist((x, y), self.obstacle.center.values)
                    > self.obstacle.radius_m)

    def edge_valid(self, a_xy, b_xy):
        a, b = _point(a_xy), _point(b_xy)
        if not self.state_valid(a) or not self.state_valid(b):
            return False
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if not math.isfinite(length):
            raise BackendFailure("segment length is not representable")
        if length == 0.0:
            return self.state_valid(a)
        direction = (dx / length, dy / length)
        center = self.obstacle.center.values
        projection = ((center[0] - a[0]) * direction[0]
                      + (center[1] - a[1]) * direction[1])
        if not math.isfinite(projection):
            raise BackendFailure("segment projection is not representable")
        distance = min(length, max(0.0, projection))
        closest = (a[0] + distance * direction[0], a[1] + distance * direction[1])
        return bool(math.dist(closest, center) > self.obstacle.radius_m)

    def replay(self, path_xy):
        if not isinstance(path_xy, list) or not 2 <= len(path_xy) <= 32:
            raise BackendFailure("replay requires a list of 2 to 32 points")
        points = [_point(point) for point in path_xy]
        final = points[0]
        if not self.state_valid(final):
            return {"completed": False, "final_xy": final}
        for destination in points[1:]:
            if not self.edge_valid(final, destination):
                return {"completed": False, "final_xy": final}
            final = destination
        return {"completed": True, "final_xy": final}


def backend_for(problem):
    """Bind the supplied checks to this problem's actual bounds and disk."""
    if not isinstance(problem, ParametricPlanningProblem):
        raise BackendFailure("expected a ParametricPlanningProblem")
    return CourseBackend(problem.bounds, problem.obstacle)
