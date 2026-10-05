"""Completed connections to the supplied checks and geometric replay."""
from .adapter import CourseAdapter
from .backend import backend_for
from .evaluator import PathEvaluator


def make_evaluator(problem):
    """Create evaluate(problem) support for candidates sharing this scene."""
    backend = backend_for(problem)
    adapter = CourseAdapter(backend.state_valid, backend.edge_valid, backend.replay)
    return PathEvaluator(adapter)


def replay_selected(problem):
    """Return the supplied geometric replay's actual execution result."""
    backend = backend_for(problem)
    adapter = CourseAdapter(backend.state_valid, backend.edge_valid, backend.replay)
    return adapter.execute(problem.path)
