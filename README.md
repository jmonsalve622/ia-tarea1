# Simulación de Evacuación de Edificios con IA

Simulación de evacuación de un edificio en llamas, donde agentes deciden su
ruta hacia la salida usando distintos algoritmos de búsqueda (no informada,
informada y una metaheurística bioinspirada), bajo restricciones de
congestión dinámica y propagación de fuego.

## Estructura del proyecto

| Archivo                                                                            | Contenido                                                                                                                 |
| ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `map.py`                                                                           | Clases `Map` y `Cell`: grilla, muros, fuego, propagación (`spread_fire`) y costo dinámico por congestión (`dynamic_cost`) |
| `agent.py`                                                                         | Clase `Agent`: posición, estado (vivo/evacuado) y delegación de la decisión a su `Search`                                 |
| `search.py`                                                                        | Clase base `Search` y los 5 algoritmos: `BFS`, `DFS`, `AStar`, `Greedy`, `Genetic`                                        |
| `simulation.py`                                                                    | Clase `Simulation`: bucle por turnos, resolución de conflictos entre agentes y métricas de resultado                      |
| `map1.txt`, `map2.txt`, `map3.txt`                                                 | Mapas de entrada (10x15), en tres niveles de densidad de muros                                                            |
| `test.py`                                                                          | Lógica común de los experimentos: celdas libres, 200 simulaciones por mapa, guardado de CSV                               |
| `test_bfs.py`, `test_dfs.py`, `test_astar.py`, `test_greedy.py`, `test_genetic.py` | Corren los experimentos de cada algoritmo y generan sus CSV en `results/`                                                 |
| `main.py`                                                                          | Lee los CSV de `results/` y muestra por terminal un resumen por algoritmo y mapa                                          |
| `requirements.txt`                                                                 | Dependencias del proyecto                                                                                                 |

## Requerimientos

- Python 3.10+
- Dependencias en `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Cómo ejecutar

1. Generar los resultados (una vez por algoritmo; el genético tarda varios minutos, el resto segundos):

   ```bash
   python test_bfs.py
   python test_dfs.py
   python test_astar.py
   python test_greedy.py
   python test_genetic.py
   ```

   Esto crea los CSV en `results/` (uno por algoritmo y mapa).

2. Mostrar el resumen:

   ```bash
   python main.py
   ```
