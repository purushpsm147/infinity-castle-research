from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import ceil
from typing import Iterable, Sequence

import networkx as nx


@dataclass(frozen=True)
class GatewayDwellCertificate:
    vertices: int
    d: int
    tau: int
    rho: int
    witness: tuple[int, ...]
    admissible_gateway_sets: int
    lower_sets_checked: int
    lower_verified: bool
    upper_verified: bool


def _require_contiguous_int_nodes(graph: nx.Graph) -> tuple[int, ...]:
    nodes = tuple(sorted(int(v) for v in graph.nodes()))
    if nodes != tuple(range(len(nodes))):
        raise ValueError("gateway-dwell helpers require nodes 0..m-1")
    return nodes


def augment_with_target(
    core: nx.Graph,
    gateways: Iterable[int],
) -> tuple[nx.Graph, int]:
    nodes = _require_contiguous_int_nodes(core)
    target = len(nodes)
    g = core.copy()
    g.add_node(target)
    for v in gateways:
        g.add_edge(int(v), target)
    return g, target


def admissible_gateway_sets(
    core: nx.Graph,
    source: int,
    d: int,
) -> tuple[tuple[int, ...], ...]:
    """All d-gateway sets whose augmented graph satisfies lambda(s,t)>=d."""
    nodes = _require_contiguous_int_nodes(core)
    if source not in nodes:
        raise ValueError("source must lie in the core")
    if d < 1 or d > len(nodes):
        raise ValueError("require 1<=d<=|V(F)|")

    out = []
    for gateways in combinations(nodes, d):
        augmented, target = augment_with_target(core, gateways)
        if nx.edge_connectivity(augmented, source, target) >= d:
            out.append(tuple(gateways))
    return tuple(out)


def set_distance(
    core: nx.Graph,
    positions: Sequence[int],
    gateways: Sequence[int],
) -> int:
    """Minimum graph distance between two nonempty vertex sets."""
    if not positions or not gateways:
        return 10**18
    dist = dict(nx.all_pairs_shortest_path_length(core))
    return min(dist[p][g] for p in positions for g in gateways)


def distance_transversal_number(
    core: nx.Graph,
    source: int,
    d: int,
    tau: int,
) -> tuple[int, tuple[int, ...], tuple[tuple[int, ...], ...]]:
    """Minimum |P| meeting every admissible gateway set within distance tau.

    This is the game value predicted by the Synchronous Gateway-Dwell Theorem.
    The returned object is a standard finite set-cover/transversal quantity,
    not a newly named graph invariant.
    """
    nodes = _require_contiguous_int_nodes(core)
    if tau < 0:
        raise ValueError("tau must be nonnegative")
    family = admissible_gateway_sets(core, source, d)
    if not family:
        raise ValueError("admissible gateway family must be nonempty")

    for k in range(1, len(nodes) + 1):
        for positions in combinations(nodes, k):
            if all(set_distance(core, positions, gateways) <= tau for gateways in family):
                return k, tuple(positions), family
    raise AssertionError("finite nonempty core must admit a full-vertex transversal")


def verify_gateway_dwell_threshold(
    core: nx.Graph,
    source: int,
    d: int,
    tau: int,
) -> GatewayDwellCertificate:
    """Mechanically verify both threshold sides for the frozen theorem.

    Epoch semantics:
      * Nakime chooses one admissible d-gateway set at a fresh epoch.
      * that gateway set is fixed for exactly tau+1 agent moves;
      * the core graph itself is fixed;
      * agents observe the fresh epoch and may wait/co-locate;
      * reaching t ends the game;
      * relocating all d gateways is allowed atomically, so b>=d is assumed.

    Lower side:
      every set of rho-1 distinct occupied vertices has an admissible gateway
      set at distance >tau. Co-location cannot improve this support, so this
      covers all configurations of <=rho-1 agents.

    Upper side:
      the returned rho-vertex witness is within distance <=tau of every
      admissible gateway set, hence some agent reaches a gateway in <=tau
      moves and crosses to t on the next move, within the tau+1 dwell.
    """
    nodes = _require_contiguous_int_nodes(core)
    rho, witness, family = distance_transversal_number(core, source, d, tau)

    lower_checked = 0
    lower_ok = True
    k_low = rho - 1

    if k_low == 0:
        lower_checked = 1
        lower_ok = True
    else:
        for positions in combinations(nodes, k_low):
            lower_checked += 1
            if not any(
                set_distance(core, positions, gateways) > tau
                for gateways in family
            ):
                lower_ok = False
                break

    upper_ok = all(
        set_distance(core, witness, gateways) <= tau
        for gateways in family
    )

    return GatewayDwellCertificate(
        vertices=len(nodes),
        d=d,
        tau=tau,
        rho=rho,
        witness=witness,
        admissible_gateway_sets=len(family),
        lower_sets_checked=lower_checked,
        lower_verified=lower_ok,
        upper_verified=upper_ok,
    )


def contiguous_grid(rows: int, cols: int) -> nx.Graph:
    if rows < 1 or cols < 1:
        raise ValueError("positive grid dimensions required")
    g = nx.grid_2d_graph(rows, cols)
    mapping = {v: i for i, v in enumerate(sorted(g.nodes()))}
    return nx.relabel_nodes(g, mapping)


def path_d1_formula(m: int, tau: int) -> int:
    return ceil(m / (2 * tau + 1))


def cycle_d1_formula(m: int, tau: int) -> int:
    return ceil(m / (2 * tau + 1))


def cycle_d2_formula(m: int, tau: int) -> int:
    return ceil((m - 1) / (2 * tau + 1))
