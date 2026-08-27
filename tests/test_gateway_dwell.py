import math

import networkx as nx
import pytest

from infinity_castle.gateway_dwell import (
    admissible_gateway_sets,
    contiguous_grid,
    cycle_d1_formula,
    cycle_d2_formula,
    distance_transversal_number,
    path_d1_formula,
    verify_gateway_dwell_threshold,
)


@pytest.mark.parametrize(
    "m,d,tau,expected",
    [
        # Clique: tau=0 recovers moving-gateway saturation; tau>=1 collapses to one.
        (4, 1, 0, 4),
        (5, 2, 0, 4),
        (6, 3, 0, 4),
        (6, 1, 1, 1),
        (7, 3, 1, 1),
        (8, 2, 2, 1),
    ],
)
def test_clique_predictions(m, d, tau, expected):
    core = nx.complete_graph(m)
    result = verify_gateway_dwell_threshold(core, source=0, d=d, tau=tau)
    assert result.rho == expected
    assert result.lower_verified
    assert result.upper_verified


@pytest.mark.parametrize(
    "m,tau",
    [
        (4, 0),
        (5, 1),
        (6, 1),
        (8, 2),
        (10, 1),
        (12, 2),
    ],
)
def test_path_d1_formula_and_threshold_sides(m, tau):
    core = nx.path_graph(m)
    source = 0
    result = verify_gateway_dwell_threshold(core, source=source, d=1, tau=tau)
    assert result.rho == path_d1_formula(m, tau)
    assert result.lower_verified
    assert result.upper_verified


@pytest.mark.parametrize(
    "m,tau",
    [
        (5, 0),
        (6, 1),
        (8, 2),
        (9, 1),
        (12, 2),
    ],
)
def test_cycle_d1_formula_and_threshold_sides(m, tau):
    core = nx.cycle_graph(m)
    result = verify_gateway_dwell_threshold(core, source=0, d=1, tau=tau)
    assert result.rho == cycle_d1_formula(m, tau)
    assert result.lower_verified
    assert result.upper_verified


@pytest.mark.parametrize(
    "m,tau",
    [
        (4, 0),
        (5, 1),
        (7, 2),
        (8, 1),
        (10, 2),
        (12, 2),
    ],
)
def test_cycle_d2_formula_and_threshold_sides(m, tau):
    core = nx.cycle_graph(m)
    result = verify_gateway_dwell_threshold(core, source=0, d=2, tau=tau)
    assert result.rho == cycle_d2_formula(m, tau)
    assert result.lower_verified
    assert result.upper_verified


@pytest.mark.parametrize(
    "rows,cols,expected",
    [
        (2, 2, 2),
        (2, 3, 2),
        (3, 3, 3),
        (4, 4, 4),
    ],
)
def test_small_grid_frozen_predictions(rows, cols, expected):
    core = contiguous_grid(rows, cols)
    result = verify_gateway_dwell_threshold(core, source=0, d=1, tau=1)
    assert result.rho == expected
    assert result.lower_verified
    assert result.upper_verified


def test_d_edge_connected_core_makes_every_d_subset_admissible():
    for core, d in [
        (nx.cycle_graph(7), 2),
        (nx.complete_graph(6), 3),
        (nx.complete_bipartite_graph(3, 3), 3),
    ]:
        family = admissible_gateway_sets(core, source=0, d=d)
        assert len(family) == math.comb(core.number_of_nodes(), d)


def test_slack_distance_domination_equivalence_on_two_connected_core():
    core = nx.cycle_graph(9)
    d, tau = 2, 1
    rho, witness, family = distance_transversal_number(core, source=0, d=d, tau=tau)

    distances = dict(nx.all_pairs_shortest_path_length(core))
    uncovered = [
        v for v in core.nodes()
        if min(distances[p][v] for p in witness) > tau
    ]
    assert len(uncovered) <= d - 1
    assert len(family) == math.comb(9, 2)
    assert rho == math.ceil((9 - 1) / 3)


def test_nonempty_admissible_family_is_required():
    # On a path endpoint, even if the source itself is a gateway, its
    # augmented degree is at most two. Therefore lambda(s,t)>=3 is impossible.
    core = nx.path_graph(5)
    with pytest.raises(ValueError, match="admissible gateway family"):
        distance_transversal_number(core, source=0, d=3, tau=1)
