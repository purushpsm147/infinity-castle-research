from __future__ import annotations

import math
from typing import Iterable

import numpy as np


def shannon_entropy(counts: Iterable[float]) -> float:
    arr = np.asarray(list(counts), dtype=float)
    arr = arr[arr > 0]
    if arr.size == 0:
        return 0.0
    p = arr / arr.sum()
    return float(-(p * np.log(p)).sum())


def effective_support(counts: Iterable[float]) -> float:
    """exp(H): effective number of equally used routes/edges."""
    return float(math.exp(shannon_entropy(counts)))


def herfindahl_index(counts: Iterable[float]) -> float:
    arr = np.asarray(list(counts), dtype=float)
    if arr.size == 0 or arr.sum() <= 0:
        return 0.0
    p = arr / arr.sum()
    return float(np.square(p).sum())


def top_b_mass(counts: Iterable[float], b: int) -> float:
    """Fraction of traffic an attacker can cover by targeting top-b edges/routes."""
    arr = np.asarray(list(counts), dtype=float)
    if arr.size == 0 or arr.sum() <= 0 or b <= 0:
        return 0.0
    b = min(int(b), arr.size)
    return float(np.sort(arr)[-b:].sum() / arr.sum())


def trace_metrics(traces, attack_budget: int = 1) -> dict[str, float]:
    entropies, supports, hhis, topmasses = [], [], [], []
    for tr in traces:
        vals = list(tr.traffic.values())
        if not vals:
            continue
        entropies.append(shannon_entropy(vals))
        supports.append(effective_support(vals))
        hhis.append(herfindahl_index(vals))
        topmasses.append(top_b_mass(vals, attack_budget))
    if not entropies:
        return {"mean_edge_entropy": 0.0, "mean_effective_support": 0.0, "mean_hhi": 0.0, "mean_top_b_mass": 0.0}
    return {
        "mean_edge_entropy": float(np.mean(entropies)),
        "mean_effective_support": float(np.mean(supports)),
        "mean_hhi": float(np.mean(hhis)),
        "mean_top_b_mass": float(np.mean(topmasses)),
    }


def expected_occupied_routes(k: int, m: int) -> float:
    if k < 0 or m <= 0:
        raise ValueError("k must be >=0 and m must be >0")
    return float(m * (1.0 - (1.0 - 1.0 / m) ** k))


def occupancy_survival_probability(k: int, m: int, b: int) -> float:
    """P(R>b) for k iid uniform choices among m routes.

    R is the number of distinct occupied routes. This models a post-choice attacker
    that can neutralize b whole route frontiers in one round.
    """
    if k < 0 or m <= 0 or b < 0:
        raise ValueError("invalid k, m, b")
    if b >= min(k, m):
        return 0.0
    S = [[0] * (k + 1) for _ in range(k + 1)]
    S[0][0] = 1
    for n in range(1, k + 1):
        for r in range(1, n + 1):
            S[n][r] = S[n - 1][r - 1] + r * S[n - 1][r]
    total = 0.0
    falling = 1
    for r in range(1, min(k, m) + 1):
        falling *= (m - r + 1)
        if r > b:
            total += falling * S[k][r]
    return float(total / (m ** k))
