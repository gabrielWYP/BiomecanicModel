# Documento de Requisitos

## Introducción

El **Optimizador Ergonómico de Layouts 3D** es un sistema de software desarrollado en Python puro para minimizar la fatiga física de obreros industriales al interactuar con herramientas en una planta de manufactura. El sistema calcula un índice de costo de fatiga basado en coordenadas espaciales XYZ, pesos de herramientas y penalizaciones biomecánicas, y aplica métodos metaheurísticos clásicos para encontrar la disposición óptima de herramientas dentro de restricciones físicas reales. El resultado se visualiza como un gráfico 3D interactivo en el navegador.

El proyecto está estructurado en tres módulos con separación estricta de responsabilidades: cálculo biomecánico puro, optimización y visualización.

---

## Glosario

- **Layout**: Matriz de coordenadas XYZ que describe la posición de cada herramienta en el espacio de trabajo.
- **Power Zone**: Rango de altura Z entre 0.8 m y 1.2 m considerado ergonómicamente óptimo para manipulación de herramientas.
- **Costo de Fatiga**: Valor escalar no negativo que cuantifica el esfuerzo físico acumulado del obrero para alcanzar y operar todas las herramientas en un layout dado.
- **Herramienta**: Objeto físico con peso conocido (kg) y una posición XYZ asignable dentro del espacio de trabajo.
- **Espacio de Trabajo**: Volumen tridimensional delimitado dentro del cual se ubican las herramientas, definido por coordenadas mínimas y máximas en X, Y y Z.
- **Radio de Alcance**: Distancia máxima (m) desde el punto de referencia del obrero hasta la cual puede alcanzar una herramienta sin desplazarse.
- **Colisión**: Condición en la que dos herramientas ocupan posiciones cuya distancia euclidiana es menor al radio mínimo de separación permitido.
- **Core Biomecánico**: Módulo `ergonomics_math.py` que contiene funciones matemáticas puras para el cálculo de fatiga.
- **Optimizador**: Módulo `optimizer.py` que ejecuta la búsqueda metaheurística del layout óptimo.
- **Visualizador**: Módulo `visualizer.py` que genera la representación gráfica 3D del layout.
- **Config**: Archivo de configuración (`config.yaml`) que define herramientas, pesos, coordenadas iniciales y parámetros del espacio de trabajo.

---

## Requisitos

### Requisito 1: Cálculo del Costo de Fatiga por Herramienta

**User Story:** Como investigador de ergonomía industrial, quiero calcular el costo de fatiga individual de cada herramienta según su posición y peso, para cuantificar el esfuerzo físico del obrero de forma objetiva.

#### Criterios de Aceptación

1. THE Core_Biomecánico SHALL calcular la distancia euclidiana entre la posición XYZ de una herramienta y el punto de referencia del obrero (origen del espacio de trabajo).
2. WHEN la coordenada Z de una herramienta es menor a 0.8 m o mayor a 1.2 m, THE Core_Biomecánico SHALL aplicar una penalización aditiva proporcional a la desviación absoluta respecto al límite más cercano de la Power Zone.
3. THE Core_Biomecánico SHALL ponderar el costo de fatiga de cada herramienta multiplicando la distancia euclidiana por el peso de la herramienta en kilogramos.
4. THE Core_Biomecánico SHALL retornar un valor escalar de tipo `float` mayor o igual a cero para cualquier combinación válida de coordenadas XYZ y peso positivo.
5. IF el peso de una herramienta es menor o igual a cero, THEN THE Core_Biomecánico SHALL lanzar una excepción de tipo `ValueError` con un mensaje descriptivo.
6. IF alguna coordenada XYZ recibida no es un número real finito, THEN THE Core_Biomecánico SHALL lanzar una excepción de tipo `ValueError` con un mensaje descriptivo.

---

### Requisito 2: Cálculo del Costo de Fatiga Total del Layout

**User Story:** Como investigador de ergonomía industrial, quiero obtener un único valor escalar que represente el costo de fatiga total del layout completo, para usarlo como función objetivo en la optimización.

#### Criterios de Aceptación

1. THE Core_Biomecánico SHALL calcular el costo de fatiga total como la suma de los costos individuales de todas las herramientas del layout.
2. WHEN el layout contiene al menos una herramienta, THE Core_Biomecánico SHALL retornar un valor escalar de tipo `float` mayor o igual a cero.
3. IF el layout está vacío (sin herramientas), THEN THE Core_Biomecánico SHALL lanzar una excepción de tipo `ValueError` con un mensaje descriptivo.
4. THE Core_Biomecánico SHALL aceptar el layout como una estructura iterable de tuplas `(x, y, z, peso)` para mantener independencia de representación.

---

### Requisito 3: Carga y Validación de la Configuración

