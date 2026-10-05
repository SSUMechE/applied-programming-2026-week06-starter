import math
import pytest
from ap_week06.adapter import AdapterError
from ap_week06.domain import Configuration, Path, PlanningModelError
from ap_week06.routes import problem_at_bends,edge_checker_for
from ap_week06.selection import shorten_route


def make_path(xy):
    return Path(Configuration(p) for p in xy)


def test_shortening_removes_safe_outer_bends_but_keeps_obstacle_avoidance():
    problem = problem_at_bends(-0.6,0.6)
    before = problem.path.as_array().tolist()
    path = shorten_route(problem.path,edge_checker_for(problem))
    assert path.as_array().tolist() == [[0,0],[2,-0.6],[4,0.6],[6,0]]
    assert path.length() == pytest.approx(6.50850336150234,abs=1e-12)
    assert problem.path.as_array().tolist() == before
    assert path is not problem.path


def test_shortening_never_removes_a_point_when_replacement_edge_is_rejected():
    path = make_path([(0,0),(1,1),(2,0)])
    result = shorten_route(path,lambda a,b:False)
    assert result.waypoints == path.waypoints
    assert result is not path


def test_shortening_restarts_and_terminates_at_two_points():
    path = make_path([(0,0),(1,2),(2,-1),(3,2),(4,0)])
    calls = []
    def checker(a,b):
        calls.append((a.values,b.values))
        return True
    result = shorten_route(path,checker)
    assert result.waypoints == (path.start,path.goal)
    assert len(calls) == 3+2+1


def test_shortening_chooses_greatest_gain_before_leftmost_and_restarts():
    path = make_path([(0,0),(1,0.1),(2,3),(3,0)])
    # Allow only the highest-gain removal; the first eligible point is worse.
    result = shorten_route(path,lambda a,b: (a.values,b.values) in [((0,0),(2,3)),((1,0.1),(3,0))])
    assert result.as_array().tolist() == [[0,0],[1,0.1],[3,0]]


def test_exact_tie_chooses_leftmost_point():
    path = make_path([(0,0),(0,1),(2,1),(2,0)])
    result = shorten_route(path,lambda a,b: (a.values,b.values) != ((0,0),(2,0)))
    assert result.as_array().tolist() == [[0,0],[2,1],[2,0]]


def test_zero_and_tiny_gain_do_not_delete_points():
    for height in (0,1e-7):
        path = make_path([(0,0),(1,height),(2,0)])
        assert len(shorten_route(path,lambda a,b:True).waypoints) == 3


def test_two_point_path_returns_a_new_path_without_checker_call():
    path = make_path([(0,0),(2,0)])
    def should_not_run(a,b):
        raise AssertionError("no internal point")
    result = shorten_route(path,should_not_run)
    assert result.waypoints == path.waypoints and result is not path


def test_checker_failure_propagates():
    def broken(a,b):
        raise AdapterError("checker unavailable")
    with pytest.raises(AdapterError,match="unavailable"):
        shorten_route(make_path([(0,0),(1,1),(2,0)]),broken)


@pytest.mark.parametrize("answer",[1,None,"yes"])
def test_checker_requires_a_boolean_result(answer):
    with pytest.raises(PlanningModelError,match="bool"):
        shorten_route(make_path([(0,0),(1,1),(2,0)]),lambda a,b:answer)


def test_bad_path_or_noncallable_checker_is_rejected():
    with pytest.raises(PlanningModelError):
        shorten_route("path",lambda a,b:True)
    with pytest.raises(PlanningModelError):
        shorten_route(make_path([(0,0),(1,1)]),None)
