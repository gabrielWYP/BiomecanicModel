"""
CLI entry point for the ergonomic layout optimizer.
"""

import argparse
import sys
from pathlib import Path

from src.config_loader import load_config
from src.ergonomics_math import total_fatigue_cost
from src.optimizer import optimize
from src.visualizer import render_comparison


def main(argv=None):
    """Run the ergonomic layout optimizer CLI.

    Args:
        argv: Optional list of arguments (defaults to sys.argv[1:]).

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Optimize ergonomic tool layout to minimize worker fatigue."
    )
    parser.add_argument("config_path", help="Path to the YAML configuration file")
    parser.add_argument(
        "--output",
        default="output/layout_optimizado.html",
        help="Path for the output HTML visualization (default: output/layout_optimizado.html)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed for reproducible optimization",
    )

    args = parser.parse_args(argv)

    try:
        config = load_config(args.config_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    # Build initial layout from config
    initial_layout = [
        {
            "name": tool.name,
            "x": tool.initial_position[0],
            "y": tool.initial_position[1],
            "z": tool.initial_position[2],
            "weight_kg": tool.weight_kg,
        }
        for tool in config.tools
    ]

    initial_cost = total_fatigue_cost(initial_layout, config.worker_reference)

    try:
        result = optimize(config, random_seed=args.seed)
    except Exception as exc:
        print(f"Unexpected error during optimization: {exc}", file=sys.stderr)
        return 1

    optimized_cost = result.cost
    improvement = 0.0
    if initial_cost > 0:
        improvement = ((initial_cost - optimized_cost) / initial_cost) * 100

    print(f"Initial cost:   {initial_cost:.4f}")
    print(f"Optimized cost: {optimized_cost:.4f}")
    print(f"Improvement:    {improvement:.1f}%")

    output_path = Path(args.output)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        render_comparison(
            initial_layout,
            result.layout,
            config.worker_reference,
            initial_cost,
            optimized_cost,
            str(output_path),
        )
    except Exception as exc:
        print(f"Unexpected error during visualization: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
