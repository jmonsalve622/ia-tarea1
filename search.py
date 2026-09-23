from abc import ABC, abstractmethod
from map import Map, Cell
from agent import Agent

class Search(ABC):
    @classmethod
    @abstractmethod
    def plan(agent: Agent, map: Map, occ, turn: int):
        pass

class BFS(Search):
    @classmethod
    def plan(agent: Agent, map: Map, occ, turn: int):
        pass

class AStar(Search):
    @classmethod
    def plan(agent: Agent, map: Map, occ, turn: int):
        pass

    
