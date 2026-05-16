# Plan de Implementación: Optimizador Ergonómico de Layouts 3D

## Visión General

Implementación incremental en Python de un sistema CLI que calcula y optimiza la disposición espacial de herramientas industriales para minimizar la fatiga física. Los módulos se construyen en orden de dependencia: core biomecánico → cargador de configuración → optimizador → visualizador → CLI.

## Tareas

- [x] 1. Configurar estructura del proyecto y dependencias
  - Crear directorios `src/`, `tests/`, `output/`
  - Crear `requirements.txt` con `scipy`, `plotly`, `pyyaml`, `pytest`, `hypothesis`
  - Crear `conftest.py` en `tests/` con perfiles de Hypothesis (`ci` con `max_examples=200`, `dev` con `max_examples=50`)
  - Crear `config.yaml` de ejemplo con el esquema definido en el diseño (2 herramientas, workspace 2x2x2)
  - _Requisitos: 3.1, 8.1_

- [ ] 2. Implementar el core biomecánico (`ergonomics_math.py`)
  - [x] 2.1 Implementar `euclidean_distance`, `power_zone_penalty` y `tool_fatigue_cost`
    - `euclidean_distance(pos_a, pos_b)` → distancia euclidiana 3D
    - `power_zone_penalty(z, z_min=0.8, z_max=1.2)` → 0.0 si z ∈ [z_min, z_max], desviación absoluta al límite más cercano si no
    - `tool_fatigue_cost(x, y, z, weight_kg, worker_ref, z_min, z_max)` → distancia * weight_kg + power_zone_penalty; lanza `ValueError` si weight_kg ≤ 0 o coordenada no finita
    - _Requisitos: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [ ] 2.2 Escribir test de propiedad P1: No negatividad del costo de fatiga
    - **Propiedad 1: No negatividad del costo de fatiga**
    - **Valida: Requisitos 1.4, 2.2, 9.1**

  - [ ] 2.3 Escribir test de propiedad P2: Penalización de Power Zone
    - **Propiedad 2: Penalización de Power Zone**
    - **Valida: Requisitos 1.2**

  - [ ] 2.4 Escribir test de propiedad P3: Linealidad del costo por peso
    - **Propiedad 3: Linealidad del costo por peso**
    - **Valida: Requisitos 1.3**

  - [ ] 2.5 Escribir test de propiedad P5: Rechazo de inputs inválidos
    - **Propiedad 5: Rechazo de inputs inválidos**
    - **Valida: Requisitos 1.5, 1.6**

  - [ ] 2.6 Escribir test de propiedad P11: Optimalidad de la Power Zone
    - **Propiedad 11: Optimalidad de la Power Zone**
    - **Valida: Requisitos 9.7**

  - [ ] 2.7 Implementar `total_fatigue_cost` y `check_separation_constraints`
    - `total_fatigue_cost(layout, worker_ref, z_min, z_max)` → suma de costos individuales; lanza `ValueError` si layout vacío
    - `check_separation_constraints(layout, min_separation)` → `True` si todas las distancias entre pares ≥ min_separation
    - _Requisitos: 2.1, 2.2, 2.3, 2.4, 5.2_

  - [ ] 2.8 Escribir test de propiedad P4: Invarianza al orden del layout
    - **Propiedad 4: Invarianza al orden del layout**
    - **Valida: Requisitos 2.1, 9.6**

  - [ ] 2.9 Escribir test de propiedad P6: Correctitud de `check_separation_constraints`
    - **Propiedad 6: Correctitud de check_separation_constraints**
    - **Valida: Requisitos 5.2**

- [ ] 3. Checkpoint — Verificar que todos los tests del core biomecánico pasan
  - Ejecutar `pytest tests/test_ergonomics_math.py -v`
  - Asegurarse de que todas las propiedades y ejemplos pasan; consultar al usuario si surgen dudas.

- [ ] 4. Implementar el cargador de configuración (`config_loader.py`)
  - [ ] 4.1 Definir dataclasses `ToolConfig`, `WorkspaceConfig` y `Config`
    - Campos exactos según el diseño
    - _Requisitos: 3.2_

  - [ ] 4.2 Implementar `load_config(path)`
    - Leer YAML con `pyyaml`
    - Validar presencia y tipos de todos los campos obligatorios; lanzar `FileNotFoundError` o `ValueError` según corresponda
    - Emitir advertencia en consola si coordenadas iniciales están fuera de bounds (no lanzar excepción)
    - _Requisitos: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 4.3 Escribir tests de ejemplo para `config_loader`
    - Carga de YAML válido, campos faltantes, tipos incorrectos, archivo inexistente, peso ≤ 0, coordenadas fuera de bounds (advertencia)
    - _Requisitos: 3.3, 3.4, 3.5, 3.6_

