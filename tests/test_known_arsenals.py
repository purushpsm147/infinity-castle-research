import networkx as nx

from infinity_castle.adversaries import NoAdversary, ReactiveCutAdversary
from infinity_castle.graphs import grid_graph
from infinity_castle.known_arsenals import (
    EXP3MinimaxHybridPolicy,
    EXP3RoutingPolicy,
    MinimaxTrafficPolicy,
    RobustMDPPolicy,
)
from infinity_castle.model import CastleConfig
from infinity_castle.simulator import run_episode


def test_known_arsenals_smoke_without_adversary():
    g, s, t = grid_graph(4)
    cfg = CastleConfig(horizon=30, agents=4, adversary_budget=0)
    for policy in (
        EXP3RoutingPolicy(),
        MinimaxTrafficPolicy(),
        RobustMDPPolicy(),
        EXP3MinimaxHybridPolicy(),
    ):
        result = run_episode(
            g, s, t, policy, NoAdversary(), cfg,
            seed=7, separate_rngs=True,
        )
        assert len(result.final_positions) == 4
        assert result.work >= 0


def test_known_arsenals_survive_reactive_cut_execution():
    g, s, t = grid_graph(4)
    cfg = CastleConfig(horizon=20, agents=4, adversary_budget=1)
    for policy in (
        EXP3RoutingPolicy(),
        MinimaxTrafficPolicy(),
        RobustMDPPolicy(),
        EXP3MinimaxHybridPolicy(),
    ):
        result = run_episode(
            g, s, t, policy, ReactiveCutAdversary(), cfg,
            seed=11, separate_rngs=True,
        )
        assert result.work >= 0


def test_minimax_spreads_colocated_crows_when_options_exist():
    import numpy as np
    g = nx.Graph()
    g.add_edges_from([
        ("s", "a"), ("s", "b"), ("s", "c"),
        ("a", "t"), ("b", "t"), ("c", "t"),
    ])
    policy = MinimaxTrafficPolicy(slack=0)
    policy.reset(g, "s", "t", 6)
    moves = policy.choose_moves(g, ["s"] * 6, "t", np.random.default_rng(1))
    assert set(moves) == {"a", "b", "c"}
