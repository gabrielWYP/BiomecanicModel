"""
Tests de propiedad para optimizer.py
"""

import math

import pytest

from src.config_loader import Config, ToolConfig, WorkspaceConfig
from src.ergonomics_math import total_fatigue_cost
from src.optimizer import OptimizationResult, optimize


# Small 2-tool config fixture
def _make_small_config(
    x_min=0.0,
    x_max=2.0,
    y_min=0.0,
    y_max=2.0,
    z_min=0.0,
    z_max=2.0,
    reach_radius=1.5,
    min_separation=0.2,
    worker_ref=(0.0, 0.0, 1.0),
    tool_positions=None,
) -> Config:
    """Build a small Config with 2 tools for fast optimization."""
    if tool_positions is None:
        tool_positions = [(0.5, 0.5, 0.5), (1.5, 1.5, 1.5)]
    return Config(
        workspace=WorkspaceConfig(
            x_min=x_min,
            x_max=x_max,
            y_min=y_min,
            y_max=y_max,
            z_min=z_min,
            z_max=z_max,
            reach_radius=reach_radius,
            min_separation=min_separation,
        ),
        worker_reference=worker_ref,
        tools=[
            ToolConfig(
                name="A",
                weight_kg=1.0,
                initial_position=tool_positions[0],
            ),
            ToolConfig(
                name="B",
                weight_kg=0.5,
                initial_position=tool_positions[1],
            ),
        ],
    )


# ============================================================================
# Task 4.5: P7 — Bounds: all coordinates within workspace
# ============================================================================


@pytest.mark.parametrize("seed", [0, 1, 42, 123, 999])
def test_optimizer_bounds(seed):
    """P7: All optimized coordinates lie within workspace bounds."""
    config = _make_small_config()
    result = optimize(config, random_seed=seed, max_iterations=200)

    assert isinstance(result, OptimizationResult)
    ws = config.workspace
    for tool in result.layout:
        assert ws.x_min <= tool["x"] <= ws.x_max
        assert ws.y_min <= tool["y"] <= ws.y_max
        assert ws.z_min <= tool["z"] <= ws.z_max


@pytest.mark.parametrize("seed", [0, 42])
def test_optimizer_bounds_different_workspace(seed):
    """P7: Bounds hold with different workspace sizes."""
    config = _make_small_config(x_max=3.0, y_max=3.0, z_max=3.0)
    result = optimize(config, random_seed=seed, max_iterations=200)

    ws = config.workspace
    for tool in result.layout:
        assert ws.x_min <= tool["x"] <= ws.x_max
        assert ws.y_min <= tool["y"] <= ws.y_max
        assert ws.z_min <= tool["z"] <= ws.z_max


# ============================================================================
# Task 4.5: P8 — Separation: all pairwise distances >= min_separation
# ============================================================================


@pytest.mark.parametrize("seed", [0, 1, 42, 123])
def test_optimizer_separation(seed):
    """P8: All pairwise distances >= min_separation in optimized layout."""
    config = _make_small_config()
    result = optimize(config, random_seed=seed, max_iterations=200)

    positions = [(t["x"], t["y"], t["z"]) for t in result.layout]
    n = len(positions)
    for i in range(n):
        for j in range(i + 1, n):
            dist = math.sqrt(
                (positions[i][0] - positions[j][0]) ** 2
                + (positions[i][1] - positions[j][1]) ** 2
                + (positions[i][2] - positions[j][2]) ** 2
            )
            assert dist >= config.workspace.min_separation, (
                f"Pair ({i},{j}) distance {dist} < min_sep {config.workspace.min_separation}"
            )


@pytest.mark.parametrize("seed", [0, 42])
def test_optimizer_separation_large_min_sep(seed):
    """P8: Separation holds even with larger min_separation."""
    config = _make_small_config(min_separation=0.5)
    result = optimize(config, random_seed=seed, max_iterations=200)

    positions = [(t["x"], t["y"], t["z"]) for t in result.layout]
    n = len(positions)
    for i in range(n):
        for j in range(i + 1, n):
            dist = math.sqrt(
                (positions[i][0] - positions[j][0]) ** 2
                + (positions[i][1] - positions[j][1]) ** 2
                + (positions[i][2] - positions[j][2]) ** 2
            )
            assert dist >= config.workspace.min_separation


# ============================================================================
# Task 4.5: P9 — Monotonic improvement: optimized cost <= initial cost
# ============================================================================


def test_optimizer_improves_cost():
    """P9: Optimized cost is <= initial cost."""
    config = _make_small_config()
    result = optimize(config, random_seed=42, max_iterations=200)

    initial_layout = [
        {"name": t.name, "x": t.initial_position[0], "y": t.initial_position[1], "z": t.initial_position[2], "weight_kg": t.weight_kg}
        for t in config.tools
    ]
    initial_cost = total_fatigue_cost(initial_layout, config.worker_reference)

    assert result.cost <= initial_cost


@pytest.mark.parametrize("seed", [0, 1, 42])
def test_optimizer_improves_cost_multiple_seeds(seed):
    """P9: Monotonic improvement across multiple seeds."""
    config = _make_small_config()
    result = optimize(config, random_seed=seed, max_iterations=200)

    initial_layout = [
        {"name": t.name, "x": t.initial_position[0], "y": t.initial_position[1], "z": t.initial_position[2], "weight_kg": t.weight_kg}
        for t in config.tools
    ]
    initial_cost = total_fatigue_cost(initial_layout, config.worker_reference)

    assert result.cost <= initial_cost


# ============================================================================
# Task 4.5: P10 — Idempotence: re-optimizing doesn't increase cost
# ============================================================================


def test_optimizer_idempotence():
    """P10: Re-optimizing with same seed doesn't increase cost."""
    config = _make_small_config()
    result1 = optimize(config, random_seed=42, max_iterations=200)
    result2 = optimize(config, random_seed=42, max_iterations=200)

    assert result2.cost <= result1.cost


# ============================================================================
# Task 4.1/4.3: OptimizationResult structure
# ============================================================================


def test_optimizer_result_structure():
    """Result has all expected fields and types."""
    config = _make_small_config()
    result = optimize(config, random_seed=42, max_iterations=200)

    assert isinstance(result.layout, list)
    assert len(result.layout) == len(config.tools)
    for tool in result.layout:
        assert isinstance(tool, dict)
        assert "name" in tool
        assert "x" in tool
        assert "y" in tool
        assert "z" in tool
        assert "weight_kg" in tool

    assert isinstance(result.cost, float)
    assert isinstance(result.converged, bool)
    assert isinstance(result.iterations, int)
    assert isinstance(result.message, str)
    assert isinstance(result.tolerance, float)


# ============================================================================
# Task 4.3: Warn on non-convergence (best-effort test with tiny budget)
# ============================================================================


def test_optimizer_warns_on_non_convergence():
    """Optimizer warns when it doesn't converge within max_iterations."""
    import warnings

    config = _make_small_config()
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = optimize(config, random_seed=42, max_iterations=5)
        if not result.converged:
            assert any("converge" in str(warning.message).lower() for warning in w)
