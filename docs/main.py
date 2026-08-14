"""Avalanche — version navigateur (PyScript / Pyodide).

Même jeu que la version Tkinter (voir ../avalanche/), redessiné sur un
<canvas> HTML. Ce fichier est le seul code de la page : le HTML ne
contient que le chargement standard de PyScript, aucun JavaScript
n'est écrit à la main.
"""

import asyncio
import json
import random

from pyodide.ffi import create_proxy
from pyscript import document, window

# --- Réglages ------------------------------------------------------------
#
# Toute la simulation est basée sur le temps réel écoulé (delta time), pas
# sur un compteur de frames : le jeu tourne à la même vitesse quel que soit
# le taux de rafraîchissement réel du navigateur/appareil. Les vitesses sont
# donc exprimées en pixels par seconde, les accélérations en px/s².

FPS_CAP = 60  # limite haute de la boucle de rendu, n'affecte pas la vitesse du jeu
GAME_DURATION = 60
INVINCIBILITY_DURATION = 2

# Résolution de conception : tout est exprimé en pixels sur une scène de
# BASE_W x BASE_H, puis mis à l'échelle par SCALE selon la taille réelle du
# canvas (calculée à partir de la fenêtre) pour un rendu responsive.
BASE_W = 900
BASE_H = 560

SANTA_WIDTH = 88
SANTA_HEIGHT = 155
SANTA_SPEED = 260  # px/s
# La hitbox est plus petite que le sprite (qui a de la marge transparente
# autour du personnage) pour des collisions plus justes visuellement.
SANTA_HITBOX_INSET_X = 0.24  # % de la largeur retiré de chaque côté
SANTA_HITBOX_TOP = 0.12      # % de la hauteur retiré en haut
SANTA_HITBOX_BOTTOM = 0.04   # % de la hauteur retiré en bas

SNOWBALL_SIZES = (4, 8, 16, 32, 64)
GRAVITY = 800          # px/s²
BOUNCE_ENERGY = 0.55   # vitesse verticale conservée après un rebond au sol
WALL_ENERGY = 0.85     # vitesse horizontale conservée après un rebond mural
MAX_FALL_SPEED = 650   # px/s

DIFFICULTIES = {
    "facile": {"spawn_interval": 1.25, "max_snowballs": 6, "speed_multiplier": 0.8},
    "normal": {"spawn_interval": 0.85, "max_snowballs": 10, "speed_multiplier": 1.0},
    "difficile": {"spawn_interval": 0.5, "max_snowballs": 14, "speed_multiplier": 1.3},
}
SCORE_PER_SECOND = {"facile": 5, "normal": 10, "difficile": 20}

canvas = document.getElementById("game")
ctx = canvas.getContext("2d")
SCALE = 1.0


def rescale_canvas():
    """Adapte la résolution du canvas à la largeur disponible, en gardant
    le ratio de la scène de conception (responsive)."""
    global SCALE
    area = document.getElementById("game-area")
    width = min(area.clientWidth or BASE_W, BASE_W)
    if width <= 0:
        width = BASE_W
    SCALE = width / BASE_W
    canvas.width = int(BASE_W * SCALE)
    canvas.height = int(BASE_H * SCALE)


# --- Chargement des images ------------------------------------------------

images = {}
_pending = 0
_load_done = asyncio.Event()


def _on_image_load(_event=None):
    global _pending
    _pending -= 1
    if _pending <= 0:
        _load_done.set()


def load_images():
    global _pending
    names = [
        "NoelG.gif",
        "NoelD.gif",
        "boule4.gif",
        "boule8.gif",
        "boule16.gif",
        "boule32.gif",
        "boule64.gif",
    ]
    _pending = len(names)
    proxy = create_proxy(_on_image_load)
    for name in names:
        img = window.Image.new()
        img.onload = proxy
        img.onerror = proxy
        img.src = f"./assets/{name}"
        images[name] = img


def sprite_for(size):
    return images[f"boule{size}.gif"]


# --- Modèle du jeu ---------------------------------------------------------


