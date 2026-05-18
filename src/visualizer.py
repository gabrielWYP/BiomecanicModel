"""
Visualizer module using Plotly for 3D ergonomic layout rendering.
"""

import plotly.graph_objects as go


def render_layout(layout, worker_ref, fatigue_cost, output_path, z_min=0.8, z_max=1.2):
    """Generate a self-contained HTML 3D scatter plot of a tool layout.

    Args:
        layout: list of dicts with keys name, x, y, z, weight_kg.
        worker_ref: (x, y, z) tuple for the worker reference point.
        fatigue_cost: float to include in the plot title.
        output_path: path where the HTML file will be written.
        z_min: lower bound of the Power Zone (default 0.8).
        z_max: upper bound of the Power Zone (default 1.2).

    Raises:
        ValueError: if layout is empty.
    """
    if not layout:
        raise ValueError("Layout cannot be empty")

    fig = go.Figure()

    # Separate tools by Power Zone membership
    inside = [t for t in layout if z_min <= t["z"] <= z_max]
    outside = [t for t in layout if t["z"] < z_min or t["z"] > z_max]

    def _scatter(data, color, name):
        if not data:
            return
        fig.add_trace(
            go.Scatter3d(
                x=[t["x"] for t in data],
                y=[t["y"] for t in data],
                z=[t["z"] for t in data],
                mode="markers+text",
                text=[t["name"] for t in data],
                textposition="top center",
                marker=dict(size=6, color=color),
                name=name,
            )
        )

    _scatter(inside, "green", "Inside Power Zone")
    _scatter(outside, "red", "Outside Power Zone")

    # Worker reference point
    fig.add_trace(
        go.Scatter3d(
            x=[worker_ref[0]],
            y=[worker_ref[1]],
            z=[worker_ref[2]],
            mode="markers",
            marker=dict(size=10, color="blue", symbol="diamond"),
            name="Worker",
        )
    )

    # Semi-transparent planes at z_min and z_max
    for z_plane in (z_min, z_max):
        fig.add_trace(
            go.Mesh3d(
                x=[-10, 10, 10, -10],
                y=[-10, -10, 10, 10],
                z=[z_plane, z_plane, z_plane, z_plane],
                color="lightblue",
                opacity=0.2,
                name=f"Z={z_plane}m",
                showlegend=True,
            )
        )

    fig.update_layout(
        title=f"Tool Layout — Total Fatigue Cost: {fatigue_cost:.4f}",
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Z (m)",
        ),
    )

    fig.write_html(output_path, include_plotlyjs="cdn")


def render_comparison(
    initial_layout,
    optimized_layout,
    worker_ref,
    initial_cost,
    optimized_cost,
    output_path,
    z_min=0.8,
    z_max=1.2,
):
    """Render both initial and optimized layouts in a single 3D plot.

    Args:
        initial_layout: original tool layout.
        optimized_layout: optimized tool layout.
        worker_ref: (x, y, z) tuple for the worker reference point.
        initial_cost: float cost of the initial layout.
        optimized_cost: float cost of the optimized layout.
        output_path: path where the HTML file will be written.
        z_min: lower bound of the Power Zone (default 0.8).
        z_max: upper bound of the Power Zone (default 1.2).

    Raises:
        ValueError: if either layout is empty.
    """
    if not initial_layout:
        raise ValueError("Initial layout cannot be empty")
    if not optimized_layout:
        raise ValueError("Optimized layout cannot be empty")

    fig = go.Figure()

    # Initial layout trace
    fig.add_trace(
        go.Scatter3d(
            x=[t["x"] for t in initial_layout],
            y=[t["y"] for t in initial_layout],
            z=[t["z"] for t in initial_layout],
            mode="markers+text",
            text=[t["name"] for t in initial_layout],
            textposition="top center",
            marker=dict(size=6, color="orange"),
            name="Initial Layout",
        )
    )

    # Optimized layout trace
    fig.add_trace(
        go.Scatter3d(
            x=[t["x"] for t in optimized_layout],
            y=[t["y"] for t in optimized_layout],
            z=[t["z"] for t in optimized_layout],
            mode="markers+text",
            text=[t["name"] for t in optimized_layout],
            textposition="top center",
            marker=dict(size=6, color="green"),
            name="Optimized Layout",
        )
    )

    # Worker reference point
    fig.add_trace(
        go.Scatter3d(
            x=[worker_ref[0]],
            y=[worker_ref[1]],
            z=[worker_ref[2]],
            mode="markers",
            marker=dict(size=10, color="blue", symbol="diamond"),
            name="Worker",
        )
    )

    # Semi-transparent planes at z_min and z_max
    for z_plane in (z_min, z_max):
        fig.add_trace(
            go.Mesh3d(
                x=[-10, 10, 10, -10],
                y=[-10, -10, 10, 10],
                z=[z_plane, z_plane, z_plane, z_plane],
                color="lightblue",
                opacity=0.2,
                name=f"Z={z_plane}m",
                showlegend=True,
            )
        )

    improvement = 0.0
    if initial_cost > 0:
        improvement = ((initial_cost - optimized_cost) / initial_cost) * 100

    fig.update_layout(
        title=(
            f"Layout Comparison — Initial: {initial_cost:.4f} | "
            f"Optimized: {optimized_cost:.4f} | "
            f"Improvement: {improvement:.1f}%"
        ),
        scene=dict(
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            zaxis_title="Z (m)",
        ),
    )

    fig.write_html(output_path, include_plotlyjs="cdn")
