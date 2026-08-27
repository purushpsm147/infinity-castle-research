from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Hashable, List, Tuple

Node = Hashable
Edge = Tuple[Node, Node]


def canon_edge(u: Node, v: Node) -> Edge:
    return (u, v) if repr(u) <= repr(v) else (v, u)


@dataclass(frozen=True)
class CastleConfig:
    horizon: int = 80
    agents: int = 4
    adversary_budget: int = 1
    preserve_connectivity: bool = True


@dataclass
class StepTrace:
    t: int
    positions_before: List[Node]
    positions_after: List[Node]
    traffic: Dict[Edge, int]
    rewires: List[Tuple[Edge, Edge]] = field(default_factory=list)


@dataclass
class RunResult:
    success: bool
    reach_time: int | None
    work: int
    max_agents: int
    final_positions: List[Node]
    traces: List[StepTrace] = field(default_factory=list)
