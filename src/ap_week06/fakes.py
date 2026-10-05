"""Small supplied test substitute with ordinary methods and recorded requests.

This fake uses a blocked-value lookup, not disk geometry. Passing its checks
demonstrates program interaction, not geometric correctness or physical safety.
"""
from .adapter import AdapterError
from .domain import Configuration
from .results import ExecutionResult


class FakeAdapter:
    def __init__(self, blocked_states=(), blocked_edges=(), fail_on=None):
        self.blocked_states = set(blocked_states)
        self.blocked_edges = set(blocked_edges)
        self.fail_on = fail_on
        self.calls = []

    def _record(self, operation, *values):
        self.calls.append((operation, *values))
        if self.fail_on == operation:
            raise AdapterError(f"fake {operation} failure")

    def is_state_valid(self, configuration):
        point = tuple(configuration.values)
        self._record("state", point)
        return point not in self.blocked_states

    def is_edge_valid(self, start, goal):
        a, b = tuple(start.values), tuple(goal.values)
        self._record("edge", a, b)
        return (a, b) not in self.blocked_edges

    def execute(self, path):
        points = tuple(tuple(point.values) for point in path.waypoints)
        self._record("execute", points)
        final = points[0]
        if final in self.blocked_states:
            return ExecutionResult(False, Configuration(final))
        for point in points[1:]:
            if point in self.blocked_states or (final, point) in self.blocked_edges:
                return ExecutionResult(False, Configuration(final))
            final = point
        return ExecutionResult(True, Configuration(final))
