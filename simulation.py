import random
from collections import defaultdict

import pandas as pd

from map import Map, CAPACITY
from agent import Agent
from search import Search

class Simulation:
    def __init__(self, search: Search, map_file_path: str, positions: list[tuple[int, int]], max_turns: int = 300, seed: int = 0):
        self.search = search
        self.map_file_path = map_file_path
        self.positions = positions
        self.max_turns = max_turns
        self.seed = seed
        self.rng = random.Random(seed)

        self.map = Map.from_file(map_file_path)
        self.agents: list[Agent] = self.create_agents()
        self.results = []

    def create_agents(self) -> list[Agent]:
        return [Agent(i, row, col, self.search) for i, (row, col) in enumerate(self.positions)]

    def active_agents(self) -> list[Agent]:
        # Agentes que siguen en juego: vivos y todavía dentro del edificio
        return [a for a in self.agents if a.is_alive and not a.has_evacuated]

    def run(self):
        turn = 0
        blocked_moves = 0  # movimientos perdidos por conflicto (congestión)
        idle_turns = 0     # turnos en que un agente esperó por no tener ruta
        evacuation_turns: list[int] = []

        # Estado inicial: algún agente podría partir sobre una celda en llamas
        self.kill_burned_agents()
        self.update_occupancy()
 
        while turn < self.max_turns:
            active = self.active_agents()
            if not active:
                break
            turn += 1
 
            # 1. Decisión: cada agente planifica con el estado actual (fuego + ocupación previa)
            intended: dict[int, tuple[int, int]] = {}
            for agent in active:
                next_cell = agent.decide_next_step(self.map)
                if next_cell is None:
                    idle_turns += 1
                    next_cell = (agent.row, agent.col)  # sin ruta: espera
                intended[agent.id] = next_cell
 
            # 2. Arbitraje de conflictos sobre las intenciones
            current = {a.id: (a.row, a.col) for a in active}
            resolved, blocked = self.resolve_conflicts(intended, current)
            blocked_moves += len(blocked)
 
            # 3. Ejecución simultánea de los movimientos ya resueltos
            for agent in active:
                agent.apply_move(resolved[agent.id])
                if (agent.row, agent.col) == self.map.exit_cell:
                    agent.has_evacuated = True
                    evacuation_turns.append(turn)
 
            # 4. El fuego avanza y elimina a quien alcance
            #    (los que llegaron a la salida en este turno ya se salvaron)
            self.map.spread_fire(turn)
            self.kill_burned_agents()
 
            # 5. Ocupación final del turno: alimenta el costo dinámico del siguiente
            self.update_occupancy()
 
        total = len(self.agents)
        evacuated = sum(1 for a in self.agents if a.has_evacuated)
        dead = sum(1 for a in self.agents if not a.is_alive)
        stranded = total - evacuated - dead  # vivos dentro al llegar a max_turns
 
        row = {
            "total_agents": total,
            "survivors": evacuated,
            "dead": dead,
            "stranded": stranded,
            "turns": turn,
            "avg_evacuation_turn": (sum(evacuation_turns) / len(evacuation_turns)) if evacuation_turns else None,
            "blocked_moves": blocked_moves,
            "idle_turns": idle_turns,
        }
        self.results.append(row)
        return row

    def kill_burned_agents(self):
        for agent in self.active_agents():
            if self.map.cells[agent.row][agent.col].is_burned:
                agent.is_alive = False

    def update_occupancy(self):
        # Se reconstruye desde cero con las posiciones reales de los agentes en juego
        table = [[0] * self.map.cols for _ in range(self.map.rows)]
        for agent in self.active_agents():
            table[agent.row][agent.col] += 1
        self.map.occupancy_table = table

    def resolve_conflicts(self, intended: dict[int, tuple[int, int]],
                          current: dict[int, tuple[int, int]]) -> tuple[dict[int, tuple[int, int]], set[int]]:
        """Recibe la celda a la que quiere ir cada agente y devuelve la celda a la
        que efectivamente va (su destino, o su celda actual si fue bloqueado)
        junto con el conjunto de agentes bloqueados."""
        blocked: set[int] = set()
 
        def destination(agent_id: int) -> tuple[int, int]:
            return current[agent_id] if agent_id in blocked else intended[agent_id]
 
        # Bloquear a un agente lo deja en su celda, y eso puede saturarla y obligar a
        # bloquear a otros; por eso se repite hasta que no haya más cambios
        changed = True
        while changed:
            changed = False
 
            # a) Cruces de frente: flujos opuestos por el mismo tramo en el mismo turno
            moves = defaultdict(list)
            for agent_id in intended:
                if agent_id not in blocked and intended[agent_id] != current[agent_id]:
                    moves[(current[agent_id], intended[agent_id])].append(agent_id)
            for (origin, target), agent_ids in moves.items():
                opposite = moves.get((target, origin))
                if opposite:
                    blocked.update(agent_ids)
                    blocked.update(opposite)
                    changed = True
 
            # b) Capacidad de cada celda destino
            groups = defaultdict(list)
            for agent_id in intended:
                groups[destination(agent_id)].append(agent_id)
 
            for cell, group in groups.items():
                # Los que ya están en la celda y se quedan tienen prioridad sobre los que entran;
                # un agente bloqueado en este mismo paso ya no va hacia esta celda
                stayers = [a for a in group if current[a] == cell]
                incoming = [a for a in group if current[a] != cell and a not in blocked]
                free_slots = max(0, CAPACITY - len(stayers))
 
                if len(incoming) > free_slots:
                    self.rng.shuffle(incoming)  # desempate aleatorio
                    blocked.update(incoming[free_slots:])
                    changed = True
 
        resolved = {agent_id: destination(agent_id) for agent_id in intended}
        return resolved, blocked

    def results_to_csv(self, results_file_name: str):
        df = pd.DataFrame(self.results)
        df.to_csv(f"./results/{results_file_name}", index=False)

    def reset(self):
        self.map = Map.from_file(self.map_file_path)
        self.agents = self.create_agents()
        self.rng = random.Random(self.seed)

