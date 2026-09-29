import os
import random
import time

import pandas as pd

from simulation import Simulation

# Mapas de entrada generados previamente (10x15, bordes de pared salvo la salida)
MAP_FILES = {
    "low_density": "./maps/map3.txt",
    "medium_density": "./maps/map2.txt",
    "high_density": "./maps/map1.txt",
}

NUM_AGENTS = 10
NUM_SIMULATIONS = 200
RESULTS_DIR = "./results"

ALGORITHMS = ["bfs", "dfs", "astar", "greedy", "genetic"]

def free_cells(map_obj):
    """Celdas disponibles para posicionar agentes: ni muro, ni fuego, ni la salida."""
    return [
        (r, c)
        for r in range(map_obj.rows)
        for c in range(map_obj.cols)
        if not map_obj.cells[r][c].is_wall
        and not map_obj.cells[r][c].is_burned
        and (r, c) != map_obj.exit_cell
    ]


def run_algorithm_tests(search_cls, algorithm_name: str):
    """Corre NUM_SIMULATIONS simulaciones por mapa para el algoritmo dado, reutilizando
    reset() y results_to_csv() de Simulation en vez de reconstruir el CSV a mano."""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output_paths = []

    for density_label, map_file in MAP_FILES.items():
        # Celdas disponibles del mapa (se leen una vez, antes de posicionar agentes)
        probe = Simulation(search_cls, map_file, [])
        cells = free_cells(probe.map)

        # Una sola Simulation por mapa: se reutiliza en las 100 corridas via reset(),
        # que reconstruye map/agents/rng a partir de self.positions y self.seed.
        # self.results no se limpia en reset(), así que las 100 filas se acumulan solas
        sim = Simulation(search_cls, map_file, [])

        start_time = time.time()
        for run_index in range(NUM_SIMULATIONS):
            # Semilla distinta por corrida: posiciones iniciales y desempates de
            # conflictos varían entre las 100 repeticiones, pero son reproducibles
            rng = random.Random(run_index)
            sim.positions = rng.sample(cells, NUM_AGENTS)
            sim.seed = run_index
            sim.reset()

            sim.run()

        elapsed = time.time() - start_time
        output_filename = f"{algorithm_name}_{density_label}_results.csv"
        sim.results_to_csv(output_filename)
        output_path = os.path.join(RESULTS_DIR, output_filename)
        output_paths.append(output_path)

        df = pd.DataFrame(sim.results)
        print(
            f"{algorithm_name:8} {density_label:14} "
            f"survivors_avg={df['survivors'].mean():5.2f} "
            f"dead_avg={df['dead'].mean():5.2f} "
            f"stranded_avg={df['stranded'].mean():5.2f} "
            f"turns_avg={df['turns'].mean():6.1f} "
            f"({elapsed:5.1f}s para {NUM_SIMULATIONS} simulaciones)"
        )

    return output_paths