- [ ] 5. Implementar el optimizador (`optimizer.py`)
  - [ ] 5.1 Definir `OptimizationResult` y la función objetivo interna `_objective`
    - `OptimizationResult`: dataclass con `layout: list[dict]`, `cost: float`, `converged: bool`
    - `_objective(x_flat, ...)`: construye layout desde vector plano, calcula `total_fatigue_cost`, suma penalizaciones por colisión y por exceso de radio de alcance
    - _Requisitos: 4.1, 4.2, 4.3, 4.4, 5.1_

  - [ ] 5.2 Implementar `optimize(config, random_seed, max_iterations)`
    - Usar `scipy.optimize.differential_evolution` con `bounds` del workspace y `seed=random_seed`
    - Emitir advertencia en consola si no converge; retornar siempre el mejor resultado encontrado
    - Convertir vector plano resultado a `list[dict]` con `name`, `x`, `y`, `z`, `weight_kg`
    - _Requisitos: 4.1, 4.2, 4.5, 4.6, 4.7, 4.8_

  - [ ] 5.3 Escribir test de propiedad P7: Bounds del resultado del optimizador
    - **Propiedad 7: Bounds del resultado del optimizador**
    - **Valida: Requisitos 4.2, 9.3**

  - [ ] 5.4 Escribir test de propiedad P8: Separación en el resultado del optimizador
    - **Propiedad 8: Separación en el resultado del optimizador**
    - **Valida: Requisitos 4.3, 5.1, 9.2**

  - [ ] 5.5 Escribir test de propiedad P9: Mejora monotónica del optimizador
    - **Propiedad 9: Mejora monotónica del optimizador**
    - **Valida: Requisitos 4.1, 9.4**

  - [ ] 5.6 Escribir test de propiedad P10: Idempotencia del optimizador
    - **Propiedad 10: Idempotencia del optimizador**
    - **Valida: Requisitos 9.5**

- [ ] 6. Checkpoint — Verificar que todos los tests del optimizador pasan
  - Ejecutar `pytest tests/test_optimizer.py -v`
  - Asegurarse de que todas las propiedades pasan con configuraciones pequeñas (2-3 herramientas); consultar al usuario si surgen dudas.

- [ ] 7. Implementar el visualizador (`visualizer.py`)
  - [ ] 7.1 Implementar `render_layout`
    - Gráfico de dispersión 3D con Plotly; cada herramienta como punto con etiqueta de nombre
    - Diferenciar visualmente herramientas dentro/fuera de Power Zone con colores distintos
    - Renderizar `worker_reference` como marcador diferenciado
    - Incluir planos semitransparentes en Z = 0.8 m y Z = 1.2 m
    - Mostrar costo de fatiga total en el título
    - Exportar HTML autocontenido a `output_path`
    - Lanzar `ValueError` si layout vacío
    - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ] 7.2 Implementar `render_comparison`
    - Renderizar layout inicial y optimizado en el mismo gráfico con trazas diferenciadas por color y leyenda
    - Mostrar en el título: costo inicial, costo optimizado y porcentaje de mejora
    - _Requisitos: 7.1, 7.2, 7.3_

  - [ ] 7.3 Escribir test de propiedad P12: Contenido del HTML de visualización
    - **Propiedad 12: Contenido del HTML de visualización**
    - **Valida: Requisitos 6.1, 6.7**

  - [ ] 7.4 Escribir tests de ejemplo para `visualizer`
    - Layout vacío lanza `ValueError`, HTML generado contiene nombres de herramientas, render_comparison incluye ambos layouts
    - _Requisitos: 6.6, 7.1, 7.3_

- [ ] 8. Implementar el punto de entrada CLI (`main.py`)
  - [ ] 8.1 Configurar `argparse` con argumentos `config_path` (obligatorio), `--output` (default `output/layout_optimizado.html`) y `--seed` (entero opcional)
    - _Requisitos: 8.1, 8.4, 8.5_

  - [ ] 8.2 Implementar la secuencia principal y manejo de errores
    - Secuencia: `load_config` → `total_fatigue_cost(inicial)` → `optimize` → `render_comparison`
    - Imprimir costo inicial, costo optimizado y porcentaje de mejora en consola
    - Capturar `FileNotFoundError`, `ValueError` y excepciones inesperadas; imprimir en `stderr` y retornar código 1
    - Retornar código 0 en éxito
    - _Requisitos: 8.2, 8.3, 8.6, 8.7_

  - [ ] 8.3 Escribir tests de ejemplo para `main.py`
    - CLI retorna código 0 en ejecución exitosa con `config.yaml` válido
    - CLI retorna código 1 con archivo inexistente o config inválida
    - _Requisitos: 8.6, 8.7_

- [ ] 9. Tests de integración end-to-end
  - [ ] 9.1 Escribir tests de integración en `test_integration.py`
    - Flujo completo: `load_config` → `total_fatigue_cost` → `optimize` → `render_comparison` → verificar HTML generado
    - Verificar que el costo optimizado ≤ costo inicial con el `config.yaml` de ejemplo
    - _Requisitos: 8.2, 4.1, 6.5_

- [ ] 10. Checkpoint final — Verificar que toda la suite de tests pasa
  - Ejecutar `pytest tests/ -v`
  - Asegurarse de que todos los tests pasan; consultar al usuario si surgen dudas.

## Notas

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Los tests de propiedad del optimizador (P7–P10) deben usar configuraciones pequeñas (2-3 herramientas) y pocas iteraciones para mantener tiempos razonables
- Cada tarea referencia requisitos específicos para trazabilidad completa
- Los checkpoints garantizan validación incremental antes de avanzar al siguiente módulo
