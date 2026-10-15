import math

# World settings
WIDTH = 820
HEIGHT = 540
GROUND_Y = 470          # top of the floor
GRAVITY = 900.0         # px/s^2, tuned on pure vibes
BOUNCE = 0.40           # 0 = no bounce, 1 = perfect bounce, kind of the coefficient of restituion
FRICTION = 0.985        # floor friction on vx


# Ball logic
class Ball:
    def __init__(self, x, y, radius=14, mass=1.0, color="#e8504b"):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.mass = mass
        self.color = color

    def update(self, dt):
        # update velocity before position (semi-implicit euler), more stable
        self.vy += GRAVITY * dt
        self.x += self.vx * dt
        self.y += self.vy * dt

    def hit_walls(self):
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx = -self.vx * BOUNCE
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx = -self.vx * BOUNCE

        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy = -self.vy * BOUNCE
        elif self.y + self.radius > GROUND_Y:
            self.y = GROUND_Y - self.radius
            self.vy = -self.vy * BOUNCE
            self.vx *= FRICTION
            # kill tiny bounces, otherwise balls jitter on the floor forever
            if abs(self.vy) < 25:
                self.vy = 0.0


# Ball vs ball collisions
def collide_balls(a, b):
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    overlap = (a.radius + b.radius) - dist
    if overlap <= 0:
        return

    # normal from a to b
    nx = dx / dist
    ny = dy / dist

    # push apart, heavier ball moves less
    total_mass = a.mass + b.mass
    a.x -= nx * overlap * (b.mass / total_mass)
    a.y -= ny * overlap * (b.mass / total_mass)
    b.x += nx * overlap * (a.mass / total_mass)
    b.y += ny * overlap * (a.mass / total_mass)

    closing = (b.vx - a.vx) * nx + (b.vy - a.vy) * ny
    if closing > 0:
        return  # already separating

    j = -(1 + BOUNCE) * closing / (1 / a.mass + 1 / b.mass)
    a.vx -= j * nx / a.mass
    a.vy -= j * ny / a.mass
    b.vx += j * nx / b.mass
    b.vy += j * ny / b.mass


# Ball vs seesaw collisions
def collide_with_seesaw(ball, seesaw):
    # easier to check in plank coords than x/y
    along, perp = seesaw.to_plank_space(ball.x, ball.y)
    gap = ball.radius + seesaw.half_thickness

    if abs(along) > seesaw.half_length:
        return          # off the end
    if abs(perp) > gap:
        return          # not touching

    nx, ny = seesaw.normal()
    sign = 1.0
    if perp < 0:
        # ball is under the plank, flip normal
        nx, ny, perp, sign = -nx, -ny, -perp, -1.0

    # move ball out of the plank
    ball.x += nx * (gap - perp)
    ball.y += ny * (gap - perp)

    # plank surface speed at contact point, faster further from pivot
    plank_speed = -seesaw.omega * along * sign
    closing = (ball.vx * nx + ball.vy * ny) - plank_speed
    if closing > 0:
        return

    # along^2 / inertia term so hits near the pivot barely spin it
    j = -(1 + BOUNCE) * closing / (1 / ball.mass + along ** 2 / seesaw.inertia)
    ball.vx += j * nx / ball.mass
    ball.vy += j * ny / ball.mass
    seesaw.omega += j * along * sign / seesaw.inertia
