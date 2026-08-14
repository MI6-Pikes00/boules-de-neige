"""Boule de neige : chute, rebond sur les bords et le sol, division de taille."""

import random


class Snowball:
    def __init__(self, size, screen_width, screen_height, speed_multiplier=1.0):
        self.screen_width = screen_width * 0.95
        self.screen_height = screen_height * 0.95

        self.x = random.randint(10, int(self.screen_width))
        self.y = 64
        self.size = size

        self.speed_x = random.randint(-10, 10) * speed_multiplier
        self.speed_y = random.randint(4, 8) * speed_multiplier

        # True le temps d'une frame quand la boule vient de rebondir au sol
        # et a besoin que son sprite soit rafraîchi.
        self.just_split = False

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x > self.screen_width or self.x < 0:
            self.speed_x = -self.speed_x

        if self.y + self.size * 2 < 0:
            self.speed_y = -self.speed_y

        self.just_split = False
        if self.y + self.size * 2 >= self.screen_height:
            self.size = int(self.size / 2)
            self.y -= self.speed_y // 2
            self.speed_y = -self.speed_y // 2
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
