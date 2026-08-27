import networkx as nx
import pytest

from infinity_castle.exact_game import (
    ExactRewireGame,
    moving_gateway_castle,
    verify_moving_gateway_threshold,
)


CASES = [
    (4, 1, 1, 3),
    (5, 1, 1, 4),
    (5, 2, 2, 3),
    (6, 1, 1, 5),
    (6, 2, 2, 4),
]


@pytest.mark.parametrize("n,d,b,expected", CASES)
def test_moving_gateway_threshold_certificates(n, d, b, expected):
    result = verify_moving_gateway_threshold(n, d, budget=b)
    assert result.agents == expected == n - d
    assert result.lower_invariant_verified
    assert result.upper_force_verified
    assert result.lower_cases_checked > 0
    assert result.lower_moves_checked > 0
    assert result.upper_rewires_checked > 0


@pytest.mark.parametrize("n,d,_,expected", CASES)
def test_gateway_family_has_expected_snapshot_connectivity(n, d, _, expected):
    g, s, t = moving_gateway_castle(n, d)
    assert len(g) == n
    assert g.degree[t] == d
    assert nx.edge_connectivity(g, s, t) == d
    assert expected == n - d


def test_smallest_case_matches_independent_exact_solver():
    # The theorem predicts K*=3 for G_{4,1}. The lower certificate is
    # eventual; this independent finite solver should agree on a long-enough
    # finite prefix and on the 2-round upper certificate.
    g, s, t = moving_gateway_castle(4, 1)
    game = ExactRewireGame(g, s, t, budget=1, lambda_min=1)

    assert not game.solve(agents=2, horizon=8).winnable
    assert game.solve(agents=3, horizon=2).winnable


def test_lower_certificate_allows_zero_swap_when_gateways_stay_free():
    # Zero edits are part of the adversary action set. The verifier's strategy
    # may keep an already-free gateway and therefore use fewer than d swaps.
    result = verify_moving_gateway_threshold(5, 2, budget=2)
    assert result.lower_invariant_verified


def test_source_is_initially_not_a_gateway():
    for n, d, _, _ in CASES:
        g, s, t = moving_gateway_castle(n, d)
        assert not g.has_edge(s, t)
