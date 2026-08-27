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


def moving_gateway_castle(n: int, d: int) -> tuple[nx.Graph, int, int]:
    """Clique-core moving-gateway family G_{n,d}.

    Vertices 0..n-2 form a clique. Target t=n-1 is adjacent to exactly the
    first d core vertices. Source s=d is therefore a non-neighbor of t.

    Preconditions: n>=3 and 1<=d<=n-2.
    """
    if n < 3 or not (1 <= d <= n - 2):
        raise ValueError("require n>=3 and 1<=d<=n-2")
    core = tuple(range(n - 1))
    target = n - 1
    source = d
    g = nx.complete_graph(core)
    g.add_node(target)
    for v in range(d):
        g.add_edge(v, target)
    return g, source, target


@dataclass(frozen=True)
class GatewayCertificateResult:
    n: int
    d: int
    budget: int
    agents: int
    lower_invariant_verified: bool
    upper_force_verified: bool
    lower_cases_checked: int
    lower_moves_checked: int
    upper_rewires_checked: int


def _position_multisets(vertices: tuple[int, ...], agents: int):
    """All sorted multisets of agent positions on the supplied vertices."""
    from itertools import combinations_with_replacement
    return combinations_with_replacement(vertices, agents)


def verify_moving_gateway_threshold(
    n: int,
    d: int,
    *,
    budget: Optional[int] = None,
) -> GatewayCertificateResult:
    """Mechanically verify the two theorem certificates for G_{n,d}.

    Candidate theorem (O3p timing, b>=d):
        K* = n-d.

    Lower certificate:
      For k=n-d-1, enumerate every d-gateway set S and every sorted k-agent
      position multiset P disjoint from S. Enumerate every legal joint move
      that does not already reach t. After the move, at least d core vertices
      are unoccupied, so the adversary can choose d of them as the next target
      neighborhood. Replacing S\\U by U\\S uses at most d<=b one-for-one swaps
      and restores the invariant.

    Upper certificate:
      For k=n-d, place agents on n-d distinct core vertices after round 1.
      Enumerate every legal adversary rewire from the initial graph. Since every
      successor has lambda(s,t)>=d, deg(t)>=d; only d-1 core vertices are
      unoccupied, so at least one target neighbor is occupied and wins next
      round before another edit.

    The lower certificate is an inductive invariant and therefore proves
    indefinite avoidance, not merely failure up to a chosen finite horizon.
    """
    if budget is None:
        budget = d
    if budget < d:
        raise ValueError("candidate theorem requires budget>=d")
    g0, source, target = moving_gateway_castle(n, d)
    core = tuple(range(n - 1))

    # ---- lower side: k=n-d-1 loses forever under the relocation invariant.
    k_low = n - d - 1
    lower_cases = 0
    lower_moves = 0
    lower_ok = True

    for gateways in combinations(core, d):
        gateway_set = set(gateways)
        base = nx.complete_graph(core)
        base.add_node(target)
        for v in gateways:
            base.add_edge(v, target)

        allowed_start_vertices = tuple(v for v in core if v not in gateway_set)
        for positions in _position_multisets(allowed_start_vertices, k_low):
            lower_cases += 1
            # Invariant: no crow begins adjacent to t.
            if gateway_set.intersection(positions):
                lower_ok = False
                break

            # Enumerate every controller move in this invariant state.
            choices = []
            for p in positions:
                choices.append(tuple(sorted({p, *base.neighbors(p)})))
            for moved_raw in product(*choices):
                moved = tuple(sorted(map(int, moved_raw)))
                lower_moves += 1

                # Under the invariant no agent can reach t in one move: only
                # gateway vertices are adjacent to t, and none was occupied
                # at the start of the round.
                if target in moved:
                    lower_ok = False
                    break

                occupied = set(moved)
                free_core = [v for v in core if v not in occupied]
                if len(free_core) < d:
                    lower_ok = False
                    break

                next_gateways = set(free_core[:d])
                removals = gateway_set - next_gateways
                additions = next_gateways - gateway_set
                swaps = len(removals)
                if swaps != len(additions) or swaps > d or swaps > budget:
                    lower_ok = False
                    break

                # Construct the adversary's certificate successor explicitly.
                nxt = base.copy()
                for v in removals:
                    nxt.remove_edge(v, target)
                for v in additions:
                    if nxt.has_edge(v, target):
                        lower_ok = False
                        break
                    nxt.add_edge(v, target)
                if not lower_ok:
                    break
                if len(nxt.edges()) != len(base.edges()):
                    lower_ok = False
                    break
                if not nx.is_connected(nxt):
                    lower_ok = False
                    break
                if nx.edge_connectivity(nxt, source, target) != d:
                    lower_ok = False
                    break
                if next_gateways.intersection(occupied):
                    lower_ok = False
                    break
            if not lower_ok:
                break
        if not lower_ok:
            break

    # ---- upper side: k=n-d wins by round 2 against every legal first rewire.
    k_high = n - d
    upper_ok = True
    occupied = set(core[:k_high])
    # Ensure the source can be one of the occupied vertices (waiting) and all
    # others are reachable in one move because the core is a clique.
    if source not in occupied:
        occupied.remove(max(occupied))
        occupied.add(source)
    if len(occupied) != k_high:
        upper_ok = False

    game = ExactRewireGame(g0, source, target, budget=budget, lambda_min=d)
    upper_rewires = 0
    if upper_ok:
        for edges in game.rewire_successors(game.initial_edges):
            upper_rewires += 1
            gg = game._graph(edges)
            nbrs = set(gg.neighbors(target))
            if len(nbrs) < d:
                upper_ok = False
                break
            if not (nbrs & occupied):
                upper_ok = False
                break

    return GatewayCertificateResult(
        n=n,
        d=d,
        budget=budget,
        agents=n-d,
        lower_invariant_verified=lower_ok,
        upper_force_verified=upper_ok,
        lower_cases_checked=lower_cases,
        lower_moves_checked=lower_moves,
        upper_rewires_checked=upper_rewires,
    )


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
