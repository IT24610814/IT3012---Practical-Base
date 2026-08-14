# agent.py
import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept.get('agent_pos', (0, 0))
        return random.choice(self.actions_pool)


class SearchAgent:
    """An agent that uses graph search algorithms to find paths to goals."""
    
    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'  # Configurable: 'BFS', 'DFS', or 'UCS'
        self.pos = (0, 0)

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
                key=lambda f: abs(f[0] - start_state[0]) + abs(f[1] - start_state[1])
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