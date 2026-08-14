"""Avalanche — version navigateur (PyScript / Pyodide).

Même jeu que la version Tkinter (voir ../avalanche/), redessiné sur un
<canvas> HTML. Ce fichier est le seul code de la page : le HTML ne
contient que le chargement standard de PyScript, aucun JavaScript
n'est écrit à la main.
"""

import asyncio
import random

from pyodide.ffi import create_proxy
from pyscript import document, window

# --- Réglages, repris de avalanche/constants.py -----------------------

FPS = 60
GAME_DURATION = 60
INVINCIBILITY_DURATION = 2

# Mêmes 5 tailles de sprite que la version Tkinter (boule4.gif à boule64.gif).
SNOWBALL_SIZES = (4, 8, 16, 32, 64)
SANTA_WIDTH = 88
SANTA_HEIGHT = 155
SANTA_STEP = 12

DIFFICULTIES = {
    "facile": {"spawn_interval": 75, "max_snowballs": 6, "speed_multiplier": 0.8},
    "normal": {"spawn_interval": 50, "max_snowballs": 10, "speed_multiplier": 1.0},
    "difficile": {"spawn_interval": 30, "max_snowballs": 14, "speed_multiplier": 1.3},
}
SCORE_PER_SECOND = {"facile": 5, "normal": 10, "difficile": 20}

canvas = document.getElementById("game")
ctx = canvas.getContext("2d")
CANVAS_W = canvas.width
CANVAS_H = canvas.height

# --- Chargement des images ---------------------------------------------

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


# --- Modèle du jeu -------------------------------------------------------


class Snowball:
    def __init__(self, size, speed_multiplier):
        self.x = random.randint(10, CANVAS_W - 10)
        self.y = -20
        self.size = size
        self.speed_x = random.uniform(-3, 3) * speed_multiplier
        self.speed_y = random.uniform(2, 4) * speed_multiplier

    def move(self):
        self.x += self.speed_x
        self.y += self.speed_y

        if self.x < 0 or self.x > CANVAS_W:
            self.speed_x = -self.speed_x

        ground = CANVAS_H - 10
        if self.y + self.size >= ground:
            self.y = ground - self.size
            self.size = int(self.size / 2)
            self.speed_y = -abs(self.speed_y) / 2

    @property
    def is_spent(self):
        return self.size / 2 < 4

    def draw(self):
        sprite = sprite_for(self.size)
        ctx.drawImage(sprite, self.x - self.size / 2, self.y - self.size / 2, self.size, self.size)

    def overlaps(self, x, y, w, h):
        return (
            self.x + self.size / 2 > x
            and self.x - self.size / 2 < x + w
            and self.y + self.size / 2 > y
            and self.y - self.size / 2 < y + h
        )


class Game:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.settings = DIFFICULTIES[difficulty]

        self.santa_x = CANVAS_W / 2
        self.santa_y = CANVAS_H - SANTA_HEIGHT - 10
        self.facing_right = False

        self.snowballs = []
        self.chrono = GAME_DURATION
        self.score = 0
        self.frame = 0
        self.spawn_timer = 0
        self.invincible = False
        self.invincible_until = 0
        self.moving_left = False
        self.moving_right = False
        self.paused = False
        self.finished = False
        self.result_message = ""

    def spawn(self):
        size = random.choice(SNOWBALL_SIZES)
        self.snowballs.append(Snowball(size, self.settings["speed_multiplier"]))

    def collides(self):
        if self.invincible:
            return False
        x = self.santa_x - SANTA_WIDTH / 2
        y = self.santa_y
        for ball in self.snowballs:
            if ball.overlaps(x, y, SANTA_WIDTH, SANTA_HEIGHT):
                return True
        return False

    def update(self, now):
        if self.finished or self.paused:
            return

        if self.moving_left:
            self.santa_x = max(SANTA_WIDTH / 2, self.santa_x - SANTA_STEP)
            self.facing_right = False
        if self.moving_right:
            self.santa_x = min(CANVAS_W - SANTA_WIDTH / 2, self.santa_x + SANTA_STEP)
            self.facing_right = True

        if self.invincible and now >= self.invincible_until:
            self.invincible = False

        if self.collides():
            self.end(won=False)
            return

        self.frame += 1
        if self.frame >= FPS:
            self.frame = 0
            self.chrono -= 1
            self.score += SCORE_PER_SECOND[self.difficulty]
            if self.chrono <= 0:
                self.end(won=True)
                return

        if len(self.snowballs) < self.settings["max_snowballs"] and self.spawn_timer <= 0:
            self.spawn_timer = self.settings["spawn_interval"]
            self.spawn()
        self.spawn_timer -= 1

        for ball in self.snowballs:
            ball.move()
        self.snowballs = [b for b in self.snowballs if not b.is_spent]

    def end(self, won):
        self.finished = True
        self.result_message = "GAGNÉ !" if won else "PERDU"
        record = get_highscore(self.difficulty)
        if self.score > record:
            set_highscore(self.difficulty, self.score)
            self.result_message += "  (nouveau record !)"

    def power(self, now):
        if self.invincible or self.finished:
            return
        self.invincible = True
        self.invincible_until = now + INVINCIBILITY_DURATION

    def draw(self):
        ctx.fillStyle = "#5a99ad"
        ctx.fillRect(0, 0, CANVAS_W, CANVAS_H)

        for ball in self.snowballs:
            ball.draw()

        santa_sprite = images["NoelD.gif"] if self.facing_right else images["NoelG.gif"]
        ctx.drawImage(
            santa_sprite,
            self.santa_x - SANTA_WIDTH / 2,
            self.santa_y,
            SANTA_WIDTH,
            SANTA_HEIGHT,
        )

        ctx.fillStyle = "white"
        ctx.font = "bold 48px sans-serif"
        ctx.textAlign = "right"
        ctx.fillText(str(max(self.chrono, 0)), CANVAS_W - 20, 60)

        ctx.textAlign = "left"
        ctx.font = "bold 24px sans-serif"
        ctx.fillText(f"Score : {self.score}", 20, 40)

        if self.invincible:
            ctx.fillStyle = "black"
            ctx.font = "bold 32px sans-serif"
            ctx.textAlign = "center"
            ctx.fillText("INVINCIBLE", CANVAS_W / 2, 60)

        if self.paused:
            self._overlay("PAUSE")

        if self.finished:
            self._overlay(self.result_message)

    def _overlay(self, text):
        ctx.fillStyle = "rgba(0, 0, 0, 0.55)"
        ctx.fillRect(0, 0, CANVAS_W, CANVAS_H)
        ctx.fillStyle = "white"
        ctx.font = "bold 40px sans-serif"
        ctx.textAlign = "center"
        ctx.fillText(text, CANVAS_W / 2, CANVAS_H / 2)