**User Story:** Como usuario del sistema, quiero cargar la configuración inicial desde un archivo YAML, para definir las herramientas, sus pesos y los parámetros del espacio de trabajo sin modificar el código fuente.

#### Criterios de Aceptación

1. THE Sistema SHALL leer la configuración desde un archivo `config.yaml` cuya ruta se especifica como argumento en tiempo de ejecución.
2. THE Sistema SHALL validar que el archivo `config.yaml` contiene los campos obligatorios: `workspace` (con subfields `x_min`, `x_max`, `y_min`, `y_max`, `z_min`, `z_max`, `reach_radius`, `min_separation`), `worker_reference` (con subfields `x`, `y`, `z`) y `tools` (lista con al menos un elemento, cada uno con `name`, `weight_kg` y `initial_position` con subfields `x`, `y`, `z`).
3. IF el archivo `config.yaml` no existe en la ruta especificada, THEN THE Sistema SHALL lanzar una excepción de tipo `FileNotFoundError` con la ruta indicada.
4. IF algún campo obligatorio está ausente o tiene un tipo de dato incorrecto, THEN THE Sistema SHALL lanzar una excepción de tipo `ValueError` enumerando los campos inválidos.
5. IF el peso de alguna herramienta en la configuración es menor o igual a cero, THEN THE Sistema SHALL lanzar una excepción de tipo `ValueError` identificando la herramienta afectada.
6. IF las coordenadas iniciales de alguna herramienta están fuera de los límites del `workspace`, THEN THE Sistema SHALL emitir una advertencia en consola e igualmente cargar la configuración para permitir que el Optimizador corrija la posición.

---

### Requisito 4: Optimización del Layout por Métodos Metaheurísticos

**User Story:** Como investigador de ergonomía industrial, quiero que el sistema encuentre automáticamente el layout de herramientas que minimice el costo de fatiga total, para obtener una recomendación objetiva de disposición.

#### Criterios de Aceptación

1. THE Optimizador SHALL minimizar la función de costo de fatiga total provista por el Core_Biomecánico usando exclusivamente métodos heurísticos o metaheurísticos clásicos (algoritmos evolutivos, optimización diferencial, o métodos de gradiente libre de `scipy.optimize`).
2. THE Optimizador SHALL respetar los límites del espacio de trabajo definidos en la Config como restricciones de caja (`bounds`) durante toda la búsqueda.
3. WHEN la distancia euclidiana entre dos herramientas en el layout resultante es menor al `min_separation` definido en la Config, THE Optimizador SHALL tratar dicha configuración como infactible aplicando una penalización al costo de fatiga.
4. WHEN la distancia euclidiana entre una herramienta y el `worker_reference` supera el `reach_radius` definido en la Config, THE Optimizador SHALL tratar dicha configuración como infactible aplicando una penalización al costo de fatiga.
5. THE Optimizador SHALL retornar el layout óptimo como una lista de diccionarios con campos `name`, `x`, `y`, `z` y `weight_kg`.
6. THE Optimizador SHALL retornar el valor del costo de fatiga mínimo encontrado como un `float`.
7. IF el Optimizador no converge dentro del número máximo de iteraciones configurado, THEN THE Optimizador SHALL retornar el mejor resultado encontrado hasta ese momento junto con una advertencia en consola.
8. THE Optimizador SHALL aceptar una semilla aleatoria (`random_seed`) como parámetro opcional para garantizar reproducibilidad de resultados.

---

### Requisito 5: Restricción de No Colisión entre Herramientas

**User Story:** Como ingeniero industrial, quiero que el layout optimizado no coloque dos herramientas en posiciones físicamente imposibles, para que los resultados sean aplicables en la planta real.

#### Criterios de Aceptación

1. THE Optimizador SHALL garantizar que en el layout final, la distancia euclidiana entre cualquier par de herramientas sea mayor o igual al `min_separation` definido en la Config.
2. THE Core_Biomecánico SHALL proveer una función que, dado un layout, retorne `True` si todas las restricciones de separación se cumplen y `False` en caso contrario.
3. WHEN el layout final viola alguna restricción de separación, THE Optimizador SHALL registrar en consola qué par de herramientas viola la restricción y por cuántos metros.

---

### Requisito 6: Visualización 3D del Layout Optimizado

**User Story:** Como investigador de ergonomía industrial, quiero visualizar el layout optimizado en un gráfico 3D interactivo, para comunicar los resultados de forma clara en mi tesis.

#### Criterios de Aceptación

