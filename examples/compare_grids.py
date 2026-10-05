"""Compare the student's full pipelines under the same constraints."""
from ap_week06.routes import RouteSettings, RouteEvaluator
from ap_week06.selection import generate_route_grid
from ap_week06.workflow import run_comparison

for count in (9,17):
    candidates = generate_route_grid(-1.6,1.6,count,RouteSettings())
    data = run_comparison(candidates, RouteEvaluator())
    accepted = sum(record["report"] is not None and record["report"]["valid"]
                   for record in data["results"].values())
    print(f"count_per_axis={count}, candidate_count={count*count}, accepted_count={accepted}, "
          f"selected_id={data['selected_id']}")
    if data["selected_id"] is not None:
        print(f"selected_length_m={data['results'][data['selected_id']]['report']['metrics']['length_m']:.6f}")
