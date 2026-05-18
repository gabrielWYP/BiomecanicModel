# BiomecanicModel

Ergonomic layout optimizer that minimizes worker fatigue by repositioning tools in 3D space using biomechanical cost functions and differential evolution.

## What It Does

Given a set of tools with known weights and initial positions, this system finds the optimal 3D arrangement that minimizes cumulative fatigue for a worker. It accounts for:

- **Euclidean reach distance** — tools farther from the worker cost more energy
- **Weight penalty** — heavier tools amplify the distance cost
- **Power Zone enforcement** — tools outside the ergonomic height band (0.8m–1.2m) receive additive penalties
- **Collision avoidance** — soft penalties prevent tools from overlapping
- **Reach constraints** — tools must stay within the worker's reachable radius

The output is an interactive 3D HTML visualization comparing the original and optimized layouts.

## Architecture

```
config.yaml
    │
    ▼
┌────────────────┐     ┌──────────────────┐     ┌────────────────┐
│  config_loader │────▶│    optimizer     │────▶│   visualizer   │
│  (Pydantic)    │     │ (SciPy DE + soft │     │   (Plotly 3D)  │
└────────────────┘     │   penalties)     │     └────────────────┘
                       └──────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ ergonomics_math  │
                       │ (pure functions) │
                       └──────────────────┘
```

| Module | Responsibility |
|--------|---------------|
| `config_loader` | YAML parsing, Pydantic validation, out-of-bounds warnings |
| `ergonomics_math` | Pure fatigue cost functions — no I/O, no state |
| `optimizer` | Differential evolution with soft constraint penalties |
| `visualizer` | 3D scatter plots with Power Zone planes and before/after comparison |
| `main` | CLI entry point orchestrating the full pipeline |

## Quick Start

```bash
# Clone
git clone git@github.com:gabrielWYP/BiomecanicModel.git
cd BiomecanicModel

# Install dependencies
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run optimization
python -m src.main config.yaml --output output/result.html
```

The optimizer prints cost reduction stats and writes an interactive HTML file:

```
Initial cost:   1.3416
Optimized cost: 0.6200
Improvement:    53.8%
```

## Configuration

All parameters live in a single `config.yaml`:

```yaml
workspace:
  x_min: 0.0
  x_max: 2.0
  y_min: 0.0
  y_max: 2.0
  z_min: 0.0
  z_max: 2.0
  reach_radius: 1.5
  min_separation: 0.2

worker_reference:
  x: 0.0
  y: 0.0
  z: 1.0

tools:
  - name: "Llave inglesa"
    weight_kg: 1.2
    initial_position: { x: 0.5, y: 0.5, z: 0.5 }
  - name: "Destornillador"
    weight_kg: 0.3
    initial_position: { x: 1.0, y: 0.5, z: 1.0 }
```

| Parameter | Description |
|-----------|-------------|
| `workspace.*` | 3D bounding box for valid tool positions |
| `reach_radius` | Maximum distance from the worker to any tool |
| `min_separation` | Minimum allowed distance between any two tools |
| `worker_reference` | Worker's torso center position (optimization target) |
| `tools[].weight_kg` | Tool mass — amplifies reach cost |
| `tools[].initial_position` | Starting coordinates before optimization |

## CLI Options

```
usage: python -m src.main [-h] [--output OUTPUT] [--seed SEED] config_path

positional arguments:
  config_path       Path to the YAML configuration file

options:
  --output OUTPUT   Path for the output HTML visualization
                    (default: output/layout_optimizado.html)
  --seed SEED       Random seed for reproducible optimization
```

## Testing

```bash
pytest
```

The test suite covers:

- Config validation (valid/invalid YAML, missing fields, bounds warnings)
- Ergonomics math (distance, power zone, fatigue cost, separation checks)
- Optimizer convergence and constraint satisfaction
- Visualizer output generation
- End-to-end integration pipeline

Property-based tests via [Hypothesis](https://hypothesis.readthedocs.io/) validate math invariants across random inputs.

## Tech Stack

- **Python 3.11+**
- **SciPy** — differential evolution optimizer
- **Plotly** — interactive 3D visualization
- **Pydantic** — configuration validation
- **PyYAML** — config file parsing
- **pytest + Hypothesis** — testing

## License

Apache License 2.0 — see [LICENSE](LICENSE).
