"""Sauvegarde du meilleur score par niveau de difficulté, dans un petit
fichier JSON local (pas de base de données, pas de dépendance externe)."""

import json
import os

from .constants import HIGHSCORE_FILE


def load_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        return {}
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_highscore(difficulty, score):
    """Met à jour le meilleur score pour une difficulté donnée si le
    nouveau score est supérieur. Renvoie True si c'est un nouveau record."""
    scores = load_highscores()
    best = scores.get(difficulty, 0)
    if score <= best:
        return False
    scores[difficulty] = score
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except OSError:
        pass
    return True


def get_highscore(difficulty):
    return load_highscores().get(difficulty, 0)
