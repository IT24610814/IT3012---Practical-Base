# agent.py
import random
import math
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right'] #[cite: 2]

    def sense_and_act(self, percept: dict) -> str:
        pos = percept.get('agent_pos', (0, 0)) #[cite: 2]
        return random.choice(self.actions_pool) #[cite: 2]


class SearchAgent:
    """An agent that uses graph search algorithms to find paths to goals."""
    
    def __init__(self):
        self.plan = [] #[cite: 2]
        self.active_algo = 'AStar'  # Defaulted to our new A* algorithm
        self.pos = (0, 0) #[cite: 2]

    def manhattan_distance(self, pos, goal):
        """Calculates the Manhattan distance between two points."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1]) #[cite: 2]

    def euclidean_distance(self, pos, goal):
        """Calculates the straight-line Euclidean distance between two points."""
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2) #[cite: 2]

    def sense_and_act(self, percept: dict) -> str:
        # Track current position
        if 'agent_pos' in percept:
            self.pos = tuple(percept['agent_pos']) #[cite: 2]

        # Generate a new path plan if the current plan is empty
        if not self.plan:
            # We need the list of coordinates (all_food), not the integer count!
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
                return state == tuple(closest_food) #[cite: 2]

            # Successor functions based on global grid environment
            width, height = percept['grid_size'] #[cite: 2]
            walls = set(tuple(w) for w in percept['walls']) #[cite: 2]
            moves = [
                ('Up', (0, 1)),
                ('Down', (0, -1)),
                ('Left', (-1, 0)),
                ('Right', (1, 0))
            ] #[cite: 2]

            def get_successors(state):
                successors = [] #[cite: 2]
                for action, (dx, dy) in moves:
                    nx, ny = state[0] + dx, state[1] + dy #[cite: 2]
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                        successors.append((action, (nx, ny))) #[cite: 2]
                return successors #[cite: 2]

            def get_ucs_successors(state):
                successors = [] #[cite: 2]
                for action, (dx, dy) in moves:
                    nx, ny = state[0] + dx, state[1] + dy #[cite: 2]
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                        cost = 1  # Uniform step cost #[cite: 2]
                        successors.append((action, (nx, ny), cost)) #[cite: 2]
                return successors #[cite: 2]

            # Execute active algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start_state, is_goal, get_successors) #[cite: 2]
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start_state, is_goal, get_successors) #[cite: 2]
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start_state, is_goal, get_ucs_successors) #[cite: 2]
            elif self.active_algo == 'AStar':
                # Call the A* method
                self.plan = self.astar_search(start_state, closest_food, walls, (width, height)) #[cite: 2]

        # Pop and return the first planned action
        if self.plan:
            action = self.plan.pop(0) #[cite: 2]
            
            # Keep internal coordinates in sync
            x, y = self.pos #[cite: 2]
            if action == 'Up': self.pos = (x, y + 1) #[cite: 2]
            elif action == 'Down': self.pos = (x, y - 1) #[cite: 2]
            elif action == 'Left': self.pos = (x - 1, y) #[cite: 2]
            elif action == 'Right': self.pos = (x + 1, y) #[cite: 2]
            
            return action #[cite: 2]

        return 'Up'  # Fallback if search returns no valid path #[cite: 2]

    def bfs_search(self, start_state, is_goal, get_successors):
        """Breadth-First Search (BFS) - FIFO Queue"""
        frontier = deque([(start_state, [])]) #[cite: 2]
        reached = {start_state} #[cite: 2]

        while frontier:
            current_state, path = frontier.popleft() #[cite: 2]

            if is_goal(current_state):
                return path #[cite: 2]

            for action, next_state in get_successors(current_state):
                if next_state not in reached:
                    reached.add(next_state) #[cite: 2]
                    frontier.append((next_state, path + [action])) #[cite: 2]

        return [] #[cite: 2]

    def dfs_search(self, start_state, is_goal, get_successors):
        """Depth-First Search (DFS) - LIFO Stack"""
        frontier = [(start_state, [])] #[cite: 2]
        reached = {start_state} #[cite: 2]

        while frontier:
            current_state, path = frontier.pop() #[cite: 2]

            if is_goal(current_state):
                return path #[cite: 2]

            for action, next_state in get_successors(current_state):
                if next_state not in reached:
                    reached.add(next_state) #[cite: 2]
                    frontier.append((next_state, path + [action])) #[cite: 2]

        return [] #[cite: 2]

    def ucs_search(self, start_state, is_goal, get_successors):
        """Uniform Cost Search (UCS) - Priority Queue ordered by path cost g(n)"""
        frontier = [(0, start_state, [])] #[cite: 2]
        reached = {start_state: 0} #[cite: 2]

        while frontier:
            current_cost, current_state, path = heapq.heappop(frontier) #[cite: 2]

            if is_goal(current_state):
                return path #[cite: 2]

            for action, next_state, step_cost in get_successors(current_state):
                new_cost = current_cost + step_cost #[cite: 2]
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost #[cite: 2]
                    heapq.heappush(frontier, (new_cost, next_state, path + [action])) #[cite: 2]

        return [] #[cite: 2]

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        """A* Search using f(n) = g(n) + h(n) to find the optimal path."""
        frontier = [] #[cite: 2]
        reached_states = set() #[cite: 2]

        # Calculate initial heuristic cost h(n)
        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(start_pos, goal_pos) #[cite: 2]
        else:
            h_cost = self.manhattan_distance(start_pos, goal_pos) #[cite: 2]

        # Push initial state: (f_cost, g_cost, current_pos, path_taken)
        g_cost = 0 #[cite: 2]
        f_cost = g_cost + h_cost #[cite: 2]
        heapq.heappush(frontier, (f_cost, g_cost, start_pos, [])) #[cite: 2]

        width, height = grid_size #[cite: 2]
        moves = [
            ('Up', (0, 1)),
            ('Down', (0, -1)),
            ('Left', (-1, 0)),
            ('Right', (1, 0))
        ] #[cite: 2]

        while frontier:
            f_current, g_current, current_pos, path_taken = heapq.heappop(frontier) #[cite: 2]

            if current_pos == goal_pos:
                return path_taken #[cite: 2]

            # Skip if we've already found a shorter path to this state
            if current_pos in reached_states:
                continue #[cite: 2]

            reached_states.add(current_pos) #[cite: 2]

            # Node Expansion
            for action, (dx, dy) in moves:
                nx, ny = current_pos[0] + dx, current_pos[1] + dy #[cite: 2]
                neighbor_pos = (nx, ny) #[cite: 2]

                # Valid neighbor check: not a wall, within bounds, and not reached
                if (0 <= nx < width and 0 <= ny < height and 
                    neighbor_pos not in walls and 
                    neighbor_pos not in reached_states):
                    
                    g_new = g_current + 1 #[cite: 2]
                    
                    # Calculate new h(n)
                    if heuristic_type == 'euclidean':
                        h_new = self.euclidean_distance(neighbor_pos, goal_pos) #[cite: 2]
                    else:
                        h_new = self.manhattan_distance(neighbor_pos, goal_pos) #[cite: 2]
                        
                    f_new = g_new + h_new #[cite: 2]
                    
                    heapq.heappush(frontier, (f_new, g_new, neighbor_pos, path_taken + [action])) #[cite: 2]

        return [] #[cite: 2]


# --- Testing Checkpoint ---
if __name__ == "__main__":
    agent = SearchAgent() #[cite: 2]
    start = (0, 0) #[cite: 2]
    goal = (3, 4) #[cite: 2]
    
    m_dist = agent.manhattan_distance(start, goal) #[cite: 2]
    e_dist = agent.euclidean_distance(start, goal) #[cite: 2]
    
    print(f"Manhattan Distance from {start} to {goal}: {m_dist}") #[cite: 2]
    print(f"Euclidean Distance from {start} to {goal}: {e_dist}") #[cite: 2]