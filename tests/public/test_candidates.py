import math
import pytest
from ap_week06.candidates import problem_at_height, supplied_candidates
from ap_week06.model import PlanningSettings
from ap_week06.support import make_evaluator


@pytest.mark.parametrize("height,length,clearance,valid", [
    (0.0, 4.0, -0.5, False), (0.5, 5.0, 0.0, False),
    (1.0, 6.0, 0.5, True), (1.5, 7.0, 1.0, True), (2.0, 8.0, 1.5, True)])
def test_supplied_path_meanings(height, length, clearance, valid):
    problem = problem_at_height(height)
    report = make_evaluator(problem).evaluate(problem)
    assert report.metrics.length_m == pytest.approx(length, abs=1e-12)
    assert report.metrics.clearance_m == pytest.approx(clearance, abs=1e-12)
    assert report.valid is valid


def test_supplied_fixed_candidates_begin_with_the_week5_baseline():
    candidates = supplied_candidates()
    assert list(candidates) == ["detour_2", "direct", "triangle", "low_detour",
                                "corner_cut", "long_zigzag"]
    assert candidates["detour_2"].path.length() == 8.0
    assert len(candidates["direct"].path.waypoints) == 2


@pytest.mark.parametrize("candidate_id,coordinates,length,clearance,valid", [
    ("detour_2", [(0, 0), (0, 2), (4, 2), (4, 0)], 8.0, 1.5, True),
    ("direct", [(0, 0), (4, 0)], 4.0, -0.5, False),
    ("triangle", [(0, 0), (2, 1.5), (4, 0)], 5.0, math.sqrt(1.45) - 0.5, True),
    ("low_detour", [(0, 0), (0, 0.5), (4, 0.5), (4, 0)], 5.0, 0.0, False),
    ("corner_cut", [(0, 0), (1, 1), (3, 1), (4, 0)], 2.0 + 2.0 * math.sqrt(2), 0.5, True),
    ("long_zigzag", [(0, 0), (0, 2), (1, 2), (1, 1), (3, 1), (3, 2), (4, 2), (4, 0)],
     10.0, 0.5, False)])
def test_supplied_mixed_shapes_have_the_announced_geometry_and_sampled_metrics(
        candidate_id, coordinates, length, clearance, valid):
    problem = supplied_candidates()[candidate_id]
    report = make_evaluator(problem).evaluate(problem)
    assert [point.values for point in problem.path.waypoints] == coordinates
    assert report.metrics.length_m == pytest.approx(length, abs=1e-12)
    assert report.metrics.clearance_m == pytest.approx(clearance, abs=1e-12)
    assert report.valid is valid