class Snowball:
    """Chute avec gravité, rebondit sur les bords et perd de l'énergie (et
    de la taille) à chaque rebond au sol — donne des trajectoires en arc
    plus naturelles qu'une simple vitesse constante."""

    def __init__(self, size, speed_multiplier):
        self.x = random.randint(int(size), int(BASE_W - size))
        self.y = -size
        self.size = size
        self.speed_multiplier = speed_multiplier
        self.speed_x = random.uniform(-90, 90) * speed_multiplier
        self.speed_y = random.uniform(0, 90) * speed_multiplier

    def move(self, dt):
        self.speed_y = min(self.speed_y + GRAVITY * dt, MAX_FALL_SPEED)
        self.x += self.speed_x * dt
        self.y += self.speed_y * dt

        half = self.size / 2
        if self.x - half < 0:
            self.x = half
            self.speed_x = -self.speed_x * WALL_ENERGY + random.uniform(-20, 20)
        elif self.x + half > BASE_W:
            self.x = BASE_W - half
            self.speed_x = -self.speed_x * WALL_ENERGY + random.uniform(-20, 20)

        ground = BASE_H - 10
        if self.y + half >= ground:
            self.y = ground - half
            self.size = int(self.size / 2)
            self.speed_y = -abs(self.speed_y) * BOUNCE_ENERGY
            self.speed_x += random.uniform(-60, 60) * self.speed_multiplier

    @property
    def is_spent(self):
        return self.size / 2 < 4

    def draw(self):
        sprite = sprite_for(self.size)
        s = self.size * SCALE
        ctx.drawImage(sprite, (self.x - self.size / 2) * SCALE, (self.y - self.size / 2) * SCALE, s, s)

    def overlaps(self, x, y, w, h):
        half = self.size / 2
        return (
            self.x + half > x
            and self.x - half < x + w
            and self.y + half > y
            and self.y - half < y + h
        )


