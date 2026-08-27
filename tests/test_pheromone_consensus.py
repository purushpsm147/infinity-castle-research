import math

import networkx as nx
import numpy as np

from infinity_castle.consensus_math import (
    junction_success_probability,
    optimal_contrarian_fraction,
    pheromone_half_life,
)
from infinity_castle.policies import (
    AdaptiveConsensusNoMemoryPolicy,
    PheromoneConsensusPolicy,
    PheromonePureConsensusPolicy,
)


def test_closed_form_contrarian_fraction_matches_stationary_point():
    p, n, d = 0.8, 4, 4
    e = optimal_contrarian_fraction(p, n, d)
    assert math.isclose(e, 0.3812774736040629, rel_tol=1e-12)
    center = junction_success_probability(p, n, d, e)
    assert center >= junction_success_probability(p, n, d, max(0.0, e - 1e-4))
    assert center >= junction_success_probability(p, n, d, min(1.0, e + 1e-4))


def test_more_redundant_crows_can_support_more_contrarians():
    e2 = optimal_contrarian_fraction(0.95, 2, 4)
    e8 = optimal_contrarian_fraction(0.95, 8, 4)
    assert e8 > e2


def test_half_life():
    assert math.isclose(pheromone_half_life(0.5), 1.0)


def test_rewire_memory_marks_attacked_region():
    g = nx.path_graph(4)
    policy = PheromoneConsensusPolicy()
    policy.reset(g, 0, 3, 2)
    policy.last_traversals[(0, 1)] = 2
    policy.observe_rewire(g, [((0, 1), (0, 2))], [1, 1], 3)
    assert policy.failure[(0, 1)] >= 3.0
    assert policy.volatility[0] > 0
    assert policy.volatility[1] > 0


def test_no_memory_control_does_not_accumulate_pheromones():
    g = nx.path_graph(4)
    policy = AdaptiveConsensusNoMemoryPolicy()
    policy.reset(g, 0, 3, 2)
    policy.observe_transition(g, [0, 0], [1, 1], 3)
    assert policy.progress == {}
    assert policy.failure == {}
    assert policy.volatility == {}


def test_pure_consensus_cohort_takes_single_best_branch():
    g = nx.Graph()
    g.add_edges_from([(0, 1), (0, 2), (1, 3), (2, 4), (4, 3)])
    policy = PheromonePureConsensusPolicy()
    policy.reset(g, 0, 3, 4)
    moves = policy.choose_moves(g, [0, 0, 0, 0], 3, np.random.default_rng(1))
    assert len(set(moves)) == 1
    assert moves[0] == 1
