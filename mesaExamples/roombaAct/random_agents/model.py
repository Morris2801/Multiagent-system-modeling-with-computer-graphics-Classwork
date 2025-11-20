from mesa import Model
from mesa.discrete_space import OrthogonalVonNeumannGrid
import mesa

from .agent import DirtyCell, RandomAgent, ObstacleAgent, ChargingStation

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
        dirty_percentage: Percentage of cells that start dirty (0-100)
        obstacle_percentage: Percentage of cells that are obstacles (0-100)
        max_steps: Maximum number of steps before stopping
        simulation_mode: "single" for Sim 1, "multiple" for Sim 2
    """
    def __init__(self, num_agents=1, width=28, height=28, dirty_percentage=50, obstacle_percentage=10, max_steps=2500, simulation_mode="single", seed=42):

        super().__init__(seed=seed)
        self.simulation_mode = simulation_mode
        self.num_agents = num_agents if simulation_mode == "multiple" else 1
        self.seed = seed
        self.width = width
        self.height = height
        self.dirty_percentage = dirty_percentage
        self.obstacle_percentage = obstacle_percentage
        self.max_steps = max_steps
        self.step_count = 0
        self.total_movements = 0

        self.grid = OrthogonalVonNeumannGrid([width, height], torus=False)
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Clean Cells": lambda m: self.count_clean_cells(m),
                "Dirty Cells": lambda m: self.count_dirty_cells(m),
                "Clean Percentage": lambda m: self.get_clean_percentage(m),
                "Total Movements": lambda m: m.total_movements,
                "Exploring Agents": lambda m: self.count_agent_status(m, "exploring"),
                "Returning Agents": lambda m: self.count_agent_status(m, "returning"),
                "Charging Agents": lambda m: self.count_agent_status(m, "charging"),
                "Dead Agents": lambda m: self.count_agent_status(m, "dead"),
                "Average Battery Level": lambda m: self.average_battery(m),
            },
            agent_reporters={
                "Battery": "battery",
                "Status": "status",
                "Movements": "movements",
            }
        )

        # Identify the coordinates of the border of the grid
        border = [(x,y)
                  for y in range(height)
                  for x in range(width)
                  if y in [0, height-1] or x in [0, width - 1]]

        # Create the border cells (obstacles)
        for _, cell in enumerate(self.grid):
            if cell.coordinate in border:
                ObstacleAgent(self, cell=cell)
        
        inner_cells = [
            cell for cell in self.grid 
            if cell.coordinate not in border
        ]
        
        num_obstacles = int(len(inner_cells) * (obstacle_percentage / 100))
        obstacle_cells = self.random.choices(inner_cells, k=min(num_obstacles, len(inner_cells)))
        for cell in obstacle_cells:
            ObstacleAgent(self, cell=cell)
        
        for cell in self.grid:
            if not any(isinstance(agent, ObstacleAgent) for agent in cell.agents):
                DirtyCell(self, cell=cell, is_clean=True)

        all_dirty_cells = [agent for agent in self.agents if isinstance(agent, DirtyCell)]
        num_dirty = int(len(all_dirty_cells) * (dirty_percentage / 100))
        cells_to_dirty = self.random.choices(all_dirty_cells, k=min(num_dirty, len(all_dirty_cells)))
        for dirty_cell in cells_to_dirty:
            dirty_cell.is_clean = False

        # SIM 1: Agente en [1,1] con estación fija
        if self.simulation_mode == "single":
            start_cell = self.grid[(1, 1)]
            
            if any(isinstance(agent, ObstacleAgent) for agent in start_cell.agents):
                available_cells = [
                    cell for cell in self.grid 
                    if not any(isinstance(agent, ObstacleAgent) for agent in cell.agents)
                ]
                start_cell = available_cells[0] if available_cells else self.grid[(1, 1)]
            RandomAgent(self, cell=start_cell)
            ChargingStation(self, cell=start_cell)
         
        # SIM 2: Múltiples agentes en posiciones aleatorias
        else:
            available_cells = [
                cell for cell in self.grid 
                if not any(isinstance(agent, ObstacleAgent) for agent in cell.agents)
            ]
            
            roomba_cells = self.random.choices(available_cells, k=self.num_agents)
            
            # Crear agentes y estaciones en posiciones aleatorias
            RandomAgent.create_agents(
                self,
                self.num_agents,
                cell=roomba_cells
            )
            ChargingStation.create_agents(
                self,
                self.num_agents,
                cell=roomba_cells
            )
            
        self.running = True
        self.datacollector.collect(self)  

    def step(self):
        '''Advance the model by one step.'''
        self.step_count += 1
        self.agents.shuffle_do("step")
        
        self.datacollector.collect(self)
        
        if self.count_dirty_cells(self) == 0:
            self.running = False
            print(f"All cells cleaned in {self.step_count} steps")
            
        if self.step_count >= self.max_steps:
            self.running = False
            print(f"Max steps reached. Clean: {self.get_clean_percentage(self):.1f}%")
            
    @staticmethod
    def count_clean_cells(model):
        """Cuenta celdas limpias."""
        return len(model.agents.select(lambda x: isinstance(x, DirtyCell) and x.is_clean))

    @staticmethod
    def count_dirty_cells(model):
        """Cuenta celdas sucias."""
        return len(model.agents.select(lambda x: isinstance(x, DirtyCell) and not x.is_clean))

    @staticmethod
    def get_clean_percentage(model):
        """Calcula porcentaje de celdas limpias."""
        total_cells = len(model.agents.select(lambda x: isinstance(x, DirtyCell)))
        if total_cells == 0:
            return 100.0
        clean_cells = model.count_clean_cells(model)
        return (clean_cells / total_cells) * 100

    @staticmethod
    def count_agent_status(model, status):
        """Cuenta agentes en un estado específico."""
        return len(model.agents.select(lambda x: isinstance(x, RandomAgent) and x.status == status))
    
    @staticmethod
    def average_battery(model):
        """Calcula batería promedio de todos los agentes."""
        roombas = model.agents.select(lambda x: isinstance(x, RandomAgent))
        if len(roombas) == 0:
            return 0
        return sum(agent.battery for agent in roombas) / len(roombas)