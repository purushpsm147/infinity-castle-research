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

    def observe_rewire(self, graph_after: nx.Graph, rewires, positions: List[Node], target: Node) -> None:
        """Optional hook for policies with memory of adversarial topology changes."""
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


class EntropyRegularizedPolicy(Policy):
    """Soft shortest-path policy: dispersion without reinforcement or biology."""

    name = "entropy_replan"

    def __init__(self, temperature: float = 1.0):
        self.temperature = temperature

    def choose_moves(self, graph, positions, target, rng):
        dist = nx.single_source_shortest_path_length(graph, target)
        out = []
        tau = max(self.temperature, 1e-6)
        for p in positions:
            if p == target:
                out.append(p)
                continue
            nbrs = list(graph.neighbors(p))
            if not nbrs:
                out.append(p)
                continue
            costs = np.asarray([dist.get(n, 10**6) for n in nbrs], dtype=float)
            logits = -costs / tau
            logits -= logits.max()
            probs = np.exp(logits)
            probs /= probs.sum()
            out.append(nbrs[int(rng.choice(len(nbrs), p=probs))])
        return out


class ElectricalFlowPolicy(PhysarumPolicy):
    """Fixed-conductance electrical-flow control.

    Uses the same potential/flux routing geometry as PhysarumPolicy but never
    adapts conductances. This isolates the value of adaptive conductance dynamics.
    """

    name = "electrical"

    def observe_transition(self, graph_before, positions_before, positions_after, target):
        self._sync(graph_before)
        return None


class EdgeDisjointPathPolicy(Policy):
    """Allocate co-located agents across actually edge-disjoint s-t paths.

    Unlike the legacy DisjointPathPolicy, this baseline does not infer
    "disjointness" from distinct first hops of shortest-simple paths.
    If fewer edge-disjoint paths exist than agents, paths are reused.
    """

    name = "edge_disjoint"

    def choose_moves(self, graph, positions, target, rng):
        grouped: Dict[Node, List[int]] = defaultdict(list)
        for i, p in enumerate(positions):
            grouped[p].append(i)

        result = list(positions)
        for p, idxs in grouped.items():
            if p == target:
                continue
            try:
                paths = list(nx.edge_disjoint_paths(graph, p, target))
            except (nx.NetworkXNoPath, nx.NetworkXError):
                paths = []

            paths = [path for path in paths if len(path) > 1]
            if not paths:
                nbrs = list(graph.neighbors(p))
                if not nbrs:
                    continue
                for j, agent_idx in enumerate(idxs):
                    result[agent_idx] = nbrs[j % len(nbrs)]
                continue

            # Stable ordering makes the baseline deterministic for a fixed graph.
            paths.sort(key=lambda path: (len(path), tuple(map(repr, path))))
            for j, agent_idx in enumerate(idxs):
                result[agent_idx] = paths[j % len(paths)][1]
        return result



