from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
import math
from typing import Dict, List

import networkx as nx
import numpy as np

from .model import Edge, Node, canon_edge


class Policy(ABC):
    name = "policy"

    def reset(self, graph: nx.Graph, source: Node, target: Node, agents: int) -> None:
        pass

    @abstractmethod
    def choose_moves(self, graph: nx.Graph, positions: List[Node], target: Node, rng: np.random.Generator) -> List[Node]:
        raise NotImplementedError

    def observe_transition(self, graph_before: nx.Graph, positions_before: List[Node], positions_after: List[Node], target: Node) -> None:
        pass


class RandomWalkPolicy(Policy):
    name = "random"

    def choose_moves(self, graph, positions, target, rng):
        out = []
        for p in positions:
            nbrs = list(graph.neighbors(p))
            out.append(nbrs[int(rng.integers(len(nbrs)))] if nbrs else p)
        return out


class ReplanShortestPathPolicy(Policy):
    name = "replan"

    def choose_moves(self, graph, positions, target, rng):
        out = []
        for p in positions:
            if p == target:
                out.append(p)
                continue
            try:
                path = nx.shortest_path(graph, p, target)
                out.append(path[1] if len(path) > 1 else p)
            except nx.NetworkXNoPath:
                nbrs = list(graph.neighbors(p))
                out.append(nbrs[int(rng.integers(len(nbrs)))] if nbrs else p)
        return out


class DisjointPathPolicy(Policy):
    name = "disjoint"

    def choose_moves(self, graph, positions, target, rng):
        grouped: Dict[Node, List[int]] = defaultdict(list)
        for i, p in enumerate(positions):
            grouped[p].append(i)
        result = list(positions)
        for p, idxs in grouped.items():
            if p == target:
                continue
            candidates = []
            try:
                gen = nx.shortest_simple_paths(graph, p, target)
                for _ in range(max(8, len(idxs) * 3)):
                    path = next(gen)
                    if len(path) > 1:
                        candidates.append(path[1])
            except (nx.NetworkXNoPath, StopIteration):
                candidates = list(graph.neighbors(p))
            uniq = []
            for n in candidates:
                if n not in uniq:
                    uniq.append(n)
            if not uniq:
                uniq = [p]
            for j, agent_idx in enumerate(idxs):
                result[agent_idx] = uniq[j % len(uniq)]
        return result


class GenericReinforcementPolicy(Policy):
    name = "reinforcement"

    def __init__(self, decay: float = 0.92, reward: float = 1.0, temperature: float = 0.6):
        self.decay = decay
        self.reward = reward
        self.temperature = temperature
        self.score: Dict[Edge, float] = {}

    def reset(self, graph, source, target, agents):
        self.score = {canon_edge(u, v): 1.0 for u, v in graph.edges()}

    def _sync(self, graph):
        active = {canon_edge(u, v) for u, v in graph.edges()}
        self.score = {e: self.score.get(e, 1.0) for e in active}

    def choose_moves(self, graph, positions, target, rng):
        self._sync(graph)
        dist = nx.single_source_shortest_path_length(graph, target)
        out = []
        for p in positions:
            if p == target:
                out.append(p)
                continue
            nbrs = list(graph.neighbors(p))
            if not nbrs:
                out.append(p)
                continue
            logits = []
            for n in nbrs:
                e = canon_edge(p, n)
                progress = dist.get(p, 10**6) - dist.get(n, 10**6)
                logits.append(math.log(max(self.score.get(e, 1e-6), 1e-6)) + progress / self.temperature)
            logits = np.array(logits, dtype=float)
            logits -= logits.max()
            probs = np.exp(logits)
            probs /= probs.sum()
            out.append(nbrs[int(rng.choice(len(nbrs), p=probs))])
        return out

    def observe_transition(self, graph_before, positions_before, positions_after, target):
        self._sync(graph_before)
        for e in list(self.score):
            self.score[e] *= self.decay
        dist = nx.single_source_shortest_path_length(graph_before, target)
        for a, b in zip(positions_before, positions_after):
            if a == b:
                continue
            improvement = max(0, dist.get(a, 10**6) - dist.get(b, 10**6))
            edge = canon_edge(a, b)
            self.score[edge] = self.score.get(edge, 1.0) + self.reward * (1 + improvement)


