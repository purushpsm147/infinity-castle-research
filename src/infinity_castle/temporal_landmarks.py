from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Dict, Iterable, Tuple

TemporalEdge = Tuple[int, int]
TemporalLabels = Dict[TemporalEdge, int]


def _canon(u: int, v: int) -> TemporalEdge:
    return (u, v) if u < v else (v, u)


def time_respecting_paths(
    labels: TemporalLabels,
    source: int,
    target: int,
) -> list[tuple[int, ...]]:
    """Enumerate simple undirected paths with nondecreasing edge labels."""
    adj = defaultdict(list)
    for (u, v), tau in labels.items():
        adj[u].append((v, tau))
        adj[v].append((u, tau))

    out: list[tuple[int, ...]] = []

    def dfs(u: int, last_tau: int, path: list[int], seen: set[int]) -> None:
        if u == target:
            out.append(tuple(path))
            return
        for v, tau in adj[u]:
            if v in seen or tau < last_tau:
                continue
            dfs(v, tau, path + [v], seen | {v})

    dfs(source, -10**18, [source], {source})
    return out


def maximum_vertex_disjoint_journeys(
    labels: TemporalLabels,
    source: int,
    target: int,
) -> int:
    paths = time_respecting_paths(labels, source, target)
    inner = [set(p[1:-1]) for p in paths]
    best = 0
    for r in range(1, len(paths) + 1):
        found = False
        for idxs in combinations(range(len(paths)), r):
            used: set[int] = set()
            ok = True
            for i in idxs:
                if used & inner[i]:
                    ok = False
                    break
                used |= inner[i]
            if ok:
                found = True
                best = r
                break
        if not found:
            break
    return best


def minimum_temporal_vertex_separator(
    labels: TemporalLabels,
    source: int,
    target: int,
) -> int:
    vertices = sorted({x for e in labels for x in e})
    inner = [v for v in vertices if v not in (source, target)]
    original = time_respecting_paths(labels, source, target)
    if not original:
        return 0

    for r in range(1, len(inner) + 1):
        for removed_tuple in combinations(inner, r):
            removed = set(removed_tuple)
            reduced = {
                e: tau for e, tau in labels.items()
                if e[0] not in removed and e[1] not in removed
            }
            if not time_respecting_paths(reduced, source, target):
                return r
    raise ValueError("no finite internal-vertex separator; check for a direct source-target edge")


def temporal_menger_witness() -> tuple[TemporalLabels, int, int]:
    """A small single-label witness of the temporal vertex-Menger violation.

    This is not claimed to be the exact Kempe-Kleinberg-Kumar figure. It is a
    compact independently found instance of the same known phenomenon:
    maximum vertex-disjoint temporal journeys = 1 while minimum temporal
    vertex separator = 2.
    """
    labels = {
        _canon(3, 4): 4,
        _canon(2, 3): 6,
        _canon(0, 1): 2,
        _canon(2, 4): 8,
        _canon(1, 3): 3,
        _canon(1, 2): 7,
        _canon(1, 4): 1,
        _canon(0, 3): 5,
    }
    return labels, 0, 4
