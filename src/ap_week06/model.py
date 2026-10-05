"""Provided completed Week 5 model. Do not edit in Week 6."""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import TypedDict
from .domain import Configuration, ConfigurationBounds, Path, Obstacle, PlanningModelError
from .provided import sample_path, path_metrics, constraint_margins


@dataclass(frozen=True)
class EvaluationResult:
    """Computed values and decision, independent of any drawing."""
    length_m: float
    clearance_m: float
    total_turn_rad: float
    clearance_margin_m: float
    length_margin_m: float
    feasible: bool
    method: str
    sample_count: int


class PlotData(TypedDict):
    path_xy: list[list[float]]
    samples_xy: list[list[float]]
    obstacle_center_xy: list[float]
    obstacle_radius_m: float
    labels: list[str]


@dataclass(frozen=True)
class PlanningSettings:
    min_clearance_m: float = 0.5
    max_length_m: float = 9.0
    resolution_m: float = 0.5
    method: str = "interpolated"

    def __post_init__(self) -> None:
        # Completed Week 5 validation: Validate and normalize settings. See Reading Sections 1 and 5.
        for name in ("min_clearance_m", "max_length_m", "resolution_m"):
            value = getattr(self, name)
            if type(value) not in (int, float):
                raise PlanningModelError(f"{name} must be a finite real number")
            try:
                number = float(value)
            except (OverflowError, ValueError) as error:
                raise PlanningModelError(f"{name} must be a finite real number") from error
            if not math.isfinite(number):
                raise PlanningModelError(f"{name} must be a finite real number")
            object.__setattr__(self, name, number)
        if not 0.0 <= self.min_clearance_m <= 2.0:
            raise PlanningModelError("min_clearance_m must lie in [0.0, 2.0]")
        if not 0.0 < self.max_length_m <= 20.0:
            raise PlanningModelError("max_length_m must lie in (0.0, 20.0]")
        if not 0.05 <= self.resolution_m <= 1.0:
            raise PlanningModelError("resolution_m must lie in [0.05, 1.0]")
        if not isinstance(self.method, str) or self.method not in ("waypoints", "interpolated"):
            raise PlanningModelError("method must be 'waypoints' or 'interpolated'")


@dataclass(frozen=True)
class ParametricPlanningProblem:
    start: Configuration
    goal: Configuration
    bounds: ConfigurationBounds
    obstacle: Obstacle
    path: Path
    settings: PlanningSettings

    def __post_init__(self) -> None:
        # Completed Week 5 object checks: Validate object relationships and path consistency.
        expected = (("start", Configuration), ("goal", Configuration),
                    ("bounds", ConfigurationBounds), ("obstacle", Obstacle),
                    ("path", Path), ("settings", PlanningSettings))
        for name, kind in expected:
            if not isinstance(getattr(self, name), kind):
                raise PlanningModelError(f"{name} must be a {kind.__name__}")
        if any(item.dimension != 2 for item in (self.start, self.goal, self.bounds, self.path)):
            raise PlanningModelError("start, goal, bounds and path must be two-dimensional")
        if not 2 <= len(self.path.waypoints) <= 32:
            raise PlanningModelError("path must have between 2 and 32 waypoints")
        if self.path.start != self.start or self.path.goal != self.goal:
            raise PlanningModelError("path endpoints must match start and goal")
        if not all(self.bounds.contains(point) for point in self.path.waypoints):
            raise PlanningModelError("all waypoints must lie inside inclusive bounds")
        if any(a == b for a, b in zip(self.path.waypoints[:-1], self.path.waypoints[1:])):
            raise PlanningModelError("consecutive waypoints must differ")

    def evaluate(self) -> EvaluationResult:
        # Completed Week 5 calculation: Use supplied calculations and return the two-margin decision.
        samples = sample_path(self.path, self.settings.resolution_m, self.settings.method)
        metrics = path_metrics(self.path, samples, self.obstacle)
        margins = constraint_margins(metrics["length_m"], metrics["clearance_m"],
                                     self.settings.min_clearance_m, self.settings.max_length_m)
        feasible = margins["clearance_margin_m"] >= 0.0 and margins["length_margin_m"] >= 0.0
        return EvaluationResult(**metrics, **margins, feasible=bool(feasible),
                                method=self.settings.method, sample_count=len(samples))

    def to_plot_data(self) -> PlotData:
        # Provided and protected: prepare display data without evaluating or rendering.
        samples = sample_path(self.path, self.settings.resolution_m, self.settings.method)
        labels = ["start"] + [f"waypoint_{index}" for index in range(1, len(self.path.waypoints) - 1)] + ["goal"]
        return {"path_xy": self.path.as_array().tolist(), "samples_xy": samples.tolist(),
                "obstacle_center_xy": list(self.obstacle.center.values),
                "obstacle_radius_m": float(self.obstacle.radius_m), "labels": labels}
