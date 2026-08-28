# agent.py
import math
import heapq
from collections import deque
from logic_engine import KnowledgeBase


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        import random
        pos = percept.get('agent_pos', (0, 0))
        return random.choice(self.actions_pool)


class SearchAgent:
    """An agent that uses graph search algorithms and dynamic KB reasoning to find paths to goals."""
    
    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'  # Defaulted to A* algorithm
        self.pos = (0, 0)
        
        # Step 3.1: Instantiate Knowledge Base & Define Safety Constraints
        self.kb = KnowledgeBase()
        
        # Rule 1: TargetVisible ∧ HasDust ⇒ SafeToEngage
        self.kb.tell_rule(["TargetVisible", "HasDust"], "SafeToEngage")
        
        # Rule 2: SafeToEngage ∧ BloodseekerMissing ⇒ Retreat
        self.kb.tell_rule(["SafeToEngage", "BloodseekerMissing"], "Retreat")

    def manhattan_distance(self, pos, goal):
        """Calculates the Manhattan distance between two points."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Calculates the straight-line Euclidean distance between two points."""
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

    def sense_and_act(self, percept: dict) -> str:
        # Track current position
        if 'agent_pos' in percept:
            self.pos = tuple(percept['agent_pos'])

        # Generate a new path plan if the current plan is empty
        if not self.plan:
            all_food = percept.get('all_food', [])
            if not all_food:
                return 'Up'  # Fallback if grid is cleared 

            # Find the closest food pellet based on Manhattan distance
            start_state = self.pos 
            closest_food = min(
                all_food,
                key=lambda f: self.manhattan_distance(start_state, f)
            )

            # Goal test function
            def is_goal(state):
                return state == tuple(closest_food)

            # Successor functions based on global grid environment
            width, height = percept['grid_size']
            walls = set(tuple(w) for w in percept['walls'])
            moves = [
                ('Up', (0, 1)),
                ('Down', (0, -1)),
                ('Left', (-1, 0)),
                ('Right', (1, 0))
            ]

            def get_successors(state):
                successors = []
                for action, (dx, dy) in moves:
                    nx, ny = state[0] + dx, state[1] + dy
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                        successors.append((action, (nx, ny)))
                return successors

            def get_ucs_successors(state):
                successors = []
                for action, (dx, dy) in moves:
                    nx, ny = state[0] + dx, state[1] + dy
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                        cost = 1  # Uniform step cost
                        successors.append((action, (nx, ny), cost))
                return successors

            # Execute active algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start_state, is_goal, get_successors)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start_state, is_goal, get_successors)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start_state, is_goal, get_ucs_successors)
            elif self.active_algo == 'AStar':
                # Call A* passing percepts to enable KB feasibility checks
                self.plan = self.astar_search(start_state, closest_food, walls, (width, height), percept=percept)

        # Pop and return the first planned action
        if self.plan:
            action = self.plan.pop(0)
            
            # Keep internal coordinates in sync
            x, y = self.pos
            if action == 'Up': self.pos = (x, y + 1)
            elif action == 'Down': self.pos = (x, y - 1)
            elif action == 'Left': self.pos = (x - 1, y)
            elif action == 'Right': self.pos = (x + 1, y)
            
            return action

        return 'Up'  # Fallback if search returns no valid path

    def bfs_search(self, start_state, is_goal, get_successors):
        """Breadth-First Search (BFS) - FIFO Queue"""
        frontier = deque([(start_state, [])])
        reached = {start_state}

        while frontier:
            current_state, path = frontier.popleft()

            if is_goal(current_state):
                return path

            for action, next_state in get_successors(current_state):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))

        return []

    def dfs_search(self, start_state, is_goal, get_successors):
        """Depth-First Search (DFS) - LIFO Stack"""
        frontier = [(start_state, [])]
        reached = {start_state}

        while frontier:
            current_state, path = frontier.pop()

            if is_goal(current_state):
                return path

            for action, next_state in get_successors(current_state):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))

        return []

    def ucs_search(self, start_state, is_goal, get_successors):
        """Uniform Cost Search (UCS) - Priority Queue ordered by path cost g(n)"""
        frontier = [(0, start_state, [])]
        reached = {start_state: 0}

        while frontier:
            current_cost, current_state, path = heapq.heappop(frontier)

            if is_goal(current_state):
                return path

            for action, next_state, step_cost in get_successors(current_state):
                new_cost = current_cost + step_cost
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    heapq.heappush(frontier, (new_cost, next_state, path + [action]))

        return []

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan', percept=None):
        """
        A* Search using f(n) = g(n) + h(n).
        Consults the Knowledge Base to prune infeasible tiles dynamically.
        """
        frontier = []
        reached_states = set()

        # Calculate initial heuristic cost h(n)
        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(start_pos, goal_pos)
        else:
            h_cost = self.manhattan_distance(start_pos, goal_pos)

        # Push initial state: (f_cost, g_cost, current_pos, path_taken)
        g_cost = 0
        f_cost = g_cost + h_cost
        heapq.heappush(frontier, (f_cost, g_cost, start_pos, []))

        width, height = grid_size
        moves = [
            ('Up', (0, 1)),
            ('Down', (0, -1)),
            ('Left', (-1, 0)),
            ('Right', (1, 0))
        ]

        # Extract tile-specific percept map if provided
        tile_percepts = percept.get('tile_percepts', {}) if percept else {}

        while frontier:
            f_current, g_current, current_pos, path_taken = heapq.heappop(frontier)

            if current_pos == tuple(goal_pos):
                return path_taken

            # Skip if we've already found a shorter path to this state
            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            # Node Expansion
            for action, (dx, dy) in moves:
                nx, ny = current_pos[0] + dx, current_pos[1] + dy
                neighbor_pos = (nx, ny)

                # Valid neighbor check: within bounds, not a physical wall, and not reached
                if (0 <= nx < width and 0 <= ny < height and 
                    neighbor_pos not in walls and 
                    neighbor_pos not in reached_states):

                    # --- Step 3.2: Knowledge Base Feasibility Check ---
                    self.kb.clear_facts()
                    
                    # Feed tile percepts for this neighbor into the KB
                    tile_facts = tile_percepts.get(neighbor_pos, [])
                    for fact in tile_facts:
                        self.kb.tell_fact(fact)
                    
                    # Run Forward Chaining inference engine
                    self.kb.forward_chain()
                    
                    # Prune neighbor if 'Retreat' is deduced
                    if 'Retreat' in self.kb.facts:
                        continue  # Tile is infeasible; skip adding to open list
                    # --------------------------------------------------

                    g_new = g_current + 1
                    
                    # Calculate new h(n)
                    if heuristic_type == 'euclidean':
                        h_new = self.euclidean_distance(neighbor_pos, goal_pos)
                    else:
                        h_new = self.manhattan_distance(neighbor_pos, goal_pos)
                        
                    f_new = g_new + h_new
                    
                    heapq.heappush(frontier, (f_new, g_new, neighbor_pos, path_taken + [action]))

        return []