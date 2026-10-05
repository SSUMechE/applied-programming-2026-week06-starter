"""Provided two-obstacle route construction, full-segment checks and records.

The Week 5 model and its sampled evaluator remain unchanged in model.py.
These Week 6 objects reuse Configuration, Path and the evaluate(problem) call.
Students do not implement closest-point geometry or the checker.
"""
from dataclasses import dataclass, replace
import math
from .adapter import AdapterError
from .domain import Configuration, ConfigurationBounds, Obstacle, Path, PlanningModelError
from .model import EvaluationResult, ParametricPlanningProblem, PlanningSettings
from .results import EvaluationReport, ExecutionResult


def _number(value, name):
    if type(value) not in (int, float):
        raise PlanningModelError(f"{name} must be a finite real number")
    try:
        number = float(value)
    except (OverflowError, ValueError) as error:
        raise PlanningModelError(f"{name} must be finite") from error
    if not math.isfinite(number):
        raise PlanningModelError(f"{name} must be finite")
    return number


@dataclass(frozen=True)
class RouteSettings:
    """Constraints for continuous straight-segment evaluation, not sampling."""
    min_clearance_m: float = 0.25
    max_length_m: float = 6.8

    def __post_init__(self):
        minimum = _number(self.min_clearance_m, "min_clearance_m")
        maximum = _number(self.max_length_m, "max_length_m")
        if not 0 <= minimum <= 2 or not 0 < maximum <= 20:
            raise PlanningModelError("require clearance in [0,2] and length in (0,20]")
        object.__setattr__(self, "min_clearance_m", minimum)
        object.__setattr__(self, "max_length_m", maximum)


@dataclass(frozen=True)
class RouteProblem:
    """Owned path and immutable scene. A distinct Week 6 multi-obstacle model."""
    start: Configuration
    goal: Configuration
    bounds: ConfigurationBounds
    obstacles: tuple[Obstacle, ...]
    path: Path
    settings: RouteSettings
    a_m: float = 0.0
    b_m: float = 0.0

    def __post_init__(self):
        try:
            obstacles = tuple(self.obstacles)
        except TypeError as error:
            raise PlanningModelError("obstacles must be a nonempty sequence") from error
        if not obstacles or not all(isinstance(item, Obstacle) for item in obstacles):
            raise PlanningModelError("obstacles must contain Obstacle objects")
        if len({item.obstacle_id for item in obstacles}) != len(obstacles):
            raise PlanningModelError("obstacle IDs must be unique")
        if not isinstance(self.settings, RouteSettings):
            raise PlanningModelError("settings must be RouteSettings")
        # Reuse the taught domain invariants without changing the Week 5 class.
        ParametricPlanningProblem(self.start, self.goal, self.bounds, obstacles[0],
                                  self.path, PlanningSettings())
        a = _number(self.a_m, "a_m")
        b = _number(self.b_m, "b_m")
        if not -1.6 <= a <= 1.6 or not -1.6 <= b <= 1.6:
            raise PlanningModelError("a_m and b_m must lie in [-1.6,1.6]")
        owned_path = Path(Configuration(point.values) for point in self.path.waypoints)
        object.__setattr__(self, "obstacles", obstacles)
        object.__setattr__(self, "path", owned_path)
        object.__setattr__(self, "a_m", a)
        object.__setattr__(self, "b_m", b)


@dataclass(frozen=True)
class RouteMetrics(EvaluationResult):
    """sample_count=0 denotes no point sampling. segment_count counts whole edges."""
    segment_count: int
    closest_segment_index: int
    closest_obstacle_id: str
    closest_point_xy: tuple[float, float]


def validate_route_grid_parameters(height_min_m, height_max_m, count):
    low = _number(height_min_m, "height_min_m")
    high = _number(height_max_m, "height_max_m")
    if not -1.6 <= low < high <= 1.6:
        raise PlanningModelError("height bounds require -1.6 <= low < high <= 1.6")
    if type(count) is not int or not 2 <= count <= 25:
        raise PlanningModelError("count must be an integer from 2 to 25 per axis")
    return low, high, count


def problem_at_bends(a_m, b_m, settings=None):
    """Build the announced six-point route, dropping consecutive duplicates."""
    if settings is None:
        settings = RouteSettings()
    a = _number(a_m, "a_m")
    b = _number(b_m, "b_m")
    coordinates = [(0,0), (0,a), (2,a), (4,b), (6,b), (6,0)]
    distinct = []
    for xy in coordinates:
        if not distinct or xy != distinct[-1]:
            distinct.append(xy)
    return RouteProblem(
        Configuration((0,0)), Configuration((6,0)),
        ConfigurationBounds(Configuration((-0.5,-2)), Configuration((6.5,2))),
        (Obstacle("left", Configuration((2,0.4)), 0.6),
         Obstacle("right", Configuration((4,-0.4)), 0.6)),
        Path(Configuration(xy) for xy in distinct), settings, a, b)


def segment_clearance(start, goal, obstacle):
    """Return disk-boundary clearance and its nearest point on the WHOLE segment."""
    if not isinstance(start, Configuration) or not isinstance(goal, Configuration):
        raise PlanningModelError("segment endpoints must be Configuration objects")
    if start.dimension != 2 or goal.dimension != 2 or not isinstance(obstacle, Obstacle):
        raise PlanningModelError("segment check requires 2-D endpoints and an Obstacle")
    a, b = start.values, goal.values
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    if not math.isfinite(length):
        raise PlanningModelError("segment length is not representable")
    if length == 0:
        nearest = a
    else:
        ux, uy = dx/length, dy/length
        center = obstacle.center.values
        projection = (center[0]-a[0])*ux + (center[1]-a[1])*uy
        if not math.isfinite(projection):
            raise PlanningModelError("segment projection is not representable")
        distance = min(length, max(0.0, projection))
        nearest = (a[0]+distance*ux, a[1]+distance*uy)
    clearance = math.dist(nearest, obstacle.center.values)-obstacle.radius_m
    if not math.isfinite(clearance):
        raise PlanningModelError("segment clearance is not representable")
    return clearance, tuple(nearest)