class Game:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.settings = DIFFICULTIES[difficulty]

        self.santa_x = BASE_W / 2
        self.santa_y = BASE_H - SANTA_HEIGHT - 10
        self.facing_right = False

        self.snowballs = []
        self.chrono = GAME_DURATION
        self.score = 0
        self.second_timer = 0.0
        self.spawn_timer = 0.0
        self.invincible = False
        self.invincible_until = 0
        self.used_power = False
        self.moving_left = False
        self.moving_right = False
        self.paused = False
        self.finished = False
        self.result_message = ""

    def spawn(self):
        size = random.choice(SNOWBALL_SIZES)
        self.snowballs.append(Snowball(size, self.settings["speed_multiplier"]))

    def _hitbox(self):
        inset_x = SANTA_WIDTH * SANTA_HITBOX_INSET_X
        x = self.santa_x - SANTA_WIDTH / 2 + inset_x
        w = SANTA_WIDTH - 2 * inset_x
        y = self.santa_y + SANTA_HEIGHT * SANTA_HITBOX_TOP
        h = SANTA_HEIGHT * (1 - SANTA_HITBOX_TOP - SANTA_HITBOX_BOTTOM)
        return x, y, w, h

    def collides(self):
        if self.invincible:
            return False
        x, y, w, h = self._hitbox()
        for ball in self.snowballs:
            if ball.overlaps(x, y, w, h):
                return True
        return False

    def update(self, now, dt):
        if self.finished or self.paused:
            return

        if self.moving_left:
            self.santa_x = max(SANTA_WIDTH / 2, self.santa_x - SANTA_SPEED * dt)
            self.facing_right = False
        if self.moving_right:
            self.santa_x = min(BASE_W - SANTA_WIDTH / 2, self.santa_x + SANTA_SPEED * dt)
            self.facing_right = True

        if self.invincible and now >= self.invincible_until:
            self.invincible = False

        if self.collides():
            self.end(won=False)
            return

        self.second_timer += dt
        if self.second_timer >= 1:
            self.second_timer -= 1
            self.chrono -= 1
            self.score += SCORE_PER_SECOND[self.difficulty]
            if self.chrono <= 0:
                self.end(won=True)
                return

        self.spawn_timer -= dt
        if len(self.snowballs) < self.settings["max_snowballs"] and self.spawn_timer <= 0:
            self.spawn_timer = self.settings["spawn_interval"]
            self.spawn()

        for ball in self.snowballs:
            ball.move(dt)
        self.snowballs = [b for b in self.snowballs if not b.is_spent]

    def end(self, won):
        self.finished = True
        self.result_message = "GAGNÉ !" if won else "PERDU"
        record = get_highscore(self.difficulty)
        if self.score > record["score"]:
            set_highscore(self.difficulty, self.score, self.used_power)
            clean = "sans pouvoir" if not self.used_power else "avec pouvoir"
            self.result_message += f"  (nouveau record, {clean} !)"

    def power(self, now):
        if self.invincible or self.finished:
            return
        self.invincible = True
        self.used_power = True
        self.invincible_until = now + INVINCIBILITY_DURATION

    # -- Rendu --------------------------------------------------------------

    def draw(self):
        ctx.fillStyle = "#5a99ad"
        ctx.fillRect(0, 0, canvas.width, canvas.height)

        for ball in self.snowballs:
            ball.draw()

        santa_sprite = images["NoelD.gif"] if self.facing_right else images["NoelG.gif"]
        ctx.drawImage(
            santa_sprite,
            (self.santa_x - SANTA_WIDTH / 2) * SCALE,
            self.santa_y * SCALE,
            SANTA_WIDTH * SCALE,
            SANTA_HEIGHT * SCALE,
        )

        ctx.fillStyle = "white"
        ctx.font = f"bold {int(48 * SCALE)}px sans-serif"
        ctx.textAlign = "right"
        ctx.fillText(str(max(self.chrono, 0)), canvas.width - 20 * SCALE, 60 * SCALE)

        ctx.textAlign = "left"
        ctx.font = f"bold {int(24 * SCALE)}px sans-serif"
        ctx.fillText(f"Score : {self.score}", 20 * SCALE, 40 * SCALE)

        if self.invincible:
            ctx.fillStyle = "black"
            ctx.font = f"bold {int(32 * SCALE)}px sans-serif"
            ctx.textAlign = "center"
            ctx.fillText("INVINCIBLE", canvas.width / 2, 60 * SCALE)

        if self.paused:
            self._overlay("PAUSE")

        if self.finished:
            self._overlay(self.result_message)

    def _overlay(self, text):
        ctx.fillStyle = "rgba(0, 0, 0, 0.55)"
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.fillStyle = "white"
        size = 40 if len(text) < 12 else 26
        ctx.font = f"bold {int(size * SCALE)}px sans-serif"
        ctx.textAlign = "center"
        # découpe le message sur deux lignes s'il contient une virgule
        lines = text.split("  ")
        y = canvas.height / 2 - (len(lines) - 1) * 20 * SCALE
        for line in lines:
            ctx.fillText(line.strip(), canvas.width / 2, y)
            y += 44 * SCALE


# --- Meilleurs scores (localStorage, équivalent web du highscore.json) ----

STORAGE_KEY = "avalanche-highscores"


def _read_scores():
    raw = window.localStorage.getItem(STORAGE_KEY)
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        return {}


def get_highscore(difficulty):
    entry = _read_scores().get(difficulty)
    if not entry:
        return {"score": 0, "used_power": False}
    if isinstance(entry, (int, float)):
        return {"score": entry, "used_power": True}
    return entry


def set_highscore(difficulty, score, used_power):
    scores = _read_scores()
    scores[difficulty] = {"score": score, "used_power": used_power}
    window.localStorage.setItem(STORAGE_KEY, json.dumps(scores))


def format_record(difficulty):
    entry = get_highscore(difficulty)
    if entry["score"] <= 0:
        return "record : 0"
    tag = "sans pouvoir" if not entry["used_power"] else "avec pouvoir"
    return f"record : {entry['score']} ({tag})"


# --- Entrées clavier / boutons ---------------------------------------------

game = None


def on_keydown(event):
    if game is None or game.finished:
        return
    key = event.key
    if key == "ArrowLeft":
        game.moving_left = True
    elif key == "ArrowRight":
        game.moving_right = True
    elif key == " ":
        event.preventDefault()
        game.power(window.performance.now() / 1000)
    elif key in ("p", "P"):
        game.paused = not game.paused


