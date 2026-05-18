"""
Tests para visualizer.py
"""

import pytest

from src.visualizer import render_layout, render_comparison


# ============================================================================
# Task 5.1: render_layout
# ============================================================================


def test_render_layout_generates_html(tmp_path):
    """render_layout creates an HTML file containing tool names and cost."""
    layout = [
        {"name": "Llave inglesa", "x": 0.5, "y": 0.5, "z": 0.5, "weight_kg": 1.2},
        {"name": "Destornillador", "x": 1.0, "y": 0.5, "z": 1.0, "weight_kg": 0.3},
    ]
    worker_ref = (0.0, 0.0, 1.0)
    fatigue_cost = 1.2345
    output_path = tmp_path / "layout.html"

    render_layout(layout, worker_ref, fatigue_cost, str(output_path))

    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "Llave inglesa" in html
    assert "Destornillador" in html
    assert str(fatigue_cost) in html


def test_render_layout_single_tool(tmp_path):
    """render_layout works with a single tool and includes cost in title."""
    layout = [
        {"name": "Martillo", "x": 1.0, "y": 1.0, "z": 1.0, "weight_kg": 2.0},
    ]
    worker_ref = (0.0, 0.0, 1.0)
    fatigue_cost = 0.75
    output_path = tmp_path / "single.html"

    render_layout(layout, worker_ref, fatigue_cost, str(output_path))

    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "Martillo" in html
    assert str(fatigue_cost) in html


def test_render_layout_empty_raises():
    """Empty layout raises ValueError."""
    with pytest.raises(ValueError):
        render_layout([], (0.0, 0.0, 1.0), 0.0, "/tmp/fake.html")


# ============================================================================
# Task 5.2: render_comparison
# ============================================================================


def test_render_comparison_generates_html(tmp_path):
    """render_comparison creates an HTML file with both layouts and costs."""
    initial_layout = [
        {"name": "Llave inglesa", "x": 0.5, "y": 0.5, "z": 0.5, "weight_kg": 1.2},
        {"name": "Destornillador", "x": 1.0, "y": 0.5, "z": 1.0, "weight_kg": 0.3},
    ]
    optimized_layout = [
        {"name": "Llave inglesa", "x": 0.6, "y": 0.6, "z": 0.9, "weight_kg": 1.2},
        {"name": "Destornillador", "x": 1.1, "y": 0.6, "z": 1.1, "weight_kg": 0.3},
    ]
    worker_ref = (0.0, 0.0, 1.0)
    initial_cost = 1.5
    optimized_cost = 1.2
    output_path = tmp_path / "comparison.html"

    render_comparison(
        initial_layout,
        optimized_layout,
        worker_ref,
        initial_cost,
        optimized_cost,
        str(output_path),
    )

    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "Llave inglesa" in html
    assert "Destornillador" in html
    assert str(initial_cost) in html
    assert str(optimized_cost) in html


def test_render_comparison_improvement_percentage(tmp_path):
    """render_comparison title includes improvement percentage."""
    initial_layout = [
        {"name": "A", "x": 0.0, "y": 0.0, "z": 0.5, "weight_kg": 1.0},
    ]
    optimized_layout = [
        {"name": "A", "x": 0.0, "y": 0.0, "z": 1.0, "weight_kg": 1.0},
    ]
    output_path = tmp_path / "improvement.html"

    render_comparison(
        initial_layout,
        optimized_layout,
        (0.0, 0.0, 1.0),
        10.0,
        5.0,
        str(output_path),
    )

    html = output_path.read_text(encoding="utf-8")
    assert "Improvement" in html
    assert "50.0%" in html


def test_render_comparison_empty_initial_raises():
    """Empty initial layout raises ValueError."""
    with pytest.raises(ValueError):
        render_comparison(
            [],
            [{"name": "A", "x": 0.0, "y": 0.0, "z": 1.0, "weight_kg": 1.0}],
            (0.0, 0.0, 1.0),
            0.0,
            0.0,
            "/tmp/fake.html",
        )


def test_render_comparison_empty_optimized_raises():
    """Empty optimized layout raises ValueError."""
    with pytest.raises(ValueError):
        render_comparison(
            [{"name": "A", "x": 0.0, "y": 0.0, "z": 1.0, "weight_kg": 1.0}],
            [],
            (0.0, 0.0, 1.0),
            0.0,
            0.0,
            "/tmp/fake.html",
        )
