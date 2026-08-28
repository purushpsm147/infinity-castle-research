import pytest

from infinity_castle.exact_game import moving_gateway_castle
from infinity_castle.global_persistence import (
    PersistentRewireGame,
    c0_matches_base_successors,
    verify_global_persistence_clique_foothold,
)


@pytest.mark.parametrize("n", [3, 4, 5, 6])
def test_c0_matches_theorem_a_rewire_semantics(n):
    g, s, t = moving_gateway_castle(n, 1)
    assert c0_matches_base_successors(
        g,
        s,
        t,
        budget=1,
        lambda_min=1,
    )


@pytest.mark.parametrize("n", [3, 4, 5, 6, 7])
@pytest.mark.parametrize("tau", [1, 2, 3])
def test_positive_persistence_clique_certificate(n, tau):
    result = verify_global_persistence_clique_foothold(n, tau)
    assert result.certificate_verified
    assert result.first_successors_checked > 0
    assert result.relocated_gateway_cases == n - 2


def test_small_exact_solver_smoke_for_theorem_c_boundary():
    g, s, t = moving_gateway_castle(4, 1)

    c0 = PersistentRewireGame(
        g,
        s,
        t,
        budget=1,
        lambda_min=1,
        tau=0,
    )
    assert not c0.solve(agents=1, horizon=2).winnable
    assert c0.solve(agents=3, horizon=2).winnable

    c1 = PersistentRewireGame(
        g,
        s,
        t,
        budget=1,
        lambda_min=1,
        tau=1,
    )
    assert not c1.solve(agents=1, horizon=2).winnable
    assert c1.solve(agents=1, horizon=3).winnable
