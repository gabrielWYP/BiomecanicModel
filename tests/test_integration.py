"""
Integration tests for the full ergonomic layout optimizer pipeline.
"""

import math
from pathlib import Path

from src.config_loader import load_config
from src.ergonomics_math import total_fatigue_cost
from src.optimizer import optimize
from src.visualizer import render_comparison


# Path to the sample configuration used for end-to-end validation
SAMPLE_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"


def test_integration_full_pipeline(tmp_path):
    """End-to-end flow produces HTML and satisfies all constraints."""
    assert SAMPLE_CONFIG.exists(), "Sample config.yaml must exist"

    config = load_config(str(SAMPLE_CONFIG))

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

    result = optimize(config, random_seed=42)

    # Cost improvement
    assert result.cost <= initial_cost, (
        f"Optimized cost {result.cost} should be <= initial cost {initial_cost}"
    )

    # Workspace bounds
    ws = config.workspace
    for tool in result.layout:
        assert ws.x_min <= tool["x"] <= ws.x_max
        assert ws.y_min <= tool["y"] <= ws.y_max
        assert ws.z_min <= tool["z"] <= ws.z_max

    # Separation constraints
    positions = [(t["x"], t["y"], t["z"]) for t in result.layout]
    n = len(positions)
    for i in range(n):
        for j in range(i + 1, n):
            dist = math.sqrt(
                (positions[i][0] - positions[j][0]) ** 2
                + (positions[i][1] - positions[j][1]) ** 2
                + (positions[i][2] - positions[j][2]) ** 2
            )
            assert dist >= ws.min_separation, (
                f"Pair ({i},{j}) distance {dist} < min_sep {ws.min_separation}"
            )

    # Visualization
    output_path = tmp_path / "integration_comparison.html"
    render_comparison(
        initial_layout,
        result.layout,
        config.worker_reference,
        initial_cost,
        result.cost,
        str(output_path),
    )

    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert config.tools[0].name in html
    assert config.tools[1].name in html
    assert str(initial_cost) in html or f"{initial_cost:.4f}" in html
    assert str(result.cost) in html or f"{result.cost:.4f}" in html
    assert "Improvement" in html


def test_integration_full_pipeline_three_tools(tmp_path):
    """End-to-end flow works with three tools."""
    config_path = tmp_path / "three_tools.yaml"
    data = {
        "workspace": {
            "x_min": 0.0,
            "x_max": 3.0,
            "y_min": 0.0,
            "y_max": 3.0,
            "z_min": 0.0,
            "z_max": 2.0,
            "reach_radius": 2.0,
            "min_separation": 0.3,
        },
        "worker_reference": {"x": 0.0, "y": 0.0, "z": 1.0},
        "tools": [
            {"name": "A", "weight_kg": 1.0, "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5}},
            {"name": "B", "weight_kg": 0.5, "initial_position": {"x": 1.5, "y": 1.5, "z": 1.5}},
            {"name": "C", "weight_kg": 0.8, "initial_position": {"x": 2.5, "y": 2.5, "z": 1.0}},
        ],
    }
    import yaml
    config_path.write_text(yaml.dump(data), encoding="utf-8")

    config = load_config(str(config_path))

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
    result = optimize(config, random_seed=123, max_iterations=500)

    assert result.cost <= initial_cost

    ws = config.workspace
    for tool in result.layout:
        assert ws.x_min <= tool["x"] <= ws.x_max
        assert ws.y_min <= tool["y"] <= ws.y_max
        assert ws.z_min <= tool["z"] <= ws.z_max

    positions = [(t["x"], t["y"], t["z"]) for t in result.layout]
    n = len(positions)
    for i in range(n):
        for j in range(i + 1, n):
            dist = math.sqrt(
                (positions[i][0] - positions[j][0]) ** 2
                + (positions[i][1] - positions[j][1]) ** 2
                + (positions[i][2] - positions[j][2]) ** 2
            )
            assert dist >= ws.min_separation

    output_path = tmp_path / "three_tools_comparison.html"
    render_comparison(
        initial_layout,
        result.layout,
        config.worker_reference,
        initial_cost,
        result.cost,
        str(output_path),
    )

    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "A" in html
    assert "B" in html
    assert "C" in html
