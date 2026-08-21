# visual_grid_game.py
import random
import tkinter as tk
from simple_reflex_agent import SimpleReflexAgent #[cite: 3]
from agent import SearchAgent  # Imported our new SearchAgent

#lab2 part 1; 
#1. step 1.1: Add the facing direction, 2.Replace get_percept(), 3.Update execute_action()
class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, custom_walls=None, num_toxic_traps=5):
        self.width = width #[cite: 3]
        self.height = height #[cite: 3]
        self.agent_pos = [0, 0] #[cite: 3]
        self.facing = "Up" #[cite: 3]

        if custom_walls is not None:
            self.walls = set(custom_walls) #[cite: 3]
        else:
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)} #[cite: 3]

        self.food_positions = set() #[cite: 3]
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1) #[cite: 3]
            fy = random.randint(0, self.height - 1) #[cite: 3]
            pos_tuple = (fx, fy) #[cite: 3]

            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple) #[cite: 3]

        self.opponents = [] #[cite: 3]
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1) #[cite: 3]
            oy = random.randint(0, self.height - 1) #[cite: 3]
            op_pos = [ox, oy] #[cite: 3]

            if (
                tuple(op_pos) != (0, 0)
                and tuple(op_pos) not in self.walls
                and tuple(op_pos) not in self.food_positions
            ):
                self.opponents.append(op_pos) #[cite: 3]

        self.toxic_traps = set() #[cite: 3]

        while len(self.toxic_traps) < num_toxic_traps:
            tx = random.randint(0, self.width - 1) #[cite: 3]
            ty = random.randint(0, self.height - 1) #[cite: 3]
            trap = (tx, ty) #[cite: 3]

            if (
                trap != (0, 0)
                and trap not in self.walls
                and trap not in self.food_positions
                and trap not in {tuple(op) for op in self.opponents}
            ):
                self.toxic_traps.add(trap) #[cite: 3]

        self.score = 0 #[cite: 3]
        self.steps = 0 #[cite: 3]
        self.collision = False #[cite: 3]


    # Step 1.1 - Partial Observability
    def get_percept(self):

        x, y = self.agent_pos #[cite: 3]

        ahead_x, ahead_y = x, y #[cite: 3]

        if self.facing == "Up":
            ahead_y += 1 #[cite: 3]
        elif self.facing == "Down":
            ahead_y -= 1 #[cite: 3]
        elif self.facing == "Left":
            ahead_x -= 1 #[cite: 3]
        elif self.facing == "Right":
            ahead_x += 1 #[cite: 3]

        out_of_bounds = (
            ahead_x < 0 or ahead_x >= self.width or
            ahead_y < 0 or ahead_y >= self.height
        ) #[cite: 3]

        wall_ahead = out_of_bounds or (ahead_x, ahead_y) in self.walls #[cite: 3]

        return {
            "wall_ahead": wall_ahead,
            "food_here": (x, y) in self.food_positions,
            "toxin_here": (x, y) in self.toxic_traps,
            "collision": self.collision,
            "score": self.score,
            "remaining_food": len(self.food_positions),
            "grid_size": (self.width, self.height),
            "walls": list(self.walls),
            "all_food": list(self.food_positions)
        } #[cite: 3]


    # Step 1.2 - Agent actions
    def execute_action(self, action):

        self.steps += 1 #[cite: 3]

        if action in ["Up", "Down", "Left", "Right"]:
            self.facing = action #[cite: 3]

        new_pos = list(self.agent_pos) #[cite: 3]

        if action == "Suck":
            pass #[cite: 3]

        elif action == "Up":
            new_pos[1] = min(self.height - 1, new_pos[1] + 1) #[cite: 3]

        elif action == "Down":
            new_pos[1] = max(0, new_pos[1] - 1) #[cite: 3]

        elif action == "Left":
            new_pos[0] = max(0, new_pos[0] - 1) #[cite: 3]

        elif action == "Right":
            new_pos[0] = min(self.width - 1, new_pos[0] + 1) #[cite: 3]


        if tuple(new_pos) in self.walls:
            self.score -= 5 #[cite: 3]
        else:
            self.agent_pos = new_pos #[cite: 3]


        pos = tuple(self.agent_pos) #[cite: 3]

        if pos in self.food_positions:
            self.food_positions.remove(pos) #[cite: 3]
            self.score += 20 #[cite: 3]


        if pos in self.toxic_traps:
            self.score -= 15 #[cite: 3]


        for op in self.opponents:

            move = random.choice(
                ["Up", "Down", "Left", "Right", "Stay"]
            ) #[cite: 3]

            if move == "Up" and op[1] < self.height - 1:
                op[1] += 1 #[cite: 3]

            elif move == "Down" and op[1] > 0:
                op[1] -= 1 #[cite: 3]

            elif move == "Left" and op[0] > 0:
                op[0] -= 1 #[cite: 3]

            elif move == "Right" and op[0] < self.width - 1:
                op[0] += 1 #[cite: 3]


            if op == self.agent_pos:
                self.score -= 50 #[cite: 3]
                self.collision = True #[cite: 3]


    def is_done(self):

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        ) #[cite: 3]