1. THE Visualizador SHALL generar un gráfico de dispersión 3D usando Plotly donde cada herramienta se representa como un punto con su nombre como etiqueta.
2. THE Visualizador SHALL diferenciar visualmente las herramientas dentro de la Power Zone (Z entre 0.8 m y 1.2 m) de las que están fuera, usando colores distintos.
3. THE Visualizador SHALL renderizar el punto de referencia del obrero (`worker_reference`) como un marcador diferenciado en el gráfico.
4. THE Visualizador SHALL incluir en el gráfico planos semitransparentes que delimiten la Power Zone (Z = 0.8 m y Z = 1.2 m) para referencia visual.
5. THE Visualizador SHALL exportar el gráfico como un archivo HTML autocontenido en la ruta de salida especificada como argumento.
6. IF la lista de herramientas del layout está vacía, THEN THE Visualizador SHALL lanzar una excepción de tipo `ValueError` con un mensaje descriptivo.
7. THE Visualizador SHALL mostrar en el título del gráfico el valor del costo de fatiga total del layout visualizado.

---

### Requisito 7: Comparación Visual entre Layout Inicial y Layout Optimizado

**User Story:** Como investigador de ergonomía industrial, quiero comparar el layout inicial (antes de optimizar) con el layout optimizado en una misma visualización, para demostrar la mejora ergonómica en mi tesis.

#### Criterios de Aceptación

1. THE Visualizador SHALL aceptar opcionalmente un layout inicial y un layout optimizado para renderizarlos en el mismo gráfico 3D con trazas diferenciadas por color y leyenda.
2. THE Visualizador SHALL mostrar en el título del gráfico comparativo el costo de fatiga del layout inicial y el costo del layout optimizado junto con el porcentaje de mejora.
3. WHEN solo se provee un layout (sin comparación), THE Visualizador SHALL renderizar únicamente ese layout sin errores.

---

### Requisito 8: Ejecución desde Línea de Comandos

**User Story:** Como usuario del sistema, quiero ejecutar el optimizador completo desde la terminal con un único comando, para integrar el flujo de trabajo en mi entorno de investigación sin necesidad de modificar código.

#### Criterios de Aceptación

1. THE Sistema SHALL proveer un script de entrada `main.py` que acepte como argumento obligatorio la ruta al archivo `config.yaml`.
2. THE Sistema SHALL ejecutar en secuencia: carga de configuración, cálculo del costo inicial, optimización y generación del archivo HTML de visualización.
3. THE Sistema SHALL imprimir en consola el costo de fatiga inicial, el costo de fatiga optimizado y el porcentaje de mejora al finalizar la ejecución.
4. THE Sistema SHALL aceptar un argumento opcional `--output` para especificar la ruta del archivo HTML de salida; si no se especifica, SHALL usar `output/layout_optimizado.html` como ruta por defecto.
5. THE Sistema SHALL aceptar un argumento opcional `--seed` de tipo entero para fijar la semilla aleatoria del Optimizador.
6. IF la ejecución termina con éxito, THE Sistema SHALL retornar código de salida `0`.
7. IF ocurre un error irrecuperable durante la ejecución, THE Sistema SHALL imprimir el mensaje de error en `stderr` y retornar código de salida `1`.

---

### Requisito 9: Validación de Resultados Físicamente Posibles (Testing)

**User Story:** Como investigador de ergonomía industrial, quiero que el sistema incluya una suite de pruebas que verifique que el optimizador nunca produce resultados físicamente imposibles, para garantizar la validez científica de los resultados de la tesis.

#### Criterios de Aceptación

1. THE Suite_de_Pruebas SHALL verificar que el costo de fatiga retornado por el Core_Biomecánico es siempre mayor o igual a cero para cualquier combinación de coordenadas XYZ dentro del espacio de trabajo y peso positivo.
2. THE Suite_de_Pruebas SHALL verificar que el layout optimizado no contiene ningún par de herramientas cuya distancia euclidiana sea menor al `min_separation`.
3. THE Suite_de_Pruebas SHALL verificar que todas las coordenadas del layout optimizado están dentro de los límites del espacio de trabajo definidos en la Config.
4. THE Suite_de_Pruebas SHALL verificar que el costo de fatiga del layout optimizado es menor o igual al costo del layout inicial para cualquier configuración de entrada válida.
5. THE Suite_de_Pruebas SHALL verificar la propiedad de idempotencia del optimizador: ejecutar el optimizador sobre el layout ya optimizado no debe producir un costo de fatiga mayor al del layout optimizado original.
6. THE Suite_de_Pruebas SHALL verificar que el Core_Biomecánico produce el mismo resultado para el mismo layout independientemente del orden en que se listen las herramientas (propiedad de conmutatividad de la suma).
7. THE Suite_de_Pruebas SHALL verificar que una herramienta ubicada exactamente en el centro de la Power Zone (Z = 1.0 m) produce un costo de fatiga menor que la misma herramienta ubicada fuera de la Power Zone, manteniendo X e Y constantes.