class PhysarumPolicy(Policy):
    """Tero-style conductance adaptation driven by electrical flow.

    This is a deliberately small research baseline, not a claim of exact biological fidelity.
    Agent positions inject equal mass; target removes the same total mass.
    Conductance follows D <- D + dt * (|Q| - D).
    """

    name = "physarum"

    def __init__(self, dt: float = 0.35, floor: float = 1e-4, temperature: float = 0.35):
        self.dt = dt
        self.floor = floor
        self.temperature = temperature
        self.D: Dict[Edge, float] = {}
        self.last_flux: Dict[Edge, float] = {}

    def reset(self, graph, source, target, agents):
        self.D = {canon_edge(u, v): 1.0 for u, v in graph.edges()}
        self.last_flux = {}

    def _sync(self, graph):
        active = {canon_edge(u, v) for u, v in graph.edges()}
        self.D = {e: self.D.get(e, 1.0) for e in active}

    def _flow(self, graph: nx.Graph, positions: List[Node], target: Node):
        self._sync(graph)
        nodes = list(graph.nodes())
        if target not in nodes:
            return {}, {n: 0.0 for n in nodes}
        non_target = [n for n in nodes if n != target]
        idx = {n: i for i, n in enumerate(non_target)}
        L = np.zeros((len(non_target), len(non_target)), dtype=float)
        rhs = np.zeros(len(non_target), dtype=float)
        live_positions = [p for p in positions if p != target]
        if not live_positions:
            return {}, {n: 0.0 for n in nodes}
        injection = 1.0 / len(live_positions)
        for p in live_positions:
            if p in idx:
                rhs[idx[p]] += injection
        for u, v in graph.edges():
            c = max(self.D.get(canon_edge(u, v), 1.0), self.floor)
            if u != target:
                L[idx[u], idx[u]] += c
            if v != target:
                L[idx[v], idx[v]] += c
            if u != target and v != target:
                L[idx[u], idx[v]] -= c
                L[idx[v], idx[u]] -= c
        try:
            pvec = np.linalg.solve(L, rhs)
        except np.linalg.LinAlgError:
            pvec = np.linalg.lstsq(L, rhs, rcond=None)[0]
        pot = {target: 0.0}
        pot.update({n: float(pvec[idx[n]]) for n in non_target})
        flux: Dict[Edge, float] = {}
        for u, v in graph.edges():
            e = canon_edge(u, v)
            flux[e] = self.D[e] * (pot[u] - pot[v])
        return flux, pot

    def choose_moves(self, graph, positions, target, rng):
        flux, pot = self._flow(graph, positions, target)
        self.last_flux = flux
        out = []
        for p in positions:
            if p == target:
                out.append(p)
                continue
            nbrs = list(graph.neighbors(p))
            if not nbrs:
                out.append(p)
                continue
            desirability = []
            for n in nbrs:
                e = canon_edge(p, n)
                downstream = max(0.0, pot.get(p, 0.0) - pot.get(n, 0.0))
                q = abs(flux.get(e, 0.0))
                desirability.append(max(self.floor, q + downstream * self.D.get(e, 1.0)))
            arr = np.asarray(desirability, dtype=float)
            arr = np.power(arr, 1.0 / max(self.temperature, 1e-6))
            if (not np.isfinite(arr).all()) or arr.sum() <= 0:
                probs = np.ones(len(nbrs)) / len(nbrs)
            else:
                probs = arr / arr.sum()
            out.append(nbrs[int(rng.choice(len(nbrs), p=probs))])
        return out

    def observe_transition(self, graph_before, positions_before, positions_after, target):
        self._sync(graph_before)
        for e in list(self.D):
            q = abs(self.last_flux.get(e, 0.0))
            self.D[e] = max(self.floor, self.D[e] + self.dt * (q - self.D[e]))
