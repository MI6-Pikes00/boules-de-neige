# Boules de neige

Bataille de boules de neige, réalisée à l'origine dans le cadre d'un TP de Numérique Science Informatique (NSI). Cette branche `improved` reprend le jeu original (`main` — Tkinter, fichier unique) en le restructurant et en ajoutant des fonctionnalités.

![Le Père Noël esquive les boules de neige](assets/NoelG.gif)

## 🎮 Jouer dans le navigateur

**[Jouer en ligne](https://mi6-pikes00.github.io/boules-de-neige/)** — aucune installation nécessaire (Python compilé en WebAssembly via [PyScript](https://pyscript.net), toujours en Python, sans JavaScript custom).

## 🖥️ Jouer en local (version Tkinter)

Prérequis : Python 3 avec `tkinter` (inclus dans l'installation standard de Python).

```bash
python3 main.py
```

## But du jeu

Guide le Père Noël (flèches gauche/droite) pour qu'il évite les boules de neige le plus longtemps possible.

- Les boules de neige arrivent du ciel avec une taille aléatoire.
- Elles rebondissent sur les bords de l'écran.
- Elles rebondissent aussi au sol, mais leur taille est alors divisée par 2 — en dessous d'une certaine taille, elles disparaissent.
- Barre d'espace : pouvoir d'invincibilité de 2 secondes.
- Survis 60 secondes pour gagner.

## Ce que la branche `improved` ajoute par rapport à l'original

- **3 niveaux de difficulté** (facile / normal / difficile) — fréquence et vitesse des boules de neige différentes.
- **Score** — points gagnés chaque seconde survécue (plus élevés en difficulté supérieure).
- **Meilleur score sauvegardé** localement (`highscore.json` en desktop, `localStorage` sur le web), par difficulté.
- **Pause** avec la touche `P` (version desktop).
- **Code restructuré** en petit package `avalanche/` au lieu d'un unique fichier de 276 lignes, correction de bugs mineurs (rechargement inutile d'images depuis le disque à chaque déplacement, doublon d'affichage si le pouvoir est activé deux fois de suite).

Les règles du jeu et la physique des boules de neige restent celles de la version originale.

## Contenu

- `main.py` — point d'entrée de la version desktop
- `avalanche/` — package Python (constantes, boule de neige, Père Noël, boucle de jeu/menu, meilleurs scores)
- `assets/` — sprites utilisés par la version desktop
- `docs/` — version jouable dans le navigateur (PyScript), servie par GitHub Pages
