"""Completed inspection. Runs before all three student TODOs."""
from ap_week06.candidates import supplied_candidates
from ap_week06.support import make_evaluator


candidates = supplied_candidates()
evaluator = make_evaluator(candidates["detour_2"])
print("candidate | length_m | clearance_m | feasible | valid")
for candidate_id, problem in candidates.items():
    report = evaluator.evaluate(problem)
    metrics = report.metrics
    print(f"{candidate_id} | {metrics.length_m:.3f} | "
          f"{metrics.clearance_m:.3f} | {metrics.feasible} | {report.valid}")
