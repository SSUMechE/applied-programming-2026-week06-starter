"""Optional completed state and edge helpers retained with the supplied support.

These helpers are not student implementation targets in the height-grid task.
"""
from .adapter import AdapterError
from .backend import BackendFailure


def check_start(problem, state_check):
    """Request one supplied operation. The caller chooses which function to pass."""
    return state_check(problem.start)


def check_edges(path, adapter):
    """Small illustration only: check adjacent saved pairs, stopping on False."""
    for start, goal in zip(path.waypoints[:-1], path.waypoints[1:]):
        if not adapter.is_edge_valid(start, goal):
            return False
    return True


class SuppliedStateAdapter:
    def __init__(self, state_fn):
        self.state_fn = state_fn

    def is_state_valid(self, configuration):
        xy = tuple(configuration.values)
        try:
            raw = self.state_fn(xy)
        except BackendFailure as error:
            raise AdapterError("state check could not complete") from error
        if type(raw) is not bool:
            raise AdapterError("state returned a non-Boolean result")
        return raw
