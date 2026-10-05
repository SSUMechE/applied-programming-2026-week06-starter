"""Provided two independent axes, not the student's general generator."""
import numpy as np
heights = np.linspace(-1.6, 1.6, 3)
print("heights=", heights.tolist())
for i,a in enumerate(heights):
    for j,b in enumerate(heights):
        print(f"grid_{i}_{j}: a_m={float(a):.1f}, b_m={float(b):.1f}")
print(f"candidate_count={len(heights)**2}")
