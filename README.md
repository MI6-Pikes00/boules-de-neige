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

- Les boules de neige tombent avec une vraie gravité et rebondissent (sol et bords) en perdant de l'énergie à chaque fois — trajectoires en arc plutôt qu'une vitesse constante.
- Une boule rétrécit à chaque rebond au sol, puis disparaît en dessous d'une certaine taille.
- ⭐ **Pouvoir d'invincibilité** : barre d'espace (ou bouton à l'écran), 2 secondes, se réarme dès qu'il retombe.
- Survis 60 secondes pour gagner. Plus la difficulté est élevée, plus les boules sont fréquentes et rapides — mais plus le score rapporte de points.

## Ce que la branche `improved` ajoute par rapport à l'original

- **3 niveaux de difficulté** (facile / normal / difficile) — fréquence et vitesse des boules de neige différentes.
- **Score**, avec **meilleur score sauvegardé** par difficulté (`highscore.json` en desktop, `localStorage` sur le web) — le record précise s'il a été obtenu *avec* ou *sans* utiliser le pouvoir d'invincibilité.
- **Trajectoires des boules de neige retravaillées** : chute avec gravité et perte d'énergie au rebond, au lieu d'une vitesse constante.
- **Hitbox du Père Noël resserrée** sur la silhouette visible du personnage plutôt que sur tout le rectangle du sprite (collisions plus justes).
- **Menu explicite** : règles du jeu et pouvoir d'invincibilité détaillés avant de jouer.
- **Écran de fin avec boutons "Rejouer" / "Menu"** plutôt qu'une fermeture automatique.
- **Version web responsive** : le canvas s'adapte à la taille de l'écran (desktop, tablette, mobile), avec des contrôles tactiles.
- **Pause** avec la touche `P` (version desktop).
- **Code restructuré** en petit package `avalanche/` au lieu d'un unique fichier de 276 lignes, correction de bugs mineurs (rechargement inutile d'images depuis le disque à chaque déplacement, doublon d'affichage si le pouvoir est activé deux fois de suite).

Les règles de base du jeu restent celles de la version originale ; la physique des boules de neige et la zone de collision ont été affinées comme décrit ci-dessus.

## Contenu

- `main.py` — point d'entrée de la version desktop
- `avalanche/` — package Python (constantes, boule de neige, Père Noël, boucle de jeu/menu, meilleurs scores)
- `assets/` — sprites utilisés par la version desktop
- `docs/` — version jouable dans le navigateur (PyScript), servie par GitHub Pages
