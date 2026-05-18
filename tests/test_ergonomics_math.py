"""
Tests de propiedad y ejemplos para ergonomics_math.py
"""

import math
import random

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.ergonomics_math import (
    tool_fatigue_cost,
    total_fatigue_cost,
    check_separation_constraints,
    power_zone_penalty,
    _layout_dicts_to_tuples,
)


# Feature: ergonomic-layout-optimizer, Propiedad 1: No negatividad del costo de fatiga
# Validates: Requirements 1.4, 2.2, 9.1
@given(
    x=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    y=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    z=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    weight=st.floats(min_value=0.001, max_value=50.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200)
def test_fatigue_cost_non_negative(x, y, z, weight):
    """P1: tool_fatigue_cost debe retornar >= 0.0 para cualquier entrada válida."""
    cost = tool_fatigue_cost(x, y, z, weight, worker_ref=(0.0, 0.0, 1.0))
    assert cost >= 0.0


# Feature: ergonomic-layout-optimizer, Propiedad 1: No negatividad del costo total de fatiga
# Validates: Requirements 1.4, 2.2, 9.1
@given(
    tools=st.lists(
        st.tuples(
            st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0.001, max_value=50.0, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=10,
    )
)
@settings(max_examples=200)
def test_total_fatigue_cost_non_negative(tools):
    """P1: total_fatigue_cost debe retornar >= 0.0 para cualquier layout no vacío válido."""
    cost = total_fatigue_cost(tools, worker_ref=(0.0, 0.0, 1.0))
    assert cost >= 0.0


def test_layout_dicts_to_tuples_conversion():
    """_layout_dicts_to_tuples convierte lista de dicts a lista de tuplas."""
    dicts = [
        {"name": "A", "x": 1.0, "y": 2.0, "z": 0.9, "weight_kg": 3.0},
        {"name": "B", "x": 0.5, "y": 1.5, "z": 1.1, "weight_kg": 2.0},
    ]
    expected = [(1.0, 2.0, 0.9, 3.0), (0.5, 1.5, 1.1, 2.0)]
    assert _layout_dicts_to_tuples(dicts) == expected


def test_total_fatigue_cost_accepts_dict_layout():
    """total_fatigue_cost acepta layout como lista de dicts y da igual resultado que tuplas."""
    tuples = [(1.0, 2.0, 0.9, 3.0), (0.5, 1.5, 1.1, 2.0)]
    dicts = [
        {"name": "A", "x": 1.0, "y": 2.0, "z": 0.9, "weight_kg": 3.0},
        {"name": "B", "x": 0.5, "y": 1.5, "z": 1.1, "weight_kg": 2.0},
    ]
    worker_ref = (0.0, 0.0, 1.0)
    assert total_fatigue_cost(dicts, worker_ref) == total_fatigue_cost(tuples, worker_ref)


def test_check_separation_constraints_accepts_dict_layout():
    """check_separation_constraints acepta layout como lista de dicts."""
    tuples = [(0.0, 0.0, 1.0, 1.0), (1.0, 0.0, 1.0, 2.0)]
    dicts = [
        {"name": "A", "x": 0.0, "y": 0.0, "z": 1.0, "weight_kg": 1.0},
        {"name": "B", "x": 1.0, "y": 0.0, "z": 1.0, "weight_kg": 2.0},
    ]
    assert check_separation_constraints(dicts, min_separation=0.5) == check_separation_constraints(
        tuples, min_separation=0.5
    )


def test_layout_dicts_to_tuples_empty():
    """_layout_dicts_to_tuples con lista vacía retorna lista vacía."""
    assert _layout_dicts_to_tuples([]) == []


def test_total_fatigue_cost_empty_dict_layout_raises():
    """total_fatigue_cost con lista vacía de dicts lanza ValueError."""
    with pytest.raises(ValueError):
        total_fatigue_cost([], worker_ref=(0.0, 0.0, 1.0))


# Feature: ergonomic-layout-optimizer, Propiedad 2: Penalización de Power Zone
# Validates: Requirements 1.2
@given(
    z=st.floats(min_value=0.8, max_value=1.2, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200)
def test_power_zone_penalty_zero_inside(z):
    """P2: power_zone_penalty es 0.0 dentro de [0.8, 1.2]."""
    assert power_zone_penalty(z) == 0.0


@given(
    z=st.floats(min_value=-10.0, max_value=0.799999, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200)
def test_power_zone_penalty_below_zone(z):
    """P2: power_zone_penalty debajo de 0.8 retorna 0.8 - z."""
    assert power_zone_penalty(z) == 0.8 - z


@given(
    z=st.floats(min_value=1.200001, max_value=10.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200)
def test_power_zone_penalty_above_zone(z):
    """P2: power_zone_penalty arriba de 1.2 retorna z - 1.2."""
    assert power_zone_penalty(z) == z - 1.2


# Feature: ergonomic-layout-optimizer, Propiedad 3: Linealidad del costo por peso
# Validates: Requirements 1.3
@given(
    x=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    y=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    weight=st.floats(min_value=0.001, max_value=50.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200)
def test_tool_fatigue_cost_linearity_with_weight(x, y, weight):
    """P3: cost(2w) == 2 * cost(w) cuando Z está en Power Zone."""
    z = 1.0  # centro de la Power Zone
    worker_ref = (0.0, 0.0, 1.0)
    cost_w = tool_fatigue_cost(x, y, z, weight, worker_ref)
    cost_2w = tool_fatigue_cost(x, y, z, weight * 2, worker_ref)
    assert math.isclose(cost_2w, cost_w * 2, rel_tol=1e-9)


# Feature: ergonomic-layout-optimizer, Propiedad 4: Invarianza al orden del layout
# Validates: Requirements 2.1, 9.6
@given(
    tools=st.lists(
        st.tuples(
            st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0.001, max_value=50.0, allow_nan=False, allow_infinity=False),
        ),
        min_size=1,
        max_size=10,
    )
)
@settings(max_examples=200)
def test_total_fatigue_cost_order_invariant(tools):
    """P4: total_fatigue_cost da igual resultado independientemente del orden."""
    worker_ref = (0.0, 0.0, 1.0)
    original_cost = total_fatigue_cost(tools, worker_ref)
    shuffled = list(tools)
    random.shuffle(shuffled)
    shuffled_cost = total_fatigue_cost(shuffled, worker_ref)
    assert math.isclose(original_cost, shuffled_cost, rel_tol=1e-9)


# Feature: ergonomic-layout-optimizer, Propiedad 5: Rechazo de inputs inválidos
# Validates: Requirements 1.5, 1.6


def test_tool_fatigue_cost_rejects_zero_weight():
    """P5: weight=0 lanza ValueError."""
    with pytest.raises(ValueError):
        tool_fatigue_cost(1.0, 1.0, 1.0, 0.0, worker_ref=(0.0, 0.0, 1.0))


def test_tool_fatigue_cost_rejects_negative_weight():
    """P5: weight negativo lanza ValueError."""
    with pytest.raises(ValueError):
        tool_fatigue_cost(1.0, 1.0, 1.0, -1.0, worker_ref=(0.0, 0.0, 1.0))


def test_tool_fatigue_cost_rejects_nan_coordinate():
    """P5: coordenada NaN lanza ValueError."""
    with pytest.raises(ValueError):
        tool_fatigue_cost(float("nan"), 1.0, 1.0, 1.0, worker_ref=(0.0, 0.0, 1.0))


def test_tool_fatigue_cost_rejects_inf_coordinate():
    """P5: coordenada infinita lanza ValueError."""
    with pytest.raises(ValueError):
        tool_fatigue_cost(1.0, float("inf"), 1.0, 1.0, worker_ref=(0.0, 0.0, 1.0))


# Feature: ergonomic-layout-optimizer, Propiedad 6: Correctitud de separation constraints
# Validates: Requirements 5.2
@given(
    x1=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    y1=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    z1=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    x2=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    y2=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    z2=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    min_sep=st.floats(min_value=0.01, max_value=2.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200)
def test_check_separation_constraints_correctness(x1, y1, z1, x2, y2, z2, min_sep):
    """P6: check_separation_constraints retorna True sii todas las distancias >= min_separation."""
    from src.ergonomics_math import euclidean_distance
    layout = [(x1, y1, z1, 1.0), (x2, y2, z2, 2.0)]
    expected = euclidean_distance((x1, y1, z1), (x2, y2, z2)) >= min_sep
    result = check_separation_constraints(layout, min_sep)
    assert result == expected


# Feature: ergonomic-layout-optimizer, Propiedad 11: Optimalidad de la Power Zone
# Validates: Requirements 9.7
@given(
    x=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    y=st.floats(min_value=0.0, max_value=2.0, allow_nan=False, allow_infinity=False),
    z_out=st.one_of(
        st.floats(min_value=0.0, max_value=0.799999, allow_nan=False, allow_infinity=False),
        st.floats(min_value=1.200001, max_value=2.0, allow_nan=False, allow_infinity=False),
    ),
    weight=st.floats(min_value=0.001, max_value=50.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200)
def test_power_zone_optimal_cost(x, y, z_out, weight):
    """P11: costo en Z=1.0 es estrictamente menor que fuera de la Power Zone (mismos X, Y)."""
    worker_ref = (0.0, 0.0, 1.0)
    cost_center = tool_fatigue_cost(x, y, 1.0, weight, worker_ref)
    cost_outside = tool_fatigue_cost(x, y, z_out, weight, worker_ref)
    assert cost_center < cost_outside
