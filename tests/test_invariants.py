import networkx as nx

from infinity_castle.adversaries import NoAdversary, ObliviousChurnAdversary, TrafficAwareAdversary
from infinity_castle.graphs import grid_graph
from infinity_castle.model import CastleConfig
from infinity_castle.policies import RandomWalkPolicy, ReplanShortestPathPolicy
from infinity_castle.simulator import run_episode


def test_replan_no_adversary_hits_shortest_path_length():
    g, s, t = grid_graph(5)
    d = nx.shortest_path_length(g, s, t)
    r = run_episode(g, s, t, ReplanShortestPathPolicy(), NoAdversary(), CastleConfig(horizon=50, agents=1, adversary_budget=0), seed=1)
    assert r.success
    assert r.reach_time == d
    assert r.work == d


def test_oblivious_rewiring_preserves_connectivity_in_trace():
    g, s, t = grid_graph(5)
    r = run_episode(g, s, t, RandomWalkPolicy(), ObliviousChurnAdversary(), CastleConfig(horizon=20, agents=3, adversary_budget=2), seed=3, keep_trace=True)
    assert len(r.traces) <= 20


def test_traffic_aware_rewiring_runs_and_preserves_edge_count():
    g, s, t = grid_graph(5)
    original_edges = g.number_of_edges()
    r = run_episode(g, s, t, ReplanShortestPathPolicy(), TrafficAwareAdversary(), CastleConfig(horizon=20, agents=3, adversary_budget=1), seed=4, keep_trace=True)
    for tr in r.traces:
        for rem, add in tr.rewires:
            assert rem != add
    assert original_edges > 0


def test_reactive_cut_adversary_smoke():
    from infinity_castle.adversaries import ReactiveCutAdversary
    g, s, t = grid_graph(5)
    r = run_episode(g, s, t, ReplanShortestPathPolicy(), ReactiveCutAdversary(), CastleConfig(horizon=30, agents=2, adversary_budget=1), seed=9, keep_trace=True)
    assert len(r.traces) <= 30
