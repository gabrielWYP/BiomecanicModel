"""
Optimizer module using differential evolution with soft penalty constraints.
"""

import math
import warnings
from dataclasses import dataclass
from typing import Any

import numpy as np
from scipy.optimize import differential_evolution

from src.config_loader import Config
from src.ergonomics_math import total_fatigue_cost


@dataclass(frozen=True)
class OptimizationResult:
    """Result of an optimization run."""

    layout: list[dict]
    cost: float
    converged: bool
    iterations: int
    message: str
    tolerance: float


def _objective(
    x_flat: np.ndarray,
    config: Config,
) -> float:
    """Internal objective function with soft penalties.

    x_flat: flat array of coordinates [x1, y1, z1, x2, y2, z2, ...]
    """
    n_tools = len(config.tools)
    worker_ref = config.worker_reference
    ws = config.workspace

    # Build layout dicts from flat vector
    layout = []
    for i in range(n_tools):
        idx = i * 3
        layout.append({
            "name": config.tools[i].name,
            "x": float(x_flat[idx]),
            "y": float(x_flat[idx + 1]),
            "z": float(x_flat[idx + 2]),
            "weight_kg": config.tools[i].weight_kg,
        })

    # Base fatigue cost
    base_cost = total_fatigue_cost(layout, worker_ref)

    # Soft penalty factor
    penalty_factor = 1e6
    penalty = 0.0

    # Collision penalty: distance < min_separation
    positions = [(t["x"], t["y"], t["z"]) for t in layout]
    for i in range(n_tools):
        for j in range(i + 1, n_tools):
            dist = math.sqrt(
                (positions[i][0] - positions[j][0]) ** 2
                + (positions[i][1] - positions[j][1]) ** 2
                + (positions[i][2] - positions[j][2]) ** 2
            )
            if dist < ws.min_separation:
                penalty += penalty_factor * (ws.min_separation - dist)

    # Reach penalty: distance > reach_radius from worker_ref
    for pos in positions:
        dist = math.sqrt(
            (pos[0] - worker_ref[0]) ** 2
            + (pos[1] - worker_ref[1]) ** 2
            + (pos[2] - worker_ref[2]) ** 2
        )
        if dist > ws.reach_radius:
            penalty += penalty_factor * (dist - ws.reach_radius)

    return base_cost + penalty


def optimize(
    config: Config,
    random_seed: int | None = None,
    max_iterations: int = 1000,
) -> OptimizationResult:
    """Optimize tool layout using differential evolution.

    Args:
        config: Validated configuration.
        random_seed: Optional seed for reproducibility.
        max_iterations: Maximum iterations for DE.

    Returns:
        OptimizationResult with layout, cost, and metadata.
    """
    n_tools = len(config.tools)
    ws = config.workspace

    # Bounds for each coordinate: [x_min, x_max], [y_min, y_max], [z_min, z_max] per tool
    bounds = []
    for _ in range(n_tools):
        bounds.append((ws.x_min, ws.x_max))
        bounds.append((ws.y_min, ws.y_max))
        bounds.append((ws.z_min, ws.z_max))

    result = differential_evolution(
        _objective,
        bounds,
        args=(config,),
        seed=random_seed,
        maxiter=max_iterations,
        polish=True,
        tol=0.01,
    )

    if not result.success:
        warnings.warn(
            f"Optimizer did not converge: {result.message}",
            stacklevel=2,
        )

    # Convert flat result to unified layout
    layout = []
    for i in range(n_tools):
        idx = i * 3
        layout.append({
            "name": config.tools[i].name,
            "x": float(result.x[idx]),
            "y": float(result.x[idx + 1]),
            "z": float(result.x[idx + 2]),
            "weight_kg": config.tools[i].weight_kg,
        })

    return OptimizationResult(
        layout=layout,
        cost=float(result.fun),
        converged=bool(result.success),
        iterations=int(result.nit),
        message=str(result.message),
        tolerance=float(result.tol) if hasattr(result, "tol") else 0.01,
    )
