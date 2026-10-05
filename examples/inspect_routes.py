"""Provided fixed-input demonstration. No general student implementation called."""
from dataclasses import asdict, replace
from ap_week06.domain import Configuration, Path
from ap_week06.routes import problem_at_bends, RouteEvaluator, edge_checker_for
from ap_week06.workflow import save_and_read

raw = problem_at_bends(-0.6, 0.6)
final = replace(raw, path=Path(Configuration(xy) for xy in [(0,0),(2,-0.6),(4,0.6),(6,0)]))
evaluator = RouteEvaluator()
reports = {}
for label, problem in (("raw", raw), ("final", final)):
    report = evaluator.evaluate(problem)
    reports[f"{label}_report"] = asdict(report)
    print(f"{label}: length_m={report.metrics.length_m:.6f}, "
          f"clearance_m={report.metrics.clearance_m:.6f}, valid={report.valid}")
data = {"a_m": raw.a_m, "b_m": raw.b_m,
        "raw_path_xy": raw.path.as_array().tolist(), "path_xy": final.path.as_array().tolist(),
        **reports}
loaded = save_and_read(data, "artifacts/route_inspection.json")
check = edge_checker_for(raw)
print("outer shortcut allowed:", check(raw.path.waypoints[0], raw.path.waypoints[2]))
print("inner shortcut allowed:", check(final.path.waypoints[0], final.path.waypoints[2]))
print("saved=artifacts/route_inspection.json")
