from __future__ import annotations

from typing import Callable, Dict, Iterable

import pandas as pd

from .adversaries import NoAdversary, ObliviousChurnAdversary, ReactiveCutAdversary, TrafficAwareAdversary
from .graphs import connected_erdos_renyi, grid_graph, ladder_graph
from .model import CastleConfig
from .policies import (
    DisjointPathPolicy,
    GenericReinforcementPolicy,
    PhysarumPolicy,
    RandomWalkPolicy,
    ReplanShortestPathPolicy,
)
from .simulator import run_episode


POLICIES: Dict[str, Callable] = {
    "random": RandomWalkPolicy,
    "replan": ReplanShortestPathPolicy,
    "disjoint": DisjointPathPolicy,
    "reinforcement": GenericReinforcementPolicy,
    "physarum": PhysarumPolicy,
}

ADVERSARIES: Dict[str, Callable] = {
    "none": NoAdversary,
    "oblivious": ObliviousChurnAdversary,
    "traffic_aware": TrafficAwareAdversary,
    "reactive_cut": ReactiveCutAdversary,
}


def make_graph(family: str, seed: int):
    if family == "grid":
        return grid_graph(6)
    if family == "ladder":
        return ladder_graph(12)
    if family == "er":
        return connected_erdos_renyi(36, 0.12, seed)
    raise KeyError(f"unknown graph family: {family}")


def sweep(
    seeds: Iterable[int],
    graph_families=("grid", "ladder"),
    policies=("random", "replan", "disjoint", "reinforcement", "physarum"),
    adversaries=("none", "oblivious", "traffic_aware", "reactive_cut"),
    agents=(2, 4),
    budgets=(0, 1, 2),
    horizon: int = 80,
) -> pd.DataFrame:
    rows = []
    for seed in seeds:
        for family in graph_families:
            graph, source, target = make_graph(family, seed)
            for adv_name in adversaries:
                for k in agents:
                    for b in budgets:
                        if adv_name == "none" and b != 0:
                            continue
                        if adv_name != "none" and b == 0:
                            continue
                        for pol_name in policies:
                            cfg = CastleConfig(horizon=horizon, agents=k, adversary_budget=b)
                            result = run_episode(
                                graph,
                                source,
                                target,
                                POLICIES[pol_name](),
                                ADVERSARIES[adv_name](),
                                cfg,
                                seed=seed * 1009 + k * 31 + b * 7,
                            )
                            rows.append(
                                {
                                    "seed": seed,
                                    "graph": family,
                                    "policy": pol_name,
                                    "adversary": adv_name,
                                    "agents": k,
                                    "budget": b,
                                    "horizon": horizon,
                                    "success": int(result.success),
                                    "reach_time": result.reach_time,
                                    "work": result.work,
                                    "max_agents": result.max_agents,
                                }
                            )
    return pd.DataFrame(rows)


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    group_cols = ["graph", "policy", "adversary", "agents", "budget", "horizon"]
    return (
        df.groupby(group_cols, dropna=False)
        .agg(
            p_reach=("success", "mean"),
            mean_work=("work", "mean"),
            median_work=("work", "median"),
            mean_reach_time=("reach_time", "mean"),
            runs=("success", "size"),
        )
        .reset_index()
    )
