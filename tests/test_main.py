"""
Tests para main.py (CLI)
"""

import sys
from io import StringIO
from pathlib import Path

import pytest
import yaml

from src.main import main


def _write_config(path, tools):
    """Helper to write a minimal config YAML."""
    data = {
        "workspace": {
            "x_min": 0.0,
            "x_max": 2.0,
            "y_min": 0.0,
            "y_max": 2.0,
            "z_min": 0.0,
            "z_max": 2.0,
            "reach_radius": 1.5,
            "min_separation": 0.2,
        },
        "worker_reference": {"x": 0.0, "y": 0.0, "z": 1.0},
        "tools": tools,
    }
    path.write_text(yaml.dump(data), encoding="utf-8")


# ============================================================================
# Task 6.4: CLI success path
# ============================================================================


def test_cli_valid_config(tmp_path, monkeypatch):
    """CLI returns 0 with valid config and creates default output."""
    config_path = tmp_path / "config.yaml"
    _write_config(
        config_path,
        [
            {"name": "A", "weight_kg": 1.0, "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5}},
            {"name": "B", "weight_kg": 0.5, "initial_position": {"x": 1.5, "y": 1.5, "z": 1.5}},
        ],
    )
    output_path = tmp_path / "output" / "layout_optimizado.html"
    monkeypatch.setattr(
        "sys.argv", ["src/main.py", str(config_path), "--output", str(output_path)]
    )

    captured_out = StringIO()
    captured_err = StringIO()
    monkeypatch.setattr(sys, "stdout", captured_out)
    monkeypatch.setattr(sys, "stderr", captured_err)

    code = main()

    assert code == 0
    assert output_path.exists()


def test_cli_default_output_path(tmp_path, monkeypatch):
    """Output file is created at the default path."""
    config_path = tmp_path / "config.yaml"
    _write_config(
        config_path,
        [
            {"name": "A", "weight_kg": 1.0, "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5}},
            {"name": "B", "weight_kg": 0.5, "initial_position": {"x": 1.5, "y": 1.5, "z": 1.5}},
        ],
    )
    default_output = tmp_path / "output" / "layout_optimizado.html"
    monkeypatch.setattr(
        "sys.argv", ["src/main.py", str(config_path), "--output", str(default_output)]
    )

    captured_out = StringIO()
    captured_err = StringIO()
    monkeypatch.setattr(sys, "stdout", captured_out)
    monkeypatch.setattr(sys, "stderr", captured_err)

    code = main()

    assert code == 0
    assert default_output.exists()


def test_cli_custom_output_path(tmp_path, monkeypatch):
    """Output file is created at a custom path via --output."""
    config_path = tmp_path / "config.yaml"
    _write_config(
        config_path,
        [
            {"name": "A", "weight_kg": 1.0, "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5}},
            {"name": "B", "weight_kg": 0.5, "initial_position": {"x": 1.5, "y": 1.5, "z": 1.5}},
        ],
    )
    custom_output = tmp_path / "custom.html"
    monkeypatch.setattr(
        "sys.argv", ["src/main.py", str(config_path), "--output", str(custom_output)]
    )

    captured_out = StringIO()
    captured_err = StringIO()
    monkeypatch.setattr(sys, "stdout", captured_out)
    monkeypatch.setattr(sys, "stderr", captured_err)

    code = main()

    assert code == 0
    assert custom_output.exists()


def test_cli_seed_argument(tmp_path, monkeypatch):
    """CLI accepts --seed and returns 0."""
    config_path = tmp_path / "config.yaml"
    _write_config(
        config_path,
        [
            {"name": "A", "weight_kg": 1.0, "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5}},
            {"name": "B", "weight_kg": 0.5, "initial_position": {"x": 1.5, "y": 1.5, "z": 1.5}},
        ],
    )
    output_path = tmp_path / "out.html"
    monkeypatch.setattr(
        "sys.argv",
        ["src/main.py", str(config_path), "--output", str(output_path), "--seed", "42"],
    )

    captured_err = StringIO()
    monkeypatch.setattr(sys, "stderr", captured_err)

    code = main()

    assert code == 0
    assert output_path.exists()


def test_cli_prints_costs(tmp_path, monkeypatch):
    """CLI prints initial cost, optimized cost, and improvement percentage."""
    config_path = tmp_path / "config.yaml"
    _write_config(
        config_path,
        [
            {"name": "A", "weight_kg": 1.0, "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5}},
            {"name": "B", "weight_kg": 0.5, "initial_position": {"x": 1.5, "y": 1.5, "z": 1.5}},
        ],
    )
    output_path = tmp_path / "out.html"
    monkeypatch.setattr(
        "sys.argv", ["src/main.py", str(config_path), "--output", str(output_path)]
    )

    captured_out = StringIO()
    captured_err = StringIO()
    monkeypatch.setattr(sys, "stdout", captured_out)
    monkeypatch.setattr(sys, "stderr", captured_err)

    code = main()

    assert code == 0
    out = captured_out.getvalue()
    assert "Initial cost:" in out
    assert "Optimized cost:" in out
    assert "Improvement:" in out


# ============================================================================
# Task 6.3: Error handling
# ============================================================================


def test_cli_missing_file(tmp_path, monkeypatch):
    """CLI returns 1 with missing config file."""
    missing = tmp_path / "missing.yaml"
    monkeypatch.setattr("sys.argv", ["src/main.py", str(missing)])

    captured_err = StringIO()
    monkeypatch.setattr(sys, "stderr", captured_err)

    code = main()

    assert code == 1
    assert "not found" in captured_err.getvalue().lower() or "missing" in captured_err.getvalue().lower()


def test_cli_invalid_config(tmp_path, monkeypatch):
    """CLI returns 1 with invalid config."""
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("not: valid\n", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["src/main.py", str(config_path)])

    captured_err = StringIO()
    monkeypatch.setattr(sys, "stderr", captured_err)

    code = main()

    assert code == 1
