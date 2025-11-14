from mesa.discrete_space import CellAgent, FixedAgent

class RandomAgent(CellAgent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
    """
    def __init__(self, model, cell):
        """
        Creates a new random agent.
        Args:
            model: Model reference for the agent
            cell: Reference to its position within the grid
        """
        super().__init__(model)
        self.battery = 100
        self.status = "exploring"
        self.start_position = cell.coordinate
        self.cell = cell
        self.checkpoints = []
    
    def charge(self):
        currentX, currentY = self.cell.coordinate
        startX, startY = self.start_position 
        if currentX == startX and currentY == startY: # CAMBIAR ESTO PARA QUE BUSQUE EN ARRAY CHECKPOINTS
            self.battery = (self.battery + 5) % 100
            return True
        return False

    def clean(self):
        #Clean @cells if dirty 
        dirty_cell = next(
            (obj for obj in self.cell.agents if isinstance(obj, DirtyCell)),
            None
        )
        if dirty_cell and not dirty_cell.is_clean:
            dirty_cell.is_clean = True

    def explore(self):
        #Move to random cell, preferably dirty one 
        available_cells = self.cell.neighborhood.select(
            lambda cell: not any(isinstance(obj, ObstacleAgent) for obj in cell.agents)
        )
        cells_with_dirt = available_cells.select(
            lambda cell: any(
                isinstance(obj, DirtyCell) and not obj.is_clean for obj in cell.agents
            )
        )
        target_cells = (
            cells_with_dirt if len(cells_with_dirt) > 0 else available_cells
        )
        if len(target_cells) > 0:
            self.cell = target_cells.select_random_cell()
    
    def goHome(self):
        available_cells = self.cell.neighborhood.select(
            lambda cell: not any(isinstance(obj, ObstacleAgent) for obj in cell.agents)
        )
        
        if len(available_cells) > 0:
            best_cell = min(
                available_cells,
                key=lambda cell: abs(cell.coordinate[0] - self.start_position[0]) + 
                               abs(cell.coordinate[1] - self.start_position[1])
            )
            self.cell = best_cell
    
    def updateStatus(self):
        #Máquina de etados 
        currentX, currentY = self.cell.coordinate
        startX, startY = self.start_position
        dist_home = abs(currentX - startX) + abs(currentY - startY)
        
        if self.battery <= 0:
            self.status = "dead"
            return
        if dist_home == 0 and self.battery < 100:
            self.status = "charging"
            return
        if self.battery < (dist_home + 10):
            self.status = "returning"
            return
        self.status = "exploring"

    def step(self): 
        self.updateStatus()
        
        if self.status == "dead":
            pass
            
        elif self.status == "charging":
            self.charge()
            
        elif self.status == "exploring":
            self.clean()
            self.explore()
            self.battery -= 1
            
        elif self.status == "returning":
            self.goHome()
            self.battery -= 1
        
        

class ChargingStation(FixedAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class ObstacleAgent(FixedAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell=cell

    def step(self):
        pass


class DirtyCell(FixedAgent):
    """Floor tile, can be either dirty or clean"""
    
    def __init__(self, model, cell, is_clean=False):
        """Create a floor tile.

        Args:
            model: Model instance
            cell: Cell to which this floor tile belongs
            is_clean: Initial cleanliness state (default: False = dirty)
        """
        super().__init__(model)
        self.cell = cell
        self._is_clean = is_clean  

    @property
    def is_clean(self):
        return self._is_clean

    @is_clean.setter
    def is_clean(self, value: bool) -> None:
        self._is_clean = value

    def step(self):
        pass

