# agent.py
import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


class SearchAgent:
    """An agent that uses graph search algorithms to find paths to goals."""
    
    def __init__(self):
        pass

    def bfs_search(self, start_state, is_goal, get_successors):
        """
        Breadth-First Search (BFS)
        Explores the shallowest nodes first using a FIFO queue.
        """
        # Initialize a FIFO queue
        frontier = deque([(start_state, [])])  # Stores tuples of (state, path_of_actions)
        reached = {start_state}  # Set to track explored states (Graph Search)

        while frontier:
            current_state, path = frontier.popleft()

            if is_goal(current_state):
                return path

            for action, next_state in get_successors(current_state):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))

        return []  # No path found

    def dfs_search(self, start_state, is_goal, get_successors):
        """
        Depth-First Search (DFS)
        Explores the deepest nodes first using a LIFO stack.
        """
        # Initialize a LIFO stack
        frontier = [(start_state, [])]  # Stores tuples of (state, path_of_actions)
        reached = {start_state}  # Set to track explored states (Graph Search)

        while frontier:
            current_state, path = frontier.pop()

            if is_goal(current_state):
                return path

            for action, next_state in get_successors(current_state):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))

        return []  # No path found

    def ucs_search(self, start_state, is_goal, get_successors):
        """
        Uniform Cost Search (UCS)
        Explores nodes ordered by the total path cost $g(n)$ using a Priority Queue.
        """
        # Initialize a Priority Queue
        # Stores tuples of (cost, state, path_of_actions)
        frontier = [(0, start_state, [])]
        
        # Dictionary to track explored states and their lowest known cost $g(n)$
        reached = {start_state: 0} 

        while frontier:
            current_cost, current_state, path = heapq.heappop(frontier)

            if is_goal(current_state):
                return path

            # get_successors should yield (action, next_state, step_cost) for UCS
            for action, next_state, step_cost in get_successors(current_state):
                new_cost = current_cost + step_cost
                
                # Only explore if it's a new state or we found a cheaper path to it
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    heapq.heappush(frontier, (new_cost, next_state, path + [action]))

        return []  # No path found