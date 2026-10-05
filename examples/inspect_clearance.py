"""Provided contrast: point samples and the nearest point on each whole segment."""
from ap_week06.domain import Configuration, Path, Obstacle
from ap_week06.provided import sample_path, path_metrics
from ap_week06.routes import segment_clearance

disk = Obstacle("disk", Configuration((2,0)), 0.5)
for height in (1.5, 1.6):
    path = Path(Configuration(xy) for xy in [(0,0),(2,height),(4,0)])
    sampled = path_metrics(path, sample_path(path,0.5,"interpolated"), disk)["clearance_m"]
    continuous = min(segment_clearance(a,b,disk)[0]
                     for a,b in zip(path.waypoints[:-1],path.waypoints[1:]))
    print(f"height_m={height:.1f}, sampled_clearance_m={sampled:.9f}, "
          f"continuous_clearance_m={continuous:.9f}")
    print(f"minimum=0.703: sampled_pass={sampled >= 0.703}, continuous_pass={continuous >= 0.703}")
