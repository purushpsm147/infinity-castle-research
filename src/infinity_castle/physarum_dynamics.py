from __future__ import annotations

from typing import Dict

import networkx as nx
import numpy as np

from .model import Edge, Node, canon_edge


def initial_conductance(graph: nx.Graph, value: float = 1.0) -> Dict[Edge, float]:
    return {canon_edge(u, v): float(value) for u, v in graph.edges()}


def static_physarum_step(
    graph: nx.Graph,
    source: Node,
    target: Node,
    conductance: Dict[Edge, float],
    *,
    dt: float = 0.1,
    floor: float = 1e-12,
) -> tuple[Dict[Edge, float], Dict[Edge, float]]:
    """One canonical fixed-source/fixed-sink Physarum conductance step.

    Edge resistance is length / conductance. Edge attribute 'length' defaults
    to 1. Unit flow is injected at source and removed at target. The update is
    D_e <- D_e + dt * (abs(Q_e) - D_e).

    This helper validates known static shortest-path behavior before we use a
    moving-source, adversarially rewired variant.
    """
    if source == target:
        return dict(conductance), {e: 0.0 for e in conductance}

    nodes = list(graph.nodes())
    non_target = [n for n in nodes if n != target]
    idx = {n: i for i, n in enumerate(non_target)}
    if source not in idx:
        raise ValueError("source/target missing from graph")

    lap = np.zeros((len(non_target), len(non_target)), dtype=float)
    rhs = np.zeros(len(non_target), dtype=float)
    rhs[idx[source]] = 1.0

    for u, v, data in graph.edges(data=True):
        e = canon_edge(u, v)
        length = float(data.get("length", 1.0))
        if length <= 0:
            raise ValueError("edge lengths must be positive")
        d = max(float(conductance.get(e, 1.0)), floor)
        c = d / length
        if u != target:
            lap[idx[u], idx[u]] += c
        if v != target:
            lap[idx[v], idx[v]] += c
        if u != target and v != target:
            lap[idx[u], idx[v]] -= c
            lap[idx[v], idx[u]] -= c

    try:
        pvec = np.linalg.solve(lap, rhs)
    except np.linalg.LinAlgError:
        pvec = np.linalg.lstsq(lap, rhs, rcond=None)[0]

    pressure = {target: 0.0}
    pressure.update({n: float(pvec[idx[n]]) for n in non_target})

    flux: Dict[Edge, float] = {}
    updated: Dict[Edge, float] = {}
    for u, v, data in graph.edges(data=True):
        e = canon_edge(u, v)
        length = float(data.get("length", 1.0))
        d = max(float(conductance.get(e, 1.0)), floor)
        q = (d / length) * (pressure[u] - pressure[v])
        flux[e] = float(q)
        updated[e] = max(floor, d + dt * (abs(q) - d))

    return updated, flux


def run_static_physarum(
    graph: nx.Graph,
    source: Node,
    target: Node,
    *,
    steps: int = 1000,
    dt: float = 0.05,
    initial: float = 1.0,
) -> Dict[Edge, float]:
    d = initial_conductance(graph, initial)
    for _ in range(steps):
        d, _ = static_physarum_step(graph, source, target, d, dt=dt)
    return d