# --- Meilleurs scores (localStorage, équivalent web du highscore.json) --

STORAGE_KEY = "avalanche-highscores"


def _read_scores():
    raw = window.localStorage.getItem(STORAGE_KEY)
    if not raw:
        return {}
    import json

    try:
        return json.loads(raw)
    except ValueError:
        return {}


def get_highscore(difficulty):
    return _read_scores().get(difficulty, 0)


def set_highscore(difficulty, score):
    import json

    scores = _read_scores()
    scores[difficulty] = score
    window.localStorage.setItem(STORAGE_KEY, json.dumps(scores))


# --- Entrées clavier / boutons -------------------------------------------

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
    elif key == "p" or key == "P":
        game.paused = not game.paused


def on_keyup(event):
    if game is None:
        return
    key = event.key
    if key == "ArrowLeft":
        game.moving_left = False
    elif key == "ArrowRight":
        game.moving_right = False


def start_game(difficulty):
    global game
    game = Game(difficulty)

    document.getElementById("menu").hidden = True
    document.getElementById("game").hidden = False
    document.getElementById("controls").hidden = False


def bind_menu():
    for difficulty in DIFFICULTIES:
        btn = document.getElementById(f"diff-{difficulty}")

        def handler(event, d=difficulty):
            start_game(d)

        btn.addEventListener("click", create_proxy(handler))
        best = get_highscore(difficulty)
        btn.innerText = f"{btn.innerText}  (record : {best})"


def bind_touch_controls():
    left = document.getElementById("btn-left")
    right = document.getElementById("btn-right")
    power = document.getElementById("btn-power")

    def set_left(down):
        def handler(event):
            if game:
                game.moving_left = down

        return create_proxy(handler)

    def set_right(down):
        def handler(event):
            if game:
                game.moving_right = down

        return create_proxy(handler)

    def do_power(event):
        if game:
            game.power(window.performance.now() / 1000)

    left.addEventListener("mousedown", set_left(True))
    left.addEventListener("mouseup", set_left(False))
    left.addEventListener("mouseleave", set_left(False))
    right.addEventListener("mousedown", set_right(True))
    right.addEventListener("mouseup", set_right(False))
    right.addEventListener("mouseleave", set_right(False))
    power.addEventListener("click", create_proxy(do_power))


async def game_loop():
    while True:
        now = window.performance.now() / 1000
        if game is not None:
            game.update(now)
            game.draw()
        await asyncio.sleep(1 / FPS)


async def main():
    document.addEventListener("keydown", create_proxy(on_keydown))
    document.addEventListener("keyup", create_proxy(on_keyup))

    load_images()
    await _load_done.wait()

    bind_menu()
    bind_touch_controls()

    document.getElementById("loading").hidden = True
    document.getElementById("menu").hidden = False

    await game_loop()


asyncio.ensure_future(main())
