import math
import random
import time
import tkinter as tk
from tkinter import messagebox

# Try importing pygame for sound effects (gracefully falls back if missing)
HAS_SOUND = False
try:
    import array
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    HAS_SOUND = True
except ImportError:
    pass


def play_tone(frequency=440, duration=0.1, wave_type="sine"):
    """Generates simple synthesized sound tones using Pygame."""
    if not HAS_SOUND:
        return
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = array.array("h", [0] * n_samples)
    
    for i in range(n_samples):
        t = float(i) / sample_rate
        if wave_type == "sine":
            val = math.sin(2.0 * math.pi * frequency * t)
        elif wave_type == "square":
            val = 0.5 if math.sin(2.0 * math.pi * frequency * t) > 0 else -0.5
        elif wave_type == "sawtooth":
            val = 2.0 * (t * frequency - math.floor(0.5 + t * frequency))
        buf[i] = int(val * 16384)
        
    sound = pygame.mixer.Sound(buffer=buf)
    sound.play()


class SnakesAndLadders:
    def __init__(self, root):
        self.root = root
        self.root.title("Snakes & Ladders - Python Edition")
        self.root.geometry("920x720")
        self.root.configure(bg="#1e1e2e")

        # Game Board Configuration (10x10)
        self.board_size = 10
        self.snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
        self.ladders = {1: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 100}

        # Game State
        self.vs_computer = False
        self.current_player = 0  # 0: Player 1, 1: Player 2 / Computer
        self.positions = [0, 0]
        self.scores = [0, 0]
        self.player_colors = ["#ff5555", "#50fa7b"]
        self.player_names = ["Player 1", "Player 2"]
        self.is_rolling = False

        self._build_gui()

    def _build_gui(self):
        # Sidebar Panel
        sidebar = tk.Frame(self.root, bg="#282a36", width=260, padx=15, pady=15)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        title = tk.Label(sidebar, text="Snakes &\nLadders", font=("Helvetica", 20, "bold"), fg="#bd93f9", bg="#282a36")
        title.pack(pady=(5, 15))

        # Mode Selection (Opponent)
        tk.Label(sidebar, text="Opponent:", font=("Helvetica", 10, "bold"), fg="#f8f8f2", bg="#282a36").pack(anchor="w")
        self.mode_var = tk.StringVar(value="p2p")
        
        rb1 = tk.Radiobutton(sidebar, text="2 Players (Local)", variable=self.mode_var, value="p2p", 
                             bg="#282a36", fg="#f8f8f2", selectcolor="#44475a", activebackground="#282a36", 
                             font=("Helvetica", 9), command=self.reset_match)
        rb2 = tk.Radiobutton(sidebar, text="VS Computer AI", variable=self.mode_var, value="ai", 
                             bg="#282a36", fg="#f8f8f2", selectcolor="#44475a", activebackground="#282a36", 
                             font=("Helvetica", 9), command=self.reset_match)
        rb1.pack(anchor="w", pady=1)
        rb2.pack(anchor="w", pady=1)

        # Match Target Selection (Single Game vs First to 3 Wins)
        tk.Label(sidebar, text="Match Target:", font=("Helvetica", 10, "bold"), fg="#f8f8f2", bg="#282a36").pack(anchor="w", pady=(10, 0))
        self.target_var = tk.StringVar(value="1")

        rb_single = tk.Radiobutton(sidebar, text="Single Match", variable=self.target_var, value="1", 
                                   bg="#282a36", fg="#f8f8f2", selectcolor="#44475a", activebackground="#282a36", 
                                   font=("Helvetica", 9), command=self.reset_match)
        rb_first3 = tk.Radiobutton(sidebar, text="First to 3 Wins", variable=self.target_var, value="3", 
                                   bg="#282a36", fg="#f8f8f2", selectcolor="#44475a", activebackground="#282a36", 
                                   font=("Helvetica", 9), command=self.reset_match)
        rb_single.pack(anchor="w", pady=1)
        rb_first3.pack(anchor="w", pady=1)

        # Score Tracker Frame
        score_frame = tk.Frame(sidebar, bg="#44475a", padx=10, pady=8)
        score_frame.pack(fill=tk.X, pady=15)
        
        tk.Label(score_frame, text="SCOREBOARD", font=("Helvetica", 9, "bold"), fg="#8be9fd", bg="#44475a").pack()
        self.lbl_scores = tk.Label(score_frame, text="P1: 0  |  P2: 0", font=("Helvetica", 11, "bold"), fg="#f8f8f2", bg="#44475a")
        self.lbl_scores.pack(pady=2)

        # Status & Turn Displays
        self.lbl_turn = tk.Label(sidebar, text="Turn: Player 1", font=("Helvetica", 12, "bold"), fg="#ff5555", bg="#282a36")
        self.lbl_turn.pack(pady=(5, 5))

        # Dice Display Box
        self.lbl_dice = tk.Label(sidebar, text="🎲", font=("Helvetica", 40), fg="#f8f8f2", bg="#44475a", width=3, height=1)
        self.lbl_dice.pack(pady=5)

        # Roll Action Button
        self.btn_roll = tk.Button(sidebar, text="ROLL DICE", font=("Helvetica", 12, "bold"), fg="#282a36", bg="#50fa7b",
                                  activebackground="#69ff94", bd=0, padx=10, pady=8, cursor="hand2", command=self.roll_dice)
        self.btn_roll.pack(pady=10, fill=tk.X)

        # Reset Button
        btn_reset = tk.Button(sidebar, text="Reset Score & Game", font=("Helvetica", 10), fg="#f8f8f2", bg="#ff5555",
                              bd=0, pady=5, cursor="hand2", command=self.reset_match)
        btn_reset.pack(side=tk.BOTTOM, fill=tk.X)

        # Game Canvas (Board)
        self.canvas = tk.Canvas(self.root, bg="#21222c", highlightthickness=0)
        self.canvas.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.canvas.bind("<Configure>", self.draw_board)

    def get_tile_center(self, num):
        """Calculates canvas (x, y) pixel coordinates for a given board square (1 to 100)."""
        if num < 1:
            num = 1
        num -= 1
        row = num // 10
        col = num % 10
        
        # Zig-zag pattern
        if row % 2 == 1:
            col = 9 - col
            
        x = col * self.cell_size + self.cell_size / 2
        y = (9 - row) * self.cell_size + self.cell_size / 2
        return x, y

    def draw_board(self, event=None):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self.cell_size = min(w, h) / 10

        # 1. Draw Grid Tiles
        for row in range(10):
            for col in range(10):
                actual_col = col if row % 2 == 0 else (9 - col)
                num = row * 10 + actual_col + 1

                x1 = col * self.cell_size
                y1 = (9 - row) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#282a36" if (row + col) % 2 == 0 else "#383a59"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#44475a", width=1)
                self.canvas.create_text(x1 + 6, y1 + 6, text=str(num), font=("Helvetica", 8, "bold"), fill="#6272a4", anchor="nw")

        # 2. Draw Ladders
        for start, end in self.ladders.items():
            sx, sy = self.get_tile_center(start)
            ex, ey = self.get_tile_center(end)
            self.canvas.create_line(sx, sy, ex, ey, fill="#50fa7b", width=6, capstyle=tk.ROUND)
            self.canvas.create_line(sx, sy, ex, ey, fill="#f1fa8c", width=2, capstyle=tk.ROUND)

        # 3. Draw Snakes
        for start, end in self.snakes.items():
            sx, sy = self.get_tile_center(start)
            ex, ey = self.get_tile_center(end)
            self.canvas.create_line(sx, sy, ex, ey, fill="#ff5555", width=6, capstyle=tk.ROUND)
            self.canvas.create_line(sx, sy, ex, ey, fill="#ff79c6", width=2, capstyle=tk.ROUND)

        # 4. Draw Player Tokens
        offsets = [-self.cell_size * 0.15, self.cell_size * 0.15]
        for p in range(2):
            pos = self.positions[p]
            if pos > 0:
                cx, cy = self.get_tile_center(pos)
                cx += offsets[p]
                r = self.cell_size * 0.2
                self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=self.player_colors[p], outline="#ffffff", width=2)

    def roll_dice(self):
        if self.is_rolling:
            return
        
        self.is_rolling = True
        self.btn_roll.config(state=tk.DISABLED)

        # Dice Animation Loop
        def animate(roll_count=0):
            val = random.randint(1, 6)
            self.lbl_dice.config(text=str(val))
            play_tone(frequency=300 + roll_count * 20, duration=0.03)

            if roll_count < 10:
                self.root.after(50, animate, roll_count + 1)
            else:
                final_val = random.randint(1, 6)
                self.lbl_dice.config(text=str(final_val))
                self.move_player(final_val)

        animate()

    def move_player(self, steps):
        p = self.current_player
        start_pos = self.positions[p]
        target_pos = start_pos + steps

        if target_pos > 100:
            target_pos = start_pos  # Overshoot rule: must land exactly on 100

        def step_by_step(current):
            if current < target_pos:
                current += 1
                self.positions[p] = current
                self.draw_board()
                play_tone(frequency=440 + current * 5, duration=0.05)
                self.root.after(150, step_by_step, current)
            else:
                # Check for Snakes or Ladders
                self.check_special_tiles(p)

        step_by_step(start_pos)

    def check_special_tiles(self, p):
        pos = self.positions[p]

        if pos in self.ladders:
            play_tone(frequency=800, duration=0.2, wave_type="square")
            self.positions[p] = self.ladders[pos]
            self.draw_board()
        elif pos in self.snakes:
            play_tone(frequency=150, duration=0.3, wave_type="sawtooth")
            self.positions[p] = self.snakes[pos]
            self.draw_board()

        # Round Victory Check
        if self.positions[p] == 100:
            play_tone(frequency=600, duration=0.4)
            self.scores[p] += 1
            self.update_score_display()

            target_wins = int(self.target_var.get())
            if self.scores[p] >= target_wins:
                if target_wins > 1:
                    messagebox.showinfo("Tournament Champion!", f"🏆 {self.player_names[p]} won {target_wins} rounds and took the match!")
                else:
                    messagebox.showinfo("Game Over!", f"🎉 {self.player_names[p]} Wins!")
                self.reset_match()
            else:
                messagebox.showinfo("Round Over", f"🎉 {self.player_names[p]} wins this round!\n\nCurrent Score:\n{self.player_names[0]}: {self.scores[0]}\n{self.player_names[1]}: {self.scores[1]}")
                self.start_next_round()
            return

        # Switch Turn
        self.current_player = 1 - self.current_player
        self.vs_computer = (self.mode_var.get() == "ai")
        self.player_names[1] = "Computer" if self.vs_computer else "Player 2"

        self.lbl_turn.config(
            text=f"Turn: {self.player_names[self.current_player]}",
            fg=self.player_colors[self.current_player]
        )
        self.is_rolling = False
        self.btn_roll.config(state=tk.NORMAL)

        # Trigger AI move if VS Computer
        if self.vs_computer and self.current_player == 1:
            self.btn_roll.config(state=tk.DISABLED)
            self.root.after(800, self.roll_dice)

    def update_score_display(self):
        p2_label = "Comp" if self.vs_computer else "P2"
        self.lbl_scores.config(text=f"P1: {self.scores[0]}  |  {p2_label}: {self.scores[1]}")

    def start_next_round(self):
        """Resets token positions for a new round while keeping score."""
        self.positions = [0, 0]
        self.current_player = 0
        self.is_rolling = False
        self.lbl_turn.config(text=f"Turn: {self.player_names[0]}", fg=self.player_colors[0])
        self.lbl_dice.config(text="🎲")
        self.btn_roll.config(state=tk.NORMAL)
        self.draw_board()

    def reset_match(self):
        """Resets tokens, scores, and resets the full tournament."""
        self.scores = [0, 0]
        self.vs_computer = (self.mode_var.get() == "ai")
        self.player_names[1] = "Computer" if self.vs_computer else "Player 2"
        self.update_score_display()
        self.start_next_round()


if __name__ == "__main__":
    root = tk.Tk()
    app = SnakesAndLadders(root)
    root.mainloop()