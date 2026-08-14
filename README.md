# Boules de neige

Bataille de boules de neige en Python avec une interface graphique Tkinter, réalisée dans le cadre d'un TP de Numérique Science Informatique (NSI).

![Le Père Noël esquive les boules de neige](NoelG.gif)

## But du jeu

Guider le Père Noël pour qu'il évite les boules de neige le plus longtemps possible.

Règles :
- Les boules de neige arrivent du ciel avec une taille aléatoire.
- Quand elles touchent un bord de l'écran, elles rebondissent.
- Quand elles touchent le sol, elles rebondissent aussi mais leur taille est divisée par 2.
- En dessous d'une certaine taille, elles disparaissent de l'écran.
- Le Père Noël gagne s'il évite les boules de neige pendant une minute.
- Le temps restant s'affiche à l'écran.

## Lancer le jeu

Prérequis : Python 3 avec `tkinter` (inclus dans l'installation standard de Python).

```bash
python3 Avalanche.py
```

## Contenu

- `Avalanche.py` — logique du jeu et interface Tkinter
- `NoelD.gif`, `NoelG.gif` — sprites du Père Noël (droite/gauche)
- `boule4.gif` à `boule64.gif` — sprites des boules de neige selon leur taille
- `play.png`, `quit.png` — boutons d'interface
