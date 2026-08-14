"""Sauvegarde du meilleur score par niveau de difficulté, dans un petit
fichier JSON local (pas de base de données, pas de dépendance externe).

Chaque entrée retient aussi si le pouvoir d'invincibilité a été utilisé
pendant la partie, pour l'afficher dans le menu ("record : 120 (sans
pouvoir)")."""

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


def save_highscore(difficulty, score, used_power):
    """Met à jour le meilleur score pour une difficulté donnée si le
    nouveau score est supérieur. Renvoie True si c'est un nouveau record."""
    scores = load_highscores()
    best = get_highscore(difficulty)["score"]
    if score <= best:
        return False
    scores[difficulty] = {"score": score, "used_power": used_power}
    try:
        with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
    except OSError:
        pass
    return True


def get_highscore(difficulty):
    entry = load_highscores().get(difficulty, {"score": 0, "used_power": False})
    if isinstance(entry, (int, float)):
        # Compatibilité avec un ancien format (score seul, sans le suivi
        # de l'utilisation du pouvoir).
        return {"score": entry, "used_power": True}
    return entry


def format_record(difficulty):
    entry = get_highscore(difficulty)
    if entry["score"] <= 0:
        return "record : 0"
    tag = "sans pouvoir" if not entry["used_power"] else "avec pouvoir"
    return f"record : {entry['score']} ({tag})"
