from map import *
from agent import *
from search import *

class Simulation:
    def __init__(self, map: Map, search: Search, positions: list[tuple[int, int]]):
        self.map = map
        self.search = search
        self.positions = positions
        self.agents: list[Agent] = [Agent(row, col) for row, col in positions]
        self.occ = OccupancyTable()
        self.results = []

    def run(self):
        self.results.append()

    def resolve_conflicts(self):
        pass

    def results_to_csv(self):
        pass

    def reset(self):
        self.agents.clear
        self.agents = [Agent(row, col) for row, col in self.positions]


    

    


