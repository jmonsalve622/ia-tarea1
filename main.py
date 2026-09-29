import os
import pandas as pd
from test import ALGORITHMS, MAP_FILES, NUM_AGENTS, NUM_SIMULATIONS, RESULTS_DIR

ALGORITHM_LABELS = {
    "bfs": "BFS",
    "dfs": "DFS",
    "astar": "A*",
    "greedy": "Greedy",
    "genetic": "Genético",
}

MAP_LABELS = {
    "low_density": "Baja densidad",
    "medium_density": "Media densidad",
    "high_density": "Alta densidad",
}


def load_summary() -> dict[str, list[dict]]:
    """Lee cada CSV generado por run_algorithm_tests() y agrupa por algoritmo
    la tasa de supervivencia y las estadísticas de turnos de cada mapa."""
    summary: dict[str, list[dict]] = {}
    for algorithm in ALGORITHMS:
        algo_label = ALGORITHM_LABELS.get(algorithm, algorithm)
        for density_label in MAP_FILES:
            path = os.path.join(RESULTS_DIR, f"{algorithm}_{density_label}_results.csv")
            if not os.path.exists(path):
                continue  # falta correr ese test_<algoritmo>.py

            df = pd.read_csv(path)
            summary.setdefault(algo_label, []).append({
                "map": MAP_LABELS.get(density_label, density_label),
                "survival_rate": df["survivors"].sum() / df["total_agents"].sum() * 100,
                "turns_mean": df["turns"].mean(),
                "turns_std": df["turns"].std(),
                "turns_min": int(df["turns"].min()),
                "turns_max": int(df["turns"].max()),
            })
    return summary


def print_header():
    print("RESUMEN DE SIMULACIONES DE EVACUACIÓN")
    print(f"Agentes por simulación : {NUM_AGENTS}")
    print(f"Simulaciones por mapa  : {NUM_SIMULATIONS}")
    print()


def build_map_block(r: dict) -> list[str]:
    """Las líneas de un mapa dentro del box de su algoritmo."""
    return [
        r["map"],
        f"  Supervivencia : {r['survival_rate']:.1f} %",
        (
            f"  Turnos        : media {r['turns_mean']:.1f}"
            f" | desv. std {r['turns_std']:.1f}"
            f" | mín {r['turns_min']}"
            f" | máx {r['turns_max']}"
        ),
    ]


def print_algorithm_box(title: str, map_rows: list[dict]):
    # None marca dónde va un separador entre mapas dentro del box
    content: list[str | None] = []
    for i, r in enumerate(map_rows):
        if i > 0:
            content.append(None)
        content.extend(build_map_block(r))

    text_lines = [line for line in content if line is not None]
    width = max(len(title), max((len(line) for line in text_lines), default=0))

    def border(left: str, mid: str, right: str):
        print(left + mid * (width + 2) + right)

    def text(line: str):
        print(f"│ {line.ljust(width)} │")

    border("┌", "─", "┐")
    text(title)
    border("├", "─", "┤")
    for line in content:
        if line is None:
            border("├", "─", "┤")
        else:
            text(line)
    border("└", "─", "┘")


if __name__ == "__main__":
    summary = load_summary()

    if not summary:
        print(f"No se encontraron resultados en {RESULTS_DIR}/")
        print("Corré primero los test_<algoritmo>.py para generar los CSV.")
    else:
        print_header()
        for algorithm, map_rows in summary.items():
            print_algorithm_box(algorithm, map_rows)
            print()