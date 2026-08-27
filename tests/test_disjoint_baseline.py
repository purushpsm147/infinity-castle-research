import networkx as nx
import numpy as np

from infinity_castle.graphs import grid_graph, unequal_corridors
from infinity_castle.policies import EdgeDisjointPathPolicy


def test_edge_disjoint_policy_uses_all_four_corridors_at_source():
    g, s, t, _ = unequal_corridors([4, 4, 4, 4])
    policy = EdgeDisjointPathPolicy()
    policy.reset(g, s, t, 4)
    moves = policy.choose_moves(g, [s] * 4, t, np.random.default_rng(0))
    assert len(set(moves)) == 4


def test_grid_corner_has_only_two_edge_disjoint_routes():
    g, s, t = grid_graph(5)
    assert nx.edge_connectivity(g, s, t) == 2
    policy = EdgeDisjointPathPolicy()
    policy.reset(g, s, t, 4)
    moves = policy.choose_moves(g, [s] * 4, t, np.random.default_rng(0))
    assert len(set(moves)) == 2