def segment_length(left, right):
    """Provided finite Euclidean distance for two Configuration endpoints."""
    if not isinstance(left, Configuration) or not isinstance(right, Configuration):
        raise PlanningModelError("segment endpoints must be Configuration objects")
    if left.dimension != right.dimension:
        raise PlanningModelError("segment dimensions must match")
    length = math.dist(left.values, right.values)
    if not math.isfinite(length):
        raise PlanningModelError("segment length is not representable")
    return length


def validate_shortening_inputs(path, edge_checker):
    """Provided input check and new working list. Does not shorten anything."""
    if not isinstance(path, Path) or path.dimension != 2:
        raise PlanningModelError("path must be a two-dimensional Path")
    if not callable(edge_checker):
        raise PlanningModelError("edge_checker must be callable")
    return list(path.waypoints)


def checked_edge(edge_checker, left, right):
    """Provided bool-result check. Checker exceptions propagate unchanged."""
    answer = edge_checker(left, right)
    if type(answer) is not bool:
        raise PlanningModelError("edge_checker must return bool")
    return answer


def edge_checker_for(problem):
    """Return checker(left, right) using this scene and minimum clearance."""
    if not isinstance(problem, RouteProblem):
        raise PlanningModelError("expected RouteProblem")
    def check(left, right):
        if not problem.bounds.contains(left) or not problem.bounds.contains(right):
            return False
        for obstacle in problem.obstacles:
            clearance, _ = segment_clearance(left, right, obstacle)
            if clearance < problem.settings.min_clearance_m or clearance <= 0:
                return False
        return True
    return check


class RouteEvaluator:
    """Provided full-segment evaluator. No plotting, saving or path alteration."""
    measurement_method = "continuous_segments"

    def evaluate(self, problem):
        if not isinstance(problem, RouteProblem):
            raise PlanningModelError("RouteEvaluator requires RouteProblem")
        best = None
        points = problem.path.waypoints
        directions = []
        for index, (left, right) in enumerate(zip(points[:-1], points[1:])):
            for obstacle in problem.obstacles:
                clearance, nearest = segment_clearance(left, right, obstacle)
                if best is None or clearance < best[0]:
                    best = (clearance, index, obstacle.obstacle_id, nearest)
            dx = right.values[0]-left.values[0]
            dy = right.values[1]-left.values[1]
            directions.append((dx,dy))
        turns = [abs(math.atan2(a[0]*b[1]-a[1]*b[0], a[0]*b[0]+a[1]*b[1]))
                 for a,b in zip(directions[:-1], directions[1:])]
        length = problem.path.length()
        clearance = best[0]
        clearance_margin = clearance-problem.settings.min_clearance_m
        length_margin = problem.settings.max_length_m-length
        feasible = clearance_margin >= 0 and length_margin >= 0
        metrics = RouteMetrics(length, clearance, math.fsum(turns), clearance_margin,
            length_margin, feasible, self.measurement_method, 0,
            len(points)-1, best[1], best[2], best[3])
        check = edge_checker_for(problem)
        valid = feasible and all(check(a,b) for a,b in zip(points[:-1],points[1:]))
        return EvaluationReport(metrics, bool(valid))


def replay_route(problem):
    """Geometric replay of the actual final path. This is not physics simulation."""
    check = edge_checker_for(problem)
    final = problem.start
    for destination in problem.path.waypoints[1:]:
        if not check(final, destination):
            return ExecutionResult(False, final)
        final = destination
    return ExecutionResult(True, final)


def prepare_routes(candidates):
    """Call the student shortener, return NEW problems and factual before/after records.

    Records list checked proposals and removed original indices. They do not
    invent a chronological deletion history from the final Path return value.
    """
    from .selection import shorten_route
    prepared, records = {}, {}
    for candidate_id, problem in candidates.items():
        proposals = []
        check = edge_checker_for(problem)
        def recording_check(left, right):
            accepted = check(left, right)
            proposals.append({"from_xy": list(left.values), "to_xy": list(right.values),
                              "clearance_allowed": accepted})
            return accepted
        final_path = shorten_route(problem.path, recording_check)
        if not isinstance(final_path, Path):
            raise PlanningModelError("shorten_route must return Path")
        final_points = [p.values for p in final_path.waypoints]
        original_points = [p.values for p in problem.path.waypoints]
        cursor = 0
        kept = []
        for point in final_points:
            while cursor < len(original_points) and original_points[cursor] != point:
                cursor += 1
            if cursor == len(original_points):
                raise PlanningModelError("shorten_route must keep an ordered original subsequence")
            kept.append(cursor)
            cursor += 1
        if kept[0] != 0 or kept[-1] != len(original_points)-1:
            raise PlanningModelError("shorten_route must preserve endpoints")
        prepared[candidate_id] = replace(problem, path=final_path)
        records[candidate_id] = {
            "raw_path_xy": problem.path.as_array().tolist(),
            "path_xy": final_path.as_array().tolist(),
            "raw_length_m": problem.path.length(), "final_length_m": final_path.length(),
            "length_saved_m": problem.path.length()-final_path.length(),
            "removed_original_indices": [i for i in range(len(original_points)) if i not in kept],
            "edge_checks": proposals}
    return prepared, records
