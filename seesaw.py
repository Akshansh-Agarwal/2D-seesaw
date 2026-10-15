import math

from physics import GROUND_Y


# Seesaw logic
class Seesaw:
    def __init__(self, pivot_x, pivot_y, half_length=190, half_thickness=7, mass=30.0):
        self.pivot_x = pivot_x
        self.pivot_y = pivot_y
        self.half_length = half_length
        self.half_thickness = half_thickness
        self.mass = mass

        # rod spinning about its center: M*L^2/3 with L = half length
        self.inertia = mass * half_length ** 2 / 3.0

        self.angle = 0.0        # radians, positive = right side down
        self.omega = 0.0        # rad/s

        # max tilt before an end hits the floor
        drop = (GROUND_Y - pivot_y) / half_length
        self.max_angle = math.asin(min(1.0, max(0.0, drop)))

    # Geometry helpers
    def direction(self):
        # unit vector pivot -> right end
        return math.cos(self.angle), math.sin(self.angle)

    def normal(self):
        # unit vector out of the top face
        return math.sin(self.angle), -math.cos(self.angle)

    def to_plank_space(self, x, y):
        # returns (along, perp). along < 0 is left of pivot, perp > 0 is above
        dx = x - self.pivot_x
        dy = y - self.pivot_y
        tx, ty = self.direction()
        nx, ny = self.normal()
        return dx * tx + dy * ty, dx * nx + dy * ny

    def corners(self):
        tx, ty = self.direction()
        nx, ny = self.normal()
        points = []
        for end in (1, -1):
            for face in (1, -1):
                points.append((
                    self.pivot_x + tx * self.half_length * end + nx * self.half_thickness * face,
                    self.pivot_y + ty * self.half_length * end + ny * self.half_thickness * face,
                ))
        # swap last two so the polygon doesn't cross itself
        return [points[0], points[1], points[3], points[2]]

    # Physics
    def update(self, dt):
        # no torque from balls here, the collision impulses already push the plank
        # (adding gravity torque too was counting their weight twice)
        self.omega *= 0.995                 # pivot friction
        self.angle += self.omega * dt
        self.stop_at_the_floor()

    def stop_at_the_floor(self):
        if self.angle > self.max_angle:
            self.angle = self.max_angle
            self.omega = -self.omega * 0.3      # small bounce off the floor
        elif self.angle < -self.max_angle:
            self.angle = -self.max_angle
            self.omega = -self.omega * 0.3

    def reset(self):
        self.angle = 0.0
        self.omega = 0.0
