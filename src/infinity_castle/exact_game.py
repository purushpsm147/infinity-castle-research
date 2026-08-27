from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, product
from typing import Iterable, Optional, Tuple

import networkx as nx

Edge = Tuple[int, int]
EdgeKey = Tuple[Edge, ...]
Positions = Tuple[int, ...]


def canon_edge(u: int, v: int) -> Edge:
    return (u, v) if u < v else (v, u)


def edge_key(graph: nx.Graph) -> EdgeKey:
    return tuple(sorted(canon_edge(int(u), int(v)) for u, v in graph.edges()))


def k23_castle() -> tuple[nx.Graph, int, int]:
    """Five-node castle with three independent length-2 s-t routes.

    Partitions are {s,t} and {1,2,3}; lambda(s,t)=3 and |E|=6.
    """
    g = nx.Graph()
    g.add_nodes_from(range(5))
    s, t = 0, 4
    for mid in (1, 2, 3):
        g.add_edge(s, mid)
        g.add_edge(mid, t)
    return g, s, t


@dataclass(frozen=True)
class ExactSolveResult:
    agents: int
    horizon: int
    winnable: bool
    states_evaluated: int
    graph_states_seen: int
    max_rewire_successors: int


class ExactRewireGame:
    """Finite perfect-information reachability game for O3p rewiring.

    Timing per round:
      1. the controller sees the current graph and all agent positions;
      2. it chooses all agent moves jointly;
      3. valid moves execute;
      4. reaching target ends the game immediately;
      5. the adversary sees realized positions and performs up to budget
         one-for-one edge rewires for the next round.

    Constraints:
      * fixed vertex set and target;
      * simple undirected graph;
      * edge count preserved;
      * every post-rewire graph is connected;
      * lambda_t(source,target) >= lambda_min.

    The solver enumerates all legal adversary rewires and asks whether a
    centralized controller has a policy that forces target reach within H.
    This is deliberately stronger than any particular routing heuristic.
    """

    def __init__(
        self,
        graph: nx.Graph,
        source: int,
        target: int,
        *,
        budget: int,
        lambda_min: int,
    ):
        self.nodes = tuple(sorted(int(v) for v in graph.nodes()))
        if self.nodes != tuple(range(len(self.nodes))):
            raise ValueError("exact solver currently requires nodes 0..n-1")
        self.n = len(self.nodes)
        self.source = int(source)
        self.target = int(target)
        self.budget = int(budget)
        self.lambda_min = int(lambda_min)
        self.initial_edges = edge_key(graph)
        self.edge_count = len(self.initial_edges)
        self.all_edges = tuple(combinations(self.nodes, 2))
        if self.budget < 0:
            raise ValueError("budget must be nonnegative")
        if self.lambda_min < 1:
            raise ValueError("lambda_min must be positive")
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
        if not nx.is_connected(g):
            return False
        return nx.edge_connectivity(g, self.source, self.target) >= self.lambda_min

    @lru_cache(maxsize=None)
    def rewire_successors(self, edges: EdgeKey) -> tuple[EdgeKey, ...]:
        """All graphs obtainable by up to b genuine one-for-one rewires.

        Additions are chosen from nonedges of the pre-edit graph. Re-adding a
        just-removed edge is omitted because the same net effect is already
        represented by using fewer edits (including zero edits).
        """
        cur = set(edges)
        nonedges = [e for e in self.all_edges if e not in cur]
        out = {edges}
        max_j = min(self.budget, len(cur), len(nonedges))
        for j in range(1, max_j + 1):
            for removed in combinations(tuple(cur), j):
                base = cur.difference(removed)
                for added in combinations(nonedges, j):
                    nxt = tuple(sorted(base.union(added)))
                    if self._valid_graph(nxt):
                        out.add(nxt)
        return tuple(sorted(out))

    @lru_cache(maxsize=None)
    def move_outcomes(self, edges: EdgeKey, positions: Positions) -> tuple[Positions, ...]:
        g = self._graph(edges)
        choices = []
        for p in positions:
            if p == self.target:
                choices.append((p,))
            else:
                choices.append(tuple(sorted({p, *g.neighbors(p)})))
        outcomes = {tuple(sorted(map(int, xs))) for xs in product(*choices)}

        dist = nx.single_source_shortest_path_length(g, self.target)
        return tuple(sorted(
            outcomes,
            key=lambda ps: (
                0 if self.target in ps else 1,
                min(dist.get(p, self.n + 1) for p in ps),
                sum(dist.get(p, self.n + 1) for p in ps),
                ps,
            ),
        ))

    def solve(self, agents: int, horizon: int) -> ExactSolveResult:
        if agents < 1 or horizon < 0:
            raise ValueError("agents >= 1 and horizon >= 0 required")

        graph_states = set()
        max_succ = 0

        @lru_cache(maxsize=None)
        def win(edges: EdgeKey, positions: Positions, remaining: int) -> bool:
            nonlocal max_succ
            graph_states.add(edges)
            if self.target in positions:
                return True
            if remaining == 0:
                return False

            adversary_graphs = self.rewire_successors(edges)
            max_succ = max(max_succ, len(adversary_graphs))

            for moved in self.move_outcomes(edges, positions):
                if self.target in moved:
                    return True
                forced = True
                for nxt_edges in adversary_graphs:
                    if not win(nxt_edges, moved, remaining - 1):
                        forced = False
                        break
                if forced:
                    return True
            return False

        start_positions = tuple([self.source] * agents)
        winnable = win(self.initial_edges, start_positions, horizon)
        return ExactSolveResult(
            agents=agents,
            horizon=horizon,
            winnable=winnable,
            states_evaluated=win.cache_info().currsize,
            graph_states_seen=len(graph_states),
            max_rewire_successors=max_succ,
        )

    def minimum_agents(self, *, horizon: int, k_max: int) -> tuple[Optional[int], list[ExactSolveResult]]:
        results = []
        for k in range(1, k_max + 1):
            r = self.solve(k, horizon)
            results.append(r)
            if r.winnable:
                return k, results
        return None, results


def worst_case_transient_cut_arrival(path_lengths: Iterable[int], budget: int) -> Optional[int]:
    """Exact worst-case arrival time for fixed edge-disjoint assigned paths.

    Each round the adversary may make at most budget current next-edges
    unavailable. Missing edges are relative to a fixed footprint and do not
    undo agent positions. All unblocked agents advance one edge.

    Returns None when the adversary can block every path forever.
    """
    lengths = tuple(int(x) for x in path_lengths)
    if not lengths or any(x < 1 for x in lengths):
        raise ValueError("positive path lengths required")
    q = len(lengths)
    if budget >= q:
        return None

    @lru_cache(maxsize=None)
    def worst(progress: tuple[int, ...]) -> int:
        if any(progress[i] >= lengths[i] for i in range(q)):
            return 0
        active = tuple(i for i in range(q) if progress[i] < lengths[i])
        worst_next = 0
        for r in range(0, min(budget, len(active)) + 1):
            for blocked in combinations(active, r):
                blocked_set = set(blocked)
                nxt = list(progress)
                for i in active:
                    if i not in blocked_set:
                        nxt[i] += 1
                worst_next = max(worst_next, 1 + worst(tuple(nxt)))
        return worst_next

    return worst(tuple([0] * q))
