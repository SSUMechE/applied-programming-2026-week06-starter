"""Completed short illustration: one caller, two supplied checking functions."""
from ap_week06.backend import backend_for
from ap_week06.candidates import supplied_candidates


def check_position(xy, checker):
    return checker(xy)


def preset_rejection(point):
    return False


problem = supplied_candidates()["detour_2"]
backend = backend_for(problem)
xy = problem.start.values
print("provided check:", check_position(xy, backend.state_valid))
print("preset answer:", check_position(xy, preset_rejection))
