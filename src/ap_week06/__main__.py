"""Completed caller. Run after all three student TODOs."""
from pathlib import Path
from .routes import RouteSettings, RouteEvaluator
from .selection import generate_route_grid
from .workflow import run_comparison, save_and_read


def main():
    destination = Path("artifacts/candidate_comparison.json")
    destination.unlink(missing_ok=True)
    Path("artifacts/candidate_selection.svg").unlink(missing_ok=True)
    candidates = generate_route_grid(-1.6, 1.6, 17, RouteSettings())
    comparison = run_comparison(candidates, RouteEvaluator())
    comparison["grid"] = {"height_min_m": -1.6, "height_max_m": 1.6,
                          "count_per_axis": 17, "candidate_count": 289, "spacing_m": 0.2}
    loaded = save_and_read(comparison, destination)
    accepted = sum(record["report"] is not None and record["report"]["valid"]
                   for record in loaded["results"].values())
    print(f"candidate_count={len(loaded['candidates'])}")
    print(f"accepted_count={accepted}")
    selected_id = loaded["selected_id"]
    print(f"selected_id={selected_id}")
    if selected_id is not None:
        candidate = loaded["candidates"][selected_id]
        metrics = loaded["results"][selected_id]["report"]["metrics"]
        print(f"a_m={candidate['a_m']:.3f}, b_m={candidate['b_m']:.3f}")
        print(f"raw_length_m={candidate['shortening']['raw_length_m']:.6f}")
        print(f"selected_length_m={metrics['length_m']:.6f}")
        print(f"clearance_m={metrics['clearance_m']:.6f}")
        print(f"measurement_method={metrics['method']}")
        print(f"sample_count={metrics['sample_count']}, segment_count={metrics['segment_count']}")
        print(f"completed={loaded['execution']['completed']}")
        print(f"final={loaded['execution']['final']['values']}")
    else:
        print("execution skipped")
    print(f"error_count={loaded['error_count']}")
    print(f"comparison_complete={loaded['comparison_complete']}")
    print(f"saved={destination.as_posix()}")


if __name__ == "__main__":
    main()
