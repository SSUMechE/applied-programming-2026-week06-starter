"""Supplied result records. Metric feasibility and external validity stay distinct."""
from dataclasses import dataclass
from .domain import Configuration, PlanningModelError
from .model import EvaluationResult


@dataclass(frozen=True)
class EvaluationReport:
    metrics: EvaluationResult
    valid: bool

    def __post_init__(self):
        if not isinstance(self.metrics, EvaluationResult) or type(self.valid) is not bool:
            raise PlanningModelError("report requires EvaluationResult and bool")
        if self.valid and not self.metrics.feasible:
            raise PlanningModelError("valid cannot be True when metrics are infeasible")


@dataclass(frozen=True)
class ExecutionResult:
    completed: bool
    final: Configuration

    def __post_init__(self):
        if type(self.completed) is not bool:
            raise PlanningModelError("completed must be bool")
        if not isinstance(self.final, Configuration) or self.final.dimension != 2:
            raise PlanningModelError("final must be a two-dimensional Configuration")


@dataclass(frozen=True)
class CandidateResult:
    """A completed report, or a failed check with no report and its message."""
    report: EvaluationReport | None
    error: str | None
