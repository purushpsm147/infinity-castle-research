"""Preregistered exact threshold experiment for the one-for-one rewire castle.

Primary estimand:
    K*(b, lambda_min; H=6, O3p)
= minimum number of centrally coordinated agents that can force target reach
within six rounds against every legal adversary rewire in the finite game.

This is an exact finite-game result for one five-node castle, not a theorem for
all dynamic graphs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from infinity_castle.exact_game import ExactRewireGame, k23_castle, worst_case_transient_cut_arrival


BUDGETS = (1, 2)
LAMBDA_MINS = (1, 2, 3)
HORIZON = 6
K_MAX = 4


def run() -> tuple[pd.DataFrame, dict]:
    g, s, t = k23_castle()
    rows = []
    thresholds = {}

    for b in BUDGETS:
        cut_floor = b + 1
        cut_paths = [2] * cut_floor
        cut_arrival = worst_case_transient_cut_arrival(cut_paths, b)

        for lam in LAMBDA_MINS:
            game = ExactRewireGame(g, s, t, budget=b, lambda_min=lam)
            k_star, results = game.minimum_agents(horizon=HORIZON, k_max=K_MAX)
            thresholds[f"b{b}_lambda{lam}"] = k_star

            for r in results:
                rows.append({
                    "budget": b,
                    "lambda_min": lam,
                    "horizon": HORIZON,
                    "agents": r.agents,
                    "winnable": int(r.winnable),
                    "states_evaluated": r.states_evaluated,
                    "graph_states_seen": r.graph_states_seen,
                    "max_rewire_successors": r.max_rewire_successors,
                    "cut_floor_b_plus_1": cut_floor,
                    "cut_worst_arrival_bound_instance": cut_arrival,
                    "k_star": k_star,
                })

    summary = {
        "model": "five-node K2,3; O3p; up-to-b one-for-one rewires; fixed edge count 6",
        "horizon": HORIZON,
        "k_max": K_MAX,
        "thresholds": thresholds,
        "interpretation_rules": {
            "rewiring_penalty": "supported on this finite instance if K* > b+1 in any cell",
            "no_separation": "if all resolved K* <= b+1, this instance does not separate rewiring from the cut floor",
            "censored": "null K* means no guarantee found for k<=4 within H=6; it is not a universal impossibility result",
        },
    }
    return pd.DataFrame(rows), summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=Path("results/exact_rewire_threshold.csv"))
    args = ap.parse_args()

    df, summary = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    args.out.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")

    print("=== EXACT REWIRE THRESHOLD ===")
    print(df.to_string(index=False))
    print("\n=== K* SUMMARY ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
