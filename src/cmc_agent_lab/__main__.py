"""Command line entrypoint for CMC Agent Lab."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cmc_agent_lab.workflow import run_workflow


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cmc-agent-lab",
        description="Run an auditable CMC process-development agent workflow.",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a scenario YAML file.")
    run_parser.add_argument("scenario", type=Path, help="Path to a scenario YAML file.")
    run_parser.add_argument("--output", type=Path, help="Write the markdown memo to this path.")
    run_parser.add_argument("--json", type=Path, help="Write the final agent state to this path.")
    run_parser.add_argument(
        "--mode",
        choices=["scope", "screen", "simulate", "optimize", "learn", "risk", "audit", "full"],
        help="Override the scenario workflow mode.",
    )

    args = parser.parse_args()
    if args.command != "run":
        parser.print_help()
        return

    state = run_workflow(args.scenario, mode_override=args.mode)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(state.report or "", encoding="utf-8")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(state.to_jsonable(), indent=2), encoding="utf-8")

    print(state.report)


if __name__ == "__main__":
    main()
