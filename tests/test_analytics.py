import math

from infinity_castle.analytics import (
    effective_support,
    expected_occupied_routes,
    herfindahl_index,
    occupancy_survival_probability,
    shannon_entropy,
    top_b_mass,
)
from infinity_castle.graphs import parallel_corridors


def test_uniform_four_way_support():
    counts = [1, 1, 1, 1]
    assert math.isclose(shannon_entropy(counts), math.log(4))
    assert math.isclose(effective_support(counts), 4.0)
    assert math.isclose(herfindahl_index(counts), 0.25)
    assert math.isclose(top_b_mass(counts, 1), 0.25)


def test_concentrated_traffic_is_easier_to_cover():
    assert top_b_mass([4, 0, 0, 0], 1) == 1.0
    assert top_b_mass([1, 1, 1, 1], 1) == 0.25


def test_occupancy_formula_known_case():
    assert math.isclose(expected_occupied_routes(2, 4), 1.75)
    assert math.isclose(occupancy_survival_probability(2, 4, 1), 0.75)
    assert math.isclose(occupancy_survival_probability(4, 4, 2), 0.65625)


def test_parallel_corridor_connectivity_and_cut_size():
    import networkx as nx
    g, s, t = parallel_corridors(5, 6)
    assert nx.is_connected(g)
    assert nx.edge_connectivity(g, s, t) == 5