def on_keyup(event):
    if game is None:
        return
    key = event.key
    if key == "ArrowLeft":
        game.moving_left = False
    elif key == "ArrowRight":
        game.moving_right = False


def show(element_id):
    document.getElementById(element_id).hidden = False


def hide(element_id):
    document.getElementById(element_id).hidden = True


def start_game(difficulty):
    global game
    game = Game(difficulty)

    hide("menu")
    show("game-area")
    show("controls")
    hide("end-overlay-actions")
    rescale_canvas()


def back_to_menu(event=None):
    global game
    game = None
    hide("game-area")
    hide("controls")
    hide("end-overlay-actions")
    refresh_menu_records()
    show("menu")


def retry_same_difficulty(event=None):
    if game is not None:
        start_game(game.difficulty)


def refresh_menu_records():
    for difficulty in DIFFICULTIES:
        btn = document.getElementById(f"diff-{difficulty}")
        btn.innerText = f"{difficulty.capitalize()} — {format_record(difficulty)}"


def bind_menu():
    for difficulty in DIFFICULTIES:
        btn = document.getElementById(f"diff-{difficulty}")

        def handler(event, d=difficulty):
            start_game(d)

        btn.addEventListener("click", create_proxy(handler))
    refresh_menu_records()


def bind_touch_controls():
    left = document.getElementById("btn-left")
    right = document.getElementById("btn-right")
    power = document.getElementById("btn-power")
    retry = document.getElementById("btn-retry")
    menu_btn = document.getElementById("btn-menu")

    def set_left(down):
        def handler(event):
            event.preventDefault()
            if game:
                game.moving_left = down

        return create_proxy(handler)

    def set_right(down):
        def handler(event):
            event.preventDefault()
            if game:
                game.moving_right = down

        return create_proxy(handler)

    def do_power(event):
        if game:
            game.power(window.performance.now() / 1000)

    left.addEventListener("mousedown", set_left(True))
    left.addEventListener("mouseup", set_left(False))
    left.addEventListener("mouseleave", set_left(False))
    left.addEventListener("touchstart", set_left(True))
    left.addEventListener("touchend", set_left(False))

    right.addEventListener("mousedown", set_right(True))
    right.addEventListener("mouseup", set_right(False))
    right.addEventListener("mouseleave", set_right(False))
    right.addEventListener("touchstart", set_right(True))
    right.addEventListener("touchend", set_right(False))

    power.addEventListener("click", create_proxy(do_power))
    retry.addEventListener("click", create_proxy(retry_same_difficulty))
    menu_btn.addEventListener("click", create_proxy(back_to_menu))


def bind_resize():
    def handler(event=None):
        rescale_canvas()

    window.addEventListener("resize", create_proxy(handler))
    window.addEventListener("orientationchange", create_proxy(handler))


_end_actions_shown_for = None

# Durée maximale d'un pas de simulation : si l'onglet est mis en arrière-plan
# puis réactivé (ou sur un appareil lent), on évite un grand saut d'un coup
# (boule qui traverse l'écran, chrono qui saute de plusieurs secondes).
MAX_DT = 0.05


async def game_loop():
    global _end_actions_shown_for
    last = window.performance.now() / 1000
    while True:
        now = window.performance.now() / 1000
        dt = min(now - last, MAX_DT)
        last = now

        if game is not None:
            game.update(now, dt)
            game.draw()
            if game.finished and _end_actions_shown_for is not game:
                show("end-overlay-actions")
                _end_actions_shown_for = game
            elif not game.finished:
                _end_actions_shown_for = None
        await asyncio.sleep(1 / FPS_CAP)


async def main():
    document.addEventListener("keydown", create_proxy(on_keydown))
    document.addEventListener("keyup", create_proxy(on_keyup))

    load_images()
    await _load_done.wait()

    rescale_canvas()
    bind_resize()
    bind_menu()
    bind_touch_controls()

    hide("loading")
    show("menu")

    await game_loop()


asyncio.ensure_future(main())
