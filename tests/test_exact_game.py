import networkx as nx

from infinity_castle.exact_game import (
    ExactRewireGame,
    k23_castle,
    worst_case_transient_cut_arrival,
)
from infinity_castle.temporal_landmarks import (
    maximum_vertex_disjoint_journeys,
    minimum_temporal_vertex_separator,
    temporal_menger_witness,
)


def test_static_k23_one_crow_reaches_within_two_rounds():
    g, s, t = k23_castle()
    game = ExactRewireGame(g, s, t, budget=0, lambda_min=3)
    result = game.solve(agents=1, horizon=2)
    assert result.winnable


def test_transient_cut_b_plus_one_guarantees_arrival():
    # Two length-3 edge-disjoint paths against one simultaneous cut.
    arrival = worst_case_transient_cut_arrival([3, 3], budget=1)
    assert arrival is not None
    assert arrival <= 6

    # Three paths against b=2 also guarantee arrival.
    arrival = worst_case_transient_cut_arrival([2, 3, 4], budget=2)
    assert arrival is not None
    assert arrival <= 9


def test_transient_cut_at_or_below_budget_can_be_blocked_forever():
    assert worst_case_transient_cut_arrival([3], budget=1) is None
    assert worst_case_transient_cut_arrival([2, 2], budget=2) is None


def test_all_exact_rewire_successors_preserve_invariants():
    g, s, t = k23_castle()
    game = ExactRewireGame(g, s, t, budget=2, lambda_min=2)
    successors = game.rewire_successors(game.initial_edges)
    assert successors
    for edges in successors:
        gg = game._graph(edges)
        assert len(edges) == 6
        assert nx.is_connected(gg)
        assert nx.edge_connectivity(gg, s, t) >= 2


def test_temporal_vertex_menger_violation_landmark():
    labels, s, t = temporal_menger_witness()
    assert maximum_vertex_disjoint_journeys(labels, s, t) == 1
    assert minimum_temporal_vertex_separator(labels, s, t) == 2
