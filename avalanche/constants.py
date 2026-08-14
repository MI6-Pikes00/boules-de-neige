"""Constantes de configuration du jeu Avalanche."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

FPS = 60
GAME_DURATION = 60  # secondes à survivre pour gagner
INVINCIBILITY_DURATION = 2  # secondes

SNOWBALL_SIZES = (4, 8, 16, 32, 64)
MIN_SNOWBALL_SIZE = 4

# Chute avec gravité + perte d'énergie au rebond (plutôt qu'une vitesse
# constante) pour des trajectoires en arc plus naturelles. Valeurs en
# pixels par frame (le jeu tourne à FPS constant via Tk .after()).
GRAVITY = 0.22
BOUNCE_ENERGY = 0.55  # vitesse verticale conservée après un rebond au sol
WALL_ENERGY = 0.85    # vitesse horizontale conservée après un rebond mural
MAX_FALL_SPEED = 11

SANTA_STEP = 50
SANTA_WIDTH = 88
SANTA_HEIGHT = 155
# La hitbox est plus petite que le sprite (marge transparente autour du
# personnage) pour des collisions plus justes visuellement.
SANTA_HITBOX_INSET_X = 0.24
SANTA_HITBOX_TOP = 0.12
SANTA_HITBOX_BOTTOM = 0.04

BACKGROUND_COLOR = "#5a99ad"
MENU_BACKGROUND = "#b19cd9"

# Chaque niveau règle la fréquence d'apparition (en frames), le nombre
# maximum de boules simultanées et un multiplicateur de vitesse.
DIFFICULTIES = {
    "facile": {"spawn_interval": 45, "max_snowballs": 6, "speed_multiplier": 0.8},
    "normal": {"spawn_interval": 30, "max_snowballs": 10, "speed_multiplier": 1.0},
    "difficile": {"spawn_interval": 18, "max_snowballs": 14, "speed_multiplier": 1.3},
}

# Points gagnés par seconde survécue, selon la difficulté.
SCORE_PER_SECOND = {"facile": 5, "normal": 10, "difficile": 20}
