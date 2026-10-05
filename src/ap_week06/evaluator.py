"""Completed protected evaluator. It does not execute, print or save a path."""
from .domain import PlanningModelError
from .model import ParametricPlanningProblem
from .results import EvaluationReport


class PathEvaluator:
    def __init__(self, adapter):
        names = ("is_state_valid", "is_edge_valid", "execute")
        if not all(callable(getattr(adapter, name, None)) for name in names):
            raise PlanningModelError("adapter must supply the three named methods")
        self.adapter = adapter

    def evaluate(self, problem):
        # Provided: require ParametricPlanningProblem, calculate metrics once,
        # reject infeasible metrics before external calls, then check saved
        # states followed by adjacent edges in order. Return on the first False.
        # Never call execute, print, draw, write files, or alter the problem.
        if not isinstance(problem, ParametricPlanningProblem):
            raise PlanningModelError("expected a ParametricPlanningProblem")
        metrics = problem.evaluate()
        if not metrics.feasible:
            return EvaluationReport(metrics=metrics, valid=False)
        for point in problem.path.waypoints:
            if not self.adapter.is_state_valid(point):
                return EvaluationReport(metrics=metrics, valid=False)
        for start, goal in zip(problem.path.waypoints[:-1], problem.path.waypoints[1:]):
            if not self.adapter.is_edge_valid(start, goal):
                return EvaluationReport(metrics=metrics, valid=False)
        return EvaluationReport(metrics=metrics, valid=True)
