"""Retained Week 5 single-obstacle input for comparison examples and supplied tests.

The Week 6 Assignment uses the two-obstacle RouteProblem in routes.py.
"""
from .domain import Configuration, ConfigurationBounds, Path, Obstacle


def supplied_case():
    """Return new completed domain objects, without constructing a TODO class."""
    points = [Configuration(point) for point in ((0, 0), (0, 2), (4, 2), (4, 0))]
    return {"start": points[0], "goal": points[-1],
            "bounds": ConfigurationBounds(Configuration((-1, -1)), Configuration((5, 3))),
            "obstacle": Obstacle("disk", Configuration((2, 0)), 0.5), "path": Path(points)}
