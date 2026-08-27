from __future__ import annotations

from collections import Counter
from copy import deepcopy
from typing import List

import networkx as nx
import numpy as np

from .adversaries import Adversary
from .model import CastleConfig, RunResult, StepTrace, canon_edge
from .policies import Policy


def run_episode(
    graph: nx.Graph,
    source,
    target,
    policy: Policy,
    adversary: Adversary,
    config: CastleConfig,
    seed: int = 0,
    keep_trace: bool = False,
    separate_rngs: bool = False,
) -> RunResult:
    if source not in graph or target not in graph:
        raise ValueError("source and target must exist in graph")
    if config.agents < 1:
        raise ValueError("agents must be positive")
    if config.horizon < 1:
        raise ValueError("horizon must be positive")

    g = deepcopy(graph)
    if separate_rngs:
        policy_seed, adversary_seed = np.random.SeedSequence(seed).spawn(2)
        policy_rng = np.random.default_rng(policy_seed)
        adversary_rng = np.random.default_rng(adversary_seed)
    else:
        shared_rng = np.random.default_rng(seed)
        policy_rng = shared_rng
        adversary_rng = shared_rng
    positions: List = [source for _ in range(config.agents)]
    policy.reset(g, source, target, config.agents)
    adversary.reset(g, source, target)
    traces = []
    work = 0

    if source == target:
        return RunResult(True, 0, 0, config.agents, positions, traces)

    for t in range(1, config.horizon + 1):
        before = list(positions)
        proposed = policy.choose_moves(g, positions, target, policy_rng)
        if len(proposed) != len(positions):
            raise ValueError("policy returned wrong number of moves")
        traffic = Counter()
        after = []
        for p, q in zip(positions, proposed):
            if p == target:
                after.append(p)
                continue
            if q != p and g.has_edge(p, q):
                after.append(q)
                traffic[canon_edge(p, q)] += 1
                work += 1
            else:
                after.append(p)
        positions = after
        policy.observe_transition(g, before, positions, target)
        if target in positions:
            if keep_trace:
                traces.append(StepTrace(t, before, list(positions), dict(traffic), []))
            return RunResult(True, t, work, config.agents, list(positions), traces)

        rewires = adversary.rewire(g, positions, traffic, config.adversary_budget, adversary_rng)
        policy.observe_rewire(g, rewires, positions, target)
        if config.preserve_connectivity and not nx.is_connected(g):
            raise AssertionError("adversary violated connectivity invariant")
        if keep_trace:
            traces.append(StepTrace(t, before, list(positions), dict(traffic), rewires))

    return RunResult(False, None, work, config.agents, list(positions), traces)
