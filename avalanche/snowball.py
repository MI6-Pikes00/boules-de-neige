"""Boule de neige : chute avec gravité, rebond sur les bords et le sol,
division de taille et perte d'énergie à chaque rebond."""

import random

from .constants import BOUNCE_ENERGY, GRAVITY, MAX_FALL_SPEED, WALL_ENERGY


class Snowball:
    def __init__(self, size, screen_width, screen_height, speed_multiplier=1.0):
        self.screen_width = screen_width * 0.95
        self.screen_height = screen_height * 0.95

        self.x = random.randint(10, int(self.screen_width))
        self.y = -size
        self.size = size
        self.speed_multiplier = speed_multiplier

        self.speed_x = random.uniform(-1.5, 1.5) * speed_multiplier
        self.speed_y = random.uniform(0, 1.5) * speed_multiplier

        # True le temps d'une frame quand la boule vient de rebondir au sol
        # et a besoin que son sprite soit rafraîchi.
        self.just_split = False

    def move(self):
        self.speed_y = min(self.speed_y + GRAVITY, MAX_FALL_SPEED)
        self.x += self.speed_x
        self.y += self.speed_y

        half = self.size / 2
        if self.x - half < 0:
            self.x = half
            self.speed_x = -self.speed_x * WALL_ENERGY + random.uniform(-0.3, 0.3)
        elif self.x + half > self.screen_width:
            self.x = self.screen_width - half
            self.speed_x = -self.speed_x * WALL_ENERGY + random.uniform(-0.3, 0.3)

        self.just_split = False
        if self.y + self.size * 2 >= self.screen_height:
            self.size = int(self.size / 2)
            self.speed_y = -abs(self.speed_y) * BOUNCE_ENERGY
            self.speed_x += random.uniform(-1, 1) * self.speed_multiplier
            self.just_split = True

    @property
    def is_spent(self):
        """La boule est trop petite pour survivre à un prochain rebond
        (elle disparaît avant de devenir plus petite que la plus petite
        taille de sprite disponible)."""
        return self.size / 2 < 4

    @property
    def position(self):
        return self.x, self.y
