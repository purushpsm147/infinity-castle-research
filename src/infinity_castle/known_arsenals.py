"""Known-theory baselines for the Infinity Castle.

These are deliberately baselines, not novelty claims.  The point is to ask
whether the castle remains difficult after importing mature tools rather than
inventing another bespoke bio-inspired policy.
"""
from __future__ import annotations

from collections import defaultdict
import math
from typing import Dict, List

import networkx as nx
import numpy as np

from .model import Edge, Node, canon_edge
from .policies import Policy


def _neighbors(graph: nx.Graph, p: Node) -> List[Node]:
    return sorted(graph.neighbors(p), key=repr)


class EXP3RoutingPolicy(Policy):
    """Local EXP3 adversarial-bandit routing.

    Each node is a bandit; outgoing neighbors are arms.  Reward is observed
    progress toward the target, penalized when the traversed edge is rewired.
    New arms start with unit weight.  This is intentionally local because a
    crow observes only the move it actually made.
    """

    name = "exp3"

    def __init__(self, gamma: float = 0.12, attack_penalty: float = 1.0):
        self.gamma = float(gamma)
        self.attack_penalty = float(attack_penalty)
        self.weights: Dict[Node, Dict[Node, float]] = defaultdict(dict)
        self.last_choices = []

    def reset(self, graph, source, target, agents):
        self.weights = defaultdict(dict)
        self.last_choices = []

    def _distribution(self, graph, p):
        nbrs = _neighbors(graph, p)
        if not nbrs:
            return nbrs, np.array([])
        w = self.weights[p]
        for n in nbrs:
            w.setdefault(n, 1.0)
        vals = np.asarray([max(w[n], 1e-12) for n in nbrs], dtype=float)
        probs = (1.0 - self.gamma) * vals / vals.sum() + self.gamma / len(nbrs)
        return nbrs, probs

    def choose_moves(self, graph, positions, target, rng):
        out, choices = [], []
        for i, p in enumerate(positions):
            if p == target:
                out.append(p); choices.append(None); continue
            nbrs, probs = self._distribution(graph, p)
            if not nbrs:
                out.append(p); choices.append(None); continue
            j = int(rng.choice(len(nbrs), p=probs))
            out.append(nbrs[j])
            choices.append((i, p, nbrs[j], float(probs[j])))
        self.last_choices = choices
        return out

    def observe_transition(self, graph_before, positions_before, positions_after, target):
        dist = nx.single_source_shortest_path_length(graph_before, target)
        for choice in self.last_choices:
            if choice is None:
                continue
            i, p, q, prob = choice
            if positions_after[i] != q:
                reward = 0.0
            else:
                delta = dist.get(p, 10**6) - dist.get(q, 10**6)
                reward = 1.0 if delta > 0 else (0.5 if delta == 0 else 0.0)
            k = max(1, len(list(graph_before.neighbors(p))))
            estimated = reward / max(prob, 1e-12)
            self.weights[p][q] = self.weights[p].get(q, 1.0) * math.exp(self.gamma * estimated / k)

    def observe_rewire(self, graph_after, rewires, positions, target):
        removed = {canon_edge(*rem) for rem, _ in rewires}
        for choice in self.last_choices:
            if choice is None:
                continue
            _, p, q, prob = choice
            if canon_edge(p, q) in removed and q in self.weights.get(p, {}):
                # Multiplicative negative update for an observed reactive cut.
                k = max(1, len(self.weights[p]))
                loss_hat = self.attack_penalty / max(prob, 1e-12)
                self.weights[p][q] *= math.exp(-self.gamma * loss_hat / k)


