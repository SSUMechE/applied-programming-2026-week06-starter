from dataclasses import replace
import pytest
from ap_week06.domain import Configuration,Path,PlanningModelError
from ap_week06.routes import (RouteSettings,RouteEvaluator,problem_at_bends,segment_clearance,
                              edge_checker_for,prepare_routes)
from ap_week06.selection import generate_route_grid,evaluate_candidates,select_shortest


def test_provided_raw_and_fixed_final_geometry_and_method_metadata():
    raw = problem_at_bends(-0.6,0.6)
    final = replace(raw,path=Path(Configuration(p) for p in [(0,0),(2,-0.6),(4,0.6),(6,0)]))
    evaluator = RouteEvaluator()
    assert evaluator.evaluate(raw).valid is False
    report = evaluator.evaluate(final)
    assert report.valid is True
    assert report.metrics.length_m == pytest.approx(6.50850336150234,abs=1e-12)
    assert report.metrics.clearance_m == pytest.approx(0.25749292571254423,abs=1e-12)
    assert report.metrics.method == "continuous_segments"
    assert report.metrics.sample_count == 0 and report.metrics.segment_count == 3


def test_provided_checker_rejects_shortcut_through_obstacle():
    p = problem_at_bends(-0.6,0.6)
    check = edge_checker_for(p)
    assert check(Configuration((0,0)),Configuration((2,-0.6))) is True
    assert check(Configuration((0,0)),Configuration((4,0.6))) is False


def test_clearance_checks_segment_interior_and_both_endpoint_cases():
    p = problem_at_bends(-0.6,0.6)
    disk = p.obstacles[0]
    clearance,nearest = segment_clearance(Configuration((0,0.4)),Configuration((4,0.4)),disk)
    assert nearest == (2.0,0.4) and clearance == -0.6
    assert segment_clearance(Configuration((0,0)),Configuration((1,0)),disk)[1] == (1.0,0.0)
    assert segment_clearance(Configuration((3,0)),Configuration((4,0)),disk)[1] == (3.0,0.0)


def test_preparation_reuses_id_and_evaluates_final_not_raw_path():
    raw = {"case":problem_at_bends(-0.6,0.6)}
    prepared,records = prepare_routes(raw)
    assert prepared["case"] is not raw["case"]
    assert len(raw["case"].path.waypoints) == 6
    assert len(prepared["case"].path.waypoints) == 4
    assert records["case"]["removed_original_indices"] == [1,4]
    assert records["case"]["path_xy"] == prepared["case"].path.as_array().tolist()
    assert RouteEvaluator().evaluate(prepared["case"]).valid is True


@pytest.mark.parametrize("count,accepted,selected",[(9,0,None),(17,1,"grid_5_11")])
def test_same_limits_coarse_miss_and_fine_accepted_route(count,accepted,selected):
    raw = generate_route_grid(-1.6,1.6,count,RouteSettings())
    prepared,_ = prepare_routes(raw)
    results = evaluate_candidates(prepared,RouteEvaluator())
    assert sum(record.report.valid for record in results.values()) == accepted
    assert select_shortest(results) == selected


def test_max_length_is_final_constraint_not_early_shortcut_rejection():
    raw = problem_at_bends(-0.6,0.6)
    assert raw.path.length() > raw.settings.max_length_m
    prepared,_ = prepare_routes({"raw":raw})
    assert RouteEvaluator().evaluate(prepared["raw"]).valid is True


@pytest.mark.parametrize("a,b",[(-0.5,0.5),(-0.8,0.8)])
def test_nearby_routes_fail_different_constraints(a,b):
    prepared,_ = prepare_routes({"p":problem_at_bends(a,b)})
    report = RouteEvaluator().evaluate(prepared["p"])
    assert report.valid is False
    if a == -0.5:
        assert report.metrics.clearance_margin_m < 0
    else:
        assert report.metrics.length_margin_m < 0


def test_route_problem_owns_immutable_path_and_obstacles():
    p = problem_at_bends(-0.6,0.6)
    points = list(p.path.waypoints)
    owned = replace(p,path=Path(points),obstacles=list(p.obstacles))
    points.clear()
    assert len(owned.path.waypoints) == 6
    assert isinstance(owned.obstacles,tuple)
    assert owned.path is not p.path
    with pytest.raises(PlanningModelError):
        problem_at_bends(True,0)
