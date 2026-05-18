"""
Core biomecánico puro para el cálculo de fatiga ergonómica.
Módulo sin I/O, sin estado, sin importaciones de módulos del proyecto.
"""

import math
from typing import Iterable


def _layout_dicts_to_tuples(
    layout: Iterable[dict],
) -> list[tuple[float, float, float, float]]:
    """Convierte un layout de dicts al formato interno de tuplas (x, y, z, weight_kg).

    Cada dict debe contener las claves: x, y, z, weight_kg.
    La clave 'name' se ignora.
    """
    return [(d["x"], d["y"], d["z"], d["weight_kg"]) for d in layout]


def euclidean_distance(
    pos_a: tuple[float, float, float],
    pos_b: tuple[float, float, float],
) -> float:
    """Distancia euclidiana entre dos puntos 3D."""
    return math.sqrt(
        (pos_a[0] - pos_b[0]) ** 2
        + (pos_a[1] - pos_b[1]) ** 2
        + (pos_a[2] - pos_b[2]) ** 2
    )


def power_zone_penalty(
    z: float,
    z_min: float = 0.8,
    z_max: float = 1.2,
) -> float:
    """Penalización aditiva por desviación de la Power Zone.

    Retorna 0.0 si z está dentro del rango [z_min, z_max].
    Retorna la desviación absoluta al límite más cercano en caso contrario.
    """
    if z < z_min:
        return z_min - z
    if z > z_max:
        return z - z_max
    return 0.0


def tool_fatigue_cost(
    x: float,
    y: float,
    z: float,
    weight_kg: float,
    worker_ref: tuple[float, float, float],
    z_min: float = 0.8,
    z_max: float = 1.2,
) -> float:
    """Costo de fatiga de una herramienta individual.

    = euclidean_distance((x, y, z), worker_ref) * weight_kg + power_zone_penalty(z)

    Raises:
        ValueError: Si weight_kg <= 0.
        ValueError: Si alguna coordenada no es un número real finito.
    """
    if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
        raise ValueError(
            f"Las coordenadas deben ser números reales finitos, se recibió: x={x}, y={y}, z={z}"
        )
    if weight_kg <= 0:
        raise ValueError(f"El peso debe ser positivo, se recibió: {weight_kg}")

    dist = euclidean_distance((x, y, z), worker_ref)
    return dist * weight_kg + power_zone_penalty(z, z_min, z_max)


def total_fatigue_cost(
    layout: Iterable[tuple[float, float, float, float] | dict],
    worker_ref: tuple[float, float, float],
    z_min: float = 0.8,
    z_max: float = 1.2,
) -> float:
    """Suma de costos individuales de todas las herramientas.

    layout: iterable de (x, y, z, weight_kg) o dicts con claves x, y, z, weight_kg.

    Raises:
        ValueError: Si el layout está vacío.
    """
    items = list(layout)
    if not items:
        raise ValueError("El layout no puede estar vacío")
    if items and isinstance(items[0], dict):
        items = _layout_dicts_to_tuples(items)
    return sum(
        tool_fatigue_cost(x, y, z, w, worker_ref, z_min, z_max)
        for x, y, z, w in items
    )


def check_separation_constraints(
    layout: Iterable[tuple[float, float, float, float] | dict],
    min_separation: float,
) -> bool:
    """Retorna True si todas las distancias entre pares de herramientas
    son >= min_separation. Retorna False en caso contrario.

    layout: iterable de (x, y, z, weight_kg) o dicts con claves x, y, z, weight_kg.
    """
    items = list(layout)
    if items and isinstance(items[0], dict):
        items = _layout_dicts_to_tuples(items)
    positions = [(x, y, z) for x, y, z, *_ in items]
    n = len(positions)
    for i in range(n):
        for j in range(i + 1, n):
            if euclidean_distance(positions[i], positions[j]) < min_separation:
                return False
    return True
