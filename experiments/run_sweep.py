from __future__ import annotations

import argparse
from pathlib import Path

from infinity_castle.experiments import summarize, sweep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--horizon", type=int, default=80)
    ap.add_argument("--out", type=Path, default=Path("results/smoke.csv"))
    args = ap.parse_args()

    df = sweep(range(args.seeds), horizon=args.horizon)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out, index=False)
    summary_path = args.out.with_name(args.out.stem + "_summary.csv")
    summarize(df).to_csv(summary_path, index=False)
    print(f"wrote {len(df)} runs to {args.out}")
    print(f"wrote summary to {summary_path}")


if __name__ == "__main__":
    main()
