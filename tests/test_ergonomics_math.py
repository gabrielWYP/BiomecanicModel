"""
Tests de propiedad y ejemplos para ergonomics_math.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from hypothesis import given, settings
from hypothesis import strategies as st

from src.ergonomics_math import tool_fatigue_cost, total_fatigue_cost


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
