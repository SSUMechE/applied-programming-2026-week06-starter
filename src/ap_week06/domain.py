"""Provided Week 3-compatible values and Week 4 obstacle. See PROVENANCE.md."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import math

import numpy as np
from numpy.typing import NDArray

from .geometry import polyline_length


ConfigurationLike = Sequence[float] | NDArray[np.generic]


class PlanningModelError(ValueError):
    """Raised when a planning-domain invariant is violated."""


def _normalized_values(values: ConfigurationLike, *, name: str) -> tuple[float, ...]:
    """Return an owned tuple of finite real values or raise the public error."""
    if isinstance(values, (str, bytes)):
        raise PlanningModelError(f"{name} must be a one-dimensional numeric sequence")
    if isinstance(values, Sequence) and any(
        isinstance(value, (bool, np.bool_)) for value in values
    ):
        raise PlanningModelError(f"{name} must contain real non-Boolean values")
    try:
        array = np.asarray(values)
    except (TypeError, ValueError, OverflowError) as exc:
        raise PlanningModelError(
            f"{name} must be a one-dimensional numeric sequence"
        ) from exc
    if array.ndim != 1 or array.size == 0:
        raise PlanningModelError(f"{name} must be a non-empty one-dimensional sequence")
    if array.dtype == object or not np.issubdtype(array.dtype, np.number):
        raise PlanningModelError(f"{name} must contain numeric values")
    if np.issubdtype(array.dtype, np.bool_) or np.issubdtype(
        array.dtype, np.complexfloating
    ):
        raise PlanningModelError(f"{name} must contain real non-Boolean values")
    try:
        normalized = np.asarray(array, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise PlanningModelError(f"{name} contains an unrepresentable value") from exc
    if not np.isfinite(normalized).all():
        raise PlanningModelError(f"{name} must contain only finite values")
    return tuple(float(value) for value in normalized)


@dataclass(frozen=True)
class Configuration:
    """One configuration represented by owned finite coordinates."""

    values: ConfigurationLike

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", _normalized_values(self.values, name="values"))

    @property
    def dimension(self) -> int:
        """Return the number of coordinates."""
        return len(self.values)

    def as_array(self) -> NDArray[np.float64]:
        """Return a new float64 array that the caller may modify."""
        return np.array(self.values, dtype=np.float64, copy=True)


@dataclass(frozen=True)
class ConfigurationBounds:
    """Inclusive lower and upper limits for one configuration space."""

    lower: Configuration
    upper: Configuration

    def __post_init__(self) -> None:
        if not isinstance(self.lower, Configuration) or not isinstance(
            self.upper, Configuration
        ):
            raise PlanningModelError("lower and upper must be Configuration objects")
        if self.lower.dimension != self.upper.dimension:
            raise PlanningModelError("lower and upper must have the same dimension")
        if not np.all(self.lower.as_array() < self.upper.as_array()):
            raise PlanningModelError(
                "every lower bound must be strictly below its upper bound"
            )

    @property
    def dimension(self) -> int:
        """Return the accepted configuration dimension."""
        return self.lower.dimension

    def contains(self, configuration: Configuration) -> bool:
        """Return whether a configuration lies inside the inclusive bounds."""
        if not isinstance(configuration, Configuration):
            raise PlanningModelError("configuration must be a Configuration object")
        if configuration.dimension != self.dimension:
            raise PlanningModelError("configuration dimension does not match the bounds")
        values = configuration.as_array()
        return bool(
            np.all(self.lower.as_array() <= values)
            and np.all(values <= self.upper.as_array())
        )


@dataclass(frozen=True)
class Path:
    """An ordered sequence of compatible configurations."""

    waypoints: Sequence[Configuration]

    def __post_init__(self) -> None:
        if isinstance(self.waypoints, (str, bytes)):
            raise PlanningModelError("waypoints must be Configuration objects")
        try:
            owned = tuple(self.waypoints)
        except TypeError as exc:
            raise PlanningModelError("waypoints must be Configuration objects") from exc
        if len(owned) < 2:
            raise PlanningModelError("a path must contain at least two waypoints")
        if not all(isinstance(item, Configuration) for item in owned):
            raise PlanningModelError("every waypoint must be a Configuration object")
        dimension = owned[0].dimension
        if any(item.dimension != dimension for item in owned[1:]):
            raise PlanningModelError("all waypoints must have the same dimension")
        object.__setattr__(self, "waypoints", owned)

    @property
    def dimension(self) -> int:
        return self.waypoints[0].dimension

    @property
    def start(self) -> Configuration:
        return self.waypoints[0]

    @property
    def goal(self) -> Configuration:
        return self.waypoints[-1]

    def as_array(self) -> NDArray[np.float64]:
        return np.stack([point.as_array() for point in self.waypoints], axis=0)

    def length(self) -> float:
        return polyline_length(self.as_array())


@dataclass(frozen=True)
class Obstacle:
    """A named circular obstacle in the two-dimensional planning scene."""

    obstacle_id: str
    center: Configuration
    radius_m: float

    def __post_init__(self) -> None:
        if not isinstance(self.obstacle_id, str) or not self.obstacle_id.strip():
            raise PlanningModelError("obstacle_id must be a non-empty string")
        object.__setattr__(self, "obstacle_id", self.obstacle_id.strip())
        if not isinstance(self.center, Configuration) or self.center.dimension != 2:
            raise PlanningModelError("obstacle center must be a 2-D Configuration")
        if isinstance(self.radius_m, bool) or not isinstance(self.radius_m, (int, float)):
            raise PlanningModelError("radius_m must be a positive finite number")
        try:
            radius = float(self.radius_m)
        except (ValueError, OverflowError) as error:
            raise PlanningModelError("radius_m must be a positive finite number") from error
        if not math.isfinite(radius) or radius <= 0.0:
            raise PlanningModelError("radius_m must be a positive finite number")
        object.__setattr__(self, "radius_m", radius)
