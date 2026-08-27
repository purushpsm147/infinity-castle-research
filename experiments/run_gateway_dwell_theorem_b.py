"""Frozen mechanical validation for Theorem B: synchronous gateway dwell.

Primary theorem:
    K*_infty = rho_tau(F, A_d(F,s))

where rho_tau is the minimum-size vertex set lying within distance tau of every
admissible d-gateway set.

This runner does not tune parameters or search for favorable instances.
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pandas as pd

from infinity_castle.gateway_dwell import (
    contiguous_grid,
    cycle_d1_formula,
    cycle_d2_formula,
    path_d1_formula,
    verify_gateway_dwell_threshold,
)


def cases():
    out = []

    # Clique corollaries.
    for m, d, tau, expected in [
        (4, 1, 0, 4),
        (5, 2, 0, 4),
        (6, 3, 0, 4),
        (6, 1, 1, 1),
        (7, 3, 1, 1),
    ]:
        out.append((f"clique_{m}", nx.complete_graph(m), 0, d, tau, expected))

    # Path d=1 closed form.
    for m, tau in [(5, 1), (8, 2), (10, 1), (12, 2)]:
        out.append((
            f"path_{m}",
            nx.path_graph(m),
            0,
            1,
            tau,
            path_d1_formula(m, tau),
        ))

    # Cycle d=1 and d=2 closed forms.
    for m, tau in [(6, 1), (9, 1), (12, 2)]:
        out.append((
            f"cycle_{m}_d1",
            nx.cycle_graph(m),
            0,
            1,
            tau,
            cycle_d1_formula(m, tau),
        ))
    for m, tau in [(5, 1), (8, 1), (10, 2), (12, 2)]:
        out.append((
            f"cycle_{m}_d2",
            nx.cycle_graph(m),
            0,
            2,
            tau,
            cycle_d2_formula(m, tau),
        ))

    # Small grids: frozen exact values only; no general grid formula claimed.
    for rows, cols, expected in [
        (2, 2, 2),
        (2, 3, 2),
        (3, 3, 3),
        (4, 4, 4),
    ]:
        out.append((
            f"grid_{rows}x{cols}",
            contiguous_grid(rows, cols),
            0,
            1,
            1,
            expected,
        ))

    return out


def main():
    rows = []
    all_pass = True

    for name, core, source, d, tau, expected in cases():
        cert = verify_gateway_dwell_threshold(core, source, d, tau)
        passed = (
            cert.rho == expected
            and cert.lower_verified
            and cert.upper_verified
        )
        all_pass = all_pass and passed
        rows.append({
            "case": name,
            "vertices": cert.vertices,
            "d": d,
            "tau": tau,
            "predicted_k_star": expected,
            "computed_rho": cert.rho,
            "lower_k": cert.rho - 1,
            "lower_verified": cert.lower_verified,
            "upper_k": cert.rho,
            "upper_verified": cert.upper_verified,
            "admissible_gateway_sets": cert.admissible_gateway_sets,
            "lower_sets_checked": cert.lower_sets_checked,
            "passed": passed,
        })

    out = Path("results/gateway_dwell_theorem_b.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)

    summary = {
        "theorem": "K*_infty = rho_tau(F, A_d(F,s)) in the frozen synchronous gateway-dwell model",
        "cases": len(rows),
        "all_pass": bool(all_pass),
        "model_freeze": {
            "core": "fixed throughout",
            "epochs": "synchronized and observable",
            "gateway_dwell_agent_moves": "tau+1",
            "replacement": "atomic full gateway relocation at epoch boundary",
            "budget": "b>=d",
            "admissibility": "lambda(s,t)>=d checked on the resulting epoch graph",
            "co_location": "allowed",
        },
        "theorem_c": "parked: globally rewritable graph with per-edge persistence is not tested here",
    }
    out.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")

    print("=== GATEWAY-DWELL THEOREM B ===")
    print(df.to_string(index=False))
    print("\n=== SUMMARY ===")
    print(json.dumps(summary, indent=2))

    if not all_pass:
        raise SystemExit("Theorem B validation failed; stop and reconcile proof/model.")


if __name__ == "__main__":
    main()
