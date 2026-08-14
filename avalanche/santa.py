"""Le Père Noël : déplacement gauche/droite et invincibilité temporaire."""

from .constants import SANTA_HEIGHT, SANTA_STEP, SANTA_WIDTH


class Santa:
    def __init__(self, canvas, x, y, sprite_left, sprite_right):
        self.canvas = canvas
        self.sprite_left = sprite_left
        self.sprite_right = sprite_right
        # Les deux sprites sont chargés une seule fois à la création (plutôt
        # que rechargés depuis le disque à chaque déplacement).
        self.id = canvas.create_image(x, y, anchor="nw", image=sprite_left)

        self.invincible = False
        self.invincible_ticks = 0

    def move_left(self):
        self.canvas.itemconfigure(self.id, image=self.sprite_left)
        self.canvas.move(self.id, -SANTA_STEP, 0)

    def move_right(self):
        self.canvas.itemconfigure(self.id, image=self.sprite_right)
        self.canvas.move(self.id, SANTA_STEP, 0)

    @property
    def bbox(self):
        x, y = self.canvas.coords(self.id)
        return x, y, x + SANTA_WIDTH, y + SANTA_HEIGHT

    def start_invincibility(self, duration_ticks):
        self.invincible = True
        self.invincible_ticks = duration_ticks

    def tick_invincibility(self):
        """Appelée une fois par seconde ; renvoie True si l'invincibilité
        vient de se terminer."""
        if not self.invincible:
            return False
        self.invincible_ticks -= 1
        if self.invincible_ticks <= 0:
            self.invincible = False
            return True
        return False
