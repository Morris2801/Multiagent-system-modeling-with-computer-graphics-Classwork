# FixedAgent: Immobile agents permanently fixed to cells
from mesa.discrete_space import FixedAgent

class Cell(FixedAgent):
    """Represents a single ALIVE or DEAD cell in the simulation."""

    DEAD = 0
    ALIVE = 1

    @property
    def x(self):
        return self.cell.coordinate[0]

    @property
    def y(self):
        return self.cell.coordinate[1]

    @property
    def is_alive(self):
        return self.state == self.ALIVE

    @property
    def neighbors(self):
        return self.cell.neighborhood.agents
    
    def __init__(self, model, cell, init_state=DEAD):
        """Create a cell, in the given state, at the given x, y position."""
        super().__init__(model)
        self.cell = cell
        self.pos = cell.coordinate
        self.state = init_state
        self._next_state = None

    def determine_state(self):
        """Compute if the cell will be dead or alive at the next tick.  This is
        based on the number of alive or dead neighbors.  The state is not
        changed here, but is just computed and stored in self._nextState,
        because our current state may still be necessary for our neighbors
        to calculate their next state.
        """
        # Get the neighbors and apply the rules on whether to be alive or dead
        # at the next tick.
        live_neighbors = sum(neighbor.is_alive for neighbor in self.neighbors)

        # Assume nextState is unchanged, unless changed below.
        self._next_state = self.state

        # Calculate abstract positions of three neighbors above (horizontally)
        upLeftPos = [self.x-1, self.y+1]
        upCenterPos = [self.x, self.y+1]
        upRightPos = [self.x+1, self.y+1]
        # Bools to check states alive/dead of corresponding neighbors
        upLeft = False
        upCenter = False
        upRight = False
        # Iterate through neighbors
        for neighbor in self.neighbors:
            #Get neighbor positions
            neighborPos = [neighbor.x, neighbor.y]
            # Compare matching positions and assign corresponding states
            if neighborPos == upLeftPos and neighbor.is_alive:
                upLeft = True
            if neighborPos == upCenterPos and neighbor.is_alive:
                upCenter = True
            if neighborPos == upRightPos and neighbor.is_alive:
                upRight = True

        # Update all cells except top row
        if (self.y != 49):
            if upRight and upCenter and upLeft:
                self._next_state = self.DEAD
            if upRight and upCenter and not upLeft:
                self._next_state = self.ALIVE
            if upRight and not upCenter and upLeft:
                self._next_state = self.DEAD
            if upRight and not upCenter and not upLeft:
                self._next_state = self.ALIVE
            if not upRight and upCenter and upLeft:
                self._next_state = self.ALIVE
            if not upRight and upCenter and not upLeft:
                self._next_state = self.DEAD
            if not upRight and not upCenter and upLeft:
                self._next_state = self.ALIVE
            if not upRight and not upCenter and not upLeft:
                self._next_state = self.DEAD
        # Maintain top row cells as initially set
        else:
            if self.y == 49 and self._next_state == self.ALIVE:
                self._next_state = self.ALIVE
            else: 
                self._next_state = self.DEAD

    def assume_state(self):
        """Set the state to the new computed state -- computed in step()."""
        self.state = self._next_state
    