class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None, num_toxic_traps=5):
        self.root = root #[cite: 3]
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt") #[cite: 3]

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents,
                                      custom_walls=walls, num_toxic_traps=num_toxic_traps) #[cite: 3]

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600 #[cite: 3]
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height)) #[cite: 3]

        canvas_w = self.env.width * self.cell_size #[cite: 3]
        canvas_h = self.env.height * self.cell_size #[cite: 3]

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white") #[cite: 3]
        self.canvas.pack() #[cite: 3]

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14)) #[cite: 3]
        self.label.pack(pady=10) #[cite: 3]

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white") #[cite: 3]
        self.btn.pack(pady=5) #[cite: 3]

        self.draw_grid() #[cite: 3]

    def draw_grid(self):
        self.canvas.delete("all") #[cite: 3]

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size #[cite: 3]
                y1 = (self.env.height - 1 - y) * self.cell_size #[cite: 3]
                x2 = x1 + self.cell_size #[cite: 3]
                y2 = y1 + self.cell_size #[cite: 3]

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b" #[cite: 3]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1") #[cite: 3]

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold")) #[cite: 3]

        # Step 2.3: Render toxic traps as purple diamond shapes
        for tx, ty in self.env.toxic_traps:
            cx = tx * self.cell_size + self.cell_size / 2 #[cite: 3]
            cy = (self.env.height - 1 - ty) * self.cell_size + self.cell_size / 2 #[cite: 3]
            half = self.cell_size * 0.35 #[cite: 3]
            points = [
                cx, cy - half,   # top
                cx + half, cy,   # right
                cx, cy + half,   # bottom
                cx - half, cy,   # left
            ] #[cite: 3]
            self.canvas.create_polygon(points, fill="#7c3aed", outline="#5b21b6") #[cite: 3]

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25 #[cite: 3]
            x1 = fx * self.cell_size + offset #[cite: 3]
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset #[cite: 3]
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706") #[cite: 3]

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2 #[cite: 3]
            x1 = ox * self.cell_size + offset #[cite: 3]
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset #[cite: 3]
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000") #[cite: 3]

        ax, ay = self.env.agent_pos #[cite: 3]
        offset = self.cell_size * 0.15 #[cite: 3]
        x1 = ax * self.cell_size + offset #[cite: 3]
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset #[cite: 3]
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a") #[cite: 3]

    def run_loop(self):
        self.btn.config(state="disabled") #[cite: 3]

        agent = SearchAgent() # Replaced the ModelBasedAgent with our SearchAgent
        agent.active_algo = 'AStar' # Explicitly telling it to use A*

        def step():
            if not self.env.is_done():
                #step 1.2
                percept = self.env.get_percept() #[cite: 3]
                action = agent.sense_and_act(percept) #[cite: 3]
                self.env.execute_action(action) #[cite: 3]

                self.draw_grid() #[cite: 3]
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}") #[cite: 3]
                self.root.after(250, step) #[cite: 3]
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}" #[cite: 3]
                self.label.config(text=end_text) #[cite: 3]
                self.btn.config(state="normal") #[cite: 3]

        step() #[cite: 3]


if __name__ == "__main__":
    root = tk.Tk() #[cite: 3]
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0, num_toxic_traps=6) #[cite: 3]
    root.mainloop() #[cite: 3]