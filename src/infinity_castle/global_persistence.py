from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
from typing import Tuple

import networkx as nx

from .exact_game import ExactRewireGame, Edge, EdgeKey, canon_edge, edge_key

LockKey = Tuple[Tuple[Edge, int], ...]
Positions = Tuple[int, ...]


def _lock_dict(locks: LockKey) -> dict[Edge, int]:
    return dict(locks)


def _lock_key(locks: dict[Edge, int]) -> LockKey:
    return tuple(sorted((edge, int(age)) for edge, age in locks.items() if age > 0))


@dataclass(frozen=True)
class PersistentSolveResult:
    agents: int
    horizon: int
    winnable: bool
    states_evaluated: int


class PersistentRewireGame:
    """Finite O3p reachability game with globally rewritable persistent edges.

    The base timing is the same as ExactRewireGame: agents move first, target
    arrival succeeds immediately, and the adaptive adversary rewires afterward.

    A newly inserted edge receives lock value tau in the successor state.
    At a later post-move edit an edge may be deleted only when its current lock
    value is zero. Retained locks age by one after each adversary phase.

    Hence tau=0 is exactly the ordinary O3p replacement semantics: an inserted
    edge exists for the next agent move and may be deleted after that move.
    """

    def __init__(
        self,
        graph: nx.Graph,
        source: int,
        target: int,
        *,
        budget: int,
        lambda_min: int,
        tau: int,
    ):
        self.nodes = tuple(sorted(int(v) for v in graph.nodes()))
        if self.nodes != tuple(range(len(self.nodes))):
            raise ValueError("persistent solver currently requires nodes 0..n-1")
        self.source = int(source)
        self.target = int(target)
        self.budget = int(budget)
        self.lambda_min = int(lambda_min)
        self.tau = int(tau)
        if self.budget < 0:
            raise ValueError("budget must be nonnegative")
        if self.lambda_min < 1:
            raise ValueError("lambda_min must be positive")
        if self.tau < 0:
            raise ValueError("tau must be nonnegative")

        self.initial_edges = edge_key(graph)
        self.edge_count = len(self.initial_edges)
        self.all_edges = tuple(combinations(self.nodes, 2))
        if not self._valid_graph(self.initial_edges):
            raise ValueError("initial graph violates connectivity/lambda_min constraints")

    @lru_cache(maxsize=None)
    def _graph(self, edges: EdgeKey) -> nx.Graph:
        g = nx.Graph()
        g.add_nodes_from(self.nodes)
        g.add_edges_from(edges)
        return g

    @lru_cache(maxsize=None)
    def _valid_graph(self, edges: EdgeKey) -> bool:
        if len(edges) != self.edge_count:
            return False
        g = self._graph(edges)
        return nx.is_connected(g) and nx.edge_connectivity(
            g, self.source, self.target
        ) >= self.lambda_min

    @lru_cache(maxsize=None)
    def rewire_successors(
        self,
        edges: EdgeKey,
        locks: LockKey = (),
    ) -> tuple[tuple[EdgeKey, LockKey], ...]:
        """All legal persistent successors after one post-move adversary phase.

        Additions are selected from nonedges of the pre-edit graph, matching the
        repository's one-for-one replacement semantics. Only mature edges
        (lock=0) may be removed. Up to budget simultaneous replacements are
        allowed, including the zero-edit action.
        """
        cur = set(edges)
        lock_map = _lock_dict(locks)
        mature = tuple(e for e in edges if lock_map.get(e, 0) == 0)
        nonedges = tuple(e for e in self.all_edges if e not in cur)

        aged = {e: max(lock_map.get(e, 0) - 1, 0) for e in edges}
        out: set[tuple[EdgeKey, LockKey]] = {(edges, _lock_key(aged))}

        max_j = min(self.budget, len(mature), len(nonedges))
        for j in range(1, max_j + 1):
            for removed in combinations(mature, j):
                base = cur.difference(removed)
                for added in combinations(nonedges, j):
                    nxt = tuple(sorted(base.union(added)))
                    if not self._valid_graph(nxt):
                        continue
                    nxt_locks = {
                        e: max(lock_map.get(e, 0) - 1, 0)
                        for e in base
                    }
                    for e in added:
                        nxt_locks[e] = self.tau
                    out.add((nxt, _lock_key(nxt_locks)))
        return tuple(sorted(out))

    @lru_cache(maxsize=None)
    def move_outcomes(
        self,
        edges: EdgeKey,
        positions: Positions,
    ) -> tuple[Positions, ...]:
        g = self._graph(edges)
        choices = []
        for p in positions:
            choices.append(tuple(sorted({p, *g.neighbors(p)})))
        return tuple(sorted({
            tuple(sorted(map(int, xs)))
            for xs in product(*choices)
        }))

    def solve(self, agents: int, horizon: int) -> PersistentSolveResult:
        if agents < 1 or horizon < 0:
            raise ValueError("agents >= 1 and horizon >= 0 required")

        @lru_cache(maxsize=None)
        def win(
            edges: EdgeKey,
            locks: LockKey,
            positions: Positions,
            remaining: int,
        ) -> bool:
            if self.target in positions:
                return True
            if remaining == 0:
                return False

            for moved in self.move_outcomes(edges, positions):
                if self.target in moved:
                    return True
                if all(
                    win(nxt_edges, nxt_locks, moved, remaining - 1)
                    for nxt_edges, nxt_locks in self.rewire_successors(edges, locks)
                ):
                    return True
            return False

        start = tuple([self.source] * agents)
        winnable = win(self.initial_edges, (), start, horizon)
        return PersistentSolveResult(
            agents=agents,
            horizon=horizon,
            winnable=winnable,
            states_evaluated=win.cache_info().currsize,
        )


