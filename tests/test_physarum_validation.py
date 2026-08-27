import math

from infinity_castle.graphs import unequal_corridors
from infinity_castle.model import canon_edge
from infinity_castle.physarum_dynamics import initial_conductance, run_static_physarum, static_physarum_step


def route_mean(conductance, route):
    vals = [conductance[canon_edge(u, v)] for u, v in route]
    return sum(vals) / len(vals)


def test_equal_corridors_preserve_symmetry_in_canonical_static_dynamics():
    g, s, t, routes = unequal_corridors([4, 4, 4])
    d = initial_conductance(g, 1.0)
    for _ in range(50):
        d, _ = static_physarum_step(g, s, t, d, dt=0.05)
    means = [route_mean(d, route) for route in routes]
    assert max(means) - min(means) < 1e-10


def test_unequal_corridors_converge_to_unique_shortest_path():
    g, s, t, routes = unequal_corridors([3, 5, 7])
    d = run_static_physarum(g, s, t, steps=1000, dt=0.05)
    means = [route_mean(d, route) for route in routes]
    assert means[0] > 0.99
    assert means[1] < 1e-5
    assert means[2] < 1e-5
