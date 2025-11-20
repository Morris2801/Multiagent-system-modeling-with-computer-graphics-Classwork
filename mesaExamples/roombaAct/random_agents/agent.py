from mesa.discrete_space import CellAgent, FixedAgent
from collections import deque

class RandomAgent(CellAgent):
    """
    Intelligent Roomba agent with pathfinding and battery management.
    
    Implemented Algorithms:
    - BFS (Breadth-First Search) for pathfinding
    - Finite State Machine (FSM) for behavior control
    - Memory-based exploration with knowledge sharing
    
    Movement: Von Neumann neighborhood (4 directions: up, down, left, right)
    Vision: Detects and remembers cells within 2-step distance
    
    Possible States:
    - exploring: Searching for dirty cells
    - returning: Going back to station (low battery)
    - charging: Charging battery
    - waiting: Waiting for cell to become available
    - dead: Out of battery
    """
    
    def __init__(self, model, cell):
        """
        Creates a new Roomba agent.
        
        Args:
            model: Mesa model reference
            cell: Initial cell of the agent
            
        Initializes:
        - Battery at 100%
        - Knowledge of initial cell and station
        - Data structures for pathfinding (BFS)
        - Memory of dirty and clean cells
        """
        super().__init__(model)
        self.battery = 100
        self.status = "exploring"
        self.start_position = cell.coordinate
        self.cell = cell
        self.known_stations = [cell.coordinate]
        self.target_station = cell.coordinate
        self.path_to_station = []
        self.visited_cells = {cell.coordinate}
        self.known_cells = {cell.coordinate}
        self.known_dirty_cells = set()
        self.known_clean_cells = {cell.coordinate}
        self.movements = 0
        self.path_to_dirty_cell = []
        self.target_dirty_cell = None
        
        self.scan_nearby_cells()
    
    def is_cell_blocked(self, cell):
        """
        Checks if a cell is traversable at the current instant.
        
        Algorithm: Collision detection
        
        Considers blocked:
        - Cells with permanent obstacles (walls)
        
        Args:
            cell: Cell to check
        
        Returns:
            bool: True if blocked, False if traversable
        """
        if any(isinstance(obj, ObstacleAgent) for obj in cell.agents):
            return True
        return False
    
    def scan_nearby_cells(self):
        """
        Scans and memorizes nearby cells using 2-step vision.
        
        Algorithm: BFS (Breadth-First Search) limited by distance
        
        Detects:
        - Permanent obstacles
        - Charging stations
        - Traversable cells
        - Dirty and clean cells
        
        Complexity: O(V + E) where V are visited cells (max ~12) and E are edges
        
        Updates:
        - self.known_cells: Adds traversable cells to mental map
        - self.known_stations: Adds discovered stations
        - self.known_dirty_cells: Adds dirty cells
        - self.known_clean_cells: Adds clean cells
        """
        current = self.cell.coordinate
        queue = deque([(current, 0)])
        visited_scan = {current}
        
        while queue:
            pos, dist = queue.popleft()
            
            if dist >= 2:
                continue
            
            x, y = pos
            neighbors = [
                (x, y + 1), (x, y - 1),
                (x - 1, y), (x + 1, y),
            ]
            
            for neighbor_coord in neighbors:
                if neighbor_coord in visited_scan:
                    continue
                
                if not (0 <= neighbor_coord[0] < self.model.width and 
                       0 <= neighbor_coord[1] < self.model.height):
                    continue
                
                visited_scan.add(neighbor_coord)
                neighbor_cell = self.model.grid[neighbor_coord]
                
                is_obstacle = any(isinstance(obj, ObstacleAgent) for obj in neighbor_cell.agents)
                
                if not is_obstacle:
                    self.known_cells.add(neighbor_coord)
                    
                    has_station = any(isinstance(obj, ChargingStation) for obj in neighbor_cell.agents)
                    if has_station and neighbor_coord not in self.known_stations:
                        self.known_stations.append(neighbor_coord)
                    
                    dirty_cell = next(
                        (obj for obj in neighbor_cell.agents if isinstance(obj, DirtyCell)),
                        None
                    )
                    if dirty_cell:
                        if not dirty_cell.is_clean:
                            self.known_dirty_cells.add(neighbor_coord)
                            self.known_clean_cells.discard(neighbor_coord)
                        else:
                            self.known_clean_cells.add(neighbor_coord)
                            self.known_dirty_cells.discard(neighbor_coord)
                    
                    queue.append((neighbor_coord, dist + 1))
    
    def update_cell_cleanliness(self, coord):
        """
        Updates the cleanliness status of a specific cell in memory.
        
        Algorithm: Direct memory update
        
        Called after cleaning a cell to update agent's knowledge.
        
        Args:
            coord: Tuple (x, y) coordinate of the cell
        """
        if coord in self.known_dirty_cells:
            self.known_dirty_cells.remove(coord)
        self.known_clean_cells.add(coord)
    
    def find_nearest_dirty_cell(self):
        """
        Finds the nearest known dirty cell using BFS.
        
        Algorithm: BFS (Breadth-First Search) on known cells only
        
        Strategy:
        1. Check if there are known dirty cells
        2. BFS from current position searching only in known_cells
        3. Stop when reaching any known dirty cell
        4. Return path to that cell
        
        Complexity: O(V + E) where V is known cells, E is edges
        
        Returns:
            tuple: (path, target_coord) where:
                   - path: List of coordinates to reach dirty cell
                   - target_coord: Coordinate of target dirty cell
                   - ([], None) if no known dirty cell is reachable
        """
        if not self.known_dirty_cells:
            return [], None
        
        start = self.cell.coordinate
        
        if start in self.known_dirty_cells:
            return [], start
        
        queue = deque([start])
        visited = {start}
        parent = {start: None}
        
        while queue:
            current = queue.popleft()
            
            if current in self.known_dirty_cells:
                path = []
                node = current
                while parent[node] is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path, current
            
            currentX, currentY = current
            neighbors = [
                (currentX, currentY + 1), (currentX, currentY - 1),
                (currentX - 1, currentY), (currentX + 1, currentY),
            ]
            
            for neighbor_coord in neighbors:
                if neighbor_coord not in self.known_cells:
                    continue
                
                if not (0 <= neighbor_coord[0] < self.model.width and 
                       0 <= neighbor_coord[1] < self.model.height):
                    continue
                    
                if neighbor_coord in visited:
                    continue
                
                neighbor_cell = self.model.grid[neighbor_coord]
                if any(isinstance(obj, ObstacleAgent) for obj in neighbor_cell.agents):
                    continue
                
                visited.add(neighbor_coord)
                parent[neighbor_coord] = current
                queue.append(neighbor_coord)
        
        return [], None
    
    def discover_stations(self):
        """
        Discovers and registers charging stations in current cell.
        
        Algorithm: Linear search in cell agents
        
        Executed each step to update knowledge.
        """
        charging_station = next(
            (obj for obj in self.cell.agents if isinstance(obj, ChargingStation)),
            None 
        )
        if charging_station:
            station_pos = charging_station.cell.coordinate
            if station_pos not in self.known_stations:
                self.known_stations.append(station_pos)
    
    def find_nearest_station(self):
        """
        Finds the nearest charging station using BFS.
        
        Algorithm: BFS (Breadth-First Search) on known cells
        
        Strategy:
        1. If only knows 1 station, return it
        2. BFS from current position until finding a station
        3. Fallback: Manhattan distance if BFS fails
        
        Complexity: O(V + E) in worst case
        
        Returns:
            tuple: (x, y) coordinates of nearest station
        """
        if not self.known_stations:
            return self.start_position
        
        if len(self.known_stations) == 1:
            return self.known_stations[0]
        
        start = self.cell.coordinate
        queue = deque([(start, 0)])
        visited = {start}
        
        while queue:
            current, dist = queue.popleft()
            
            if current in self.known_stations:
                return current
            
            currentX, currentY = current
            neighbors = [
                (currentX, currentY + 1), (currentX, currentY - 1),
                (currentX - 1, currentY), (currentX + 1, currentY),
            ]
            
            for neighbor_coord in neighbors:
                if neighbor_coord not in self.known_cells:
                    continue
                
                if not (0 <= neighbor_coord[0] < self.model.width and 
                       0 <= neighbor_coord[1] < self.model.height):
                    continue
                
                if neighbor_coord in visited:
                    continue
                
                neighbor_cell = self.model.grid[neighbor_coord]
                if any(isinstance(obj, ObstacleAgent) for obj in neighbor_cell.agents):
                    continue
                
                visited.add(neighbor_coord)
                queue.append((neighbor_coord, dist + 1))
        
        nearest = min(
            self.known_stations,
            key=lambda station: abs(start[0] - station[0]) + abs(start[1] - station[1])
        )
        return nearest
    
    def bfs_path_to_target(self, target_coord, use_known_only=False):
        """
        Calculates shortest path to target using BFS.
        
        Algorithm: BFS (Breadth-First Search) with path reconstruction
        
        Process:
        1. BFS from current position
        2. Save parent nodes for reconstruction
        3. When target found, reconstruct path
        
        Complexity: O(V + E)
        
        Args:
            target_coord: Target coordinates
            use_known_only: If True, only explores known cells
        
        Returns:
            list: List of coordinates in path (excluding current position)
                  Empty list if no path exists
        """
        start = self.cell.coordinate
        
        if start == target_coord:
            return []
        
        queue = deque([start])
        visited = {start}
        parent = {start: None}
        
        while queue:
            current = queue.popleft()
            
            if current == target_coord:
                path = []
                node = current
                while parent[node] is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path
            
            currentX, currentY = current
            neighbors = [
                (currentX, currentY + 1), (currentX, currentY - 1),
                (currentX - 1, currentY), (currentX + 1, currentY),
            ]
            
            for neighbor_coord in neighbors:
                if use_known_only and neighbor_coord not in self.known_cells:
                    continue
                
                if not (0 <= neighbor_coord[0] < self.model.width and 
                       0 <= neighbor_coord[1] < self.model.height):
                    continue
                    
                if neighbor_coord in visited:
                    continue
                
                neighbor_cell = self.model.grid[neighbor_coord]
                if any(isinstance(obj, ObstacleAgent) for obj in neighbor_cell.agents):
                    continue
                
                visited.add(neighbor_coord)
                parent[neighbor_coord] = current
                queue.append(neighbor_coord)
        
        return []
    
    def charge(self):
        """
        Charges battery if at a charging station.
        
        Algorithm: Linear increment
        
        Charge rate: +5% per step
        Maximum: 100%
        
        Returns:
            bool: True if charging, False if no station present
        """
        charging_station = next(
            (obj for obj in self.cell.agents if isinstance(obj, ChargingStation)),
            None
        )
        if charging_station:
            self.battery = min(100, self.battery + 5)
            return True
        return False

    def wait(self):
        """
        Waits in current cell without performing any action.
        
        Algorithm: No-op (no operation)
        
        Used when:
        - Blocked at charging station
        - Path occupied by another agent
        
        Consumption: -1% battery per step in main loop
        """
        pass

    def clean(self):
        """
        Cleans current cell if dirty.
        
        Algorithm: Linear search and state update
        
        Searches for DirtyCell in the cell and changes its state to clean.
        Updates memory of dirty/clean cells.
        """
        dirty_cell = next(
            (obj for obj in self.cell.agents if isinstance(obj, DirtyCell)),
            None
        )
        if dirty_cell and not dirty_cell.is_clean:
            dirty_cell.is_clean = True
            self.update_cell_cleanliness(self.cell.coordinate)

    def explore(self):
        """
        Exploratory movement with priority strategy.
        
        Algorithm: Greedy selection with randomness + BFS to known dirty cells
        
        Priorities:
        1. Path to known dirty cell (BFS) - Intelligent targeting
        2. Adjacent dirty cells (greedy) - Immediate cleaning
        3. Unvisited cells (exploration) - Discover new areas
        4. Any available cell (random walk) - Keep moving
        
        Updates:
        - visited_cells: Marks cell as visited
        - known_cells: Adds to mental map
        - movements: Movement counter
        
        Consumption: -1% battery per step
        """
        old_pos = self.cell.coordinate
        
        # Priority 0: Follow path to known dirty cell
        if self.path_to_dirty_cell:
            next_coord = self.path_to_dirty_cell.pop(0)
            next_cell = self.model.grid[next_coord]
            
            if not self.is_cell_blocked(next_cell):
                self.cell = next_cell
                self.visited_cells.add(self.cell.coordinate)
                self.known_cells.add(self.cell.coordinate)
                self.scan_nearby_cells()
                
                if self.cell.coordinate != old_pos:
                    self.movements += 1
                    self.model.total_movements += 1
                
                # Check if target is still dirty
                if self.cell.coordinate == self.target_dirty_cell:
                    if self.cell.coordinate not in self.known_dirty_cells:
                        self.path_to_dirty_cell = []
                        self.target_dirty_cell = None
                
                return
            else:
                self.path_to_dirty_cell = []
                self.target_dirty_cell = None
        
        # Check for new path to known dirty cell
        if not self.path_to_dirty_cell and self.known_dirty_cells:
            path, target = self.find_nearest_dirty_cell()
            if path:
                self.path_to_dirty_cell = path
                self.target_dirty_cell = target
                return
        
        # Local movement priorities
        available_cells = self.cell.neighborhood.select(
            lambda cell: not self.is_cell_blocked(cell)
        )
        
        # Priority 1: Adjacent dirty cells
        dirty_cells = available_cells.select(
            lambda cell: any(
                isinstance(obj, DirtyCell) and not obj.is_clean for obj in cell.agents
            )
        )
        
        # Priority 2: Unvisited cells
        unvisited = available_cells.select(
            lambda cell: cell.coordinate not in self.visited_cells
        )
        
        if len(dirty_cells) > 0:
            target_cells = dirty_cells
        elif len(unvisited) > 0:
            target_cells = unvisited
        else:
            target_cells = available_cells

        if len(target_cells) > 0:
            self.cell = target_cells.select_random_cell()
            self.visited_cells.add(self.cell.coordinate)
            self.known_cells.add(self.cell.coordinate)
            self.scan_nearby_cells()
            
            if self.cell.coordinate != old_pos:
                self.movements += 1
                self.model.total_movements += 1
    
    def goHome(self):
        """
        Navigates to nearest charging station.
        
        Algorithm: BFS pathfinding with dynamic recalculation
        
        Strategy:
        1. Find nearest station (BFS)
        2. Calculate optimal route (BFS)
        3. Follow route step by step
        4. Recalculate if dynamic obstacle found
        
        Collision handling:
        - If cell blocked: recalculate route
        - If no route: wait
        
        Consumption: -1% battery per step
        """
        old_pos = self.cell.coordinate
        nearest_station = self.find_nearest_station()
        
        if (self.target_station != nearest_station or not self.path_to_station):
            self.target_station = nearest_station
            self.path_to_station = self.bfs_path_to_target(nearest_station, use_known_only=True)
            
            if not self.path_to_station:
                return
        
        if self.path_to_station:
            next_coord = self.path_to_station.pop(0)
            next_cell = self.model.grid[next_coord]
            
            if not self.is_cell_blocked(next_cell):
                self.cell = next_cell
                self.scan_nearby_cells()
                
                if self.cell.coordinate != old_pos:
                    self.movements += 1
                    self.model.total_movements += 1
            else:
                self.path_to_station = []
    
    def communicate(self):
        """
        Shares knowledge with other Roombas in adjacent cells (Von Neumann neighborhood).
        
        Algorithm: Direct neighborhood check (same as obstacle detection)
        
        Shared information:
        - Known charging stations
        - Explored cells map
        - Known dirty and clean cells
        
        Benefit: Collaboration for more efficient exploration
        
        Complexity: O(4 * N * M) where N,M are for merging lists with up to 4 neighbors
        
        Note: Uses Von Neumann neighborhood (4 adjacent cells: up, down, left, right)
        """
        adjacent_cells = self.cell.neighborhood
        
        for neighbor_cell in adjacent_cells:
            for agent in neighbor_cell.agents:
                if isinstance(agent, RandomAgent) and agent != self:
                    combined_stations = list(set(
                        agent.known_stations + self.known_stations
                    ))
                    agent.known_stations = combined_stations
                    self.known_stations = combined_stations
                    
                    combined_cells = agent.known_cells.union(self.known_cells)
                    agent.known_cells = combined_cells
                    self.known_cells = combined_cells
                    
                    combined_dirty = agent.known_dirty_cells.union(self.known_dirty_cells)
                    agent.known_dirty_cells = combined_dirty
                    self.known_dirty_cells = combined_dirty
                    
                    combined_clean = agent.known_clean_cells.union(self.known_clean_cells)
                    agent.known_clean_cells = combined_clean
                    self.known_clean_cells = combined_clean

    def updateStatus(self):
        """
        Finite State Machine (FSM) to control behavior.
        
        Algorithm: FSM with hierarchical priorities
        
        Priority order:
        1. DEAD (battery = 0) - Terminal state
        2. CHARGING (at station + battery < 100)
        3. WAITING (blocked at station)
        4. RETURNING (insufficient battery to reach station)
        5. EXPLORING (default state)
        
        Transitions:
        - EXPLORING → RETURNING: battery < (dist_to_station + margin)
        - RETURNING → CHARGING: arrives at station
        - CHARGING → EXPLORING: battery = 100
        
        Battery management:
        - Calculates real distance with BFS
        - Safety margin: 15%
        """
        
        if self.battery <= 0:
            self.status = "dead"
            return
        
        charging_station = next(
            (obj for obj in self.cell.agents if isinstance(obj, ChargingStation)),
            None
        )
        
        # Priority 1: Charge if battery not full
        if charging_station and self.battery < 100:
            self.status = "charging"
            self.path_to_station = []
            return
        
        # Priority 2: Wait if blocked at station (battery full)
        if charging_station and self.battery >= 100:
            available_neighbors = self.cell.neighborhood.select(
                lambda cell: not self.is_cell_blocked(cell)
            )
            if len(available_neighbors) == 0:
                self.status = "waiting"
                return
        
        # Calculate if needs to return to charge
        nearest_station = self.find_nearest_station()
        test_path = self.bfs_path_to_target(nearest_station, use_known_only=True)
        
        if test_path:
            dist_nearest = len(test_path)
        else:
            currentX, currentY = self.cell.coordinate
            dist_nearest = abs(currentX - nearest_station[0]) + abs(currentY - nearest_station[1])
            dist_nearest = int(dist_nearest * 1.5)
        
        # Priority 3: Return if insufficient battery
        safety_margin = 15 
        if self.battery < (dist_nearest + safety_margin):
            self.status = "returning"
            return
        
        # Default state
        self.status = "exploring"

    def step(self): 
        """
        Executes one simulation step of the agent.
        
        Algorithm: Dispatcher based on FSM
        
        Sequence:
        1. Update state (FSM)
        2. Discover stations in current cell
        3. Communicate with other agents
        4. Execute action based on current state
        
        Actions per state:
        - dead: Does nothing
        - charging: Charges battery (+5%)
        - waiting: Waits (-1% battery)
        - exploring: Cleans and moves (-1% battery)
        - returning: Navigates to station and cleans (-1% battery)
        """
        self.updateStatus()
        self.discover_stations()
        self.communicate()
        
        if self.status == "dead":
            pass
            
        elif self.status == "charging":
            self.charge()
            
        elif self.status == "waiting":
            self.wait()
            self.battery -= 1
            
        elif self.status == "exploring":
            self.clean()
            self.explore()
            self.battery -= 1
            
        elif self.status == "returning":
            self.goHome()
            self.clean()
            self.battery -= 1


class ChargingStation(FixedAgent):
    """
    Charging station for Roomba agents.
    
    Characteristics:
    - Fixed position in grid
    - Charges Roomba battery (+5% per step)
    - Can be shared by multiple agents
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class ObstacleAgent(FixedAgent):
    """
    Permanent obstacle (wall).
    
    Characteristics:
    - Fixed position
    - Blocks Roomba movement
    - Forms grid border
    """
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def step(self):
        pass


class DirtyCell(FixedAgent):
    """
    Floor cell that can be dirty or clean.
    
    States:
    - is_clean=True: Clean cell
    - is_clean=False: Dirty cell (requires cleaning)
    
    Roombas automatically clean when passing through dirty cells.
    """
    
    def __init__(self, model, cell, is_clean=False):
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
