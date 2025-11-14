from mesa import Model
from mesa.discrete_space import OrthogonalMooreGrid

from .agent import DirtyCell, RandomAgent, ObstacleAgent, ChargingStation

class RandomModel(Model):
    """
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
        dirty_cells: Number of cells that start dirty
        num_obstacles: Number of random obstacles to place (in addition to border)
    """
    def __init__(self, num_agents=10, width=8, height=8, dirty_cells=50, num_obstacles=60, seed=42):

        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.seed = seed
        self.width = width
        self.height = height
        self.dirty_cells = dirty_cells
        self.num_obstacles = num_obstacles
        self.max_steps = 1000

        self.grid = OrthogonalMooreGrid([width, height], torus=False)

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
        obstacle_cells = self.random.choices(inner_cells, k=min(self.num_obstacles, len(inner_cells)))
        for cell in obstacle_cells:
            ObstacleAgent(self, cell=cell)
        
        for cell in self.grid:
            if not any(isinstance(agent, ObstacleAgent) for agent in cell.agents):
                DirtyCell(self, cell=cell, is_clean=True)

        all_dirty_cells = [agent for agent in self.agents if isinstance(agent, DirtyCell)]
        cells_to_dirty = self.random.choices(all_dirty_cells, k=min(self.dirty_cells, len(all_dirty_cells)))
        for dirty_cell in cells_to_dirty:
            dirty_cell.is_clean = False

        available_cells = [
            cell for cell in self.grid 
            if not any(isinstance(agent, ObstacleAgent) for agent in cell.agents)
        ]
        
        roomba_cells = self.random.choices(available_cells, k=self.num_agents)
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

        if self.step_count >= self.max_steps:
            self.running = False
        self.running = True

    def step(self):
        '''Advance the model by one step.'''
        self.agents.shuffle_do("step")
