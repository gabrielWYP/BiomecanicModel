"""
Tests de ejemplo para config_loader.py
"""

import math
import warnings
from pathlib import Path

import pytest
import yaml

from src.config_loader import Config, ToolConfig, WorkspaceConfig, load_config


# ============================================================================
# Task 3.1 / 3.2: Valid YAML loads correctly
# ============================================================================


def test_load_valid_config(tmp_path):
    """Valid YAML loads correctly into Config dataclass."""
    config_path = tmp_path / "valid_config.yaml"
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
        "tools": [
            {
                "name": "Llave inglesa",
                "weight_kg": 1.2,
                "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5},
            },
            {
                "name": "Destornillador",
                "weight_kg": 0.3,
                "initial_position": {"x": 1.0, "y": 0.5, "z": 1.0},
            },
        ],
    }
    config_path.write_text(yaml.dump(data))

    config = load_config(str(config_path))

    assert isinstance(config, Config)
    assert isinstance(config.workspace, WorkspaceConfig)
    assert config.workspace.x_min == 0.0
    assert config.workspace.x_max == 2.0
    assert config.workspace.reach_radius == 1.5
    assert config.workspace.min_separation == 0.2

    assert isinstance(config.worker_reference, tuple)
    assert config.worker_reference == (0.0, 0.0, 1.0)

    assert len(config.tools) == 2
    assert isinstance(config.tools[0], ToolConfig)
    assert config.tools[0].name == "Llave inglesa"
    assert config.tools[0].weight_kg == 1.2
    assert config.tools[0].initial_position == (0.5, 0.5, 0.5)

    assert config.tools[1].name == "Destornillador"
    assert config.tools[1].weight_kg == 0.3
    assert config.tools[1].initial_position == (1.0, 0.5, 1.0)


# ============================================================================
# Task 3.2: Missing file raises FileNotFoundError
# ============================================================================


def test_load_missing_file_raises():
    """Missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")


# ============================================================================
# Task 3.2: Missing fields raise ValueError
# ============================================================================


def test_load_missing_workspace_raises(tmp_path):
    """Missing workspace field raises ValueError."""
    config_path = tmp_path / "bad_config.yaml"
    data = {
        "worker_reference": {"x": 0.0, "y": 0.0, "z": 1.0},
        "tools": [
            {"name": "A", "weight_kg": 1.0, "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5}}
        ],
    }
    config_path.write_text(yaml.dump(data))

    with pytest.raises(ValueError):
        load_config(str(config_path))


def test_load_missing_tool_name_raises(tmp_path):
    """Missing tool name raises ValueError."""
    config_path = tmp_path / "bad_config.yaml"
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
        "tools": [
            {"weight_kg": 1.0, "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5}}
        ],
    }
    config_path.write_text(yaml.dump(data))

    with pytest.raises(ValueError):
        load_config(str(config_path))


# ============================================================================
# Task 3.2: Invalid types raise ValueError
# ============================================================================


def test_load_invalid_tool_weight_type_raises(tmp_path):
    """Invalid tool weight type raises ValueError."""
    config_path = tmp_path / "bad_config.yaml"
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
        "tools": [
            {
                "name": "A",
                "weight_kg": "heavy",
                "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5},
            }
        ],
    }
    config_path.write_text(yaml.dump(data))

    with pytest.raises(ValueError):
        load_config(str(config_path))


# ============================================================================
# Task 3.2: Weight <= 0 raises ValueError
# ============================================================================


def test_load_zero_weight_raises(tmp_path):
    """Tool weight = 0 raises ValueError."""
    config_path = tmp_path / "bad_config.yaml"
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
        "tools": [
            {
                "name": "A",
                "weight_kg": 0.0,
                "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5},
            }
        ],
    }
    config_path.write_text(yaml.dump(data))

    with pytest.raises(ValueError):
        load_config(str(config_path))


def test_load_negative_weight_raises(tmp_path):
    """Tool weight < 0 raises ValueError."""
    config_path = tmp_path / "bad_config.yaml"
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
        "tools": [
            {
                "name": "A",
                "weight_kg": -1.0,
                "initial_position": {"x": 0.5, "y": 0.5, "z": 0.5},
            }
        ],
    }
    config_path.write_text(yaml.dump(data))

    with pytest.raises(ValueError):
        load_config(str(config_path))


# ============================================================================
# Task 3.3: Out-of-bounds coordinates emit warning
# ============================================================================


def test_load_out_of_bounds_coords_warns(tmp_path):
    """Initial coordinates outside workspace bounds emit warnings.warn()."""
    config_path = tmp_path / "bad_config.yaml"
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
        "tools": [
            {
                "name": "A",
                "weight_kg": 1.0,
                "initial_position": {"x": 5.0, "y": 0.5, "z": 0.5},
            }
        ],
    }
    config_path.write_text(yaml.dump(data))

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        config = load_config(str(config_path))

        assert len(w) >= 1
        assert any("out of bounds" in str(warning.message).lower() for warning in w)
        assert config.tools[0].initial_position == (5.0, 0.5, 0.5)