def c0_matches_base_successors(
    graph: nx.Graph,
    source: int,
    target: int,
    *,
    budget: int,
    lambda_min: int,
) -> bool:
    """Check the semantic boundary C_0 = the base O3p replacement model."""
    base = ExactRewireGame(
        graph,
        source,
        target,
        budget=budget,
        lambda_min=lambda_min,
    )
    persistent = PersistentRewireGame(
        graph,
        source,
        target,
        budget=budget,
        lambda_min=lambda_min,
        tau=0,
    )
    c0_edges = {
        edges
        for edges, locks in persistent.rewire_successors(
            persistent.initial_edges, ()
        )
        if not locks
    }
    return c0_edges == set(base.rewire_successors(base.initial_edges))


@dataclass(frozen=True)
class GlobalPersistenceCertificate:
    n: int
    tau: int
    first_successors_checked: int
    relocated_gateway_cases: int
    second_successors_checked: int
    certificate_verified: bool


def verify_global_persistence_clique_foothold(
    n: int,
    tau: int,
) -> GlobalPersistenceCertificate:
    """Verify the b=d=1 positive-persistence clique certificate.

    Proposition:
        For G_{n,1}, b=d=1 and tau>=1, one persistent agent forces
        target reach within three moves.

    The verifier exhaustively enumerates every legal first successor and every
    legal second successor in each gateway-relocation branch.
    """
    if n < 3:
        raise ValueError("require n>=3")
    if tau < 1:
        raise ValueError("positive-persistence proposition requires tau>=1")

    core = tuple(range(n - 1))
    target = n - 1
    initial_gateway = 0
    source = 1

    g = nx.complete_graph(core)
    g.add_node(target)
    g.add_edge(initial_gateway, target)

    game = PersistentRewireGame(
        g,
        source,
        target,
        budget=1,
        lambda_min=1,
        tau=tau,
    )

    if not g.has_edge(source, initial_gateway):
        raise AssertionError("clique strategy requires source->gateway move")

    first_successors = game.rewire_successors(game.initial_edges, ())
    relocated = 0
    second_checked = 0

    for edges, locks in first_successors:
        gg = game._graph(edges)

        # If the old gateway survives, the agent at g crosses on round 2.
        if gg.has_edge(initial_gateway, target):
            continue

        relocated += 1
        target_neighbors = tuple(sorted(gg.neighbors(target)))
        if not target_neighbors:
            return GlobalPersistenceCertificate(
                n, tau, len(first_successors), relocated, second_checked, False
            )

        # In this branch the deleted edge was g-t, so the clique core is intact.
        for new_gateway in target_neighbors:
            if not gg.has_edge(initial_gateway, new_gateway):
                return GlobalPersistenceCertificate(
                    n, tau, len(first_successors), relocated, second_checked, False
                )
            new_target_edge = canon_edge(new_gateway, target)
            if _lock_dict(locks).get(new_target_edge, 0) < 1:
                return GlobalPersistenceCertificate(
                    n, tau, len(first_successors), relocated, second_checked, False
                )

            # After g->u, every legal next adversary action must retain u-t.
            for nxt_edges, _ in game.rewire_successors(edges, locks):
                second_checked += 1
                if new_target_edge not in set(nxt_edges):
                    return GlobalPersistenceCertificate(
                        n, tau, len(first_successors), relocated, second_checked, False
                    )

    return GlobalPersistenceCertificate(
        n=n,
        tau=tau,
        first_successors_checked=len(first_successors),
        relocated_gateway_cases=relocated,
        second_successors_checked=second_checked,
        certificate_verified=True,
    )
