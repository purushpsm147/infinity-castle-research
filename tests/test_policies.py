from infinity_castle.adversaries import NoAdversary
from infinity_castle.graphs import ladder_graph
from infinity_castle.model import CastleConfig
from infinity_castle.policies import DisjointPathPolicy, GenericReinforcementPolicy, PhysarumPolicy
from infinity_castle.simulator import run_episode


def test_core_policies_smoke():
    g, s, t = ladder_graph(8)
    cfg = CastleConfig(horizon=40, agents=3, adversary_budget=0)
    for policy in (DisjointPathPolicy(), GenericReinforcementPolicy(), PhysarumPolicy()):
        r = run_episode(g, s, t, policy, NoAdversary(), cfg, seed=7)
        assert r.work >= 0
        assert len(r.final_positions) == 3
