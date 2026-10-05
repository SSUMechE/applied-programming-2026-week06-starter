"""Completed protected wrapper. No student implementation is required."""
from .backend import BackendFailure
from .domain import Configuration, Path, PlanningModelError
from .results import ExecutionResult


class AdapterError(RuntimeError):
    """A requested external operation failed or returned an unusable result."""


def _xy(configuration):
    if not isinstance(configuration, Configuration) or configuration.dimension != 2:
        raise PlanningModelError("expected a two-dimensional Configuration")
    return tuple(configuration.values)


def _path_xy(path):
    if not isinstance(path, Path) or path.dimension != 2:
        raise PlanningModelError("expected a two-dimensional Path")
    if not 2 <= len(path.waypoints) <= 32:
        raise PlanningModelError("expected 2 to 32 waypoints")
    return [_xy(point) for point in path.waypoints]


def _boolean(raw, operation):
    if type(raw) is not bool:
        raise AdapterError(f"{operation} returned a non-Boolean result")
    return raw


def _execution(raw):
    if not isinstance(raw, dict) or set(raw) != {"completed", "final_xy"}:
        raise AdapterError("execute returned an invalid result dictionary")
    completed = _boolean(raw["completed"], "execute")
    xy = raw["final_xy"]
    if not isinstance(xy, (tuple, list)) or len(xy) != 2:
        raise AdapterError("execute returned an invalid final_xy")
    try:
        final = Configuration(xy)
    except PlanningModelError as error:
        raise AdapterError("execute returned invalid final coordinates") from error
    return ExecutionResult(completed=completed, final=final)


class CourseAdapter:
    """Convert course objects to raw function inputs and raw outputs back again."""

    def __init__(self, state_fn, edge_fn, execute_fn):
        if not all(callable(fn) for fn in (state_fn, edge_fn, execute_fn)):
            raise PlanningModelError("all three backend operations must be callable")
        self.state_fn = state_fn
        self.edge_fn = edge_fn
        self.execute_fn = execute_fn

    def is_state_valid(self, configuration):
        # Provided: convert input, call state_fn once, convert only BackendFailure,
        # and validate the returned Boolean. False is a normal check result.
        xy = _xy(configuration)
        try:
            raw = self.state_fn(xy)
        except BackendFailure as error:
            raise AdapterError("state check could not complete") from error
        return _boolean(raw, "state")

    def is_edge_valid(self, start, goal):
        # Provided: convert both inputs, call edge_fn once in the same order,
        # convert only BackendFailure, and validate the returned Boolean.
        a_xy, b_xy = _xy(start), _xy(goal)
        try:
            raw = self.edge_fn(a_xy, b_xy)
        except BackendFailure as error:
            raise AdapterError("edge check could not complete") from error
        return _boolean(raw, "edge")

    def execute(self, path):
        # Provided: convert input, call execute_fn once, convert only BackendFailure,
        # and return the supplied _execution conversion without inventing success.
        path_xy = _path_xy(path)
        try:
            raw = self.execute_fn(path_xy)
        except BackendFailure as error:
            raise AdapterError("execution could not complete") from error
        return _execution(raw)
