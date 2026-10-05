"""Provided application/storage. Every evaluation uses the prepared final path."""
from dataclasses import asdict
import json
from pathlib import Path as FilePath
from .selection import evaluate_candidates, select_shortest
from .routes import prepare_routes, replay_route


def run_comparison(candidates, evaluator, execute_selected=replay_route):
    prepared, shortening = prepare_routes(candidates)
    results = evaluate_candidates(prepared, evaluator)
    selected_id = select_shortest(results)
    execution = None if selected_id is None else execute_selected(prepared[selected_id])
    first = next(iter(prepared.values()), None)
    scene = None if first is None else {
        "bounds": {"lower": list(first.bounds.lower.values), "upper": list(first.bounds.upper.values)},
        "obstacles": [{"obstacle_id": o.obstacle_id, "center_xy": list(o.center.values),
                       "radius_m": o.radius_m} for o in first.obstacles]}
    error_count = sum(record.error is not None for record in results.values())
    return {
        "candidates": {key: {"a_m": p.a_m, "b_m": p.b_m,
                       "path_xy": p.path.as_array().tolist(), "settings": asdict(p.settings),
                       "shortening": shortening[key]} for key,p in prepared.items()},
        "scene": scene, "results": {key: asdict(value) for key,value in results.items()},
        "selected_id": selected_id, "execution": None if execution is None else asdict(execution),
        "error_count": error_count, "comparison_complete": error_count == 0}


def save_and_read(comparison, destination):
    destination = FilePath(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(comparison, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    return json.loads(destination.read_text(encoding="utf-8"))