class PheromoneConsensusPolicy(Policy):
    """Shared-memory consensus with an optional contrarian minority.

    Memory channels:
    - progress: repeated traversals that reduce current graph distance to target;
    - failure: non-progress traversals and recently attacked edges;
    - volatility: rewiring activity around incident vertices;
    - evidence: decayed corroboration count used only to track memory strength.

    The target-distance term is deliberately the same current-graph information
    available to shortest-path baselines. Pheromones add temporal memory, not a
    hidden oracle.

    contrarian_mode:
    - "none": all crows follow the consensus branch;
    - "fixed": each crow is contrarian with fixed_epsilon;
    - "adaptive": epsilon is chosen from the one-junction reliability formula.
    """

    name = "pheromone_adaptive"

    def __init__(
        self,
        *,
        contrarian_mode: str = "adaptive",
        fixed_epsilon: float = 0.25,
        memory_enabled: bool = True,
        progress_decay: float = 0.88,
        failure_decay: float = 0.82,
        volatility_decay: float = 0.86,
        evidence_decay: float = 0.90,
        immediate_weight: float = 1.0,
        progress_weight: float = 0.75,
        failure_weight: float = 0.90,
        volatility_weight: float = 0.45,
        consensus_temperature: float = 1.0,
    ):
        self.contrarian_mode = contrarian_mode
        self.fixed_epsilon = float(fixed_epsilon)
        self.memory_enabled = bool(memory_enabled)
        self.progress_decay = float(progress_decay)
        self.failure_decay = float(failure_decay)
        self.volatility_decay = float(volatility_decay)
        self.evidence_decay = float(evidence_decay)
        self.immediate_weight = float(immediate_weight)
        self.progress_weight = float(progress_weight)
        self.failure_weight = float(failure_weight)
        self.volatility_weight = float(volatility_weight)
        self.consensus_temperature = float(consensus_temperature)
        self.progress: Dict[Edge, float] = {}
        self.failure: Dict[Edge, float] = {}
        self.evidence: Dict[Edge, float] = {}
        self.volatility: Dict[Node, float] = {}
        self.last_traversals: Dict[Edge, int] = {}

    def reset(self, graph, source, target, agents):
        self.progress = {}
        self.failure = {}
        self.evidence = {}
        self.volatility = {}
        self.last_traversals = {}

    @staticmethod
    def optimal_contrarian_fraction(p: float, n: int, d: int) -> float:
        """Maximize one-junction P(at least one crow takes the correct branch).

        Assumes consensus is correct with probability p; each contrarian chooses
        uniformly among the d-1 non-consensus branches.
        """
        if d <= 1 or n <= 1:
            return 0.0
        p = min(max(float(p), 1.0 / d), 1.0 - 1e-12)
        a = ((1.0 - p) / (p * (d - 1))) ** (1.0 / (n - 1))
        return float(a * (d - 1) / (d - 1 + a))

    def _decay(self):
        if not self.memory_enabled:
            return
        for store, rate in (
            (self.progress, self.progress_decay),
            (self.failure, self.failure_decay),
            (self.evidence, self.evidence_decay),
            (self.volatility, self.volatility_decay),
        ):
            for key in list(store):
                store[key] *= rate
                if store[key] < 1e-8:
                    del store[key]

    def _edge_score(self, graph, p, n, target, dist):
        immediate = float(dist.get(p, 10**6) - dist.get(n, 10**6))
        if not self.memory_enabled:
            return self.immediate_weight * immediate
        e = canon_edge(p, n)
        pos = math.log1p(self.progress.get(e, 0.0))
        neg = math.log1p(self.failure.get(e, 0.0))
        vol = 0.5 * (self.volatility.get(p, 0.0) + self.volatility.get(n, 0.0))
        return (
            self.immediate_weight * immediate
            + self.progress_weight * pos
            - self.failure_weight * neg
            - self.volatility_weight * math.log1p(vol)
        )

    def _consensus(self, graph, p, target):
        nbrs = list(graph.neighbors(p))
        if not nbrs:
            return [], None, 1.0
        dist = nx.single_source_shortest_path_length(graph, target)
        scores = np.asarray([self._edge_score(graph, p, n, target, dist) for n in nbrs], dtype=float)
        tau = max(self.consensus_temperature, 1e-8)
        logits = scores / tau
        logits -= logits.max()
        probs = np.exp(logits)
        probs /= probs.sum()
        best = int(np.argmax(probs))
        return nbrs, best, float(probs[best])

    def choose_moves(self, graph, positions, target, rng):
        grouped: Dict[Node, List[int]] = defaultdict(list)
        for i, p in enumerate(positions):
            grouped[p].append(i)

        out = list(positions)
        for p, idxs in grouped.items():
            if p == target:
                continue
            nbrs, best_idx, p_consensus = self._consensus(graph, p, target)
            if not nbrs:
                continue
            consensus = nbrs[best_idx]
            alternatives = [n for j, n in enumerate(nbrs) if j != best_idx]

            if self.contrarian_mode == "none" or not alternatives:
                epsilon = 0.0
            elif self.contrarian_mode == "fixed":
                epsilon = min(max(self.fixed_epsilon, 0.0), 1.0)
            elif self.contrarian_mode == "adaptive":
                epsilon = self.optimal_contrarian_fraction(p_consensus, len(idxs), len(nbrs))
            else:
                raise ValueError(f"unknown contrarian_mode: {self.contrarian_mode}")

            for agent_idx in idxs:
                if alternatives and rng.random() < epsilon:
                    out[agent_idx] = alternatives[int(rng.integers(len(alternatives)))]
                else:
                    out[agent_idx] = consensus
        return out

    def observe_transition(self, graph_before, positions_before, positions_after, target):
        self._decay()
        self.last_traversals = {}
        if not self.memory_enabled:
            return
        dist = nx.single_source_shortest_path_length(graph_before, target)
        for a, b in zip(positions_before, positions_after):
            if a == b:
                continue
            e = canon_edge(a, b)
            self.last_traversals[e] = self.last_traversals.get(e, 0) + 1
            delta = float(dist.get(a, 10**6) - dist.get(b, 10**6))
            self.evidence[e] = self.evidence.get(e, 0.0) + 1.0
            if delta > 0:
                self.progress[e] = self.progress.get(e, 0.0) + delta
            else:
                self.failure[e] = self.failure.get(e, 0.0) + 0.5 + max(0.0, -delta)

    def observe_rewire(self, graph_after, rewires, positions, target):
        if not self.memory_enabled:
            return
        for removed, added in rewires:
            attack_mass = float(self.last_traversals.get(removed, 0))
            self.failure[removed] = self.failure.get(removed, 0.0) + 1.0 + attack_mass
            for node in removed:
                self.volatility[node] = self.volatility.get(node, 0.0) + 1.0
            for node in added:
                self.volatility[node] = self.volatility.get(node, 0.0) + 0.35


class PheromonePureConsensusPolicy(PheromoneConsensusPolicy):
    name = "pheromone_consensus"

    def __init__(self, **kwargs):
        super().__init__(contrarian_mode="none", memory_enabled=True, **kwargs)


class PheromoneFixedContrarianPolicy(PheromoneConsensusPolicy):
    name = "pheromone_fixed25"

    def __init__(self, epsilon: float = 0.25, **kwargs):
        super().__init__(contrarian_mode="fixed", fixed_epsilon=epsilon, memory_enabled=True, **kwargs)


class AdaptiveConsensusNoMemoryPolicy(PheromoneConsensusPolicy):
    """Same consensus/contrarian machinery with all pheromone memory disabled."""

    name = "adaptive_no_memory"

    def __init__(self, **kwargs):
        super().__init__(contrarian_mode="adaptive", memory_enabled=False, **kwargs)
