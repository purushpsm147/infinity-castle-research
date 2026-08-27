from __future__ import annotations

import networkx as nx
import numpy as np


def grid_graph(side: int = 6) -> tuple[nx.Graph, tuple[int, int], tuple[int, int]]:
    g = nx.grid_2d_graph(side, side)
    return g, (0, 0), (side - 1, side - 1)


def ladder_graph(length: int = 12) -> tuple[nx.Graph, tuple[int, int], tuple[int, int]]:
    g = nx.Graph()
    for i in range(length):
        g.add_edge((0, i), (0, i + 1))
        g.add_edge((1, i), (1, i + 1))
        g.add_edge((0, i), (1, i))
    g.add_edge((0, length), (1, length))
    return g, (0, 0), (1, length)


def connected_erdos_renyi(n: int = 36, p: float = 0.12, seed: int = 0):
    rng = np.random.default_rng(seed)
    for _ in range(1000):
        s = int(rng.integers(0, 2**31 - 1))
        g = nx.gnp_random_graph(n, p, seed=s)
        if nx.is_connected(g):
            lengths = dict(nx.single_source_shortest_path_length(g, 0))
            target = max(lengths, key=lengths.get)
            return g, 0, target
    raise RuntimeError("failed to sample a connected Erdos-Renyi graph")
