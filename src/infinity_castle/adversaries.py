from __future__ import annotations

from abc import ABC, abstractmethod
from collections import Counter
from typing import List, Tuple

import networkx as nx
import numpy as np

from .model import Edge, Node, canon_edge


class Adversary(ABC):
    name = "adversary"

    def reset(self, graph: nx.Graph, source: Node, target: Node) -> None:
        self.source = source
        self.target = target

    @abstractmethod
    def rewire(
        self,
        graph: nx.Graph,
        positions: List[Node],
        traffic: Counter,
        budget: int,
        rng: np.random.Generator,
    ) -> List[Tuple[Edge, Edge]]:
        raise NotImplementedError


def _candidate_nonedges(graph: nx.Graph):
    return [canon_edge(u, v) for u, v in nx.non_edges(graph)]


def _bridges(graph: nx.Graph):
    return {canon_edge(u, v) for u, v in nx.bridges(graph)}


def _safe_remove(graph: nx.Graph, edge: Edge, preserve_connectivity: bool = True) -> bool:
    if not graph.has_edge(*edge):
        return False
    if not preserve_connectivity:
        return True
    return edge not in _bridges(graph)


def _distance_score(graph: nx.Graph, positions: List[Node], target: Node) -> float:
    try:
        dist = nx.single_source_shortest_path_length(graph, target)
    except nx.NetworkXError:
        return float("-inf")
    vals = [dist.get(p, 10**6) for p in positions if p != target]
    return float(sum(vals) / len(vals)) if vals else 0.0


def _best_nonhelping_addition(
    graph_after_removal: nx.Graph,
    positions: List[Node],
    target: Node,
    rng: np.random.Generator,
    sample_cap: int = 40,
):
    candidates = _candidate_nonedges(graph_after_removal)
    if not candidates:
        return None
    if len(candidates) > sample_cap:
        idx = rng.choice(len(candidates), size=sample_cap, replace=False)
        candidates = [candidates[int(i)] for i in idx]
    scored = []
    for add in candidates:
        graph_after_removal.add_edge(*add)
        score = _distance_score(graph_after_removal, positions, target)
        graph_after_removal.remove_edge(*add)
        scored.append((score, float(rng.random()), add))
    scored.sort(reverse=True)
    return scored[0][2]


def _strategic_rewire(graph, remove: Edge, positions, target, rng):
    if not _safe_remove(graph, remove):
        return None
    graph.remove_edge(*remove)
    if not nx.is_connected(graph):
        graph.add_edge(*remove)
        return None
    add = _best_nonhelping_addition(graph, positions, target, rng)
    if add is None:
        graph.add_edge(*remove)
        return None
    graph.add_edge(*add)
    return remove, add


class NoAdversary(Adversary):
    name = "none"

    def rewire(self, graph, positions, traffic, budget, rng):
        return []


class ObliviousChurnAdversary(Adversary):
    name = "oblivious"

    def rewire(self, graph, positions, traffic, budget, rng):
        changes = []
        for _ in range(budget):
            edges = list(graph.edges())
            rng.shuffle(edges)
            nonedges = _candidate_nonedges(graph)
            rng.shuffle(nonedges)
            done = False
            bridges = _bridges(graph)
            for u, v in edges:
                rem = canon_edge(u, v)
                if rem in bridges:
                    continue
                graph.remove_edge(*rem)
                if not nx.is_connected(graph):
                    graph.add_edge(*rem)
                    continue
                valid = [e for e in nonedges if not graph.has_edge(*e)]
                if valid:
                    add = valid[int(rng.integers(len(valid)))]
                    graph.add_edge(*add)
                    changes.append((rem, add))
                    done = True
                else:
                    graph.add_edge(*rem)
                if done:
                    break
            if not done:
                break
        return changes


class TrafficAwareAdversary(Adversary):
    name = "traffic_aware"

    def rewire(self, graph, positions, traffic, budget, rng):
        changes = []
        for _ in range(budget):
            bridges = _bridges(graph)
            ranked = sorted(
                (canon_edge(u, v) for u, v in graph.edges() if canon_edge(u, v) not in bridges),
                key=lambda e: (traffic.get(e, 0), int(e[0] in positions or e[1] in positions)),
                reverse=True,
            )
            done = False
            for rem in ranked:
                change = _strategic_rewire(graph, rem, positions, self.target, rng)
                if change:
                    changes.append(change)
                    done = True
                    break
            if not done:
                break
        return changes


class ReactiveCutAdversary(Adversary):
    name = "reactive_cut"

    def rewire(self, graph, positions, traffic, budget, rng):
        changes = []
        for _ in range(budget):
            bridges = _bridges(graph)
            score = Counter()
            for p in positions:
                if p == self.target:
                    continue
                try:
                    paths = nx.all_shortest_paths(graph, p, self.target)
                    for j, path in enumerate(paths):
                        if j >= 12:
                            break
                        for u, v in zip(path, path[1:]):
                            score[canon_edge(u, v)] += 1
                except nx.NetworkXNoPath:
                    pass
            for e, q in traffic.items():
                score[e] += q

            ranked = sorted(
                (canon_edge(u, v) for u, v in graph.edges() if canon_edge(u, v) not in bridges),
                key=lambda e: (score[e], int(e[0] in positions or e[1] in positions)),
                reverse=True,
            )
            done = False
            for rem in ranked:
                if score[rem] <= 0:
                    break
                change = _strategic_rewire(graph, rem, positions, self.target, rng)
                if change:
                    changes.append(change)
                    done = True
                    break
            if not done:
                break
        return changes
