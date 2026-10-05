"""Ready basic checks for the three Week 6 algorithms."""
from dataclasses import replace
from ap_week06.domain import Configuration, Path
from ap_week06.routes import (
    RouteSettings, RouteEvaluator, problem_at_bends, edge_checker_for,
)
from ap_week06.selection import (
    generate_route_grid, shorten_route, evaluate_candidates, select_shortest,
)


def test_grid_contains_independent_height_pairs():
    candidates = generate_route_grid(-1.0, 1.0, 3, RouteSettings())
    assert len(candidates) == 9
    assert candidates["grid_0_2"].a_m == -1.0
    assert candidates["grid_0_2"].b_m == 1.0


def test_shortening_keeps_the_bends_needed_to_avoid_obstacles():
    raw = problem_at_bends(-0.6, 0.6)
    before = raw.path.as_array().tolist()
    final = shorten_route(raw.path, edge_checker_for(raw))
    assert final.as_array().tolist() == [[0, 0], [2, -0.6], [4, 0.6], [6, 0]]
    assert final.length() < raw.path.length()
    assert raw.path.as_array().tolist() == before


def test_selection_chooses_the_shortest_accepted_path():
    settings = RouteSettings(max_length_m=6.9)
    long = replace(
        problem_at_bends(-0.8, 0.8, settings),
        path=Path(Configuration(xy) for xy in [(0, 0), (2, -0.8), (4, 0.8), (6, 0)]),
    )
    short = replace(
        problem_at_bends(-0.6, 0.6, settings),
        path=Path(Configuration(xy) for xy in [(0, 0), (2, -0.6), (4, 0.6), (6, 0)]),
    )
    blocked = problem_at_bends(0, 0, settings)
    results = evaluate_candidates(
        {"long": long, "blocked": blocked, "short": short}, RouteEvaluator(),
    )
    assert select_shortest(results) == "short"
    assert select_shortest({}) is None
