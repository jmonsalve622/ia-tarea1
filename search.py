from __future__ import annotations

import heapq
import itertools
from abc import ABC, abstractmethod
from collections import deque
import random
from typing import TYPE_CHECKING
 
if TYPE_CHECKING:
    from agent import Agent
    from map import Map

class Search(ABC):
    REPLAN_EVERY_TURN = True

    @classmethod
    @abstractmethod
    def plan(self, agent: Agent, map: Map) -> list[tuple[int, int]]:
        pass

    @staticmethod
    def is_passable(map: Map, row: int, col: int) -> bool:
        # La salida siempre se puede pisar: el agente sale del edificio al llegar
        if (row, col) == map.exit_cell:
            return True
        # Muro, fuego o celda saturada (ocupación >= CAPACITY) devuelven costo infinito
        return map.dynamic_cost(row, col) != float("inf")

    @staticmethod
    def step_cost(map: Map, row: int, col: int) -> float:
        # Entrar a la salida cuesta lo mínimo: los agentes salen al llegar, ahí no se acumula gente
        if (row, col) == map.exit_cell:
            return 1
        return map.dynamic_cost(row, col)
 
    @staticmethod
    def manhattan(cell: tuple[int, int], goal: tuple[int, int]) -> int:
        # Heurística admisible: solo hay movimientos ortogonales y cada paso cuesta al menos 1
        return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])
 
    @staticmethod
    def reconstruct_path(came_from: dict, goal: tuple[int, int]) -> list[tuple[int, int]]:
        # Se recorre hacia atrás desde la salida hasta el inicio (su padre es None),
        # por lo que la celda inicial queda fuera de la ruta
        path = []
        node = goal
        while came_from[node] is not None:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path

class BFS(Search):
    @classmethod
    def plan(cls, agent: Agent, map: Map) -> list[tuple[int, int]]:
        start = (agent.row, agent.col)
        goal = map.exit_cell
    
        if start == goal:
            return []
    
        frontier = deque([start])
        came_from = {start: None}  # sirve además como conjunto de visitados
    
        while frontier:
            current = frontier.popleft()
    
            if current == goal:
                return cls.reconstruct_path(came_from, goal)
    
            for neighbor in map.orthogonal_neighbors(*current):
                if neighbor in came_from:
                    continue
                if not cls.is_passable(map, *neighbor):
                    continue
                came_from[neighbor] = current
                frontier.append(neighbor)
    
        return []  # sin ruta posible

class DFS(Search):
    @classmethod
    def plan(cls, agent: Agent, map: Map) -> list[tuple[int, int]]:
        start = (agent.row, agent.col)
        goal = map.exit_cell
 
        if start == goal:
            return []
 
        # La pila guarda (celda, padre); el padre se fija recién al sacar la celda,
        # así el camino reconstruido corresponde al orden real de exploración
        stack = [(start, None)]
        came_from = {}
 
        while stack:
            current, parent = stack.pop()
 
            if current in came_from:
                continue
            came_from[current] = parent
 
            if current == goal:
                return cls.reconstruct_path(came_from, goal)
 
            for neighbor in map.orthogonal_neighbors(*current):
                if neighbor in came_from:
                    continue
                if not cls.is_passable(map, *neighbor):
                    continue
                stack.append((neighbor, current))
 
        return []  # sin ruta posible
    
