import pytest
from ap_week06.domain import PlanningModelError
from ap_week06.routes import RouteSettings
from ap_week06.selection import generate_route_grid


def test_grid_has_two_independent_axes_in_announced_order():
    settings = RouteSettings()
    grid = generate_route_grid(-1.6,1.6,3,settings)
    assert list(grid) == [f"grid_{i}_{j}" for i in range(3) for j in range(3)]
    assert [(p.a_m,p.b_m) for p in grid.values()] == [(a,b) for a in (-1.6,0,1.6) for b in (-1.6,0,1.6)]
    assert all(p.settings == settings for p in grid.values())
    assert len(grid["grid_1_1"].path.waypoints) == 4


@pytest.mark.parametrize("count",[2,9,17,25])
def test_grid_count_endpoints_and_independent_path_ownership(count):
    grid = generate_route_grid(-1.6,1.6,count,RouteSettings())
    assert len(grid) == count*count
    assert (grid["grid_0_0"].a_m,grid["grid_0_0"].b_m) == (-1.6,-1.6)
    last = grid[f"grid_{count-1}_{count-1}"]
    assert (last.a_m,last.b_m) == (1.6,1.6)
    assert len({id(p.path) for p in grid.values()}) == count*count


@pytest.mark.parametrize("low,high,count",[(-1.7,1.6,3),(-1.6,1.7,3),(0,0,3),(1,-1,3),
    (-1,1,1),(-1,1,26),(-1,1,3.0),(-1,1,True),(float("nan"),1,3),(False,1,3)])
def test_grid_uses_supplied_validation(low,high,count):
    with pytest.raises(PlanningModelError):
        generate_route_grid(low,high,count,RouteSettings())
