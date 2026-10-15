# Seesaw sim
# click = drop ball, B = heavy ball, R/space = reset

import math
import random
import tkinter as tk

import physics
from physics import Ball, collide_balls, collide_with_seesaw
from seesaw import Seesaw

# Settings
FPS = 60
DT = 1.0 / FPS
SUBSTEPS = 3            # fast balls were clipping through the plank with 1
MAX_BALLS = 14

BALL_COLORS = ["#e8504b", "#f2a33c", "#58b368", "#4c8ff2", "#9a6ad6"]
SKY = "#141821"


# App / window setup
class App:
    def __init__(self, root):
        root.title("Seesaw")
        self.canvas = tk.Canvas(root, width=physics.WIDTH, height=physics.HEIGHT,
                                bg=SKY, highlightthickness=0)
        self.canvas.pack()

        self.seesaw = Seesaw(physics.WIDTH / 2, 355)
        self.balls = []
        self.reset()

        self.canvas.bind("<Button-1>", self.on_click)
        root.bind("<r>", lambda event: self.reset())
        root.bind("<R>", lambda event: self.reset())
        root.bind("<space>", lambda event: self.reset())
        root.bind("<b>", lambda event: self.drop_heavy())
        root.bind("<B>", lambda event: self.drop_heavy())

        self.tick()

    # Spawning balls
    def add_ball(self, x, y, radius=14, mass=1.0, color=None):
        if len(self.balls) >= MAX_BALLS:
            self.balls.pop(0)       # remove oldest
        if color is None:
            color = random.choice(BALL_COLORS)
        self.balls.append(Ball(x, y, radius, mass, color))

    def reset(self):
        self.balls = []
        self.seesaw.reset()
        # one ball resting on the left, a heavier one dropping on the right
        self.add_ball(self.seesaw.pivot_x - 150, 320, 14, 1.0, "#58b368")
        self.add_ball(self.seesaw.pivot_x + 110, 60, 20, 3.0, "#e8504b")

    def on_click(self, event):
        self.add_ball(event.x, event.y, radius=random.randint(10, 18))

    def drop_heavy(self):
        side = random.choice([-1, 1])
        x = self.seesaw.pivot_x + side * random.randint(90, 180)
        self.add_ball(x, 40, radius=24, mass=6.0, color="#d8dce6")

    # Main loop
    def tick(self):
        self.step()
        self.draw()
        self.canvas.after(int(1000 * DT), self.tick)

    def step(self):
        dt = DT / SUBSTEPS
        for _ in range(SUBSTEPS):
            for ball in self.balls:
                ball.update(dt)

            for i in range(len(self.balls)):
                for j in range(i + 1, len(self.balls)):
                    collide_balls(self.balls[i], self.balls[j])

            self.seesaw.update(dt)
            for ball in self.balls:
                collide_with_seesaw(ball, self.seesaw)
                ball.hit_walls()

    # Drawing
    def draw(self):
        self.canvas.delete("all")
        ground = physics.GROUND_Y
        self.canvas.create_rectangle(0, ground, physics.WIDTH, physics.HEIGHT,
                                     fill="#2b313d", outline="")

        # pivot triangle
        px, py = self.seesaw.pivot_x, self.seesaw.pivot_y
        self.canvas.create_polygon(px, py, px - 42, ground, px + 42, ground,
                                   fill="#4a515f", outline="")

        self.canvas.create_polygon(self.seesaw.corners(),
                                   fill="#c8a06a", outline="#8a6a40")
        self.canvas.create_oval(px - 6, py - 6, px + 6, py + 6,
                                fill="#30363f", outline="")

        for ball in self.balls:
            r = ball.radius
            self.canvas.create_oval(ball.x - r, ball.y - r, ball.x + r, ball.y + r,
                                    fill=ball.color, outline="")

        self.canvas.create_text(12, 14, anchor="w", fill="#8e97a8",
                                font=("Consolas", 11),
                                text="click: drop ball    B: heavy ball    R: reset")
        self.canvas.create_text(12, 34, anchor="w", fill="#8e97a8",
                                font=("Consolas", 11),
                                text="tilt %6.1f deg    balls %d"
                                     % (math.degrees(self.seesaw.angle), len(self.balls)))


# Entry point
def main():
    root = tk.Tk()
    root.resizable(False, False)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
