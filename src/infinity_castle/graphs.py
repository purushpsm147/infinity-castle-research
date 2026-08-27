from __future__ import annotations

import networkx as nx
import numpy as np


def grid_graph(side: int = 6) -> tuple[nx.Graph, tuple[int, int], tuple[int, int]]:
    g = nx.grid_2d_graph(side, side)
    nx.set_edge_attributes(g, 1.0, "length")
    return g, (0, 0), (side - 1, side - 1)


def ladder_graph(length: int = 12) -> tuple[nx.Graph, tuple[int, int], tuple[int, int]]:
    g = nx.Graph()
    for i in range(length):
        g.add_edge((0, i), (0, i + 1), length=1.0)
        g.add_edge((1, i), (1, i + 1), length=1.0)
        g.add_edge((0, i), (1, i), length=1.0)
    g.add_edge((0, length), (1, length), length=1.0)
    return g, (0, 0), (1, length)


def connected_erdos_renyi(n: int = 36, p: float = 0.12, seed: int = 0):
    rng = np.random.default_rng(seed)
    for _ in range(1000):
        s = int(rng.integers(0, 2**31 - 1))
        g = nx.gnp_random_graph(n, p, seed=s)
        if nx.is_connected(g):
            nx.set_edge_attributes(g, 1.0, "length")
            lengths = dict(nx.single_source_shortest_path_length(g, 0))
            target = max(lengths, key=lengths.get)
            return g, 0, target
    raise RuntimeError("failed to sample a connected Erdos-Renyi graph")


def unequal_corridors(lengths: list[int] | tuple[int, ...]):
    """Internally edge-disjoint unit-edge corridors with specified path lengths."""
    if not lengths or any(int(x) < 2 for x in lengths):
        raise ValueError("each corridor length must be >=2")
    g = nx.Graph()
    source = ("s", 0)
    target = ("t", 0)
    route_edges = []
    for r, path_length in enumerate(lengths):
        prev = source
        edges = []
        for j in range(1, int(path_length)):
            cur = (r, j)
            g.add_edge(prev, cur, length=1.0)
            edges.append((prev, cur))
            prev = cur
        g.add_edge(prev, target, length=1.0)
        edges.append((prev, target))
        route_edges.append(edges)
    return g, source, target, route_edges


def parallel_corridors(routes: int = 4, length: int = 6):
    """Backward-compatible equal-length corridor benchmark."""
    g, source, target, _ = unequal_corridors([length] * routes)
    return g, source, target
