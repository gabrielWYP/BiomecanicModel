"""
Config loader with Pydantic models for the ergonomic layout optimizer.
"""

import warnings
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator


class WorkspaceConfig(BaseModel):
    """Workspace boundaries and constraints."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float
    reach_radius: float = Field(..., gt=0)
    min_separation: float = Field(..., gt=0)


class ToolConfig(BaseModel):
    """Tool configuration with name, weight, and initial position."""

    name: str
    weight_kg: float = Field(..., gt=0)
    initial_position: tuple[float, float, float]

    @model_validator(mode="after")
    def _check_weight_positive(self) -> "ToolConfig":
        if self.weight_kg <= 0:
            raise ValueError(
                f"Tool '{self.name}' weight must be positive, got {self.weight_kg}"
            )
        return self


class _RawToolConfig(BaseModel):
    """Internal tool config that accepts dict from YAML."""

    name: str
    weight_kg: float = Field(..., gt=0)
    initial_position: dict[str, float]

    @model_validator(mode="after")
    def _check_weight_positive(self) -> "_RawToolConfig":
        if self.weight_kg <= 0:
            raise ValueError(
                f"Tool '{self.name}' weight must be positive, got {self.weight_kg}"
            )
        return self


class Config(BaseModel):
    """Top-level configuration model."""

    workspace: WorkspaceConfig
    worker_reference: tuple[float, float, float]
    tools: list[ToolConfig]


class _RawConfig(BaseModel):
    """Internal raw config for validation before conversion."""

    workspace: WorkspaceConfig
    worker_reference: dict[str, float]
    tools: list[_RawToolConfig]


def load_config(path: str) -> Config:
    """Load and validate a YAML configuration file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        Config: Validated configuration object.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML is invalid or required fields are missing/wrong.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    try:
        with file_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"Configuration file must contain a top-level mapping, got {type(raw).__name__}")

    # Validate using Pydantic
    try:
        validated = _RawConfig(**raw)
    except Exception as exc:
        # Re-raise as ValueError with a clear message
        raise ValueError(f"Configuration validation failed: {exc}") from exc

    # Convert worker_reference to tuple for easier downstream use
    worker_ref = (
        validated.worker_reference["x"],
        validated.worker_reference["y"],
        validated.worker_reference["z"],
    )

    # Convert tool initial_position dicts to tuples
    tools_with_tuple_pos = []
    for tool in validated.tools:
        pos = tool.initial_position
        pos_tuple = (pos["x"], pos["y"], pos["z"])

        # Check bounds and warn
        ws = validated.workspace
        if (
            pos_tuple[0] < ws.x_min
            or pos_tuple[0] > ws.x_max
            or pos_tuple[1] < ws.y_min
            or pos_tuple[1] > ws.y_max
            or pos_tuple[2] < ws.z_min
            or pos_tuple[2] > ws.z_max
        ):
            warnings.warn(
                f"Tool '{tool.name}' initial position {pos_tuple} is out of bounds "
                f"[x: {ws.x_min}-{ws.x_max}, y: {ws.y_min}-{ws.y_max}, z: {ws.z_min}-{ws.z_max}]",
                stacklevel=2,
            )

        tools_with_tuple_pos.append(
            ToolConfig(
                name=tool.name,
                weight_kg=tool.weight_kg,
                initial_position=pos_tuple,
            )
        )

    return Config(
        workspace=validated.workspace,
        worker_reference=worker_ref,
        tools=tools_with_tuple_pos,
    )
