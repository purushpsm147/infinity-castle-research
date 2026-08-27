from __future__ import annotations

import math


def junction_success_probability(p: float, n: int, d: int, epsilon: float) -> float:
    """Probability at least one crow takes the correct branch.

    Consensus is correct with probability p. Each crow follows consensus with
    probability 1-epsilon. A contrarian chooses uniformly among the d-1 other
    branches.
    """
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0,1]")
    if n < 1 or d < 2:
        raise ValueError("n >= 1 and d >= 2 required")
    if not (0.0 <= epsilon <= 1.0):
        raise ValueError("epsilon must be in [0,1]")
    return float(
        p * (1.0 - epsilon**n)
        + (1.0 - p) * (1.0 - (1.0 - epsilon / (d - 1)) ** n)
    )


def optimal_contrarian_fraction(p: float, n: int, d: int) -> float:
    """Closed-form epsilon maximizing *only* junction_success_probability.

    This is a one-junction toy optimum, not a trajectory-level or adversarial
    castle optimum. It assumes p is a calibrated probability that consensus is
    correct and does not model common-cause failure when a demon attacks a
    shared corridor.

    For n=1, following the most-probable branch is optimal whenever p >= 1/d.
    """
    if n < 1 or d < 2:
        raise ValueError("n >= 1 and d >= 2 required")
    p = float(p)
    if p < 1.0 / d:
        raise ValueError("consensus reliability must be at least random chance 1/d")
    if n == 1:
        return 0.0
    if p >= 1.0:
        return 0.0
    a = ((1.0 - p) / (p * (d - 1))) ** (1.0 / (n - 1))
    return float(a * (d - 1) / (d - 1 + a))


def pheromone_half_life(decay: float) -> float:
    """Rounds until an exponentially decayed signal falls to half strength."""
    if not (0.0 < decay < 1.0):
        raise ValueError("decay must be in (0,1)")
    return float(math.log(0.5) / math.log(decay))