class MinimaxTrafficPolicy(Policy):
    """One-step security-game baseline.

    Co-located crows are allocated across candidate next hops to minimize the
    maximum traffic placed on any one branch, while preferring branches with
    shorter current distance to target.  This approximates the defender's
    max-min response to a traffic-aware budgeted interdictor.
    """

    name = "minimax_traffic"

    def __init__(self, slack: int = 1):
        self.slack = int(slack)

    def choose_moves(self, graph, positions, target, rng):
        dist = nx.single_source_shortest_path_length(graph, target)
        grouped: Dict[Node, List[int]] = defaultdict(list)
        for i, p in enumerate(positions):
            grouped[p].append(i)
        result = list(positions)
        for p, idxs in grouped.items():
            if p == target:
                continue
            nbrs = _neighbors(graph, p)
            if not nbrs:
                continue
            best = min((dist.get(n, 10**6) for n in nbrs), default=10**6)
            admissible = [n for n in nbrs if dist.get(n, 10**6) <= best + self.slack]
            if not admissible:
                admissible = nbrs
            # Round-robin is the discrete minimax allocation: it minimizes the
            # largest branch load among the admissible actions.
            admissible.sort(key=lambda n: (dist.get(n, 10**6), repr(n)))
            for j, idx in enumerate(idxs):
                result[idx] = admissible[j % len(admissible)]
        return result


class RobustMDPPolicy(Policy):
    """Small robust-control baseline using pessimistic edge-risk estimates.

    This is not a full solved robust MDP over graph states (which is exponential).
    It is a receding-horizon robust surrogate: estimate attack probability per
    edge, then minimize immediate distance + beta * adversarial risk.  The label
    is intentionally explicit about that limitation in experiment reports.
    """

    name = "robust_mdp_surrogate"

    def __init__(self, beta: float = 2.0, decay: float = 0.95, exploration: float = 0.08):
        self.beta = float(beta)
        self.decay = float(decay)
        self.exploration = float(exploration)
        self.risk: Dict[Edge, float] = {}

    def reset(self, graph, source, target, agents):
        self.risk = {canon_edge(u, v): 0.0 for u, v in graph.edges()}

    def choose_moves(self, graph, positions, target, rng):
        dist = nx.single_source_shortest_path_length(graph, target)
        out = []
        for p in positions:
            if p == target:
                out.append(p); continue
            nbrs = _neighbors(graph, p)
            if not nbrs:
                out.append(p); continue
            if rng.random() < self.exploration:
                out.append(nbrs[int(rng.integers(len(nbrs)))]); continue
            scored = []
            for n in nbrs:
                e = canon_edge(p, n)
                scored.append((dist.get(n, 10**6) + self.beta * self.risk.get(e, 0.0), repr(n), n))
            out.append(min(scored)[2])
        return out

    def observe_rewire(self, graph_after, rewires, positions, target):
        for e in list(self.risk):
            self.risk[e] *= self.decay
        for rem, add in rewires:
            r = canon_edge(*rem)
            self.risk[r] = self.risk.get(r, 0.0) + 1.0
            self.risk.setdefault(canon_edge(*add), 0.0)


class EXP3MinimaxHybridPolicy(EXP3RoutingPolicy):
    """Bandit learning plus explicit anti-herding across a crow group.

    EXP3 supplies adversarial online learning; a load-balancing correction
    discourages all agents from selecting the same currently-favoured arm.
    This is a benchmark combination, not claimed as a new algorithm.
    """

    name = "exp3_minimax"

    def __init__(self, gamma: float = 0.12, crowd_penalty: float = 0.75):
        super().__init__(gamma=gamma)
        self.crowd_penalty = float(crowd_penalty)

    def choose_moves(self, graph, positions, target, rng):
        grouped: Dict[Node, List[int]] = defaultdict(list)
        for i, p in enumerate(positions):
            grouped[p].append(i)
        result = list(positions)
        choices = [None] * len(positions)
        for p, idxs in grouped.items():
            if p == target:
                continue
            nbrs, base = self._distribution(graph, p)
            if not nbrs:
                continue
            loads = np.zeros(len(nbrs), dtype=float)
            for idx in idxs:
                adjusted = base * np.exp(-self.crowd_penalty * loads)
                adjusted /= adjusted.sum()
                j = int(rng.choice(len(nbrs), p=adjusted))
                result[idx] = nbrs[j]
                choices[idx] = (idx, p, nbrs[j], float(adjusted[j]))
                loads[j] += 1.0
        self.last_choices = choices
        return result