class AStar(Search):
    @classmethod
    def plan(cls, agent: Agent, map: Map) -> list[tuple[int, int]]:
        start = (agent.row, agent.col)
        goal = map.exit_cell
 
        if start == goal:
            return []
 
        # El contador desempata de forma estable sin comparar celdas entre sí
        counter = itertools.count()
        h_start = cls.manhattan(start, goal)
        # Entrada del heap: (f, h, desempate, g, celda); a igual f se prefiere la más cercana a la salida
        frontier = [(h_start, h_start, next(counter), 0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}
 
        while frontier:
            _, _, _, g, current = heapq.heappop(frontier)
 
            # Entrada obsoleta: la celda ya se alcanzó después por un camino más barato
            if g > cost_so_far[current]:
                continue
 
            # La meta se verifica al sacar del heap (no al generarla) para garantizar optimalidad
            if current == goal:
                return cls.reconstruct_path(came_from, goal)
 
            for neighbor in map.orthogonal_neighbors(*current):
                if not cls.is_passable(map, *neighbor):
                    continue
 
                new_cost = g + cls.step_cost(map, *neighbor)
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    came_from[neighbor] = current
                    h = cls.manhattan(neighbor, goal)
                    heapq.heappush(frontier, (new_cost + h, h, next(counter), new_cost, neighbor))
 
        return []  # sin ruta posible

class Greedy(Search):
    @classmethod
    def plan(cls, agent: Agent, map: Map) -> list[tuple[int, int]]:
        start = (agent.row, agent.col)
        goal = map.exit_cell
 
        if start == goal:
            return []
 
        counter = itertools.count()
        # Solo importa h: no se acumula costo, así que el valor de dynamic_cost no influye;
        # la congestión solo actúa bloqueando celdas saturadas (igual que en BFS y DFS)
        frontier = [(cls.manhattan(start, goal), next(counter), start)]
        came_from = {start: None}  # sirve además como conjunto de visitados
 
        while frontier:
            _, _, current = heapq.heappop(frontier)
 
            if current == goal:
                return cls.reconstruct_path(came_from, goal)
 
            for neighbor in map.orthogonal_neighbors(*current):
                if neighbor in came_from:
                    continue
                if not cls.is_passable(map, *neighbor):
                    continue
                came_from[neighbor] = current
                heapq.heappush(frontier, (cls.manhattan(neighbor, goal), next(counter), neighbor))
 
        return []  # sin ruta posible

MOVES = {
    "UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1), "WAIT": (0, 0)
}

class Genetic(Search):
    REPLAN_EVERY_TURN = False  # la planificación es costosa, se hace una sola vez al inicio
    POPULATION_SIZE = 60
    GENERATIONS = 80
    MUTATION_RATE = 0.15
    ELITE_SIZE = 4

    @classmethod
    def plan(cls, agent: Agent, map: Map) -> list[tuple[int, int]]:
        start = (agent.row, agent.col)
        goal = map.exit_cell
        if start == goal:
            return []

        chromosome_length = cls.chromosome_length(start, goal, map)
        population = [cls.random_chromosome(chromosome_length) for _ in range(cls.POPULATION_SIZE)]

        best_chromosome, best_fitness = None, float("-inf")
        for _ in range(cls.GENERATIONS):
            scored = [(chromo, cls.fitness(chromo, start, goal, map)) for chromo in population]
            scored.sort(key=lambda x: x[1], reverse=True)

            if scored[0][1] > best_fitness:
                best_chromosome, best_fitness = scored[0]

            population = cls.next_generation(scored, chromosome_length)

        return cls.chromosome_to_path(best_chromosome, start, goal, map)

    @staticmethod
    def chromosome_length(start, goal, map) -> int:
        manhattan = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
        return manhattan + max(4, manhattan // 2)  # margen para rodeos/esperas

    @staticmethod
    def random_chromosome(length: int) -> list[str]:
        return [random.choice(list(MOVES.keys())) for _ in range(length)]

    @classmethod
    def fitness(cls, chromosome, start, goal, map) -> float:
        row, col = start
        total_congestion_cost = 0
        reached_goal = False
        steps_taken = 0

        for move in chromosome:
            dr, dc = MOVES[move]
            nr, nc = row + dr, col + dc
            steps_taken += 1

            if not (0 <= nr < map.rows and 0 <= nc < map.cols):
                break  # sale del mapa: cromosoma inválido, se corta la simulación aquí
            if map.cells[nr][nc].is_wall:
                break  # choca con un muro: igual se corta
            if map.cells[nr][nc].is_burned:
                # el fuego lo alcanza: penalización fuerte, y no sigue avanzando
                return -1000 + steps_taken  # morir antes es peor que morir después
            
            row, col = nr, nc
            total_congestion_cost += Search.step_cost(map, row, col)

            if (row, col) == goal:
                reached_goal = True
                break

        if reached_goal:
            # premia llegar, y entre los que llegan, premia llegar rápido y con poco costo
            return 1000 - steps_taken - total_congestion_cost
        else:
            # no llegó ni murió: se evalúa qué tan cerca quedó de la salida
            remaining = abs(row - goal[0]) + abs(col - goal[1])
            return -remaining - total_congestion_cost

    @classmethod
    def next_generation(cls, scored, chromosome_length):
        next_gen = [chromo for chromo, _ in scored[:cls.ELITE_SIZE]]  # elitismo

        while len(next_gen) < cls.POPULATION_SIZE:
            parent_a = cls.tournament_select(scored)
            parent_b = cls.tournament_select(scored)
            child = cls.crossover(parent_a, parent_b, chromosome_length)
            child = cls.mutate(child)
            next_gen.append(child)

        return next_gen

    @staticmethod
    def tournament_select(scored, k=3):
        contestants = random.sample(scored, k)
        return max(contestants, key=lambda x: x[1])[0]

    @staticmethod
    def crossover(parent_a, parent_b, length):
        point = random.randint(1, length - 1)
        return parent_a[:point] + parent_b[point:]

    @classmethod
    def mutate(cls, chromosome):
        return [
            random.choice(list(MOVES.keys())) if random.random() < cls.MUTATION_RATE else gene
            for gene in chromosome
        ]

    @staticmethod
    def chromosome_to_path(chromosome, start, goal, map) -> list[tuple[int, int]]:
        row, col = start
        path = []
        for move in chromosome:
            dr, dc = MOVES[move]
            nr, nc = row + dr, col + dc
            if not (0 <= nr < map.rows and 0 <= nc < map.cols):
                break
            if map.cells[nr][nc].is_wall or map.cells[nr][nc].is_burned:
                break
            row, col = nr, nc
            path.append((row, col))
            if (row, col) == goal:
                break
        return path
