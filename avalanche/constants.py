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

SANTA_STEP = 50
SANTA_WIDTH = 88
SANTA_HEIGHT = 155

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
