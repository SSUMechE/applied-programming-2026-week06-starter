"""Provided practice inputs. Copy into ignored practice/ before changing values.

Fixed routes expose geometry outcomes before the TODOs. They do not implement
the general greedy shortener or grid generator.
"""
from dataclasses import replace
from ap_week06.domain import Configuration, Path
from ap_week06.routes import problem_at_bends, RouteEvaluator, RouteSettings

A_M = -0.6
B_M = 0.6
MAX_LENGTH_M = 6.8
MIN_CLEARANCE_M = 0.25
raw = problem_at_bends(A_M,B_M,RouteSettings(MIN_CLEARANCE_M,MAX_LENGTH_M))
final = replace(raw, path=Path(Configuration(xy) for xy in [(0,0),(2,A_M),(4,B_M),(6,0)]))
for name,problem in (("raw",raw),("final",final)):
    report = RouteEvaluator().evaluate(problem)
    print(f"{name}: length_m={report.metrics.length_m:.6f}, "
          f"clearance_m={report.metrics.clearance_m:.6f}, valid={report.valid}")
